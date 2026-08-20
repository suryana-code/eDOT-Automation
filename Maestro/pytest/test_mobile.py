import json
import os

import allure
from utils.maestro_runner import run_maestro


@allure.feature("Mobile Automation - eWork SFA")
@allure.story("Create Customer - Tier 2")
def test_create_customer_mobile(ai_customer_data):
    """
    Execute the main Maestro flow using dynamically generated
    customer data.
    """

    env = os.environ.copy()

    # Credentials
    env["APP_ID"] = os.environ["APP_ID"]
    env["COMPANY_ID"] = os.environ["COMPANY_ID"]
    env["USER_NAME"] = os.environ["USER_NAME"]
    env["PASSWORD"] = os.environ["PASSWORD"]

    # Dynamic customer data
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

    # Attach generated test data to Allure.
    # Password is intentionally excluded.
    test_data = {
        key: env[key]
        for key in [
            "OUTLET_NAME",
            "PHONE",
            "EMAIL",
            "CONTACT_PERSON",
            "CHANNEL",
            "OUTLET_TYPE",
            "ADDRESS_TYPE",
            "ADDRESS",
            "PROVINCE",
            "CITY",
            "DISTRICT",
            "SUBDISTRICT",
        ]
    }

    allure.attach(
        json.dumps(
            test_data,
            indent=2,
            ensure_ascii=False,
        ),
        name="Generated Customer Data",
        attachment_type=allure.attachment_type.JSON,
    )

    with allure.step("Run Maestro main flow"):
        result = run_maestro(env)

    allure.attach(
        result.stdout + "\n" + result.stderr,
        name="Maestro Execution Log",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert result.returncode == 0, (
        "Maestro flow execution failed:\n"
        f"{result.stdout}\n"
        f"{result.stderr}"
    )