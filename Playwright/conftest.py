import os
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from tests.login_setup import login

ROOT_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ROOT_ENV_PATH)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Group all Web test results under one explicit Allure suite."""
    allure.dynamic.parent_suite("Playwright")
    allure.dynamic.suite("Web Automation")


@pytest.fixture(scope="session")
def config():
    return {
        "base_url": os.getenv("BASE_URL"),
        "email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
        "storage_state": "auth/storage_state.json",
    }


@pytest.fixture(scope="session")
def storage_state(browser, config):

    storage = Path(config["storage_state"])

    storage.parent.mkdir(parents=True, exist_ok=True)

    if storage.exists():
        return config["storage_state"]

    page = browser.new_page()

    try:
        login(page, config)

    except Exception:
        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = (
            screenshot_dir / "storage_state_login_failure.png"
        )

        screenshot = page.screenshot(
            full_page=True
        )

        page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )

        allure.attach(
            screenshot,
            name="Login Setup Failure Screenshot",
            attachment_type=allure.attachment_type.PNG
        )

        raise

    finally:
        page.close()

    return config["storage_state"]


@pytest.fixture
def authenticated_page(browser, storage_state, config):

    context = browser.new_context(
        storage_state=storage_state
    )

    page = context.new_page()

    # buka aplikasi
    page.goto(config["base_url"])

    yield page

    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.failed:

        page = item.funcargs.get("authenticated_page")

        if page:

            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)

            screenshot_path = screenshot_dir / f"{item.name}.png"

            screenshot = page.screenshot(full_page=True)

            allure.attach(
                screenshot,
                name="Login Setup Failure Screenshot",
                attachment_type=allure.attachment_type.PNG
            )

            page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )
