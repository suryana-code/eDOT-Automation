import json

import allure

from utils.ai_helper import AIDataGenerator, GeneratedTestData


class CompanyData:

    @staticmethod
    def generate() -> dict:
        """Backward-compatible company data entrypoint for Playwright tests."""
        return CompanyData.generate_with_metadata().data

    @staticmethod
    def generate_with_metadata() -> GeneratedTestData:
        return AIDataGenerator().generate_company()


class CustomerData:
    """Validated customer data contract reserved for the later Maestro suite."""

    @staticmethod
    def generate_with_metadata() -> GeneratedTestData:
        return AIDataGenerator().generate_customer()


def attach_generated_company_data(generated_data: GeneratedTestData) -> None:
    """Attach exactly the company data that the Playwright test will submit."""
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
