# /home/jdennis/Projects/JennAI/src/data/obj/ai_analysis_result_dto.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class AIAnalysisResultDTO:
    """
    Data Transfer Object for storing the result from an AI analysis.
    Maps to the 'ai_analysis_results' table.
    """
    prompt_id: int # Foreign key to GeneratedPromptDTO.prompt_id
    ai_response_raw: str
    response_timestamp: str # ISO 8601 string

    # Store parsed structured data as JSON strings
    parsed_system_requirements_json: Optional[str] = None
    parsed_dependencies_json: Optional[str] = None

    result_id: Optional[int] = None # Primary Key, auto-generated

    def __post_init__(self):
        if not self.response_timestamp:
            self.response_timestamp = datetime.utcnow().isoformat()