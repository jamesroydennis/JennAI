# /home/jdennis/Projects/JennAI/src/data/obj/system_profile_dto.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class SystemProfileDTO:
    """
    Data Transfer Object for a system hardware/software profile.
    Maps to the 'system_profiles' table in the database.
    The fields like os_info, cpu_info, etc., are expected to store
    JSON-compatible dictionary structures, which will be serialized to TEXT
    in the SQLite database.
    """
    session_id: int  # Foreign key linking to AnalysisSessionDTO.session_id
    profile_timestamp: str # Store as ISO 8601 string

    os_info: Optional[Dict[str, Any]] = None
    cpu_info: Optional[Dict[str, Any]] = None
    ram_info: Optional[Dict[str, Any]] = None
    gpu_info: Optional[Dict[str, Any]] = None # Could be a dict with a list of GPUs
    disk_info: Optional[Dict[str, Any]] = None
    python_info: Optional[Dict[str, Any]] = None

    # Primary key, will be set by the database upon creation (AUTOINCREMENT)
    profile_id: Optional[int] = None

    @classmethod
    def new_profile(cls, session_id: int, profile_data: Dict[str, Any]) -> 'SystemProfileDTO':
        """
        Factory method to create a new system profile from collected data.
        """
        return cls(session_id=session_id, profile_timestamp=datetime.utcnow().isoformat(), **profile_data)