# /home/jdennis/Projects/JennAI/src/data/implementations/system_profile_sqlite_repository.py

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, Optional
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
    Handles JSON serialization/deserialization for dictionary fields.
    """

    JSON_FIELDS = ["os_info", "cpu_info", "ram_info", "gpu_info", "disk_info", "python_info"]

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_name="system_profiles", pk_column="profile_id")
        # The table creation SQL should be defined and executed elsewhere,
        # e.g., in datadesign.ipynb or a dedicated setup script.
        # For example:
        # create_sql = """
        # CREATE TABLE IF NOT EXISTS system_profiles (
        #     profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #     session_id INTEGER NOT NULL,
        #     profile_timestamp TEXT NOT NULL,
        #     os_info TEXT,
        #     cpu_info TEXT,
        #     ram_info TEXT,
        #     gpu_info TEXT,
        #     disk_info TEXT,
        #     python_info TEXT,
        #     FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
        # );"""
        # self._create_table_if_not_exists(create_sql) # Call this if repo is responsible for table creation

    def _entity_to_dict(self, item: SystemProfileDTO) -> Dict[str, Any]:
        """
        Converts a SystemProfileDTO to a dictionary, serializing specified fields to JSON strings.
        """
        data = asdict(item) # Convert dataclass to dict
        for field_name in self.JSON_FIELDS:
            if field_name in data and data[field_name] is not None:
                try:
                    data[field_name] = json.dumps(data[field_name])
                except TypeError as e:
                    logger.error(f"Error serializing field '{field_name}' to JSON for SystemProfileDTO: {e}. Value: {data[field_name]}")
                    # Decide handling: raise error, log and skip, or store as None/error string
                    data[field_name] = None # Or some error indicator
        return data

    def _row_to_entity(self, row: sqlite3.Row) -> SystemProfileDTO:
        """
        Converts a database row to a SystemProfileDTO, deserializing JSON strings from specified fields.
        """
        data = dict(row) # Convert sqlite3.Row to dict
        for field_name in self.JSON_FIELDS:
            if field_name in data and isinstance(data[field_name], str): # Check if it's a string to deserialize
                try:
                    data[field_name] = json.loads(data[field_name])
                except json.JSONDecodeError as e:
                    logger.error(f"Error deserializing field '{field_name}' from JSON for SystemProfileDTO: {e}. Value: {data[field_name]}")
                    # Decide handling: raise error, log and return None for field, or return DTO with raw string
                    data[field_name] = None # Or keep raw string / error indicator
        
        # Ensure all fields expected by SystemProfileDTO are present, even if None
        return SystemProfileDTO(**data)