"""Read Allure failure results and produce an advisory-only Markdown triage report.

This module never invokes pytest, changes Allure results, or modifies test source.
"""

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional

import requests
from pydantic import BaseModel, ConfigDict, Field, ValidationError

try:
    # Package import used by pytest and other project modules.
    from utils.ai_helper import AI_API_KEY_ENV, AI_MODEL_ENV, DEFAULT_MODEL, AIDataGenerator
except ModuleNotFoundError:  # pragma: no cover - direct `python utils/...` entry point
    # Direct-script import used by `make triage`.
    from ai_helper import AI_API_KEY_ENV, AI_MODEL_ENV, DEFAULT_MODEL, AIDataGenerator


MAX_ATTACHMENT_CHARS = 4_000
MAX_AI_ATTEMPTS = 2


class TriageAdvice(BaseModel):
    """The only data the AI is allowed to return for a failed test."""

    model_config = ConfigDict(extra="forbid")

    verdict: Literal["Script/Environment Defect", "Product Bug", "Flaky"]
    reasoning: str = Field(min_length=1, max_length=1_500)
    confidence: int = Field(ge=0, le=100)
    recommended_human_follow_up: str = Field(min_length=1, max_length=1_000)
    evidence_sequence: List[str] = Field(min_length=5, max_length=5)


@dataclass(frozen=True)
class FailedAllureTest:
    name: str
    full_name: str
    status: str
    error: str
    trace: str
    steps: List[str]
    attachments: List[Dict[str, str]]


@dataclass(frozen=True)
class TriageResult:
    failed_test: FailedAllureTest
    advice: Optional[TriageAdvice]
    ai_status: str


def read_failed_results(results_dir: Path) -> List[FailedAllureTest]:
    """Read only failed *-result.json files; no Allure artifact is modified."""
    failures = []
    for result_path in sorted(results_dir.glob("*-result.json")):
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if result.get("status") not in {"failed", "broken"}:
            continue

        details = result.get("statusDetails") or {}
        failures.append(
            FailedAllureTest(
                name=result.get("name", "Unnamed test"),
                full_name=result.get("fullName", ""),
                status=result.get("status", "unknown"),
                error=details.get("message", "No error message in Allure result"),
                trace=details.get("trace", ""),
                steps=_collect_steps(result.get("steps", [])),
                attachments=_read_attachments(result.get("attachments", []), results_dir),
            )
        )
    return failures


def _collect_steps(steps: Iterable[Dict[str, Any]]) -> List[str]:
    collected = []
    for step in steps:
        name = step.get("name")
        if name:
            collected.append(str(name))
        collected.extend(_collect_steps(step.get("steps", [])))
    return collected


def _read_attachments(
    attachments: Iterable[Dict[str, Any]], results_dir: Path
) -> List[Dict[str, str]]:
    evidence = []
    for attachment in attachments:
        source = attachment.get("source")
        name = attachment.get("name", "Unnamed attachment")
        attachment_path = results_dir / str(source)
        content = "Binary attachment not included in AI prompt."
        attachment_type = attachment.get("type", "")

        if attachment_type.startswith("text/") or str(source).endswith((".txt", ".json")):
            try:
                content = attachment_path.read_text(encoding="utf-8")[:MAX_ATTACHMENT_CHARS]
            except (OSError, UnicodeDecodeError):
                content = "Attachment could not be read."

        evidence.append({"name": str(name), "type": str(attachment_type), "content": content})
    return evidence


class FailureTriageAI:
    """Small, constrained OpenAI client used only to classify existing failures."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        request_post=requests.post,
    ):
        self.api_key = api_key or os.getenv(AI_API_KEY_ENV)
        self.model = model or os.getenv(AI_MODEL_ENV, DEFAULT_MODEL)
        self.request_post = request_post

    def analyse(self, failed_test: FailedAllureTest) -> Optional[TriageAdvice]:
        if not self.api_key:
            return None

        for _ in range(MAX_AI_ATTEMPTS):
            try:
                response = self.request_post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "store": False,
                        "input": _triage_prompt(failed_test),
                        "text": {
                            "format": {
                                "type": "json_schema",
                                "name": "triage_advice",
                                "strict": True,
                                "schema": TriageAdvice.model_json_schema(),
                            }
                        },
                    },
                    timeout=20,
                )
                response.raise_for_status()
                payload = json.loads(AIDataGenerator._output_text(response.json()))
                return TriageAdvice.model_validate(payload)
            except (requests.RequestException, ValueError, ValidationError, KeyError):
                continue
        return None


def _triage_prompt(failed_test: FailedAllureTest) -> str:
    evidence = {
        "test_name": failed_test.name,
        "status": failed_test.status,
        "exception_or_assertion": failed_test.error,
        "trace": failed_test.trace[:MAX_ATTACHMENT_CHARS],
        "previous_steps": failed_test.steps,
        "attachments": failed_test.attachments,
    }
    return """You are a QA failure-triage assistant. This is advisory-only human review.
You must not propose changes to assertions, expected values, test code, test execution,
bug trackers, or Allure results. Do not state that a test passed.

Classify the existing failure as exactly one of: Script/Environment Defect,
Product Bug, Flaky. Analyse evidence in this exact order and return five concise
evidence_sequence entries with these labels: (1) Exception/timeout/assertion,
(2) Locator correctness and uniqueness, (3) Previous steps and preconditions,
(4) Expected-value correctness, (5) Reproducibility/intermittency.
If evidence is missing, explicitly say so rather than inventing it.

Allure evidence follows:\n""" + json.dumps(evidence, ensure_ascii=False)


def triage_failures(results_dir: Path, ai: FailureTriageAI) -> List[TriageResult]:
    results = []
    for failed_test in read_failed_results(results_dir):
        advice = ai.analyse(failed_test)
        ai_status = "AI advisory generated" if advice else "AI unavailable; human triage required"
        results.append(TriageResult(failed_test, advice, ai_status))
    return results


def render_markdown(results: List[TriageResult], results_dir: Path) -> str:
    lines = [
        "# Allure Failure Triage Report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Source (read-only): `{results_dir}`",
        "- Scope: advisory-only; this report cannot alter test outcomes, assertions, or Allure results.",
        "",
    ]
    if not results:
        lines.extend(["No failed or broken Allure test result was found.", ""])
        return "\n".join(lines)

    for index, result in enumerate(results, start=1):
        failure = result.failed_test
        lines.extend([
            f"## {index}. {failure.name}",
            "",
            f"- Status: `{failure.status}`",
            f"- Full name: `{failure.full_name or 'not available'}`",
            f"- AI status: {result.ai_status}",
            "",
            "### Error / exception",
            "",
            "```text",
            failure.error or "No error message available.",
            "```",
            "",
            "### Evidence available",
            "",
            f"- Previous Allure steps: {', '.join(failure.steps) if failure.steps else 'not available'}",
            f"- Attachments: {', '.join(item['name'] for item in failure.attachments) or 'none'}",
            "",
        ])
        if result.advice:
            advice = result.advice
            lines.extend([
                "### AI advisory",
                "",
                f"- Verdict: **{advice.verdict}**",
                f"- Confidence: {advice.confidence}%",
                f"- Reasoning: {advice.reasoning}",
                f"- Recommended human follow-up: {advice.recommended_human_follow_up}",
                "",
                "### Required evidence sequence",
                "",
            ])
            lines.extend(f"{position}. {entry}" for position, entry in enumerate(advice.evidence_sequence, start=1))
            lines.append("")
        else:
            lines.extend([
                "### AI advisory",
                "",
                "AI verdict unavailable because no API key was configured or the provider/schema request failed. Review the evidence manually; no fallback verdict is invented.",
                "",
            ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an advisory failure-triage report from Allure results.")
    parser.add_argument("--results-dir", default="allure-results", type=Path)
    parser.add_argument("--output", default="triage-report.md", type=Path)
    args = parser.parse_args()

    report = render_markdown(triage_failures(args.results_dir, FailureTriageAI()), args.results_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Triage report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
