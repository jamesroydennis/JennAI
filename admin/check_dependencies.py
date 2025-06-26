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

def check_command(cmd, name):
    path = shutil.which(cmd)
    if path:
        print(f"{name}: ✅ ({path})")
    else:
        print(f"{name}: ❌ NOT FOUND")

def check_python_package(pkg):
    try:
        importlib.import_module(pkg)
        print(f"Python package '{pkg}': ✅")
    except ImportError:
        print(f"Python package '{pkg}': ❌ NOT INSTALLED")

def main():
    print("=== System Dependency Checks ===")
    check_command("nvm", "nvm")
    check_command("node", "Node.js")
    check_command("npm", "npm")
    check_command("sass", "Sass CLI")
    check_command("eza", "eza (tree view)")
    check_command("allure", "Allure CLI")
    check_command("java", "Java")

    print("\n=== Python Package Checks ===")
    for pkg in config.PYTHON_PACKAGES:
        check_python_package(pkg)

if __name__ == "__main__":
    main()