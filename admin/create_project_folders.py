#!/usr/bin/env python
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
PROJECT_ROOT = jennai_root_for_path

# --- Directory Structure Definition ---
DIRECTORIES_TO_CREATE = [
    "admin", "config", "core", "logs", "src", "tests",
    "src/business", "src/data", "src/presentation",
    "src/business/ai", "src/business/interfaces", "src/business/notebooks",
    "src/business/prp_workflow", "src/business/sys", "src/business/tests",
    "src/business/ai/prompt_templates", "src/business/ai/tests",
    "src/business/sys/tests",
    "src/data/database", "src/data/generated_prompts", "src/data/implementations",
    "src/data/interfaces", "src/data/min_sys_reqs", "src/data/notebooks", "src/data/obj",
    "src/data/sample", "src/data/scripts", "src/data/system_info", "src/data/tests",
    "src/data/implementations/tests",
    "src/data/scripts/sql",
    "src/presentation/api_server", "src/presentation/img", "src/presentation/tests", "src/presentation/web_clients",
    "src/presentation/api_server/controllers", "src/presentation/api_server/flask_app", "src/presentation/api_server/schemas",
    "src/presentation/api_server/flask_app/routes", "src/presentation/api_server/flask_app/static", "src/presentation/api_server/flask_app/templates",
    "src/presentation/api_server/flask_app/static/css", "src/presentation/api_server/flask_app/static/img", "src/presentation/api_server/flask_app/static/js",
    "tests/integration", "tests/presentation", "tests/sample_repos",
    "tests/sample_repos/dev_sample", "tests/sample_repos/proofconcept",
]

# Directories that should be Python packages (i.e., need an __init__.py)
PACKAGES_TO_INITIALIZE = [
    "admin", "config", "core", "src", "tests",
    "src/business", "src/data", "src/presentation", 
    "src/business/ai", "src/business/interfaces", "src/business/prp_workflow", "src/business/sys", "src/business/tests",
    "src/business/ai/tests",
    "src/business/sys/tests",
    "src/data/implementations", "src/data/interfaces", "src/data/obj", "src/data/scripts", "src/data/tests",
    "src/data/implementations/tests",
    "src/data/scripts/sql",
    "src/presentation/api_server", "src/presentation/tests",
    "src/presentation/api_server/controllers", "src/presentation/api_server/flask_app", "src/presentation/api_server/schemas",
    "src/presentation/api_server/flask_app/routes",
    "tests/integration", "tests/presentation", "tests/sample_repos",
]

def create_folders_and_inits():
    """
    Creates the defined directory structure and adds __init__.py files
    to specified package directories, logging only the changes made.
    """
    logger.info("Verifying project folder structure...")
    dirs_created = 0
    inits_created = 0

    # Create directories
    for dir_path_str in sorted(list(set(DIRECTORIES_TO_CREATE))):
        path = PROJECT_ROOT / dir_path_str
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            dirs_created += 1

    # Create __init__.py files
    for pkg_path_str in sorted(list(set(PACKAGES_TO_INITIALIZE))):
        init_file = PROJECT_ROOT / pkg_path_str / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            init_file.write_text(f"# Initializes the {pkg_path_str.replace('/', '.')} package.\n")
            inits_created += 1

    if dirs_created > 0 or inits_created > 0:
        logger.success(f"Project structure updated. Created {dirs_created} director(y/ies) and {inits_created} __init__.py file(s).")
    else:
        logger.info("Project structure is already up to date. No changes made.")

if __name__ == "__main__":
    # Setup logging for this script, similar to cleanup.py
    # Assuming verbose output is desired for this utility.
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for create_project_folders.py.")
    create_folders_and_inits()
