"""
Shared utility functions for tests within the 'presentation' layer.

This module provides common helpers to avoid code duplication across different
persona test files (e.g., test_architect.py, test_contractor.py).
"""
import importlib.util
from pathlib import Path
import pytest

def load_attribute_from_script(script_path: Path, attribute_name: str):
    """
    Dynamically loads a specific attribute (e.g., a dictionary, a class)
    from a Python script, especially useful for scripts with non-standard names
    that cannot be imported directly (e.g., '42_present.py').

    Args:
        script_path: The absolute path to the Python script.
        attribute_name: The string name of the attribute to load from the script.

    Returns:
        The loaded attribute from the script.

    Raises:
        pytest.fail: If the script or attribute cannot be found.
    """
    if not script_path.exists():
        pytest.fail(f"Required script for testing not found: {script_path}")

    module_name = f"dynamic_module_{script_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    dynamic_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dynamic_module)
    if not hasattr(dynamic_module, attribute_name):
        pytest.fail(f"Attribute '{attribute_name}' not found in script {script_path}")
    return getattr(dynamic_module, attribute_name)