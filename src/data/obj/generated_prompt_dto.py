# /home/jdennis/Projects/JennAI/src/data/obj/generated_prompt_dto.py

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class GeneratedPromptDTO:
    """
    Data Transfer Object for a generated prompt sent to an AI service.
    Maps to the 'generated_prompts' table.
    """
    session_id: int  # Foreign key to AnalysisSessionDTO.session_id
    prompt_content: str
    prompt_type: str # e.g., "min_sys_reqs_determination", "dependency_resolution"
    creation_timestamp: str # ISO 8601 string
    template_name_used: Optional[str] = None

    prompt_id: Optional[int] = None # Primary Key, auto-generated

    def __post_init__(self):
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.utcnow().isoformat()