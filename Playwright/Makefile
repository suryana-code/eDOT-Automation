.PHONY: test headed allure allure-headed clean

# Run all tests (headless)
test:
	pytest

# Run tests with browser UI
headed:
	pytest -v -s --headed

# Run tests and generate Allure Report (headless)
allure:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results
	allure serve allure-results

# Run tests with browser UI and generate Allure Report
allure-headed:
	rm -rf allure-results allure-report
	pytest -v -s --headed --alluredir=allure-results
	allure serve allure-results

# Clean generated reports
clean:
	rm -rf allure-results allure-report .pytest_cache