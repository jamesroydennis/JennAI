#!/usr/bin/env python

import os
import sys
import shutil
import fnmatch
import subprocess
from pathlib import Path

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from loguru import logger
from config.loguru_setup import setup_logging

# Directories and files to ignore in the tree view to keep the output clean.
IGNORE_LIST = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".virtual_documents",
    ".ipynb_checkpoints",
    "dist",
    "build",
    ".angular",
    "allure-results",
    "allure-report",
    ".vscode",
    "*.pyc",
    "*.zip",  # To hide compressed logs
]

def run_eza_tree():
    """Attempts to generate a tree view using the 'eza' command."""
    ignore_glob = "|".join(IGNORE_LIST)
    command = [
        "eza", "--tree", "--level=4", f"--ignore-glob={ignore_glob}", "--git-ignore"
    ]
    try:
        logger.info("Found 'eza'. Generating a rich, colorized tree view...")
        subprocess.run(command, check=True, cwd=ROOT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning(f"Failed to run 'eza': {e}. It may not be in your PATH.")
        return False

def print_basic_tree(directory: Path, prefix: str = "", ignore_list: list = None):
    """
    A basic, pure-Python fallback for displaying a directory tree.
    This version correctly handles glob patterns in the ignore list.
    """
    if ignore_list is None:
        ignore_list = IGNORE_LIST

    try:
        # Filter paths based on the ignore list, supporting both names and glob patterns.
        paths_to_process = []
        for p in directory.iterdir():
            is_ignored = any(fnmatch.fnmatch(p.name, pattern) for pattern in ignore_list)
            if not is_ignored:
                paths_to_process.append(p)
        # Sort to show directories first, then files, both alphabetically.
        paths = sorted(paths_to_process, key=lambda p: (p.is_file(), p.name.lower()))
    except FileNotFoundError:
        logger.error(f"Directory not found: {directory}")
        return

    pointers = ["├── "] * (len(paths) - 1) + ["└── "]
    for pointer, path in zip(pointers, paths):
        print(f"{prefix}{pointer}{path.name}{'/' if path.is_dir() else ''}")
        if path.is_dir():
            extension = "    " if pointer == "└── " else "│   "
            print_basic_tree(path, prefix + extension, ignore_list)

def main():
    """Main function to decide which tree-printing method to use."""
    setup_logging(debug_mode=True)
    logger.info(f"Generating directory tree for: {ROOT}")

    if shutil.which("eza") and run_eza_tree():
        return

    logger.info("'eza' not found or failed. Falling back to a basic tree view.")
    print_basic_tree(ROOT)

if __name__ == "__main__":
    main()