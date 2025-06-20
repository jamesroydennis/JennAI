# /home/jdennis/Projects/JennAI/src/data/obj/analysis_session_dto.py

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class AnalysisSessionDTO:
    """
    Data Transfer Object for an analysis session.
    Maps to the 'analysis_sessions' table in the database.
    """
    target_repository_identifier: str
    analysis_timestamp: str  # Store as ISO 8601 string for SQLite compatibility
    status: str = "pending"  # Default status
    user_notes: Optional[str] = None
    session_id: Optional[int] = None # Will be set by the database upon creation (AUTOINCREMENT)

    def __post_init__(self):
        # Ensure analysis_timestamp is set if not provided (though it's not optional in constructor)
        if not self.analysis_timestamp:
            self.analysis_timestamp = datetime.utcnow().isoformat()

    @classmethod
    def new_session(cls, target_repo_id: str, notes: Optional[str] = None) -> 'AnalysisSessionDTO':
        """
        Factory method to create a new session with the current timestamp.
        """
        return cls(
            target_repository_identifier=target_repo_id,
            analysis_timestamp=datetime.utcnow().isoformat(),
            user_notes=notes
        )