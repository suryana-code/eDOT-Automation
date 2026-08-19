.PHONY: test headed allure allure-headed allure-ci triage clean

# Run all tests (headless)
test:
	pytest

# Run tests with browser UI
headed:
	pytest -v -s --headed

# Run tests and open Allure Report
allure:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report; \
	exit $${TEST_EXIT:-0}

# Run tests and open Allure Report (headed)
allure-headed:
	rm -rf allure-results allure-report
	pytest -v -s --headed --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report; \
	exit $${TEST_EXIT:-0}

# Run test for CI (without opening browser)
allure-ci:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	exit $${TEST_EXIT:-0}

# Read existing Allure results only;
# does not run tests or change their outcome.
triage:
	python utils/failure_triage.py \
		--results-dir allure-results \
		--output triage-report.md

# Clean generated reports
clean:
	rm -rf allure-results allure-report .pytest_cache