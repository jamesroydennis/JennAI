# /home/jdennis/Projects/JennAI/admin/tree.py

import sys
import subprocess
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
# Assumes this script is in 'JennAI/admin/'.
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import setup_logging
from loguru import logger

# Setup logging for this script if run directly
if __name__ == "__main__":
    setup_logging(debug_mode=True) # Default to verbose logging when run directly
    logger.info("Loguru setup complete for tree.py.")

def run_eza_tree(project_root: Path):
    """
    Attempts to run 'eza --tree' and prints its output using the logger.
    This function can be called by other scripts or run directly.
    """
    logger.info("Attempting to display project tree with 'eza --tree'...")
    try:
        # Check if eza is installed by trying to get its version
        subprocess.run(["eza", "--version"], check=True, capture_output=True, text=True)
        
        # Run eza --tree
        result = subprocess.run(["eza", "--tree"], cwd=project_root, check=True, capture_output=True, text=True)
        # Print eza tree output directly to console, not to the log file.
        print("\n------------------- Project Tree (eza) -------------------")
        print(result.stdout.strip())
        print("--------------------------------------------------------")
        logger.info("Successfully displayed project tree using 'eza --tree'.")
    except FileNotFoundError:
        logger.warning("'eza' command not found. Skipping tree view. Please install eza to use this feature.")
    except subprocess.CalledProcessError as e:
        logger.error(f"'eza --tree' command failed with error: {e}")
        logger.error(f"  Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while trying to run 'eza --tree': {e}")

if __name__ == "__main__":
    # If run directly, default to the JennAI project root
    run_eza_tree(jennai_root_for_path)