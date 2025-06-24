#!/usr/bin/env python
import shutil
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from loguru import logger
from config.loguru_setup import setup_logging

def check_dependency(command: str, purpose: str, install_instructions: str, is_critical: bool = False):
    """Checks for a command in the system's PATH and logs the result."""
    logger.info(f"Checking for '{command}'...")
    path = shutil.which(command)
    if path:
        logger.success(f"  ✅ Found '{command}' at: {path}")
        return True
    else:
        log_func = logger.error if is_critical else logger.warning
        log_func(f"  ⚠️  '{command}' not found in system PATH. {purpose}.")
        log_func(f"     To install, please follow system-specific instructions. e.g., on Windows with Scoop:")
        log_func(f"     {install_instructions}")
        return False

def main():
    """Checks for all required external system dependencies."""
    setup_logging(debug_mode=True)
    logger.info("=" * 70)
    logger.info("==      CHECKING FOR EXTERNAL DEPENDENCIES                    ==")
    logger.info("=" * 70)
    logger.info("These tools are required for full functionality but are not managed by Conda/pip.")

    all_deps_found = True

    # Check for Java (required by Allure)
    if not check_dependency("java", "Required by Allure for report generation", "scoop install openjdk"):
        all_deps_found = False

    # Check for Allure
    if not check_dependency("allure", "Required for viewing test reports", "scoop install allure"):
        all_deps_found = False

    # Check for eza
    if not check_dependency("eza", "Used for the enhanced project tree view", "scoop install eza"):
        all_deps_found = False

    logger.info("-" * 70)
    if all_deps_found:
        logger.success("All checked external dependencies were found.")
        return 0
    else:
        logger.warning("One or more optional external dependencies are missing.")
        logger.warning("The application will run, but some features (like reporting or tree view) may be unavailable.")
        return 0 # Return 0 so it doesn't block the main installation

if __name__ == "__main__":
    sys.exit(main())