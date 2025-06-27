# loguru_setup.py
import os # No longer needed for file paths
import sys
from pathlib import Path # Import Path for clean path manipulation
from loguru import logger # Loguru must be installed in the environment
from typing import Optional # To type hint the optional debug_mode

from config.config import DEBUG_MODE as GLOBAL_DEBUG_MODE # Import global default

# Global variable to hold the ID of the file handler so it can be removed later
_file_handler_id: Optional[int] = None

def setup_logging(log_file_name: str = "jennai.log", debug_mode: Optional[bool] = None):
    """
    Sets up the global Loguru logger configuration.
    Logs to console and to 'logs/jennai.log'.

    Args:
        log_file_name (str): The name of the log file (e.g., "jennai.log", "pytest_session.log"). This function
                             will attempt to add a file handler for this name if one doesn't exist.
        debug_mode (Optional[bool]): If True, sets level to DEBUG; otherwise, INFO.
                                     If None, reads from config.config.DEBUG_MODE.
    """
    global _file_handler_id
    # Determine debug mode
    current_debug_mode = GLOBAL_DEBUG_MODE if debug_mode is None else debug_mode
    log_level = "DEBUG" if current_debug_mode else "INFO"

    # Always remove previous handlers to ensure a clean setup for the current context
    logger.remove()

    # Add console handler
    # Add color tags for different levels
    # <level> will automatically color based on default, but we can be explicit
    # <yellow> for WARNING, <red> for ERROR, <bold><red> for CRITICAL, <green> for SUCCESS
    # Default for INFO is usually plain, DEBUG might be dim or plain.
    log_format_console = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.add(sys.stderr, level=log_level, format=log_format_console, colorize=True)

    # Add file handler
    current_script_dir = Path(__file__).resolve().parent
    jennai_root_path = current_script_dir.parent
    log_dir = jennai_root_path / 'logs' # Using Path object for clean joining
    os.makedirs(log_dir, exist_ok=True) # Ensure logs directory exists
    actual_log_file_path = log_dir / log_file_name
    # Store the handler ID so we can remove it later to release file locks
    _file_handler_id = logger.add(str(actual_log_file_path), rotation="10 MB", level=log_level, compression="zip", retention="10 days", enqueue=True)
    logger.info(f"Loguru setup complete. Console logging active. File logging to: {actual_log_file_path}. Level: {log_level}.")

def stop_file_logging():
    """Removes the file handler from the logger to release the file lock."""
    global _file_handler_id
    if _file_handler_id is not None:
        try:
            logger.remove(_file_handler_id)
            _file_handler_id = None # Clear the ID
            logger.info("File logging handler removed.")
        except ValueError:
            # This can happen if the handler was already removed. It's safe to ignore.
            logger.debug("File handler already removed, nothing to do.")
            pass

def start_file_logging(debug_mode: Optional[bool] = None):
    """A convenience function to re-initialize logging, including the file handler."""
    logger.info("Re-initializing logging...")
    setup_logging(debug_mode=debug_mode)
