#!/usr/bin/env python
import sys
import shutil
import argparse
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config
from loguru import logger
from config.loguru_setup import setup_logging

# --- Define Asset Paths ---
BRAND_SRC_DIR = config.BRAND_DIR
PRESENTATION_DIR = PROJECT_ROOT / "src" / "presentation"

# --- Target Configurations ---
# This dictionary defines the asset destinations for each presentation framework.
# It's the single source of truth for asset injection.
TARGETS = {
    "console": {
        "img_dir": None,
        "css_dir": None,
        "text_dir": None,
        "asset_map": {} # The console is abstract and has no assets.
    },
    "flask": {
        "img_dir": PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "img",
        "css_dir": PRESENTATION_DIR / "api_server" / "flask_app" / "static" / "css",
        "text_dir": None, # Flask reads text directly from Brand/, doesn't copy to static
        "asset_map": {
            BRAND_SRC_DIR / "jennai-logo.png": "jennai-logo.png",
            BRAND_SRC_DIR / "favicon_io" / "favicon.ico": "favicon.ico",
            BRAND_SRC_DIR / "me.jpeg": "your-portrait.jpg",
            BRAND_SRC_DIR / "circuit-dark.jpg": "circuit-dark-bg.jpg",
            BRAND_SRC_DIR / "person.jpg": "person-interacting-ai.jpg",
            BRAND_SRC_DIR / "heart-blueforeground.jpg": "neon-heart.jpg",
            BRAND_SRC_DIR / "under_construction.png": "under_construction.png",
            BRAND_SRC_DIR / "theme.scss": "_variables.scss",
        }
    },
    "angular": {
        "img_dir": PRESENTATION_DIR / "angular_app" / "src" / "assets",
        "css_dir": PRESENTATION_DIR / "angular_app" / "src" / "styles",
        "text_dir": PRESENTATION_DIR / "angular_app" / "src" / "assets", # Angular often puts text in assets
        "asset_map": {
            BRAND_SRC_DIR / "jennai-logo.png": "logo.png",
            BRAND_SRC_DIR / "favicon_io" / "favicon.ico": "favicon.ico",
            BRAND_SRC_DIR / "theme.scss": "theme.scss",
            BRAND_SRC_DIR / "mission.txt": "mission.txt",
            BRAND_SRC_DIR / "vision.md": "vision.md",
            # Add other Angular-specific assets here
        }
    },
    "vue": {
        "img_dir": PRESENTATION_DIR / "vue_app" / "src" / "assets",
        "css_dir": PRESENTATION_DIR / "vue_app" / "src" / "styles",
        "text_dir": PRESENTATION_DIR / "vue_app" / "src" / "assets",
        "asset_map": {
            BRAND_SRC_DIR / "jennai-logo.png": "logo.png",
            BRAND_SRC_DIR / "favicon_io" / "favicon.ico": "favicon.ico",
            BRAND_SRC_DIR / "theme.scss": "theme.scss",
            BRAND_SRC_DIR / "mission.txt": "mission.txt",
            BRAND_SRC_DIR / "vision.md": "vision.md",
                    }
    },
    "react": {
        "img_dir": PRESENTATION_DIR / "react_app" / "src" / "assets",
        "css_dir": PRESENTATION_DIR / "react_app" / "src",  # React often imports SCSS from src/
        "text_dir": PRESENTATION_DIR / "react_app" / "src" / "assets",
        "asset_map": {
            BRAND_SRC_DIR / "jennai-logo.png": "logo.png",
            BRAND_SRC_DIR / "favicon_io" / "favicon.ico": "favicon.ico",
            BRAND_SRC_DIR / "theme.scss": "theme.scss",
            BRAND_SRC_DIR / "mission.txt": "mission.txt",
            BRAND_SRC_DIR / "vision.md": "vision.md",
        }
    }
}

def main(target: str):
    """Copies brand assets to the specified presentation layer."""
    logger.info(f"Starting brand asset injection for '{target}' presentation layer...")

    if target not in TARGETS:
        logger.error(f"Invalid target '{target}'. Available targets are: {list(TARGETS.keys())}")
        return

    target_config = TARGETS[target]
    img_dir = target_config.get("img_dir")
    css_dir = target_config.get("css_dir")
    text_dir = target_config.get("text_dir")

    for src_path, dest_name in target_config["asset_map"].items():
        # Determine the correct destination directory based on file type
        if dest_name.endswith(('.scss', '.css')):
            dest_dir = css_dir
        elif dest_name.endswith(('.txt', '.md')):
            dest_dir = text_dir
        else: # Default to image directory for png, jpg, ico, etc.
            dest_dir = img_dir

        if not dest_dir:
            logger.warning(f"No destination directory configured for asset '{dest_name}' in target '{target}'. Skipping.")
            continue

        # The DESIGNER now depends on the CONSTRUCTOR. It will not create directories.
        if not dest_dir.exists():
            logger.error(f"DESIGNER CRITIQUE: The destination directory '{dest_dir}' does not exist. The foundational structure must be created first (e.g., via 'Initialize/Create Folders').")
            return # Abort this design task.

        dest_path = dest_dir / dest_name
        if not src_path.exists():
            logger.warning(f"Source asset not found, skipping: {src_path}")
            continue
        try:
            shutil.copy2(src_path, dest_path)
            logger.success(f"Copied '{src_path.name}' to '{dest_path.relative_to(PROJECT_ROOT)}'")
        except Exception as e:
            logger.error(f"Failed to copy '{src_path.name}' to '{dest_path}': {e}")

    logger.info(f"\n✅ Brand asset injection for '{target}' complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject brand assets into a presentation layer.")
    parser.add_argument("--target", required=True, choices=TARGETS.keys(), help="The target presentation framework (e.g., 'flask').")
    args = parser.parse_args()
    
    setup_logging(debug_mode=True)
    main(args.target)