# /home/jdennis/Projects/JennAI/src/business/data_source/filesystem_data_source.py

import sys
from pathlib import Path
from typing import Dict, Optional

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.business.interfaces.IRepositoryDataSource import IRepositoryDataSource
from src.business.ai import repo_data_collector
from config.loguru_setup import logger

class FilesystemRepositoryDataSource(IRepositoryDataSource):
    """
    Implementation of IRepositoryDataSource that reads repository
    data directly from the local filesystem.
    """
    def get_repository_data(self, repo_identifier: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Collects data from a repository located at a local filesystem path.

        Args:
            repo_identifier: The local path to the repository.

        Returns:
            A dictionary with repository file contents, or None if the path is invalid.
        """
        logger.info(f"Attempting to get repository data from filesystem: {repo_identifier}")
        collected_data = repo_data_collector.collect_repository_data(repo_identifier)
        
        return None if collected_data.get("error") else collected_data