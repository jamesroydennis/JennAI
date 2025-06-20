# /home/jdennis/Projects/JennAI/src/data/implementations/tests/test_repository_snapshot_sqlite_repository.py

import sys
import pytest
import sqlite3
from pathlib import Path
from datetime import datetime # Though not directly used by snapshot, good for consistency

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.data.obj.repository_snapshot_dto import RepositorySnapshotDTO
from src.data.implementations.repository_snapshot_sqlite_repository import RepositorySnapshotSQLiteRepository

@pytest.fixture
def snapshot_repo(setup_test_database: Path) -> RepositorySnapshotSQLiteRepository: # Use shared fixture
    # The setup_test_database fixture already creates analysis_sessions and repository_snapshots tables
    # and a dummy session with ID 1.
    return RepositorySnapshotSQLiteRepository(db_path=str(setup_test_database))

@pytest.fixture
def snapshot_repo_fixture(setup_test_database: Path) -> RepositorySnapshotSQLiteRepository: # Renamed to avoid conflict if needed, or keep as snapshot_repo
    return RepositorySnapshotSQLiteRepository(db_path=str(setup_test_database))

def test_create_and_read_repository_snapshot(snapshot_repo_fixture: RepositorySnapshotSQLiteRepository): # Use the renamed fixture
    new_snapshot = RepositorySnapshotDTO(
        session_id=1, # Assumes session_id 1 exists from setup_test_database
        readme_content="This is a test README.",
        requirements_txt_content="pytest==8.0.0\nloguru==0.7.0",
        environment_yaml_content=None,
        existing_min_sys_reqs_content="Python 3.9+"
    )
    created_snapshot = snapshot_repo_fixture.create(new_snapshot)
    assert created_snapshot.snapshot_id is not None, "Snapshot ID should be populated after creation."

    retrieved_snapshot = snapshot_repo_fixture.read_by_id(created_snapshot.snapshot_id)
    assert retrieved_snapshot is not None, "Snapshot should be retrievable by ID."
    assert retrieved_snapshot.readme_content == "This is a test README."
    assert retrieved_snapshot.requirements_txt_content == "pytest==8.0.0\nloguru==0.7.0"
    assert retrieved_snapshot.environment_yaml_content is None
    assert retrieved_snapshot.existing_min_sys_reqs_content == "Python 3.9+"
    assert retrieved_snapshot.session_id == 1

def test_update_repository_snapshot(snapshot_repo_fixture: RepositorySnapshotSQLiteRepository): # Use the renamed fixture
    """Tests updating an existing repository snapshot."""
    # 1. Create initial snapshot
    initial_snapshot = RepositorySnapshotDTO(
        session_id=1,
        readme_content="Original README",
        requirements_txt_content="Original requirements",
        environment_yaml_content=None,
        existing_min_sys_reqs_content="Original sys reqs"
    )
    created_snapshot = snapshot_repo_fixture.create(initial_snapshot)
    assert created_snapshot.snapshot_id is not None

    # 2. Modify the DTO
    created_snapshot.readme_content = "Updated README"
    created_snapshot.requirements_txt_content = "Updated requirements"

    # 3. Update in repository
    updated_snapshot_result = snapshot_repo_fixture.update(created_snapshot)
    assert updated_snapshot_result is not None
    assert updated_snapshot_result.snapshot_id == created_snapshot.snapshot_id

    # 4. Read back and verify
    retrieved_after_update = snapshot_repo_fixture.read_by_id(created_snapshot.snapshot_id)
    assert retrieved_after_update is not None
    assert retrieved_after_update.readme_content == "Updated README"
    assert retrieved_after_update.requirements_txt_content == "Updated requirements"
    assert retrieved_after_update.session_id == 1 # Unchanged

def test_delete_repository_snapshot(snapshot_repo_fixture: RepositorySnapshotSQLiteRepository): # Use the renamed fixture
    """Tests deleting a repository snapshot."""
    # 1. Create a snapshot to delete
    snapshot_to_delete = RepositorySnapshotDTO(
        session_id=1,
        readme_content="To be deleted README",
        requirements_txt_content="To be deleted requirements"
    )
    created_snapshot = snapshot_repo_fixture.create(snapshot_to_delete)
    assert created_snapshot.snapshot_id is not None

    # 2. Delete the snapshot
    snapshot_repo_fixture.delete(created_snapshot.snapshot_id)

    # 3. Try to read it back
    retrieved_after_delete = snapshot_repo_fixture.read_by_id(created_snapshot.snapshot_id)
    assert retrieved_after_delete is None, "Snapshot should be None after deletion."