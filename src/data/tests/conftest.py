import pytest
from pathlib import Path

from config import config

@pytest.fixture(scope="function")
def test_db():
    """
    A fixture that provides a clean, temporary SQLite database for data layer tests.
    It ensures the database file is deleted before and after each test function,
    guaranteeing test isolation.
    Scope is 'function' to give each test a fresh database.
    """
    db_path = config.TEST_DB_PATH
    # Ensure the test database does not exist from a previous failed run
    if db_path.exists():
        db_path.unlink()

    yield db_path  # Provide the path to the test function

    # Teardown: clean up the database file after the test completes
    if db_path.exists():
        db_path.unlink()