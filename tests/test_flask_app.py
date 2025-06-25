import pytest
from flask import Flask

# This import works because conftest.py adds the project root to sys.path
from config import config
from src.presentation.api_server.flask_app.app import create_app


@pytest.fixture(scope="module")
def app():
    """
    Create and configure a new app instance for each test module.
    Using 'module' scope is efficient as the app setup is needed only once.
    """
    # The create_app factory is used to set up the app instance.
    flask_app = create_app()

    # Establish an application context before running the tests.
    with flask_app.app_context():
        yield flask_app


@pytest.fixture(scope="module")
def client(app: Flask):
    """A test client for the app, created once per module."""
    return app.test_client()


def test_homepage_loads_successfully(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid and contains expected content.
    """
    # --- Read the expected content from the source files ---
    mission_content = (config.BRAND_DIR / "mission.txt").read_text(encoding="utf-8").strip()
    # For the vision, we check for a key phrase that should be present after markdown rendering.
    expected_vision_phrase = "seed the next evolutionary leap"

    # --- Make the request and perform assertions ---
    response = client.get('/')
    assert response.status_code == 200, "Homepage should return a 200 OK status."
    # Check that the dynamically loaded content is present in the response
    assert mission_content.encode() in response.data, "Mission statement from mission.txt should be displayed."
    assert expected_vision_phrase.encode() in response.data, "Key phrase from vision.md should be displayed."


def test_404_page_loads_correctly(client):
    """
    GIVEN a Flask application configured for testing
    WHEN a non-existent page is requested (GET)
    THEN check that the response is a 404 and contains expected content.
    """
    response = client.get('/non-existent-page')
    assert response.status_code == 404, "Non-existent page should return a 404 Not Found status."
    assert b"<title>Page Not Found - JennAI</title>" in response.data, "404 page should contain the correct title."


def test_500_page_loads_correctly(client):
    """
    GIVEN a Flask application configured for testing
    WHEN an internal server error occurs (via a dedicated test route)
    THEN check that the response is a 500 and contains expected content.
    """
    response = client.get('/test-500-error') # Request the route designed to trigger a 500
    assert response.status_code == 500, "Internal server error should return a 500 status."
    assert b"<title>Internal Server Error - JennAI</title>" in response.data, "500 page should contain the correct title."