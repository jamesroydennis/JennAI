import sys
from pathlib import Path
from flask import Flask, send_from_directory
from flask_assets import Environment, Bundle
from core.dependency_container import DependencyContainer
from src.presentation.api_server.flask_app.routes.default_routes import default_bp

# --- Root Project Path Setup ---
# This block ensures the main /JennAI project root is always on Python's sys.path.
# This allows all sub-projects (project/data, project/business, etc.)
# and centralized modules (config, core) to be imported using absolute paths.
# Assuming this file is src/presentation/api_server/flask_app/__init__.py
# Project root is 4 levels up from this file.
jennai_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(jennai_root) not in sys.path:
    sys.path.append(str(jennai_root))


def create_app(container: DependencyContainer):
    # Flask's default static_folder and template_folder are relative to the app's root path.
    # Determine absolute paths for Flask's static and template folders
    # This file is src/presentation/api_server/flask_app/__init__.py
    # So, static folder is at src/presentation/api_server/flask_app/static
    # And template folder is at src/presentation/api_server/flask_app/templates
    flask_app_base_path = Path(__file__).resolve().parent

    app = Flask(
        __name__,
        static_folder=str(flask_app_base_path / 'static'),
        template_folder=str(flask_app_base_path / 'templates')
    )
    app.container = container # Attach container to app instance
    
    # A secret key is required for session management and flashing messages.
    # For production, this should be a secure, randomly generated key loaded from config.
    app.secret_key = 'dev-secret-key-for-flashing'

    # --- Setup Flask-Assets ---
    assets = Environment(app)
    # Define the SCSS bundle
    scss_bundle = Bundle(
        'scss/style.scss',         # Input file
        filters='libsass',         # Use the libsass filter directly
        output='css/style.css'     # Output file
    )
    assets.register('css_all', scss_bundle) # Register the bundle

    # Register blueprints
    app.register_blueprint(default_bp)

    # Add a static URL path for the Allure report
    # This makes files in the project's 'allure-report' directory accessible via /allure_report/ URL
    app.add_url_rule(
        '/allure_report/<path:filename>',
        endpoint='allure_report_static',
        view_func=lambda filename: send_from_directory(str(jennai_root / 'allure-report'), filename)
    )

    return app