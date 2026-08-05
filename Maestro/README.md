# Maestro Mobile Automation

## Overview

This repository contains a Maestro mobile test suite for the eWork SFA application.
The test covers:

- Login and dashboard verification
- Customer creation with tier 2 validation
- Customer verification after creation

## Running the test

### Prerequisites

- Maestro CLI installed and available via `maestro --version`
- A connected Android device visible with `adb devices`
- The app package `id.edot.ework` installed on the target device
- Environment variables set for credentials and test data

### Environment variables

Set these before running tests:

- `APP_ID` (example: `id.edot.ework`)
- `COMPANY_ID`
- `USER_NAME`
- `PASSWORD`
- `CUSTOMER_NAME`
- `CUSTOMER_PHONE`
- `CUSTOMER_ADDRESS`

### Run via Maestro

```bash
cd /Users/suryana/Git/eDOT-Automation/Maestro
maestro test -p android -e APP_ID=id.edot.ework -e COMPANY_ID=5049209 -e USER_NAME=salesmanqaauto -e PASSWORD=it.QA2025 -e CUSTOMER_NAME="Nama Pelanggan" -e CUSTOMER_PHONE="081234567890" -e CUSTOMER_ADDRESS="Alamat Test" flows/main.yaml
```

### Run via Pytest wrapper

```bash
cd /Users/suryana/Git/eDOT-Automation/Maestro
pytest -q pytest/test_mobile.py
```

### Notes

- Credentials are not hardcoded in YAML flows.
- Login is extracted to a shared flow under `flows/login/login.yaml`.
- The wrapper attaches Maestro stdout/stderr to Allure.
- Use Maestro `record` to capture video if needed.
