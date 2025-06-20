#!/bin/bash
echo "INFO: Starting regression workflow..."

# --- Argument Parsing ---
RUN_TREE=false
RUN_CLEAN=false

for arg in "$@"
do
    case $arg in
        --tree)
        RUN_TREE=true
        shift # Remove --tree from processing
        ;;
        --clean)
        RUN_CLEAN=true
        shift # Remove --clean from processing
        ;;
        *)
        # Unknown option, maybe handle or ignore
        ;;
    esac
done

# --- Workflow Steps ---

# Step 1: Optional Clean and Setup
if [ "$RUN_CLEAN" = true ]; then
    echo "INFO: --clean flag set. Running full setup script..."
    python admin/setup.py
    if [ $? -ne 0 ]; then
        echo "ERROR: admin/setup.py failed. Aborting."
        exit 1
    fi
else
    # If --clean is NOT set, run the standard cleanup
    echo "INFO: Running cleanup script..."
    python admin/cleanup.py
    if [ $? -ne 0 ]; then
        echo "ERROR: cleanup.py failed. Aborting."
        exit 1
    fi
fi

# Step 2: Run pytest
echo "INFO: Running pytest..." # This is Step 2 now
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
# Step 3: Generate Allure report
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

# Step 4: Optionally Print out the project tree using eza
if [ "$RUN_TREE" = true ]; then
    echo "INFO: --tree flag set. Displaying project tree..."
    python -c "from admin import cleanup; cleanup.run_eza_tree(cleanup.jennai_root_for_path)"
fi

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "WARNING: Pytest reported failures. Opening Allure report..."
    allure open allure-report
    exit $PYTEST_EXIT_CODE # Exit with pytest's error code after opening report
else
    echo "SUCCESS: Regression workflow completed. Opening Allure report..."
    allure open allure-report # Open report on success too
    exit 0
fi
