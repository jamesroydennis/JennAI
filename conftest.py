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

def pytest_configure(config):
    """
    Hook called by pytest after command line options have been parsed
    and before the test collection process starts.
    We use this to set up our custom Loguru logging for the test session.
    """
    console = Console() # Initialize Rich Console

    # Display environment and configuration before tests start
    console.print("\n[cyan]" + "=" * 70 + "[/cyan]")
    console.print("[cyan]  PRE-TEST DIAGNOSTICS[/cyan]")
    console.print("[cyan]" + "=" * 70 + "[/cyan]")

    # Display .env contents
    try:
        env_script = ROOT / "admin" / "show_env.py"
        if env_script.exists():
            subprocess.run([sys.executable, str(env_script)], check=True)
        else:
            print(f"Warning: {env_script} not found. Skipping .env display.")
    except subprocess.CalledProcessError as e:
        print(f"Error displaying .env contents: {e}")
    except Exception as e:
        print(f"Unexpected error displaying .env contents: {e}")

    # Display configuration
    try:
        config_script = ROOT / "admin" / "show_config.py"
        if config_script.exists():
            subprocess.run([sys.executable, str(config_script)], check=True)
        else:
            print(f"Warning: {config_script} not found. Skipping configuration display.")
    except subprocess.CalledProcessError as e:
        print(f"Error displaying configuration: {e}")
    except Exception as e:
        print(f"Unexpected error displaying configuration: {e}")

    # Display Project Tree
    try:
        console.print() # Add a blank line for spacing
        tree_script = ROOT / "admin" / "tree.py"
        if tree_script.exists():
            subprocess.run([sys.executable, str(tree_script)], check=True)
        else:
            print(f"Warning: {tree_script} not found. Skipping project tree display.")
    except subprocess.CalledProcessError as e:
        print(f"Error displaying project tree: {e}")
    except Exception as e:
        print(f"Unexpected error displaying project tree: {e}")

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

# --- Project Scope Configuration ---
SCOPES = {
    "ROOT": None,  # Special case: None means run all tests.
    "SYSTEM": [os.path.normcase(str(ROOT / 'tests'))],
    "PRESENTATION": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests'))],
    "FLASK_PRESENTATION": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_flask_app.py')), os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_brand_routes.py'))],
    "ANGULAR_PRESENTATION": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_angular_app.py'))],
    "REACT_PRESENTATION": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_react_app.py'))],
    "VUE_PRESENTATION": [os.path.normcase(str(ROOT / 'src' / 'presentation' / 'tests' / 'test_vue_app.py'))],
    "BUSINESS": [os.path.normcase(str(ROOT / 'src' / 'business' / 'tests'))],
    "DATA": [os.path.normcase(str(ROOT / 'src' / 'data' / 'tests'))],
    "VALIDATION": [os.path.normcase(str(ROOT / 'src' / 'validation' / 'tests'))],
}

def pytest_addoption(parser):
    """Adds custom command-line options to pytest."""
    parser.addoption(
        "--scope", action="store", default="ROOT", help=f"Specify test scope. Available: {', '.join(SCOPES.keys())}"
    )

def pytest_collection_modifyitems(session, config, items):
    """
    Pytest hook to dynamically deselect tests based on the --scope option.
    1. Filters tests based on the --scope command-line option.
    2. Dynamically deselects test suites for presentation layers that have not been scaffolded.
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
        item_path_norm = os.path.normcase(str(item.path))

        # Condition 1: Check if the item is within the selected scope.
        in_scope = (whitelisted_paths is None) or any(item_path_norm.startswith(p) for p in whitelisted_paths)

        # Condition 2: Check if the implementation exists (if applicable).
        implementation_exists = True
        if item_path_norm in implementation_map:
            implementation_dir = implementation_map[item_path_norm]
            if not implementation_dir.exists():
                implementation_exists = False

        # A test is selected only if it's in scope AND its implementation exists.
        if in_scope and implementation_exists:
            selected_items.append(item)
        else:
            deselected_items.append(item)

    # Modify the collected items list in-place and report to the user.
    if deselected_items:
        items[:] = selected_items
        config.hook.pytest_deselected(items=deselected_items)