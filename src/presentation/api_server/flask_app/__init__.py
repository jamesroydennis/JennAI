from flask import Flask
from loguru import logger

# Assuming DependencyContainer might be type-hinted or used if passed directly
# from core.dependency_container import DependencyContainer

def create_app(container=None): # Accept the dependency container
    """
    Factory function to create and configure the Flask application.
    """
    logger.info("Creating Flask application instance...")
    # __name__ here will be 'src.presentation.api_server.flask_app'
    # Flask will look for 'templates' and 'static' folders relative to this 'flask_app' directory.
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # --- Configuration ---
    # Example: Load configuration from a config object or environment variables
    # app.config.from_object('your_project.config.FlaskConfig')
    # app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_dev')
    logger.info(f"Flask app instance created. Static folder: {app.static_folder}, Template folder: {app.template_folder}")

    # --- Dependency Injection ---
    # Store the container on the app context if needed by routes or extensions
    if container:
        app.container = container
        logger.info("Dependency container attached to Flask app.")

    # --- Register Blueprints ---
    from .routes.default_routes import default_bp  # Import your blueprint(s)
    app.register_blueprint(default_bp)
    logger.info("Registered 'default_bp' blueprint.")

    logger.success("Flask application instance configured successfully.")
    return app

