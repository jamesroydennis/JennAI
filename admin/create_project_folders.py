# /home/jdennis/Projects/JennAI/admin/create_project_folders.py

import os
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from loguru import logger
from config.loguru_setup import setup_logging

# --- Configuration ---
# Determine the JennAI project root dynamically.
# Assumes this script is in 'JennAI/admin/'.
# SCRIPT_DIR = Path(__file__).resolve().parent  # This will be .../JennAI/admin
# JENNAI_ROOT = SCRIPT_DIR.parent              # This will be .../JennAI
JENNAI_ROOT = jennai_root_for_path # Use the globally defined root

# logger.info(f"JennAI Project Root determined as: {JENNAI_ROOT}") # Logged by setup_logging

# --- Directory Structure Definition ---
# List of all directories to create relative to JENNAI_ROOT.
# Using a set for quick lookups if needed, though a list is fine for iteration.
DIRECTORIES_TO_CREATE = [
    "admin",  # The script itself is here, but good to ensure it's listed
    "config",
    "core",
    "logs",
    "src",
    "src/business",
    "src/business/ai",
    "src/business/pyrepopal", # For the new workflow service
    "src/business/sys", # New folder for general system utilities
    "src/business/ai/tests", # Tests for AI components
    "src/business/ai/prompt_templates", # New folder for prompt templates
    "src/business/interfaces",
    "src/business/sys/tests", # Tests for sys components
    "src/business/notebooks",
    "src/business/tests",
    "src/data",
    "src/data/implementations/tests", # Tests for data implementation components
    "src/data/implementations",
    "src/data/interfaces",
    "src/data/generated_prompts", # New folder for storing generated prompts
    "src/data/min_sys_reqs", # New folder for minimum system requirement files
    "src/data/notebooks",
    "src/data/obj",
    "src/data/sample", # New folder for sample data files
    "src/data/system_info", # New folder for system hardware details
    "src/data/tests",
    "src/presentation",
    "src/presentation/api_server", # For backend API logic
    "src/presentation/api_server/controllers",
    "src/presentation/api_server/schemas",
    "src/presentation/api_server/flask_app", # Example for Flask
    "src/presentation/api_server/flask_app/routes",
    "src/presentation/api_server/flask_app/static", # Static files for Flask app
    "src/presentation/api_server/flask_app/static/css", # For CSS files
    "src/presentation/api_server/flask_app/static/img",  # For Flask app specific images
    "src/presentation/api_server/flask_app/static/js",   # For JavaScript files
    "src/presentation/api_server/flask_app/templates", # Templates for Flask app
    "src/presentation/img", # For general presentation layer images
    "src/presentation/web_clients", # For frontend client projects
    # "src/presentation/web_clients/react_app", # You'd init React project here
    # "src/presentation/web_clients/angular_app", # You'd init Angular project here
    "src/presentation/tests", # Tests for the presentation layer (e.g., API tests)
    "tests",  # Top-level tests directory
]

# Directories that should be Python packages (i.e., need an __init__.py)
PACKAGES_TO_INITIALIZE = [
    "config",
    "core",
    "src",
    "src/business",
    "src/business/ai",
    "src/business/ai/tests", # Initialize as package
    "src/business/sys", # Initialize as package
    "src/business/sys/tests", # Initialize as package
    "src/business/interfaces",
    "src/business/tests",
    "src/data/implementations/tests", # Initialize as package
    "src/data",
    "src/data/implementations",
    "src/data/interfaces",
    "src/data/obj",
    "src/data/tests",
    "src/presentation",
    "src/presentation/api_server",
    "src/presentation/api_server/controllers",
    "src/presentation/api_server/schemas",
    "src/presentation/api_server/flask_app",
    "src/presentation/api_server/flask_app/routes",
    "src/presentation/tests", # For presentation layer tests
    "tests", # Top-level tests directory
]

def create_folders_and_inits():
    """
    Creates the defined directory structure and adds __init__.py files
    to specified package directories.
    """
    logger.info("Starting project folder creation...")

    # Create directories
    for dir_path_str in DIRECTORIES_TO_CREATE:
        path = JENNAI_ROOT / dir_path_str
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.success(f"Created directory: {path}")
        else:
            logger.info(f"Skipped, directory already exists: {path}")

    logger.info("Initializing Python package directories...")
    # Create __init__.py files
    for pkg_path_str in PACKAGES_TO_INITIALIZE:
        pkg_path = JENNAI_ROOT / pkg_path_str
        init_file = pkg_path / "__init__.py"
        if not init_file.exists():
            # Ensure the parent directory exists (should be true from above step)
            if not pkg_path.exists(): # Should not happen if DIRECTORIES_TO_CREATE is comprehensive
                pkg_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created parent directory for __init__.py: {pkg_path}")

            with open(init_file, "w") as f:
                f.write(f"# Initializes the {pkg_path_str.replace('/', '.')} package.\n")
            logger.success(f"Created __init__.py in: {pkg_path}")
        else:
            logger.info(f"Skipped, __init__.py already exists in: {pkg_path}")

    logger.success("Project folder structure setup complete.")

if __name__ == "__main__":
    # Setup logging for this script, similar to cleanup.py
    # Assuming verbose output is desired for this utility.
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for create_project_folders.py.")
    create_folders_and_inits()
