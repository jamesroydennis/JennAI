import os
import sys
from pathlib import Path
from dotenv import load_dotenv  # Import load_dotenv
import pytest
# --- Root Project Path Setup (CRITICAL for Imports) ---
# This ensures that conftest.py can import from your project's modules (config, core, etc.)
ROOT = Path(__file__).resolve().parent # conftest.py is in the project root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env file BEFORE importing config
# This ensures DEBUG_MODE and other settings are correctly read.
load_dotenv(dotenv_path=ROOT / ".env")

from config import config # Import the entire config module
from config.loguru_setup import setup_logging, logger
from config.config import DEBUG_MODE

def pytest_configure(config):
    """
    Hook called by pytest after command line options have been parsed
    and before the test collection process starts.
    We use this to set up our custom Loguru logging for the test session.
    """
    # The `config` parameter is a pytest object provided by the hook.
    # Setup logging for the test session, directing to a separate file
    # The log level (DEBUG/INFO) will be determined by DEBUG_MODE from config.py
    # Console logging will also respect DEBUG_MODE as per loguru_setup.py logic
    setup_logging(log_file_name="pytest_session.log", debug_mode=DEBUG_MODE)
    logger.info(f"Pytest session logging initialized. Log file: logs/pytest_session.log, DEBUG_MODE: {DEBUG_MODE}")

@pytest.fixture(scope="session")
def app_config():
    """
    Pytest fixture to provide access to the application's configuration module.
    The scope is "session" because the configuration is static and doesn't change
    during a test session, making it efficient to load once.
    """
    return config