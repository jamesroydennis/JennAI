import subprocess
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from loguru import logger
from config.loguru_setup import setup_logging
from admin.create_directories import main as create_directories_main

# Setup logging for this script
setup_logging(debug_mode=True) # Assuming verbose output for installation script
logger.info("Loguru setup complete for install_requirements.py.")




def run_command(command, description):
    """
    Runs a command in the shell, streams its output, and checks for errors.

    Args:
        command (list): The command and its arguments to execute.
        description (str): A description of the action being performed for logging.

    Returns:
        bool: True if the command was successful, False otherwise.
    """
    logger.info(f"Starting: {description}...")
    logger.info(f"Executing command: {' '.join(command)}")
    try:
        # We don't capture stdout/stderr so that the user can see the
        # real-time output from conda and pip.
        process = subprocess.run(command, check=True, text=True)
        logger.success(f"SUCCESS: {description} completed.")
        return True
    except FileNotFoundError:
        logger.error(f"ERROR: Command not found. Is 'conda' in your system's PATH?")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR: {description} failed with exit code {e.returncode}.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False


def main():
    """
    Main function to orchestrate the environment setup and installation process.
    """
    logger.info("\n" + "=" * 70)
    logger.info("==      JENN-AI ENVIRONMENT & PYTORCH INSTALLATION SCRIPT       ==")
    logger.info("=" * 70 + "\n")

    # --- Step 1: Check for external system dependencies ---
    check_deps_script = jennai_root_for_path / "admin" / "check_dependencies.py"
    check_deps_command = [sys.executable, str(check_deps_script)] # Renamed script
    if not run_command(check_deps_command, "Check for external system dependencies (e.g., Allure, Java)"):
        # This check is currently non-blocking, but we could add an abort here if needed.
        logger.warning("Dependency check finished with warnings. Continuing installation...")

    logger.info("-" * 70)

    # --- Define paths and commands ---
    project_root = jennai_root_for_path
    env_file = project_root / "environment.yaml"
    pytorch_installer = project_root / "admin" / "install_pytorch.py"
    env_name = "jennai-root"

    # --- Step 2: Create Project Folders ---
    if not create_directories_main():
        logger.error("Aborting due to failure in project folder creation.")
        sys.exit(1)

    logger.info("-" * 70)

    # --- Step 3: Create Conda Environment ---
    if not env_file.exists():
        logger.error(f"environment.yaml not found at {env_file}")
        sys.exit(1)

    create_env_command = ["conda", "env", "create", "-f", str(env_file)]
    if not run_command(create_env_command, "Create Conda environment from environment.yaml"):
        logger.error("Aborting due to failure in environment creation.")
        sys.exit(1)

    logger.info("-" * 70)

    # --- Step 4: Install PyTorch using the dedicated script ---
    # We use 'conda run' to execute the command within the new environment.
    # This is the correct way to run a command without needing to 'activate' it
    # in a way that persists outside the script.
    if not pytorch_installer.exists():
        logger.error(f"PyTorch installer not found at {pytorch_installer}")
        sys.exit(1)

    install_pytorch_command = [
        "conda", "run", "-n", env_name,
        "python", str(pytorch_installer)
    ]
    if not run_command(install_pytorch_command, "Install PyTorch with CUDA support"):
        logger.error("Aborting due to failure in PyTorch installation.")
        sys.exit(1)

    logger.info("\n" + "=" * 70)
    logger.info("== ✅ INSTALLATION COMPLETE                                     ==")
    logger.info("=" * 70)
    logger.success("All steps completed successfully.")
    logger.info(f"To activate your new environment, run: conda activate {env_name}")
    logger.info("-" * 70)


if __name__ == "__main__":
    main()