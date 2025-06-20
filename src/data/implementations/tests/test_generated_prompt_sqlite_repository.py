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

@pytest.fixture
def prompt_repo(setup_test_database: Path) -> GeneratedPromptSQLiteRepository: # Use shared fixture
    # The setup_test_database fixture already creates analysis_sessions and generated_prompts tables
    # and a dummy session with ID 1.
    return GeneratedPromptSQLiteRepository(db_path=str(setup_test_database))

@pytest.fixture
def prompt_repo_fixture(setup_test_database: Path) -> GeneratedPromptSQLiteRepository: # Renamed
    return GeneratedPromptSQLiteRepository(db_path=str(setup_test_database))

def test_create_and_read_generated_prompt(prompt_repo_fixture: GeneratedPromptSQLiteRepository): # Use renamed fixture
    timestamp_now = datetime.utcnow().isoformat()
    new_prompt = GeneratedPromptDTO(
        session_id=1, # Assuming a session with ID 1 exists (created in fixture)
        prompt_type="min_sys_reqs",
        template_name_used="generate_min_sys_reqs_from_repo_prompt.md",
        prompt_content="Analyze this repo...",
        creation_timestamp=timestamp_now
    )
    created_prompt = prompt_repo_fixture.create(new_prompt)
    assert created_prompt.prompt_id is not None
    retrieved_prompt = prompt_repo_fixture.read_by_id(created_prompt.prompt_id)
    assert retrieved_prompt is not None
    assert retrieved_prompt.prompt_content == "Analyze this repo..."
    assert retrieved_prompt.session_id == 1
    assert retrieved_prompt.creation_timestamp == timestamp_now

def test_update_generated_prompt(prompt_repo_fixture: GeneratedPromptSQLiteRepository): # Use renamed fixture
    """Tests updating an existing generated prompt."""
    # 1. Create initial prompt
    timestamp_initial = datetime.utcnow().isoformat()
    initial_prompt = GeneratedPromptDTO(
        session_id=1,
        prompt_type="initial_analysis",
        template_name_used="template_v1.md",
        prompt_content="Original prompt content.",
        creation_timestamp=timestamp_initial
    )
    created_prompt = prompt_repo_fixture.create(initial_prompt)
    assert created_prompt.prompt_id is not None

    # 2. Modify the DTO
    created_prompt.prompt_content = "Updated prompt content for testing."
    created_prompt.prompt_type = "follow_up_analysis"

    # 3. Update in repository
    updated_prompt_result = prompt_repo_fixture.update(created_prompt)
    assert updated_prompt_result is not None
    assert updated_prompt_result.prompt_id == created_prompt.prompt_id

    # 4. Read back and verify
    retrieved_after_update = prompt_repo_fixture.read_by_id(created_prompt.prompt_id)
    assert retrieved_after_update is not None
    assert retrieved_after_update.prompt_content == "Updated prompt content for testing."
    assert retrieved_after_update.prompt_type == "follow_up_analysis"
    assert retrieved_after_update.session_id == 1 # Unchanged

def test_delete_generated_prompt(prompt_repo_fixture: GeneratedPromptSQLiteRepository): # Use renamed fixture
    """Tests deleting a generated prompt."""
    # 1. Create a prompt to delete
    prompt_to_delete = GeneratedPromptDTO(
        session_id=1,
        prompt_type="test_delete_type", # Added missing required argument
        prompt_content="This prompt will be deleted.",
        creation_timestamp=datetime.utcnow().isoformat()
    )
    created_prompt = prompt_repo_fixture.create(prompt_to_delete)
    assert created_prompt.prompt_id is not None

    # 2. Delete the prompt
    prompt_repo_fixture.delete(created_prompt.prompt_id)

    # 3. Try to read it back
    retrieved_after_delete = prompt_repo_fixture.read_by_id(created_prompt.prompt_id)
    assert retrieved_after_delete is None, "Prompt should be None after deletion."