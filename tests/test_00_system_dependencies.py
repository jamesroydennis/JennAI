import subprocess
import sys
from pathlib import Path
import pytest
import importlib

REQUIRED_PACKAGES = [
    "torch",
    "torchvision",
    "torchaudio",
    "torchtext",
    "torchdata",
    "pydantic",
    "google.generativeai",
    "loguru",
    "pytest",
    "pytest_loguru",
    "numexpr",
    "allure_pytest",
    "cv2",
    "rich",
]
CLI_TOOLS = [
    "ruff",
]

# Determine the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent
def test_required_packages_installed():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    assert not missing, f"Missing required packages: {missing}"
    
@pytest.mark.system_check
def test_system_dependencies_check_runs_successfully():
    """
    Tests that the admin/check_dependencies.py script runs without Python errors
    and indicates a successful check (even if some optional dependencies are missing).
    """
    check_deps_script_path = PROJECT_ROOT / "admin" / "check_dependencies.py"
    assert check_deps_script_path.exists(), "admin/check_dependencies.py not found."

    try:
        # Run check_dependencies.py as a subprocess
        process = subprocess.run(
            [sys.executable, str(check_deps_script_path)],
            capture_output=True,
            text=True,
            check=False, # We'll check the returncode manually
            cwd=PROJECT_ROOT,
            env=None # No special environment variables needed for this script
        )

        # Assert that the script exited successfully (return code 0)
        assert process.returncode == 0, \
            f"check_dependencies.py exited with code {process.returncode}.\n" \
            f"Stdout:\n{process.stdout}\nStderr:\n{process.stderr}"

        # Loguru outputs to stderr by default, so we check the combined output to be robust.
        full_output = process.stdout + process.stderr
        assert "=== System Dependency Checks ===" in full_output, "Expected 'System Dependency Checks' header not found in output."
        assert "=== Python Package Checks ===" in full_output, "Expected 'Python Package Checks' header not found in output."

    except FileNotFoundError:
        pytest.fail(f"Failed to find Python interpreter: {sys.executable} or check_dependencies.py script.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred while running check_dependencies.py subprocess: {e}")