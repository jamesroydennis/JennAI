# config.py

import os # Import os to read environment variables

from pathlib import Path

from pathlib import Path

# Global configuration settings for the JennAI project.

# Set to True for development mode (more verbose logging, dev-specific behaviors)
# Set to False for production mode.
DEBUG_MODE = True # Default for development

# --- Environment Configuration ---
# Defines the current operational environment of the application.
# Possible values: "DEV", "TEST", "PROD"
# This can be overridden by an environment variable (e.g., JENNAI_ENVIRONMENT)
# for deployment flexibility. Defaults to "DEV" if not set.
ENVIRONMENT = os.getenv("JENNAI_ENVIRONMENT", "DEV").upper()
# --- Database Configuration ---
# Define the database path (relative to the project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent # JennAI/
DB_DIR = PROJECT_ROOT / "src" / "data" / "database"
DATABASE_FILE_PATH = DB_DIR / "prp.db"
