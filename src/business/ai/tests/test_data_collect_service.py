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
def test_generate_and_save_repo_analysis_prompt_success(
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
    
    # Generated prompts directory
    generated_prompts_dir = tmp_path / "src" / "data" / "generated_prompts"
    generated_prompts_dir.mkdir(parents=True, exist_ok=True) # Ensure this temp dir is created


    # Override service paths to use tmp_path
    service.prompt_template_dir = template_dir
    service.generated_prompts_dir = generated_prompts_dir
    # sys_info_file path is also part of service, but _collect_system_info is mocked for its side effect

    # --- Call the Service Method ---
    repo_path_to_scan = "/fake/repo/path" # This path isn't actually used due to mocking collect_repository_data
    output_filename = "test_output_prompt.txt"
    
    result_path = service.generate_and_save_repo_analysis_prompt(
        repo_path=repo_path_to_scan,
        template_filename="actual_template.md", # The template file we created in tmp_path
        output_prompt_filename=output_filename
    )

    # --- Assertions ---
    mock_sys_profiler_main.assert_called_once()
    mock_collect_repo_data.assert_called_once_with(repo_path_to_scan)
    
    assert result_path is not None
    assert result_path.name == output_filename
    assert result_path.parent == generated_prompts_dir
    assert result_path.exists()

    # Verify content of the generated prompt
    generated_prompt_text = result_path.read_text()
    assert "Repository Description: A sample repository for testing." in generated_prompt_text
    assert "README: This is a README." in generated_prompt_text
    assert "REQUIREMENTS_TXT: package1==1.0\npackage2>=2.0" in generated_prompt_text
    assert "UNEXPECTED_KEY: Some extra info." in generated_prompt_text

@patch('src.business.ai.data_collect_service.repo_data_collector.collect_repository_data')
def test_generate_and_save_repo_analysis_prompt_repo_collection_fails(mock_collect_repo_data, service):
    """Test case where repository data collection fails."""
    mock_collect_repo_data.return_value = None # Simulate failure

    result_path = service.generate_and_save_repo_analysis_prompt(
        repo_path="/fake/repo",
        template_filename="any_template.md",
        output_prompt_filename="wont_be_created.txt"
    )
    assert result_path is None