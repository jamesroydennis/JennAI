@echo off
setlocal

:: This script performs a full reset of the JennAI project,
:: including deleting and recreating the Conda environment.
:: It relies on the ROOT environment variable being set by the calling script (e.g., admin/42.py).

if "%ROOT%"=="" (
    echo ERROR: ROOT environment variable is not set.
    echo This script must be called by a parent script that sets ROOT.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo                 JENN AI PROJECT FULL RESET
echo ====================================================================
echo.
echo WARNING: This will DELETE and RECREATE the 'jennai-root' Conda environment.
echo          All installed packages and local changes to the environment
echo          will be lost.
echo.
echo Project Root: %ROOT%
echo.

:: --- User Confirmation ---
set /p CONFIRM="Are you absolutely sure you want to proceed? (yes/no): "
if /i "%CONFIRM%" NEQ "yes" (
    echo.
    echo Reset cancelled by user.
    pause
    exit /b 0
)

echo.
echo --- Step 1: Deleting existing 'jennai-root' Conda environment ---
call conda env remove --name jennai-root
if %errorlevel% NEQ 0 (
    echo ERROR: Failed to remove Conda environment. Please check your Conda setup.
    pause
    exit /b 1
)
echo.
echo 'jennai-root' environment removed.

echo.
echo --- Step 2: Recreating 'jennai-root' Conda environment ---
echo Using environment file: %ROOT%\environment.yaml
call conda env create -f "%ROOT%\environment.yaml"
if %errorlevel% NEQ 0 (
    echo ERROR: Failed to create Conda environment.
    pause
    exit /b 1
)
echo.
echo 'jennai-root' environment recreated.

echo.
echo --- Step 3: Running project setup (e.g., pip install -r requirements.txt) ---
echo Running: python "%ROOT%\admin\setup.py"
call python "%ROOT%\admin\setup.py"
if %errorlevel% NEQ 0 (
    echo WARNING: Project setup script returned an error. Please check output.
    :: Do not exit here, as environment might still be usable.
)

echo.
echo ====================================================================
echo                 JENN AI PROJECT RESET COMPLETE
echo ====================================================================
echo.
pause
endlocal
exit /b 0