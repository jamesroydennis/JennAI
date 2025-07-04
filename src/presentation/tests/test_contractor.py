"""
Test suite for the CONTRACTOR persona.

This file contains tests that verify the CONTRACTOR's ability to correctly
orchestrate and manage the various presentation platforms. It ensures that the
CONTRACTOR's tools and configurations are in sync with the ARCHITECT's master plan.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the ARCHITECT's master plan (config)
# and the CONTRACTOR's testing configuration (conftest).
from config import config
from config.config import ROOT  # Import ROOT from config instead of redefining
from conftest import SCOPES
from config.config import ArchitecturalPersona
from admin.inject_brand_assets import TARGETS as DESIGNER_BLUEPRINT
from admin.compile_scss import COMPILE_TARGETS
from admin.presentation_utils import get_presentation_apps
import subprocess
import re


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
    platform_paths = get_presentation_apps()
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
    script_path = config.ROOT / "admin" / "compile_scss.py"
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
    missing_dirs = {str(d.relative_to(config.ROOT)) for d in dependency_info["required_dirs"]} - {str(d.relative_to(config.ROOT)) for d in dependency_info["constructor_created_dirs"]}
    assert not missing_dirs, f"Critique failed: The Contractor found that the CONSTRUCTOR for '{dependency_info['platform_name']}' does not create all the directories required by the DESIGNER.\nMissing directories:\n" + "\n".join(sorted(list(missing_dirs)))

def test_contractor_brand_compilation_validation():
    """
    CONTRACTOR TEST: Critical validation that brand SCSS is compiled to CSS.
    
    This test ensures the CONTRACTOR fulfills their core responsibility:
    - SCSS files from brand directory must be compiled to CSS
    - CSS files must exist and be accessible to the presentation app
    - Brand implementation must be complete and functional
    
    FAILURE INDICATES: Contractor has not ensured brand is properly applied.
    """
    all_platform_paths = get_presentation_apps()
    
    for platform_name, platform_info in config.PRESENTATION_APPS.items():
        if platform_name == 'console':  # Console doesn't use CSS
            continue
            
        # Get the platform base path
        platform_base = all_platform_paths.get(platform_name)
        if not platform_base:
            continue
            
        css_dir = platform_base / 'static' / 'css'
        
        # Check if SCSS files exist (Designer should have injected them)
        scss_file = css_dir / 'main.scss'
        css_file = css_dir / 'main.css'
        
        if scss_file.exists():
            # If SCSS exists, CSS MUST exist (Contractor responsibility)
            assert css_file.exists(), \
                f"CONTRACTOR FAILURE for {platform_name}: " \
                f"SCSS file exists at {scss_file} but CSS file is missing at {css_file}. " \
                f"The Contractor must ensure SCSS is compiled to CSS."
            
            # CSS file must not be empty
            css_content = css_file.read_text()
            assert len(css_content.strip()) > 0, \
                f"CONTRACTOR FAILURE for {platform_name}: " \
                f"CSS file at {css_file} is empty. " \
                f"The Contractor must ensure SCSS compilation produces valid CSS."
            
            # CSS must contain brand colors (basic validation)
            assert '#87CEEB' in css_content or 'rgb(135, 206, 235)' in css_content, \
                f"CONTRACTOR FAILURE for {platform_name}: " \
                f"CSS file at {css_file} does not contain brand colors. " \
                f"The Contractor must ensure brand theme is properly compiled."


def test_contractor_brand_content_integration():
    """
    CONTRACTOR TEST: Validates that brand content files are integrated into templates.
    
    This test ensures the CONTRACTOR verifies:
    - Mission, vision, problem statement are accessible to the app
    - Brand images and assets are properly linked
    - Templates reference brand content correctly
    """
    all_platform_paths = get_presentation_apps()
    
    for platform_name, platform_info in config.PRESENTATION_APPS.items():
        if platform_name == 'console':  # Console doesn't use templates
            continue

        # Get the platform base path
        platform_base = all_platform_paths.get(platform_name)
        if not platform_base:
            continue

        # Check that brand content files exist
        brand_dir = config.BRAND_DIR
        mission_file = brand_dir / 'mission.txt'
        vision_file = brand_dir / 'vision.md'
        
        if mission_file.exists() and vision_file.exists():
            # Templates should reference these files or load their content
            templates_dir = platform_base / 'templates'
            if templates_dir.exists():
                template_files = list(templates_dir.glob('*.html'))
                # At least one template should exist if brand content is available
                assert len(template_files) > 0, \
                    f"CONTRACTOR FAILURE for {platform_name}: " \
                    f"Brand content exists but no templates found in {templates_dir}."


def test_contractor_creates_contract_when_all_validations_pass():
    """
    CONTRACTOR TEST: Contract creation when all validation steps pass.
    
    This test validates the core contractor workflow:
    1. When brand assets are injected ✅
    2. When SCSS is compiled to CSS ✅ 
    3. When all brand requirements are validated ✅
    4. When compliance enforcement passes ✅
    5. THEN a formal contract MUST be created ✅
    
    FAILURE INDICATES: Contractor has not created required contract documentation.
    """
    all_platform_paths = get_presentation_apps()
    
    for platform_name, platform_info in config.PRESENTATION_APPS.items():
        if platform_name == 'console':  # Console doesn't use CSS contracts
            continue
            
        platform_base = all_platform_paths.get(platform_name)
        if not platform_base:
            continue
            
        # Step 1: Check if brand assets are injected (Designer's work)
        css_dir = platform_base / 'static' / 'css'
        scss_file = css_dir / 'main.scss'
        
        # Step 2: Check if SCSS is compiled to CSS (Designer's work)  
        css_file = css_dir / 'main.css'
        
        # Step 3: Check if brand requirements are met
        templates_dir = platform_base / 'templates'
        base_template = templates_dir / 'base.html'
        
        # Only proceed with contract validation if all prerequisites are met
        if (scss_file.exists() and 
            css_file.exists() and 
            css_file.stat().st_size > 0 and
            base_template.exists()):
            
            # Step 4: Verify CSS contains brand colors (validation)
            css_content = css_file.read_text()
            brand_colors_present = ('#87CEEB' in css_content or 
                                 'rgb(135, 206, 235)' in css_content)
            
            # Step 5: Verify templates reference CSS correctly (enforcement)
            template_content = base_template.read_text()
            css_linked = 'main.css' in template_content
            
            # IF ALL VALIDATIONS PASS, CONTRACTOR MUST CREATE CONTRACT
            if brand_colors_present and css_linked:
                # Contract file should exist
                contracts_dir = config.PRESENTATION_DIR / 'contracts'
                contract_file = contracts_dir / f'{platform_name}-brand-contract.md'
                
                assert contract_file.exists(), \
                    f"CONTRACTOR FAILURE for {platform_name}: " \
                    f"All validations passed (assets injected ✅, SCSS compiled ✅, " \
                    f"brand colors present ✅, CSS linked ✅) but NO CONTRACT created. " \
                    f"Expected contract at: {contract_file}"
                
                # Contract must not be empty
                contract_content = contract_file.read_text()
                assert len(contract_content.strip()) > 0, \
                    f"CONTRACTOR FAILURE for {platform_name}: " \
                    f"Contract exists at {contract_file} but is empty."
                
                # Contract must contain essential elements
                assert 'BRAND IMPLEMENTATION CONTRACT' in contract_content, \
                    f"CONTRACTOR FAILURE for {platform_name}: " \
                    f"Contract at {contract_file} missing required header."
                
                assert platform_name in contract_content.lower(), \
                    f"CONTRACTOR FAILURE for {platform_name}: " \
                    f"Contract at {contract_file} doesn't specify platform."
                
                assert 'VALIDATED' in contract_content or 'PASSED' in contract_content, \
                    f"CONTRACTOR FAILURE for {platform_name}: " \
                    f"Contract at {contract_file} doesn't show validation status."


def test_contractor_scaffold_validation():
    """
    CONTRACTOR VALIDATION: Verifies that presentation app scaffolding meets requirements.

    This test validates that the basic structure and required files are in place
    for each platform, ensuring scaffold compliance with architectural contracts.
    """
    validation_failures = []
    all_platform_paths = get_presentation_apps()

    for platform_name, platform_config in config.PRESENTATION_APPS.items():
        platform_base = all_platform_paths.get(platform_name)
        if not platform_base:
            continue
        
        # Check if platform directory exists
        if not platform_base.exists():
            validation_failures.append(f"{platform_name}: Directory does not exist at {platform_base}")
            continue
        
        # Check for required platform-specific files
        required_files = []
        if platform_name == "flask":
            required_files = ["app.py", "static", "templates"]
        elif platform_name == "angular":
            required_files = ["package.json", "src", "angular.json"]
        elif platform_name == "react":
            required_files = ["package.json", "src", "public"]
        elif platform_name == "vue":
            required_files = ["package.json", "src", "public"]
            
        for required_file in required_files:
            file_path = platform_base / required_file
            if not file_path.exists():
                validation_failures.append(f"{platform_name}: Missing required file/directory: {required_file}")
    
    assert not validation_failures, \
        f"CONTRACTOR VALIDATION FAILURE: Scaffold validation failed:\n" + \
        "\n".join(f"  - {failure}" for failure in validation_failures)

def test_contractor_brand_compliance():
    """
    CONTRACTOR VALIDATION: Verifies that brand assets are properly integrated.

    This test validates that all platforms have the required brand assets
    in place and properly referenced, ensuring brand compliance contracts.
    """
    validation_failures = []
    all_platform_paths = get_presentation_apps()

    for platform_name, platform_config in config.PRESENTATION_APPS.items():
        platform_base = all_platform_paths.get(platform_name)
        if not platform_base:
            continue
        
        if not platform_base.exists():
            validation_failures.append(f"{platform_name}: Platform not scaffolded")
            continue
        
        # Check for brand assets integration
        if platform_name == "flask":
            # Check for static assets
            static_dir = platform_base / "static"
            if static_dir.exists():
                # Check for favicon
                if not (static_dir / "favicon.ico").exists():
                    validation_failures.append(f"{platform_name}: Missing favicon.ico in static directory")
                
                # Check for logo in images
                images_dir = static_dir / "images"
                if images_dir.exists():
                    logo_files = list(images_dir.glob("logo.*"))
                    if not logo_files:
                        validation_failures.append(f"{platform_name}: Missing logo file in static/images")
                else:
                    validation_failures.append(f"{platform_name}: Missing static/images directory")
            else:
                validation_failures.append(f"{platform_name}: Missing static directory")
    
    assert not validation_failures, \
        f"CONTRACTOR VALIDATION FAILURE: Brand compliance validation failed:\n" + \
        "\n".join(f"  - {failure}" for failure in validation_failures)

def test_contractor_asset_integration():
    """
    CONTRACTOR VALIDATION: Verifies that assets are properly integrated into templates.

    This test validates that brand assets are not only present but also
    properly referenced in the application templates and configurations.
    """
    validation_failures = []
    all_platform_paths = get_presentation_apps()

    for platform_name, platform_config in config.PRESENTATION_APPS.items():
        platform_base = all_platform_paths.get(platform_name)
        if not platform_base:
            continue
        
        if not platform_base.exists():
            validation_failures.append(f"{platform_name}: Platform not scaffolded")
            continue
        
        # Platform-specific asset integration checks
        if platform_name == "flask":
            # Check if templates reference the favicon
            templates_dir = platform_base / "templates"
            if templates_dir.exists():
                template_files = list(templates_dir.glob("*.html"))
                favicon_referenced = False
                logo_referenced = False
                
                for template_file in template_files:
                    try:
                        content = template_file.read_text(encoding='utf-8')
                        if "favicon.ico" in content:
                            favicon_referenced = True
                        if "logo" in content.lower():
                            logo_referenced = True
                    except Exception as e:
                        validation_failures.append(f"{platform_name}: Error reading template {template_file.name}: {e}")
                
                if not favicon_referenced:
                    validation_failures.append(f"{platform_name}: Favicon not referenced in templates")
                if not logo_referenced:
                    validation_failures.append(f"{platform_name}: Logo not referenced in templates")
            else:
                validation_failures.append(f"{platform_name}: Missing templates directory")
    
    assert not validation_failures, \
        f"CONTRACTOR VALIDATION FAILURE: Asset integration validation failed:\n" + \
        "\n".join(f"  - {failure}" for failure in validation_failures)