# C:\Users\jarde\Projects\JennAI\main.py

import sys
import os
from pathlib import Path

# --- Load Environment Variables from .env file ---
from dotenv import load_dotenv
load_dotenv() # This will load .env file from the current directory or parent directories

# --- Root Project Path Setup (CRITICAL for Monorepo Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows all sub-projects (project/data, project/business, etc.)
# and centralized modules (config, core) to be imported using absolute paths.
jennai_root = Path(__file__).resolve().parent
if str(jennai_root) not in sys.path:
    sys.path.append(str(jennai_root))

# --- Centralized Core Imports ---
# These modules are now directly discoverable from the JennAI root
from config.loguru_setup import setup_logging
from config.config import DEBUG_MODE, DATABASE_FILE_PATH # Import DATABASE_FILE_PATH
from core.dependency_container import DependencyContainer

# --- Global Setup (Orchestrated by main.py) ---
setup_logging(debug_mode=DEBUG_MODE) # Initialize Loguru for the entire monorepo
from loguru import logger # Import the configured logger instance

logger.info(f"INFO - PyRepo-Pal Main: Orchestration initialized.")
logger.info(f"INFO - Python interpreter: {sys.executable}")
logger.info(f"INFO - Current working directory: {os.getcwd()}")
logger.info(f"INFO - PyRepo-Pal project root added to PATH: {jennai_root}")
logger.info(f"INFO - Running in DEBUG_MODE: {DEBUG_MODE}")

# --- Dependency Configuration Functions for Sub-Projects ---
# These functions will be defined in main.py to configure specific sub-project dependencies.


def configure_project_business_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/business` layer.
    """
    logger.info("INFO - Configuring src/business dependencies (conceptual).")

    # --- AI Service Registration ---
    from src.business.interfaces.IAIService import IAIService
    from src.business.ai.gemini_api import AIGenerator
    from src.business.ai.data_collect_service import DataCollectService
    from src.business.ai.ai_response_parser import AIResponseParser # Import the new parser
    # Import the new workflow service (adjust path if it's different)
    from src.business.pyrepopal_workflow_service import PyRepoPalWorkflowService
    # Import DTOs and ICrudRepository for resolving dependencies
    from src.data.interfaces.ICrudRepository import ICrudRepository
    from src.data.obj.analysis_session_dto import AnalysisSessionDTO
    from src.data.obj.system_profile_dto import SystemProfileDTO
    from src.data.obj.repository_snapshot_dto import RepositorySnapshotDTO
    from src.data.obj.generated_prompt_dto import GeneratedPromptDTO
    from src.data.obj.ai_analysis_result_dto import AIAnalysisResultDTO

    # Register AIGenerator as the concrete implementation for IAIService
    container.register_singleton(IAIService, lambda: AIGenerator(api_key=os.getenv("GOOGLE_API_KEY")))
    logger.info("Registered AIGenerator for IAIService.")
    

    # --- User Management Service Registration (Conceptual) ---
    from src.business.interfaces.IUserManager import IUserManager
    # Assume you have a concrete implementation, e.g., InMemoryUserManager or DatabaseUserManager
    # For this example, let's create a placeholder concrete class here or import it.
    # from src.business.services.user_service import InMemoryUserManager # Example import
    class ConceptualUserManager(IUserManager): # Placeholder
        def create_user(self, user_data): logger.info("ConceptualUserManager: create_user called"); raise NotImplementedError
        def get_user_by_id(self, user_id): logger.info("ConceptualUserManager: get_user_by_id called"); raise NotImplementedError
        def get_user_by_email(self, email): logger.info("ConceptualUserManager: get_user_by_email called"); raise NotImplementedError
    
    container.register_singleton(IUserManager, ConceptualUserManager)
    logger.info("Registered ConceptualUserManager for IUserManager.")

    # --- Register DataCollectService (as it's a dependency for PyRepoPalWorkflowService) ---
    container.register_singleton(DataCollectService, DataCollectService)
    logger.info("Registered DataCollectService.")

    # --- Register AIResponseParser ---
    container.register_singleton(AIResponseParser, AIResponseParser)
    logger.info("Registered AIResponseParser.")

    # --- Register PyRepoPalWorkflowService ---
    # It depends on DataCollectService, IAIService, and several repositories
    container.register_singleton(
        PyRepoPalWorkflowService,
        lambda: PyRepoPalWorkflowService(
            data_collect_service=container.resolve(DataCollectService),
            ai_service=container.resolve(IAIService),
            ai_response_parser=container.resolve(AIResponseParser), # Inject the parser
            # Inject all the required repository dependencies
            analysis_session_repo=container.resolve(ICrudRepository[AnalysisSessionDTO]),
            system_profile_repo=container.resolve(ICrudRepository[SystemProfileDTO]),
            repository_snapshot_repo=container.resolve(ICrudRepository[RepositorySnapshotDTO]),
            generated_prompt_repo=container.resolve(ICrudRepository[GeneratedPromptDTO]),
            ai_analysis_result_repo=container.resolve(ICrudRepository[AIAnalysisResultDTO])
        )
    )
    logger.info("Registered PyRepoPalWorkflowService factory.")

    logger.success("SUCCESS - src/business dependencies configured (conceptual).")

def configure_project_data_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/data` layer.
    """
    logger.info("INFO - Configuring src/data dependencies (conceptual).")

    # --- CRUD Repository Registration (Conceptual for a User entity) ---
    # This part can be removed or adapted if UserDTO is not actually used.
    from src.data.interfaces.ICrudRepository import ICrudRepository
    class UserDTO: pass # Placeholder
    class ConceptualUserRepository(ICrudRepository[UserDTO]): # Placeholder
        def create(self, item): logger.info("ConceptualUserRepository: create called"); raise NotImplementedError
        def read_by_id(self, item_id): logger.info("ConceptualUserRepository: read_by_id called"); raise NotImplementedError
    container.register_singleton(ICrudRepository[UserDTO], ConceptualUserRepository)
    logger.info("Registered ConceptualUserRepository for ICrudRepository[UserDTO] (placeholder).")

    # --- Register SQLite Repositories for PyRepoPal DTOs ---
    from src.data.obj.analysis_session_dto import AnalysisSessionDTO
    from src.data.implementations.analysis_session_sqlite_repository import AnalysisSessionSQLiteRepository
    from src.data.obj.system_profile_dto import SystemProfileDTO
    from src.data.implementations.system_profile_sqlite_repository import SystemProfileSQLiteRepository
    from src.data.obj.repository_snapshot_dto import RepositorySnapshotDTO
    from src.data.implementations.repository_snapshot_sqlite_repository import RepositorySnapshotSQLiteRepository
    # We'll need to create GeneratedPromptSQLiteRepository and AIAnalysisResultSQLiteRepository as well.
    # For now, let's assume they exist and follow the same pattern.
    from src.data.obj.generated_prompt_dto import GeneratedPromptDTO
    from src.data.implementations.generated_prompt_sqlite_repository import GeneratedPromptSQLiteRepository # Assuming this will be created
    from src.data.obj.ai_analysis_result_dto import AIAnalysisResultDTO
    from src.data.implementations.ai_analysis_result_sqlite_repository import AIAnalysisResultSQLiteRepository # Assuming this will be created

    db_path_str = str(DATABASE_FILE_PATH) # Get DB path from config

    container.register_singleton(
        ICrudRepository[AnalysisSessionDTO],
        lambda: AnalysisSessionSQLiteRepository(db_path=db_path_str)
    )
    logger.info(f"Registered AnalysisSessionSQLiteRepository for ICrudRepository[AnalysisSessionDTO] with DB: {db_path_str}")

    container.register_singleton(
        ICrudRepository[SystemProfileDTO],
        lambda: SystemProfileSQLiteRepository(db_path=db_path_str)
    )
    logger.info(f"Registered SystemProfileSQLiteRepository for ICrudRepository[SystemProfileDTO] with DB: {db_path_str}")

    container.register_singleton(
        ICrudRepository[RepositorySnapshotDTO],
        lambda: RepositorySnapshotSQLiteRepository(db_path=db_path_str)
    )
    logger.info(f"Registered RepositorySnapshotSQLiteRepository for ICrudRepository[RepositorySnapshotDTO] with DB: {db_path_str}")

    # Register GeneratedPromptSQLiteRepository
    container.register_singleton(
        ICrudRepository[GeneratedPromptDTO],
        lambda: GeneratedPromptSQLiteRepository(db_path=db_path_str)
    )
    logger.info(f"Registered GeneratedPromptSQLiteRepository for ICrudRepository[GeneratedPromptDTO] with DB: {db_path_str}")

    # Register AIAnalysisResultSQLiteRepository
    container.register_singleton(
        ICrudRepository[AIAnalysisResultDTO],
        lambda: AIAnalysisResultSQLiteRepository(db_path=db_path_str)
    )
    logger.info(f"Registered AIAnalysisResultSQLiteRepository for ICrudRepository[AIAnalysisResultDTO] with DB: {db_path_str}")


    logger.success("SUCCESS - src/data dependencies configured (conceptual).")

def configure_project_presentation_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/presentation` layer.
    """
    logger.info("INFO - Configuring src/presentation dependencies (conceptual).")
    
    # Import the app factory
    from src.presentation.api_server.flask_app import create_app

    flask_app = create_app(container=container) 
    logger.info("Flask application instance created.")
    
    logger.success("SUCCESS - src/presentation dependencies configured (conceptual).")
    # Return the app instance so it can be run by the main execution block
    return flask_app

# --- Main Application Execution Block ---
if __name__ == '__main__':
    global_container = DependencyContainer() 

    logger.info("INFO - JennAI OS is booting up and configuring core services...")

    # Order matters if dependencies are cross-layer during configuration itself,
    # but typically resolution happens lazily.
    # Data layer first, then business layer.
    configure_project_data_dependencies(global_container)
    configure_project_business_dependencies(global_container)

    # Now that all dependencies are registered, we can resolve the workflow service
    # to ensure its own dependencies (like repositories) are injected correctly.
    # This is also a good place to test if the DI setup is correct.
    # workflow_service = global_container.resolve(PyRepoPalWorkflowService)
    # logger.info(f"PyRepoPalWorkflowService resolved: {workflow_service is not None}")

    flask_app_instance = configure_project_presentation_dependencies(global_container)

    logger.success("SUCCESS - JennAI OS has successfully booted and performed initial checks. Vibe coding initiated!")

    # Run the Flask app if main.py is executed directly and DEBUG_MODE is True
    # AND we are not in a test run that should prevent the server from starting
    if flask_app_instance and DEBUG_MODE and not os.getenv("PYTEST_RUNNING_MAIN"):
        logger.info(f"Starting Flask development server on http://0.0.0.0:5000 (DEBUG_MODE: {DEBUG_MODE})...")
        # Use host='0.0.0.0' to make the server accessible from your network
        # Use port=5000 (or any other port you prefer)
        flask_app_instance.run(debug=DEBUG_MODE, host='0.0.0.0', port=5000)
    elif flask_app_instance:
        logger.info(f"Flask app created. Not starting dev server automatically (DEBUG_MODE: {DEBUG_MODE}, PYTEST_RUNNING_MAIN: {os.getenv('PYTEST_RUNNING_MAIN')}).")
        if DEBUG_MODE and not os.getenv("PYTEST_RUNNING_MAIN"):
             logger.info("To run the development server, ensure DEBUG_MODE is True in your config/config.py and run 'python main.py'.")
        elif os.getenv("PYTEST_RUNNING_MAIN"):
            logger.info("Flask dev server start skipped due to PYTEST_RUNNING_MAIN environment variable.")