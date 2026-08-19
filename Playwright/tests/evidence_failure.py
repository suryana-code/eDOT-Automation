"""Explicit-only Allure evidence fixture; this file is not collected by normal pytest runs."""


def test_deliberate_failure_for_failure_triage_evidence():
    """Produces a known failure without opening the application or creating test data."""
    actual_status = "failure"
    assert actual_status == "success", "DELIBERATE TRIAGE EVIDENCE: expected success, got failure"
