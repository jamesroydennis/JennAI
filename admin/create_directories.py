# c:\Users\jarde\Projects\JennAI\admin\create_directories.py
import os
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from loguru import logger
from config.loguru_setup import setup_logging

PROJECT_ROOT = jennai_root_for_path

# Define the directory structure.
# 'is_package': True will create an __init__.py file.
DIRECTORIES = {
    # Top-level directories
    "admin": {"is_package": False},
    "admin/templates": {"is_package": False},
    "admin/templates/flask": {"is_package": False},
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
    # Business layer
    "src/business": {"is_package": True},
    "src/business/ai": {"is_package": True},
    "src/business/interfaces": {"is_package": True},
    "src/business/notebooks": {"is_package": False},
    "src/business/tests": {"is_package": True},
    # Data layer
    "src/data": {"is_package": True},
    "src/data/implementations": {"is_package": True},
    "src/data/interfaces": {"is_package": True},
    "src/data/notebooks": {"is_package": False},
    "src/data/obj": {"is_package": True},
    "src/data/tests": {"is_package": True},
    # Presentation layer
    "src/presentation": {"is_package": True},
    "src/presentation/tests": {"is_package": True},
    "src/presentation/angular_app": {"is_package": False},
    "src/presentation/angular_app/src": {"is_package": False},
    "src/presentation/angular_app/src/app": {"is_package": False},
    "src/presentation/angular_app/src/assets": {"is_package": False},
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
    "src/presentation/img": {"is_package": False},
    "src/presentation/react_app": {"is_package": False},
    "src/presentation/react_app/public": {"is_package": False},
    "src/presentation/react_app/src": {"is_package": False},
    "src/presentation/react_app/node_modules": {"is_package": False},
    "src/presentation/web_clients": {"is_package": False},
}

def main():
    """
    Creates the defined directory structure and adds __init__.py files
    to specified package directories.
    """
    logger.info("Creating project directories...")
    try:
        for dir_path, properties in DIRECTORIES.items():
            full_path = PROJECT_ROOT / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.success(f"Ensured directory exists: {dir_path}")
            if properties["is_package"]:
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    with open(init_file, "w") as f:
                        f.write(f"# Initializes the {dir_path.replace('/', '.')} package.\n")
                    logger.info(f"    -> Created __init__.py to make it a Python package.")
                else:
                    logger.info(f"    -> Ensured it is a Python package.")
        logger.success("\n✅ Project directory structure is up to date.")
        return True
    except OSError as e:
        logger.error(f"Error creating directories: {e}")
        return False

if __name__ == "__main__":
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for create_directories.py.")
    if not main():
        sys.exit(1)
    sys.exit(0)