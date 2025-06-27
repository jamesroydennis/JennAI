"""
JennAI Project Configuration

Centralizes all key paths, environment whitelists, and global settings.
Import from this file in admin scripts, tests, and modules to ensure consistency and maintainability.

- All paths are resolved relative to the project root.
- Update this file if your directory structure changes.
"""
import os # Added for os.getenv

from pathlib import Path # Assuming this is where your config.py is located

# ============================================================================
# 1. PROJECT METADATA
# ============================================================================
APP_NAME = "JennAI"
VERSION = "0.1.0"

# ============================================================================
# 2. ROOT & DIRECTORY STRUCTURE
# ============================================================================
ROOT = Path(__file__).resolve().parent.parent

# Core directories
ADMIN_DIR         = ROOT / "admin"
CONFIG_DIR        = ROOT / "config"
SRC_DIR           = ROOT / "src"
NOTEBOOKS_DIR     = ROOT / "notebooks"
ALLURE_RESULTS_DIR= ROOT / "allure-results"
LOGS_DIR          = ROOT / "logs"
BRAND_DIR         = SRC_DIR / "presentation" / "brand" # Corrected path to user's brand folder
VALIDATION_DIR    = SRC_DIR / "validation" # Consolidated and moved to be under src
DATA_DIR          = SRC_DIR / "data"
PRESENTATION_DIR  = SRC_DIR / "presentation"
BUSINESS_DIR      = SRC_DIR / "business"
SAMPLE_DATA_DIR   = DATA_DIR / "samples" # Renamed for clarity

# ============================================================================
# 3. LOGGING
# ============================================================================
LOG_FILE = LOGS_DIR / "jennai.log"

# ============================================================================
# 4. DATABASE CONFIGURATION
# ============================================================================
DB_PATH      = ROOT / "jennai_db.sqlite"
TEST_DB_PATH = ROOT / "test_jennai_db.sqlite"

# ============================================================================
# 5. ENVIRONMENTS & EXECUTION CONTEXT
# ============================================================================
ENVIRONMENTS = [
    "DEV",
    "TEST",
    "STAGING",
    "PROD"
]

# Conda environments allowed to run admin scripts
WHITELIST_ENVIRONMENTS = [
    "jennai-root",
    "lily-presents"
]
# Alias for backward compatibility
ALLOWED_ENVS = WHITELIST_ENVIRONMENTS

# ============================================================================
# 6. APPLICATION PRESENTATION LAYER NAMES
# ============================================================================
ANGULAR_NAME = f"{APP_NAME}-angular"
FLASK_NAME   = f"{APP_NAME}-flask"
REACT_NAME   = f"{APP_NAME}-react"
VUE_NAME     = f"{APP_NAME}-vue" # Added for consistency

# Whitelist of supported web application keys for admin scripts
WEB_APP_NAMES = ["flask", "angular", "react", "vue"]

# ============================================================================
# 7. USER ROLES & CROSS-CUTTING CONFIGURATION
# ============================================================================
ROLES = [
    "SUPER",
    "ADMIN",
    "DEVELOPER",
    "QA",
    "TESTER",
    "USER",
    "VIEWER"
]

# ============================================================================
# 8. DEBUGGING & DEVELOPMENT FLAGS
# ============================================================================
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ('true', '1', 't')
TESTING_MODE = os.getenv("TESTING_MODE", "False").lower() in ('true', '1', 't')
# ============================================================================
# 9. (OPTIONAL) BRANDING & ASSET PATHS
# ============================================================================
FAVICON_PATH = BRAND_DIR / "favicon_io" / "favicon.ico"
LOGO_PATH    = BRAND_DIR / "jennai-logo.png"

# ============================================================================
# 10. DEFAULT ADMIN USER (for dev/testing)
# ============================================================================
DEFAULT_ADMIN_USER  = "admin"
DEFAULT_ADMIN_EMAIL = "admin@jennai.local"

# ============================================================================
# 11. CORE PYTHON DEPENDENCIES
# ============================================================================
# Central list of required Python packages for the project.
# Used by admin/check_dependencies.py to verify the environment.
PYTHON_PACKAGES = [
    "flask", "flask_cors", "flask_assets", "InquirerPy",
    "numpy", "pandas", "requests", "matplotlib", "jupyter", "markdown",
    "pytest", "loguru","dotenv"
]
# ============================================================================
# END OF CONFIGURATION
# ============================================================================