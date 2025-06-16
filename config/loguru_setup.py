# C:\Users\jarde\Projects\JennAI\config\loguru_setup.py

import os
import sys
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

    # Add a console handler for development visibility
    logger.add(sys.stderr, level=log_level, format="{time} {level} {message}", filter="jennai")

    # Define the log file path relative to the JennAI root
    # This assumes loguru_setup.py is in JennAI/config/
    # So, to get to JennAI root: up 1 from config/
    jennai_root = os.path.dirname(os.path.abspath(__file__)) 
    log_dir = os.path.join(jennai_root, 'logs') # Logs folder at JennAI root
    os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists
    log_file_path = os.path.join(log_dir, log_file_name)

    # Add a file handler for persistent logs
    logger.add(log_file_path, rotation="10 MB", level=log_level, compression="zip", retention="10 days")

    logger.info(f"INFO - Loguru setup complete. Logging to file: {log_file_path}. Running in {log_level} mode.")