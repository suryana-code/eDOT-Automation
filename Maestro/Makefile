.PHONY: test allure

# Run the Maestro flow through the Pytest wrapper.
test:
	pytest -v -s pytest/test_mobile.py

# Run the test, then open the Allure results produced by pytest.ini.
allure:
	pytest -v -s pytest/test_mobile.py || TEST_EXIT=$$?; \
	allure serve allure-results; \
	exit $${TEST_EXIT:-0}
