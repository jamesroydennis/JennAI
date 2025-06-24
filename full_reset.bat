@echo off
echo.
echo ======================================================================
echo ==           JENN-AI FULL PROJECT & ENVIRONMENT RESET             ==
echo ======================================================================
echo.
echo DANGER: This script will delete project files (logs, reports) AND
echo         completely remove and recreate the 'jennai-root' environment.
echo.

set /p "confirm=(ADVANCED USERS) Are you absolutely sure you want to continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    exit /b
)

echo.
echo [STEP 1/5] Cleaning project files...
python admin/cleanup.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed during cleanup. Aborting.
    pause
    exit /b
)

echo.
echo [STEP 2/5] Removing Conda environment 'jennai-root'...
call conda env remove --name jennai-root -y
if %errorlevel% neq 0 (
    echo [WARNING] Failed to remove environment. It might not have existed. Continuing...
)

echo.
echo [STEP 3/5] Creating Conda environment 'jennai-root'...
call conda env create -f environment.yaml
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create environment. Aborting.
    pause
    exit /b
)

echo.
echo [STEP 4/5] Creating project folders in new environment...
call conda run -n jennai-root python admin/create_project_folders.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create project folders. Aborting.
    pause
    exit /b
)

echo.
echo [STEP 5/5] Running tests in new environment...
call conda run -n jennai-root python -m pytest
if %errorlevel% neq 0 (
    echo [WARNING] Tests failed. Please review the output.
)

echo.
echo ======================================================================
echo ==  ✅ FULL RESET COMPLETE                                         ==
echo ======================================================================
echo You can now activate the new environment: conda activate jennai-root
echo.
pause