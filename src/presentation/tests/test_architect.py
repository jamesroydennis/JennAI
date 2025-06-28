"""
Test suite for the ARCHITECT persona.

This file contains tests that verify the ARCHITECT's high-level plans and
blueprints are consistent and correctly configured.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the ARCHITECT's master plan (config)
# and the various blueprints it defines.
from config import config
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT
from conftest import SCOPES
from config.config import ArchitecturalPersona
from admin.42_present import MENU_HANDLERS


def test_architect_ensures_contractor_is_aware_of_all_platforms():
    """
    OBSERVER-ARCHITECT TEST: Verifies that for every presentation platform
    defined by the ARCHITECT (in config.py), the CONTRACTOR has a corresponding
    test scope defined (in conftest.py).
    """
    missing_scopes = []
    for platform_name in config.PRESENTATION_APPS.keys():
        expected_scope_name = f"{platform_name.upper()}_PRESENTATION"
        if expected_scope_name not in SCOPES:
            missing_scopes.append(platform_name)
    assert not missing_scopes, f"Critique failed: The Contractor's testing configuration (conftest.py) is missing test scopes for the following platforms: {missing_scopes}."

def test_architect_ensures_designer_has_blueprint_for_all_platforms():
    """
    OBSERVER-ARCHITECT TEST: Verifies that for every presentation platform
    defined by the ARCHITECT, a corresponding design blueprint exists in the
    DESIGNER's configuration (inject_brand_assets.py).
    """
    defined_platforms = set(config.PRESENTATION_APPS.keys())
    designed_platforms = set(DESIGNER_BLUEPRINT.keys())
    missing_blueprints = defined_platforms - designed_platforms
    assert not missing_blueprints, f"Critique failed: The Designer's blueprint is missing configurations for the following platforms: {missing_blueprints}."

def test_architect_ensures_designer_blueprint_is_valid():
    """OBSERVER-ARCHITECT TEST: Verifies that every entry in the DESIGNER's blueprint points to a real source asset."""
    for platform, blueprint in DESIGNER_BLUEPRINT.items():
        for src_path in blueprint.get("asset_map", {}).keys():
            assert src_path.exists(), f"Critique failed: Designer blueprint for '{platform}' points to a non-existent source asset: '{src_path}'."

def test_architect_ensures_all_personas_have_a_menu_handler():
    """
    OBSERVER-ARCHITECT TEST: Verifies that every persona defined in the
    architecture has a corresponding menu handler implemented in the main
    presentation console (42_present.py).
    """
    defined_personas = {persona.name for persona in ArchitecturalPersona}
    implemented_handlers = set(MENU_HANDLERS.keys())
    # The 'legacy' view is a special case and not a persona, so it's excluded from the check.
    implemented_handlers.discard("legacy")
    missing_handlers = defined_personas - implemented_handlers
    assert not missing_handlers, f"Critique failed: The Architect's plan includes personas that are missing menu handlers in 'admin/42_present.py'.\nMissing handlers for: {sorted(list(missing_handlers))}"