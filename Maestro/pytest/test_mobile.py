import os

import allure
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

    env["OUTLET_NAME"] = ai_customer_data["outlet_name"]

    env["PHONE"] = ai_customer_data["phone"]

    env["EMAIL"] = ai_customer_data["email"]

    env["CONTACT_PERSON"] = ai_customer_data["contact_person"]

    env["CHANNEL"] = ai_customer_data["channel"]

    env["OUTLET_TYPE"] = ai_customer_data["outlet_type"]

    env["ADDRESS_TYPE"] = ai_customer_data["address_type"]

    env["ADDRESS"] = ai_customer_data["address"]

    env["PROVINCE"] = ai_customer_data["province"]

    env["CITY"] = ai_customer_data["city"]

    env["DISTRICT"] = ai_customer_data["district"]

    env["SUBDISTRICT"] = ai_customer_data["subdistrict"]

    env["KTP"] = ai_customer_data["ktp"]

    result = run_maestro(env)

    allure.attach(
        result.stdout + "\n" + result.stderr,
        name="Maestro Execution Log",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert result.returncode == 0, (
        f"Maestro flow execution failed:\n{result.stderr}"
    )