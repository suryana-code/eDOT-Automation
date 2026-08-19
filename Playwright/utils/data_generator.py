from faker import Faker

fake = Faker("id_ID")


class CompanyData:

    @staticmethod
    def generate():

        return {
            "company_name": fake.company(),
            "email": fake.company_email(),
            "phone": "628" + fake.msisdn()[:10],
            "industry": "Technology",
            "company_type": "Marketplace",
            "language": "Indonesia",
            "country": "Indonesia",
            "province": "JAWA BARAT",
            "city": "KOTA BANDUNG",
            "district": "BUAHBATU",
            "zone": "JATISARI",
            "sub_district": "JATISARI",
            "postal_code": "40286",
            "address": fake.street_address(),
            "branch_name": "Headquarter"

        }
