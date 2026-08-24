.PHONY: test allure generate-open clean

# Menjalankan flow Maestro melalui wrapper Pytest
test:
	pytest -v -s pytest/test_mobile.py

# Menjalankan test lalu membuka Allure Report
allure:
	pytest -v -s pytest/test_mobile.py || TEST_EXIT=$$?; \
	allure serve allure-results; \
	exit $${TEST_EXIT:-0}

# Generate dan membuka Allure Report dari result yang sudah ada
generate-open:
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report

# Menghapus result dan report Allure
clean-maestro:
	rm -rf allure-results allure-report