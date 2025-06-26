import sys
import os
import platform
from pathlib import Path

# --- Root Project Path Setup ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables first, then config
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env")

from config import config
from config.loguru_setup import setup_logging, logger

def generate_environment_file():
    """
    Creates an environment.properties file in the Allure results directory
    to add environment details to the test report.
    """
    allure_dir = config.ALLURE_RESULTS_DIR
    if not allure_dir.exists():
        logger.warning(f"Allure results directory not found at {allure_dir}. Skipping environment file generation.")
        return

    env_file_path = allure_dir / "environment.properties"

    environment_data = {
        "App.Name": config.APP_NAME,
        "App.Version": config.VERSION,
        "Debug.Mode": config.DEBUG_MODE,
        "Python.Version": platform.python_version(),
        "Platform": f"{platform.system()} {platform.release()}",
        "Conda.Environment": os.getenv("CONDA_DEFAULT_ENV", "Not set"),
    }

    with open(env_file_path, "w") as f:
        for key, value in environment_data.items():
            f.write(f"{key}={value}\n")
    logger.success(f"Allure environment file created at: {env_file_path}")

if __name__ == "__main__":
    setup_logging(debug_mode=config.DEBUG_MODE)
    generate_environment_file()