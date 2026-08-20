# import subprocess
# from pathlib import Path

# ROOT_DIR = Path(__file__).resolve().parents[2]


# def run_maestro(env):
#     flow = ROOT_DIR / "flows" / "main.yaml"

#     cmd = [
#         "maestro",
#         "test",
#         str(flow),
#         "-p",
#         "android",
#     ]

#     return subprocess.run(
#         cmd,
#         capture_output=True,
#         text=True,
#         env=env,
#     )

import subprocess

MAESTRO_ENV_KEYS = [
    "APP_ID",
    "COMPANY_ID",
    "USER_NAME",
    "PASSWORD",
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
    "KTP",
]


def run_maestro(env):
    """
    Execute the main Maestro flow and explicitly pass
    required environment variables to Maestro.
    """

    command = [
        "maestro",
        "test",
        "-p",
        "android",
    ]

    for key in MAESTRO_ENV_KEYS:
        value = env.get(key)

        if value is not None:
            command.extend(["-e", f"{key}={value}"])

    command.append("flows/main.yaml")

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
    )