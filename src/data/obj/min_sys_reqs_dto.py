# /home/jdennis/Projects/JennAI/src/data/obj/min_sys_reqs_dto.py
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class MinSysReqsDTO(BaseModel):
    """
    A Pydantic Data Transfer Object for representing the minimum system requirements
    parsed from an AI's response. This structure serves as the schema for validation.
    """
    cpu_cores: int = Field(
        ...,
        description="The minimum number of CPU cores required.",
        gt=0 # Must be a positive integer
    )
    ram_gb: float = Field(
        ...,
        description="The minimum amount of RAM in gigabytes (GB).",
        gt=0.0 # Must be a positive float
    )
    storage_gb: float = Field(
        ...,
        description="The minimum amount of free storage space in gigabytes (GB).",
        gt=0.0 # Must be a positive float
    )
    operating_system: Optional[List[str]] = Field(
        default=None,
        description="A list of compatible operating systems (e.g., ['Windows 10', 'Ubuntu 20.04'])."
    )
    dependencies: Optional[List[str]] = Field(
        default=None,
        description="A list of required software dependencies or libraries (e.g., ['python>=3.8', 'cuda==11.8'])."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Any additional notes or context provided by the AI regarding the requirements."
    )

    # Pydantic model configuration using ConfigDict (Pydantic V2+)
    # `extra = 'forbid'` prevents unexpected fields in the JSON from being silently ignored,
    # ensuring the AI's output strictly matches our schema.
    model_config = ConfigDict(extra='forbid', json_schema_extra={
        "example": {
            "cpu_cores": 4,
            "ram_gb": 8.0,
            "storage_gb": 20.5,
            "operating_system": ["Windows 10", "Ubuntu 20.04", "macOS Big Sur"],
            "dependencies": ["python>=3.9", "pytorch==2.1", "cuda==11.8"],
            "notes": "A dedicated GPU with at least 6GB of VRAM is highly recommended for optimal performance."
        }
    })