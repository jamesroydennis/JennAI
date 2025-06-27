#!/usr/bin/env python
import subprocess
import sys
import os
from pathlib import Path
import shutil
from rich.console import Console

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Import config for paths and logging setup
    from config import config
    from config.loguru_setup import setup_logging, logger
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
ALLURE_EXEC = "allure" # Assumes Allure CLI is in PATH
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

# --- Platform Configuration & Helpers ---
PLATFORM_PATHS = {
    "flask": config.PRESENTATION_DIR / "api_server" / "flask_app",
    "angular": config.PRESENTATION_DIR / "angular_app",
    "react": config.PRESENTATION_DIR / "react_app",
    "vue": config.PRESENTATION_DIR / "vue_app",
}

def delete_platform(platform_key: str):
    """
    Safely deletes the directory for a given presentation platform after user confirmation.
    """
    platform_dir = PLATFORM_PATHS.get(platform_key)
    if not platform_dir:
        color_print([("red", f"Error: No path defined for platform '{platform_key}'.")])
        return

    if not platform_dir.exists():
        print(f"\nINFO: Directory for {platform_key.capitalize()} not found at '{platform_dir}'. Nothing to delete.")
        return

    # Confirmation prompt
    confirmed = inquirer.confirm(
        message=f"DANGER: This will permanently delete the entire '{platform_dir.name}' directory and all its contents. Are you sure?",
        default=False,
        confirm_message="Deletion confirmed. Proceeding...",
        reject_message="Deletion cancelled."
    ).execute()

    if not confirmed:
        return

    try:
        shutil.rmtree(platform_dir)
        color_print([("green", f"\n✅ Successfully deleted the {platform_key.capitalize()} application directory.")])
    except OSError as e:
        color_print([("red", f"\n❌ Error deleting directory '{platform_dir}': {e}")])

# --- Centralized Step Definitions ---

# Cleanup and Directory Creation Steps (re-used from admin/42.py)
CLEANUP_STEPS = [
    {"name": "Cleaning Project", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"'},
    {"name": "Creating Directories", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"'},
]

# Allure Reporting Step (re-used from admin/42.py)
REPORTING_STEP = {"name": "Serve Report", "command": f'"{ALLURE_EXEC}" serve "{config.ALLURE_RESULTS_DIR}"', "abort_on_fail": False}

# Pytest Command Builders for different scopes
def build_pytest_command(scope: str, with_allure: bool = False) -> str:
    # Dynamically set verbosity based on the project's DEBUG_MODE
    verbosity_flag = "-v" if config.DEBUG_MODE else "-q -rA"
    base_cmd = f'{PY_EXEC} -m pytest {verbosity_flag} --scope={scope}'
    if with_allure:
        return f'{base_cmd} --alluredir="{config.ALLURE_RESULTS_DIR}" --clean-alluredir'
    return base_cmd

# Test Step Definitions for specific platforms (e.g., Flask, Angular)
def get_platform_testing_steps(platform_key: str, with_allure: bool = False) -> list:
    # Construct scope based on platform_key
    scope = f"{platform_key.upper()}_PRESENTATION"
    steps = [
        {"name": f"Run {platform_key.capitalize()} Tests", "command": build_pytest_command(scope, with_allure)},
    ]
    if with_allure:
        steps.append({"name": "Generate Allure Environment", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "generate_allure_environment.py"}"', "abort_on_fail": False})
    return steps

# Test Step Definitions for the entire Presentation Layer
def get_presentation_testing_steps(with_allure: bool = False) -> list:
    scope = "PRESENTATION"
    steps = [
        {"name": "Run All Presentation Tests", "command": build_pytest_command(scope, with_allure)},
    ]
    if with_allure:
        steps.append({"name": "Generate Allure Environment", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "generate_allure_environment.py"}"', "abort_on_fail": False})
    return steps

def handle_platform_actions(platform_key: str):
    """Handles the sub-menu for a selected platform."""
    while True:
        platform_dir = PLATFORM_PATHS.get(platform_key)
        app_exists = platform_dir and platform_dir.exists()

        # Dynamically build the menu based on whether the app exists
        if app_exists:
            sub_menu_choices = [
                Choice(value="run", name="🏃 Run (Start Dev Server)"),
                Separator("--- Testing ---"),
                Choice(value="test", name="Test (Run Unit/Integration Tests)"),
                Choice(value="test_report", name="Test & Report"),
                Separator("--- Management ---"),
                Choice(value="inject_assets", name="🎨 Inject Brand Assets"),
                Choice(value="reset", name="🔄 Reset (Delete & Re-scaffold)"),
                Choice(value="delete", name="❌ Delete (Remove App)"),
                Separator("──────────────────────────────────"),
                Choice(value="back", name="⬅️ Back to Platform Selection"),
            ]
            default_choice = "run"
        else:
            sub_menu_choices = [
                Choice(value="scaffold", name="🏗️  Scaffold (Initial Setup)"),
                Separator("──────────────────────────────────"),
                Choice(value="back", name="⬅️ Back to Platform Selection"),
            ]
            default_choice = "scaffold"

        print_header(f"{platform_key.capitalize()} Platform Actions")
        if supports_interactive_console():
            action_selection = inquirer.select(
                message=f"Select an action for {platform_key.capitalize()}:",
                choices=sub_menu_choices,
                default=default_choice,
                qmark=">",
                cycle=False,
                max_height=12,
            ).execute()
        else:
            print("\nRunning in simplified, non-interactive mode. Please use command-line arguments.")
            break

        if action_selection is None or action_selection == "back":
            break # Go back to main platform selection

        if action_selection == "scaffold":
            print_header(f"{platform_key.capitalize()}: Scaffolding Application")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')
        elif action_selection == "inject_assets":
            print_header(f"{platform_key.capitalize()}: Injecting Brand Assets")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}')
        elif action_selection == "reset":
            print_header(f"{platform_key.capitalize()}: Resetting Application")
            delete_platform(platform_key)
            # Now run the scaffold and inject steps
            print_header(f"{platform_key.capitalize()}: Scaffolding Application")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')
            print_header(f"{platform_key.capitalize()}: Injecting Brand Assets")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}')
        elif action_selection == "delete":
            delete_platform(platform_key)
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
        elif action_selection == "test":
            # Run platform-specific tests without Allure report generation
            steps = get_platform_testing_steps(platform_key, with_allure=False)
            for i, step in enumerate(steps, 1):
                color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
                run_command(step["command"])
        elif action_selection == "test_report":
            # Run platform-specific tests with Allure report generation and serve
            steps = get_platform_testing_steps(platform_key, with_allure=True)
            for i, step in enumerate(steps, 1):
                color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
                run_command(step["command"])
            color_print([("cyan", f"\n--- Step {len(steps) + 1} of {len(steps) + 1}: Serve Report ---")])
            run_command(REPORTING_STEP["command"])

        if supports_interactive_console():
            input("\nPress Enter to continue...")

def main():
    """Main function to present the presentation layer options."""
    # Initialize logging for the admin console itself.
    # The log level will be determined by the DEBUG_MODE from the loaded config.
    setup_logging(debug_mode=config.DEBUG_MODE)
    logger.info(f"Admin console started. DEBUG_MODE is set to: {config.DEBUG_MODE}")
    MENU = [
        # Dynamically create choices from the config whitelist
        *[Choice(value=app_name, name=app_name.capitalize()) for app_name in config.WEB_APP_NAMES],
        Separator("──────────────────────────────────"),
        Choice(value="test_all_presentation", name="Test (All Presentation)"),
        Choice(value="test_all_presentation_report", name="Test & Report (All Presentation)"),
        Choice(value="regression_all_presentation", name="Regression Testing (All Presentation)"),
        Choice(value="regression_all_presentation_report", name="Regression Testing & Report (All Presentation)"),
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
                if selection in config.WEB_APP_NAMES:
                    handle_platform_actions(selection)
                elif selection == "test_all_presentation":
                    steps = get_presentation_testing_steps(with_allure=False)
                    for i, step in enumerate(steps, 1):
                        color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
                        run_command(step["command"])
                elif selection == "test_all_presentation_report":
                    steps = get_presentation_testing_steps(with_allure=True)
                    for i, step in enumerate(steps, 1):
                        color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
                        run_command(step["command"])
                    color_print([("cyan", f"\n--- Step {len(steps) + 1} of {len(steps) + 1}: Serve Report ---")])
                    run_command(REPORTING_STEP["command"])
                elif selection == "regression_all_presentation":
                    steps = CLEANUP_STEPS + get_presentation_testing_steps(with_allure=True)
                    for i, step in enumerate(steps, 1):
                        color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
                        run_command(step["command"])
                elif selection == "regression_all_presentation_report":
                    steps = CLEANUP_STEPS + get_presentation_testing_steps(with_allure=True)
                    for i, step in enumerate(steps, 1):
                        color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
                        run_command(step["command"])
                    color_print([("cyan", f"\n--- Step {len(steps) + 1} of {len(steps) + 1}: Serve Report ---")])
                    run_command(REPORTING_STEP["command"])
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