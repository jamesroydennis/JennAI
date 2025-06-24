@echo off
echo.
echo ======================================================================
echo ==           JENN-AI FULL PROJECT ^& ENVIRONMENT RESET             ==
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
echo [STEP 3/4] Running full installation script...
echo This will create the environment and install all dependencies, including PyTorch.
python admin/install_requirements.py
if %errorlevel% neq 0 (
    echo [ERROR] The installation script failed. Aborting.
    pause
    exit /b
)

echo.
echo [STEP 4/4] Running tests in new environment...
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
echo IMPORTANT: If you are using an IDE (like VS Code), it is highly
echo            recommended to RESTART it now. This ensures it detects
echo            the new 'jennai-root' environment and interpreter correctly.
echo.
pause