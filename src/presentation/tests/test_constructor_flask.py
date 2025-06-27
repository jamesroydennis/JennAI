"""
Test suite for the CONSTRUCTOR-FLASK persona.

This file verifies that the Flask application is scaffolded correctly according to
its specific blueprint.
"""
import pytest
from pathlib import Path
import sys
import importlib

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import config

def generate_flask_constructor_test_cases():
    """Dynamically generates test cases for the Flask constructor blueprint."""
    cases = []
    platform_name = "flask"
    try:
        module_name = f"admin.create_presentation_{platform_name}"
        module = importlib.import_module(module_name)
        dest_root = getattr(module, "DEST_ROOT", None)
        template_map = getattr(module, "TEMPLATE_MAP", {})
        directories_to_create = getattr(module, "DIRECTORIES_TO_CREATE", [])
        if not dest_root: return []
    except ImportError:
        return [] # If constructor script doesn't exist, no tests are generated.

    for dir_path in directories_to_create:
        test_id = f"CONSTRUCTOR-creates-dir-{platform_name}-{dir_path.relative_to(dest_root).as_posix().replace('/', '-')}"
        cases.append(pytest.param(dir_path, "dir", id=test_id))
    for template_rel, dest_rel in template_map.items():
        dest_path = dest_root / dest_rel
        test_id = f"CONSTRUCTOR-creates-file-{platform_name}-{dest_rel.replace('/', '-')}"
        cases.append(pytest.param(dest_path, "file", id=test_id))
    return cases

@pytest.mark.parametrize("expected_artifact_path, artifact_type", generate_flask_constructor_test_cases())
def test_constructor_flask_creates_required_artifacts(expected_artifact_path, artifact_type):
    """OBSERVER TEST: Verifies CONSTRUCTOR-FLASK creates a specific artifact correctly."""
    assert expected_artifact_path.exists(), f"Critique failed: Constructor for Flask did not create '{expected_artifact_path}'."
    if artifact_type == "dir":
        assert expected_artifact_path.is_dir(), f"Critique failed: Expected a directory, but found a file at '{expected_artifact_path}'."
    elif artifact_type == "file":
        assert expected_artifact_path.is_file(), f"Critique failed: Expected a file, but found a directory at '{expected_artifact_path}'."
        assert expected_artifact_path.stat().st_size > 0, f"Critique failed: Constructor created an empty file at '{expected_artifact_path}'."