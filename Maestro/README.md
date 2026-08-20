# Maestro Mobile Automation

## Overview

This repository contains a Maestro mobile test suite for the eWork SFA application.
The test covers:

- Login and dashboard verification
- Customer creation with tier 2 validation
- Customer verification after creation

## Setup and Running the Test

### Prerequisites

- Maestro CLI installed and available via `maestro --version`
- A connected Android device visible with `adb devices`
- The app package `id.edot.ework` installed on the target device
- Python dependencies installed with `pip install -r requirements.txt`
- Allure CLI only when using `make allure`

### Environment variables

Create a shared local `.env` file in the repository root (`../.env` when running from `Maestro/`) with the credentials and application configuration required by the login flow:

- `APP_ID` (example: `id.edot.ework`)
- `COMPANY_ID`
- `USER_NAME`
- `PASSWORD`

`pytest/conftest.py` explicitly loads the repository-root `.env` through `python-dotenv`. Do not place credentials in YAML commands or commit local credentials.

### Run via Makefile

```bash
make test
```

Run this command from the `Maestro/` directory. It is equivalent to:

```bash
pytest -v -s pytest/test_mobile.py
```

### Run a Maestro Flow Directly for Login Debugging

The complete customer scenario should be run through Pytest because Pytest creates its dynamic customer data. To debug the reusable login flow directly, export the shared root `.env` values first:

```bash
set -a
. ../.env
set +a
maestro test -p android flows/login/login.yaml
```

### Generate and Open Allure Report

```bash
make allure
```

`pytest.ini` writes Allure results to `allure-results/`; `make allure` runs the same Pytest wrapper and opens those results with `allure serve`.

If the Allure CLI is not installed, run `make test` and install Allure before opening `allure-results/`.

### Notes

- The repository-root `.env` provides credentials and application configuration for the Pytest wrapper.
- Faker in `pytest/conftest.py` creates dynamic customer data for each test execution.
- Pytest is the wrapper/orchestrator: it loads `.env`, prepares dynamic data, invokes Maestro, and attaches the generated data and Maestro execution log to Allure.
- Maestro YAML files under `flows/` contain the mobile automation steps.
- Login is extracted to a shared flow under `flows/login/login.yaml`.
- Maestro uses native `startRecording` and `stopRecording` in the main flow, covering Login and Create Customer. Each Pytest run writes its output and MP4 recording to a unique subdirectory under `recordings/`.
- The Pytest wrapper attaches `Maestro Execution Output` as `text/plain` and `Maestro Screen Recording` as `video/mp4` inside the `Run Maestro main flow` Allure step. The video is intended to play inline in Allure-supported browsers.
- When `ffmpeg` and `ffprobe` are available, the wrapper may attach an H.264 compressed MP4 only after confirming that its width and height match the original recording. Otherwise, it attaches the original MP4.
