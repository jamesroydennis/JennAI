import subprocess
import sys
import logging
from pathlib import Path

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)-7s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)


def run_command(command, description):
    """
    Runs a command in the shell, streams its output, and checks for errors.

    Args:
        command (list): The command and its arguments to execute.
        description (str): A description of the action being performed for logging.

    Returns:
        bool: True if the command was successful, False otherwise.
    """
    logging.info(f"Starting: {description}...")
    logging.info(f"Executing command: {' '.join(command)}")
    try:
        # We don't capture stdout/stderr so that the user can see the
        # real-time output from conda and pip.
        process = subprocess.run(command, check=True, text=True)
        logging.info(f"SUCCESS: {description} completed.")
        return True
    except FileNotFoundError:
        logging.error(f"ERROR: Command not found. Is 'conda' in your system's PATH?")
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"ERROR: {description} failed with exit code {e.returncode}.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False


def main():
    """
    Main function to orchestrate the environment setup and installation process.
    """
    print("\n" + "=" * 70)
    print("==      JENN-AI ENVIRONMENT & PYTORCH INSTALLATION SCRIPT       ==")
    print("=" * 70 + "\n")

    # --- Define paths and commands ---
    project_root = Path(__file__).resolve().parent.parent
    env_file = project_root / "environment.yaml"
    pytorch_installer = project_root / "admin" / "install_pytorch.py"
    env_name = "jennai-root"

    # --- Step 1: Create Conda Environment ---
    if not env_file.exists():
        logging.error(f"environment.yaml not found at {env_file}")
        sys.exit(1)

    create_env_command = ["conda", "env", "create", "-f", str(env_file)]
    if not run_command(create_env_command, "Create Conda environment from environment.yaml"):
        logging.error("Aborting due to failure in environment creation.")
        sys.exit(1)

    print("-" * 70)

    # --- Step 2: Install PyTorch using the dedicated script ---
    # We use 'conda run' to execute the command within the new environment.
    # This is the correct way to run a command without needing to 'activate' it
    # in a way that persists outside the script.
    if not pytorch_installer.exists():
        logging.error(f"PyTorch installer not found at {pytorch_installer}")
        sys.exit(1)

    install_pytorch_command = [
        "conda", "run", "-n", env_name,
        "python", str(pytorch_installer)
    ]
    if not run_command(install_pytorch_command, "Install PyTorch with CUDA support"):
        logging.error("Aborting due to failure in PyTorch installation.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("== ✅ INSTALLATION COMPLETE                                     ==")
    print("=" * 70)
    logging.info("All steps completed successfully.")
    logging.info(f"To activate your new environment, run: conda activate {env_name}")
    print("-" * 70)


if __name__ == "__main__":
    main()