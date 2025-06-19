# /home/jdennis/Projects/JennAI/tests/presentation/test_flask_routes.py

import pytest
import os

# Ensure the project root is on the path for imports, pytest usually handles this
# when run from the root, but explicit addition can be robust.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.presentation.api_server.flask_app import create_app
from core.dependency_container import DependencyContainer
from main import (
    configure_project_business_dependencies,
    configure_project_data_dependencies
)
from config.config import DEBUG_MODE # To potentially set app.debug

@pytest.fixture(scope="module")
def app_instance():
    """
    Creates a Flask app instance for testing.
    This fixture is module-scoped, meaning the app is set up once per test module.
    """
    # Set a dummy API key for tests if AIGenerator is initialized during app creation
    # and requires it, even if not directly used by the tested routes.
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "DUMMY_API_KEY_FOR_FLASK_TESTS")

    test_container = DependencyContainer()
    configure_project_business_dependencies(test_container)
    configure_project_data_dependencies(test_container)

    flask_app = create_app(container=test_container)
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": DEBUG_MODE, # Use the same debug mode as the app for consistency
        # Add any other test-specific configurations here
        # For example, if you use a database:
        # "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    yield flask_app

@pytest.fixture()
def client(app_instance):
    """A test client for the app."""
    return app_instance.test_client()

def test_home_page_get(client):
    """
    Test that the home page ('/') returns a 200 OK status and expected content.
    """
    response = client.get('/')
    assert response.status_code == 200
    # Check for content from your index.html
    # The title "JennAI Home" is passed from default_routes.py
    assert b"<h1>JennAI Home</h1>" in response.data
    assert b"Your JennAI Flask application is up and running!" in response.data
    assert b"under_construction.png" in response.data # Check for the image