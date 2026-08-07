from pages.base_page import BasePage


class DashboardPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        self.lbl_welcome = page.get_by_text("Welcome Back,")
        self.lnk_companies = page.get_by_role("link", name="Companies")
        

    def verify_dashboard_loaded(self):
        self.expect_visible(self.lbl_welcome)

    def open_companies(self):
        self.click(self.lnk_companies)