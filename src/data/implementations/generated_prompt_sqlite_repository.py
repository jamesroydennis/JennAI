# /home/jdennis/Projects/JennAI/src/data/implementations/generated_prompt_sqlite_repository.py

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
from src.data.obj.generated_prompt_dto import GeneratedPromptDTO
from config.loguru_setup import logger

class GeneratedPromptSQLiteRepository(SQLiteRepository[GeneratedPromptDTO]):
    """
    SQLite repository specific to GeneratedPromptDTO.
    """

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, table_name="generated_prompts", pk_column="prompt_id")

    def _entity_to_dict(self, item: GeneratedPromptDTO) -> Dict[str, Any]:
        return asdict(item)

    def _row_to_entity(self, row: sqlite3.Row) -> GeneratedPromptDTO:
        return GeneratedPromptDTO(**dict(row))