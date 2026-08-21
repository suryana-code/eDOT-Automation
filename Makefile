.PHONY: test-all generate-all open-all allure-all clean-all

ALLURE_DIR := .allure
ALLURE_RESULTS := $(ALLURE_DIR)/results
ALLURE_REPORT := $(ALLURE_DIR)/report

PLAYWRIGHT_RESULTS := $(ALLURE_DIR)/playwright-results
MAESTRO_RESULTS := $(ALLURE_DIR)/maestro-results

# Run Web and Mobile suites in parallel.
# Each framework writes to its own temporary Allure result directory.
# Results are merged only after both suites finish.
test-all:
	@rm -rf "$(ALLURE_DIR)"
	@mkdir -p "$(ALLURE_RESULTS)" "$(PLAYWRIGHT_RESULTS)" "$(MAESTRO_RESULTS)"
	@echo "========================================"
	@echo "Starting combined automation"
	@echo "Playwright + Maestro will run in parallel"
	@echo "========================================"
	@echo ""

	@web_status=0; \
	mobile_status=0; \
	( \
		echo "➡️ [Playwright] START $$(date '+%H:%M:%S')"; \
		cd Playwright && \
		.venv/bin/pytest -v -s --alluredir=../$(PLAYWRIGHT_RESULTS); \
		status=$$?; \
		echo "➡️ [Playwright] END   $$(date '+%H:%M:%S') (exit=$$status)"; \
		exit $$status; \
	) & \
	web_pid=$$!; \
	( \
		echo "➡️ [Maestro]    START $$(date '+%H:%M:%S')"; \
		cd Maestro && \
		pytest -v -s pytest/test_mobile.py --alluredir=../$(MAESTRO_RESULTS); \
		status=$$?; \
		echo "➡️ [Maestro]    END   $$(date '+%H:%M:%S') (exit=$$status)"; \
		exit $$status; \
	) & \
	mobile_pid=$$!; \
	echo ""; \
	echo "Both suites started. Waiting for completion..."; \
	echo ""; \
	wait $$web_pid || web_status=$$?; \
	wait $$mobile_pid || mobile_status=$$?; \
	echo ""; \
	echo "========================================"; \
	echo "Execution finished"; \
	echo "Playwright exit code: $$web_status"; \
	echo "Maestro exit code:    $$mobile_status"; \
	echo "========================================"; \
	echo ""; \
	echo "Merging Allure results..."; \
	cp -R "$(PLAYWRIGHT_RESULTS)/." "$(ALLURE_RESULTS)/"; \
	cp -R "$(MAESTRO_RESULTS)/." "$(ALLURE_RESULTS)/"; \
	echo "Allure results merged successfully."; \
	echo ""; \
	if [ $$web_status -ne 0 ] || [ $$mobile_status -ne 0 ]; then \
		echo "Combined execution failed."; \
		exit 1; \
	fi

# Generate one HTML report from the merged Allure results.
generate-all:
	@echo "Generating combined Allure report..."
	@rm -rf "$(ALLURE_REPORT)"
	@allure generate "$(ALLURE_RESULTS)" --clean -o "$(ALLURE_REPORT)"

# Open the generated Allure report.
open-all:
	@echo "Opening combined Allure report..."
	@allure open "$(ALLURE_REPORT)"

# Run Playwright and Maestro in parallel,
# merge their Allure results,
# generate one combined report,
# then open the report.
allure-all:
	@$(MAKE) test-all; \
	test_status=$$?; \
	echo ""; \
	echo "Generating Allure report..."; \
	$(MAKE) generate-all; \
	generate_status=$$?; \
	if [ $$generate_status -ne 0 ]; then \
		exit $$generate_status; \
	fi; \
	echo ""; \
	echo "Opening Allure report..."; \
	$(MAKE) open-all; \
	open_status=$$?; \
	if [ $$test_status -ne 0 ]; then \
		exit $$test_status; \
	fi; \
	exit $$open_status

# Remove only integrated Allure artifacts.
clean-all:
	rm -rf "$(ALLURE_DIR)"
