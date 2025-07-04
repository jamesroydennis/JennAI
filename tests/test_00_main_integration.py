import subprocess
import sys
from pathlib import Path
import os
import pytest
from config.loguru_setup import logger 


@pytest.mark.integration
def test_main_py_initializes_successfully(app_config):
    """
    Tests if main.py runs its initialization sequence without errors
    and logs expected success messages.
    """
    # Use the canonical ROOT path from the config fixture for consistency
    main_script_path = app_config.ROOT / "main.py"
    assert main_script_path.exists(), "main.py not found at the expected location."

    # Prepare environment variables for the subprocess
    # Provide a dummy API key to prevent AIGenerator from failing if the key is required at startup.
    env = os.environ.copy()
    env["GOOGLE_API_KEY"] = "DUMMY_API_KEY_FOR_TESTING"
    env["PYTEST_RUNNING_MAIN"] = "1"  # Prevent main.py from starting the blocking Flask server
    # Explicitly set DEBUG_MODE for the subprocess to ensure it logs at the correct level.
    # This is necessary because the test asserts for "Level: DEBUG" in the log output.
    env["DEBUG_MODE"] = "True"

    try:
        # Run main.py as a subprocess
        # sys.executable ensures we use the same Python interpreter as pytest
        process = subprocess.run(
            [sys.executable, str(main_script_path)],
            capture_output=True,
            text=True,
            check=False,  # We'll check the returncode manually
            cwd=app_config.ROOT, # Run from the project root
            env=env
        )

        # Assert that main.py exited successfully
        assert process.returncode == 0, f"main.py exited with code {process.returncode}.\nStderr:\n{process.stderr}\nStdout:\n{process.stdout}"

        # Check for key success messages in stderr (where Loguru console output goes)
        # These assertions confirm that the main orchestration script ran through its key stages.
        # We also check that DEBUG_MODE was correctly passed to and logged by the subprocess.
        assert "INFO - Running in DEBUG_MODE: True" in process.stderr
        assert "SUCCESS - src/business dependencies configured (conceptual)." in process.stderr
        assert "SUCCESS - src/data dependencies configured (conceptual)." in process.stderr
        assert "SUCCESS - src/presentation dependencies configured (conceptual)." in process.stderr
        assert "SUCCESS - JennAI OS has successfully booted and performed initial checks." in process.stderr

    except FileNotFoundError:
        pytest.fail(f"Failed to find Python interpreter: {sys.executable} or main.py script.")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred while running main.py subprocess: {e}")