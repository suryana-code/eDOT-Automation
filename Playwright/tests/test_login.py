from pages.dashboard_page import DashboardPage


def test_dashboard_loaded(authenticated_page):

    dashboard = DashboardPage(authenticated_page)

    dashboard.verify_dashboard_loaded()