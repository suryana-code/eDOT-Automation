"""Fixture evidence Allure yang hanya dijalankan eksplisit; file ini tidak dikoleksi suite Pytest normal."""


def test_deliberate_failure_for_failure_triage_evidence():
    """Menghasilkan failure yang diketahui tanpa membuka aplikasi atau membuat data test."""
    actual_status = "failure"
    assert actual_status == "success", "DELIBERATE TRIAGE EVIDENCE: expected success, got failure"
