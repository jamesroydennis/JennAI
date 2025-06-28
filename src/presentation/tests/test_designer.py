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
import subprocess

# --- Root Project Path Setup (CRITICAL for Imports) ---
# This ensures we can import from 'admin' and 'config' to access blueprints.
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the DESIGNER's blueprint (the TARGETS dictionary).
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT
from admin.compile_scss import COMPILE_TARGETS
from admin.presentation_utils import get_platform_paths
from config import config

PLATFORM_PATHS = get_platform_paths()


def test_designer_prerequisite_brand_directory_exists():
    """
    OBSERVER-DESIGNER TEST: Verifies that the core brand directory, which is the
    source of all design assets, actually exists. This is a fundamental prerequisite
    for any design work.
    """
    assert config.BRAND_DIR.exists(), \
        f"Critique failed: The Designer's source of truth, the brand directory, is missing at '{config.BRAND_DIR}'."
    assert config.BRAND_DIR.is_dir(), \
        f"Critique failed: The path for the brand directory '{config.BRAND_DIR}' exists but is not a directory."

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


@pytest.fixture
def scss_compilation_env(request):
    """
    A fixture that prepares the environment for an SCSS compilation test.
    It receives the platform_name and target_config from the test parameterization,
    ensures the destination file is deleted before the test, and cleans up after.
    """
    platform_name = request.param["platform_name"]
    target_config = request.param["target_config"]
    dest_path = target_config["dest"]

    # Setup: ensure the destination file doesn't exist to guarantee a fresh compilation.
    if dest_path.exists():
        dest_path.unlink()

    yield platform_name, dest_path  # Provide the test function with what it needs.

    # Teardown: clean up the generated file after the test runs.
    if dest_path.exists():
        dest_path.unlink()

def generate_scss_compile_test_cases():
    """
    Generates test cases for the SCSS compilation script.
    Only creates tests for platforms that are installed and have a source SCSS file.
    """
    cases = []
    for platform_name, target_config in COMPILE_TARGETS.items():
        platform_root = PLATFORM_PATHS.get(platform_name)
        src_path = target_config.get("src")
        if platform_root and platform_root.exists() and src_path and src_path.exists():
            test_id = f"DESIGNER-compile-scss-{platform_name}"
            param_data = {"platform_name": platform_name, "target_config": target_config}
            cases.append(pytest.param(param_data, id=test_id))
    return cases

@pytest.mark.parametrize("scss_compilation_env", generate_scss_compile_test_cases(), indirect=True)
def test_designer_can_compile_scss(scss_compilation_env):
    """
    OBSERVER-DESIGNER TEST: Verifies that the Designer's `compile_scss.py`
    script correctly compiles a source SCSS file into a non-empty CSS file.
    """
    platform_name, dest_path = scss_compilation_env
    script_path = ROOT / "admin" / "compile_scss.py"
    command = [sys.executable, str(script_path), "--target", platform_name]

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, f"SCSS compilation script failed for target '{platform_name}'. Stderr:\n{result.stderr}"

    assert dest_path.exists(), f"Critique failed: SCSS compilation did not create the expected output file at '{dest_path}'."
    assert dest_path.stat().st_size > 0, f"Critique failed: SCSS compilation produced an empty file at '{dest_path}'."