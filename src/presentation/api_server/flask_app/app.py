import sys
from pathlib import Path

# --- Root Project Path Setup ---
# This ensures that the application can be run directly and that it can find
# the necessary project modules (like config).
FLASK_APP_DIR = Path(__file__).resolve().parent
API_SERVER_DIR = FLASK_APP_DIR.parent
PROJECT_ROOT = API_SERVER_DIR.parent.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask
from config.config import DEBUG_MODE

# Import the blueprints for the routes
from src.presentation.api_server.flask_app.routes.main_routes import main_bp
from src.presentation.api_server.flask_app.routes.brand_routes import brand_bp

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(brand_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG_MODE, port=5000)