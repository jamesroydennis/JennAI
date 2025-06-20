#!/bin/bash

# This script runs pytest to generate Allure results, then generates the Allure report.
# It exits with a non-zero status code if either pytest or allure generation fails.

# Clean up old status files before starting
rm -f .test_run_status_*

echo "INFO: Running pytest to generate Allure results..."
pytest --alluredir=allure-results
PYTEST_EXIT_CODE=$?

# We will generate the report regardless of pytest outcome.
echo "INFO: Generating Allure HTML report..."
allure generate allure-results -o allure-report --clean
ALLURE_GENERATE_EXIT_CODE=$?

# Determine the final exit code for this script.
# Prioritize pytest failure code. If pytest passed, use allure's code.
if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pytest reported failures. Report was still generated."
    touch .test_run_status_failure # Signal failure
    exit $PYTEST_EXIT_CODE
fi

if [ $ALLURE_GENERATE_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Allure report generation failed."
    touch .test_run_status_failure # Signal failure
    exit $ALLURE_GENERATE_EXIT_CODE
fi

echo "SUCCESS: Tests ran and report generated successfully."
touch .test_run_status_success # Signal success
exit 0