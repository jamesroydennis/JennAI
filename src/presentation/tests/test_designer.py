"""
Test suite for the DESIGNER persona's work.

This file contains tests that verify the integrity and correctness of the
brand assets injected into a constructed presentation layer. It acts as the
OBSERVER, performing a "reverse test of expectations" by checking the final state
of the application against the ARCHITECT's design blueprint.
"""
import pytest
import filecmp
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This ensures we can import from 'admin' and 'config' to access blueprints.
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the DESIGNER's blueprint (the TARGETS dictionary).
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT
from admin.presentation_utils import get_platform_paths

PLATFORM_PATHS = get_platform_paths()

# --- Test Data Generation ---
def generate_designer_test_cases():
    """
    The OBSERVER generates its test cases by inspecting the ARCHITECT's blueprint
    for the DESIGNER.
    """
    cases = []
    for platform_name, blueprint in DESIGNER_BLUEPRINT.items():
        # First, check if the platform has been constructed. If not, there's nothing to observe.
        platform_root = PLATFORM_PATHS.get(platform_name)
        if not platform_root or not platform_root.exists():
            continue

        # Get the destination directories from the blueprint, just like the DESIGNER's script does.
        img_dir = blueprint.get("img_dir")
        css_dir = blueprint.get("css_dir")
        text_dir = blueprint.get("text_dir")

        for src_path, dest_name in blueprint.get("asset_map", {}).items():
            # Replicate the destination logic from inject_brand_assets.py
            if dest_name.endswith(('.scss', '.css')):
                dest_dir = css_dir
            elif dest_name.endswith(('.txt', '.md')):
                dest_dir = text_dir
            else: # Default to image directory
                dest_dir = img_dir

            if dest_dir:
                dest_path = dest_dir / dest_name
                test_id = f"DESIGNER-{platform_name}-{dest_name}"
                cases.append(pytest.param(src_path, dest_path, id=test_id))
    return cases


@pytest.mark.parametrize("src_path, dest_path", generate_designer_test_cases())
def test_designer_asset_injection_is_correct(src_path, dest_path):
    """
    OBSERVER TEST: Verifies that a constructed asset (the design) matches the
    original asset from the brand blueprint (the architecture).
    """
    assert dest_path.exists(), f"Critique failed: Designer did not place asset at expected location '{dest_path}'."
    assert src_path.exists(), f"Critique failed: Architectural blueprint asset is missing from '{src_path}'."

    # The core critique: comparing the final product to the blueprint byte-by-byte.
    assert filecmp.cmp(src_path, dest_path, shallow=False), \
        f"Critique failed: Design asset '{dest_path}' does not match architectural blueprint '{src_path}'."