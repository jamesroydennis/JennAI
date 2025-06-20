# /home/jdennis/Projects/JennAI/src/data/implementations/ai_analysis_result_sqlite_repository.py

import json
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
from src.data.obj.ai_analysis_result_dto import AIAnalysisResultDTO
from config.loguru_setup import logger

class AIAnalysisResultSQLiteRepository(SQLiteRepository[AIAnalysisResultDTO]):
    """
    SQLite repository specific to AIAnalysisResultDTO.
    Handles JSON serialization/deserialization for dictionary fields.
    """

    JSON_FIELDS = ["parsed_system_requirements_json", "parsed_dependencies_json"]

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_name="ai_analysis_results", pk_column="result_id")

    def _entity_to_dict(self, item: AIAnalysisResultDTO) -> Dict[str, Any]:
        data = asdict(item)
        for field_name in self.JSON_FIELDS:
            if field_name in data and data[field_name] is not None and not isinstance(data[field_name], str):
                try:
                    data[field_name] = json.dumps(data[field_name])
                except TypeError as e:
                    logger.error(f"Error serializing field '{field_name}' to JSON for AIAnalysisResultDTO: {e}. Value: {data[field_name]}")
                    data[field_name] = None # Or some error indicator
        return data

    def _row_to_entity(self, row: sqlite3.Row) -> AIAnalysisResultDTO:
        data = dict(row)
        for field_name in self.JSON_FIELDS:
            if field_name in data and isinstance(data[field_name], str):
                # No need to parse here, DTO expects string for these JSON fields
                pass # The DTO itself stores these as Optional[str]
        return AIAnalysisResultDTO(**data)