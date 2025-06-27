import pytest
from config import config
import markdown

@pytest.mark.parametrize(
    "asset_url, expected_content_type, content_check",
    [
        # Test case for the favicon, checking its magic number
        (
            "/favicon.ico",  # Corrected URL: Favicon is served from the root
            "image/x-icon",  # Corrected Content-Type to match common server behavior
            lambda data: data.startswith(b"\x00\x00\x01\x00"),
        ),
        # Test case for the PNG logo, checking its magic number
        (
            "/brand/logo.png",
            "image/png",
            lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
        ),
    ],
    ids=["favicon-ico", "logo-png"] # Descriptive IDs for test runs
)
def test_must_serve_core_brand_assets(client, asset_url, expected_content_type, content_check):
    """
    A concrete implementation of the presentation contract.
    Verifies that essential brand assets (logo, favicon) are served correctly.
    """
    response = client.get(asset_url)
    assert response.status_code == 200, f"Asset at {asset_url} should return a 200 OK status."
    assert response.content_type == expected_content_type, f"Asset at {asset_url} should have content type {expected_content_type}."
    assert content_check(response.data), f"Content check failed for asset at {asset_url}."


def test_must_register_brand_routes(app):
    """
    A concrete implementation of the presentation contract.
    Verifies that the 'brand' blueprint is registered and its routes are accessible.
    """
    # Check if the blueprint itself is registered
    assert 'brand' in app.blueprints, "The 'brand' blueprint should be registered."

    # Check if key routes from the blueprint are part of the app's URL map
    # The correct way to check for rules is to iterate through them.
    rules = [r.rule for r in app.url_map.iter_rules()]
    assert '/brand/logo.png' in rules, "Route for /brand/logo.png should exist under the brand blueprint."
    assert '/favicon.ico' in rules, "Route for /favicon.ico should exist at the app root."

def test_must_be_a_recognized_web_app():
    """
    A concrete implementation of the presentation contract.
    Verifies that 'flask' is a recognized web application type.
    """
    assert 'flask' in config.WEB_APP_NAMES, "The 'flask' key must be in the WEB_APP_NAMES whitelist."

# --- Presentation Contract Tests ---

def test_must_have_a_main_entry_point(client):
    """
    A concrete implementation of the presentation contract.
    Verifies that the main entry point (homepage) loads successfully.
    """
    response = client.get('/')
    assert response.status_code == 200, "The homepage should return a 200 OK status."
    # Check for content from the index.html template
    assert b"Welcome to JennAI" in response.data, "The welcome message should be present."
    assert b'alt="JennAI Logo"' in response.data, "The logo's alt text should be present."

def test_must_display_vision_statement(client):
    """
    A concrete implementation of the presentation contract.
    Verifies that the main entry point correctly displays the vision statement.
    """
    vision_path = config.BRAND_DIR / "vision.md"
    assert vision_path.exists(), f"The vision file must exist at {vision_path}"

    # Read the raw markdown and convert it to HTML to check against the response
    raw_md = vision_path.read_text(encoding="utf-8")
    expected_html = markdown.markdown(raw_md)

    response = client.get('/')
    assert response.status_code == 200
    assert bytes(expected_html, 'utf-8') in response.data, "The rendered vision statement HTML should be on the homepage."

def test_must_display_mission_statement(client):
    """
    A concrete implementation of the presentation contract.
    Verifies that the main entry point correctly displays the mission statement.
    """
    mission_path = config.BRAND_DIR / "mission.txt"
    assert mission_path.exists(), f"The mission file must exist at {mission_path}"

    expected_text = mission_path.read_text(encoding="utf-8")

    response = client.get('/')
    assert response.status_code == 200
    assert bytes(expected_text, 'utf-8') in response.data, "The mission statement text should be on the homepage."

def test_must_handle_not_found_error_gracefully(client):
    """
    A concrete implementation of the presentation contract.
    Verifies that accessing a non-existent resource returns a 404 Not Found.
    """
    response = client.get('/this-route-does-not-exist')
    assert response.status_code == 404, "A non-existent page should return a 404 status."
    assert b"404 - Page Not Found" in response.data, "The 404 page title should be present."
    assert b"The page you are looking for does not exist." in response.data, "The 404 page message should be present."

def test_must_handle_internal_server_error_gracefully(app, client):
    """
    A concrete implementation of the presentation contract.
    Verifies that an internal server error returns a 500 Internal Server Error.
    """
    # To test a 500 error, we need a route that reliably fails.
    # We can add one to the app just for this test.
    @app.route('/test-500-error')
    def error_route():
        raise Exception("This is a simulated internal server error for testing.")

    # By default, Flask's test client propagates exceptions when TESTING is True.
    # We must temporarily disable this to test the rendered 500 page.
    app.config['TESTING'] = False

    # Now, request the route that we know will cause an error.
    response = client.get('/test-500-error')

    # It's good practice to restore the config after the test, although the
    # function-scoped fixture will handle this for the next test anyway.
    app.config['TESTING'] = True

    assert response.status_code == 500, "A route with an exception should return a 500 status."
    assert b"500 - Internal Server Error" in response.data, "The 500 page title should be present."
    assert b"Something went wrong on our end." in response.data, "The 500 page message should be present."