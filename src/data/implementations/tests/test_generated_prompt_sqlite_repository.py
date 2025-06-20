# /home/jdennis/Projects/JennAI/src/data/implementations/tests/test_generated_prompt_sqlite_repository.py

import sys
import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.data.obj.generated_prompt_dto import GeneratedPromptDTO
from src.data.implementations.generated_prompt_sqlite_repository import GeneratedPromptSQLiteRepository

# SQL to create the generated_prompts table (from datadesign.ipynb)
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

# We also need analysis_sessions table for the foreign key constraint
CREATE_ANALYSIS_SESSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS analysis_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_repository_identifier TEXT NOT NULL,
    analysis_timestamp TEXT NOT NULL,
    user_notes TEXT,
    status TEXT
);
"""

@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    db_file = tmp_path / "test_pyrepopal_prompts.db"
    # Create tables
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(CREATE_ANALYSIS_SESSIONS_TABLE_SQL) # Prerequisite for FK
    cursor.execute(CREATE_GENERATED_PROMPTS_TABLE_SQL)
    conn.commit()
    # Create a dummy session for FK integrity
    cursor.execute("INSERT INTO analysis_sessions (target_repository_identifier, analysis_timestamp, status) VALUES (?, ?, ?)",
                   ("test_repo", datetime.utcnow().isoformat(), "created"))
    conn.commit()
    conn.close()
    return db_file

@pytest.fixture
def prompt_repo(temp_db_path: Path) -> GeneratedPromptSQLiteRepository:
    return GeneratedPromptSQLiteRepository(db_path=str(temp_db_path))

def test_create_and_read_generated_prompt(prompt_repo: GeneratedPromptSQLiteRepository):
    timestamp_now = datetime.utcnow().isoformat()
    new_prompt = GeneratedPromptDTO(
        session_id=1, # Assuming a session with ID 1 exists (created in fixture)
        prompt_type="min_sys_reqs",
        template_name_used="generate_min_sys_reqs_from_repo_prompt.md",
        prompt_content="Analyze this repo...",
        creation_timestamp=timestamp_now
    )
    created_prompt = prompt_repo.create(new_prompt)
    assert created_prompt.prompt_id is not None
    retrieved_prompt = prompt_repo.read_by_id(created_prompt.prompt_id)
    assert retrieved_prompt is not None
    assert retrieved_prompt.prompt_content == "Analyze this repo..."
    assert retrieved_prompt.session_id == 1
    assert retrieved_prompt.creation_timestamp == timestamp_now