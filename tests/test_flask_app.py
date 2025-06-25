import pytest
from flask import Flask

# This import works because conftest.py adds the project root to sys.path
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
    response = client.get('/')
    assert response.status_code == 200, "Homepage should return a 200 OK status."
    assert b"Illuminating the Intelligent Frontier" in response.data, "Homepage should contain the main vision title."
    assert b"Our Core Mission" in response.data, "Homepage should contain the mission section."


def test_404_page_loads_correctly(client):
    """
    GIVEN a Flask application configured for testing
    WHEN a non-existent page is requested (GET)
    THEN check that the response is a 404 and contains expected content.
    """
    response = client.get('/non-existent-page')
    assert response.status_code == 404, "Non-existent page should return a 404 Not Found status."
    assert b"404 - Page Not Found" in response.data, "404 page should contain '404 - Page Not Found' text."


def test_500_page_loads_correctly(app, client):
    """
    GIVEN a Flask application configured for testing
    WHEN an internal server error occurs
    THEN check that the response is a 500 and contains expected content.
    """
    # Temporarily add a route that raises an exception to trigger a 500 error
    @app.route('/trigger-500')
    def trigger_500():
        raise Exception("Simulated internal server error")

    response = client.get('/trigger-500')
    assert response.status_code == 500, "Internal server error should return a 500 status."
    assert b"500 - Internal Server Error" in response.data, "500 page should contain '500 - Internal Server Error' text."