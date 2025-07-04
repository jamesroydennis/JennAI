#!/usr/bin/env python

import os
from pathlib import Path

# This script is a foundational utility and should have NO dependencies on other
# project modules (like config or loguru) to avoid circular import errors
# during initial project setup. It uses standard `print` for output.

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent

# Define the directory structure.
# 'is_package': True will create an __init__.py file.
DIRECTORIES = {
    # Top-level directories
    "admin": {"is_package": False},

    "admin/templates": {"is_package": False},
    "admin/templates/flask": {"is_package": False},
    "admin/templates/flask/routes": {"is_package": False},
    "admin/templates/flask/templates": {"is_package": False},
    "admin/templates/flask/static": {"is_package": False},
    "admin/templates/flask/static/css": {"is_package": False},
    "admin/templates/flask/static/js": {"is_package": False},
    "config": {"is_package": True},
    "core": {"is_package": True},
    "logs": {"is_package": False},
    "notebooks": {"is_package": False},
    "src": {"is_package": True},
    "tests": {"is_package": True},
    "validation": {"is_package": True},
    "validation/tests": {"is_package": True},
    # Business layer
    "src/business": {"is_package": True},
    "src/business/ai": {"is_package": True},
    "src/business/interfaces": {"is_package": True},
    "src/business/notebooks": {"is_package": False},
    "src/business/tests": {"is_package": True},
    # Validation layer (moved under src)
    "src/validation": {"is_package": True},
    "src/validation/tests": {"is_package": True}, # New: Tests for validation module
    # Data layer
    "src/data": {"is_package": True},
    "src/data/implementations": {"is_package": True},
    "src/data/interfaces": {"is_package": True},
    "src/data/notebooks": {"is_package": False},
    "src/data/obj": {"is_package": True},
    "src/data/samples": {"is_package": False}, # Sample data directories are typically not packages
    "src/data/tests": {"is_package": True},

    # Presentation layer
    "src/presentation": {"is_package": True},
    "src/presentation/tests": {"is_package": True},
    "src/presentation/angular_app": {"is_package": False},
    "src/presentation/angular_app/src": {"is_package": False},
    "src/presentation/angular_app/src/assets": {"is_package": False},
    "src/presentation/angular_app/src/styles": {"is_package": False},
    "src/presentation/angular_app/src/environments": {"is_package": False},
    "src/presentation/api_server": {"is_package": True},
    "src/presentation/api_server/controllers": {"is_package": True},
    "src/presentation/api_server/flask_app": {"is_package": True},
    "src/presentation/api_server/flask_app/routes": {"is_package": True},
    "src/presentation/api_server/flask_app/static": {"is_package": False},
    "src/presentation/api_server/flask_app/static/css": {"is_package": False},
    "src/presentation/api_server/flask_app/static/img": {"is_package": False},
    "src/presentation/api_server/flask_app/static/js": {"is_package": False},
    "src/presentation/api_server/flask_app/templates": {"is_package": False},
    "src/presentation/api_server/schemas": {"is_package": True},
    "src/presentation/console_app": {"is_package": True},
    "src/presentation/img": {"is_package": False},
    "src/presentation/react_app": {"is_package": False},
    "src/presentation/react_app/src": {"is_package": False},
    "src/presentation/react_app/src/assets": {"is_package": False},
    "src/presentation/vue_app": {"is_package": False},
    "src/presentation/vue_app/src": {"is_package": False},
    "src/presentation/vue_app/src/assets": {"is_package": False},
    "src/presentation/vue_app/src/styles": {"is_package": False},
    "src/presentation/web_clients": {"is_package": False},
    # Workflow persona directories (for TDD workflow tests)
    "blueprints": {"is_package": False},
    "contractor_decisions": {"is_package": False},
    "constructor": {"is_package": False},
    "constructor/received_blueprints": {"is_package": False},
    "designer": {"is_package": False},
    "designer/brand_verification": {"is_package": False},
    "collaboration": {"is_package": False},
    "collaboration/designer_constructor": {"is_package": False},
    "observer": {"is_package": False},
    "observer/approvals": {"is_package": False},
    "workflow": {"is_package": False},
}

def main():
    """
    Creates the defined directory structure and adds __init__.py files
    to specified package directories.
    """
    print("Creating project directories...")
    try:
        for dir_path, properties in DIRECTORIES.items():
            full_path = ROOT / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            if properties["is_package"]:
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    with open(init_file, "w") as f:
                        f.write(f"# Initializes the {dir_path.replace('/', '.')} package.\n")
                    print(f"  -> Created __init__.py in '{dir_path}'")
        print("\n✅ Project directory structure is up to date.")
        return True
    except OSError as e:
        print(f"Error creating directories: {e}")
        return False

if __name__ == "__main__":
    main()