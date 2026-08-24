.PHONY: test headed allure allure-headed allure-ci generate-open triage clean

# Menjalankan seluruh test dalam mode headless
test:
	pytest --alluredir=allure-results

# Menjalankan test dengan UI browser
headed:
	pytest -v -s --headed

# Menjalankan test dan membuka Allure Report
allure:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report; \
	exit $${TEST_EXIT:-0}

# Menjalankan test mode headed dan membuka Allure Report
allure-headed:
	rm -rf allure-results allure-report
	pytest -v -s --headed --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report; \
	exit $${TEST_EXIT:-0}

# Menjalankan test untuk CI tanpa membuka browser
allure-ci:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	exit $${TEST_EXIT:-0}

# Generate dan membuka Allure Report dari result yang sudah ada
generate-open:
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report

# Membaca result Allure yang sudah ada saja
triage:
	.venv/bin/python utils/failure_triage.py \
		--results-dir allure-results \
		--output triage-report.md

# Menghapus result dan report yang dihasilkan
clean-playwright:
	rm -rf allure-results allure-report .pytest_cache