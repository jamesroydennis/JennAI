#!/usr/bin/env python


import sys
import os
import shutil
from pathlib import Path
import argparse

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows centralized modules (config, core) to be imported.
ROOT = Path(__file__).resolve().parent.parent # Go up two levels from admin/script.py to JennAI/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT)) # Insert at the beginning for higher priority

from loguru import logger # Import the logger instance
from config import config
from config.loguru_setup import setup_logging, stop_file_logging

def get_size(start_path: Path) -> int:
    """Calculates the size of a directory or a file in bytes."""
    if start_path.is_file():
        return start_path.stat().st_size
    if start_path.is_dir():
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    return 0

def main(args):
    """
    Recursively deletes specified Python-related cache folders and other
    temporary folders within the JennAI project root.
    """
    try:
        if args.dry_run:
            logger.info("--- DRY RUN MODE ACTIVATED ---")
            logger.info("No files will be deleted. Calculating potential space savings...")
        # Use the standardized ROOT path.
        jennai_root_path = config.ROOT

        if not jennai_root_path.exists() or not jennai_root_path.is_dir():
            logger.error(f"Project root not found or is not a directory at calculated path: {jennai_root_path}")
            logger.error("Please ensure the script is located in the 'admin' subdirectory of your project.")
            return 1 # Indicate an error
        # --- Stop logging to file before deletion, keeping console logging active ---
        logger.info("Stopping file logging to allow deletion of the logs directory...")
        stop_file_logging()
        logger.info("File logging handler removed. Cleanup will proceed with console-only logging.")

        total_space_to_be_freed = 0
        deleted_items_count = 0

        # --- Clean out the entire logs directory ---
        logs_dir = config.LOGS_DIR
        if logs_dir.is_dir():
            logger.info(f"Cleaning all files from log directory: {logs_dir}")
            for item in logs_dir.iterdir():
                if item.is_file():
                    file_size = get_size(item)
                    total_space_to_be_freed += file_size
                    deleted_items_count += 1
                    if args.dry_run:
                        logger.info(f"  WOULD DELETE log file: {item.name} ({file_size/1024:.2f} KB)")
                    else:
                        try:
                            logger.info(f"  DELETING log artifact: {item.name}")
                            item.unlink()
                        except OSError as e:
                            logger.error(f"  Failed to delete log artifact {item}. Reason: {e}")

        # --- Delete configured top-level directories by their absolute path ---
        configured_dirs_to_remove = [
            config.ALLURE_RESULTS_DIR,
            config.ALLURE_REPORT_DIR,
        ]
        for dir_path in configured_dirs_to_remove:
            if dir_path.is_dir():
                dir_size = get_size(dir_path)
                total_space_to_be_freed += dir_size
                deleted_items_count += 1
                if args.dry_run:
                    logger.info(f"  WOULD DELETE configured directory: {dir_path} ({dir_size/1024/1024:.2f} MB)")
                else:
                    try:
                        logger.info(f"  DELETING configured directory: {dir_path}")
                        shutil.rmtree(dir_path)
                    except OSError as e:
                        logger.error(f"  Failed to delete {dir_path}. Reason: {e}")

        # --- Recursively find and delete common cache folders by name ---
        cache_folders_to_find_and_remove = [
            '__pycache__',
            '.pytest_cache',
            '.virtual_documents',
            '.ipynb_checkpoints', # Add Jupyter Notebook checkpoints
            'node_modules',       # For Node.js dependencies (can be very large)
            'dist',               # Common build output directory
            'build',              # Common build output directory
            '.angular',           # Angular cache directory
        ]

        logger.info(f"Starting comprehensive cleanup under JennAI root: {jennai_root_path}")
        for folder_name in cache_folders_to_find_and_remove:
            logger.info(f"Searching for and deleting '{folder_name}' folders...")
            # Walk through all directories and files under the root
            for path_object in jennai_root_path.rglob(f"*{folder_name}"): # Use rglob for recursive search
                if path_object.is_dir() and path_object.name == folder_name:
                    dir_size = get_size(path_object)
                    total_space_to_be_freed += dir_size
                    deleted_items_count += 1
                    if args.dry_run:
                        logger.info(f"  WOULD DELETE: {path_object} ({dir_size/1024/1024:.2f} MB)")
                    else:
                        try:
                            logger.info(f"  DELETING: {path_object}")
                            shutil.rmtree(path_object)
                        except OSError as e:
                            logger.error(f"  Failed to delete {path_object}. Reason: {e}")

        if args.dry_run:
            logger.success("--- DRY RUN SUMMARY ---")
            logger.success(f"Found {deleted_items_count} items to delete.")
            logger.success(f"A total of {total_space_to_be_freed / 1024 / 1024:.2f} MB would be freed.")
        else:
            if deleted_items_count > 0:
                logger.success(f"Cleanup complete. {deleted_items_count} item(s) deleted.")
            else:
                logger.info("Cleanup complete. No items matching the criteria were found to delete.")
        return 0 # Indicate success

    except Exception as e:
        logger.critical(f"An unexpected error occurred during cleanup: {e}")
        return 1 # Indicate an error

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up temporary project files and directories.")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be deleted without actually deleting anything.")
    args = parser.parse_args()

    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for cleanup.py.")

    exit(main(args)) # Run the cleanup and exit with its code
