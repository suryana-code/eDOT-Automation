"""Membaca result failure Allure dan membuat report triage Markdown advisory-only.

Modul ini tidak pernah memanggil Pytest, mengubah result Allure, atau memodifikasi source test.
"""

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

try:
    from utils.ai_helper import AI_API_KEY_ENV, AI_MODEL_ENV, DEFAULT_MODEL, AIDataGenerator
except ModuleNotFoundError:  # pragma: no cover - direct `python utils/...` entry point
    from ai_helper import AI_API_KEY_ENV, AI_MODEL_ENV, DEFAULT_MODEL, AIDataGenerator


MAX_ATTACHMENT_CHARS = 4_000
MAX_AI_ATTEMPTS = 2
ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ROOT_ENV_PATH)

EVIDENCE_STAGES = (
    "Exception/timeout/assertion",
    "Locator correctness and uniqueness",
    "Previous steps and preconditions",
    "Expected-value correctness",
    "Reproducibility/intermittency",
)
STOPPED_AFTER_FIRST_MATCH = "Not evaluated after first applicable match."


class TriageEvidenceStep(BaseModel):
    """Satu pemeriksaan triage berurutan yang dikembalikan oleh advisory AI."""

    model_config = ConfigDict(extra="forbid")

    stage: Literal[
        "Exception/timeout/assertion",
        "Locator correctness and uniqueness",
        "Previous steps and preconditions",
        "Expected-value correctness",
        "Reproducibility/intermittency",
    ]
    finding: str = Field(min_length=1, max_length=1_000)
    applicable: bool


class TriageAdvice(BaseModel):
    """Satu-satunya data yang boleh dikembalikan AI untuk test gagal."""

    model_config = ConfigDict(extra="forbid")

    verdict: Literal["Script/Environment Defect", "Product Bug", "Flaky"]
    reasoning: str = Field(min_length=1, max_length=1_500)
    confidence: int = Field(ge=0, le=100)
    recommended_human_follow_up: str = Field(min_length=1, max_length=1_000)
    first_applicable_match: Literal[
        "Exception/timeout/assertion",
        "Locator correctness and uniqueness",
        "Previous steps and preconditions",
        "Expected-value correctness",
        "Reproducibility/intermittency",
    ]
    evidence_sequence: List[TriageEvidenceStep] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def enforce_evidence_order_and_stop(self):
        """Menolak output advisory yang melewati stage atau mengevaluasi setelah kecocokan pertama."""
        stages = tuple(entry.stage for entry in self.evidence_sequence)
        if stages != EVIDENCE_STAGES:
            raise ValueError("evidence_sequence must use the required ordered stages")

        try:
            match_index = next(
                index
                for index, entry in enumerate(self.evidence_sequence)
                if entry.applicable
            )
        except StopIteration as error:
            raise ValueError("evidence_sequence must identify a first applicable match") from error

        if self.first_applicable_match != EVIDENCE_STAGES[match_index]:
            raise ValueError("first_applicable_match must be the first applicable evidence stage")

        if any(entry.applicable for entry in self.evidence_sequence[match_index + 1:]):
            raise ValueError("evidence evaluation must stop after the first applicable match")

        if any(
            entry.finding != STOPPED_AFTER_FIRST_MATCH
            for entry in self.evidence_sequence[match_index + 1:]
        ):
            raise ValueError("stages after the first applicable match must be marked as not evaluated")

        return self


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
    """Membaca hanya file *-result.json gagal; tidak ada artefak Allure yang diubah."""
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
                attachments=_read_attachments(_collect_attachments(result), results_dir),
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


def _collect_attachments(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Mengumpulkan attachment tingkat result dan nested step tanpa mengubah data Allure."""
    attachments = list(result.get("attachments", []))

    def visit(steps: Iterable[Dict[str, Any]]) -> None:
        for step in steps:
            attachments.extend(step.get("attachments", []))
            visit(step.get("steps", []))

    visit(result.get("steps", []))
    return attachments


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
    """Client OpenAI kecil dan terbatas yang hanya mengklasifikasikan failure yang sudah ada."""

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
Product Bug, Flaky. Evaluate evidence in this exact order: (1) Exception/timeout/assertion,
(2) Locator correctness and uniqueness, (3) Previous steps and preconditions,
(4) Expected-value correctness, (5) Reproducibility/intermittency. Set applicable=true
only for the first stage with enough evidence to classify the failure. For every later
stage, set applicable=false and write "Not evaluated after first applicable match." exactly.
Set first_applicable_match to that first applicable stage. Return all five ordered stages.
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
            lines.extend(
                f"{position}. **{entry.stage}** — {entry.finding}"
                for position, entry in enumerate(advice.evidence_sequence, start=1)
            )
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
