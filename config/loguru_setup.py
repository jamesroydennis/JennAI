import sys
from pathlib import Path
from loguru import logger
from typing import Optional

# --- Project Path Configuration ---
# Ensure the config module can be found by other scripts.
try:
    from . import config
except ImportError:
    # This allows the script to be run directly for testing,
    # though its primary use is as a module.
    import config

# --- Global State for Handlers ---
# Use a dictionary to keep track of handler IDs to prevent duplicates
# and allow for easy removal and re-adding of handlers.
_handler_ids = {
    "file": None,
    "console": None
}

def setup_logging(debug_mode: bool = False, log_file_name: Optional[str] = None):
    """
    Configures Loguru logging for the entire application.

    This setup includes a console logger and a file logger with automatic
    rotation, retention, and compression to manage disk space.

    Args:
        debug_mode (bool): If True, sets the console log level to DEBUG.
                           Otherwise, it's set to INFO. The file logger
                           always logs at the DEBUG level.
        log_file_name (Optional[str]): If provided, this filename will be used
                                       for the log file inside the LOGS_DIR.
                                       Defaults to 'jennai.log'.
    """
    # Stop any existing loggers to ensure a clean setup
    logger.remove()

    console_level = "DEBUG" if debug_mode else "INFO"
    if log_file_name:
        log_file_path = config.LOGS_DIR / log_file_name
    else:
        log_file_path = config.LOGS_DIR / "jennai.log"

    # --- Console Logger ---
    # This handler prints messages to your terminal.
    _handler_ids["console"] = logger.add(
        sys.stderr,
        level=console_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # --- File Logger (with Rotation and Retention) ---
    # This handler writes messages to a file and manages old logs automatically.
    _handler_ids["file"] = logger.add(
        log_file_path,
        level="DEBUG",  # Always log debug messages to the file
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        rotation="10 MB",      # Create a new file when the current one reaches 10 MB.
        retention="14 days",   # Keep log files for a maximum of 14 days.
        compression="zip",     # Compress old log files to save space.
        backtrace=True,        # Show full stack traces for exceptions.
        diagnose=True,         # Add exception variable values for easier debugging.
        enqueue=True,          # Make logging non-blocking (good for performance).
        catch=True             # Automatically catch uncaught exceptions.
    )

def stop_file_logging():
    """Stops logging to the file, typically before a cleanup operation."""
    if _handler_ids["file"] is not None:
        logger.remove(_handler_ids["file"])
        _handler_ids["file"] = None

def start_file_logging(debug_mode: bool):
    """Re-initializes all logging handlers."""
    setup_logging(debug_mode)