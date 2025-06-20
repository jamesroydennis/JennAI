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

@pytest.fixture
def result_repo(setup_test_database: Path) -> AIAnalysisResultSQLiteRepository: # Use shared fixture
    # The setup_test_database fixture already creates all necessary tables
    # and dummy session (ID 1) and prompt (ID 1).
    return AIAnalysisResultSQLiteRepository(db_path=str(setup_test_database))

@pytest.fixture
def result_repo_fixture(setup_test_database: Path) -> AIAnalysisResultSQLiteRepository: # Renamed
    return AIAnalysisResultSQLiteRepository(db_path=str(setup_test_database))

def test_create_and_read_ai_analysis_result(result_repo_fixture: AIAnalysisResultSQLiteRepository): # Use renamed fixture
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
    created_result = result_repo_fixture.create(new_result)
    assert created_result.result_id is not None

    retrieved_result = result_repo_fixture.read_by_id(created_result.result_id)
    assert retrieved_result is not None
    assert retrieved_result.ai_response_raw == "Raw AI output here."
    assert retrieved_result.prompt_id == 1
    assert retrieved_result.response_timestamp == timestamp_now
    # Check if JSON strings are stored and retrieved correctly
    assert json.loads(retrieved_result.parsed_system_requirements_json) == sys_reqs_dict
    assert json.loads(retrieved_result.parsed_dependencies_json) == deps_dict

def test_update_ai_analysis_result(result_repo_fixture: AIAnalysisResultSQLiteRepository): # Use renamed fixture
    """Tests updating an existing AI analysis result."""
    # 1. Create initial result
    timestamp_initial = datetime.utcnow().isoformat()
    initial_sys_reqs = {"os": "InitialOS"}
    initial_deps = {"lib": "v1"}
    initial_result = AIAnalysisResultDTO(
        prompt_id=1,
        ai_response_raw="Initial raw response",
        response_timestamp=timestamp_initial,
        parsed_system_requirements_json=json.dumps(initial_sys_reqs),
        parsed_dependencies_json=json.dumps(initial_deps)
    )
    created_result = result_repo_fixture.create(initial_result)
    assert created_result.result_id is not None

    # 2. Modify the DTO
    updated_sys_reqs = {"os": "UpdatedOS", "cpu": "i7"}
    created_result.ai_response_raw = "Updated raw response"
    created_result.parsed_system_requirements_json = json.dumps(updated_sys_reqs)
    # Let's assume parsed_dependencies_json remains unchanged for this test

    # 3. Update in repository
    updated_result_from_repo = result_repo_fixture.update(created_result)
    assert updated_result_from_repo is not None
    assert updated_result_from_repo.result_id == created_result.result_id

    # 4. Read back and verify
    retrieved_after_update = result_repo_fixture.read_by_id(created_result.result_id)
    assert retrieved_after_update is not None
    assert retrieved_after_update.ai_response_raw == "Updated raw response"
    assert json.loads(retrieved_after_update.parsed_system_requirements_json) == updated_sys_reqs
    assert json.loads(retrieved_after_update.parsed_dependencies_json) == initial_deps # Unchanged
    assert retrieved_after_update.prompt_id == 1 # Unchanged

def test_delete_ai_analysis_result(result_repo_fixture: AIAnalysisResultSQLiteRepository): # Use renamed fixture
    """Tests deleting an AI analysis result."""
    # 1. Create a result to delete
    result_to_delete = AIAnalysisResultDTO(
        prompt_id=1,
        ai_response_raw="Response to be deleted",
        response_timestamp=datetime.utcnow().isoformat(),
        parsed_system_requirements_json=json.dumps({"status": "delete_me"}),
        parsed_dependencies_json=json.dumps({"lib": "to_delete"})
    )
    created_result = result_repo_fixture.create(result_to_delete)
    assert created_result.result_id is not None

    # 2. Delete the result
    result_repo_fixture.delete(created_result.result_id)

    # 3. Try to read it back
    retrieved_after_delete = result_repo_fixture.read_by_id(created_result.result_id)
    assert retrieved_after_delete is None, "AI Analysis Result should be None after deletion."