#!/usr/bin/env python
# /home/jdennis/Projects/JennAI/admin/setup_env.py
import sys
from pathlib import Path
import shutil

# --- Root Project Path Setup ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.loguru_setup import setup_logging, logger

def setup_environment_file():
    """
    Checks for .env.example and creates .env from it if it doesn't exist.
    """
    logger.info("Checking for local environment file (.env)...")
    
    env_example_path = project_root / ".env.example"
    env_path = project_root / ".env"

    if not env_example_path.exists():
        logger.error(f"'.env.example' not found at {env_example_path}. Cannot create .env file.")
        return 1 # Indicate failure

    if env_path.exists():
        logger.info(f"'.env' file already exists at {env_path}. No action taken.")
        return 0 # Indicate success, no action needed

    try:
        shutil.copy(env_example_path, env_path)
        logger.success(f"Successfully created '.env' from '.env.example'.")
        logger.warning("Please open the new '.env' file and add your secret API keys.")
        return 0 # Indicate success
    except Exception as e:
        logger.critical(f"Failed to create '.env' file: {e}")
        return 1 # Indicate failure

if __name__ == "__main__":
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for setup_env.py.")
    exit_code = setup_environment_file()
    sys.exit(exit_code)