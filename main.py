# C:\Users\jarde\Projects\JennAI\main.py

import sys
import os
from pathlib import Path
from dotenv import load_dotenv # Import load_dotenv

# --- Root Project Path Setup (CRITICAL for Monorepo Imports) ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows all sub-projects (project/data, project/business, etc.)
# and centralized modules (config, core) to be imported using absolute paths.
jennai_root = Path(__file__).resolve().parent
if str(jennai_root) not in sys.path:
    sys.path.append(str(jennai_root))

# Load environment variables from .env file (if it exists)
load_dotenv(dotenv_path=jennai_root / ".env")

# --- Centralized Core Imports ---
# These modules are now directly discoverable from the JennAI root
from config.loguru_setup import setup_logging
from config.config import DEBUG_MODE
from core.dependency_container import DependencyContainer

# --- Global Setup (Orchestrated by main.py) ---
setup_logging(debug_mode=DEBUG_MODE) # Initialize Loguru for the entire monorepo
from loguru import logger # Import the configured logger instance

logger.info(f"INFO - JennAI Monorepo Main: Orchestration initialized.")
logger.info(f"INFO - Python interpreter: {sys.executable}")
logger.info(f"INFO - Current working directory: {os.getcwd()}")
logger.info(f"INFO - JennAI project root added to PATH: {jennai_root}")
logger.info(f"INFO - Running in DEBUG_MODE: {DEBUG_MODE}")

# --- Dependency Configuration Functions for Sub-Projects ---
# These functions will be defined in main.py to configure specific sub-project dependencies.

def configure_project_business_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/business` layer.
    """
    logger.info("INFO - Configuring src/business dependencies (conceptual).")

    # --- AI Service Registration (Conceptual) ---
    from src.business.interfaces.IAIService import IAIService
    # Placeholder for a concrete AI service implementation
    class AIGenerator(IAIService):
        def generate_text(self, prompt: str) -> str:
            logger.info(f"AIGenerator: Generating text for prompt: {prompt[:50]}...")
            return "Conceptual AI generated text."
    container.register_singleton(IAIService, AIGenerator)
    logger.info("Registered AIGenerator for IAIService.")
    # We log success to align with the integration test's expectations for this layer.
    logger.success("SUCCESS - src/business dependencies configured (conceptual).")

    
def configure_project_data_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/data` layer.
    """
    logger.info("INFO - Configuring src/data dependencies (conceptual).")
    # This is a placeholder. As data repositories are added, they will be registered here,
    # for now, we just log success to indicate the function was called.
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

    flask_app_instance = None # Initialize to None

    # Call all configuration functions
    configure_project_business_dependencies(global_container)
    configure_project_data_dependencies(global_container)
    flask_app_instance = configure_project_presentation_dependencies(global_container)

    logger.success("SUCCESS - JennAI OS has successfully booted and performed initial checks. Vibe coding initiated!")

    # Run the Flask app if main.py is executed directly and DEBUG_MODE is True
    # AND we are not in a test run that should prevent the server from starting
    # if flask_app_instance and DEBUG_MODE and not os.getenv("PYTEST_RUNNING_MAIN"):
    #     logger.info(f"Starting Flask development server on http://0.0.0.0:5000 (DEBUG_MODE: {DEBUG_MODE})...")
    #     # Use host='0.0.0.0' to make the server accessible from your network
    #     # Use port=5000 (or any other port you prefer)
    #     flask_app_instance.run(debug=DEBUG_MODE, host='0.0.0.0', port=5000)
    # elif flask_app_instance:
    #     logger.info(f"Flask app created. Not starting dev server automatically (DEBUG_MODE: {DEBUG_MODE}, PYTEST_RUNNING_MAIN: {os.getenv('PYTEST_RUNNING_MAIN')}).")
    #     if DEBUG_MODE and not os.getenv("PYTEST_RUNNING_MAIN"):
    #          logger.info("To run the development server, ensure DEBUG_MODE is True in your config/config.py and run 'python main.py'.")
    #     elif os.getenv("PYTEST_RUNNING_MAIN"):
    #         logger.info("Flask dev server start skipped due to PYTEST_RUNNING_MAIN environment variable.")