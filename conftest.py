import os
import sys
from pathlib import Path
from dotenv import load_dotenv  # Import load_dotenv
import pytest
import subprocess # New import for running external scripts
from rich.console import Console # Import Console for colored output
# --- Root Project Path Setup (CRITICAL for Imports) ---
# This ensures that conftest.py can import from your project's modules (config, core, etc.)
ROOT = Path(__file__).resolve().parent # conftest.py is in the project root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env file BEFORE importing config
# This ensures DEBUG_MODE and other settings are correctly read.
load_dotenv(dotenv_path=ROOT / ".env")

from config import config # Import the entire config module
from config.loguru_setup import setup_logging, logger
from config.config import DEBUG_MODE

def _run_diagnostic_script(script_path: Path, description: str):
    """Helper function to run a diagnostic script as a subprocess and handle errors."""
    try:
        if script_path.exists():
            subprocess.run([sys.executable, str(script_path)], check=True)
        else:
            print(f"Warning: {script_path.name} not found. Skipping {description}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}: {e}")
    except Exception as e:
        print(f"Unexpected error running {description}: {e}")

def _display_pre_test_diagnostics(console: Console):
    """Displays all pre-test diagnostic information by running external scripts."""
    console.print("\n[cyan]" + "=" * 70 + "[/cyan]")
    console.print("[cyan]  PRE-TEST DIAGNOSTICS[/cyan]")
    console.print("[cyan]" + "=" * 70 + "[/cyan]")

    _run_diagnostic_script(ROOT / "admin" / "show_env.py", "environment display")
    _run_diagnostic_script(ROOT / "admin" / "show_config.py", "configuration display")

    console.print()  # Add a blank line for spacing
    _run_diagnostic_script(ROOT / "admin" / "tree.py", "project tree display")

def pytest_configure(config):
    """
    Hook called by pytest after command line options have been parsed
    and before the test collection process starts.
    We use this to display diagnostics and set up session logging.
    """
    console = Console()

    _display_pre_test_diagnostics(console)

    console.print("\n[cyan]" + "=" * 70 + "[/cyan]")
    console.print("[cyan]  STARTING PYTEST SESSION[/cyan]")
    console.print("[cyan]" + "=" * 70 + "[/cyan]\n")

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
    return config

def _build_dynamic_scopes() -> dict:
    """
    Builds the SCOPES dictionary dynamically from a declarative configuration,
    reducing manual configuration and improving maintainability.
    """
    # --- Declarative Scope Configuration ---

    # 1. Define static scopes.
    STATIC_SCOPES_CONFIG = {
        "ROOT": None,
        "SYSTEM": [os.path.normcase(str(ROOT / 'tests'))],
        "PRESENTATION": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests'))],
        "DESIGNER_COMPILE": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_designer.py'))],
        "CONSTRUCTOR_BLUEPRINTS": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests'))],
        "PERSONA_CRITIQUES": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests'))],
        "BUSINESS": [os.path.normcase(str(ROOT / 'src' / 'business' / 'tests'))],
        "DATA": [os.path.normcase(str(ROOT / 'src' / 'data' / 'tests'))],
        "VALIDATION": [os.path.normcase(str(ROOT / 'src' / 'validation' / 'tests'))],
    }

    # 2. Define special cases for platform-specific scopes.
    PLATFORM_SCOPE_EXTRAS = {
        "flask": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / "test_brand_routes.py"))]
    }

    # --- Scope Building Logic ---

    # Start with the static scopes.
    scopes = STATIC_SCOPES_CONFIG.copy()

    # Dynamically generate and add platform-specific scopes.
    presentation_tests_dir = ROOT / 'src' / 'presentation' / 'tests'
    for platform_name in config.PRESENTATION_APPS.keys():
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

def _is_in_scope(item, scope: str, whitelisted_paths: list | None) -> bool:
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

    if scope == "PERSONA_CRITIQUES":
        persona_test_files = [
            "test_architect.py",
            "test_contractor.py",
            "test_designer.py",
            "test_qa_engineer.py",
        ]
        # A test is in this scope if it's one of the main persona files OR a constructor test.
        return item.path.name in persona_test_files or "test_constructor_" in item.path.name

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
        os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_angular_app.py')):
            ROOT / 'src' / 'presentation' / 'angular_app',
        os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_react_app.py')):
            ROOT / 'src' / 'presentation' / 'react_app',
        os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_vue_app.py')):
            ROOT / 'src' / 'presentation' / 'vue_app',
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