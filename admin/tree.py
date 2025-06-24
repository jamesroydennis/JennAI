# c/Users/jarde/Projects/JennAI/admin/tree.py

import sys
import subprocess
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from loguru import logger
from config.loguru_setup import setup_logging

def print_basic_tree(root_dir: Path, prefix: str = "", ignore_list: list = None):
    """
    A simple, recursive Python-based directory tree printer.
    This serves as a fallback if 'eza' is not installed.
    """
    if ignore_list is None:
        # Ignore common metadata, assets, and cache folders for a clean code structure view
        ignore_list = [
            # Version control & caches
            '.git', '.idea', '.vscode', '.pytest_cache', '__pycache__', '.trash',
            # Virtual environments
            '.venv', 'jennai-root', 'env', 'venv',
            # Documentation & metadata files at root
            '.gitignore', 'LICENSE', 'README.md', 'plan.md', 'monorepo.ipynb',
            'environment.yaml', 'pyproject.toml', 'pytest.ini', 'requirements.txt', 'requirements.ps1',
            # Top-level test/log/report/asset folders
            'logs', 'allure-results', 'allure-report', 'Brand',
            # Core script files at root
            'main.py', 'conftest.py',
        ]

    try:
        # Filter out ignored items and sort for consistent order
        items = sorted([item for item in root_dir.iterdir() if item.name not in ignore_list])
    except FileNotFoundError:
        return  # Should not happen if called correctly

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_basic_tree(item, prefix=new_prefix, ignore_list=ignore_list)

def run_eza_tree(project_root: Path) -> bool:
    """
    Attempts to run 'eza --tree' and prints its output.
    Returns True if eza ran successfully, False otherwise.
    """
    logger.info("Attempting to display project tree with 'eza --tree'...")
    try:
        # On Windows with shell=True, passing the command as a string is more reliable.
        # 'encoding="utf-8"' is CRITICAL to fix garbled Unicode output.
        result = subprocess.run(
            "eza --tree",
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8'
        )
        # Print eza tree output directly to console for better formatting.
        print("\n------------------- Project Tree (eza) -------------------")
        print(result.stdout.strip())
        print("--------------------------------------------------------")
        logger.info("Successfully displayed project tree using 'eza --tree'.")
        return True
    except FileNotFoundError:
        # This is the most common case: 'eza' is not installed or not in PATH.
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"'eza --tree' command failed with error: {e}")
        # Use .strip() to clean up potential newlines in the stderr output
        logger.error(f"  Stderr: {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while trying to run 'eza --tree': {e}")
        return False

if __name__ == "__main__":
    setup_logging(debug_mode=True)
    logger.info("Loguru setup complete for tree.py.")
    if not run_eza_tree(jennai_root_for_path):
        logger.warning("'eza' command not found or failed. Falling back to basic Python tree view.")
        print("\n------------------- Project Tree (Basic) -------------------")
        print_basic_tree(jennai_root_for_path)
        print("----------------------------------------------------------")
