#!/usr/bin/env python
import subprocess
import sys
import os
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator
    from InquirerPy.utils import color_print
except ImportError:
    print("Error: InquirerPy is not installed or not found in the current environment.")
    print("Please ensure your conda environment is active and the package is installed.")
    print("You can try running: pip install InquirerPy")
    sys.exit(1)

PY_EXEC = f'"{sys.executable}"'

def run_command(command: str, cwd: Path = PROJECT_ROOT) -> int:
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True,
            encoding="utf-8",
        )
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
        process.stdout.close()
        return process.wait()
    except Exception as e:
        color_print([("red", f"An error occurred: {e}")])
        return 1

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)

def main():
    # --- Always cleanup and create directories first ---
    print_header("JennAI Presentation Admin Console")
    print("Running cleanup and directory creation scripts...\n")
    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"')
    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')

    MENU = [
        Choice("flask", "Flask: Scaffold/Setup Presentation Layer"),
        Choice("angular", "Angular: Scaffold/Setup Presentation Layer"),
        Choice("react", "React: Scaffold/Setup Presentation Layer"),
        Separator(),
        Choice("regression", "Regression Testing (cleanup, dirs, tests, Allure report)"),
        Separator(),
        Choice("exit", "Exit"),
    ]

    while True:
        try:
            selection = inquirer.select(
                message="Select a presentation task:",
                choices=MENU,
                default="flask",
                qmark=">",
                cycle=False,
                max_height=10,
            ).execute()

            if selection == "flask":
                print_header("Flask: Scaffold/Setup")
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_presentation_flask.py"}"') # Step 1: Scaffold
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target flask') # Step 2: Inject Assets
                print("\nFlask presentation layer setup complete.")
                input("\nPress Enter to return to the menu...")

            elif selection == "angular":
                print_header("Angular: Scaffold/Setup")
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_presentation_angular.py"}"')
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target angular')
                print("\nAngular presentation layer setup complete.")
                input("\nPress Enter to return to the menu...")

            elif selection == "react":
                print_header("React: Scaffold/Setup")
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_presentation_react.py"}"')  # Step 1: Scaffold
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target react')  # Step 2: Inject Assets
                print("\nReact presentation layer setup complete.")
                input("\nPress Enter to return to the menu...")

            elif selection == "regression":
                print_header("Regression Testing")
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"')
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')
                run_command(f'{PY_EXEC} -m pytest --alluredir="{str(PROJECT_ROOT / "allure-results")}" --clean-alluredir')
                run_command(f'allure generate allure-results -o allure-report --clean')
                print("\nRegression testing and Allure report generation complete.")
                input("\nPress Enter to return to the menu...")

            elif selection == "exit":
                print("\nGoodbye!")
                break

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break

if __name__ == "__main__":
    main()