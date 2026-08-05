import random

from faker import Faker

import pytest

fake = Faker("id_ID")

@pytest.fixture
def ai_customer_data():

    channels = [
        "General Trade (GT)",
        "Modern Trade (MT)"
    ]

    outlet_types = [
        "Grosir",
        "Retail Small",
        "Retail Medium"
    ]

    address_types = [
        "Delivery Address",
        "Invoice Address",
        "Other"
    ]

    provinces = [
        "RIAU"
    ]

    cities = [
        "KAB KAMPAR"
    ]

    districts = [
        "BANGKINANG KOTA"
    ]

    subdistricts = [
        "KUMANTAN"
    ]

    return {

        "outlet_name": fake.company(),

        "phone": fake.msisdn()[:12],

        "email": fake.email(),

        "contact_person": fake.name(),

        "channel": random.choice(channels),

        "outlet_type": random.choice(outlet_types),

        "address_type": random.choice(address_types),

        "address": fake.address(),

        "province": random.choice(provinces),

        "city": random.choice(cities),

        "district": random.choice(districts),

        "subdistrict": random.choice(subdistricts),

        "ktp": fake.numerify("################")
    }