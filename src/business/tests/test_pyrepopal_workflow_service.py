# /home/jdennis/Projects/JennAI/src/business/tests/test_pyrepopal_workflow_service.py

import sys
import pytest # type: ignore
from pathlib import Path
from unittest.mock import MagicMock

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.business.pyrepopal_workflow_service import PyRepoPalWorkflowService
from src.business.ai.data_collect_service import DataCollectService
from src.business.interfaces.IAIService import IAIService
from src.data.interfaces.ICrudRepository import ICrudRepository
from src.data.obj.analysis_session_dto import AnalysisSessionDTO
from src.data.obj.system_profile_dto import SystemProfileDTO
from src.data.obj.repository_snapshot_dto import RepositorySnapshotDTO
from src.data.obj.generated_prompt_dto import GeneratedPromptDTO
from src.data.obj.ai_analysis_result_dto import AIAnalysisResultDTO

@pytest.fixture
def mock_data_collect_service():
    return MagicMock(spec=DataCollectService)

@pytest.fixture
def mock_ai_service():
    return MagicMock(spec=IAIService)

@pytest.fixture
def mock_analysis_session_repo():
    return MagicMock(spec=ICrudRepository)

@pytest.fixture
def mock_system_profile_repo():
    return MagicMock(spec=ICrudRepository)

@pytest.fixture
def mock_repository_snapshot_repo():
    return MagicMock(spec=ICrudRepository)

@pytest.fixture
def mock_generated_prompt_repo():
    return MagicMock(spec=ICrudRepository)

@pytest.fixture
def mock_ai_analysis_result_repo():
    return MagicMock(spec=ICrudRepository)

def test_pyrepopal_workflow_service_initialization(
    mock_data_collect_service, mock_ai_service, mock_analysis_session_repo,
    mock_system_profile_repo, mock_repository_snapshot_repo,
    mock_generated_prompt_repo, mock_ai_analysis_result_repo
):
    """Tests that PyRepoPalWorkflowService initializes correctly with all mocked dependencies."""
    service = PyRepoPalWorkflowService(
        data_collect_service=mock_data_collect_service,
        ai_service=mock_ai_service,
        analysis_session_repo=mock_analysis_session_repo,
        system_profile_repo=mock_system_profile_repo,
        repository_snapshot_repo=mock_repository_snapshot_repo,
        generated_prompt_repo=mock_generated_prompt_repo,
        ai_analysis_result_repo=mock_ai_analysis_result_repo
    )
    assert service is not None
    assert service.data_collect_service == mock_data_collect_service
    assert service.ai_service == mock_ai_service
    assert service.analysis_session_repo == mock_analysis_session_repo
    assert service.system_profile_repo == mock_system_profile_repo
    assert service.repository_snapshot_repo == mock_repository_snapshot_repo
    assert service.generated_prompt_repo == mock_generated_prompt_repo
    assert service.ai_analysis_result_repo == mock_ai_analysis_result_repo

@pytest.fixture
def workflow_service(
    mock_data_collect_service, mock_ai_service, mock_analysis_session_repo,
    mock_system_profile_repo, mock_repository_snapshot_repo,
    mock_generated_prompt_repo, mock_ai_analysis_result_repo
):
    """Provides a PyRepoPalWorkflowService instance with all dependencies mocked."""
    return PyRepoPalWorkflowService(
        data_collect_service=mock_data_collect_service,
        ai_service=mock_ai_service,
        analysis_session_repo=mock_analysis_session_repo,
        system_profile_repo=mock_system_profile_repo,
        repository_snapshot_repo=mock_repository_snapshot_repo,
        generated_prompt_repo=mock_generated_prompt_repo,
        ai_analysis_result_repo=mock_ai_analysis_result_repo
    )

def test_analyze_repository_happy_path(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_system_profile_repo, # Removed type hint
    mock_repository_snapshot_repo, # Removed type hint
    mock_generated_prompt_repo, # Removed type hint
    mock_ai_service: MagicMock,
    mock_ai_analysis_result_repo # Removed type hint
):
    """Tests the happy path where all data collection and persistence succeed."""
    # --- Mock Setup ---
    mock_session_id = 123
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session

    mock_system_info = {"os_info": {"mock_platform": "TestOS"}} # Corrected structure
    mock_repo_info = {"readme_content": "Test README"}
    mock_prompt_str = "Test prompt content"
    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {
        "system_info": mock_system_info,
        "repo_info": mock_repo_info,
        "prompt_str": mock_prompt_str
    }

    mock_system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info=mock_system_info.get("os_info"))
    mock_repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README", requirements_txt_content=None, environment_yaml_content=None, existing_min_sys_reqs_content=None)
    
    mock_prompt_id = 99
    mock_generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=mock_prompt_id, session_id=mock_session_id, prompt_content=mock_prompt_str, prompt_type="initial_analysis", creation_timestamp="now", template_name_used="template.md")

    mock_ai_response_raw = "{\"key\": \"value\"}"
    mock_ai_service.generate_text.return_value = mock_ai_response_raw
    
    # Mock for initial save of AIAnalysisResultDTO
    saved_ai_result_dto_before_parse = AIAnalysisResultDTO(result_id=1, prompt_id=mock_prompt_id, ai_response_raw=mock_ai_response_raw, response_timestamp="now")
    mock_ai_analysis_result_repo.create.return_value = saved_ai_result_dto_before_parse
    # Mock for update after parsing
    mock_ai_analysis_result_repo.update.return_value = AIAnalysisResultDTO(result_id=1, prompt_id=mock_prompt_id, ai_response_raw=mock_ai_response_raw, response_timestamp="now", parsed_system_requirements_json=mock_ai_response_raw)

    # --- Call Method ---
    result_session = workflow_service.analyze_repository("test/repo", "template.md")

    # --- Assertions ---
    assert result_session is not None
    assert result_session.session_id == mock_session_id
    mock_data_collect_service.prepare_analysis_data_and_prompt.assert_called_once_with(repo_path="test/repo", template_filename="template.md")
    
    mock_system_profile_repo.create.assert_called_once()
    # We could add more detailed assertions on the DTO passed to create if needed
    assert mock_system_profile_repo.create.call_args[0][0].session_id == mock_session_id
    assert mock_system_profile_repo.create.call_args[0][0].os_info == mock_system_info.get("os_info")

    mock_repository_snapshot_repo.create.assert_called_once()
    assert mock_repository_snapshot_repo.create.call_args[0][0].session_id == mock_session_id
    assert mock_repository_snapshot_repo.create.call_args[0][0].readme_content == mock_repo_info["readme_content"]

    mock_generated_prompt_repo.create.assert_called_once()
    assert mock_generated_prompt_repo.create.call_args[0][0].session_id == mock_session_id
    assert mock_generated_prompt_repo.create.call_args[0][0].prompt_content == mock_prompt_str
    
    mock_ai_service.generate_text.assert_called_once_with(mock_prompt_str)
    mock_ai_analysis_result_repo.create.assert_called_once()
    ai_result_dto_arg = mock_ai_analysis_result_repo.create.call_args[0][0]
    assert ai_result_dto_arg.prompt_id == mock_prompt_id
    assert ai_result_dto_arg.ai_response_raw == mock_ai_response_raw

    mock_ai_analysis_result_repo.update.assert_called_once()
    updated_ai_result_dto_arg = mock_ai_analysis_result_repo.update.call_args[0][0]
    assert updated_ai_result_dto_arg.result_id == 1 # from saved_ai_result_dto_before_parse
    assert updated_ai_result_dto_arg.parsed_system_requirements_json == mock_ai_response_raw

    # In happy path, status should be "completed_successfully" (or whatever the final success status is)
    # For now, the method ends before AI interaction, so let's check the last status update before that.
    # The provided code sets it to "completed_successfully" if all these steps pass.
    assert result_session.status == "completed_successfully"
    mock_analysis_session_repo.update.assert_called_with(result_session)


def test_analyze_repository_no_system_info(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_system_profile_repo: MagicMock # We need to assert it's NOT called
):
    """Tests behavior when no system information is collected."""
    mock_session_id = 456
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_no_sysinfo", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session

    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {
        "system_info": None, # Key point: system_info is None
        "repo_info": {"readme_content": "Test README"},
        "prompt_str": "Test prompt"
    }
    # Assume other saves succeed
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    workflow_service.generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=1, session_id=mock_session_id, prompt_content="Test prompt", prompt_type="initial", creation_timestamp="now", template_name_used="template.md")
    
    mock_valid_json_response = "{\"key\": \"mock_ai_output_for_no_sys_info_test\"}"
    workflow_service.ai_service.generate_text.return_value = mock_valid_json_response
    # Mock initial save of AI result
    workflow_service.ai_analysis_result_repo.create.return_value = AIAnalysisResultDTO(result_id=1, prompt_id=1, ai_response_raw=mock_valid_json_response, response_timestamp="now")
    # Mock update after parsing
    workflow_service.ai_analysis_result_repo.update.return_value = AIAnalysisResultDTO(result_id=1, prompt_id=1, ai_response_raw=mock_valid_json_response, response_timestamp="now", parsed_system_requirements_json=mock_valid_json_response)


    result_session = workflow_service.analyze_repository("test/repo_no_sysinfo", "template.md")

    assert result_session is not None
    mock_system_profile_repo.create.assert_not_called() # System profile save should be skipped
    workflow_service.ai_service.generate_text.assert_called_once() # AI interaction should still happen
    assert result_session.status == "completed_successfully" # Assuming it still completes


def test_analyze_repository_snapshot_save_fails(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_repository_snapshot_repo: MagicMock
):
    """Tests behavior when repository snapshot save fails (critical)."""
    mock_session_id = 789
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_fail_snapshot", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session

    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {
        "system_info": {"os_info": {"mock_platform": "TestOS"}}, # Corrected structure
        "repo_info": {"readme_content": "Test README"},
        "prompt_str": "Test prompt"
    }
    # System profile save succeeds (or is skipped if system_info was None)
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={"mock_platform": "TestOS"})
    
    mock_repository_snapshot_repo.create.return_value = None # Simulate failure

    result_session = workflow_service.analyze_repository("test/repo_fail_snapshot", "template.md")

    assert result_session is not None
    assert result_session.session_id == mock_session_id
    assert result_session.status == "failed_repo_snapshot_save"
    mock_analysis_session_repo.update.assert_called_with(result_session)
    workflow_service.generated_prompt_repo.create.assert_not_called() # Should not proceed to save prompt


def test_analyze_repository_prompt_save_fails(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_generated_prompt_repo: MagicMock
):
    """Tests behavior when generated prompt save fails (critical)."""
    mock_session_id = 101
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_fail_prompt", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session

    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {
        "system_info": {"os_info": {"mock_platform": "TestOS"}}, # Corrected structure
        "repo_info": {"readme_content": "Test README"},
        "prompt_str": "Test prompt"
    }
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={"mock_platform": "TestOS"})
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    
    mock_generated_prompt_repo.create.return_value = None # Simulate failure

    result_session = workflow_service.analyze_repository("test/repo_fail_prompt", "template.md")

    assert result_session is not None
    assert result_session.session_id == mock_session_id
    assert result_session.status == "failed_prompt_save"
    mock_analysis_session_repo.update.assert_called_with(result_session)
    # AI service interaction should not happen
    workflow_service.ai_service.generate_text.assert_not_called()

def test_analyze_repository_ai_interaction_empty_response(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_ai_service: MagicMock
):
    """Tests behavior when AI service returns an empty response."""
    mock_session_id = 202
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_ai_empty", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session

    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {
        "system_info": {"os_info": {"mock_platform": "TestOS"}}, # Corrected structure
        "repo_info": {"readme_content": "Test README"},
        "prompt_str": "Test prompt for AI"
    }
    # Assume prior saves succeed
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={"mock_platform": "TestOS"})
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    workflow_service.generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=1, session_id=mock_session_id, prompt_content="Test prompt for AI", prompt_type="initial", creation_timestamp="now", template_name_used="template.md")

    mock_ai_service.generate_text.return_value = None # Simulate empty AI response

    result_session = workflow_service.analyze_repository("test/repo_ai_empty", "template.md")

    assert result_session is not None
    assert result_session.status == "failed_ai_empty_response"
    mock_analysis_session_repo.update.assert_called_with(result_session)
    workflow_service.ai_analysis_result_repo.create.assert_not_called()

def test_analyze_repository_ai_interaction_exception(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_ai_service: MagicMock
):
    """Tests behavior when AI service interaction raises an exception."""
    mock_session_id = 303
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_ai_exception", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session

    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {
        "system_info": {"os_info": {"mock_platform": "TestOS"}}, # Corrected structure
        "repo_info": {"readme_content": "Test README"},
        "prompt_str": "Test prompt for AI exception"
    }
    # Assume prior saves succeed
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={"mock_platform": "TestOS"})
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    workflow_service.generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=1, session_id=mock_session_id, prompt_content="Test prompt for AI exception", prompt_type="initial", creation_timestamp="now", template_name_used="template.md")

    mock_ai_service.generate_text.side_effect = Exception("AI API Error")

    result_session = workflow_service.analyze_repository("test/repo_ai_exception", "template.md")

    assert result_session is not None
    assert result_session.status == "failed_ai_interaction_exception"
    mock_analysis_session_repo.update.assert_called_with(result_session)
    workflow_service.ai_analysis_result_repo.create.assert_not_called()

def test_analyze_repository_ai_result_save_fails(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_ai_service: MagicMock,
    mock_ai_analysis_result_repo # Removed type hint
):
    """Tests behavior when saving AI analysis result fails."""
    mock_session_id = 404
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_ai_result_fail", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session
    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {"system_info": None, "repo_info": {}, "prompt_str": "prompt"} # system_info as None
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={})
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    workflow_service.generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=1, session_id=mock_session_id, prompt_content="prompt", prompt_type="initial", creation_timestamp="now", template_name_used="template.md")
    mock_ai_service.generate_text.return_value = "AI Raw Response"
    mock_ai_analysis_result_repo.create.return_value = None # Simulate failure

    result_session = workflow_service.analyze_repository("test/repo_ai_result_fail", "template.md")
    assert result_session is not None
    assert result_session.status == "failed_ai_result_save"
    mock_analysis_session_repo.update.assert_called_with(result_session)

def test_analyze_repository_ai_response_parsing_fails(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_ai_service: MagicMock,
    mock_ai_analysis_result_repo # Removed type hint
):
    """Tests behavior when AI response is not valid JSON."""
    mock_session_id = 505
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_parse_fail", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session
    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {"system_info": None, "repo_info": {}, "prompt_str": "prompt"} # system_info as None
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={})
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    workflow_service.generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=1, session_id=mock_session_id, prompt_content="prompt", prompt_type="initial", creation_timestamp="now", template_name_used="template.md")
    
    invalid_json_response = "This is not JSON"
    mock_ai_service.generate_text.return_value = invalid_json_response
    # Mock initial save of AI result
    mock_ai_analysis_result_repo.create.return_value = AIAnalysisResultDTO(result_id=1, prompt_id=1, ai_response_raw=invalid_json_response, response_timestamp="now")

    result_session = workflow_service.analyze_repository("test/repo_parse_fail", "template.md")

    assert result_session is not None
    assert result_session.status == "failed_ai_response_parsing"
    mock_analysis_session_repo.update.assert_called_with(result_session)
    mock_ai_analysis_result_repo.update.assert_not_called() # Update should not be called if parsing fails

def test_analyze_repository_ai_result_update_with_parsed_data_fails(
    workflow_service: PyRepoPalWorkflowService,
    mock_data_collect_service: MagicMock,
    mock_analysis_session_repo, # Removed type hint
    mock_ai_service: MagicMock,
    mock_ai_analysis_result_repo # Removed type hint
):
    """Tests behavior when updating AIAnalysisResultDTO with parsed data fails."""
    mock_session_id = 606
    mock_initial_session = AnalysisSessionDTO(session_id=mock_session_id, target_repository_identifier="test/repo_update_fail", analysis_timestamp="sometime", status="session_created", user_notes=None)
    mock_analysis_session_repo.create.return_value = mock_initial_session
    mock_data_collect_service.prepare_analysis_data_and_prompt.return_value = {"system_info": None, "repo_info": {}, "prompt_str": "prompt"} # system_info as None
    workflow_service.system_profile_repo.create.return_value = SystemProfileDTO(profile_id=1, session_id=mock_session_id, profile_timestamp="now", os_info={})
    workflow_service.repository_snapshot_repo.create.return_value = RepositorySnapshotDTO(snapshot_id=1, session_id=mock_session_id, readme_content="Test README")
    workflow_service.generated_prompt_repo.create.return_value = GeneratedPromptDTO(prompt_id=1, session_id=mock_session_id, prompt_content="prompt", prompt_type="initial", creation_timestamp="now", template_name_used="template.md")
    
    valid_json_response = "{\"key\": \"valid_json\"}"
    mock_ai_service.generate_text.return_value = valid_json_response
    mock_ai_analysis_result_repo.create.return_value = AIAnalysisResultDTO(result_id=1, prompt_id=1, ai_response_raw=valid_json_response, response_timestamp="now")
    mock_ai_analysis_result_repo.update.return_value = None # Simulate failure of the update operation

    result_session = workflow_service.analyze_repository("test/repo_update_fail", "template.md")

    assert result_session is not None
    assert result_session.status == "failed_ai_result_update_parsed"
    mock_analysis_session_repo.update.assert_called_with(result_session) # The session status update
    mock_ai_analysis_result_repo.update.assert_called_once() # Assert that update was attempted