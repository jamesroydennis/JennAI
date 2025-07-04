"""
Test suite for the CONSTRUCTOR-FLASK persona.

This file verifies that the Flask application is scaffolded correctly according to
its specific blueprint.
"""
import pytest
from pathlib import Path

# Import the centralized test case generator
from src.presentation.tests.constructor_test_utils import generate_constructor_test_cases_for_platform

@pytest.mark.parametrize("expected_artifact_path, artifact_type", generate_constructor_test_cases_for_platform("flask"))
def test_constructor_flask_creates_required_artifacts(expected_artifact_path, artifact_type):
    """OBSERVER TEST: Verifies CONSTRUCTOR-FLASK creates a specific artifact correctly."""
    assert expected_artifact_path.exists(), f"Critique failed: Constructor for Flask did not create '{expected_artifact_path}'."
    if artifact_type == "dir":
        assert expected_artifact_path.is_dir(), f"Critique failed: Expected a directory, but found a file at '{expected_artifact_path}'."
    elif artifact_type == "file":
        assert expected_artifact_path.is_file(), f"Critique failed: Expected a file, but found a directory at '{expected_artifact_path}'."
        assert expected_artifact_path.stat().st_size > 0, f"Critique failed: Constructor created an empty file at '{expected_artifact_path}'."