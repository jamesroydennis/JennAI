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

def get_presentation_apps() -> dict:
    """
    Returns the dictionary of all supported presentation apps with their paths.
    
    This function combines the platform information from config.PRESENTATION_APPS
    with the actual filesystem paths where each platform is located.
    
    Returns:
        dict: Platform name -> Path mapping for all presentation apps
    """
    return {
        "console": config.PRESENTATION_DIR / "console_app",
        "flask": config.PRESENTATION_DIR / "api_server" / "flask_app",
        "angular": config.PRESENTATION_DIR / "angular_app",
        "react": config.PRESENTATION_DIR / "react_app",
        "vue": config.PRESENTATION_DIR / "vue_app",
    }

# Backward compatibility alias (to be removed after updating all references)
def get_platform_paths() -> dict:
    """DEPRECATED: Use get_presentation_apps() instead."""
    return get_presentation_apps()