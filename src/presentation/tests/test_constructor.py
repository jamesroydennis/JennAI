"""
Test suite for the CONSTRUCTOR persona.

This file contains tests that verify the structural integrity of a scaffolded
application. It ensures that the CONSTRUCTOR correctly builds the application
framework from the ARCHITECT's blueprints.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import importlib
from config import config

# --- Test Data Generation ---
def generate_constructor_test_cases():
    """Dynamically generates test cases for all defined CONSTRUCTOR blueprints."""
    cases = []
    # The Observer dynamically imports blueprints from the CONSTRUCTOR scripts,
    # iterating over the keys of the PRESENTATION_APPS dictionary.
    for platform_name in config.PRESENTATION_APPS.keys():
        try:
            # Dynamically import the constructor script for the platform
            module_name = f"admin.create_presentation_{platform_name}"
            module = importlib.import_module(module_name)

            # Get the blueprint variables from the module
            dest_root = getattr(module, "DEST_ROOT", None)
            template_map = getattr(module, "TEMPLATE_MAP", {})
            directories_to_create = getattr(module, "DIRECTORIES_TO_CREATE", [])

            if not dest_root: continue

        except ImportError:
            continue # Skip platforms that don't have a constructor script yet.

        # The OBSERVER generates tests for ALL blueprints, not just for
        # applications that have already been constructed. This is the core of TDD.
        # Add checks for explicitly created directories
        for dir_path in directories_to_create:
            test_id = f"CONSTRUCTOR-DIR-{platform_name}-{dir_path.relative_to(dest_root).as_posix().replace('/', '-')}"
            cases.append(pytest.param(dir_path, id=test_id))
        # Add checks for copied files
        for template_rel, dest_rel in template_map.items():
            dest_path = dest_root / dest_rel
            test_id = f"CONSTRUCTOR-{platform_name}-{dest_rel.replace('/', '-')}"
            cases.append(pytest.param(dest_path, id=test_id))
    return cases

@pytest.mark.parametrize("expected_artifact_path", generate_constructor_test_cases())
def test_constructor_creates_required_artifacts(expected_artifact_path):
    """
    OBSERVER TEST: Verifies that the CONSTRUCTOR has created a specific file or directory
    as defined in the architectural blueprint.
    """
    assert expected_artifact_path.exists(), \
        f"Critique failed: Constructor did not create expected artifact at '{expected_artifact_path}'."