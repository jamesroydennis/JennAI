# /home/jdennis/Projects/JennAI/src/data/implementations/tests/conftest.py

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

# --- SQL Table Creation Statements ---
# Centralized here to be used by the shared database fixture.

CREATE_ANALYSIS_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS analysis_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_repository_identifier TEXT NOT NULL,
    analysis_timestamp TEXT NOT NULL,
    user_notes TEXT,
    status TEXT
);
"""

CREATE_SYSTEM_PROFILES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS system_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    profile_timestamp TEXT NOT NULL,
    os_info TEXT,
    cpu_info TEXT,
    ram_info TEXT,
    gpu_info TEXT,
    disk_info TEXT,
    python_info TEXT,
    FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
);
"""

CREATE_REPOSITORY_SNAPSHOTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS repository_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    readme_content TEXT,
    requirements_txt_content TEXT,
    environment_yaml_content TEXT,
    existing_min_sys_reqs_content TEXT,
    FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
);
"""

CREATE_GENERATED_PROMPTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS generated_prompts (
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    prompt_type TEXT,
    template_name_used TEXT,
    prompt_content TEXT NOT NULL,
    creation_timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
);
"""

CREATE_AI_ANALYSIS_RESULTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ai_analysis_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    ai_response_raw TEXT NOT NULL,
    response_timestamp TEXT NOT NULL,
    parsed_system_requirements_json TEXT,
    parsed_dependencies_json TEXT,
    FOREIGN KEY (prompt_id) REFERENCES generated_prompts (prompt_id)
);
"""

@pytest.fixture(scope="function") # "function" scope ensures a fresh DB for each test
def setup_test_database(tmp_path: Path) -> Path:
    """
    Sets up a temporary SQLite database with the full schema for testing repositories.
    Also creates a common dummy session (ID 1) and prompt (ID 1) for FK constraints.
    """
    db_file = tmp_path / "test_pyrepopal_shared.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create tables in order of dependencies
    cursor.execute(CREATE_ANALYSIS_SESSIONS_TABLE_SQL)
    cursor.execute(CREATE_SYSTEM_PROFILES_TABLE_SQL) # Depends on analysis_sessions
    cursor.execute(CREATE_REPOSITORY_SNAPSHOTS_TABLE_SQL) # Depends on analysis_sessions
    cursor.execute(CREATE_GENERATED_PROMPTS_TABLE_SQL) # Depends on analysis_sessions
    cursor.execute(CREATE_AI_ANALYSIS_RESULTS_TABLE_SQL) # Depends on generated_prompts
    conn.commit()

    # Create a common dummy session (ID will be 1)
    cursor.execute("INSERT INTO analysis_sessions (target_repository_identifier, analysis_timestamp, status) VALUES (?, ?, ?)",
                   ("shared_test_repo", datetime.utcnow().isoformat(), "created_for_fk"))
    # Create a common dummy prompt (ID will be 1, linked to session_id 1)
    cursor.execute("INSERT INTO generated_prompts (session_id, prompt_type, prompt_content, creation_timestamp) VALUES (?, ?, ?, ?)",
                   (1, "shared_test_prompt_type", "dummy shared prompt", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return db_file