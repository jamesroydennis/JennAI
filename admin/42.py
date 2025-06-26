#!/usr/bin/env python
import subprocess
import os
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from config.config import WHITELIST_ENVIRONMENTS, DEBUG_MODE

try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator
    from InquirerPy.utils import color_print  # Still used for headers
    from rich.console import Console
except ImportError:
    print("Error: InquirerPy is not installed or not found in the current environment.")
    print("Please ensure your conda environment is active and the package is installed.")
    print("You can try running: pip install InquirerPy")
    sys.exit(1)

# ==============================================================================

ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"

PROMPT_RETURN_TO_MENU = "\nPress Enter to return to the menu, or Ctrl-C to exit..."

def print_header(title: str):
    print()
    color_print([("cyan", "=" * 70)])
    color_print([("cyan", f"  {title}")])
    color_print([("cyan", "=" * 70)])
    print()

def print_formatted_help(text_block: str):
    """
    Parses and prints a multi-line string as formatted Markdown to the console
    using the 'rich' library.
    """
    console = Console()
    console.print(text_block, markup=False)

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
        try:
            for line in iter(process.stdout.readline, ""):
                print(line, end="")
            return_code = process.wait()
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Terminating subprocess...")
            process.terminate()
            return_code = process.wait()
            return 0
        process.stdout.close()
        return return_code
    except FileNotFoundError:
        color_print([("red", f"Error: Command not found for '{command}'. Is it installed and in your PATH?")])
        return 1
    except Exception as e:
        color_print([("red", f"An unexpected error occurred: {e}")])
        return 1

def _run_steps(action):
    if action.get("key") == "separator":
        return

    print_header(action["name"])

    if action.get("confirm", False):
        try:
            confirm_message = action.get("confirm_message", "Are you sure you want to continue?")
            confirmed = inquirer.confirm(
                message=confirm_message,
                default=False,
            ).execute()
            if not confirmed:
                print()
                return

            if action.get("key") == "full_reset":
                final_confirm_message = (
                    "FINAL WARNING: This is your last chance to back out.\n"
                    "The 'jennai-root' environment and project data WILL BE DELETED.\n\n"
                    "Are you absolutely sure you want to proceed with destruction?"
                )
                final_confirmed = inquirer.confirm(message=final_confirm_message, default=False).execute()
                if not final_confirmed:
                    print("\nOperation cancelled by user at final confirmation.")
                    return
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return

    steps = action.get("steps", [])
    all_steps_ok = True
    for i, step in enumerate(steps, 1):
        if len(steps) > 1:
            color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])

        return_code = run_command(step["command"])
        if return_code != 0:
            all_steps_ok = False
            if step.get("abort_on_fail", True):
                color_print([("red", f"\n❌ Sequence failed at step '{step['name']}'. Aborting.")])
                return

    if all_steps_ok:
        color_print([("green", f"\n✅ {action.get('success_message', 'Operation completed successfully!')}")])
    else:
        color_print([("yellow", f"\n⚠️  Operation completed, but with non-critical errors.")])

PY_EXEC = f'"{sys.executable}"'
ALLURE_EXEC = "allure"

HELP_TEXT = """
The JennAI Admin Console provides the following commands:

--- Testing ---
  Test
    Runs the full test suite using `pytest`. Generates raw Allure data
    for later analysis but does not launch the report server.

  Test & Report
    Runs the full test suite and then immediately launches the Allure
    web server to display an interactive report of the results.

  Regression Testing
    A comprehensive check. It first cleans the project of old artifacts
    (logs, caches, old reports), then runs the full test suite.

  Regression Testing & Report
    The most complete check. Cleans the project, runs all tests, and
    then serves the Allure report for immediate review.

--- Diagnostics & Utilities ---
  Check Logs
    Scans the project's log files (e.g., jennai.log) for any lines
    containing "ERROR" or "WARNING" to help quickly diagnose issues.

  Full-Tree
    Displays a visual tree of the project's directory structure.
    Uses the 'eza' command if available for a detailed, colorized view,
    otherwise falls back to a basic display.

  Clean
    Removes temporary files and folders generated by Python and testing,
    such as __pycache__, .pytest_cache, and previous Allure report data.

  Build Website CSS
    Performs a one-time compilation of the project's SCSS files into CSS.
    This is useful for production builds or manual updates.

  Initialize/Create Folders
    Creates the standard project directory structure as defined in the
    project's configuration. Useful for initial setup or after a clean.

--- Presentation Layer ---
  Presentation Layer Console
    Launches a dedicated sub-menu for scaffolding and managing
    different presentation layers (Flask, Angular, React).

  Mock Data install
    Launches an interactive console to create or destroy the mock LLM
    data and the corresponding SQLite database.

--- Environment Management (Advanced) ---
  Update Conda Environment
    Synchronizes your 'jennai-root' conda environment with the 'environment.yaml' file.

  Reset
    DANGER: Executes a script that completely removes and reinstalls the conda environment.
"""

MENU_ACTIONS = [
    {"key": "help", "name": "❓  Help", "is_instruction": True, "help_text": HELP_TEXT},
    {"key": "separator", "name": "──────────────────────────────────"},
    {"key": "test", "name": "Test", "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest src/business/tests src/data/tests tests/test_00_system_dependencies.py tests/test_cuda.py tests/test_main_integration.py --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'}
    ]},
    {"key": "test_and_report", "name": "Test & Report", "pause_after": True, "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest src/business/tests src/data/tests tests/test_00_system_dependencies.py tests/test_cuda.py tests/test_main_integration.py --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'},
        {"name": "Serve Report", "command": f'"{ALLURE_EXEC}" serve "{str(ALLURE_RESULTS_DIR)}"', "abort_on_fail": False} 
    ]},
    {"key": "regression", "name": "Regression Testing", "steps": [
        {"name": "Cleaning Project", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "cleanup.py")}"'},
        {"name": "Creating Directories", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "create_directories.py")}"'},
        {"name": "Running Tests", "command": f'{PY_EXEC} -m pytest src/business/tests src/data/tests tests/test_00_system_dependencies.py tests/test_cuda.py tests/test_main_integration.py --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'}
    ]},
    {"key": "regression_and_report", "name": "Regression Testing & Report", "pause_after": True, "steps": [
        {"name": "Cleaning Project", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "cleanup.py")}"'},
        {"name": "Creating Directories", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "create_directories.py")}"'},
        {"name": "Running Tests", "command": f'{PY_EXEC} -m pytest src/business/tests src/data/tests tests/test_00_system_dependencies.py tests/test_cuda.py tests/test_main_integration.py --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'},
        {"name": "Serve Report", "command": f'"{ALLURE_EXEC}" serve "{str(ALLURE_RESULTS_DIR)}"', "abort_on_fail": False}
    ]},
    {"key": "separator", "name": "──────────────────────────────────"},
    {"key": "check_logs", "name": "Check Logs", "steps": [
        {"name": "Scan Logs", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "check_logs.py")}"'}]},
    {"key": "tree", "name": "Full-Tree", "steps": [
        {"name": "Display Tree", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "tree.py")}"'}]},
    {"key": "cleanup", "name": "Clean Project", "steps": [
        {"name": "Run Cleanup Script", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "cleanup.py")}"'}]},
    {"key": "create_folders", "name": "Initialize/Create Folders", "steps": [
        {"name": "Create Directories", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "create_directories.py")}"'}]},
    {"key": "separator", "name": "──────────────────────────────────"},
    # --- Presentation Layer ---
    {"key": "presentation_console", "name": "🎨 Presentation Layer Console", "pause_after": True, "steps": [{"name": "Launch Presentation Console", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "42_present.py"}"', "abort_on_fail": False}]},
    {"key": "mock_data_install", "name": "💾 Mock Data install", "pause_after": True, "steps": [{"name": "Run Mock Data Creation", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_mock_data.py"}"', "abort_on_fail": False}]},
]

HIDDEN_ACTIONS = {
    "install": {"key": "install", "name": "Run Project Installation (setup.py)", "confirm": True,
     "confirm_message": "This will execute 'setup.py', which may perform destructive actions. Continue?",
     "steps": [{"name": "Run Setup", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "setup.py")}"'}]},
    "conda_update": {"key": "conda_update", "name": "Update Conda Environment", "confirm": True,
     "confirm_message": (
         "This will synchronize your Conda environment with 'environment.yaml'.\n"
         "IMPORTANT: This should be run from your 'base' environment for best results.\n\n"
         "Continue?"
     ),
     "steps": [{"name": "Run Conda Update", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "conda_update.py")}"'}]},
    "full_reset": {"key": "full_reset", "name": "Reset", "confirm": True, "pause_after": True,
     "confirm_message": "This action performs a full destruction of data and the conda environment. You will be directed to a reset script where deletion, reset, and re-creation will begin.",
     "steps": [
         {"name": "Run Full Reset", "command": f'"{PROJECT_ROOT / "full_reset.bat"}"'}
     ]}
}

def main():
    # --- Environment Sanity Check ---
    # Ensure the script is being run from an allowed conda environment.
    current_env = os.getenv("CONDA_DEFAULT_ENV")
    if not current_env or os.path.basename(current_env) not in WHITELIST_ENVIRONMENTS:
        print(f"\n\033[91mFATAL ERROR: Incorrect Conda Environment\033[0m")
        print(f"This admin console MUST be run from one of: {WHITELIST_ENVIRONMENTS}")
        print(f"You are currently in the '{current_env or 'None'}' environment.")
        print("\nPlease activate an allowed environment and try again.")
        sys.exit(1)

    action_map = {action["key"]: action for action in MENU_ACTIONS}
    action_map.update(HIDDEN_ACTIONS)

    while True:
        try:
            choices = []
            choices.append(Choice(None, name="🔚  Exit"))
            for action in MENU_ACTIONS:
                if action.get("key") == "separator":
                    choices.append(Separator(action["name"]))
                else:
                    choices.append(Choice(value=action["key"], name=action["name"]))

            selected_key = inquirer.select(
                message="Welcome to the JennAI Admin Console. Select a task:",
                choices=choices,
                default="test",
                qmark="",
                cycle=False,
                max_height=16,
            ).execute()

            if selected_key is None:
                print("\nGoodbye!")
                break

            selected_action = action_map.get(selected_key)
            if selected_action:
                if selected_action.get("is_instruction"):
                    print_header(selected_action["name"])
                    help_text = selected_action.get("help_text")
                    if help_text:
                        print_formatted_help(help_text)
                    input(PROMPT_RETURN_TO_MENU)
                else:
                    _run_steps(selected_action)
                    if not selected_action.get("pause_after", False):
                        input(PROMPT_RETURN_TO_MENU)
            else:
                color_print([("red", f"Error: No action found for key '{selected_key}'")])
                input(PROMPT_RETURN_TO_MENU)

        except KeyboardInterrupt:
            print("\n\nOperation cancelled. Restarting admin console...")
            sys.exit(1)

if __name__ == "__main__":
    main()