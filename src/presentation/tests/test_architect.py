"""
Test suite for the ARCHITECT persona.

This file contains tests that verify the ARCHITECT's high-level plans and
blueprints are consistent and correctly configured.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the ARCHITECT's master plan (config)
# and the various blueprints it defines.
from config import config
from config.config import ROOT  # Import ROOT from config instead of redefining
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT
from conftest import SCOPES
from config.config import ArchitecturalPersona
from src.presentation.tests.presentation_test_utils import load_attribute_from_script

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
def test_architect_ensures_constructor_can_build_all_platforms():
    """
    OBSERVER-ARCHITECT TEST: Verifies that for every presentation platform
    defined by the ARCHITECT, a corresponding 'create_presentation_<platform>.py'
    script exists for the CONSTRUCTOR to use.
    """
    missing_scripts = []
    admin_dir = config.ROOT / "admin"
    for platform_name in config.PRESENTATION_APPS.keys():
        # The 'console' platform is abstract and doesn't have a creation script.
        if platform_name == "console":
            continue
        expected_script = admin_dir / f"create_presentation_{platform_name}.py"
        if not expected_script.exists():
            missing_scripts.append(expected_script.name)
    assert not missing_scripts, f"Critique failed: The Architect's plan includes platforms that are missing their construction scripts in 'admin/'.\nMissing scripts for: {sorted(missing_scripts)}"