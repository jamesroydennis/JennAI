# /home/jdennis/Projects/JennAI/src/data/implementations/system_profile_sqlite_repository.py

import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any
from dataclasses import asdict

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.data.implementations.sqlite_repository import SQLiteRepository
from src.data.obj.system_profile_dto import SystemProfileDTO
from config.loguru_setup import logger

class SystemProfileSQLiteRepository(SQLiteRepository[SystemProfileDTO]):
    """
    SQLite repository specific to SystemProfileDTO.
    """

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_name="system_profiles", pk_column="profile_id")

    def _entity_to_dict(self, item: SystemProfileDTO) -> Dict[str, Any]:
        """
        Converts a SystemProfileDTO to a dictionary for database insertion/update.
        """
        return asdict(item)

    def _row_to_entity(self, row: sqlite3.Row) -> SystemProfileDTO:
        """
        Converts a database row to a SystemProfileDTO.
        """
        return SystemProfileDTO(**dict(row))