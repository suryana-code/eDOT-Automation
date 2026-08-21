.PHONY: test allure

# Menjalankan flow Maestro melalui wrapper Pytest.
test:
	pytest -v -s pytest/test_mobile.py

# Menjalankan test, lalu membuka result Allure yang dibuat oleh pytest.ini.
allure:
	pytest -v -s pytest/test_mobile.py || TEST_EXIT=$$?; \
	allure serve allure-results; \
	exit $${TEST_EXIT:-0}
