"""
JennAI Project Configuration

Centralizes all key paths, environment whitelists, and global settings.
Import from this file in admin scripts, tests, and modules to ensure consistency and maintainability.

- All paths are resolved relative to the project root.
- Update this file if your directory structure changes.
"""
from enum import Enum, auto
import os # Added for os.getenv

from pathlib import Path # Assuming this is where your config.py is located

# ============================================================================
# 1. METADATA
# ============================================================================
APP_NAME = "JennAI"
VERSION = "0.1.0"  # Your project's version
GEMINI_VERSION = "2025-06-27T07:00:00Z"  # A timestamp to mark the state of the codebase when Gemini assisted

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
# Dictionary of supported presentation applications, containing their properties.
PRESENTATION_APPS = {
    "flask":   {"name": f"{APP_NAME}-flask",   "display_name": "Flask"},
    "angular": {"name": f"{APP_NAME}-angular", "display_name": "Angular"},
    "react":   {"name": f"{APP_NAME}-react",   "display_name": "React"},
    "vue":     {"name": f"{APP_NAME}-vue",     "display_name": "Vue"},
}

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
# 12. ARCHITECTURAL PERSONAS
# ============================================================================
class ArchitecturalPersona(Enum):
    """
    Defines the roles involved in the project's development lifecycle.
    """
    ARCHITECT = auto()    # Designs the foundational blueprints (scaffolding, brand) and delegates execution.
    CONTRACTOR = auto()   # Manages Constructors and Designers to ensure the Architect's blueprint is deployed to specification on a solid foundation.
    CONSTRUCTOR = auto()  # The developer scaffolding the application framework.
    DESIGNER = auto()     # The designer applying the brand and theme.
    OBSERVER = auto()     # Ensures the design matches the brand and the construction adheres to the Architect's blueprints.
    QA_ENGINEER = auto()  # Verifies the quality and testability of all components.

ROLES_PRESENTATION = [persona.name for persona in ArchitecturalPersona]
# ============================================================================
# END OF CONFIGURATION
# ============================================================================