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

ANGULAR_APP_DIR = SRC_DIR / "presentation" / "angular_app"

# Define blueprint variables for the Observer's tests.
DEST_ROOT = ANGULAR_APP_DIR
TEMPLATE_MAP = {} # No files copied by this script directly
DIRECTORIES_TO_CREATE = [
    DEST_ROOT / "src" / "assets",
    DEST_ROOT / "src" / "styles",
]

def main():
    """Orchestrates the scaffolding of the Angular presentation layer."""
    logger.info("--- Angular Presentation Layer Scaffolder ---")

    # 1. Check for Angular CLI
    try:
        subprocess.run(["ng", "--version"], check=True, capture_output=True, text=True)
        logger.success("Angular CLI ('ng' command) found.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Angular CLI ('ng' command) not found.")
        logger.info("Please install it globally: npm install -g @angular/cli")
        logger.info("Then try again.")
        sys.exit(1)

    # 2. Guide user to run ng new if project doesn't exist
    if not ANGULAR_APP_DIR.exists() or not (ANGULAR_APP_DIR / "angular.json").exists():
        logger.info(f"Angular project not found at '{ANGULAR_APP_DIR.relative_to(SRC_DIR.parent)}'.")
        logger.info("You need to scaffold the Angular project first using the Angular CLI.")
        logger.warning("\n--- MANUAL STEP REQUIRED ---")
        logger.warning(f"1. Navigate to the parent directory: cd {ANGULAR_APP_DIR.parent}")
        logger.warning(f"2. Run Angular CLI to create the app: ng new {ANGULAR_APP_DIR.name} --directory {ANGULAR_APP_DIR.name} --skip-git")
        logger.warning("   (Choose 'SCSS' for stylesheet format when prompted).")
        logger.warning("3. Once 'ng new' completes, run this admin task again to inject brand assets.")
        logger.warning("-" * 70)
        sys.exit(0)  # Exit gracefully, as the next step (asset injection) will be done on the next run.

    logger.success(f"Angular project already exists at '{ANGULAR_APP_DIR.relative_to(SRC_DIR.parent)}'.")
    logger.info("Directory structure is managed by 'create_directories.py'.")

if __name__ == "__main__":
    setup_logging(debug_mode=True) # Setup logging for this script
    main()