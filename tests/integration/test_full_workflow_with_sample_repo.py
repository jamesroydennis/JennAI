# /home/jdennis/Projects/JennAI/tests/integration/test_full_workflow_with_sample_repo.py

import sys
from pathlib import Path
import pytest

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.business.pyrepopal_workflow_service import PyRepoPalWorkflowService
from core.dependency_container import DependencyContainer
from src.data.obj.analysis_session_dto import AnalysisSessionDTO
from config.config import DATABASE_FILE_PATH
from src.data.implementations.analysis_session_sqlite_repository import AnalysisSessionSQLiteRepository

@pytest.fixture(scope="module")
def integration_container():
    """
    Sets up a dependency container with real implementations for integration testing.
    This container is scoped to the module, meaning it's created once per test file.
    """
    container = DependencyContainer()

    # --- Data Layer ---
    from main import configure_project_data_dependencies
    configure_project_data_dependencies(container)

    # --- Business Layer ---
    from main import configure_project_business_dependencies
    configure_project_business_dependencies(container)

    return container

def test_full_workflow_with_sample_repo(integration_container: DependencyContainer):
    """
    Tests the full analysis workflow using the sample repository data.
    This test uses real implementations, so it interacts with the database and AI service.
    """
    # --- Resolve Dependencies ---
    workflow_service = integration_container.resolve(PyRepoPalWorkflowService)
    assert workflow_service is not None, "Workflow service could not be resolved."

    # --- Define Test Parameters ---
    sample_repo_path = str(Path(__file__).resolve().parent.parent / "sample_repos" / "proofconcept")
    prompt_template_filename = "generate_min_sys_reqs_from_repo_prompt.md"
    user_notes = "Integration test run with sample repository."

    # --- Run the Workflow ---
    result_session = workflow_service.analyze_repository(
        target_repo_identifier=sample_repo_path,
        prompt_template_filename=prompt_template_filename,
        user_notes=user_notes
    )

    # --- Assertions ---
    assert result_session is not None, "Analysis session was not created."
    assert isinstance(result_session, AnalysisSessionDTO)
    assert result_session.status == "completed_successfully", f"Workflow did not complete successfully. Status: {result_session.status}"

    # --- Additional Checks (Optional) ---
    # You can add more specific checks here, such as:
    # - Verify that the AI analysis result was saved and parsed correctly.
    # - Check the contents of the parsed system requirements.
    # - Query the database to ensure the data was persisted as expected.
    # Example:
    # analysis_session_repo = integration_container.resolve(ICrudRepository[AnalysisSessionDTO])
    # retrieved_session = analysis_session_repo.read_by_id(result_session.session_id)
    # assert retrieved_session is not None
    # assert retrieved_session.status == "completed_successfully"