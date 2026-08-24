import json
import os

import allure
from utils.maestro_runner import run_maestro


@allure.feature("Mobile Automation - eWork SFA")
@allure.story("Create Customer - Tier 2")
def test_create_customer_mobile(ai_customer_data):
    """
    Menjalankan flow utama Maestro menggunakan data customer yang dibuat dinamis.
    """

    env = os.environ.copy()

    # Credential dari environment

    env["APP_ID"] = os.environ["APP_ID"]
    env["COMPANY_ID"] = os.environ["COMPANY_ID"]
    env["USER_NAME"] = os.environ["USER_NAME"]
    env["PASSWORD"] = os.environ["PASSWORD"]

    # Teruskan data customer dinamis ke flow Maestro

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

    # Lampirkan data yang dipakai ke Allure

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

    # Jalankan flow utama Maestro

    with allure.step("Run Maestro main flow"):
        execution = run_maestro(env)

        # Lampirkan evidence dari run yang sama
        if execution.output_path.exists():
            allure.attach.file(
                str(execution.output_path),
                name="Maestro Execution Output",
                attachment_type="text/plain",
                extension="txt",
            )

        for screenshot in execution.screenshots:
            allure.attach.file(
                str(screenshot.path),
                name=f"Maestro Screenshot - {screenshot.name}",
                attachment_type="image/png",
                extension="png",
            )

        for recording in execution.recordings:
            if recording.attached_video_path:
                allure.attach.file(
                    str(recording.attached_video_path),
                    name="Maestro Screen Recording",
                    attachment_type="video/mp4",
                    extension="mp4",
                )

    # Tampilkan output agar failure mudah ditelusuri

    print("\n" + "=" * 70)
    print("MAESTRO EXECUTION RESULT")
    print("=" * 70)

    print(f"Return code: {execution.result.returncode}")

    print("\n--- MAESTRO STDOUT ---")
    print(execution.result.stdout or "(empty)")

    print("\n--- MAESTRO STDERR ---")
    print(execution.result.stderr or "(empty)")

    print("=" * 70)

    # Return code Maestro menentukan status test

    assert execution.result.returncode == 0, (
        "Maestro flow execution failed.\n\n"
        f"Return code: {execution.result.returncode}\n\n"
        f"STDOUT:\n{execution.result.stdout}\n\n"
        f"STDERR:\n{execution.result.stderr}"
    )
