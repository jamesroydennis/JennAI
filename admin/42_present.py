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
    from admin.presentation_utils import get_platform_paths
    from config.loguru_setup import setup_logging, logger, stop_file_logging, start_file_logging
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator
    from InquirerPy.utils import color_print
except ImportError as e:
    # Differentiate between a missing external package and a broken internal import
    if '.' in e.name: # Likely an internal module (e.g., 'config.loguru_setup')
        print(f"\n\033[91mFATAL ERROR: A required project module is missing or cannot be imported: {e.name}\033[0m")
        print("This usually means the project's directory structure is incomplete (e.g., missing '__init__.py' files).")
        print("\nTo fix this, please run the directory creation script:")
        print(f"  python admin/create_directories.py")
        print("\nThen try running this script again.")
    else: # Likely an external package (e.g., 'InquirerPy')
        print(f"\n\033[91mFATAL ERROR: A required package is missing: {e.name}\033[0m")
        print("This usually means your Conda environment is out of sync with 'environment.yaml'.")
        print("\nTo fix this, please run the environment update script from your 'base' environment:")
        print(f"  1. conda deactivate")
        print(f"  2. python admin/conda_update.py")
    sys.exit(1)

PY_EXEC = f'"{sys.executable}"'
ALLURE_EXEC = "allure" # Assumes Allure CLI is in PATH
console = Console()

def supports_interactive_console():
    """Check if the terminal supports interactive features and colors."""
    return console.is_terminal

def run_command(command: str, cwd: Path = PROJECT_ROOT, abort_on_fail: bool = True) -> bool:
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
        return_code = process.wait()

        if return_code != 0:
            error_msg = f"Command failed with exit code {return_code}: {command}"
            if supports_interactive_console():
                color_print([("red", f"\n❌ {error_msg}")])
            else:
                print(f"\n❌ {error_msg}")
            logger.error(error_msg) # Always log the error
            if abort_on_fail:
                logger.error(error_msg)
                sys.exit(return_code) # Exit with the command's return code
            return False
        else:
            return True
    except Exception as e:
        if supports_interactive_console():
            color_print([("red", f"An error occurred: {e}")])
        else:
            print(f"An error occurred: {e}")
        return False

def print_header(title: str):
    if supports_interactive_console():
        color_print([("cyan", "\n" + "=" * 70)])
        color_print([("cyan", f"{title}")])
        color_print([("cyan", "=" * 70)])
    else:
        print("\n" + "=" * 70)
        print(f"{title}")
        print("=" * 70)

def print_formatted_help(text_block: str):
    """
    Parses and prints a multi-line string as formatted Markdown to the console
    using the 'rich' library.
    """
    # This function is added for consistency with 42.py
    console.print(text_block, markup=False)

# --- Platform Configuration & Helpers ---
PLATFORM_PATHS = get_platform_paths()

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

def _execute_test_steps(steps: list, serve_report: bool = False, is_regression: bool = False):
    """Helper function to execute a list of test-related steps."""
    total_steps = len(steps)
    if serve_report:
        total_steps += 1 # Account for the final report serving step

    for i, step in enumerate(steps, 1):
        color_print([("cyan", f"\n--- Step {i} of {total_steps}: {step['name']} ---")])
        # For regression, cleanup steps are critical and should abort on failure.
        # Test steps should generally not abort the entire console, just report failure.
        abort_on_fail = True if is_regression and step in CLEANUP_STEPS else False
        run_command(step["command"], abort_on_fail=abort_on_fail)

    if serve_report:
        color_print([("cyan", f"\n--- Step {total_steps} of {total_steps}: {REPORTING_STEP['name']} ---")])
        run_command(REPORTING_STEP["command"], abort_on_fail=REPORTING_STEP.get("abort_on_fail", True))

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
                Choice(value="regression_report", name="Regression Test & Report"),
                Separator("--- Management ---"),
                Choice(value="inject_assets", name="🎨 Inject Brand Assets"),
                Choice(value="compile_scss", name="🎨 Compile SCSS"),
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
            # CONTRACTOR delegates to CONSTRUCTOR to build the application from a blueprint.
            print_header(f"{platform_key.capitalize()}: Scaffolding Application")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')

        elif action_selection == "inject_assets":
            # CONTRACTOR delegates to DESIGNER to apply the brand theme.
            print_header(f"{platform_key.capitalize()}: Injecting Brand Assets")
            # Injecting assets is critical, so abort on failure
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}',
                        abort_on_fail=True)
        elif action_selection == "compile_scss":
            # CONTRACTOR delegates to DESIGNER to compile the final styles.
            print_header(f"{platform_key.capitalize()}: Compiling SCSS")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "compile_scss.py"}" --target {platform_key}',
                        abort_on_fail=True)
        elif action_selection == "reset":
            # CONTRACTOR orchestrates a full reset, combining destruction, construction, and design.
            print_header(f"{platform_key.capitalize()}: Resetting Application")
            delete_platform(platform_key)
            print_header(f"{platform_key.capitalize()}: Scaffolding Application")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')
            print_header(f"{platform_key.capitalize()}: Injecting Brand Assets")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}')
            print_header(f"{platform_key.capitalize()}: Compiling SCSS")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "compile_scss.py"}" --target {platform_key}')
        elif action_selection == "delete":
            # CONTRACTOR performs a direct destructive action.
            delete_platform(platform_key)

        elif action_selection == "run":
            # CONTRACTOR orchestrates the execution of the development server.
            print_header(f"Running {platform_key.capitalize()} Dev Server")
            if platform_key == "flask":
                flask_app_path = PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app" / "app.py"
                run_command(f'{PY_EXEC} "{flask_app_path}"')
            elif platform_key == "angular":
                angular_dir = PROJECT_ROOT / "src" / "presentation" / "angular_app"
                if angular_dir.exists():
                    # Use 'npx ng serve' to directly execute the local Angular CLI,
                    # which is more robust if the "start" script is missing from package.json.
                    run_command('npx ng serve --open', cwd=angular_dir)
                else:
                    print(f"Angular project not found at {angular_dir}. Please create it first.")
            elif platform_key == "react":
                react_dir = PROJECT_ROOT / "src" / "presentation" / "react_app"
                if react_dir.exists():
                    run_command('npm start', cwd=react_dir)
                else:
                    print(f"React project not found at {react_dir}. Please create it first.")
            elif platform_key == "vue":
                vue_dir = PROJECT_ROOT / "src" / "presentation" / "vue_app"
                if vue_dir.exists():
                    run_command('npm run dev', cwd=vue_dir)
                else:
                    print(f"Vue project not found at {vue_dir}. Please create it first.")
        elif action_selection == "test":
            # CONTRACTOR orchestrates the test suite for the specific platform.
            # Run platform-specific tests without Allure report generation
            _execute_test_steps(get_platform_testing_steps(platform_key, with_allure=False))
        elif action_selection == "test_report":
            # CONTRACTOR orchestrates the test suite and report generation.
            # Run platform-specific tests with Allure report generation and serve
            _execute_test_steps(get_platform_testing_steps(platform_key, with_allure=True), serve_report=True)
        elif action_selection == "regression_report":
            # CONTRACTOR orchestrates a full regression test for a specific platform.
            print_header(f"{platform_key.capitalize()}: Regression Test & Report")
            # Stop file logging before cleanup to avoid file lock issues
            stop_file_logging()
            steps = CLEANUP_STEPS + get_platform_testing_steps(platform_key, with_allure=True)
            _execute_test_steps(steps, serve_report=True, is_regression=True)
            # Restart file logging after cleanup and tests
            start_file_logging(debug_mode=config.DEBUG_MODE)

HELP_TEXT_PRESENTATION = """
The Presentation Layer Console manages the frontend applications.

--- Platform-Specific Actions (Flask, Angular, etc.) ---
  Select a platform to access its dedicated menu. From there, you can:
  - Scaffold: Create the initial project structure.
  - Run: Start the development server.
  - Test: Run tests for that specific platform.
  - Inject Assets: Apply the central brand theme.
  - Reset: A full delete, scaffold, and asset injection cycle.

--- Global Presentation Actions ---
  Test (All Presentation)
    Runs all tests located in 'src/presentation/tests'.

  Regression Testing (All Presentation)
    Cleans the project, creates directories, and then runs all
    presentation layer tests.

--- Utilities ---
  Initialize/Create Folders
    Ensures the project's directory structure is correct, creating
    any missing folders or '__init__.py' files.
"""

def main():
    """Main function to present the presentation layer options."""
    # This entire console acts as the tool for the CONTRACTOR persona,
    # orchestrating the actions of the CONSTRUCTOR and DESIGNER.

    # --- Environment Sanity Check ---
    # Ensure the script is being run from an allowed conda environment.
    current_env = os.getenv("CONDA_DEFAULT_ENV")
    if not current_env or os.path.basename(current_env) not in config.WHITELIST_ENVIRONMENTS:
        print(f"\n\033[91mFATAL ERROR: Incorrect Conda Environment\033[0m")
        print(f"This admin console MUST be run from one of: {config.WHITELIST_ENVIRONMENTS}")
        print(f"You are currently in the '{current_env or 'None'}' environment.")
        print("\nPlease activate an allowed environment and try again.")
        sys.exit(1)

    # The log level will be determined by the DEBUG_MODE from the loaded config.
    setup_logging(debug_mode=config.DEBUG_MODE)
    logger.info(f"Admin console started. DEBUG_MODE is set to: {config.DEBUG_MODE}")

    # Define menu actions in a structured way, similar to 42.py
    MENU_ACTIONS = [
        {"key": "help", "name": "❓  Help", "is_instruction": True, "help_text": HELP_TEXT_PRESENTATION},
        {"key": "separator", "name": "--- Platforms ---"},
        *[{"key": key, "name": details["display_name"]} for key, details in config.PRESENTATION_APPS.items()],
        {"key": "separator", "name": "--- Global Testing ---"},
        {"key": "test_all_presentation", "name": "Test (All Presentation)"},
        {"key": "test_all_presentation_report", "name": "Test & Report (All Presentation)"},
        {"key": "regression_all_presentation", "name": "Regression Testing (All Presentation)"},
        {"key": "regression_all_presentation_report", "name": "Regression Testing & Report (All Presentation)"},
        {"key": "separator", "name": "--- Utilities ---"},
        {"key": "create_folders", "name": "Initialize/Create Folders"},
    ]

    action_map = {action["key"]: action for action in MENU_ACTIONS}

    while True:
        try:
            if supports_interactive_console():
                # Build choices dynamically for InquirerPy, adding Exit at the top
                choices = [Choice(None, name="🔚  Exit")]
                for action in MENU_ACTIONS:
                    if action.get("key") == "separator":
                        choices.append(Separator(action["name"]))
                    else:
                        choices.append(Choice(value=action["key"], name=action["name"]))

                selection_key = inquirer.select(
                    message="Select a presentation task:",
                    choices=choices,
                    default="flask",
                    qmark=">",
                    cycle=False,
                    max_height=16,
                ).execute()
            else:
                print("\nRunning in simplified, non-interactive mode due to lack of console support.")
                print("Please use command-line arguments to run specific tasks.")
                break # Exit the loop if not interactive

            if selection_key is None: # Handle None for Ctrl+C or 'Exit' choice
                print("\nExiting Presentation Console.")
                break

            selected_action = action_map.get(selection_key)
            if not selected_action:
                print("\nInvalid selection.")
                continue

            try:
                if selected_action.get("is_instruction"):
                    print_header(selected_action["name"])
                    print_formatted_help(selected_action.get("help_text", "No help available."))
                    input("\nPress Enter to return to the menu...")
                elif selection_key in config.PRESENTATION_APPS.keys():
                    handle_platform_actions(selection_key)
                elif selection_key == "test_all_presentation":
                    _execute_test_steps(get_presentation_testing_steps(with_allure=False))
                elif selection_key == "test_all_presentation_report":
                    _execute_test_steps(get_presentation_testing_steps(with_allure=True), serve_report=True)
                elif selection_key == "regression_all_presentation":
                    # Stop file logging before cleanup to avoid file lock issues
                    stop_file_logging()
                    steps = CLEANUP_STEPS + get_presentation_testing_steps(with_allure=True)
                    _execute_test_steps(steps, is_regression=True)
                    # Restart file logging after cleanup and tests
                    start_file_logging(debug_mode=config.DEBUG_MODE)
                elif selection_key == "regression_all_presentation_report":
                    # Stop file logging before cleanup to avoid file lock issues
                    stop_file_logging()
                    steps = CLEANUP_STEPS + get_presentation_testing_steps(with_allure=True)
                    _execute_test_steps(steps, serve_report=True, is_regression=True)
                    # Restart file logging after cleanup and tests
                    start_file_logging(debug_mode=config.DEBUG_MODE)
                elif selection_key == "create_folders":
                    print_header("Initializing Project Folders")
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')
                    input("\nPress Enter to return to the menu...")
                else:
                    print("\nInvalid selection.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                # Do not break; allow the main loop to continue and show the menu again.
                pass
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break

if __name__ == "__main__":
    main()