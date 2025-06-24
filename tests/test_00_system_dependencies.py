import subprocess
import sys
from pathlib import Path
import pytest

# Determine the project root dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent

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
            f"Stderr/Stdout:\n{process.stderr}"

        # Optionally, check for specific success/warning messages in the output
        assert "CHECKING FOR EXTERNAL DEPENDENCIES" in process.stderr, "Expected header not found in check_dependencies.py output."
        assert "All checked external dependencies were found." in process.stderr or \
               "One or more optional external dependencies are missing." in process.stderr, \
            "Expected success/warning message not found in check_dependencies.py output."

    except FileNotFoundError:
        pytest.fail(f"Failed to find Python interpreter: {sys.executable} or check_dependencies.py script.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred while running check_dependencies.py subprocess: {e}")