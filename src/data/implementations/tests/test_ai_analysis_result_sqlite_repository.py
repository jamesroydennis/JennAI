# /home/jdennis/Projects/JennAI/src/data/implementations/tests/test_ai_analysis_result_sqlite_repository.py

import sys
import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.data.obj.ai_analysis_result_dto import AIAnalysisResultDTO
from src.data.implementations.ai_analysis_result_sqlite_repository import AIAnalysisResultSQLiteRepository

# SQL to create tables (from datadesign.ipynb)
CREATE_ANALYSIS_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS analysis_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_repository_identifier TEXT NOT NULL,
    analysis_timestamp TEXT NOT NULL,
    user_notes TEXT,
    status TEXT
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
    parsed_system_requirements_json TEXT,
    parsed_dependencies_json TEXT,
    response_timestamp TEXT NOT NULL,
    FOREIGN KEY (prompt_id) REFERENCES generated_prompts (prompt_id)
);
"""

@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    db_file = tmp_path / "test_pyrepopal_results.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(CREATE_ANALYSIS_SESSIONS_TABLE_SQL)
    cursor.execute(CREATE_GENERATED_PROMPTS_TABLE_SQL)
    cursor.execute(CREATE_AI_ANALYSIS_RESULTS_TABLE_SQL)
    conn.commit()
    # Create dummy session and prompt for FK integrity
    cursor.execute("INSERT INTO analysis_sessions (target_repository_identifier, analysis_timestamp, status) VALUES (?, ?, ?)",
                   ("test_repo", datetime.utcnow().isoformat(), "created"))
    session_id = cursor.lastrowid
    cursor.execute("INSERT INTO generated_prompts (session_id, prompt_content, creation_timestamp) VALUES (?, ?, ?)",
                   (session_id, "dummy prompt", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return db_file

@pytest.fixture
def result_repo(temp_db_path: Path) -> AIAnalysisResultSQLiteRepository:
    return AIAnalysisResultSQLiteRepository(db_path=str(temp_db_path))

def test_create_and_read_ai_analysis_result(result_repo: AIAnalysisResultSQLiteRepository):
    timestamp_now = datetime.utcnow().isoformat()
    sys_reqs_dict = {"os": "Linux", "ram_gb": 16}
    deps_dict = {"python": "3.9", "pytorch": "2.0"}

    new_result = AIAnalysisResultDTO(
        prompt_id=1, # Assuming a prompt with ID 1 exists
        ai_response_raw="Raw AI output here.",
        response_timestamp=timestamp_now,
        # Pass dictionaries, repository should handle JSON string conversion
        parsed_system_requirements_json=json.dumps(sys_reqs_dict), # DTO expects string
        parsed_dependencies_json=json.dumps(deps_dict) # DTO expects string
    )
    created_result = result_repo.create(new_result)
    assert created_result.result_id is not None

    retrieved_result = result_repo.read_by_id(created_result.result_id)
    assert retrieved_result is not None
    assert retrieved_result.ai_response_raw == "Raw AI output here."
    assert retrieved_result.prompt_id == 1
    assert retrieved_result.response_timestamp == timestamp_now
    # Check if JSON strings are stored and retrieved correctly
    assert json.loads(retrieved_result.parsed_system_requirements_json) == sys_reqs_dict
    assert json.loads(retrieved_result.parsed_dependencies_json) == deps_dict