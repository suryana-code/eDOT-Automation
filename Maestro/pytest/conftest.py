
import allure
import pytest
from pathlib import Path
from dotenv import load_dotenv
from faker import Faker

ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ROOT_ENV_PATH)

fake = Faker("id_ID")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Mengelompokkan seluruh hasil test Mobile pada satu suite Allure eksplisit."""
    allure.dynamic.parent_suite("Maestro")
    allure.dynamic.suite("Mobile Automation")


@pytest.fixture
def ai_customer_data():
    return {
        "outlet_name": fake.company(),
        "phone": fake.numerify("08############"),
        "email": fake.unique.email(),
        "contact_person": fake.name(),
        "address": fake.street_address(),
        "ktp": fake.numerify("################"),

        "channel": "Modern Trade (MT)",
        "outlet_type": "Grosir",
        "address_type": "Delivery Address",

        "province": "RIAU",
        "city": "KAB KAMPAR",
        "district": "BANGKINANG KOTA",
        "subdistrict": "KUMANTAN",
    }
