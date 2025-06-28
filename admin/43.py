#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.config import DEBUG_MODE
from config.loguru_setup import setup_logging, logger
from src.validation.validator import validate_admin_environment

try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator
except ImportError:
    print("Error: InquirerPy is not installed or not found in the current environment.")
    print("Please ensure your conda environment is active and the package is installed.")
    print("You can try running: pip install InquirerPy")
    sys.exit(1)

PY_EXEC = f'"{sys.executable}"'
ALLURE_EXEC = "allure"

def run_command(command: str) -> int:
    try:
        # Use Popen to stream output in real-time, which is better for user feedback.
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout to capture all output
            cwd=ROOT,
            text=True,
            encoding="utf-8"
        )
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
            process.stdout.close()
        return process.wait()
    except FileNotFoundError:
        logger.error(f"Error: Command not found for '{command}'. Is it installed and in your PATH?")
        return 1
    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user.")
        return 130 # Standard exit code for Ctrl+C
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return 1

# --- Menu and Action Definitions ---
MENU_ACTIONS = [
    {"key": "separator", "name": "--- Sub-Consoles ---"},
    {
        "key": "present_console",
        "name": "🚀 Launch Presentation Console",
        "steps": [
            {"name": "Launching Presentation Console", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "42_present.py")}"'},
        ]
    },
    {"key": "separator", "name": "--- Testing ---"},
    {
        "key": "test",
        "name": "▶️  Run Pytest",
        "steps": [
            {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest'},
        ]
    },
    {
        "key": "test_and_report",
        "name": "📊 Test & Report",
        "steps": [
            {"name": "Run Tests with Allure", "command": f'{PY_EXEC} -m pytest --alluredir="{str(ROOT / "allure-results")}" --clean-alluredir'},
            {"name": "Serve Allure Report", "command": f'"{ALLURE_EXEC}" serve "{str(ROOT / "allure-results")}"'},
        ]
    },
    {"key": "separator", "name": "--- Regression ---"},
    {
        "key": "regression",
        "name": "🚦 Run Regression Test (Clean, Create Dirs, Test)",
        "steps": [
            {"name": "Cleaning Project", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "cleanup.py")}"'},
            {"name": "Creating Directories", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "create_directories.py")}"'},
            {"name": "Run Tests", "command": f'{PY_EXEC} -m pytest'},
        ]
    },
    {
        "key": "regression_and_report",
        "name": "🚦📊 Run Regression Test & Report",
        "steps": [
            {"name": "Cleaning Project", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "cleanup.py")}"'},
            {"name": "Creating Directories", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "create_directories.py")}"'},
            {"name": "Run Tests with Allure", "command": f'{PY_EXEC} -m pytest --alluredir="{str(ROOT / "allure-results")}" --clean-alluredir'},
            {"name": "Serve Allure Report", "command": f'"{ALLURE_EXEC}" serve "{str(ROOT / "allure-results")}"'},
        ]
    },
    {"key": "separator", "name": "--- Diagnostics & Validation ---"},
    {
        "key": "clean_dry_run",
        "name": "🧹 Preview Project Cleanup (Dry Run)",
        "steps": [
            {"name": "Running Cleanup in Dry Run Mode", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "cleanup.py")}" --dry-run'},
        ]
    },
    {
        "key": "clean_project",
        "name": "🗑️ Clean Project (Deletes Caches & Logs)",
        "steps": [
            {"name": "Cleaning Project", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "cleanup.py")}"'},
        ]
    },
    {
        "key": "context",
        "name": "🖼️ Show Full Context (Env, Config, Tree)",
        "steps": [
            {"name": "Displaying Environment Variables", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "show_env.py")}"'},
            {"name": "Displaying Master Configuration", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "show_config.py")}"'},
            {"name": "Displaying Project Tree", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "tree.py")}"'},
        ]
    },
    {
        "key": "check_deps",
        "name": "✅ Check Dependencies",
        "steps": [
            {"name": "Checking Dependencies", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "check_dependencies.py")}"'},
        ]
    },
    {
        "key": "check_logs",
        "name": "🔎 Check Logs",
        "steps": [
            {"name": "Scanning Project Logs", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "check_logs.py")}"'},
        ]
    },
    {"key": "separator", "name": "--- Individual Views ---"},
    {
        "key": "show_env",
        "name": "🔑 Show Environment Variables",
        "steps": [
            {"name": "Displaying Environment Variables", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "show_env.py")}"'},
        ]
    },
    {
        "key": "show_config",
        "name": "⚙️  Show Master Config",
        "steps": [
            {"name": "Displaying Master Configuration", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "show_config.py")}"'},
        ]
    },
    {
        "key": "tree",
        "name": "🌲 Show Project Tree",
        "steps": [
            {"name": "Displaying Project Tree", "command": f'{PY_EXEC} "{str(ROOT / "admin" / "tree.py")}"'},
        ]
    },
]

def _run_steps(action: dict):
    """Executes the steps for a given menu action."""
    logger.info(f"--- Starting Action: {action['name']} ---")
    steps = action.get("steps", [])
    all_steps_ok = True

    for i, step in enumerate(steps, 1):
        if len(steps) > 1:
            logger.info(f"--- Step {i} of {len(steps)}: {step['name']} ---")

        return_code = run_command(step["command"])

        if return_code != 0:
            all_steps_ok = False
            logger.error(f"❌ Step '{step['name']}' failed with exit code {return_code}. Aborting action.")
            break

    if all_steps_ok:
        logger.success(f"✅ Action '{action['name']}' completed successfully!")
    else:
        logger.warning(f"⚠️ Action '{action['name']}' finished with errors.")

def main():
    # --- LOGGING DISABLED FOR DEMONSTRATION ---
    # The following line, which is part of YOUR application's code, is responsible
    # for creating the 'jennai.log' file. It has been commented out.
    # setup_logging(debug_mode=DEBUG_MODE)
    # logger.info("Admin console started.")
    print("--> NOTE: File logging has been manually disabled in this script. 'jennai.log' will not be created or modified.")

    # --- Environment Validation ---
    is_valid, message = validate_admin_environment()
    if not is_valid:
        logger.error(f"Environment validation failed: {message}")
        logger.error("Please check your setup and try again. Aborting.")
        sys.exit(1)
    logger.success("Environment validation successful.")

    action_map = {action["key"]: action for action in MENU_ACTIONS if action.get("key") != "separator"}

    while True:
        try:
            choices = []
            for action in MENU_ACTIONS:
                if action.get("key") == "separator":
                    choices.append(Separator(action["name"]))
                else:
                    choices.append(Choice(value=action["key"], name=action["name"]))

            choices.append(Separator())
            choices.append(Choice(None, "🔚 Exit"))

            selected_key = inquirer.select(
                message="Select an action:",
                choices=choices,
                default=None,
                cycle=False,
            ).execute()

            if selected_key is None:
                break

            selected_action = action_map.get(selected_key)
            if selected_action:
                _run_steps(selected_action)
                input("\nPress Enter to return to the menu...")
            else:
                logger.error(f"Error: No action found for key '{selected_key}'")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()