import os
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv

from tests.login_setup import login

load_dotenv()


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

    login(page, config)

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

            page.screenshot(path=str(screenshot_path), full_page=True)

            allure.attach.file(
                str(screenshot_path),
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG
            )