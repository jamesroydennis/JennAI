# /home/jdennis/Projects/JennAI/config/loguru_setup.py

import os
import sys
from pathlib import Path # Import Path for clean path manipulation
from loguru import logger # Loguru must be installed in the environment

_logging_configured_for_process = False

def setup_logging(log_file_name: str = "jennai.log", debug_mode: bool = True):
    """
    Sets up the global Loguru logger configuration.
    If called during a pytest run (after conftest.py has configured logging for "pytest.log"),
    this function will avoid reconfiguring the file sink to preserve test logs.

    Args:
        log_file_name (str): The name of the log file (e.g., "jennai.log").
        debug_mode (bool): If True, sets level to DEBUG; otherwise, INFO.
    """
    global _logging_configured_for_process

    is_pytest_running = "PYTEST_CURRENT_TEST" in os.environ

    if _logging_configured_for_process and is_pytest_running:
        # Logging was already configured by conftest.py for the test session.
        # Avoid removing the "pytest.log" handler.
        # We can still ensure the console handler reflects the current debug_mode if needed,
        # but typically the initial setup by conftest should suffice for console too.
        logger.debug(f"Test logging already configured. Call for '{log_file_name}' will not alter file sink.")
        return

    # If it's the first call in the process, or if it's not a pytest run,
    # then proceed with a full logger removal and setup.
    logger.remove() # Remove all existing handlers to start fresh.
    _logging_configured_for_process = True

    log_level = "DEBUG" if debug_mode else "INFO"

    if debug_mode:
        # Console handler for debug mode, without the "jennai" specific filter
        # to allow admin scripts and other utilities to also log to console.
        logger.add(sys.stderr, level=log_level, format="{time} {level} {message}")

    # --- CORRECTED LOG FILE PATH DETERMINATION ---
    # Determine the actual JennAI project root
    # Current file is in 'JennAI/config/loguru_setup.py'
    # Step 1: Get the directory of the current file (e.g., .../JennAI/config)
    current_script_dir = Path(__file__).resolve().parent

    # Step 2: Go up one level from 'config' to get to the JennAI root (e.g., .../JennAI)
    jennai_root_path = current_script_dir.parent

    # Define the logs directory at the JennAI root
    log_dir = jennai_root_path / 'logs' # Using Path object for clean joining
    os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists

    # Define the full path to the log file
    log_file_path = log_dir / log_file_name # Using Path object for the log file

    # Add a file handler for persistent logs
    logger.add(str(log_file_path), rotation="10 MB", level=log_level, compression="zip", retention="10 days") # Convert Path to string for logger.add

    logger.info(f"Loguru setup complete. Logging to file: {log_file_path}. Running in {log_level} mode.")
