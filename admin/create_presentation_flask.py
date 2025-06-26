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
from config.config import ROOT, ADMIN_DIR, SRC_DIR


# Map template files to their destination relative to DEST_ROOT
TEMPLATE_MAP = {
    "app.py.template": "app.py",
    "templates/base.html.template": "templates/base.html",
    "templates/index.html.template": "templates/index.html",
    "templates/404.html.template": "templates/404.html",
    "templates/500.html.template": "templates/500.html",
    "static/css/main.scss.template": "static/css/main.scss",
    "static/css/_variables.scss.template": "static/css/_variables.scss",
    "static/js/scripts.js.template": "static/js/scripts.js",
}

TEMPLATE_DIR = ADMIN_DIR / "templates" / "flask"
DEST_ROOT = SRC_DIR / "presentation" / "api_server" / "flask_app"

def ensure_and_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)
        print(f"Created: {dst}")
    else:
        print(f"Exists:  {dst}")

def compile_scss(input_path: Path, output_path: Path):
    """Compiles an SCSS file to CSS using the 'sass' CLI."""
    try:
        print(f"Compiling SCSS: {input_path.name} -> {output_path.name}")
        # Use subprocess.run for simple command execution
        subprocess.run(
            ['sass', str(input_path), str(output_path)],
            check=True, # Raise an exception if the command returns a non-zero exit code
            capture_output=True, # Capture stdout and stderr
            text=True # Decode stdout/stderr as text
        )
        print(f"Successfully compiled: {output_path.name}")
    except FileNotFoundError:
        print(f"Error: 'sass' command not found. Please install Dart Sass CLI (npm install -g sass).")
        print(f"Skipping SCSS compilation for {input_path.name}.")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling SCSS for {input_path.name}:\n{e.stderr}")

def main():
    for template_rel, dest_rel in TEMPLATE_MAP.items():
        src = TEMPLATE_DIR / template_rel
        dst = DEST_ROOT / dest_rel
        if src.exists():
            ensure_and_copy(src, dst)
        else:
            print(f"Warning: Template {src} does not exist.")
            
    # After copying, compile the main SCSS file
    main_scss_path = DEST_ROOT / "static" / "css" / "main.scss"
    main_css_path = DEST_ROOT / "static" / "css" / "main.css"
    if main_scss_path.exists():
        compile_scss(main_scss_path, main_css_path)
    print("\n✅ Presentation Flask starter files are in place.")

if __name__ == "__main__":
    exit(main())