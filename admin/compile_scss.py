#!/usr/bin/env python
import sys
import argparse
import subprocess
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config
from loguru import logger
from config.loguru_setup import setup_logging

# --- Target Configurations ---
# This dictionary defines the source SCSS and destination CSS for each platform.
COMPILE_TARGETS = {
    "flask": {
        "src": config.PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "css" / "main.scss",
        "dest": config.PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "css" / "main.css"
    },
    "angular": {
        # For Angular, we compile the main styles.scss file. The Angular CLI will
        # handle the final bundling, but this allows for manual compilation checks.
        "src": config.PRESENTATION_DIR / "angular_app" / "src" / "styles.scss",
        "dest": config.PRESENTATION_DIR / "angular_app" / "src" / "styles.css"
    },
    "vue": {
        # For Vue, we compile the main theme file.
        "src": config.PRESENTATION_DIR / "vue_app" / "src" / "styles" / "theme.scss",
        "dest": config.PRESENTATION_DIR / "vue_app" / "src" / "styles" / "theme.css"
    },
    "react": {
        # For React, we compile the main theme file.
        "src": config.PRESENTATION_DIR / "react_app" / "src" / "theme.scss",
        "dest": config.PRESENTATION_DIR / "react_app" / "src" / "theme.css"
    }
}

def check_sass_installed():
    """Checks if the Dart Sass CLI is installed and accessible."""
    import os
    import shutil
    
    # First try to find sass in the system PATH
    sass_path = shutil.which("sass")
    if sass_path:
        try:
            subprocess.run([sass_path, "--version"], check=True, capture_output=True, text=True)
            logger.success(f"Sass CLI found at: {sass_path}")
            return True
        except subprocess.CalledProcessError:
            pass
    
    # If not found in PATH, try common installation locations
    common_paths = [
        os.path.expanduser("~\\AppData\\Roaming\\npm\\sass.cmd"),  # Windows npm global
        os.path.expanduser("~\\AppData\\Roaming\\npm\\sass"),      # Windows npm global
        "C:\\Program Files\\nodejs\\sass.cmd",                      # System-wide npm
        "C:\\Program Files\\nodejs\\sass",                          # System-wide npm
    ]
    
    for sass_cmd in common_paths:
        if os.path.exists(sass_cmd):
            try:
                subprocess.run([sass_cmd, "--version"], check=True, capture_output=True, text=True)
                logger.success(f"Sass CLI found at: {sass_cmd}")
                return True
            except subprocess.CalledProcessError:
                continue
    
    # Last resort: try the command directly in case it's in PATH but shutil.which didn't find it
    try:
        subprocess.run(["sass", "--version"], check=True, capture_output=True, text=True)
        logger.success("Sass CLI found via direct command.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Sass CLI ('sass' command) not found.")
        logger.info("Please install it globally via npm: npm install -g sass")
        return False

def get_sass_command():
    """Gets the correct sass command path."""
    import os
    import shutil
    
    # First try to find sass in the system PATH
    sass_path = shutil.which("sass")
    if sass_path:
        return sass_path
    
    # If not found in PATH, try common installation locations
    common_paths = [
        os.path.expanduser("~\\AppData\\Roaming\\npm\\sass.cmd"),  # Windows npm global
        os.path.expanduser("~\\AppData\\Roaming\\npm\\sass"),      # Windows npm global
        "C:\\Program Files\\nodejs\\sass.cmd",                      # System-wide npm
        "C:\\Program Files\\nodejs\\sass",                          # System-wide npm
    ]
    
    for sass_cmd in common_paths:
        if os.path.exists(sass_cmd):
            return sass_cmd
    
    # Default fallback
    return "sass"

def main(target: str):
    """Compiles the main SCSS file for the specified presentation layer."""
    logger.info(f"Starting SCSS compilation for '{target}'...")

    if not check_sass_installed():
        return

    if target not in COMPILE_TARGETS:
        logger.error(f"Invalid target '{target}'. Available targets are: {list(COMPILE_TARGETS.keys())}")
        return

    target_config = COMPILE_TARGETS[target]
    src_path = target_config.get("src")
    dest_path = target_config.get("dest")

    if not src_path or not dest_path:
        logger.error(f"Source or destination path not configured for target '{target}'.")
        return

    if not src_path.exists():
        logger.error(f"Source SCSS file not found at '{src_path.relative_to(PROJECT_ROOT)}'. Cannot compile.")
        return

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    sass_cmd = get_sass_command()
    command = [sass_cmd, str(src_path), str(dest_path)]
    logger.info(f"Executing command: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.success(f"Successfully compiled '{src_path.name}' to '{dest_path.relative_to(PROJECT_ROOT)}'")
        if result.stdout:
            logger.info(f"Sass output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to compile SCSS for '{target}'.")
        logger.error(f"Sass CLI Error:\n{e.stderr}")
        if e.stdout:
            logger.error(f"Sass CLI Output:\n{e.stdout}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile SCSS for a presentation layer.")
    parser.add_argument("--target", required=True, choices=COMPILE_TARGETS.keys(), help="The target presentation framework (e.g., 'flask').")
    args = parser.parse_args()

    setup_logging(debug_mode=True)
    main(args.target)