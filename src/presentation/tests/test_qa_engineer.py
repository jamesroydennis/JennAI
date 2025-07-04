"""
Test suite for the QA_ENGINEER persona.

This file contains tests that verify the overall testability and quality
assurance infrastructure of the project. It ensures that every component
has a defined quality contract and that the tools for verification are present.
"""
import pytest
from pathlib import Path
import sys

from config import config
import ast
from admin.presentation_utils import get_platform_paths

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


def _is_placeholder_test_file(file_path: Path) -> bool:
    """
    Uses AST to determine if a test file contains only placeholder tests.
    A placeholder test is a function that only contains a 'pass' statement or a docstring.
    """
    if not file_path.exists():
        return False # File doesn't exist, can't be a placeholder

    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    test_functions_found = 0
    implemented_tests_found = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            test_functions_found += 1
            # Check the body of the function. If it has more than one statement,
            # or its single statement is not a 'pass' or a docstring, it's implemented.
            if len(node.body) > 1 or not isinstance(node.body[0], (ast.Pass, ast.Expr)):
                implemented_tests_found += 1

    # If we found test functions but none of them are implemented, it's a placeholder file.
    return test_functions_found > 0 and implemented_tests_found == 0

def test_qa_engineer_verifies_quality_of_implemented_test_contracts():
    """
    OBSERVER-QA_ENGINEER TEST: Verifies that for every *installed* presentation
    platform, its corresponding test contract (test_*_app.py) is not just an
    empty placeholder. It must contain meaningful test implementations.
    """
    platform_paths = get_platform_paths()
    presentation_tests_dir = config.PRESENTATION_DIR / "tests"
    substandard_contracts = []

    for platform_name, platform_path in platform_paths.items():
        if platform_path.exists():
            test_file = presentation_tests_dir / f"test_{platform_name}_app.py"
            if _is_placeholder_test_file(test_file):
                substandard_contracts.append(
                    f"'{test_file.relative_to(config.ROOT)}' for installed platform '{platform_name}' contains only placeholder tests."
                )

    assert not substandard_contracts, \
        "Critique failed: The QA Engineer found test contracts for installed platforms that appear to be unimplemented placeholders:\n" + "\n".join(substandard_contracts)

def test_qa_engineer_verifies_no_empty_test_files_globally():
    """
    OBSERVER-QA_ENGINEER TEST: Scans the entire project for test files
    (test_*.py) and ensures none of them are merely placeholders containing
    only 'pass' statements. This enforces a high standard of quality,
    preventing incomplete tests from being committed.
    """
    # Define the root directories to scan for test files.
    scan_directories = [
        config.SRC_DIR,
        config.ROOT / "tests"
    ]
    placeholder_files = []

    for directory in scan_directories:
        for test_file in directory.rglob("test_*.py"):
            # The abstract contract file is intentionally a placeholder, so it's excluded.
            if test_file.name == "test_presentation_contract.py":
                continue

            if _is_placeholder_test_file(test_file):
                placeholder_files.append(str(test_file.relative_to(config.ROOT)))

    assert not placeholder_files, \
        "Critique failed: The QA Engineer found test files that appear to be unimplemented placeholders:\n" + "\n".join(sorted(placeholder_files))