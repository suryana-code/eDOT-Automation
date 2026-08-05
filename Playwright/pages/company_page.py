from playwright.sync_api import TimeoutError, expect

from pages.base_page import BasePage


class CompanyPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # =====================================================
        # TAB 1

        self.btn_add_company = page.get_by_role(
            "button",
            name="+ Add Company"
        )

        self.txt_company_name = page.get_by_role(
            "textbox",
            name="Input Company Name"
        )

        self.txt_email = page.get_by_role(
            "textbox",
            name="Input Email"
        )

        self.txt_phone = page.get_by_role(
            "textbox",
            name="Input Phone"
        )

        self.txt_address = page.get_by_role(
            "textbox",
            name="Input Address"
        )

        self.ddl_industry = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Industry Type"
        )

        self.ddl_company_type = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Company Type"
        )

        self.ddl_language = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Language"
        )

        self.ddl_country = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Country"
        )

        self.ddl_province = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Province"
        )

        self.ddl_city = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose City"
        )

        self.ddl_district = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose District"
        )

        self.ddl_sub_district = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Sub District"
        )

        # =====================================================
        # TAB 2

        self.lbl_register_legal = page.get_by_text(
            "Register Legal"
        )

        self.btn_add_document = page.get_by_role(
            "button",
            name="+ Add Document"
        )

        # =====================================================
        # TAB 3

        self.lbl_create_branch = page.get_by_text(
            "Create Your Branch"
        )

        self.txt_branch_name = page.get_by_role(
            "textbox",
            name="Input Branch Name"
        ).last

        self.txt_branch_address = page.get_by_placeholder(
            "Input Address"
        )

        self.ddl_branch_country = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Country"
        )

        self.ddl_branch_province = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Province"
        )

        self.ddl_branch_city = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose City"
        )

        self.ddl_branch_district = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose District"
        )

        self.ddl_branch_sub_district = page.get_by_role(
            "combobox"
        ).filter(
            has_text="Choose Sub District"
        )

        self.lnk_policy = page.get_by_text("Policy")

        self.lnk_terms = page.get_by_text(
            "Terms and Conditions",
            exact=True
        )

        self.lbl_policy_modal = page.get_by_role(
            "heading",
            name="esuite Policy"
        )

        self.lbl_terms_modal = page.get_by_role(
            "heading",
            name="Terms and Conditions"
        )

        self.btn_agree = page.get_by_role(
            "button",
            name="I'm Agree"
        )

        self.chk_agreement = page.locator("#select-all")

        self.btn_register = page.get_by_role(
            "button",
            name="Register"
        )

        self.toast_success = page.get_by_role(
            "alert"
        ).filter(
            has_text="Success Register Company"
        )
        self.toast_alert = page.get_by_role("alert").filter(
            has_text="Success"
        )
        self.lnk_back_to_companies = page.get_by_text(
            "Back to Companies",
            exact=False
        )

        # =====================================================
        # DETAIL COMPANY

        self.ddl_detail_industry = page.get_by_role(
            "combobox"
        ).nth(0)

        self.ddl_detail_company_type = page.get_by_role(
            "combobox"
        ).nth(1)

        self.txt_detail_address = page.get_by_placeholder(
            "Input Company Address"
        )

        self.txt_detail_email = page.get_by_placeholder(
            "Input Email"
        )

        self.txt_detail_phone = page.get_by_placeholder(
            "Input Mobile Number"
        )

        self.btn_delete = page.get_by_role(
            "button",
            name="Delete"
        )

        self.lbl_delete_modal = page.get_by_role(
            "heading",
            name="Confirmation Delete"
        )

        self.chk_delete = page.locator(
            "#select-all"
        )

        self.btn_confirm_delete = page.get_by_role(
            "button",
            name="Confirm"
        )

        self.toast_delete = page.get_by_text(
            "Success Delete Company",
            exact=True
        )

        # =====================================================
        # GLOBAL

        self.btn_back = page.get_by_role(
            "button",
            name="Back"
        )

        self.btn_next = page.get_by_role(
            "button",
            name="Next"
        )
        

    # =====================================================
    # TAB 1

    def click_add_company(self):
        self.click(self.btn_add_company)

    def fill_company_name(self, value):
        self.fill(self.txt_company_name, value)

    def fill_email(self, value):
        self.fill(self.txt_email, value)

    def fill_phone(self, value):
        self.fill(self.txt_phone, value)

    def fill_address(self, value):
        self.fill(self.txt_address, value)

    def select_industry_type(self, value):
        self.select_dropdown(self.ddl_industry, value)

    def select_company_type(self, value):
        self.select_dropdown(self.ddl_company_type, value)

    def select_language(self, value):
        self.select_dropdown(self.ddl_language, value)

    def select_country(self, value):
        self.select_dropdown(
            self.ddl_country,
            value
        )

    def select_province(self, value):
        self.select_searchable_dropdown(self.ddl_province, value)

    def select_city(self, value):
        self.select_searchable_dropdown(self.ddl_city, value)

    def select_district(self, value):
        self.select_searchable_dropdown(self.ddl_district, value)

    def select_sub_district(self, value):
        self.select_searchable_dropdown(self.ddl_sub_district, value)

    # =====================================================
    # TAB 2

    def verify_register_legal_loaded(self):
        self.expect_visible(self.lbl_register_legal)

    def click_add_document(self):
        self.click(self.btn_add_document)

    # =====================================================
    # TAB 3

    def verify_create_branch_loaded(self):
        self.expect_visible(self.lbl_create_branch)

    def fill_branch_name(self, value):
        self.txt_branch_name.wait_for(state="visible")
        self.txt_branch_name.click()
        self.txt_branch_name.fill(value)

    def verify_branch_name(self, value):
        self.expect_value(self.txt_branch_name, value)

    def fill_branch_address(self, value):
        self.fill(self.txt_branch_address, value)

    def select_branch_country(self, value):
        self.select_dropdown(
            self.ddl_branch_country,
            value
        )

    def select_branch_province(self, value):
        self.select_searchable_dropdown(
            self.ddl_branch_province,
            value
        )

    def select_branch_city(self, value):
        self.select_searchable_dropdown(
            self.ddl_branch_city,
            value
        )

    def select_branch_district(self, value):
        self.select_searchable_dropdown(
            self.ddl_branch_district,
            value
        )

    def select_branch_sub_district(self, value):
        self.select_searchable_dropdown(
            self.ddl_branch_sub_district,
            value
        )

    def open_policy(self):
        self.click(self.lnk_policy)

    def verify_policy_modal(self):
        self.expect_visible(self.lbl_policy_modal)

    def agree_policy(self):
        self.click(self.btn_agree)

    def open_terms(self):
        self.click(self.lnk_terms)

    def verify_terms_modal(self):
        self.expect_visible(self.lbl_terms_modal)

    def agree_terms(self):
        self.click(self.btn_agree)

    ##################################################
    # COMMON

    def click_next(self):
        self.click(self.btn_next)

    def click_back(self):
        self.click(self.btn_back)

    def verify_next_enabled(self):
        self.expect_enabled(self.btn_next)

    def verify_next_disabled(self):
        self.expect_disabled(self.btn_next)

    def verify_finish_enabled(self):
        self.expect_enabled(self.btn_next)

    def check_agreement(self):
        self.chk_agreement.wait_for(state="visible")
        self.chk_agreement.check()

    def click_register(self):
        self.click(self.btn_register)

    def verify_register_enabled(self):
        self.expect_enabled(self.btn_register)

    def verify_success_toast(self):
        try:
            self.toast_success.wait_for(state="visible", timeout=8000)
            return
        except TimeoutError:
            pass

        try:
            self.toast_alert.wait_for(state="visible", timeout=5000)
            return
        except TimeoutError:
            pass

        if self.lnk_back_to_companies.is_visible():
            return

        self.page.wait_for_url("**/companies", timeout=10000)

    def verify_company_created(self, company_name):
        self.page.wait_for_url("**/companies")
        self.expect_visible(self.btn_add_company)

        card = self.page.locator(
            "div.rounded-lg.border"
        ).filter(
            has_text=company_name
        )

        # Tier 1 - Company card should exist
        expect(card).to_be_visible()

        # Tier 2 - Product validation
        expect(card.get_by_text("Active")).to_be_visible()

        # Tier 2 - Product validation
        expect(card.get_by_test_id("plus-badge")).to_be_visible()

        expect(card.get_by_role("button", name="Manage")).to_be_visible()
        expect(card.get_by_role("button", name="Go To")).to_be_visible()

    # =====================================================
    # COMPANY DETAIL

    def open_company_manage(self, company_name):
        self.page.wait_for_url("**/companies")

        self.expect_visible(self.btn_add_company)

        card = self.page.locator(
            "div.rounded-lg.border"
        ).filter(
            has_text=company_name
        )

        expect(card).to_be_visible(timeout=10000)

        card.scroll_into_view_if_needed()

        card.get_by_role(
            "button",
            name="Manage"
        ).click()

        self.page.wait_for_load_state("domcontentloaded")

        for attempt in range(1, 6):

            try:

                expect(self.txt_company_name).to_have_value(
                    company_name,
                    timeout=5000
                )
                return

            except AssertionError:

                if attempt == 5:
                    raise AssertionError(
                        f"Company detail never loaded after {attempt} reloads."
                    )

                self.page.reload(wait_until="networkidle")


    def verify_company_detail(self, data):

        self.expect_value(
            self.txt_company_name,
            data["company_name"]
        )

        self.expect_text(
            self.ddl_detail_industry,
            data["industry"]
        )

        self.expect_text(
            self.ddl_detail_company_type,
            data["company_type"]
        )

        self.expect_value(
            self.txt_detail_address,
            data["address"]
        )

        self.expect_value(
            self.txt_detail_email,
            data["email"]
        )

        self.expect_value(self.txt_detail_phone, data["phone"])


    def delete_company(self):

        self.click(
            self.btn_delete
        )

        self.expect_visible(
            self.lbl_delete_modal
        )


    def confirm_delete(self):

        self.chk_delete.check()

        self.expect_enabled(
            self.btn_confirm_delete
        )

        self.click(
            self.btn_confirm_delete
        )


    def verify_company_deleted(self, company_name):

        self.page.wait_for_url(
            "**/companies"
        )

        self.expect_visible(
            self.btn_add_company
        )

        company = self.page.get_by_text(
            company_name,
            exact=True
        )

        expect(company).not_to_be_visible()