.PHONY: test headed allure allure-headed allure-ci clean

# Run all tests (headless)
test:
	pytest

# Run tests with browser UI
headed:
	pytest -v -s --headed

# Run tests and open Allure Report
allure:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results
	allure serve allure-results

# Run tests and open Allure Report (headed)
allure-headed:
	rm -rf allure-results allure-report
	pytest -v -s --headed --alluredir=allure-results
	allure serve allure-results

# Run test for CI (without opening browser)
allure-ci:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results
	allure generate allure-results --clean -o allure-report

# Clean generated reports
clean:
	rm -rf allure-results allure-report .pytest_cache