#!/usr/bin/env python
import subprocess
import sys
import os
from pathlib import Path
import shutil
from typing import Optional
from rich.console import Console

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Import config for paths and logging setup
    from config import config
    from config.config import ArchitecturalPersona
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

def _pause_for_acknowledgement(message: str = "\nPress Enter to return to the menu..."):
    """Pauses execution and waits for the user to press Enter."""
    input(message)

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
def build_pytest_command(target: str, with_allure: bool = False, is_scope: bool = True) -> str:
    # Dynamically set verbosity based on the project's DEBUG_MODE
    verbosity_flag = "-v" if config.DEBUG_MODE else "-q -rA"
    target_arg = f"--scope={target}" if is_scope else f'"{target}"'
    base_cmd = f'{PY_EXEC} -m pytest {verbosity_flag} {target_arg}'
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

def get_all_presentation_testing_steps(with_allure: bool = False) -> list:
    """Returns a list of steps to run all presentation tests."""
    steps = [
        {"name": "Run All Presentation Tests", "command": build_pytest_command("PRESENTATION", with_allure)},
    ]
    if with_allure:
        steps.append({"name": "Generate Allure Environment", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "generate_allure_environment.py"}"', "abort_on_fail": False})
    return steps

def _execute_test_steps(steps: list, *, serve_report: bool = False, is_regression: bool = False):
    """
    Helper function to execute a list of test-related steps.
    The '*' makes 'serve_report' and 'is_regression' keyword-only arguments,
    improving call clarity and preventing positional argument errors.
    """
    if is_regression:
        # Display diagnostics only for regression tests
        run_command(f'{PY_EXEC} "{PROJECT_ROOT / "conftest.py"}"')
    else:
        # For non-regression, just show the tree
        run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "tree.py"}"')

    total_steps = len(steps)
    if serve_report:
        total_steps += 1

    for i, step in enumerate(steps, 1):
        color_print([("cyan", f"\n--- Step {i} of {total_steps}: {step['name']} ---")])
        run_command(step["command"], abort_on_fail=step.get("abort_on_fail", True))

    if serve_report:
        color_print([("cyan", f"\n--- Step {total_steps} of {total_steps}: {REPORTING_STEP['name']} ---")])
        run_command(REPORTING_STEP["command"], abort_on_fail=REPORTING_STEP.get("abort_on_fail", True))

HELP_TEXT_PRESENTATION = """
The Presentation Layer Console manages the frontend applications.

Platforms (Flask, Angular, etc.):
  - Scaffold: Creates the initial file and directory structure for a new app.
  - Run: Starts the development server for the selected platform.
  - Test: Runs the unit and integration tests for the platform.
  - Inject Assets: Copies brand assets (logos, themes) into the app.
  - Compile SCSS: Compiles SCSS files into CSS.
  - Reset: Deletes and re-scaffolds the application.
  - Delete: Permanently removes the application directory.

Global Testing:
  - Test (All): Runs tests for all existing presentation layers.
  - Test & Report: Runs all tests and serves an Allure report.
  - Regression: Cleans the project, re-runs all tests, and generates a report.

Utilities:
  - Initialize/Create Folders: Ensures all necessary project directories and
    any missing folders or '__init__.py' files exist.
"""

def _prompt_for_platform(message: str = "Select a platform:") -> Optional[str]:
    """Helper function to prompt the user to select a presentation platform."""
    choices = [Choice(key, name=details["display_name"]) for key, details in config.PRESENTATION_APPS.items()]
    choices.append(Separator())
    choices.append(Choice(value=None, name="⬅️ Back"))
    return inquirer.select(message=message, choices=choices, default="flask").execute()

def handle_architect_menu():
    """Handles the menu for the Architect persona."""
    while True:
        print_header("Architect Menu: Foundational Blueprints & Configuration")
        action = inquirer.select(
            message="Select an Architect action:",
            choices=[
                Choice("show_config", "Show Master Configuration (config.py)"),
                Choice("show_env", "Show Environment Variables (.env)"),
                Choice("create_folders", "Initialize/Create Project Folders"),
                Separator(),
                Choice("critique", "Critique Architect's Plan (test_architect.py)"),
                Choice("verify_blueprints", "Verify All Constructor Blueprints"),
                Separator(),
                Choice(None, "⬅️ Back to Persona Selection"),
            ],
            qmark="🏛️"
        ).execute()

        if action is None: break

        if action == "show_config":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "show_config.py"}"')
        elif action == "show_env":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "check_env_vars.py"}"')
        elif action == "create_folders":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')
        elif action == "critique":
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_architect.py")
            steps = [{"name": "Critiquing Architect's Plan", "command": build_pytest_command(test_file, is_scope=False)}]
            _execute_test_steps(steps=steps)
        elif action == "verify_blueprints":
            steps = [{"name": "Verifying All Constructor Blueprints", "command": build_pytest_command("CONSTRUCTOR_BLUEPRINTS", is_scope=True)}]
            _execute_test_steps(steps=steps)

        _pause_for_acknowledgement()

def handle_contractor_menu():
    """
    Handles the menu for the Contractor persona, who manages the full lifecycle
    of presentation applications.
    """
    while True:
        print_header("Contractor Menu: Application Lifecycle Management")
        platform_key = _prompt_for_platform("Select a platform to manage:")
        if platform_key is None:
            break # User selected "Back"

        handle_platform_actions(platform_key)

def handle_qa_engineer_menu():
    """Handles the menu for the QA Engineer persona."""
    while True:
        print_header("QA Engineer Menu: Testability & Quality Contracts")
        action = inquirer.select(
            message="Select a QA Engineer action:",
            choices=[
                Choice("critique", "Critique Testability & Quality Contracts (test_qa_engineer.py)"),
                Separator(),
                Choice(None, "⬅️ Back to Persona Selection"),
            ],
            qmark="🔬"
        ).execute()

        if action is None: break

        if action == "critique":
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_qa_engineer.py")
            steps = [{"name": "Critiquing Testability & Quality Contracts", "command": build_pytest_command(test_file, is_scope=False)}]
            _execute_test_steps(steps=steps)

        _pause_for_acknowledgement()

def handle_designer_menu():
    """Handles the menu for the Designer persona."""
    while True:
        print_header("Designer Menu: Brand & Style Application")
        action = inquirer.select(
            message="Select a Designer action:",
            choices=[
                Choice("inject", "🎨 Apply Brand to an Application"),
                Choice("compile", "🎨 Compile Styles for an Application"),
                Separator(),
                Choice("critique_compile", "Critique SCSS Compilation (Fast)"),
                Choice("critique", "Critique All Design Work (test_designer.py)"),
                Separator(),
                Choice(None, "⬅️ Back to Persona Selection"),
            ],
            qmark="🖌️"
        ).execute()

        if action is None: break

        if action in ["inject", "compile"]:
            platform_key = _prompt_for_platform(f"Select a platform to '{action}' assets for:")
            if platform_key:
                if action == "inject":
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}', abort_on_fail=True)
                elif action == "compile":
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "compile_scss.py"}" --target {platform_key}', abort_on_fail=True)
        elif action == "critique_compile":
            steps = [{"name": "Critiquing SCSS Compilation Tooling", "command": build_pytest_command("DESIGNER_COMPILE", is_scope=True)}]
            _execute_test_steps(steps=steps)
        elif action == "critique":
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_designer.py")
            steps = [{"name": "Critiquing All Design Work", "command": build_pytest_command(test_file, is_scope=False)}]
            _execute_test_steps(steps=steps)

        _pause_for_acknowledgement()

def _handle_observer_critique_constructors_submenu():
    """Handles the sub-menu for critiquing a specific constructor."""
    while True:
        print_header("Observer: Critique Specific Constructor")

        choices = [
            Choice(value=f"critique_{key}", name=f"Critique CONSTRUCTOR-{key.upper()}", enabled=PLATFORM_PATHS.get(key, Path()).exists())
            for key in config.PRESENTATION_APPS.keys()
        ]
        choices.append(Separator())
        choices.append(Choice(None, "⬅️ Back to Persona Selection"))

        action = inquirer.select(message="Select a constructor's work to critique:", choices=choices, qmark="🧐").execute()
        if action is None: break

        platform_key = action.replace("critique_", "")
        test_file_path = PROJECT_ROOT / "src" / "presentation" / "tests" / f"test_constructor_{platform_key}.py"

        if not test_file_path.exists():
            color_print([("yellow", f"Warning: Test file for {platform_key.upper()} constructor not found at {test_file_path}.")])
            _pause_for_acknowledgement("\nPress Enter to continue...")
            continue

        steps = [{"name": f"Critiquing CONSTRUCTOR-{platform_key.upper()}", "command": build_pytest_command(str(test_file_path), is_scope=False)}]
        _execute_test_steps(steps=steps)

        if not inquirer.confirm(message="Critique another constructor's work?", default=True).execute():
            break

def handle_observer_menu():
    """Handles the menu for the Observer persona, focusing on critiques."""
    while True:
        print_header("Observer Critique Menu")
        choices = [
            Choice("critique_all", "🧐 Critique All Personas (Comprehensive Check)"),
            Separator(),
            Choice("critique_constructors", "🛠️  Critique a specific Constructor's work..."),
            Separator(),
            Choice(None, "⬅️ Back to Persona Selection"),
        ]
        action = inquirer.select(message="Select a critique to perform:", choices=choices, qmark="🧐").execute()

        if action is None: break

        if action == "critique_all":
            steps = [{"name": "Critiquing All Persona Responsibilities", "command": build_pytest_command("PERSONA_CRITIQUES", is_scope=True)}]
            _execute_test_steps(steps=steps)
            _pause_for_acknowledgement()
        elif action == "critique_constructors":
            _handle_observer_critique_constructors_submenu()

# Dispatch dictionary to map persona selections to their handler functions.
# This makes the main loop cleaner and easier to extend.
MENU_HANDLERS = {
    "ARCHITECT": handle_architect_menu,
    "CONTRACTOR": handle_contractor_menu,
    "CONSTRUCTOR": handle_constructor_menu,
    "DESIGNER": handle_designer_menu,
    "QA_ENGINEER": handle_qa_engineer_menu,
    "OBSERVER": handle_observer_menu,
    "legacy": handle_legacy_menu,
    # Add other persona handlers here as they are implemented.
}

def handle_constructor_menu():
    """Handles the menu for the Constructor persona."""
    while True:
        print_header("Constructor Menu: Build Application Skeletons")
        platform_key = _prompt_for_platform("Select a platform to build:")
        if platform_key is None: break

        print_header(f"Constructing {platform_key.capitalize()} Application")
        run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')

        if not inquirer.confirm(message="Build another application?", default=True).execute():
            break

def handle_platform_actions(platform_key: str):
    """
    Handles the lifecycle action sub-menu for a selected platform.
    This function is invoked by the Contractor and the Legacy View.
    """
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
            print_header(f"{platform_key.capitalize()}: Scaffolding Application")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')
        elif action_selection == "inject_assets":
            print_header(f"{platform_key.capitalize()}: Injecting Brand Assets")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}', abort_on_fail=True)
        elif action_selection == "compile_scss":
            print_header(f"{platform_key.capitalize()}: Compiling SCSS")
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "compile_scss.py"}" --target {platform_key}', abort_on_fail=True)
        elif action_selection == "reset":
            print_header(f"{platform_key.capitalize()}: Resetting Application")
            delete_platform(platform_key)
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}')
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "compile_scss.py"}" --target {platform_key}')
        elif action_selection == "delete":
            delete_platform(platform_key)
        elif action_selection == "run":
            print_header(f"Running {platform_key.capitalize()} Dev Server")
            if platform_key == "flask":
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app" / "app.py"}"')
            elif platform_key == "angular":
                run_command('npx ng serve --open', cwd=PLATFORM_PATHS["angular"])
            elif platform_key == "react":
                run_command('npm start', cwd=PLATFORM_PATHS["react"])
            elif platform_key == "vue":
                run_command('npm run dev', cwd=PLATFORM_PATHS["vue"])
        elif action_selection == "test":
            _execute_test_steps(steps=get_platform_testing_steps(platform_key, with_allure=False))
        elif action_selection == "test_report":
            _execute_test_steps(steps=get_platform_testing_steps(platform_key, with_allure=True), serve_report=True)
        elif action_selection == "regression_report":
            print_header(f"{platform_key.capitalize()}: Regression Test & Report")
            stop_file_logging()
            steps = CLEANUP_STEPS + get_platform_testing_steps(platform_key, with_allure=True)
            _execute_test_steps(steps=steps, serve_report=True, is_regression=True)
            start_file_logging(debug_mode=config.DEBUG_MODE)

def handle_legacy_menu():
    """Presents the original, platform-centric menu for backward compatibility."""
    while True:
        original_menu_actions = [
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
        action_map = {action["key"]: action for action in original_menu_actions}

        choices = [Choice(None, name="⬅️ Back to Persona Selection")]
        for action in original_menu_actions:
            if action.get("key") == "separator":
                choices.append(Separator(action["name"]))
            else:
                choices.append(Choice(value=action["key"], name=action["name"]))

        selection_key = inquirer.select(
            message="Select a presentation task (Legacy View):",
            choices=choices,
            default="flask",
            qmark=">",
            cycle=False,
            max_height=16,
        ).execute()

        if selection_key is None: break

        selected_action = action_map.get(selection_key)
        if not selected_action: continue

        if selected_action.get("is_instruction"):
            print_header(selected_action["name"])
            print_formatted_help(selected_action.get("help_text", "No help available."))
            input("\nPress Enter to return to the menu...")
        else: # This else block corrects the indentation error.
            if selection_key in config.PRESENTATION_APPS:
                handle_platform_actions(selection_key)
            elif selection_key == "test_all_presentation":
                _execute_test_steps(steps=get_all_presentation_testing_steps(with_allure=False))
            elif selection_key == "test_all_presentation_report":
                _execute_test_steps(steps=get_all_presentation_testing_steps(with_allure=True), serve_report=True)
            elif selection_key == "regression_all_presentation":
                stop_file_logging()
                _execute_test_steps(steps=CLEANUP_STEPS + get_all_presentation_testing_steps(with_allure=False), is_regression=True)
                start_file_logging(debug_mode=config.DEBUG_MODE)
            elif selection_key == "regression_all_presentation_report":
                stop_file_logging()
                _execute_test_steps(steps=CLEANUP_STEPS + get_all_presentation_testing_steps(with_allure=True), serve_report=True, is_regression=True)
                start_file_logging(debug_mode=config.DEBUG_MODE)
            elif selection_key == "create_folders":
                run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')

def main():
    """Main function to display the interactive menu."""
    logger.info(f"Admin console started. DEBUG_MODE is set to: {config.DEBUG_MODE}")

    if not supports_interactive_console():
        print("\nRunning in simplified, non-interactive mode. Please use command-line arguments.")
        return

    while True:
        print_header("Presentation Layer - Persona-Driven Console")

        persona_choices = [
            Choice(value="exit", name="🔚 Exit"),
            Choice(value="help", name="❓ Help"),
            Separator(),
            *[Choice(value=persona.name, name=persona.name.replace("_", " ").title()) for persona in ArchitecturalPersona],
            Separator(),
            Choice(value="legacy", name="[Legacy Platform View]"),
        ]

        persona_selection = inquirer.select(
            message="Select your persona:",
            choices=persona_choices,
            default="CONSTRUCTOR",
            qmark="👤"
        ).execute()

        if persona_selection == "exit":
            break
        elif persona_selection == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT_PRESENTATION)
            _pause_for_acknowledgement()
        else:
            handler = MENU_HANDLERS.get(persona_selection)
            if handler:
                handler()
            else:
                color_print([("yellow", f"Menu for '{persona_selection}' persona is not yet implemented.")])
                _pause_for_acknowledgement()

if __name__ == "__main__":
    # Setup logging as the first step
    setup_logging(debug_mode=config.DEBUG_MODE)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting console. Goodbye!")
    finally:
        # Ensure the file logging handler is removed on exit
        stop_file_logging()
