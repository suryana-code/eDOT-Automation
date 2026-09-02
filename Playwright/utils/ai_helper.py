"""Pembuatan data test AI pada runtime dengan fallback tervalidasi yang aman untuk offline.

Author: Muhamad Suryana
Public portfolio / educational reference
"""
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal, Optional, Type
from uuid import uuid4

import requests
from faker import Faker
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


AI_API_KEY_ENV = "EDOT_AI_API_KEY"
AI_MODEL_ENV = "EDOT_AI_MODEL"
TEST_DATA_SEED_ENV = "EDOT_TEST_DATA_SEED"
TEST_RUN_ID_ENV = "EDOT_TEST_RUN_ID"
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_TEST_DATA_SEED = 20260819
MAX_AI_ATTEMPTS = 2


class CompanyTestData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(min_length=8, max_length=30)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str = Field(pattern=r"^628\d{8,11}$")
    industry: Literal["Technology"]
    company_type: Literal["Marketplace"]
    language: Literal["Indonesia"]
    country: Literal["Indonesia"]
    province: Literal["JAWA BARAT"]
    city: Literal["KOTA BANDUNG"]
    district: Literal["BUAHBATU"]
    zone: Literal["JATISARI"]
    sub_district: Literal["JATISARI"]
    postal_code: Literal["40286"]
    address: str = Field(min_length=10, max_length=200)
    branch_name: Literal["Headquarter"]

    @field_validator("company_name")
    @classmethod
    def company_name_must_have_test_run_id(cls, value: str) -> str:
        if "QA-" not in value:
            raise ValueError("company_name must include the QA run identifier")
        return value


class CustomerTestData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=3, max_length=100)
    contact: str = Field(min_length=3, max_length=100)
    address: str = Field(min_length=10, max_length=200)
    phone: str = Field(pattern=r"^628\d{8,11}$")


@dataclass(frozen=True)
class GeneratedTestData:
    data: Dict[str, Any]
    source: Literal["ai", "fallback"]
    attempts: int


class AIDataGenerator:
    """Memanggil OpenAI hanya saat dikonfigurasi; output invalid/tidak tersedia memakai fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        request_post: Callable[..., requests.Response] = requests.post,
    ):
        self.api_key = api_key or os.getenv(AI_API_KEY_ENV)
        self.model = model or os.getenv(AI_MODEL_ENV, DEFAULT_MODEL)
        self.request_post = request_post
        self.run_id = os.getenv(TEST_RUN_ID_ENV) or uuid4().hex[:8]

    def generate_company(self) -> GeneratedTestData:
        run_id = self._run_id("company")
        fallback = self._fallback_company(run_id)
        prompt = self._company_prompt(run_id)
        return self._generate(
            prompt=prompt,
            schema_model=CompanyTestData,
            fallback=fallback,
        )

    def generate_customer(self) -> GeneratedTestData:
        run_id = self._run_id("customer")
        fallback = self._fallback_customer(run_id)
        prompt = self._customer_prompt(run_id)
        return self._generate(
            prompt=prompt,
            schema_model=CustomerTestData,
            fallback=fallback,
        )

    def _generate(
        self,
        prompt: str,
        schema_model: Type[BaseModel],
        fallback: BaseModel,
    ) -> GeneratedTestData:
        if not self.api_key:
            return GeneratedTestData(
                data=fallback.model_dump(), source="fallback", attempts=0
            )

        for attempt in range(1, MAX_AI_ATTEMPTS + 1):
            try:
                payload = self._request_ai(prompt, schema_model)
                validated = schema_model.model_validate(payload)
                return GeneratedTestData(
                    data=validated.model_dump(), source="ai", attempts=attempt
                )
            except (requests.RequestException, ValueError, ValidationError, KeyError):
                # Kegagalan di sini hanya memilih data fallback; assertion test tetap sama
                continue

        return GeneratedTestData(
            data=fallback.model_dump(), source="fallback", attempts=MAX_AI_ATTEMPTS
        )

    def _request_ai(
        self, prompt: str, schema_model: Type[BaseModel]
    ) -> Dict[str, Any]:
        response = self.request_post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "store": False,
                "input": prompt,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": schema_model.__name__.lower(),
                        "strict": True,
                        "schema": schema_model.model_json_schema(),
                    }
                },
            },
            timeout=20,
        )
        response.raise_for_status()
        return json.loads(self._output_text(response.json()))

    @staticmethod
    def _output_text(response: Dict[str, Any]) -> str:
        if response.get("output_text"):
            return response["output_text"]

        for item in response.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return content["text"]

        raise ValueError("AI response has no output text")

    @staticmethod
    def _seed() -> int:
        seed = os.getenv(TEST_DATA_SEED_ENV)
        return int(seed) if seed else DEFAULT_TEST_DATA_SEED

    def _run_id(self, kind: str) -> str:
        return self.run_id

    def _faker(self, run_id: str) -> Faker:
        faker = Faker("id_ID")
        faker.seed_instance(f"{self._seed()}:{run_id}")
        return faker

    def _fallback_company(self, run_id: str) -> CompanyTestData:
        faker = self._faker(run_id)
        return CompanyTestData(
            company_name=f"PT {faker.last_name()} QA-{run_id}",
            email=f"qa.{run_id}@example.test",
            phone="628" + faker.msisdn()[:10],
            industry="Technology",
            company_type="Marketplace",
            language="Indonesia",
            country="Indonesia",
            province="JAWA BARAT",
            city="KOTA BANDUNG",
            district="BUAHBATU",
            zone="JATISARI",
            sub_district="JATISARI",
            postal_code="40286",
            address=faker.street_address().replace("\n", ", "),
            branch_name="Headquarter",
        )

    def _fallback_customer(self, run_id: str) -> CustomerTestData:
        faker = self._faker(run_id)
        return CustomerTestData(
            name=f"Pelanggan QA-{run_id}",
            contact=faker.name(),
            address=faker.street_address().replace("\n", ", "),
            phone="628" + faker.msisdn()[:10],
        )

    @staticmethod
    def _company_prompt(run_id: str) -> str:
        return f"""Return only JSON that matches the supplied schema.
Generate coherent, realistic Indonesian business test data for an eSuite company.
Use a legal Indonesian-style company name of at most 30 characters containing exactly this run identifier: QA-{run_id}.
Use an email at example.test and an Indonesian mobile phone starting with 628.
The target application only accepts this verified location cascade: Indonesia, JAWA BARAT,
KOTA BANDUNG, BUAHBATU, JATISARI, postal code 40286. Set industry to Technology,
company_type to Marketplace, language to Indonesia, and branch_name to Headquarter.
The street address must be a realistic single-line Bandung address. Do not add commentary."""

    @staticmethod
    def _customer_prompt(run_id: str) -> str:
        return f"""Return only JSON that matches the supplied schema.
Generate realistic Indonesian customer data for future mobile test use: name, contact,
street address, and mobile phone starting with 628. Include QA-{run_id} in the name.
Do not add commentary."""
