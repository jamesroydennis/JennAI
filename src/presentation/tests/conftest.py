import pytest
import re
from pathlib import Path
import sys
from src.presentation.api_server.flask_app import create_app
from core.dependency_container import DependencyContainer
from config import config

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from admin.presentation_utils import get_platform_paths
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


def pytest_collection_modifyitems(config, items):
    """
    QA_ENGINEER HOOK: Dynamically skips tests for presentation platforms that
    have not been constructed.

    This hook embodies the QA Engineer's responsibility to ensure the test suite
    adapts to the current state of the project. It inspects each collected test,
    and if a test belongs to a specific platform (e.g., 'test_angular_app.py'),
    it verifies that the corresponding application directory exists. If not, it
    marks all tests in that file to be skipped.
    """
    platform_paths = get_platform_paths()

    for item in items:
        # Check for concrete app tests (e.g., test_angular_app.py)
        match = re.search(r"test_(\w+)_app\.py", str(item.fspath))
        if match:
            platform_name = match.group(1)
            if platform_name == "flask":
                continue

            platform_dir = platform_paths.get(platform_name)
            if not platform_dir or not platform_dir.exists():
                reason = f"QA Engineer determined '{platform_name}' is not installed. Skipping tests."
                item.add_marker(pytest.mark.skip(reason=reason))