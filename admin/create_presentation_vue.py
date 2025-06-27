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

VUE_APP_DIR = SRC_DIR / "presentation" / "vue_app"

# Define blueprint variables for the Observer's tests.
DEST_ROOT = VUE_APP_DIR
TEMPLATE_MAP = {} # No files copied by this script directly
DIRECTORIES_TO_CREATE = [] # Directory creation is now handled by the central create_directories.py

def main():
    """Orchestrates the scaffolding of the Vue presentation layer."""
    logger.info("--- Vue Presentation Layer Scaffolder ---")

    # 1. Check for Node/npm/npx
    try:
        subprocess.run(["npx", "--version"], check=True, capture_output=True, text=True)
        logger.success("npx (Node.js) found.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("npx (Node.js) not found.")
        logger.info("Please install Node.js and npm (preferably using nvm) before proceeding.")
        sys.exit(1)

    # 2. Guide user to run `npm create vue` if project doesn't exist
    if not VUE_APP_DIR.exists() or not (VUE_APP_DIR / "package.json").exists():
        logger.info(f"Vue project not found at '{VUE_APP_DIR.relative_to(SRC_DIR.parent)}'.")
        logger.info("You need to scaffold the Vue project first using the Vue CLI.")
        logger.warning("\n--- MANUAL STEP REQUIRED ---")
        logger.warning(f"1. Navigate to the parent directory: cd {VUE_APP_DIR.parent}")
        logger.warning(f"2. Run the Vue create command: npm create vue@latest {VUE_APP_DIR.name}")
        logger.warning("   (Follow the prompts. Choose options like SCSS, Pinia, etc. as needed).")
        logger.warning("3. Once complete, run this admin task again to inject brand assets.")
        logger.warning("-" * 70)
        sys.exit(0)  # Exit gracefully, as the next step (asset injection) will be done on the next run.

    logger.success(f"Vue project already exists at '{VUE_APP_DIR.relative_to(SRC_DIR.parent)}'.")
    logger.info("Directory structure is managed by 'create_directories.py'.")

if __name__ == "__main__":
    setup_logging(debug_mode=True) # Setup logging for this script
    main()