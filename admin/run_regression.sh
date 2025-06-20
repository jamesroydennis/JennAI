#!/bin/bash
echo "INFO: Starting regression workflow..."

echo "INFO: Running cleanup script..."
python admin/cleanup.py
if [ $? -ne 0 ]; then
    echo "ERROR: cleanup.py failed. Aborting."
    exit 1
fi

echo "INFO: Running pytest..."
pytest --alluredir=allure-results # Generate Allure raw results
PYTEST_EXIT_CODE=$?
# We might not want to exit immediately if pytest fails,
# as we still want to generate the Allure report.


# Optionally, check main application log if main.py was run or tested
# With Allure, direct log checking for test failures becomes less critical.

# This step might be re-purposed or removed in the future.
# echo "INFO: Checking logs/jennai.log for application-specific errors..."
# python admin/check_logs.py logs/jennai.log
# CHECK_APP_LOGS_EXIT_CODE=$?

echo "INFO: Generating Allure report..."
allure generate allure-results -o allure-report --clean
ALLURE_GENERATE_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pytest reported failures."
    exit $PYTEST_EXIT_CODE
elif [ $ALLURE_GENERATE_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Allure report generation failed."
    # If report generation fails, we should exit.
    exit $ALLURE_GENERATE_EXIT_CODE
fi

# Step 4: Print out the project tree using eza
echo "INFO: Displaying project tree..."
python -c "from admin import cleanup; cleanup.run_eza_tree(cleanup.jennai_root_for_path)"

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "WARNING: Pytest reported failures. Opening Allure report..."
    allure open allure-report
    exit $PYTEST_EXIT_CODE # Exit with pytest's error code after opening report
else
    echo "SUCCESS: Regression workflow completed. Opening Allure report..."
    allure open allure-report # Open report on success too
    exit 0
fi
