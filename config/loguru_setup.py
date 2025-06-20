# loguru_setup.py
import os # No longer needed for file paths
import sys
from pathlib import Path # Import Path for clean path manipulation
from loguru import logger # Loguru must be installed in the environment
from typing import Optional # To type hint the optional debug_mode

# Flag to indicate if pytest-specific logging has been initialized
# _pytest_logging_initialized = False # No longer needed with single log file strategy
from config.config import DEBUG_MODE as GLOBAL_DEBUG_MODE # Import global default

def setup_logging(log_file_name: str = "jennai.log", debug_mode: Optional[bool] = None):
    """
    Sets up the global Loguru logger configuration.
    Logs to console and to 'logs/jennai.log'.

    Args:
        log_file_name (str): The name of the log file. This will be effectively ignored
                             as we are standardizing to 'jennai.log'.
        debug_mode (Optional[bool]): If True, sets level to DEBUG; otherwise, INFO.
                                     If None, reads from config.config.DEBUG_MODE.
    """
    # Determine debug mode
    current_debug_mode = GLOBAL_DEBUG_MODE if debug_mode is None else debug_mode
    log_level = "DEBUG" if current_debug_mode else "INFO"

    # Always remove previous handlers to ensure a clean setup
    logger.remove()

    # Add console handler
    logger.add(sys.stderr, level=log_level, format="{time} {level} {message}")

    # Add file handler for jennai.log
    current_script_dir = Path(__file__).resolve().parent
    jennai_root_path = current_script_dir.parent
    log_dir = jennai_root_path / 'logs' # Using Path object for clean joining
    os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists
    jennai_log_path = log_dir / "jennai.log" # Standardized log file name
    logger.add(str(jennai_log_path), rotation="10 MB", level=log_level, compression="zip", retention="10 days")
    logger.info(f"Loguru setup complete. Logging to console and to file: {jennai_log_path}. Level: {log_level}.")
