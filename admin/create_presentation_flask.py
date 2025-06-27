#!/usr/bin/env python
import os
import shutil
from pathlib import Path
import subprocess # Import subprocess for running external commands
# Import the configuration
import sys

jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))
from config.loguru_setup import setup_logging, logger # Import logger
from config.config import ROOT, ADMIN_DIR, SRC_DIR


# Map template files to their destination relative to DEST_ROOT
TEMPLATE_MAP = {
    "app.py.template": "app.py",
    "routes/brand_routes.py.template": "routes/brand_routes.py",
    "templates/base.html.template": "templates/base.html",
    "templates/index.html.template": "templates/index.html",
    "templates/404.html.template": "templates/404.html",
    "templates/500.html.template": "templates/500.html",
    "static/css/main.scss.template": "static/css/main.scss",
    "static/js/scripts.js.template": "static/js/scripts.js",
}

TEMPLATE_DIR = ADMIN_DIR / "templates" / "flask"
DEST_ROOT = SRC_DIR / "presentation" / "api_server" / "flask_app"

def ensure_and_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src.stat().st_mtime - dst.stat().st_mtime > 1: # Copy if doesn't exist or source is newer
        shutil.copy2(src, dst)
        logger.info(f"Created/Updated: {dst.relative_to(ROOT)}")
    else:
        logger.info(f"Exists: {dst.relative_to(ROOT)}")

def main():
    # Add a top-level check to see if the app already exists.
    # This makes the script's behavior explicit and safe.
    if DEST_ROOT.exists():
        logger.info(f"Flask application directory already exists at '{DEST_ROOT.relative_to(ROOT)}'.")
        logger.info("No files were changed. Use the 'Reset' option in the console to delete and re-scaffold.")
        return 0 # Exit gracefully

    for template_rel, dest_rel in TEMPLATE_MAP.items():
        src = TEMPLATE_DIR / template_rel
        dst = DEST_ROOT / dest_rel
        if src.exists():
            ensure_and_copy(src, dst)
        else:
            logger.warning(f"Template {src.relative_to(ROOT)} does not exist.")
    logger.success("Presentation Flask starter files are in place.")

if __name__ == "__main__":
    setup_logging(debug_mode=True) # Setup logging for this script
    exit(main())