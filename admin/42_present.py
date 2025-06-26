#!/usr/bin/env python
import subprocess
import sys
import os
from pathlib import Path
from rich.console import Console

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

console = Console()

def supports_interactive_console():
    """Check if the terminal supports interactive features and colors."""
    return console.is_terminal

def run_command(command: str, cwd: Path = PROJECT_ROOT) -> int:
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True, # Use text mode for universal newline handling
            encoding="utf-8", # Explicitly set encoding
        )
        for line in iter(process.stdout.readline, ""):
            if supports_interactive_console():
                console.print(line, end="")
            else:
                print(line, end="")
        process.stdout.close()
        return process.wait()
    except Exception as e:
        if supports_interactive_console():
            color_print([("red", f"An error occurred: {e}")])
        else:
            print(f"An error occurred: {e}")
        return 1

def print_header(title: str):
    if supports_interactive_console():
        color_print([("cyan", "\n" + "=" * 70)])
        color_print([("cyan", f"{title}")])
        color_print([("cyan", "=" * 70)])
    else:
        print("\n" + "=" * 70)
        print(f"{title}")
        print("=" * 70)
def main():
    """Main function to present the presentation layer options."""

    def handle_platform_actions(platform_key: str):
        """Handles the sub-menu for a selected platform."""
        PLATFORM_SUB_MENU = [
            Choice(value="run", name="🏃 Run (Start Dev Server)"), # This is the "dev" option
            Separator("──────────────────────────────────"),
            Choice(value="create", name="Create (Scaffold & Brand)"),
            Choice(value="update", name="Update (Re-brand)"),
            Choice(value="delete", name="Delete (Remove App)"),
            Choice(value="qa", name="QA (Run QA Checks)"), # New QA option
            Choice(value="test", name="Test (Run Unit/Integration Tests)"),
            Separator("──────────────────────────────────"),
            Choice(value="back", name="⬅️ Back to Platform Selection"),
        ]

        while True:
            print_header(f"{platform_key.capitalize()} Platform Actions")
            if supports_interactive_console():
                action_selection = inquirer.select(
                    message=f"Select an action for {platform_key.capitalize()}:",
                    choices=PLATFORM_SUB_MENU,
                    default="run",
                    qmark=">",
                    cycle=False,
                    max_height=10,
                ).execute()
            else:
                print("\nRunning in simplified, non-interactive mode. Please use command-line arguments.")
                break

            if action_selection is None or action_selection == "back":
                break # Go back to main platform selection

            if action_selection == "create":
                print_header(f"{platform_key.capitalize()}: Scaffold/Setup")
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"') # Step 1: Scaffold
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}') # Step 2: Inject Assets
                print(f"\n{platform_key.capitalize()} presentation layer setup complete.")
            elif action_selection == "update":
                print(f"\nUpdate for {platform_key.capitalize()} not yet implemented.")
            elif action_selection == "delete":
                print(f"\nDelete for {platform_key.capitalize()} not yet implemented.")
            elif action_selection == "run":
                print_header(f"Running {platform_key.capitalize()} Dev Server")
                if platform_key == "flask":
                    flask_app_path = PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app" / "app.py"
                    run_command(f'{PY_EXEC} "{flask_app_path}"')
                elif platform_key == "angular":
                    angular_dir = PROJECT_ROOT / "src" / "presentation" / "angular_app"
                    if angular_dir.exists():
                        run_command('ng serve --open', cwd=angular_dir)
                    else:
                        print(f"Angular project not found at {angular_dir}. Please create it first.")
                elif platform_key == "react":
                    react_dir = PROJECT_ROOT / "src" / "presentation" / "react_app"
                    if react_dir.exists():
                        run_command('npm start', cwd=react_dir)
                    else:
                        print(f"React project not found at {react_dir}. Please create it first.")
            elif action_selection == "qa":
                print(f"\nQA for {platform_key.capitalize()} not yet implemented.")
            elif action_selection == "test":
                print(f"\nTest for {platform_key.capitalize()} not yet implemented.")
            
            if supports_interactive_console():
                input("\nPress Enter to continue...")

    """Main function to present the presentation layer options."""

    MENU = [
        Choice(value="flask", name="Flask"),
        Choice(value="angular", name="Angular"),
        Choice(value="react", name="React"),
        Separator("──────────────────────────────────"),
        Choice(value="regression", name="Regression Testing (cleanup, dirs, tests, Allure report)"),
        Separator("──────────────────────────────────"),
        Choice(value="exit", name="Exit"),
    ]

    while True:
        try:
            if supports_interactive_console():
                selection = inquirer.select(
                    message="Select a presentation task:",
                    choices=MENU,
                    default="flask",
                    qmark=">",
                    cycle=False,
                    max_height=10,
                ).execute()
            else:
                print("\nRunning in simplified, non-interactive mode due to lack of console support.")
                print("Please use command-line arguments to run specific tasks.")
                break # Exit the loop if not interactive

            if selection is None or selection == "exit": # Handle None for Ctrl+C or 'exit' choice
                print("\nExiting Presentation Console.")
                break

            try:
                if selection in ["flask", "angular", "react"]:
                    handle_platform_actions(selection)
                elif selection == "regression": # This is the top-level regression for the entire project
                    print_header("Regression Testing")
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"')
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')
                    run_command(f'{PY_EXEC} -m pytest --alluredir="{str(PROJECT_ROOT / "allure-results")}" --clean-alluredir')
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "generate_allure_environment.py"}"')
                    run_command(f'allure generate allure-results -o allure-report --clean')
                    print("\nRegression testing and Allure report generation complete.")

                else:
                    print("\nInvalid selection.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break # Exit the loop on Ctrl+C

        except prompt_toolkit.output.win32.NoConsoleScreenBufferError:
            print("\nError: Incompatible console. Running in simplified mode.")
            print("Please use command-line arguments to run specific tasks.")
            break
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break

if __name__ == "__main__":
    main()