import json

from utils.data_generator import attach_generated_company_data
from utils.ai_helper import AIDataGenerator, CompanyTestData, CustomerTestData


def test_company_data_uses_validated_deterministic_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("EDOT_AI_API_KEY", raising=False)
    monkeypatch.setenv("EDOT_TEST_DATA_SEED", "12345")
    monkeypatch.setenv("EDOT_TEST_RUN_ID", "1234abcd")

    first = AIDataGenerator().generate_company()
    second = AIDataGenerator().generate_company()

    assert first.source == "fallback"
    assert first.attempts == 0
    assert first.data == second.data
    assert len(first.data["company_name"]) <= 30
    assert CompanyTestData.model_validate(first.data).postal_code == "40286"


def test_company_fallback_name_varies_with_run_id(monkeypatch):
    monkeypatch.delenv("EDOT_AI_API_KEY", raising=False)
    monkeypatch.setenv("EDOT_TEST_DATA_SEED", "12345")

    monkeypatch.setenv("EDOT_TEST_RUN_ID", "1111aaaa")
    first = AIDataGenerator().generate_company()

    monkeypatch.setenv("EDOT_TEST_RUN_ID", "2222bbbb")
    second = AIDataGenerator().generate_company()

    assert first.data["company_name"] != second.data["company_name"]
    assert first.data["company_name"].startswith("PT ")
    assert second.data["company_name"].startswith("PT ")
    assert CompanyTestData.model_validate(first.data)
    assert CompanyTestData.model_validate(second.data)


def test_customer_fallback_matches_future_mobile_data_contract(monkeypatch):
    monkeypatch.delenv("EDOT_AI_API_KEY", raising=False)

    generated = AIDataGenerator().generate_customer()

    assert generated.source == "fallback"
    assert CustomerTestData.model_validate(generated.data).phone.startswith("628")


def test_invalid_ai_response_retries_then_falls_back(monkeypatch):
    monkeypatch.setenv("EDOT_AI_API_KEY", "test-key")
    calls = []

    class InvalidResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output_text": '{"company_name": "invalid"}'}

    def invalid_post(*_args, **_kwargs):
        calls.append(1)
        return InvalidResponse()

    generated = AIDataGenerator(request_post=invalid_post).generate_company()

    assert len(calls) == 2
    assert generated.source == "fallback"
    assert generated.attempts == 2
    assert CompanyTestData.model_validate(generated.data).company_name.startswith("PT ")


def test_valid_ai_output_is_used_after_schema_validation(monkeypatch):
    monkeypatch.setenv("EDOT_AI_API_KEY", "test-key")
    generator = AIDataGenerator(api_key="test-key")
    valid_data = generator._fallback_company("1234abcd").model_dump()

    class ValidResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output_text": json.dumps(valid_data)}

    generated = AIDataGenerator(
        api_key="test-key", request_post=lambda *_args, **_kwargs: ValidResponse()
    ).generate_company()

    assert generated.source == "ai"
    assert generated.attempts == 1
    assert generated.data == valid_data


def test_actual_company_data_attachment_is_created(monkeypatch):
    monkeypatch.delenv("EDOT_AI_API_KEY", raising=False)
    generated = AIDataGenerator(api_key=None).generate_company()

    attach_generated_company_data(generated)
