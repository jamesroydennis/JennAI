"""
Utility functions for testing CONSTRUCTOR personas.

This module centralizes the logic for generating test cases from constructor
blueprints to avoid code duplication across multiple constructor test files.
"""
import pytest
import importlib
from pathlib import Path

def generate_constructor_test_cases_for_platform(platform_name: str):
    """
    Dynamically generates test cases for a specific constructor blueprint.

    This function is the single source of truth for parsing a constructor's
    blueprint script (e.g., 'admin/create_presentation_flask.py') and
    generating parameterized test cases from it.

    Args:
        platform_name: The name of the platform (e.g., 'flask', 'angular').

    Returns:
        A list of pytest.param objects for parameterization.
    """
    cases = []
    persona_name = f"CONSTRUCTOR-{platform_name.upper()}"
    try:
        module_name = f"admin.create_presentation_{platform_name}"
        module = importlib.import_module(module_name)
        dest_root = getattr(module, "DEST_ROOT", None)
        template_map = getattr(module, "TEMPLATE_MAP", None)
        directories_to_create = getattr(module, "DIRECTORIES_TO_CREATE", None)

        if dest_root is None or template_map is None or directories_to_create is None:
            raise AttributeError(
                f"Blueprint '{module_name}' is malformed. It must define DEST_ROOT, TEMPLATE_MAP, and DIRECTORIES_TO_CREATE."
            )
    except ImportError:
        pytest.fail(f"Critique failed: The blueprint script for {persona_name} ('{module_name}.py') is missing.")
    except AttributeError as e:
        pytest.fail(f"Critique failed: {e}")

    for dir_path in directories_to_create:
        test_id = f"CONSTRUCTOR-creates-dir-{platform_name}-{dir_path.relative_to(dest_root).as_posix().replace('/', '-')}"
        cases.append(pytest.param(dir_path, "dir", id=test_id))
    for template_rel, dest_rel in template_map.items():
        dest_path = dest_root / dest_rel
        test_id = f"CONSTRUCTOR-creates-file-{platform_name}-{dest_rel.replace('/', '-')}"
        cases.append(pytest.param(dest_path, "file", id=test_id))
    return cases