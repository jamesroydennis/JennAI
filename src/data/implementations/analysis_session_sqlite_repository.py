# /home/jdennis/Projects/JennAI/src/data/implementations/analysis_session_sqlite_repository.py

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
from src.data.obj.analysis_session_dto import AnalysisSessionDTO
from config.loguru_setup import logger

class AnalysisSessionSQLiteRepository(SQLiteRepository[AnalysisSessionDTO]):
    """
    SQLite repository specific to AnalysisSessionDTO.
    """

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_name="analysis_sessions", pk_column="session_id")
        # Table creation is handled by datadesign.ipynb or a setup script.

    def _entity_to_dict(self, item: AnalysisSessionDTO) -> Dict[str, Any]:
        # The default asdict from dataclasses should work fine here.
        return asdict(item)

    def _row_to_entity(self, row: sqlite3.Row) -> AnalysisSessionDTO:
        # Convert sqlite3.Row to a dictionary and then unpack into the DTO.
        return AnalysisSessionDTO(**dict(row))