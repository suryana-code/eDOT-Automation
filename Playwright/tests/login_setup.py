from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


def login(page, config):

    login_page = LoginPage(page)

    dashboard = DashboardPage(page)

    login_page.open_login_page(config["base_url"])

    login_page.click_use_email()

    login_page.fill_email(config["email"])

    login_page.click_login_email()

    login_page.fill_password(config["password"])

    login_page.click_login_password()

    dashboard.verify_dashboard_loaded()

    page.context.storage_state(
        path=config["storage_state"]
    )