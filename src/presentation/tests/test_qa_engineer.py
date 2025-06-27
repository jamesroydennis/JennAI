"""
Test suite for the QA_ENGINEER persona.

This file contains tests that verify the overall testability and quality
assurance infrastructure of the project. It ensures that every component
has a defined quality contract and that the tools for verification are present.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import config

def test_qa_engineer_verifies_testing_infrastructure():
    """
    OBSERVER-QA_ENGINEER TEST: Verifies that the fundamental testing
    infrastructure, like pytest.ini, is present and configured.
    """
    pytest_ini_path = config.ROOT / "pytest.ini"
    assert pytest_ini_path.exists(), \
        "Critique failed: The QA Engineer found that the core testing configuration file 'pytest.ini' is missing."
    assert pytest_ini_path.stat().st_size > 0, \
        "Critique failed: The QA Engineer found that 'pytest.ini' is empty, indicating a misconfiguration."

def test_qa_engineer_ensures_all_platforms_are_testable():
    """
    OBSERVER-QA_ENGINEER TEST: Verifies that for every presentation platform
    defined by the ARCHITECT, a corresponding test file exists. This ensures
    that a quality contract is defined for every application.
    """
    presentation_tests_dir = config.PRESENTATION_DIR / "tests"
    missing_test_files = []

    for platform_name in config.PRESENTATION_APPS.keys():
        # This enforces the convention that an app's quality contract is in its test file.
        expected_test_file = presentation_tests_dir / f"test_{platform_name}_app.py"
        if not expected_test_file.exists():
            missing_test_files.append(str(expected_test_file.relative_to(config.ROOT)))

    assert not missing_test_files, \
        "Critique failed: The QA Engineer found platforms defined by the Architect that lack a quality contract (test file):\n" + "\n".join(missing_test_files)