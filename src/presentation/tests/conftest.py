import pytest
from src.presentation.api_server.flask_app import create_app
from core.dependency_container import DependencyContainer

@pytest.fixture(scope="function")
def app():
    """
    Creates a new Flask app instance for each test function.
    Using 'function' scope is crucial for test isolation, preventing state
    from one test (like a handled request) from affecting another.
    """
    container = DependencyContainer()
    app = create_app(container)
    app.config.update({
        "TESTING": True,
        # Setting SERVER_NAME is a good practice for testing url_for and other context-dependent features.
        "SERVER_NAME": "localhost.test"
    })
    yield app

@pytest.fixture(scope="function")
def client(app):
    """A test client for the app, created once for each test function."""
    return app.test_client()