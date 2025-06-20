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


# Optionally, check main application log if main.py was run or tested
echo "INFO: Checking logs/jennai.log for errors..."
python admin/check_logs.py logs/jennai.log
CHECK_LOGS_EXIT_CODE=$? # Renamed for clarity

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Pytest reported failures."
    exit $PYTEST_EXIT_CODE
elif [ $CHECK_LOGS_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Log check for jennai.log reported issues."
    exit $CHECK_LOGS_EXIT_CODE # Use the renamed variable
fi

# Step 4: Print out the project tree using eza
echo "INFO: Displaying project tree..."
python -c "from admin import cleanup; cleanup.run_eza_tree(cleanup.jennai_root_for_path)"

echo "SUCCESS: Regression workflow completed."
exit 0
