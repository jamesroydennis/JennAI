"""
Test suite for the CONTRACTOR persona.

This file contains tests that verify the CONTRACTOR's ability to correctly
orchestrate and manage the various presentation platforms. It ensures that the
CONTRACTOR's tools and configurations are in sync with the ARCHITECT's master plan.
"""
import pytest
from pathlib import Path
import sys
import subprocess
import re

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the ARCHITECT's master plan (config)
# and the CONTRACTOR's testing configuration (conftest).
from config import config
from conftest import SCOPES
from config.config import ArchitecturalPersona
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT
from admin.compile_scss import COMPILE_TARGETS
from admin.presentation_utils import get_platform_paths

def test_contractor_has_test_scope_for_every_platform():
    """
    OBSERVER-CONTRACTOR TEST: Verifies that for every presentation platform
    defined by the ARCHITECT (in config.py), the CONTRACTOR has a corresponding
    test scope defined (in conftest.py).

    This ensures that the 'Test' command in the presentation console will work
    for every supported platform.
    """
    missing_scopes = []
    for platform_name in config.PRESENTATION_APPS.keys():
        # This enforces the convention for naming platform-specific test scopes.
        expected_scope_name = f"{platform_name.upper()}_PRESENTATION"
        if expected_scope_name not in SCOPES:
            missing_scopes.append(platform_name)

    assert not missing_scopes, \
        f"Critique failed: The Contractor's testing configuration (conftest.py) is missing " \
        f"test scopes for the following platforms defined by the Architect: {missing_scopes}.\n" \
        f"Please add a '{'<PLATFORM>'.upper()}_PRESENTATION' entry to the SCOPES dictionary in conftest.py."

def _generate_constructor_reqs_test_cases():
    """
    Generates test cases for each constructor script found in the admin directory.
    This provides the parameterization for the requirements verification test.
    """
    cases = []
    admin_dir = config.ADMIN_DIR
    constructor_scripts = list(admin_dir.glob("create_presentation_*.py"))
    for script in constructor_scripts:
        match = re.search(r"create_presentation_(.+)\.py", script.name)
        if match:
            platform_name = match.group(1)
            test_id = f"CONTRACTOR-constructor-reqs-{platform_name}"
            # Pass both script and platform name for a more detailed assertion message.
            cases.append(pytest.param((script, platform_name), id=test_id))
    return cases

@pytest.mark.parametrize("constructor_info", _generate_constructor_reqs_test_cases())
def test_contractor_verifies_constructor_has_requirements(constructor_info):
    """
    OBSERVER-CONTRACTOR TEST: Verifies that for every CONSTRUCTOR script the
    CONTRACTOR can invoke (i.e., create_presentation_*.py files), a
    corresponding requirements test file (test_*_app.py) exists.
    This ensures the Contractor doesn't offer to build an application that
    has no defined quality contract.
    """
    constructor_script, platform_name = constructor_info
    presentation_tests_dir = config.PRESENTATION_DIR / "tests"
    expected_reqs_file = presentation_tests_dir / f"test_{platform_name}_app.py"
    assert expected_reqs_file.exists(), f"Critique failed: The Contractor found that constructor script '{constructor_script.name}' is missing its requirements file: '{expected_reqs_file.relative_to(ROOT)}'"

def test_contractor_verifies_all_personas_are_testable():
    """
    OBSERVER-CONTRACTOR TEST: Verifies that for every persona the Contractor
    might interact with, a corresponding test file exists. This ensures that
    all roles have defined, verifiable responsibilities before the Contractor
    begins orchestration.
    """
    presentation_tests_dir = config.PRESENTATION_DIR / "tests"
    missing_test_files = []

    for persona in ArchitecturalPersona:
        persona_name = persona.name
        if persona_name == "OBSERVER":
            continue

        if persona_name == "CONSTRUCTOR":
            if not any(presentation_tests_dir.glob("test_constructor_*.py")):
                missing_test_files.append(f"CONSTRUCTOR (expected at least one 'test_constructor_*.py' file)")
        else:
            expected_file = presentation_tests_dir / f"test_{persona_name.lower()}.py"
            if not expected_file.exists():
                missing_test_files.append(f"{persona_name} (expected '{expected_file.relative_to(ROOT)}')")

    assert not missing_test_files, \
        "Critique failed: The Contractor has determined that some personas lack a corresponding test file to define their responsibilities.\n" \
        f"Missing test files for: {', '.join(missing_test_files)}"

def test_contractor_verifies_designer_blueprint_is_valid():
    """
    OBSERVER-CONTRACTOR TEST: Verifies that every entry in the DESIGNER's blueprint
    (inject_brand_assets.py) points to a real, existing source asset. This ensures
    the Contractor doesn't assign a design task that is impossible to complete due
    to missing materials.
    """
    for platform, blueprint in DESIGNER_BLUEPRINT.items():
        for src_path in blueprint.get("asset_map", {}).keys():
            assert src_path.exists(), \
                f"Critique failed: Contractor found that the Designer's blueprint for '{platform}' " \
                f"points to a non-existent source asset: '{src_path}'."

def test_contractor_verifies_all_test_scopes_are_valid():
    """
    OBSERVER-CONTRACTOR TEST: Verifies that every test scope defined in the
    root conftest.py points to valid, existing file paths. This ensures the
    Contractor doesn't try to orchestrate a test run against a misconfigured scope.
    """
    invalid_scope_paths = []
    for scope_name, paths in SCOPES.items():
        if paths is None:  # Skip special cases like 'ROOT'
            continue

        for path_str in paths:
            if not Path(path_str).exists():
                invalid_scope_paths.append(f"Scope '{scope_name}': Path '{path_str}' does not exist.")

    assert not invalid_scope_paths, \
        "Critique failed: The Contractor found invalid paths in the test scope configuration (conftest.py):\n" + "\n".join(invalid_scope_paths)

@pytest.fixture
def contractor_scss_compilation_env(request):
    """
    A fixture that prepares the environment for the Contractor's SCSS compilation check.
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

def generate_contractor_scss_compile_test_cases():
    """
    Generates test cases for the Contractor's verification of the SCSS compilation script.
    Only creates tests for platforms that are installed and have a source SCSS file.
    """
    cases = []
    platform_paths = get_platform_paths()
    for platform_name, target_config in COMPILE_TARGETS.items():
        platform_root = platform_paths.get(platform_name)
        src_path = target_config.get("src")
        if platform_root and platform_root.exists() and src_path and src_path.exists():
            test_id = f"CONTRACTOR-compile-scss-{platform_name}"
            param_data = {"platform_name": platform_name, "target_config": target_config}
            cases.append(pytest.param(param_data, id=test_id))
    return cases

@pytest.mark.parametrize("contractor_scss_compilation_env", generate_contractor_scss_compile_test_cases(), indirect=True)
def test_contractor_verifies_scss_can_be_compiled(contractor_scss_compilation_env):
    """
    OBSERVER-CONTRACTOR TEST: Verifies that the SCSS assets provided by the DESIGNER
    can be successfully compiled. This is a pre-flight check to ensure the project's
    styling is buildable before proceeding with orchestration.
    """
    platform_name, dest_path = contractor_scss_compilation_env
    script_path = ROOT / "admin" / "compile_scss.py"
    command = [sys.executable, str(script_path), "--target", platform_name]

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, f"Contractor's pre-flight check failed: SCSS compilation script failed for target '{platform_name}'. Stderr:\n{result.stderr}"

    assert dest_path.exists(), f"Critique failed: Contractor determined that SCSS compilation for '{platform_name}' did not create the expected output file at '{dest_path}'."
    assert dest_path.stat().st_size > 0, f"Critique failed: Contractor determined that SCSS compilation for '{platform_name}' produced an empty file at '{dest_path}'."

def _generate_platform_test_cases():
    """Generates test cases for each platform defined by the Architect."""
    cases = []
    for platform_name in config.PRESENTATION_APPS.keys():
        test_id = f"CONTRACTOR-verifies-blueprint-{platform_name}"
        cases.append(pytest.param(platform_name, id=test_id))
    return cases

@pytest.mark.parametrize("platform_name", _generate_platform_test_cases())
def test_contractor_verifies_constructor_blueprint_is_complete(platform_name):
    """
    OBSERVER-CONTRACTOR TEST: Verifies that the blueprint for each CONSTRUCTOR
    is complete and well-formed. This is a pre-flight check to ensure the
    Contractor has valid instructions before assigning a build task.
    """
    import importlib

    try:
        module_name = f"admin.create_presentation_{platform_name}"
        module = importlib.import_module(module_name)

        # The Contractor verifies that the blueprint contains all necessary instructions.
        assert hasattr(module, "DEST_ROOT"), f"Blueprint for '{platform_name}' is missing 'DEST_ROOT'."
        assert hasattr(module, "TEMPLATE_MAP"), f"Blueprint for '{platform_name}' is missing 'TEMPLATE_MAP'."
        assert hasattr(module, "DIRECTORIES_TO_CREATE"), f"Blueprint for '{platform_name}' is missing 'DIRECTORIES_TO_CREATE'."

    except ImportError:
        pytest.fail(f"Critique failed: Contractor could not find the blueprint script for '{platform_name}' at 'admin/create_presentation_{platform_name}.py'.")

def _generate_designer_dependency_test_cases():
    """
    Generates test cases to verify that each constructor's blueprint
    fulfills the directory requirements of the designer's blueprint.
    """
    cases = []
    # The designer's blueprint defines what directories are needed per platform.
    for platform_name, designer_blueprint in DESIGNER_BLUEPRINT.items():
        # Collect all unique destination directories the designer needs for this platform.
        required_dirs = {d for d in [designer_blueprint.get("img_dir"), designer_blueprint.get("css_dir"), designer_blueprint.get("text_dir")] if d}

        # The constructor's blueprint defines what directories it will create.
        try:
            import importlib
            module_name = f"admin.create_presentation_{platform_name}"
            constructor_module = importlib.import_module(module_name)
            constructor_created_dirs = constructor_module.DIRECTORIES_TO_CREATE
            
            test_id = f"CONTRACTOR-verifies-designer-deps-{platform_name}"
            param_data = {"platform_name": platform_name, "required_dirs": required_dirs, "constructor_created_dirs": constructor_created_dirs}
            cases.append(pytest.param(param_data, id=test_id))
        except (ImportError, AttributeError):
            continue # Other tests will catch a missing/malformed constructor blueprint.
    return cases

@pytest.mark.parametrize("dependency_info", _generate_designer_dependency_test_cases())
def test_contractor_verifies_constructor_fulfills_designer_needs(dependency_info):
    """
    OBSERVER-CONTRACTOR TEST: Verifies that the CONSTRUCTOR's framework provides
    all the necessary directories that the DESIGNER needs to implement the brand.
    This ensures the "handoff" from constructor to designer is valid.
    """
    missing_dirs = {str(d.relative_to(ROOT)) for d in dependency_info["required_dirs"]} - {str(d.relative_to(ROOT)) for d in dependency_info["constructor_created_dirs"]}
    assert not missing_dirs, f"Critique failed: The Contractor found that the CONSTRUCTOR for '{dependency_info['platform_name']}' does not create all the directories required by the DESIGNER.\nMissing directories:\n" + "\n".join(sorted(list(missing_dirs)))