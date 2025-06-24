#!/usr/bin/env python
import subprocess
import os
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

PROMPT_RETURN_TO_MENU = "\nPress Enter to return to the menu, or Ctrl-C to exit..."

def print_header(title: str):
    print()
    color_print([("cyan", "=" * 70)])
    color_print([("cyan", f"  {title}")])
    color_print([("cyan", "=" * 70)])
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
            ).execute()
            if not confirmed:
                print()
                return

            # Add a special, secondary confirmation for the most destructive actions
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
# Construct a robust path to the allure executable inside the current environment.
# This avoids relying on the system's PATH, which can be unreliable in sub-processes.
# On Windows, executables are in the 'Scripts' subdirectory of the env. On Unix-like systems, they are in 'bin'.
# Use system-wide Allure CLI installed by Scoop (relies on PATH)
ALLURE_EXEC = "allure"

MENU_ACTIONS = [
    {"key": "test", "name": "Test", "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'}]},
    {"key": "test_and_report", "name": "Test & Report", "pause_after": True, "steps": [
        {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'},
        {"name": "Serve Report", "command": f'"{ALLURE_EXEC}" serve "{str(ALLURE_RESULTS_DIR)}"', "abort_on_fail": False}
    ]},
    {"key": "check_logs", "name": "Check Logs", "steps": [
        {"name": "Scan Logs", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "check_logs.py")}"'}]}, # Already correct
    {"key": "tree", "name": "Full-Tree", "steps": [
        {"name": "Display Tree", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "tree.py")}"'}]},
    {"key": "cleanup", "name": "Clean", "steps": [ # Already correct
        {"name": "Cleanup", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "cleanup.py")}"'}]}, # Already correct
    {"key": "create_folders", "name": "Initialize/Create Folders", "steps": [
        {"name": "Create Folders", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "create_project_folders.py")}"'}]}, # Already correct
    {"key": "regression", "name": "Run Full Regression", "steps": [
        {"name": "Cleaning Project", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "cleanup.py")}"'},
        {"name": "Creating Project Folders", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "create_project_folders.py")}"'},
        {"name": "Running Tests", "command": f'{PY_EXEC} -m pytest --alluredir="{str(ALLURE_RESULTS_DIR)}" --clean-alluredir'}
    ]},
    {"key": "conda_update", "name": "Update Conda Environment", "confirm": True,
     "confirm_message": (
         "This will synchronize your Conda environment with 'environment.yaml'.\n"
         "IMPORTANT: This should be run from your 'base' environment for best results.\n\n"
         "Continue?"
     ),
     "steps": [{"name": "Run Conda Update", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "conda_update.py")}"'}]}
]

HIDDEN_ACTIONS = {
    "install": {"key": "install", "name": "Run Project Installation (setup.py)", "confirm": True,
     "confirm_message": "This will execute 'setup.py', which may perform destructive actions. Continue?",
     "steps": [{"name": "Run Setup", "command": f'{PY_EXEC} "{str(PROJECT_ROOT / "admin" / "setup.py")}"'}]},
    "full_reset": {"key": "full_reset", "name": "Full Destroy & Create", "confirm": True, "pause_after": True,
     "confirm_message": "This action performs a full destruction of data and the conda environment. You will be directed to a reset script where deletion, reset, and re-creation will begin.",
     "steps": [
         {"name": "Run Full Reset", "command": f'"{PROJECT_ROOT / "full_reset.bat"}"'}
     ]}
}


def main():
    # --- Environment Sanity Check ---
    # Ensure the script is being run from the correct conda environment.
    # This prevents a whole class of "module not found" errors by ensuring
    # that sys.executable points to the correct interpreter.
    expected_env_name = "jennai-root"
    current_env = os.getenv("CONDA_DEFAULT_ENV")

    if not current_env or os.path.basename(current_env) != expected_env_name:
        print(f"\n\033[91mFATAL ERROR: Incorrect Conda Environment\033[0m")
        print(f"This admin console MUST be run from the '{expected_env_name}' environment.")
        print(f"You are currently in the '{current_env or 'None'}' environment.")
        print("\nPlease activate the correct environment and try again:")
        print(f"  conda activate {expected_env_name}")
        sys.exit(1)

    action_map = {action["key"]: action for action in MENU_ACTIONS}
    action_map.update(HIDDEN_ACTIONS)

    while True:
        try:
            # Build the list of choices for the menu, handling the separator.
            choices = []
            choices.append(Choice(None, name="Exit")) # Exit is always the first option
            for action in MENU_ACTIONS: # Then add all other defined menu actions
                if action.get("key") == "separator":
                    choices.append(Separator(action["name"]))
                else:
                    choices.append(Choice(value=action["key"], name=action["name"]))

            selected_key = inquirer.select(
                message="Welcome to the JennAI Admin Console. Select a task:",
                choices=choices,
                default="test",
                qmark="", # This parameter is supported in InquirerPy >= 0.5.0
            ).execute()

            if selected_key is None:
                print("\nGoodbye!")
                break

            selected_action = action_map.get(selected_key)
            if selected_action:
                if selected_action.get("is_instruction"):
                    print_header(selected_action["name"])
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
            # Removed os.execv to allow normal script termination on Ctrl-C
            sys.exit(1) # Exit with an error code to indicate interruption


if __name__ == "__main__":
    main()