import os

import allure
import pytest

from utils.maestro_runner import run_maestro


@allure.feature("Mobile Automation - eWork SFA")
@allure.story("Create and Verify Customer (Tier 2)")
def test_create_customer_mobile(ai_customer_data):
    """
    Execute Maestro flow via Pytest wrapper.
    Customer data is provided by AI Generator (Phase 3A) or fallback values.
    """

    env = os.environ.copy()

    env["APP_ID"] = os.getenv("APP_ID", "id.edot.ework")
    env["COMPANY_ID"] = os.getenv("COMPANY_ID", "5049209")
    env["USER_NAME"] = os.getenv("USER_NAME", "salesmanqaauto")
    env["PASSWORD"] = os.getenv("PASSWORD", "it.QA2025")

    env["CUSTOMER_NAME"] = ai_customer_data["name"]
    env["CUSTOMER_PHONE"] = ai_customer_data["phone"]
    env["CUSTOMER_ADDRESS"] = ai_customer_data["address"]

    result = run_maestro(env)

    allure.attach(
        result.stdout + "\n" + result.stderr,
        name="Maestro Execution Log",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert result.returncode == 0, (
        f"Maestro flow execution failed:\n{result.stderr}"
    )