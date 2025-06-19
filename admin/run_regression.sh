#!/bin/bash
echo "INFO: Starting regression workflow..."

echo "INFO: Running cleanup script..."
python admin/cleanup.py
if [ $? -ne 0 ]; then
    echo "ERROR: cleanup.py failed. Aborting."
    exit 1
fi

echo "INFO: Running pytest..."
pytest
PYTEST_EXIT_CODE=$?
# We might not want to exit immediately if pytest fails,
# as we still want to check logs.

echo "INFO: Checking pytest logs..."
python admin/check_logs.py logs/pytest.log
CHECK_PYTEST_LOGS_EXIT_CODE=$?

# Optionally, check main application log if main.py was run or tested
# echo "INFO: Checking main application logs..."
# python admin/check_logs.py logs/jennai.log
# CHECK_JENNAI_LOGS_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pytest reported failures."
    exit $PYTEST_EXIT_CODE
elif [ $CHECK_PYTEST_LOGS_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Log check for pytest.log reported issues."
    exit $CHECK_PYTEST_LOGS_EXIT_CODE
# elif [ $CHECK_JENNAI_LOGS_EXIT_CODE -ne 0 ]; then
#     echo "ERROR: Log check for jennai.log reported issues."
#     exit $CHECK_JENNAI_LOGS_EXIT_CODE
fi

echo "SUCCESS: Regression workflow completed."
exit 0
