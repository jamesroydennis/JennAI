# /home/jdennis/Projects/JennAI/src/business/interfaces/IRepositoryDataSource.py

from abc import ABC, abstractmethod
from typing import Dict, Optional

class IRepositoryDataSource(ABC):
    """
    Interface for services that provide repository data.
    This abstracts the source of the repository information, whether it's
    from a live filesystem, a database, or a remote git repository.
    """
    @abstractmethod
    def get_repository_data(self, repo_identifier: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Retrieves key file contents from a repository.

        Args:
            repo_identifier: A string that identifies the repository (e.g., a local path, a URL).

        Returns:
            A dictionary containing the content of key files (e.g., readme_content),
            or None if the repository cannot be accessed.
        """
        raise NotImplementedError