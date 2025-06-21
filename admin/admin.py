#!/usr/bin/env python
# /home/jdennis/Projects/JennAI/admin/admin.py
"""
PyRepo-Pal Administrative & Regression Testing Orchestrator

**Target Audience:** Software Engineers, DevOps, and Project Maintainers.

**Purpose:**
This script serves as the primary administrative entry point for the PyRepo-Pal
project. It provides a unified, interactive, and user-friendly interface for
executing common development, testing, and maintenance workflows. Its main goal
is to abstract the complexity of multi-step processes (like cleaning, building,
and testing) into a single, reliable command.

**Architectural Philosophy (Vibe Engineering):**
The design of this script adheres to several key software engineering principles:
1.  **Separation of Concerns:** This script is an **orchestrator**, not a worker.
    It does not contain the logic for cleaning files, creating folders, or
    setting up the database. Instead, it imports and calls dedicated, single-
    responsibility scripts for each of these tasks. This makes the overall
    system more modular, maintainable, and easier to debug.
2.  **User-Centric Design:** The script prioritizes developer experience by
    replacing complex command-line flags with an interactive menu powered by
    the `inquirer` library. This reduces cognitive load and minimizes errors.
    The workflow for destructive actions is a prime example: it confirms the
    user's intent for data loss *before* asking for any other configuration,
    respecting the user's decision-making process.
3.  **Configuration over Code:** The script leverages environment variables
    (`PYREPOPAL_ENVIRONMENT`) to control the application's runtime context.
    This allows the core application logic (in `config/config.py`) to remain
    unaware of the testing harness, promoting loose coupling.

**Key Features & Functionality:**

*   **Interactive Menu:** Provides a list of predefined workflows, from simple
    test runs to full project resets.
*   **Environment Selection:** Allows the user to override the default
    application environment (e.g., force 'TEST' mode), which dynamically
    configures aspects like the database connection.
*   **Destructive Action Safety:** Implements a clear, color-coded confirmation
    prompt for any workflow that involves deleting files or database tables,
    preventing accidental data loss.
*   **Modular Workflow Execution:** Sequentially executes a series of steps
    based on the selected mode. The primary steps are:
    1.  **Cleanup:** Deletes logs, caches, and the database.
    2.  **Create:** Rebuilds the folder structure and database schema.
    3.  **Test & Report:** Runs the full `pytest` suite and can generate/open
        an Allure test report.
*   **Visual Feedback:** Concludes by displaying a project tree structure using
    `eza` (if available), providing a clear visual confirmation of the final
    project state.

**Execution Flow:**
1.  **Path Setup:** The script begins by adding the project root to `sys.path`,
    ensuring that all project modules (like `config`, `core`, etc.) can be
    imported reliably.
2.  **Help Flag Check:** It manually checks for `--help` or `-h` arguments to
    provide a static usage guide, as `argparse` is not used for the main
    interactive flow.
3.  **Mode Selection:** The user is prompted to select a regression mode.
4.  **Confirmation (Conditional):** If a 'destroy' mode is selected, the script
    immediately asks for confirmation before proceeding.
5.  **Environment Selection:** The user is prompted to select a runtime
    environment (DEFAULT, DEV, TEST).
6.  **Orchestration:** Based on the selected mode, the script calls the
    necessary functions from other admin modules in the correct order:
    - `admin.cleanup.main()`
    - `admin.create_project_folders.create_folders_and_inits()`
    - `src.data.scripts.sql.setup_database.setup_database()`
    - `admin.report_tests.sh` (via `subprocess`)
    - `admin.tree.run_eza_tree()`
7.  **Exit:** The script exits with a status code of 0 on success or a non-zero
    code on failure.

**Dependencies:**
- **Internal:**
  - `config.loguru_setup`, `config.config`
  - `admin.cleanup`, `admin.create_project_folders`, `admin.tree`
  - `src.data.scripts.sql.setup_database`
- **External:**
  - `inquirer`: For building the interactive command-line menus.
  - `loguru`: For structured and colorful logging.
"""

import argparse
import inquirer # For interactive menus
import subprocess
import shutil
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

def setup_environment_file():
    """
    Checks for .env.example and creates .env from it if it doesn't exist.
    """
    logger.info("Checking for local environment file (.env)...")
    
    # Use the project root defined in this script
    project_root = jennai_root_for_path 
    
    env_example_path = project_root / ".env.example"
    env_path = project_root / ".env"

    if not env_example_path.exists():
        logger.error(f"'.env.example' not found at {env_example_path}. Cannot create .env file.")
        return 1 # Indicate failure

    if env_path.exists():
        logger.info(f"'.env' file already exists at {env_path}. No action taken.")
        return 0 # Indicate success, no action needed

    try:
        shutil.copy(env_example_path, env_path)
        logger.success(f"Successfully created '.env' from '.env.example'.")
        logger.warning("Please open the new '.env' file and add your secret API keys.")
        return 0 # Indicate success
    except Exception as e:
        logger.critical(f"Failed to create '.env' file: {e}")
        return 1 # Indicate failure

def main():
    """
    Main function to parse arguments and run the selected regression mode.
    """
    # --- Manual Help Flag Check ---
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Usage: admin/admin.py

Runs an interactive regression testing suite for the PyRepo-Pal project.
Use the arrow keys to select an option and press Enter.

Modes:
  - Test only:                          Runs pytest.
  - Clean, then Test:                   Cleans artifacts, then runs pytest.
  - Clean, Test, and Report:            Cleans, tests, and generates/opens an Allure report.
  - Destroy, Create, and Test:          Destructive. Resets logs, DB, folders, then tests.
  - Destroy, Create, Test, and Report:  Destructive. Full reset, test, and report.

Environments:
  - DEFAULT: Use environment set by OS (PYREPOPAL_ENVIRONMENT) or 'DEV' default.
  - DEV:     Force the environment to 'DEV' for this run.
  - TEST:    Force the environment to 'TEST' for this run.
""")
        sys.exit(0)

    logger.info("Please use the arrow keys to navigate and Enter to select an option.")
    # --- Interactive Mode & Environment Selection ---
    mode_question = [
        inquirer.List(
            'mode',
            message="Select an administrative task",
            choices=[
                ("Test only: Runs the Pytest test suite.", 'test'),
                # Green color for "Clean" options
                ("\033[92mClean, then Test: Cleans artifacts, then runs Pytest.\033[0m", 'clean-test'),
                ("\033[92mClean, Test, and Report: Cleans, tests, and generates an Allure report.\033[0m", 'clean-test-report'),
                # Orange/Yellow color for "Destroy" options
                ("\033[93mDestroy, Create, and Test: Resets the project and runs tests.\033[0m", 'destroy-create-test'),
                ("\033[93mDestroy, Create, Test, and Report: Full reset, test, and report.\033[0m", 'destroy-create-test-report'),
                ("Initial Project Setup: Run this once for a new clone.", 'setup')
            ],
            default='test'
        )
    ]
    
    mode_answers = inquirer.prompt(mode_question)
    if mode_answers is None:
        logger.info("Operation cancelled by user. Exiting.")
        sys.exit(0)
    mode = mode_answers['mode']

    # Handle the one-time setup mode separately as it has a unique flow.
    if mode == 'setup':
        logger.info("--- Running Initial Project Setup ---")
        if setup_environment_file() != 0:
            logger.error("Failed to set up .env file. Aborting.")
            sys.exit(1)
        if run_cleanup() != 0:
            logger.error("Cleanup failed during setup. Aborting.")
            sys.exit(1)
        run_create_folders()
        # Setup mode should always be a full destroy and create
        if run_setup_db(DATABASE_FILE_PATH, destroy_first=True) != 0:
            logger.error("Database setup failed during setup. Aborting.")
            sys.exit(1)
        
        # New step: Run tests to verify the setup
        logger.info("--- Verifying Setup by Running Tests ---")
        test_command_args = ['bash', 'admin/report_tests.sh', '--no-generate', '--no-open']
        run_command(test_command_args) # This will exit on failure
        logger.success("Verification tests passed successfully.")

        logger.info("--- Displaying Project Tree ---")
        run_eza_tree(jennai_root_for_path)
        logger.success("Initial project setup complete and verified! You can now run other admin tasks.")
        sys.exit(0)

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
        os.environ["PYREPOPAL_ENVIRONMENT"] = environment
        logger.info(f"Environment explicitly set to '{environment}' for this run.")
    else:
        logger.info("Using default environment as determined by config.config (PYREPOPAL_ENVIRONMENT env var or 'DEV').")

    # --- Mode Logic ---
    logger.info(f"Running in mode: '{mode}'")

    # Determine which steps to run based on the mode
    do_cleanup = 'clean' in mode or 'destroy' in mode
    # The 'create' step now only applies to 'destroy' modes.
    do_create = 'destroy' in mode
    do_test = 'test' in mode
    do_report = 'report' in mode

    if do_cleanup:
        logger.info("--- Step 1: Cleaning Project ---")
        # Cleanup now only removes logs and caches, not the DB.
        if run_cleanup() != 0:
            logger.error("Cleanup failed. Aborting.")
            sys.exit(1)

    if do_create:
        logger.info("--- Step 2: Creating Folder Structure ---")
        run_create_folders() # Assumes this doesn't return a status code, but is safe to run
        
        logger.info("--- Step 3: Setting Up Database ---")
        # Only 'destroy' modes will get here. They should drop tables first.
        if run_setup_db(DATABASE_FILE_PATH, destroy_first=True) != 0:
            logger.error("Database setup failed. Aborting.")
            sys.exit(1)

    if do_test:
        # Before running tests, we need to ensure the DB schema exists,
        # especially for 'clean' and 'test' modes where we didn't run the create step.
        if not do_create:
            logger.info("--- Verifying Database Schema ---")
            if run_setup_db(DATABASE_FILE_PATH, destroy_first=False) != 0:
                logger.error("Database schema verification failed. Aborting.")
                sys.exit(1)

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
    logger.info("Loguru setup complete for admin.py.")
    main()