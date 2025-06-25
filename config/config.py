"""
JennAI Project Configuration

This module centralizes all key project paths, environment whitelists, and global settings.
Import from this file in admin scripts, tests, and modules to ensure consistency and maintainability.

- All paths are resolved relative to the project root.
- Update this file if your directory structure changes.
"""

from pathlib import Path

# Project root directory (one level above this config file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Key project directories
ADMIN_DIR = PROJECT_ROOT / "admin"
CONFIG_DIR = PROJECT_ROOT / "config"
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
SRC_DIR = PROJECT_ROOT / "src"
BRAND_DIR = PROJECT_ROOT / "Brand"
# Add more as needed

# List of Conda environments allowed to run admin scripts
WHITELIST_ENVIRONMENTS = [
    "jennai-root",
    "lily-presents"
]

# (Optional) Debug mode flag for development
DEBUG_MODE = True

# (Legacy/alias) List of allowed environments (use WHITELIST_ENVIRONMENTS)
ALLOWED_ENVS = WHITELIST_ENVIRONMENTS