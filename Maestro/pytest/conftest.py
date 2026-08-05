import os
import pytest

@pytest.fixture
def ai_customer_data():
    """Provide customer data for mobile Maestro tests.

    Uses environment variables when available, otherwise defaults to stable sample data.
    """
    return {
        "name": os.getenv("CUSTOMER_NAME", "QA Customer " + os.getenv("USER_NAME", "auto")[:8]),
        "phone": os.getenv("CUSTOMER_PHONE", "081234567890"),
        "address": os.getenv("CUSTOMER_ADDRESS", "Jl. Test Automation 1"),
    }
