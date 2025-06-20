# /home/jdennis/Projects/JennAI/src/business/ai/tests/test_data_collect_service.py

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.business.ai.data_collect_service import DataCollectService
from src.business.ai import repo_data_collector # For mocking its output
from src.business.sys import sys_profiler # For mocking its output/main

# --- Fixtures ---

@pytest.fixture
def service():
    """Provides an instance of DataCollectService."""
    return DataCollectService()

@pytest.fixture
def mock_template_content():
    """Provides a sample template string."""
    return """
Repository Description: {{repository_description}}
README: {{readme_content}}
REQUIREMENTS_TXT: {{requirements_txt_content}}
ENVIRONMENT_YAML: {{environment_yaml_content}}
EXISTING_MIN_REQS: {{existing_min_sys_reqs_content}}
UNEXPECTED_KEY: {{unexpected_key_from_data}}
"""

@pytest.fixture
def sample_repo_data_full():
    """Simulates full data returned by repo_data_collector."""
    return {
        "readme_content": "This is a README.",
        "requirements_txt_content": "package1==1.0\npackage2>=2.0",
        "environment_yaml_content": "name: test_env\ndependencies:\n  - python=3.9",
        "existing_min_sys_reqs_content": "Min RAM: 8GB", # Assuming repo_collector might find this
        "repository_description": "A sample repository for testing.",
        "unexpected_key_from_data": "Some extra info.",
        "error": None
    }

@pytest.fixture
def sample_repo_data_partial():
    """Simulates partial data (some files missing) returned by repo_data_collector."""
    return {
        "readme_content": "This is a README.",
        "requirements_txt_content": None, # requirements.txt not found
        "environment_yaml_content": None, # environment.yaml not found
        "existing_min_sys_reqs_content": None, # No existing reqs file found
        "repository_description": "Another sample repo.",
        "error": None
    }

@pytest.fixture
def sample_repo_data_empty():
    """Simulates empty data (all relevant files missing) returned by repo_data_collector."""
    return {
        "readme_content": None,
        "requirements_txt_content": None,
        "environment_yaml_content": None,
        "existing_min_sys_reqs_content": None,
        "error": None
    }

# --- Test Cases ---

def test_load_prompt_template_exists(service, tmp_path):
    """Test loading an existing prompt template."""
    template_dir = tmp_path / "src" / "business" / "ai" / "prompt_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_file = template_dir / "test_template.md"
    template_file.write_text("Hello {{name}}")

    # Temporarily override the service's template directory
    original_template_dir = service.prompt_template_dir
    service.prompt_template_dir = template_dir
    
    content = service._load_prompt_template("test_template.md")
    assert content == "Hello {{name}}"
    
    # Restore original path
    service.prompt_template_dir = original_template_dir

def test_load_prompt_template_not_exists(service):
    """Test loading a non-existent prompt template."""
    content = service._load_prompt_template("non_existent_template.md")
    assert content is None

def test_populate_prompt_template_full_data(service, mock_template_content, sample_repo_data_full):
    """Test populating template with all data present."""
    populated = service._populate_prompt_template(mock_template_content, sample_repo_data_full)
    assert "Repository Description: A sample repository for testing." in populated
    assert "README: This is a README." in populated
    assert "REQUIREMENTS_TXT: package1==1.0\npackage2>=2.0" in populated
    assert "ENVIRONMENT_YAML: name: test_env\ndependencies:\n  - python=3.9" in populated
    assert "EXISTING_MIN_REQS: Min RAM: 8GB" in populated
    assert "UNEXPECTED_KEY: Some extra info." in populated

def test_populate_prompt_template_partial_data(service, mock_template_content, sample_repo_data_partial):
    """Test populating template when some repository data is missing."""
    populated = service._populate_prompt_template(mock_template_content, sample_repo_data_partial)
    assert "Repository Description: Another sample repo." in populated
    assert "README: This is a README." in populated
    assert "REQUIREMENTS_TXT: requirements.txt not found or empty." in populated
    assert "ENVIRONMENT_YAML: environment.yaml not found or empty." in populated
    assert "EXISTING_MIN_REQS: No existing min-sys-requirements file found or empty." in populated
    assert "UNEXPECTED_KEY: unexpected_key_from_data not found or empty." in populated # Default for unexpected keys not in data

def test_populate_prompt_template_empty_data(service, mock_template_content, sample_repo_data_empty):
    """Test populating template when all repository data is missing."""
    populated = service._populate_prompt_template(mock_template_content, sample_repo_data_empty)
    assert "Repository Description: No repository description provided." in populated # Default
    assert "README: README.md not found or empty." in populated
    assert "REQUIREMENTS_TXT: requirements.txt not found or empty." in populated
    assert "ENVIRONMENT_YAML: environment.yaml not found or empty." in populated
    assert "EXISTING_MIN_REQS: No existing min-sys-requirements file found or empty." in populated
    assert "UNEXPECTED_KEY: unexpected_key_from_data not found or empty." in populated

@patch('src.business.ai.data_collect_service.sys_profiler.main')
@patch('src.business.ai.data_collect_service.repo_data_collector.collect_repository_data')
def test_prepare_analysis_data_and_prompt_success( # Renamed test to reflect method
    mock_collect_repo_data, mock_sys_profiler_main, service, 
    tmp_path, mock_template_content, sample_repo_data_full
):
    """
    Integration-style test for the main service method, mocking external calls.
    """
    # --- Setup Mocks ---
    mock_collect_repo_data.return_value = sample_repo_data_full
    # sys_profiler.main doesn't return anything, just needs to be callable

    # --- Setup Temporary Paths for Service ---
    # Template directory and file
    template_dir = tmp_path / "src" / "business" / "ai" / "prompt_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_file = template_dir / "actual_template.md"
    template_file.write_text(mock_template_content) # Use the mock_template_content for this test
    
    # Generated prompts directory is no longer managed by DataCollectService directly
    # generated_prompts_dir = tmp_path / "src" / "data" / "generated_prompts"
    # generated_prompts_dir.mkdir(parents=True, exist_ok=True) 


    # Override service paths to use tmp_path
    service.prompt_template_dir = template_dir
    # service.generated_prompts_dir = generated_prompts_dir # This attribute was removed
    # sys_info_file path is also part of service, but _collect_system_info is mocked for its side effect
    # We also need to mock the sys_info_file location if _collect_system_info is to write/read from it.
    # However, for this test, sys_profiler.main is mocked, and _collect_system_info reads from service.sys_info_file
    # Let's ensure sys_info_file points to a temporary location for the _collect_system_info part.
    temp_sys_info_dir = tmp_path / "src" / "data" / "system_info"
    temp_sys_info_dir.mkdir(parents=True, exist_ok=True)
    service.sys_info_file = temp_sys_info_dir / "hardware_specs.json"
    # Create a dummy system info file that sys_profiler.main would create
    # and _collect_system_info would read.
    dummy_sys_info_content = {"os": "mockOS"}
    with open(service.sys_info_file, 'w') as f:
        import json
        json.dump(dummy_sys_info_content, f)

    # --- Call the Service Method ---
    repo_path_to_scan = "/fake/repo/path" # This path isn't actually used due to mocking collect_repository_data
    
    result_dict = service.prepare_analysis_data_and_prompt(
        repo_path=repo_path_to_scan,
        template_filename="actual_template.md" # The template file we created in tmp_path
    )

    # --- Assertions ---
    mock_sys_profiler_main.assert_called_once()
    mock_collect_repo_data.assert_called_once_with(repo_path_to_scan)
    
    assert result_dict is not None
    assert "prompt_str" in result_dict
    assert "system_info" in result_dict
    assert "repo_info" in result_dict
    assert result_dict["system_info"] == dummy_sys_info_content # Check if mocked system info was loaded
    assert result_dict["repo_info"] == sample_repo_data_full

    # Verify content of the generated prompt
    generated_prompt_text = result_dict["prompt_str"]
    assert "Repository Description: A sample repository for testing." in generated_prompt_text
    assert "README: This is a README." in generated_prompt_text
    assert "REQUIREMENTS_TXT: package1==1.0\npackage2>=2.0" in generated_prompt_text
    assert "UNEXPECTED_KEY: Some extra info." in generated_prompt_text

@patch('src.business.ai.data_collect_service.repo_data_collector.collect_repository_data')
def test_prepare_analysis_data_and_prompt_repo_collection_fails(mock_collect_repo_data, service): # Renamed test
    """Test case where repository data collection fails."""
    mock_collect_repo_data.return_value = None # Simulate failure

    result_dict = service.prepare_analysis_data_and_prompt(
        repo_path="/fake/repo",
        template_filename="any_template.md"
    )
    assert result_dict is None