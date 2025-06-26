import os
import sys
from pathlib import Path

# --- Path Setup ---
# This ensures that the application can be run directly from the command line
# and that it can find the root project modules (like 'config' and 'core').
FLASK_APP_DIR = Path(__file__).resolve().parent
API_SERVER_DIR = FLASK_APP_DIR.parent
PRESENTATION_DIR = API_SERVER_DIR.parent
SRC_DIR = PRESENTATION_DIR.parent
ROOT = SRC_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.presentation.api_server.flask_app import create_app
from core.dependency_container import DependencyContainer
from config import config

# This block allows the Flask app to be run directly for development.
if __name__ == '__main__':
    # A dummy container is sufficient for now, as dependencies are not yet injected.
    container = DependencyContainer()
    app = create_app(container=container)
    # The host '0.0.0.0' makes the server accessible from your local network.
    app.run(debug=config.DEBUG_MODE, host='0.0.0.0', port=5000)
