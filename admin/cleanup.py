#!/usr/bin/env python


import sys
import shutil
import subprocess
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows centralized modules (config, core) to be imported.
ROOT = Path(__file__).resolve().parent.parent # Go up two levels from admin/script.py to JennAI/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT)) # Insert at the beginning for higher priority


from loguru import logger # Import the logger instance
from config.loguru_setup import setup_logging # Import the setup function

def main():
    """
    Recursively deletes specified Python-related cache folders and other
    temporary folders within the JennAI project root.
    """
    try:
        # Use the standardized ROOT path.
        jennai_root_path = ROOT

        if not jennai_root_path.exists() or not jennai_root_path.is_dir():
            logger.error(f"Project root not found or is not a directory at calculated path: {jennai_root_path}")
            logger.error("Please ensure the script is located in the 'admin' subdirectory of your project.")
            return 1 # Indicate an error

        # This print statement was likely for debugging before logger was integrated.
        # logger.info(f"JennAI Project Root determined as: {jennai_root_path}") # Already logged by setup_logging

        # --- Stop logging to file before deletion ---
        logger.info("Stopping file logging to allow deletion...")
        logger.remove() # Removes all handlers, including the file handler.
        # Re-add a console-only handler to see subsequent messages.
        logger.add(sys.stderr, level="DEBUG") # Assuming we want to maintain verbose output
        logger.info("File logger removed. Continuing cleanup with console-only logging.")
        
        
        # --- Delete jennai.log file ---
        logs_dir = jennai_root_path / "logs"
        
        # List of log files to delete
        log_files_to_delete = [
            "jennai.log",
            "pytest_session.log"
        ]

        for log_fn in log_files_to_delete:
            log_file_path_to_delete = logs_dir / log_fn
            if log_file_path_to_delete.exists() and log_file_path_to_delete.is_file():
                try:
                    log_file_path_to_delete.unlink() # Delete the file
                    logger.info(f"  DELETED log file: {log_file_path_to_delete}")
                except OSError as e:
                    logger.error(f"  Failed to delete log file {log_file_path_to_delete}. Reason: {e}")
            else:
                logger.info(f"Log file '{log_fn}' not found (or not a file), no need to delete: {log_file_path_to_delete}")

        # Define the cache folder names to be removed
        cache_folders_to_remove = [
            '__pycache__',
            '.pytest_cache',
            '.virtual_documents',
            'allure-results', # Add Allure results directory
            'allure-report',  # Add Allure report directory
            '.ipynb_checkpoints' # Add Jupyter Notebook checkpoints
        ]

        logger.info(f"Starting comprehensive cleanup under JennAI root: {jennai_root_path}")

        deleted_count = 0
        for folder_name in cache_folders_to_remove:
            logger.info(f"Searching for and deleting '{folder_name}' folders...")

            # Walk through all directories and files under the root
            for path_object in jennai_root_path.rglob(f"*{folder_name}"): # Use rglob for recursive search
                if path_object.is_dir() and path_object.name == folder_name:
                    try:
                        logger.info(f"  DELETING: {path_object}")
                        shutil.rmtree(path_object)
                        deleted_count += 1
                    except OSError as e:
                        logger.error(f"  Failed to delete {path_object}. Reason: {e}")

        # This print statement can be removed as logger adds its own formatting.
        # print("--------------------------------------------------------")
        if deleted_count > 0:
            logger.success(f"Cleanup complete. {deleted_count} cache folder(s) deleted.")
        else:
            logger.info("Cleanup complete. No cache folders matching the criteria were found to delete.")
        return 0 # Indicate success

    except Exception as e:
        logger.critical(f"An unexpected error occurred during cleanup: {e}")
        return 1 # Indicate an error

if __name__ == "__main__":
    # Setup logging first
    # Pass debug_mode=True or False based on your preference for the cleanup script
    # You might want cleanup to always be verbose, or respect the global config
    # For now, let's assume verbose for a utility script
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for cleanup.py.")

    exit(main()) # Run the cleanup and exit with its code
