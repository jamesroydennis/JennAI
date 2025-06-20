# /home/jdennis/Projects/JennAI/src/data/obj/repository_snapshot_dto.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RepositorySnapshotDTO:
    """
    Data Transfer Object for a snapshot of repository files.
    Maps to the 'repository_snapshots' table in the database.
    """
    session_id: int  # Foreign key linking to AnalysisSessionDTO.session_id
    
    # Content of the files. Optional because a file might not exist in the repo.
    readme_content: Optional[str] = None
    requirements_txt_content: Optional[str] = None
    environment_yaml_content: Optional[str] = None
    existing_min_sys_reqs_content: Optional[str] = None
    
    # Primary key, will be set by the database upon creation (AUTOINCREMENT)
    snapshot_id: Optional[int] = None

    # No __post_init__ or factory method needed for this simple DTO for now,
    # as instances will likely be created directly with data from repo_data_collector.