def test_homepage_loads_successfully(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' route is requested (GET)
    THEN check that the response is valid and contains expected content
    """
    response = client.get('/')
    assert response.status_code == 200, "The homepage should return a 200 OK status."
    # Check for content from the index.html template
    assert b"Welcome to JennAI" in response.data, "The welcome message should be present."
    assert b'alt="JennAI Logo"' in response.data, "The logo's alt text should be present."

def test_404_page_loads_correctly(client):
    """
    GIVEN a Flask application configured for testing
    WHEN a non-existent route is requested (GET)
    THEN check that a 404 Not Found response is returned with the correct content
    """
    response = client.get('/this-route-does-not-exist')
    assert response.status_code == 404, "A non-existent page should return a 404 status."
    assert b"404 - Page Not Found" in response.data, "The 404 page title should be present."
    assert b"The page you are looking for does not exist." in response.data, "The 404 page message should be present."

def test_500_page_loads_correctly(app, client):
    """
    GIVEN a Flask application configured for testing
    WHEN a route that raises an exception is requested (GET)
    THEN check that a 500 Internal Server Error response is returned with the correct content
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