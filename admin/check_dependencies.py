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

def check_command(cmd: str, name: str, is_critical: bool = True) -> bool:
    """Checks for a command's existence and returns True if found, False otherwise."""
    path = shutil.which(cmd)
    if path:
        print(f"{name}: ✅ ({path})")
        return True
    else:
        print(f"{name}: ❌ NOT FOUND")
        return False

def check_python_package(pkg: str) -> bool:
    """Checks if a Python package can be imported."""
    try:
        importlib.import_module(pkg)
        print(f"Python package '{pkg}': ✅")
        return True
    except ImportError:
        print(f"Python package '{pkg}': ❌ NOT INSTALLED")
        return False

def main():
    success = True
    print("=== System Dependency Checks ===")
    if not check_command("node", "Node.js"): success = False
    if not check_command("npm", "npm"): success = False
    if not check_command("allure", "Allure CLI"): success = False
    if not check_command("java", "Java"): success = False
    # Optional tools don't affect the success status
    check_command("nvm", "nvm (optional)", is_critical=False)
    check_command("sass", "Sass CLI (optional)", is_critical=False)
    check_command("eza", "eza (optional, for tree view)", is_critical=False)

    print("\n=== Python Package Checks ===")
    for pkg in config.PYTHON_PACKAGES:
        if not check_python_package(pkg):
            success = False

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        print("\n✅ All critical dependencies are met.")
    else:
        print("\n❌ Critical dependencies are missing. Please review the checklist.")
    sys.exit(exit_code)