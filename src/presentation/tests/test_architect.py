"""
Test suite for the ARCHITECT persona's blueprints.

This file contains tests that act as the OBSERVER at the highest level.
It verifies the integrity and completeness of the blueprints that the
CONTRACTOR, CONSTRUCTOR, and DESIGNER will use. These tests are completely
agnostic to any concrete presentation framework.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the ARCHITECT's master plan (config)
# and the blueprints used by other personas.
from config import config
from admin.presentation_utils import get_platform_paths
import ast
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT


def test_architect_ensures_contractor_is_aware_of_all_platforms():
    """
    OBSERVER-ARCHITECT TEST: Verifies the CONTRACTOR's list of manageable platforms.
    (from admin_utils) matches the official list from the ARCHITECT's configuration.
    This ensures the primary orchestration tool is complete.
    """
    platform_paths = get_platform_paths()
    assert set(config.WEB_APP_NAMES) == set(platform_paths.keys()), \
        "Critique failed: Contractor's platform awareness (get_platform_paths) is out of sync with Architect's configuration (config.WEB_APP_NAMES)."


def test_architect_ensures_designer_has_blueprint_for_all_platforms():
    """
    OBSERVER-ARCHITECT TEST: Verifies that every platform the ARCHITECT has defined.
    in the master plan (config.WEB_APP_NAMES) has a corresponding entry in the
    DESIGNER's blueprint (inject_brand_assets.py).
    """
    missing_blueprints = [name for name in config.WEB_APP_NAMES if name not in DESIGNER_BLUEPRINT]
    assert not missing_blueprints, \
        f"Critique failed: The Designer's blueprint is missing entries for the following platforms defined by the Architect: {missing_blueprints}"


def test_architect_ensures_designer_blueprint_is_valid():
    """
    OBSERVER-ARCHITECT TEST: Verifies the DESIGNER's blueprint (the TARGETS
    dictionary in inject_brand_assets.py) is valid. It checks that every
    source asset file defined in the blueprint actually exists in the brand directory.
    This prevents runtime errors due to typos or missing source files.
    """
    all_source_assets = []
    for platform, blueprint in DESIGNER_BLUEPRINT.items():
        for src_path in blueprint.get("asset_map", {}).keys():
            all_source_assets.append(src_path)

    missing_assets = [path for path in all_source_assets if not path.exists()]
    assert not missing_assets, \
        f"Critique failed: The Designer's blueprint references source assets that do not exist in '{config.BRAND_DIR}':\n" + "\n".join(map(str, missing_assets))
        