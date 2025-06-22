# /home/jdennis/Projects/JennAI/src/data/obj/system_profile_dto.py

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class SystemProfileDTO:
    """
    Data Transfer Object for a system hardware/software profile, stored as a single JSON blob.
    Maps to the 'system_profiles' table in the database.
    """
    session_id: int  # Foreign key linking to AnalysisSessionDTO.session_id
    profile_timestamp: str # Store as ISO 8601 string
    profile_data: str # The full JSON string of the system profile

    # Primary key, will be set by the database upon creation (AUTOINCREMENT)
    profile_id: Optional[int] = None