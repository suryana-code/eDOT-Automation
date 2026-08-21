.PHONY: test headed allure allure-headed allure-ci triage clean

# Menjalankan seluruh test dalam mode headless.
test:
	pytest

# Menjalankan test dengan UI browser.
headed:
	pytest -v -s --headed

# Menjalankan test dan membuka Allure Report.
allure:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report; \
	exit $${TEST_EXIT:-0}

# Menjalankan test mode headed dan membuka Allure Report.
allure-headed:
	rm -rf allure-results allure-report
	pytest -v -s --headed --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	allure open allure-report; \
	exit $${TEST_EXIT:-0}

# Menjalankan test untuk CI tanpa membuka browser.
allure-ci:
	rm -rf allure-results allure-report
	pytest --alluredir=allure-results || TEST_EXIT=$$?; \
	allure generate allure-results --clean -o allure-report; \
	exit $${TEST_EXIT:-0}

# Membaca result Allure yang sudah ada saja;
# tidak menjalankan test atau mengubah hasilnya.
triage:
	.venv/bin/python utils/failure_triage.py \
		--results-dir allure-results \
		--output triage-report.md

# Menghapus report yang dihasilkan.
clean:
	rm -rf allure-results allure-report .pytest_cache
