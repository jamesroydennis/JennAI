import sqlite3
import sys
from pathlib import Path
import os

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows centralized modules (config, core) to be imported.
# From src/data/scripts/sql/, the root is four levels up.
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path)) # Insert at the beginning for higher priority

from config.loguru_setup import setup_logging # Import the setup function
from config.config import DATABASE_FILE_PATH # Import the database path from config
from loguru import logger # Import the configured logger instance

def setup_database(db_path: Path, destroy_first: bool = False):
    """
    Sets up the SQLite database by creating tables if they don't exist.
    """
    # Ensure the directory for the database file exists
    db_dir = db_path.parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created database directory: {db_dir}")

    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if destroy_first:
            logger.warning("Dropping all existing tables before creation...")
            drop_tables_sql = """
            DROP TABLE IF EXISTS ai_analysis_results;
            DROP TABLE IF EXISTS generated_prompts;
            DROP TABLE IF EXISTS repository_snapshots;
            DROP TABLE IF EXISTS system_profiles;
            DROP TABLE IF EXISTS analysis_sessions;
            """
            cursor.executescript(drop_tables_sql)
            logger.info("All tables dropped.")

        # Use CREATE TABLE IF NOT EXISTS to be non-destructive by default
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS analysis_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_repository_identifier TEXT NOT NULL, -- Path or identifier of the repo analyzed
            analysis_timestamp TEXT NOT NULL,          -- ISO 8601 timestamp of session creation
            user_notes TEXT,                           -- Optional notes provided by the user
            status TEXT                                -- Current status (e.g., 'created', 'failed_data_collection', 'completed_successfully')
        );

        CREATE TABLE IF NOT EXISTS system_profiles (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,               -- Foreign key to analysis_sessions
            profile_timestamp TEXT NOT NULL,           -- ISO 8601 timestamp of profile collection
            profile_data TEXT NOT NULL,                -- A single JSON blob of the entire system profile
            FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
        );

        CREATE TABLE IF NOT EXISTS repository_snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,               -- Foreign key to analysis_sessions
            snapshot_data TEXT NOT NULL,               -- A single JSON blob of all captured file contents
            creation_timestamp TEXT NOT NULL,          -- ISO 8601 timestamp of snapshot creation
            FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
        );

        CREATE TABLE IF NOT EXISTS generated_prompts (
            prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,               -- Foreign key to analysis_sessions
            prompt_type TEXT,                          -- Type of prompt (e.g., 'initial_analysis', 'follow_up')
            template_name_used TEXT,                   -- Filename of the template used
            prompt_content TEXT NOT NULL,              -- The full text of the prompt
            creation_timestamp TEXT NOT NULL,          -- ISO 8601 timestamp of prompt generation
            FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
        );

        CREATE TABLE IF NOT EXISTS ai_analysis_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER NOT NULL,                -- Foreign key to generated_prompts
            ai_response_raw TEXT NOT NULL,             -- The raw text response received from the AI
            response_timestamp TEXT NOT NULL,          -- ISO 8601 timestamp of response reception
            parsed_system_requirements_json TEXT,      -- JSON string of parsed system requirements
            parsed_dependencies_json TEXT,             -- JSON string of parsed dependencies (if AI provides this)
            FOREIGN KEY (prompt_id) REFERENCES generated_prompts (prompt_id)
        );
        """

        # Execute all create table statements
        cursor.executescript(create_tables_sql)
        conn.commit()
        if destroy_first:
            logger.success(f"Database schema reset and created for: {db_path}")
        else:
            logger.success(f"Database schema verified/created for: {db_path}")
        return 0 # Indicate success

    except sqlite3.Error as e:
        logger.critical(f"Database setup failed: {e}")
        return 1 # Indicate error
    except Exception as e:
        logger.critical(f"An unexpected error occurred during database setup: {e}")
        return 1 # Indicate error
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Setup logging for the script
    setup_logging(debug_mode=True) # Use DEBUG mode for setup script verbosity
    logger.info("Loguru setup complete for setup_database.py.")

    # Get the database path from config
    db_file_path = DATABASE_FILE_PATH
    logger.info(f"Using database path from config: {db_file_path}")

    # Run the database setup
    exit_code = setup_database(db_file_path, destroy_first=True) # Standalone run should be destructive
    sys.exit(exit_code)