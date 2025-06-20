# C:\Users\jarde\Projects\JennAI\config\config.py

from pathlib import Path

# Global configuration settings for the JennAI project.

# Set to True for development mode (more verbose logging, dev-specific behaviors)
# Set to False for production mode.
DEBUG_MODE = True # Default for development

# --- Database Configuration ---
# Define the database path (relative to the project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent # JennAI/
DB_DIR = PROJECT_ROOT / "src" / "data" / "database"
DATABASE_FILE_PATH = DB_DIR / "pyrepopal.db"
