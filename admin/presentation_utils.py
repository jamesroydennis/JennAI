"""
Shared utilities for the presentation layer admin scripts.

This file centralizes common functions and data structures related to managing
different presentation frameworks to avoid code duplication and circular dependencies.
"""
from pathlib import Path
import sys

# This setup is needed so the utility can import from config
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config

def get_platform_paths() -> dict:
    """Returns the dictionary of all supported presentation platform paths."""
    return {
        "flask": config.PRESENTATION_DIR / "api_server" / "flask_app",
        "angular": config.PRESENTATION_DIR / "angular_app",
        "react": config.PRESENTATION_DIR / "react_app",
        "vue": config.PRESENTATION_DIR / "vue_app",
    }