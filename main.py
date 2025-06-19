# C:\Users\jarde\Projects\JennAI\main.py

import sys
import os
from pathlib import Path

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
    
    # Import the AIGenerator from its correct location
    from src.business.ai.gemini_api import AIGenerator
    
    # Register AIGenerator as a singleton or transient based on your needs.
    # Using a factory lambda to provide the API key from environment variables.
    container.register_singleton(AIGenerator, lambda: AIGenerator(api_key=os.getenv("GOOGLE_API_KEY")))
    logger.success("SUCCESS - src/business dependencies configured (conceptual).")

def configure_project_presentation_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/presentation` layer.
    """
    logger.info("INFO - Configuring src/presentation dependencies (conceptual).")
    # Example: If you had a Flask app instance defined in src/presentation/app.py
    # from src.presentation.app import create_flask_app
    logger.success("SUCCESS - src/presentation dependencies configured (conceptual).")

# --- Main Application Execution Block ---
if __name__ == '__main__':
    global_container = DependencyContainer() 

    logger.info("INFO - JennAI OS is booting up and configuring core services...")

    configure_project_business_dependencies(global_container)
    configure_project_presentation_dependencies(global_container)


    logger.success("SUCCESS - JennAI OS has successfully booted and performed initial checks. Vibe coding initiated!")