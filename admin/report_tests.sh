#!/bin/bash

# Default behavior
RUN_TESTS=true
GENERATE_REPORT=true
OPEN_REPORT=true

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Run pytest and generate/open Allure reports."
    echo ""
    echo "Options:"
    echo "  --no-tests      Do not run pytest, only generate/open report from existing results."
    echo "  --no-generate   Do not generate Allure report, only run tests."
    echo "  --no-open       Do not open Allure report in browser."
    echo "  -h, --help      Display this help message."
    echo ""
    echo "Examples:"
    echo "  $0                  # Run tests, generate report, open report (default)"
    echo "  $0 --no-generate    # Run tests only"
    echo "  $0 --no-tests       # Generate and open report from existing results"
    echo "  $0 --no-open        # Run tests, generate report, but do not open"
    exit 1
}

# Parse command-line arguments
for arg in "$@"; do
    case $arg in
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --no-generate)
            GENERATE_REPORT=false
            OPEN_REPORT=false # If no report is generated, it cannot be opened
            shift
            ;;
        --no-open)
            OPEN_REPORT=false
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Error: Unknown option '$arg'"
            usage
            ;;
    esac
done

PYTEST_EXIT_CODE=0
ALLURE_GENERATE_EXIT_CODE=0

# Step 1: Run Pytest
if $RUN_TESTS; then
    echo "INFO: Running pytest..."
    pytest --alluredir=allure-results # Generate Allure raw results
    PYTEST_EXIT_CODE=$?
    if [ $PYTEST_EXIT_CODE -ne 0 ]; then
        echo "WARNING: Pytest reported failures."
    fi
else
    echo "INFO: Skipping pytest execution (--no-tests)."
fi

# Step 2: Generate Allure report
if $GENERATE_REPORT; then
    echo "INFO: Generating Allure report..."
    allure generate allure-results -o allure-report --clean
    ALLURE_GENERATE_EXIT_CODE=$?
    if [ $ALLURE_GENERATE_EXIT_CODE -ne 0 ]; then
        echo "ERROR: Allure report generation failed."
        exit $ALLURE_GENERATE_EXIT_CODE
    fi
else
    echo "INFO: Skipping Allure report generation (--no-generate)."
fi

# Step 3: Open Allure report
if $OPEN_REPORT; then
    if [ $PYTEST_EXIT_CODE -ne 0 ]; then
        echo "WARNING: Pytest reported failures. Opening Allure report..."
    else
        echo "SUCCESS: Tests completed. Opening Allure report..."
    fi
    allure open allure-report
fi

# Final exit code for this script
if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    exit $PYTEST_EXIT_CODE
else
    exit 0
fi

