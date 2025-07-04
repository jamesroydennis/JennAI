#!/usr/bin/env python
import sys
import importlib
import shutil

from pathlib import Path

# --- Project Root Path Setup ---
# This allows the script to import modules from the project (e.g., config)
# when run from any directory.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import config
from config.loguru_setup import setup_logging, logger

INSTALL_INSTRUCTIONS = {
    "node": "Install using Node Version Manager (nvm). See environment.yaml for details.",
    "npm": "Install using Node Version Manager (nvm). See environment.yaml for details.",
    "sass": "Install globally via npm: npm install -g sass",
    "allure": "Install using Scoop, Chocolatey, or Homebrew. See environment.yaml for details.",
    "java": "Install OpenJDK. It is required by Allure. See environment.yaml for details.",
    "eza": "Optional. Install using Scoop, Chocolatey, or Homebrew for a better tree view."
}

def check_command(cmd: str, name: str, is_critical: bool = True) -> bool:
    """Checks for a command's existence and returns True if found, False otherwise."""
    path = shutil.which(cmd)
    if path:
        logger.success(f"{name}: Found ({path})")
        return True
    else:
        if is_critical:
            logger.error(f"{name}: NOT FOUND")
            if cmd in INSTALL_INSTRUCTIONS:
                logger.warning(f"  ↪ How to fix: {INSTALL_INSTRUCTIONS[cmd]}")
            return False
        else:
            logger.info(f"{name}: Not found (optional)")
            return True # Not a failure for optional tools

def check_python_package(pkg: str) -> bool:
    """Checks if a Python package can be imported."""
    try:
        importlib.import_module(pkg)
        logger.success(f"Python package '{pkg}': Installed")
        return True
    except ImportError:
        logger.error(f"Python package '{pkg}': NOT INSTALLED")
        return False

def main():
    success = True
    logger.info("=== System Dependency Checks ===")
    if not check_command("node", "Node.js"): success = False
    if not check_command("npm", "npm"): success = False
    if not check_command("allure", "Allure CLI"): success = False
    if not check_command("java", "Java"): success = False
    # Optional tools don't affect the success status
    check_command("nvm", "nvm", is_critical=False)
    check_command("sass", "Sass CLI", is_critical=False)
    check_command("eza", "eza (for tree view)", is_critical=False)

    logger.info("\n=== Python Package Checks ===")
    for pkg in config.PYTHON_PACKAGES:
        if not check_python_package(pkg):
            success = False

    return 0 if success else 1

if __name__ == "__main__":
    setup_logging(debug_mode=True)
    exit_code = main()
    if exit_code == 0:
        logger.success("\nAll critical dependencies are met.")
    else:
        logger.error("\nCritical dependencies are missing. Please review the checklist.")
    sys.exit(exit_code)