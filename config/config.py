"""
JennAI Project Configuration

Centralizes all key paths, environment whitelists, and global settings.
Import from this file in admin scripts, tests, and modules to ensure consistency and maintainability.

- All paths are resolved relative to the project root.
- Update this file if your directory structure changes.
"""

from pathlib import Path

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
BRAND_DIR         = SRC_DIR / "presentation" / "brand" # Corrected path to user's brand folder
ALLURE_RESULTS_DIR= ROOT / "allure-results"
VALIDATION_DIR    = ROOT / "validation"
LOGS_DIR          = ROOT / "logs"
DATA_DIR          = SRC_DIR / "data"
SAMPLES_DIR       = DATA_DIR / "samples"

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
DEBUG_MODE = True

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
# END OF CONFIGURATION
# ============================================================================