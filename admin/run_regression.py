#!/usr/bin/env python
# /home/jdennis/Projects/JennAI/admin/run_regression.py

import argparse
import inquirer # For interactive menus
import subprocess
import sys
from pathlib import Path
import os

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import setup_logging, logger

# Import the main functions from our other admin scripts
from config.config import DATABASE_FILE_PATH
from admin.cleanup import main as run_cleanup
from admin.create_project_folders import create_folders_and_inits as run_create_folders
from src.data.scripts.sql.setup_database import setup_database as run_setup_db
from admin.tree import run_eza_tree

def confirm_action(prompt: str) -> bool:
    """
    Prompts the user for a Y/N confirmation.

    Args:
        prompt: The message to display to the user.

    Returns:
        True if the user confirms, False otherwise.
    """
    while True:
        response = input(f"{prompt} [y/N]: ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']: # Default to No
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def run_command(command_list, check=True):
    """Helper to run a subprocess and handle errors."""
    logger.info(f"Executing command: {' '.join(command_list)}")
    result = subprocess.run(command_list, check=check)
    if result.returncode != 0:
        logger.error(f"Command failed with exit code {result.returncode}: {' '.join(command_list)}")
        sys.exit(result.returncode)
    return result

def main():
    """
    Main function to parse arguments and run the selected regression mode.
    """
    # --- Manual Help Flag Check ---
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Usage: admin/run_regression.py

Runs an interactive regression testing suite for the JennAI project.
Use the arrow keys to select an option and press Enter.

Modes:
  - Test only:                          Runs pytest.
  - Clean, then Test:                   Cleans artifacts, then runs pytest.
  - Clean, Test, and Report:            Cleans, tests, and generates/opens an Allure report.
  - Destroy, Create, and Test:          Destructive. Resets logs, DB, folders, then tests.
  - Destroy, Create, Test, and Report:  Destructive. Full reset, test, and report.

Environments:
  - DEFAULT: Use environment set by OS (JENNAI_ENVIRONMENT) or 'DEV' default.
  - DEV:     Force the environment to 'DEV' for this run.
  - TEST:    Force the environment to 'TEST' for this run.
""")
        sys.exit(0)

    logger.info("Please use the arrow keys to navigate and Enter to select an option.")
    # --- Interactive Mode & Environment Selection ---
    mode_question = [
        inquirer.List(
            'mode',
            message="Select a regression mode",
            choices=[
                ("Test only", 'test'),
                ("Clean, then Test", 'clean-test'),
                ("Clean, Test, and Report", 'clean-test-report'),
                ("Destroy, Create, and Test", 'destroy-create-test'),
                ("Destroy, Create, Test, and Report", 'destroy-create-test-report')
            ],
            default='test'
        )
    ]
    
    mode_answers = inquirer.prompt(mode_question)
    if mode_answers is None:
        logger.info("Operation cancelled by user. Exiting.")
        sys.exit(0)
    mode = mode_answers['mode']

    # If a destructive mode is chosen, prompt for confirmation immediately.
    if 'destroy' in mode:
        # Use ANSI escape codes for red color (\033[91m) and to reset (\033[0m)
        warning_prompt = "\033[91mWARNING: Data loss is imminent. This will restore the project to a clean and functioning state.\033[0m Are you sure?"
        if not confirm_action(warning_prompt):
            logger.warning("Operation cancelled by user.")
            sys.exit(0)

    # Now, prompt for the environment.
    env_question = [
        inquirer.List(
            'environment',
            message="Select the target environment",
            choices=['DEFAULT', 'DEV', 'TEST'],
            default='DEFAULT'
        ),
    ]
    env_answers = inquirer.prompt(env_question)
    if env_answers is None:
        logger.info("Operation cancelled by user. Exiting.")
        sys.exit(0)
    environment = env_answers['environment']

    # --- Set Environment Variable ---
    if environment != 'DEFAULT':
        os.environ["JENNAI_ENVIRONMENT"] = environment
        logger.info(f"Environment explicitly set to '{environment}' for this run.")
    else:
        logger.info("Using default environment as determined by config.config (JENNAI_ENVIRONMENT env var or 'DEV').")

    # --- Mode Logic ---
    logger.info(f"Running in mode: '{mode}'")

    # Determine which steps to run based on the mode
    do_cleanup = 'clean' in mode or 'destroy' in mode
    do_create = 'create' in mode
    do_test = 'test' in mode
    do_report = 'report' in mode

    if do_cleanup:
        logger.info("--- Step 1: Cleaning Project ---")
        if run_cleanup() != 0:
            logger.error("Cleanup failed. Aborting.")
            sys.exit(1)

    if do_create:
        logger.info("--- Step 2: Creating Folder Structure ---")
        run_create_folders() # Assumes this doesn't return a status code, but is safe to run
        
        logger.info("--- Step 3: Setting Up Database ---")
        if run_setup_db(DATABASE_FILE_PATH) != 0: # Pass the path and check for non-zero exit code
            logger.error("Database setup failed. Aborting.")
            sys.exit(1)

    if do_test:
        logger.info("--- Step 4: Running Tests and Reports ---")
        report_pytest_args = ['bash', 'admin/report_tests.sh']
        if not do_report:
            report_pytest_args.extend(['--no-generate', '--no-open'])
        
        run_command(report_pytest_args)

    logger.info("--- Step 5: Displaying Project Tree ---")
    run_eza_tree(jennai_root_for_path)

    logger.success(f"Regression workflow for mode '{mode}' completed successfully.")

if __name__ == "__main__":
    # Setup logging for this script
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for run_regression.py.")
    main()