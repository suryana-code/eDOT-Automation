import json

from utils.failure_triage import (
    FailedAllureTest,
    FailureTriageAI,
    TriageAdvice,
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


def test_triage_reads_text_attachment_from_nested_allure_step(tmp_path):
    attachment_name = "maestro-output.txt"
    (tmp_path / attachment_name).write_text("real nested output", encoding="utf-8")
    result = {
        "name": "nested_attachment_failure",
        "status": "failed",
        "statusDetails": {"message": "AssertionError", "trace": "trace"},
        "steps": [
            {
                "name": "Run Maestro main flow",
                "attachments": [
                    {
                        "name": "Maestro Execution Output",
                        "type": "text/plain",
                        "source": attachment_name,
                    }
                ],
                "steps": [],
            }
        ],
    }
    (tmp_path / "nested-result.json").write_text(json.dumps(result), encoding="utf-8")

    failure = read_failed_results(tmp_path)[0]

    assert failure.steps == ["Run Maestro main flow"]
    assert failure.attachments == [
        {
            "name": "Maestro Execution Output",
            "type": "text/plain",
            "content": "real nested output",
        }
    ]


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
                        "first_applicable_match": "Exception/timeout/assertion",
                        "evidence_sequence": [
                            {
                                "stage": "Exception/timeout/assertion",
                                "finding": "AssertionError is explicit.",
                                "applicable": True,
                            },
                            {
                                "stage": "Locator correctness and uniqueness",
                                "finding": "Not evaluated after first applicable match.",
                                "applicable": False,
                            },
                            {
                                "stage": "Previous steps and preconditions",
                                "finding": "Not evaluated after first applicable match.",
                                "applicable": False,
                            },
                            {
                                "stage": "Expected-value correctness",
                                "finding": "Not evaluated after first applicable match.",
                                "applicable": False,
                            },
                            {
                                "stage": "Reproducibility/intermittency",
                                "finding": "Not evaluated after first applicable match.",
                                "applicable": False,
                            },
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


def test_triage_rejects_advice_that_evaluates_after_first_match():
    invalid = {
        "verdict": "Script/Environment Defect",
        "reasoning": "A timeout was found.",
        "confidence": 90,
        "recommended_human_follow_up": "Inspect the environment.",
        "first_applicable_match": "Exception/timeout/assertion",
        "evidence_sequence": [
            {"stage": "Exception/timeout/assertion", "finding": "Timeout found.", "applicable": True},
            {"stage": "Locator correctness and uniqueness", "finding": "Also evaluated.", "applicable": True},
            {"stage": "Previous steps and preconditions", "finding": "Not evaluated.", "applicable": False},
            {"stage": "Expected-value correctness", "finding": "Not evaluated.", "applicable": False},
            {"stage": "Reproducibility/intermittency", "finding": "Not evaluated.", "applicable": False},
        ],
    }

    try:
        TriageAdvice.model_validate(invalid)
    except ValueError as error:
        assert "stop after the first applicable match" in str(error)
    else:
        raise AssertionError("TriageAdvice accepted evidence evaluated after its first match")


def test_triage_retries_invalid_ai_advice_then_uses_safe_fallback():
    calls = []

    class InvalidResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output_text": json.dumps({"verdict": "Not allowed"})}

    def invalid_post(*_args, **_kwargs):
        calls.append(1)
        return InvalidResponse()

    failed_test = FailedAllureTest(
        name="invalid", full_name="", status="failed", error="AssertionError", trace="",
        steps=[], attachments=[]
    )
    advice = FailureTriageAI(api_key="test-key", request_post=invalid_post).analyse(failed_test)

    assert len(calls) == 2
    assert advice is None
