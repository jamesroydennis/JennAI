#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

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

# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"

def print_header(title: str):
    print()
    color_print([("yellow", "=" * 70)])
    color_print([("yellow", f"  {title}")])
    color_print([("yellow", "=" * 70)])
    print()

def run_command(command: str, cwd: Path = PROJECT_ROOT) -> int:
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=cwd, text=True, encoding='utf-8'
        )
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

def _run_steps(action):
    if action.get("key") == "separator":
        return

    print_header(action["name"])

    if action.get("confirm", False):
        try:
            confirm_message = action.get("confirm_message", "Are you sure you want to continue?")
            confirmed = inquirer.confirm(
                message=confirm_message, # InquirerPy can handle styled lists of tuples directly
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

    steps = action.get("steps", [])
    for i, step in enumerate(steps, 1):
        if len(steps) > 1:
            color_print([("cyan", f"\n--- Step {i} of {len(steps)}: {step['name']} ---")])

        return_code = run_command(step["command"])
        if return_code != 0 and step.get("abort_on_fail", True):
            color_print([("red", f"\n❌ Sequence failed at step '{step['name']}'. Aborting.")])
            return

    color_print([("green", f"\n✅ {action.get('success_message', 'Operation completed successfully!')}")])

PY_EXEC = f'"{sys.executable}"'

MENU_ACTIONS = [
    {"key": "test", "name": "🧪    Run Tests (No Report)", "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR.as_posix()}" --clean-alluredir'}]},
    {"key": "check_logs", "name": "🔎    Check Logs for Errors/Warnings", "steps": [
        {"name": "Scan Logs", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "check_logs.py").as_posix()}"'}]},
    {"key": "tree", "name": "🌳    Display Project Tree", "steps": [
        {"name": "Display Tree", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "tree.py").as_posix()}"'}]},
    {"key": "cleanup", "name": "🧹    Clean-Up Project", "steps": [
        {"name": "Cleanup", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "cleanup.py").as_posix()}"'}]},
    {"key": "test_and_report", "name": "📊    Run Tests & Serve Report", "pause_after": True, "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR.as_posix()}" --clean-alluredir'},
        {"name": "Serve Report", "command": f'allure serve "{ALLURE_RESULTS_DIR.as_posix()}"', "abort_on_fail": False}
    ]},
    {"key": "create_folders", "name": "🏗️    Create Project Folders", "steps": [
        {"name": "Create Folders", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "create_project_folders.py").as_posix()}"'}]},
    {"key": "regression", "name": "🚀    Run Full Regression", "steps": [
        {"name": "Cleaning Project", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "cleanup.py").as_posix()}"'},
        {"name": "Creating Project Folders", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "create_project_folders.py").as_posix()}"'},
        {"name": "Running Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{ALLURE_RESULTS_DIR.as_posix()}" --clean-alluredir'}
    ]},
    {"key": "conda_update", "name": "🐍    Update Conda Environment", "confirm": True,
     "confirm_message": [
         ("class:warning", "This will synchronize your Conda environment with 'environment.yaml'.\n"),
         ("class:warning", "IMPORTANT: This should be run from your 'base' environment for best results.\n"),
         ("class:default", "Continue?")
     ],
     "steps": [{"name": "Run Conda Update", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "conda_update.py").as_posix()}"'}]},
    # Add a separator for more critical/destructive actions (not selectable)
    {"key": "separator", "name": "-"*30},
    {"key": "full_reset", "name": "💥    Full Destroy & Create", "confirm": True, "pause_after": True,
     "confirm_message": "This action performs a full destruction of data and conda environment. You will be directed to a reset script where deletion, reset, and re-creation will begin.",
     "steps": [
         {"name": "Run Full Reset", "command": f'"{PROJECT_ROOT / "full_reset.bat"}"'}
     ]
    }
]

HIDDEN_ACTIONS = {
    "install": {"key": "install", "name": "⚙️    Run Project Installation (setup.py)", "confirm": True,
     "confirm_message": [("class:warning", "This will execute 'setup.py', which may perform destructive actions. Continue?")],
     "steps": [{"name": "Run Setup", "command": f'{PY_EXEC} "{(PROJECT_ROOT / "admin" / "setup.py").as_posix()}"'}]}
}


def main():
    action_map = {action["key"]: action for action in MENU_ACTIONS}
    action_map.update(HIDDEN_ACTIONS)

    while True:
        try:
            # Build the list of choices for the menu, handling the separator.
            choices = []
            for action in MENU_ACTIONS:
                if action.get("key") == "separator":
                    choices.append(Separator(action["name"]))
                else:
                    choices.append(Choice(value=action["key"], name=action["name"]))
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
                if selected_action.get("is_instruction"):
                    print_header(selected_action["name"])
                    input("\nPress Enter to return to the menu...")
                else:
                    _run_steps(selected_action)
                    if not selected_action.get("pause_after", False):
                        input("\nPress Enter to return to the menu...")
            else:
                color_print([("red", f"Error: No action found for key '{selected_key}'")])
                input("\nPress Enter to return to the menu...")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()