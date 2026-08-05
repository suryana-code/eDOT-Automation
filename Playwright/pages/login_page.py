from pages.base_page import BasePage


class LoginPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        self.btn_use_email = page.get_by_role("button", name="Use Email or Username")
        self.txt_email = page.get_by_role("textbox", name="Input Email or Username")
        self.txt_password = page.get_by_role("textbox", name="Password")
        self.btn_login = page.get_by_role("button", name="Log In")

    def open_login_page(self, url):
        self.open(url)

    def click_use_email(self):
        self.click(self.btn_use_email)

    def fill_email(self, email):
        self.fill(self.txt_email, email)

    def click_login_email(self):
        self.click(self.btn_login)

    def fill_password(self, password):
        self.fill(self.txt_password, password)

    def click_login_password(self):
        self.click(self.btn_login)
        self.wait_network_idle()