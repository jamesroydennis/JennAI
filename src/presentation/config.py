"""
Configuration specific to the Presentation Layer.

This file contains settings, enums, and constants that are only relevant
to the development, testing, and management of the UI/presentation components.
"""
from enum import Enum, auto

class PresentationPersona(Enum):
    """
    Defines the roles involved in the presentation layer's development lifecycle.
    """
    MANAGER = auto()      # The orchestrator using the admin console.
    CONSTRUCTOR = auto()  # The developer scaffolding the application framework.
    DESIGNER = auto()     # The designer applying the brand and theme.