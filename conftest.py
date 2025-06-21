# /home/jdennis/Projects/JennAI/conftest.py

import sys
from pathlib import Path
import pytest

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This ensures that conftest.py can import from your project's modules (config, core, etc.)
jennai_root_for_path = Path(__file__).resolve().parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import setup_logging, logger # Import setup and logger from config
from config.config import DEBUG_MODE # Use the global DEBUG_MODE

def pytest_configure(config):
    """
    Hook called by pytest after command line options have been parsed
    and before the test collection process starts.
    We use this to set up our custom Loguru logging for the test session.
    """
    # Setup logging for the test session, directing to a separate file
    # The log level (DEBUG/INFO) will be determined by DEBUG_MODE from config.py
    # Console logging will also respect DEBUG_MODE as per loguru_setup.py logic
    setup_logging(log_file_name="pytest_session.log", debug_mode=DEBUG_MODE)
    logger.info(f"Pytest session logging initialized. Log file: logs/pytest_session.log, DEBUG_MODE: {DEBUG_MODE}")