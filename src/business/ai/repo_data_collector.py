# /home/jdennis/Projects/JennAI/src/business/ai/repo_data_collector.py

import sys
from pathlib import Path
from typing import Dict, Optional

# --- Root Project Path Setup ---
# This ensures the script can import modules from the JennAI project root,
# like the logging configuration.
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from config.loguru_setup import logger # Simply import the configured logger

def _read_file_content(file_path: Path) -> Optional[str]:
    """
    Safely reads the content of a file.

    Args:
        file_path: Path object pointing to the file.

    Returns:
        The content of the file as a string, or None if the file
        is not found, cannot be read, or is not a file.
    """
    if file_path.is_file():
        try:
            content = file_path.read_text(encoding='utf-8')
            logger.debug(f"Successfully read content from: {file_path}")
            return content
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return None
    logger.debug(f"File not found or is not a file: {file_path}")
    return None

def collect_repository_data(repo_path_str: str) -> Dict[str, Optional[str]]:
    """
    Collects data from specified known files within a given repository path.
    This first iteration focuses on README.md, requirements.txt, and environment.yaml.

    Args:
        repo_path_str: The string path to the root of the target repository.

    Returns:
        A dictionary containing the content of the files:
        - "readme_content"
        - "requirements_txt_content"
        - "environment_yaml_content"
        Values will be None if a file is not found or cannot be read.
        Includes an "error" key if the repo_path_str is invalid.
    """
    repo_root = Path(repo_path_str).resolve()
    logger.info(f"Starting data collection for repository: {repo_root}")

    if not repo_root.is_dir():
        logger.error(f"Provided repository path is not a valid directory: {repo_root}")
        return {
            "readme_content": None,
            "requirements_txt_content": None,
            "environment_yaml_content": None,
            "error": f"Invalid repository path: {repo_root}"
        }

    data = {
        "readme_content": _read_file_content(repo_root / "README.md"),
        "requirements_txt_content": _read_file_content(repo_root / "requirements.txt"),
        "environment_yaml_content": _read_file_content(repo_root / "environment.yaml"),
        "error": None # No error if path is valid
    }

    logger.success(f"Repository data collection complete for: {repo_root}")
    return data

if __name__ == "__main__":
    logger.info("Repo Data Collector - Standalone Run Example (First Iteration)")
    # Example usage: Point to the JennAI project root for testing
    test_repo_path = str(jennai_root_for_path) 
    # Or uncomment and set to another local git repository path for testing:
    # test_repo_path = "/path/to/your/other/repository" 

    collected_data = collect_repository_data(test_repo_path)
    
    if collected_data.get("error"):
        logger.error(f"Error collecting data: {collected_data['error']}")
    else:
        logger.info("\nCollected Data Summary:")
        for key, content in collected_data.items():
            if key == "error": continue # Skip the error key if no error
            if content is not None:
                logger.info(f"--- {key} ---")
                logger.info(f"{content[:200].strip()}..." if len(content) > 200 else content.strip())
            else:
                logger.info(f"--- {key} --- \nNot found or empty.")