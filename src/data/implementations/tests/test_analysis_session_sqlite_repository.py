# test_analysis_session_sqlite_repository.py

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

@pytest.fixture
def session_repo(setup_test_database: Path) -> AnalysisSessionSQLiteRepository: # Use shared fixture
    """
    Provides an AnalysisSessionSQLiteRepository instance using a temporary database
    and ensures the necessary table is created.
    """
    # The setup_test_database fixture already creates the table and a dummy session (ID 1)
    return AnalysisSessionSQLiteRepository(db_path=str(setup_test_database))

def test_create_and_read_analysis_session(session_repo: AnalysisSessionSQLiteRepository):
    """
    Tests creating a new analysis session and then reading it back by ID.
    """
    # 1. Create a DTO instance
    timestamp_now = datetime.utcnow().isoformat()
    new_session_dto = AnalysisSessionDTO( # This will create a new session, likely with ID 2
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

def test_update_analysis_session(session_repo: AnalysisSessionSQLiteRepository):
    """
    Tests updating an existing analysis session.
    """
    # 1. Create an initial session
    timestamp_initial = datetime.utcnow().isoformat()
    initial_session_dto = AnalysisSessionDTO(
        target_repository_identifier="https://github.com/test/updatable.git",
        analysis_timestamp=timestamp_initial,
        status="pending_update",
        user_notes="Initial notes for update test"
    )
    created_session = session_repo.create(initial_session_dto)
    assert created_session.session_id is not None

    # 2. Modify the DTO
    created_session.status = "completed_update"
    created_session.user_notes = "Updated notes after test."
    # target_repository_identifier and analysis_timestamp are not typically updated, but PK is.

    # 3. Use the repository to update the session
    updated_session_result = session_repo.update(created_session)
    assert updated_session_result is not None, "Update should return the updated DTO."
    assert updated_session_result.session_id == created_session.session_id

    # 4. Read the session back to verify changes
    retrieved_after_update = session_repo.read_by_id(created_session.session_id)
    assert retrieved_after_update is not None
    assert retrieved_after_update.status == "completed_update"
    assert retrieved_after_update.user_notes == "Updated notes after test."
    assert retrieved_after_update.target_repository_identifier == "https://github.com/test/updatable.git" # Unchanged

def test_delete_analysis_session(session_repo: AnalysisSessionSQLiteRepository):
    """
    Tests deleting an analysis session.
    """
    # 1. Create a session to delete
    session_to_delete_dto = AnalysisSessionDTO(
        target_repository_identifier="https://github.com/test/deletable.git",
        analysis_timestamp=datetime.utcnow().isoformat(),
        status="to_be_deleted"
    )
    created_session = session_repo.create(session_to_delete_dto)
    assert created_session.session_id is not None

    # 2. Delete the session
    session_repo.delete(created_session.session_id)

    # 3. Try to read it back and assert it's None
    retrieved_after_delete = session_repo.read_by_id(created_session.session_id)
    assert retrieved_after_delete is None, "Session should be None after deletion."
