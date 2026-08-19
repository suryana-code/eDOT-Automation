import json

from utils.failure_triage import (
    FailedAllureTest,
    FailureTriageAI,
    read_failed_results,
    render_markdown,
    triage_failures,
)


def test_triage_reads_failed_allure_result_and_writes_safe_fallback_report(tmp_path, monkeypatch):
    result = {
        "name": "test_deliberate_failure",
        "fullName": "tests.evidence_failure.test_deliberate_failure",
        "status": "failed",
        "statusDetails": {"message": "AssertionError: deliberate", "trace": "assert False"},
        "steps": [{"name": "Prepare evidence", "steps": []}],
        "attachments": [],
    }
    (tmp_path / "sample-result.json").write_text(json.dumps(result), encoding="utf-8")
    monkeypatch.delenv("EDOT_AI_API_KEY", raising=False)

    failures = read_failed_results(tmp_path)
    triage = triage_failures(tmp_path, FailureTriageAI())
    report = render_markdown(triage, tmp_path)

    assert failures[0].name == "test_deliberate_failure"
    assert len(triage) == 1
    assert triage[0].advice is None
    assert "AI unavailable; human triage required" in report
    assert "DELIBERATE TRIAGE EVIDENCE" not in report


def test_triage_ignores_passing_allure_result(tmp_path):
    (tmp_path / "passed-result.json").write_text(
        json.dumps({"name": "passing", "status": "passed"}), encoding="utf-8"
    )

    assert read_failed_results(tmp_path) == []


def test_triage_ai_returns_only_validated_advisory_verdict():
    class ValidResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "output_text": json.dumps(
                    {
                        "verdict": "Script/Environment Defect",
                        "reasoning": "The evidence is a deliberate assertion failure.",
                        "confidence": 99,
                        "recommended_human_follow_up": "Do not file a product bug; keep this as evidence only.",
                        "evidence_sequence": [
                            "1. AssertionError is explicit.",
                            "2. No locator is involved.",
                            "3. No application precondition is needed.",
                            "4. Expected value is deliberately different.",
                            "5. The failure is reproducible by explicit execution.",
                        ],
                    }
                )
            }

    failed_test = FailedAllureTest(
        name="deliberate", full_name="", status="failed", error="AssertionError", trace="",
        steps=[], attachments=[]
    )
    advice = FailureTriageAI(
        api_key="test-key", request_post=lambda *_args, **_kwargs: ValidResponse()
    ).analyse(failed_test)

    assert advice.verdict == "Script/Environment Defect"
    assert advice.confidence == 99
