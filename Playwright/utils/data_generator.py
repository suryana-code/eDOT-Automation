import json

import allure

from utils.ai_helper import AIDataGenerator, GeneratedTestData


class CompanyData:

    @staticmethod
    def generate() -> dict:
        """Entry point data company yang kompatibel dengan test Playwright sebelumnya."""
        return CompanyData.generate_with_metadata().data

    @staticmethod
    def generate_with_metadata() -> GeneratedTestData:
        return AIDataGenerator().generate_company()


class CustomerData:
    """Contract data customer tervalidasi yang disiapkan untuk suite Maestro berikutnya."""

    @staticmethod
    def generate_with_metadata() -> GeneratedTestData:
        return AIDataGenerator().generate_customer()


def attach_generated_company_data(generated_data: GeneratedTestData) -> None:
    """Melampirkan data company yang tepat akan dikirim oleh test Playwright."""
    allure.attach(
        json.dumps(
            {
                "source": generated_data.source,
                "ai_attempts": generated_data.attempts,
                "company": generated_data.data,
            },
            ensure_ascii=False,
            indent=2,
        ),
        name="Actual Company Test Data",
        attachment_type=allure.attachment_type.JSON,
    )
