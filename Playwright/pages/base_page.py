# Author: Muhamad Suryana
# Public portfolio / educational reference
# This file is part of the original eDOT automation project.

from playwright.sync_api import Page, expect


class BasePage:

    def __init__(self, page: Page):
        self.page = page

    # =====================================================
    # Aksi umum yang digunakan kembali oleh Page Object.

    def open(self, url):
        self.page.goto(url)

    def click(self, locator):
        locator.click()

    def fill(self, locator, value):
        locator.fill(value)

    def type(self, locator, value):
        locator.press_sequentially(value)

    def text(self, locator):
        return locator.inner_text()

    # =====================================================
    # Helper assertion berbasis Playwright expect.

    def expect_visible(self, locator):
        expect(locator).to_be_visible()

    def expect_enabled(self, locator):
        expect(locator).to_be_enabled()

    def expect_disabled(self, locator):
        expect(locator).to_be_disabled()

    def expect_text(self, locator, value):
        expect(locator).to_have_text(value)

    def expect_value(self, locator, value):
        expect(locator).to_have_value(value)   

    def wait_network_idle(self):
        self.page.wait_for_load_state("networkidle")

    def select_dropdown(self, dropdown, value):

        dropdown.wait_for(state="visible")

        dropdown.click()

        option = self.page.get_by_role(
            "option"
        ).filter(
            has_text=value
        )

        option.wait_for(state="visible")

        option.click()

    def select_searchable_dropdown(self, dropdown, value):

        dropdown.wait_for(state="visible")

        dropdown.click()

        search = self.page.get_by_role(
            "textbox",
            name="Search"
        )

        search.wait_for(state="visible")

        search.fill(value)

        option = self.page.get_by_role(
            "option"
        ).filter(
            has_text=value
        )

        option.wait_for(state="visible")

        option.click()
