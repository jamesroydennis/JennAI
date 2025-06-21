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
    # --- Interactive Mode & Environment Selection ---
    questions = [
        inquirer.List(
            'mode',
            message="Select a regression mode",
            choices=[
                ('Clean artifacts, then Test (no report)', 'clean-test'),
                ('Clean artifacts, Test, then Generate and Open Report', 'clean-test-report'),
                ('Only Run Tests (no report)', 'test'),
                ('Run Tests, then Generate and Open Report', 'test-report'),
                ('Destroy all, Create folders/DB, then Test (no report)', 'destroy-create-test'),
                ('Destroy all, Create folders/DB, Test, and Report', 'destroy-create-test-report')
            ],
            default='clean-test'
        ),
        inquirer.List(
            'environment',
            message="Select the target environment",
            choices=['DEV', 'TEST'],
            default='TEST'
        ),
    ]
    
    answers = inquirer.prompt(questions)

    if answers is None:
        logger.warning("No selection made. Exiting.")
        sys.exit(0)

    mode = answers['mode']
    environment = answers['environment']

    # --- Set Environment Variable ---
    os.environ["JENNAI_ENVIRONMENT"] = environment
    logger.info(f"Environment set to '{environment}'")

    # --- Mode Logic ---
    logger.info(f"Running in mode: '{mode}'")

    # Determine which steps to run based on the mode
    do_cleanup = 'clean' in mode or 'destroy' in mode
    do_create = 'create' in mode
    do_test = 'test' in mode
    do_report = 'report' in mode

    if do_cleanup:
        if 'destroy' in mode:
            warning_prompt = "WARNING: This will destroy the database and all logs. Are you sure?"
            if not confirm_action(warning_prompt):
                logger.warning("Operation cancelled by user.")
                sys.exit(0)
        
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
        report_pytest_args = ['bash', 'admin/report-pytest.sh']
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