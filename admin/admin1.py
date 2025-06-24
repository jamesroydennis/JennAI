#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import color_print

# ==============================================================================
# JennAI Interactive Admin Console (Simplified)
# ==============================================================================
#
# This script provides a user-friendly command-line interface for managing
# and running development tasks for the JennAI project.
#
# ==============================================================================


# --- Configuration ---

# Determine the project root directory (assuming this script is in /admin)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
ALLURE_REPORT_DIR = PROJECT_ROOT / "allure-report"


# --- Helper Functions ---

def print_header(title: str):
    """Prints a styled header to the console."""
    print()
    color_print([("yellow", "=" * 70)])
    color_print([("yellow", f"  {title}")])
    color_print([("yellow", "=" * 70)])
    print()


def run_command(command: str, cwd: Path = PROJECT_ROOT) -> int:
    """
    Runs a command in the shell, streams its output, and returns the exit code.
    """
    try:
        # Use Popen to stream output in real-time, which is better for long tasks.
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=cwd, text=True, encoding='utf-8'
        )
        # Stream the output line by line
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        process.stdout.close()
        return process.wait()
    except FileNotFoundError:
        color_print([("red", f"Error: Command not found for '{command}'. Is it installed and in your PATH?")])
        return 1
    except Exception as e:
        color_print([("red", f"An unexpected error occurred: {e}")])
        return 1

# --- Action Runner ---

def _run_steps(action):
    """Generic function to run a sequence of steps defined in an action dictionary."""
    print_header(action["name"])

    if action.get("confirm", False):
        try:
            confirmed = inquirer.confirm(
                message=action.get("confirm_message", "Are you sure you want to continue?"),
                default=False,
                confirm_message="Confirmed. Starting process...",
                reject_message="Operation cancelled by user."
            ).execute()
            if not confirmed:
                print()
                return
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return

    steps = action["steps"]
    for i, step in enumerate(steps, 1):
        if len(steps) > 1:
            color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])
        
        return_code = run_command(step["command"])
        
        if return_code != 0 and action.get("abort_on_fail", True):
            color_print([("red", f"\n❌ Sequence failed at step '{step['name']}'. Aborting.")])
            return

    color_print([("green", f"\n✅ {action.get('success_message', 'Operation completed successfully!')}")])


# --- Action Definitions ---

PY_EXEC = f'"{sys.executable}"' # Reusable python executable string

MENU_ACTIONS = [
    {"key": "tree", "name": "🌳 Display Project Tree", "steps": [{"name": "Display Tree", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "tree.py"}"'}]},
    {"key": "cleanup", "name": "🧹 Clean-Up Project", "steps": [{"name": "Cleanup", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"'}]},
    {"key": "test", "name": "🧪 Run Tests (No Report)", "steps": [{"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'}]},
    {"key": "test_and_report", "name": "📊 Run Tests & Serve Report", "pause_after": True, "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'},
        {"name": "Serve Report", "command": f'allure serve "{ALLURE_RESULTS_DIR}"', "abort_on_fail": False}
    ]},
    {"key": "create_folders", "name": "🏗️ Create Project Folders", "steps": [{"name": "Create Folders", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_project_folders.py"}"'}]},
    {"key": "regression", "name": "🚀 Run Full Regression", "steps": [
        {"name": "Cleaning Project", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"'},
        {"name": "Creating Project Folders", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_project_folders.py"}"'},
        {"name": "Running Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'}
    ]},
]

# Actions not in the menu can be defined here and called programmatically if needed
HIDDEN_ACTIONS = {
    "install": {"key": "install", "name": "⚙️ Running Project Installation", "confirm": True, "confirm_message": "This will execute 'setup.py', which may perform destructive actions. Continue?", "steps": [{"name": "Run Setup", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "setup.py"}"'}]},
    "destroy_create": {"key": "destroy_create", "name": "💥 Running Full Destroy, Create & Test Sequence", "pause_after": True, "confirm": True, "confirm_message": "WARNING: This is a destructive reset. All logs, reports, and the database will be deleted. Continue?", "steps": [
        {"name": "Cleaning Project", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"'},
        {"name": "Creating Project Folders", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_project_folders.py"}"'},
        {"name": "Setting up Database", "command": f'{PY_EXEC} "{PROJECT_ROOT / "src" / "data" / "scripts" / "sql" / "setup_database.py"}"'},
        {"name": "Displaying Project Tree", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "tree.py"}"', "abort_on_fail": False},
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'},
        {"name": "Serve Report", "command": f'allure serve "{ALLURE_RESULTS_DIR}"', "abort_on_fail": False}
    ]},
}

# --- Main Application ---

def main():
    """Displays the interactive menu and handles user choices."""
    # Combine all actions for the handler, but only menu_actions for the display
    action_map = {action["key"]: action for action in MENU_ACTIONS}
    action_map.update(HIDDEN_ACTIONS)

    while True:
        try:
            # Dynamically create choices from the menu actions list
            choices = [Choice(action["key"], name=action["name"]) for action in MENU_ACTIONS]
            choices.append(Choice(None, name="Exit"))

            selected_key = inquirer.select(
                message="Welcome to the JennAI Admin Console. Select a task:",
                choices=choices,
                default="test",
            ).execute()

            if selected_key is None:
                print("\nGoodbye!")
                break

            selected_action = action_map.get(selected_key)
            if selected_action:
                _run_steps(selected_action)
                if not selected_action.get("pause_after", False):
                    input("\nPress Enter to return to the menu...")
            else:
                # This case should not be reached with the current logic
                color_print([("red", f"Error: No action found for key '{selected_key}'")])
                input("\nPress Enter to return to the menu...")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()