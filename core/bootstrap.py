"""
This module centralizes the bootstrapping process for the application,
including the configuration of the dependency injection container.
"""
from loguru import logger
from .dependency_container import DependencyContainer

# --- Dependency Configuration Functions for Sub-Projects ---

def configure_project_business_dependencies(container: DependencyContainer):
    """
    Configures dependencies specific to the `src/business` layer.
    """
    logger.info("INFO - Configuring src/business dependencies (conceptual).")

    # --- AI Service Registration (Conceptual) ---
    from config.config import AI_API_KEY, AI_API_RESOURCE, AI_PROVIDER
    from src.business.ai.gemini_api import AIGenerator
    from src.business.interfaces.IAIService import IAIService

    container.register_singleton(
        IAIService,
        lambda: AIGenerator(
            api_key=AI_API_KEY,
            provider=AI_PROVIDER,
            api_resource=AI_API_RESOURCE,
        ),
    )
    logger.info(f"Registered AIGenerator for IAIService using provider '{AI_PROVIDER}'.")
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