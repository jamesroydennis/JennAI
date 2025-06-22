# /home/jdennis/Projects/JennAI/src/data/obj/repository_snapshot_dto.py

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class RepositorySnapshotDTO:
    """
    Data Transfer Object for a snapshot of repository file contents, stored as a single JSON blob.
    Maps to the 'repository_snapshots' table in the database.
    creation_timestamp will be stored as an ISO 8601 string.
    """
    session_id: int  # Foreign key linking to AnalysisSessionDTO.session_id
    snapshot_data: str # The full JSON string of the file contents dictionary
    creation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    snapshot_id: Optional[int] = None