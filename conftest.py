import os
import sys
from pathlib import Path
from dotenv import load_dotenv  # Import load_dotenv
import platform
import pytest
from typing import Union
import subprocess
# --- Root Project Path Setup (CRITICAL for Imports) ---
# This ensures that conftest.py can import from your project's modules (config, core, etc.)
ROOT = Path(__file__).resolve().parent # conftest.py is in the project root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env file BEFORE importing config
# This ensures DEBUG_MODE and other settings are correctly read.
load_dotenv(dotenv_path=ROOT / ".env")

from config import config as project_config # Import the config module with an alias to avoid name conflicts
from config.loguru_setup import setup_logging, logger
from config.config import DEBUG_MODE

def pytest_configure(config):
    """
    Hook called by pytest after command line options have been parsed
    and before the test collection process starts.
    We use this to first show project context, then set up session-wide logging for test runs.
    """
    # First, show project context using admin/show_context.py
    # This provides comprehensive project state information before test execution
    try:
        show_context_path = ROOT / "admin" / "show_context.py"
        if show_context_path.exists():
            subprocess.run([sys.executable, str(show_context_path)], check=True)
        else:
            print(f"Warning: show_context.py not found at {show_context_path}")
    except (subprocess.CalledProcessError, Exception) as e:
        print(f"Error running show_context.py: {e}")
    
    # The `config` parameter is a pytest object provided by the hook.
    # Setup logging for the test session, directing to a separate file
    # The log level (DEBUG/INFO) will be determined by DEBUG_MODE from config.py
    # Console logging will also respect DEBUG_MODE as per loguru_setup.py logic
    setup_logging(log_file_name="pytest_session.log", debug_mode=DEBUG_MODE)
    logger.info(f"Pytest session logging initialized. Log file: logs/pytest_session.log, DEBUG_MODE: {DEBUG_MODE}")

@pytest.fixture(scope="session")
def app_config():
    """
    Pytest fixture to provide access to the application's configuration module.
    The scope is "session" because the configuration is static and doesn't change
    during a test session, making it efficient to load once.
    """
    return project_config

def _build_dynamic_scopes() -> dict:
    """
    Builds the SCOPES dictionary dynamically from a declarative configuration,
    reducing manual configuration and improving maintainability.
    """
    # --- Declarative Scope Configuration ---

    # 1. Define static scopes.
    STATIC_SCOPES_CONFIG = {
        "ROOT": None,
        "SYSTEM": [os.path.normcase(str(project_config.ROOT / 'tests'))],
        "PRESENTATION": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests'))],
        "DESIGNER_COMPILE": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_designer.py'))],
        "CONSTRUCTOR_BLUEPRINTS": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests'))],
        "PERSONA_CRITIQUES": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests'))],
        "BUSINESS": [os.path.normcase(str(project_config.BUSINESS_DIR / 'tests'))],
        "DATA": [os.path.normcase(str(project_config.DATA_DIR / 'tests'))],
        "VALIDATION": [os.path.normcase(str(project_config.VALIDATION_DIR / 'tests'))],
        "REGRESSION_FULL_LIFECYCLE": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests'))],
    }

    # 2. Define persona-specific scopes for targeted testing in the new admin console.
    # These scopes are designed to test the responsibilities of each architectural persona.
    PERSONA_SCOPES_CONFIG = {
        "ARCHITECT": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_architect.py'))],
        "CONTRACTOR": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_contractor.py'))],
        "DESIGNER": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_designer.py'))],
        "QA_ENGINEER": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_qa_engineer.py'))],
        # CONSTRUCTOR and OBSERVER are special scopes handled by name filtering, not just paths.
        # We still need to provide a base path for initial test collection.
        "CONSTRUCTOR": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests'))],
        "OBSERVER": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests'))],
    }

    # 2. Define special cases for platform-specific scopes.
    PLATFORM_SCOPE_EXTRAS = {
        "flask": [os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / "test_brand_routes.py"))]
    }

    # --- Scope Building Logic ---

    # Start with the static scopes.
    scopes = STATIC_SCOPES_CONFIG.copy()
    scopes.update(PERSONA_SCOPES_CONFIG)

    # Dynamically generate and add platform-specific scopes.
    presentation_tests_dir = project_config.PRESENTATION_DIR / 'tests'
    for platform_name in project_config.PRESENTATION_APPS.keys():
        scope_name = f"{platform_name.upper()}_PRESENTATION"

        # All platforms have a primary test file by convention.
        primary_test_file = presentation_tests_dir / f"test_{platform_name}_app.py"
        scope_paths = [os.path.normcase(str(primary_test_file))]

        # Add any declared extras.
        scope_paths.extend(PLATFORM_SCOPE_EXTRAS.get(platform_name, []))
        scopes[scope_name] = scope_paths

    return scopes

# --- Project Scope Configuration ---
SCOPES = _build_dynamic_scopes()

def pytest_addoption(parser):
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--scope", action="store", default="ROOT", help=f"Specify test scope. Available: {', '.join(SCOPES.keys())}"
    )

def _is_in_scope(item, scope: str, whitelisted_paths: Union[list, None]) -> bool:
    """
    Determines if a given test item falls within the specified scope,
    handling both path-based and special name-based filtering.
    """
    item_path_norm = os.path.normcase(str(item.path))

    # Start with the basic path-based check. If it's not in the path, it's out.
    if whitelisted_paths and not any(item_path_norm.startswith(p) for p in whitelisted_paths):
        return False

    # Now apply special, more restrictive filters for certain scopes.
    if scope == "DESIGNER_COMPILE":
        return "DESIGNER-compile-scss" in item.nodeid

    if scope == "CONSTRUCTOR_BLUEPRINTS":
        return "test_constructor_" in str(item.path)

    if scope == "CONSTRUCTOR":
        # This scope is for running all constructor-related tests.
        return "test_constructor_" in item.path.name

    if scope == "OBSERVER":
        # The Observer critiques all other personas' work.
        persona_test_files = [
            "test_architect.py", "test_contractor.py", "test_designer.py", "test_qa_engineer.py"
        ]
        # A test is in this scope if it's one of the main persona files OR a constructor test.
        return item.path.name in persona_test_files or "test_constructor_" in item.path.name

    if scope == "PERSONA_CRITIQUES":
        persona_test_files = [
            "test_architect.py",
            "test_contractor.py",
            "test_designer.py",
            "test_qa_engineer.py",
        ]
        # A test is in this scope if it's one of the main persona files OR a constructor test.
        return item.path.name in persona_test_files or "test_constructor_" in item.path.name

    if scope == "REGRESSION_FULL_LIFECYCLE":
        # This scope enforces the architectural workflow order.
        ordered_test_files = [
            "test_architect.py",
            # Constructor tests are matched by pattern
            "test_designer.py",
            "test_contractor.py",
            "test_qa_engineer.py",
        ]
        return item.path.name in ordered_test_files or "test_constructor_" in item.path.name

    # If no special filter applies and it passed the path check (or scope is ROOT), it's in.
    return True

def _implementation_exists(item, implementation_map: dict) -> bool:
    """
    Checks if a test item has a corresponding implementation directory that
    is required for it to run. Returns True if the implementation exists or
    if no check is required for this item.
    """
    item_path_norm = os.path.normcase(str(item.path))
    if item_path_norm in implementation_map:
        implementation_dir = implementation_map[item_path_norm]
        return implementation_dir.exists()
    return True # If not in the map, no implementation check is needed.

def pytest_collection_modifyitems(session, config, items):
    """
    Pytest hook to dynamically deselect tests based on the --scope option and
    the existence of corresponding application implementations. This function
    orchestrates the filtering by calling helper functions.
    """
    scope = config.getoption("--scope").upper()
    whitelisted_paths = SCOPES.get(scope)

    # This map links a test file to the implementation directory that must exist for it to be run.
    implementation_map = {
        os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_angular_app.py')):
            project_config.PRESENTATION_DIR / 'angular_app',
        os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_react_app.py')):
            project_config.PRESENTATION_DIR / 'react_app',
        os.path.normcase(str(project_config.PRESENTATION_DIR / 'tests' / 'test_vue_app.py')):
            project_config.PRESENTATION_DIR / 'vue_app',
    }

    selected_items = []
    deselected_items = []

    for item in items:
        # A test is selected only if it's in scope AND its implementation exists.
        if _is_in_scope(item, scope, whitelisted_paths) and _implementation_exists(item, implementation_map):
            selected_items.append(item)
        else:
            deselected_items.append(item)

    # Modify the collected items list in-place and report to the user.
    if deselected_items:
        items[:] = selected_items
        config.hook.pytest_deselected(items=deselected_items)

def _get_git_info(command: list) -> str:
    """Runs a Git command and returns the stripped output, or 'N/A' on error."""
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "N/A"

def _generate_allure_environment(allure_dir: Path):
    """Creates the environment.properties file for the Allure report."""
    if not allure_dir.is_dir():
        logger.warning(f"Allure results directory '{allure_dir}' not found. Skipping environment file generation.")
        return
    env_file = allure_dir / "environment.properties"

    properties = {
        # Application Info
        "App.Name": project_config.APP_NAME,
        "App.Version": project_config.VERSION,
        "Debug.Mode": str(project_config.DEBUG_MODE),
        # System & Environment Info
        "Python.Version": platform.python_version(),
        "Platform": f"{platform.system()} {platform.release()}",
        "Conda.Environment": os.getenv("CONDA_DEFAULT_ENV", "Not set"),
        # Git Info
        "Git.Branch": _get_git_info(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "Git.Commit": _get_git_info(["git", "rev-parse", "--short", "HEAD"]),
    }

    try:
        with open(env_file, "w") as f:
            for key, value in properties.items():
                f.write(f"{key}={value}\n")
        logger.info(f"Allure environment file generated at: {env_file}")
    except IOError as e:
        logger.error(f"Failed to write Allure environment file: {e}")

def pytest_sessionfinish(session):
    """Hook to generate Allure environment data if --alluredir is used."""
    allure_dir_str = session.config.getoption("--alluredir")
    if allure_dir_str:
        allure_dir = Path(allure_dir_str)
        _generate_allure_environment(allure_dir if allure_dir.is_absolute() else ROOT / allure_dir)