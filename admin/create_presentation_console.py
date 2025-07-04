#!/usr/bin/env python
"""
Console presentation creation script.

The console platform is abstract and doesn't create physical files,
but this script provides the required DEST_ROOT variable for testing consistency.
"""
import sys
from pathlib import Path

# Setup path for imports
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.config import ROOT, SRC_DIR
from config.loguru_setup import setup_logging, logger

# Required for testing framework - defines where console app would be located
DEST_ROOT = SRC_DIR / "presentation" / "console_app"

# Required for testing framework - console platform has no templates since it's abstract
TEMPLATE_MAP = {}

# Required for testing framework - console platform has no directories to create since it's abstract
DIRECTORIES_TO_CREATE = []

def main():
    """
    Console platform is abstract - it represents command-line interfaces
    that are scattered throughout the admin directory rather than being
    a single constructed application.
    """
    logger.info("Console platform is abstract - no files to create.")
    logger.info(f"Console app conceptual location: {DEST_ROOT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    setup_logging()
    main()