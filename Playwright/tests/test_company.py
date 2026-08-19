from pages.company_page import CompanyPage
from pages.dashboard_page import DashboardPage
from utils.data_generator import CompanyData


def test_add_company(authenticated_page):
    dashboard = DashboardPage(authenticated_page)
    company = CompanyPage(authenticated_page)

    data = CompanyData.generate()

    dashboard.open_companies()

    company.click_add_company()
    company.verify_next_disabled()

    company.fill_company_name(data["company_name"])
    company.fill_email(data["email"])
    company.fill_phone(data["phone"])
    company.select_industry_type(data["industry"])
    company.select_company_type(data["company_type"])
    company.select_language(data["language"])
    company.fill_address(data["address"])
    company.select_country(data["country"])
    company.select_province(data["province"])
    company.select_city(data["city"])
    company.select_district(data["district"])
    company.select_zone(data["zone"])
    company.verify_postal_code_selected(data["postal_code"])

    company.verify_next_enabled()
    company.click_next()

    company.verify_register_legal_loaded()
    company.verify_next_enabled()
    company.click_next()

    company.verify_create_branch_loaded()
    company.fill_branch_name(data["branch_name"])
    company.verify_branch_name(data["branch_name"])
    company.fill_branch_address(data["address"])
    company.select_branch_country(data["country"])
    company.select_branch_province(data["province"])
    company.select_branch_city(data["city"])
    company.select_branch_district(data["district"])
    company.select_branch_sub_district(data["sub_district"])

    company.check_agreement()
    company.verify_register_enabled()
    company.click_register()

    company.verify_success_toast()
    company.verify_company_created(data["company_name"])

    company.open_company_manage(data["company_name"])
    company.verify_company_detail(data)

    company.delete_company()
    company.confirm_delete()
    company.verify_company_deleted(data["company_name"])
