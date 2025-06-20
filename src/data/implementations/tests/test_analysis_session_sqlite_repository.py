# /home/jdennis/Projects/JennAI/src/data/implementations/tests/test_analysis_session_sqlite_repository.py

import sys
import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.data.obj.analysis_session_dto import AnalysisSessionDTO
from src.data.implementations.analysis_session_sqlite_repository import AnalysisSessionSQLiteRepository

# SQL to create the analysis_sessions table (copied from datadesign.ipynb for test setup)
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
    """Creates a temporary database file path for testing."""
    db_file = tmp_path / "test_pyrepopal.db"
    return db_file

@pytest.fixture
def session_repo(temp_db_path: Path) -> AnalysisSessionSQLiteRepository:
    """
    Provides an AnalysisSessionSQLiteRepository instance using a temporary database
    and ensures the necessary table is created.
    """
    # Ensure the table exists in the temporary database
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute(CREATE_ANALYSIS_SESSIONS_TABLE_SQL)
    conn.commit()
    conn.close()
    
    return AnalysisSessionSQLiteRepository(db_path=str(temp_db_path))

def test_create_and_read_analysis_session(session_repo: AnalysisSessionSQLiteRepository):
    """
    Tests creating a new analysis session and then reading it back by ID.
    """
    # 1. Create a DTO instance
    timestamp_now = datetime.utcnow().isoformat()
    new_session_dto = AnalysisSessionDTO(
        target_repository_identifier="https://github.com/test/repo.git",
        analysis_timestamp=timestamp_now,
        status="started",
        user_notes="Test session for create and read"
    )

    # 2. Use the repository to create the session in the database
    created_session = session_repo.create(new_session_dto)

    # 3. Assertions for creation
    assert created_session.session_id is not None, "Session ID should be populated after creation."
    assert created_session.target_repository_identifier == new_session_dto.target_repository_identifier
    assert created_session.status == "started"

    # 4. Read the session back using the populated ID
    retrieved_session = session_repo.read_by_id(created_session.session_id)

    # 5. Assertions for reading
    assert retrieved_session is not None, "Session should be retrievable by ID."
    assert retrieved_session.session_id == created_session.session_id
    assert retrieved_session.target_repository_identifier == "https://github.com/test/repo.git"
    assert retrieved_session.analysis_timestamp == timestamp_now
    assert retrieved_session.user_notes == "Test session for create and read"
    assert retrieved_session.status == "started"