#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))
from config.loguru_setup import setup_logging, logger # Import logger
from config.config import SRC_DIR

REACT_APP_DIR = SRC_DIR / "presentation" / "react_app"

# Define blueprint variables for the Observer's tests.
DEST_ROOT = REACT_APP_DIR
TEMPLATE_MAP = {} # No files copied by this script directly
DIRECTORIES_TO_CREATE = [] # Directory creation is handled by 'npx create-react-app'.

def main():
    """Orchestrates the scaffolding of the React presentation layer."""
    logger.info("--- React Presentation Layer Scaffolder ---")

    # 1. Check for Node/npm/npx
    try:
        subprocess.run(["npx", "--version"], check=True, capture_output=True, text=True)
        logger.success("npx (Node.js) found.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("npx (Node.js) not found.")
        logger.info("Please install Node.js and npm (preferably using nvm) before proceeding.")
        sys.exit(1)

    # 2. Guide user to run create-react-app if project doesn't exist
    if not REACT_APP_DIR.exists() or not (REACT_APP_DIR / "package.json").exists():
        logger.info(f"React project not found at '{REACT_APP_DIR.relative_to(SRC_DIR.parent)}'.")
        logger.info("You need to scaffold the React project first using create-react-app.")
        logger.warning("\n--- MANUAL STEP REQUIRED ---")
        logger.warning(f"1. Navigate to the parent directory: cd {REACT_APP_DIR.parent}")
        logger.warning(f"2. Run create-react-app: npx create-react-app {REACT_APP_DIR.name}")
        logger.warning("3. Once complete, run this admin task again to inject brand assets.")
        logger.warning("-" * 70)
        sys.exit(0)  # Exit gracefully, as the next step (asset injection) will be done on the next run.

    logger.success(f"React project already exists at '{REACT_APP_DIR.relative_to(SRC_DIR.parent)}'.")
    logger.info("The asset injection step will run next if called from the main console.")

if __name__ == "__main__":
    setup_logging(debug_mode=True) # Setup logging for this script
    main()