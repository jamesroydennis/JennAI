# /home/jdennis/Projects/JennAI/admin/cleanup.py

import sys
import shutil
import subprocess
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows centralized modules (config, core) to be imported.
jennai_root_for_path = Path(__file__).resolve().parent.parent # Go up two levels from admin/script.py to JennAI/
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path)) # Insert at the beginning for higher priority


from loguru import logger # Import the logger instance
from config.loguru_setup import setup_logging # Import the setup function
from config.config import DATABASE_FILE_PATH # Import the database path

def main():
    """
    Recursively deletes specified Python-related cache folders and other
    temporary folders within the JennAI project root.
    """
    try:
        # Determine the JennAI project root dynamically.
        # Assumes this script is in 'JennAI/admin/'.
        # script_dir is already used for jennai_root_for_path, we can reuse that
        script_dir = jennai_root_for_path / "admin" # .../JennAI/admin
        jennai_root_path = script_dir.parent          # .../JennAI

        if not jennai_root_path.exists() or not jennai_root_path.is_dir():
            logger.error(f"JennAI project root not found or is not a directory at calculated path: {jennai_root_path}")
            logger.error("Please ensure the script is located in the 'admin' subdirectory of your project.")
            return 1 # Indicate an error

        # This print statement was likely for debugging before logger was integrated.
        # logger.info(f"JennAI Project Root determined as: {jennai_root_path}") # Already logged by setup_logging

        # --- Delete jennai.log file ---
        # Also add the database file to the list of files to delete
        logs_dir = jennai_root_path / "logs"
        
        # List of files to delete (logs and database)
        files_to_delete = [logs_dir / "jennai.log", DATABASE_FILE_PATH]

        for file_path_to_delete in files_to_delete:
            if file_path_to_delete.exists() and file_path_to_delete.is_file():
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
            'allure-report'   # Add Allure report directory
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

def run_eza_tree(project_root: Path):
    """
    Attempts to run 'eza --tree' and prints its output using the logger.
    """
    logger.info("Attempting to display project tree with 'eza --tree'...")
    try:
        # Check if eza is installed by trying to get its version
        subprocess.run(["eza", "--version"], check=True, capture_output=True, text=True)
        
        # Run eza --tree
        result = subprocess.run(["eza", "--tree"], cwd=project_root, check=True, capture_output=True, text=True)
        # Print eza tree output directly to console, not to the log file.
        print("\n------------------- Project Tree (eza) -------------------")
        print(result.stdout.strip())
        print("--------------------------------------------------------")
        logger.info("Successfully displayed project tree using 'eza --tree'.")
    except FileNotFoundError:
        logger.warning("'eza' command not found. Skipping tree view. Please install eza to use this feature.")
    except subprocess.CalledProcessError as e:
        logger.error(f"'eza --tree' command failed with error: {e}")
        logger.error(f"  Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while trying to run 'eza --tree': {e}")

if __name__ == "__main__":
    # Determine project root once for both functions
    # jennai_root_for_path is already defined globally and points to the project root
    jennai_root_path_main = jennai_root_for_path

    # Setup logging first
    # Pass debug_mode=True or False based on your preference for the cleanup script
    # You might want cleanup to always be verbose, or respect the global config
    # For now, let's assume verbose for a utility script
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for cleanup.py.")

    exit(main()) # Run the cleanup and exit with its code
