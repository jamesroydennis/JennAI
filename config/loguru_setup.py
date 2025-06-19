# /home/jdennis/Projects/JennAI/config/loguru_setup.py

import os
import sys
from pathlib import Path # Import Path for clean path manipulation
from loguru import logger # Loguru must be installed in the environment

def setup_logging(log_file_name: str = "jennai.log", debug_mode: bool = True):
    """
    Sets up the global Loguru logger configuration.
    Removes default handlers and adds a file handler and a console handler.

    Args:
        log_file_name (str): The name of the log file (e.g., "jennai.log").
        debug_mode (bool): If True, sets level to DEBUG; otherwise, INFO.
    """
    # Remove default handler to prevent duplicate logs if setup is called multiple times
    logger.remove()

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
