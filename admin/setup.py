# /home/jdennis/Projects/JennAI/admin/setup.py

import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
jennai_root_for_path = Path(__file__).resolve().parent.parent # Go up two levels from admin/setup.py to JennAI/
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import setup_logging
from loguru import logger

# Import functions from other setup scripts
from admin.create_project_folders import create_folders_and_inits
from admin.cleanup import main as run_cleanup_main, run_eza_tree # Import cleanup functions
from src.data.scripts.sql.setup_database import setup_database as setup_db_schema
from config.config import DATABASE_FILE_PATH

def main_setup():
    """
    Orchestrates all project setup tasks.
    """
    logger.info("Starting main project setup orchestration...")
    all_successful = True

    # --- 1. Run Cleanup Script ---
    logger.info("Step 1: Running cleanup script...")
    try:
        cleanup_exit_code = run_cleanup_main()
        if cleanup_exit_code == 0:
            logger.success("Cleanup completed successfully by cleanup.py.")
        else:
            logger.error("Cleanup script failed. Check logs from cleanup.py for details.")
            all_successful = False # Decide if you want to stop here or continue
            # For a full reset, we might want to stop if cleanup fails.
            # return 1 # Optional: exit immediately if cleanup fails
    except Exception as e:
        logger.critical(f"Cleanup script encountered an unexpected error: {e}")
        all_successful = False

    # --- 2. Create Project Folders and __init__.py files ---
    if all_successful: # Only proceed if previous steps were successful
        logger.info("Step 2: Setting up project folder structure...")
        try:
            create_folders_and_inits() # This function logs its own success/failure
            logger.success("Project folder structure setup completed successfully by create_project_folders.py.")
        except Exception as e:
            logger.critical(f"Project folder setup failed: {e}")
            all_successful = False

    # --- 3. Setup Database Schema ---
    if all_successful: # Only proceed if previous steps were successful
        logger.info("Step 3: Setting up database schema...")
        try:
            db_setup_exit_code = setup_db_schema(DATABASE_FILE_PATH)
            if db_setup_exit_code == 0:
                logger.success("Database schema setup completed successfully by setup_database.py.")
            else:
                logger.error("Database schema setup failed. Check logs from setup_database.py for details.")
                all_successful = False
        except Exception as e:
            logger.critical(f"Database schema setup encountered an unexpected error: {e}")
            all_successful = False

    # --- 4. Display Project Tree ---
    if all_successful: # Optionally, only display tree if all setup steps were successful
        logger.info("Step 4: Displaying project tree with eza...")
        try:
            # jennai_root_for_path is defined globally in this script
            run_eza_tree(jennai_root_for_path)
        except Exception as e:
            logger.error(f"Displaying project tree encountered an unexpected error: {e}")
            # Not necessarily a failure of the setup itself, so 'all_successful' might not be set to False

    if all_successful:
        logger.success("All project setup tasks completed successfully!")
        return 0
    else:
        logger.error("One or more project setup tasks failed. Please review the logs.")
        return 1

if __name__ == "__main__":
    setup_logging(debug_mode=True) # Use DEBUG mode for setup script verbosity
    logger.info("Loguru setup complete for main setup.py orchestrator.")
    sys.exit(main_setup())