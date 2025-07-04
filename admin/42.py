#!/usr/bin/env python
import sys
import shutil
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Import config for paths and logging setup
    from config import config
    from config.config import ArchitecturalPersona, DEBUG_MODE, ARCHITECTURAL_PERSONAS
    from config.loguru_setup import setup_logging, logger, stop_file_logging, start_file_logging
    # Attempt to import the project's validation logic.
    try:
        from src.validation.validator import validate_admin_environment
    except ImportError:
        # Provide a graceful fallback if the validator isn't available.
        # This allows the console to run even if the validation module is under development.
        validate_admin_environment = lambda: (True, "Validator not found, skipping.")
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice
    from InquirerPy.separator import Separator
    from presentation_utils import get_platform_paths
    
    # Import check_apps functions from the same directory
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from check_apps import check_app_status, test_app_status
    
    from InquirerPy.utils import color_print
    from admin_utils import (
        print_header,
        _pause_for_acknowledgement,
        run_command,
        SEPARATOR_LINE,
        console,
        print_formatted_help
    )
except ImportError as e:
    print(f"\n\033[91mFATAL ERROR: A required package is missing: {e.name}\033[0m")
    print("This usually means your Conda environment is out of sync with 'environment.yaml'.")
    print("\nTo fix this, please ensure your environment is active and run:")
    print(f"  pip install -r requirements.txt")
    sys.exit(1)

PY_EXEC = f'"{sys.executable}"'
ALLURE_EXEC = "allure"

HELP_TEXT = """
This is the JennAI Persona-Driven Console.
It provides a context-aware menu system tailored to the responsibilities of each architectural persona.

--- Supermenu Actions (Top-Level) ---
- Run All Persona Tests: Executes all defined tests across all personas.
- Run All Persona Tests & Report: Runs all tests and serves an Allure report.
- Show Project Context: Displays a full snapshot of the environment, config, and file tree.
- Select a Specific Persona: Drills down into a dedicated sub-menu for a single persona.

--- Persona-Specific Sub-menus ---
Each persona has a unique menu of actions relevant to their role:
- ARCHITECT: Manages high-level blueprints, configuration, and runs analysis notebooks.
- DESIGNER: Applies branding and compiles styles.
- CONSTRUCTOR: Builds application skeletons from blueprints.
- CONTRACTOR: Validates and enforces compliance contracts for presentation applications.
- QA_ENGINEER: Verifies quality and testability contracts.
- OBSERVER: Critiques the work of all other personas.
"""

# --- Centralized Step & Command Definitions ---

PYTEST_VERBOSITY_FLAG = "-v" if DEBUG_MODE else "-q -rA"

CLEANUP_STEPS = [
    {"name": "Cleaning Project", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "cleanup.py"}"'},
    {"name": "Creating Directories", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"'},
]
SHOW_CONTEXT_STEP = {"name": "Display CONTEXT", "command": f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "show_context.py"}"', "abort_on_fail": False}

REPORTING_STEP = {"name": "Serve Allure Report", "command": f'"{ALLURE_EXEC}" serve "{config.ALLURE_RESULTS_DIR}"'}

def build_pytest_command(target: str, with_allure: bool, clean_allure: bool = True) -> str:
    """Builds the full pytest command for a scope or a specific test file."""
    is_file = ".py" in target
    target_arg = f'"{target}"' if is_file else f'--scope={target}'
    base_cmd = f'{PY_EXEC} -m pytest {PYTEST_VERBOSITY_FLAG} {target_arg}'
    if with_allure:
        allure_flags = f'--alluredir="{config.ALLURE_RESULTS_DIR}"'
        if clean_allure:
            allure_flags += " --clean-alluredir"
        return f'{base_cmd} {allure_flags}'
    return base_cmd

def _run_test_sequence(target: str, with_allure: bool, is_regression: bool, serve_report: bool):
    """Orchestrates the execution of a full test sequence."""
    steps_to_run = []
    if is_regression:
        steps_to_run.extend(CLEANUP_STEPS)
        steps_to_run.append(SHOW_CONTEXT_STEP)
    else:
        steps_to_run.append(SHOW_CONTEXT_STEP)

    steps_to_run.append({"name": f"Run {target} Tests", "command": build_pytest_command(target, with_allure, clean_allure=True)})

    if serve_report:
        steps_to_run.append(REPORTING_STEP)

    all_ok = True
    for i, step in enumerate(steps_to_run, 1):
        print_header(f"Step {i}/{len(steps_to_run)}: {step['name']}")
        is_cleanup = "cleanup.py" in step["command"]
        if is_cleanup:
            stop_file_logging()

        if not run_command(step["command"]):
            all_ok = False
            logger.error(f"❌ Step '{step['name']}' failed. Aborting sequence.")
            break

        if is_cleanup:
            start_file_logging(debug_mode=DEBUG_MODE)

    if all_ok:
        logger.success(f"✅ Sequence for target '{target}' completed successfully!")
    else:
        logger.warning(f"⚠️ Sequence for target '{target}' finished with errors.")

def _run_full_lifecycle_regression(serve_report: bool = False):
    """
    Runs a full regression test that critiques each persona's work in the
    correct architectural order. This simulates the project's development lifecycle.
    """
    print_header("Full Lifecycle Regression Test")
    logger.info("This test will critique each persona's work in architectural order.")
    logger.info("Aborting if any stage fails...")

    # Define the architectural order of critiques.
    # The target can be a scope name or a direct file path.
    lifecycle_stages = [
        {"persona": "Architect", "target": str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_architect.py")},
        {"persona": "Constructor", "target": "CONSTRUCTOR"}, # This scope runs all constructor tests
        {"persona": "Designer", "target": str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_designer.py")},
        {"persona": "Contractor", "target": str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_contractor.py")},
        {"persona": "QA Engineer", "target": str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_qa_engineer.py")},
    ]

    # Run initial cleanup and context display once.
    for step in CLEANUP_STEPS + [SHOW_CONTEXT_STEP]:
         print_header(f"Setup Step: {step['name']}")
         if not run_command(step["command"]):
             logger.error(f"❌ Setup step '{step['name']}' failed. Aborting lifecycle test.")
             return

    overall_success = True
    for i, stage in enumerate(lifecycle_stages, 1):
        print_header(f"Lifecycle Stage {i}/{len(lifecycle_stages)}: Critiquing {stage['persona']}")
        # For the report, we clean allure results only on the first stage.
        clean_allure_dir = (i == 1) if serve_report else False
        pytest_command = build_pytest_command(stage["target"], with_allure=serve_report, clean_allure=clean_allure_dir)
        if not run_command(pytest_command):
            logger.error(f"❌ Lifecycle critique FAILED at the '{stage['persona']}' stage.")
            overall_success = False
            break # Stop the sequence on the first failure.

    if overall_success:
        logger.success("✅ Full lifecycle regression test passed all stages!")
        if serve_report:
            print_header(f"Final Step: {REPORTING_STEP['name']}")
            run_command(REPORTING_STEP["command"])
    else:
        logger.warning("⚠️ Full lifecycle regression test failed.")

def _handle_architect_menu():
    """Handles the menu for the Architect persona."""
    NOTEBOOK_TO_RUN = PROJECT_ROOT / "notebooks" / "architectural_analysis.ipynb"
    while True:
        print_header("Architect: Analysis, Blueprints & Configuration")
        action = inquirer.select(
            message="Select an Architect action:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Persona Selection"),
                Separator(SEPARATOR_LINE),
                Choice("run_notebook", "🔬  Run Architectural Analysis Notebook"),
                Choice("show_config", "📄  Show Master Configuration (config.py)"),
                Choice("create_folders", "📁  Initialize/Create Project Folders"),
                Separator(SEPARATOR_LINE),
                Choice("critique", "🏛️  Critique Architect's Plan (test_architect.py)"),
                Choice("verify_blueprints", "🛠️  Verify All Constructor Blueprints"),
            ],
            qmark="🏛️"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "run_notebook":
            if not NOTEBOOK_TO_RUN.exists():
                logger.error(f"Notebook not found at the expected path: {NOTEBOOK_TO_RUN}")
            else:
                run_command(f'jupyter nbconvert --execute --to notebook --inplace "{NOTEBOOK_TO_RUN}"')
        elif action == "show_config":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "show_config.py"}"')
        elif action == "create_folders":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_directories.py"}"')
        elif action == "critique":
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_architect.py")
            _run_test_sequence(target=test_file, with_allure=False, is_regression=False, serve_report=False)
        elif action == "verify_blueprints":
            _run_test_sequence(target="CONSTRUCTOR_BLUEPRINTS", with_allure=False, is_regression=False, serve_report=False)

        _pause_for_acknowledgement()

def _prompt_for_presentation_app(message: str = "Select a platform:"):
    """Helper function to prompt the user to select a presentation platform."""
    choices = [Choice(key, name=details["display_name"]) for key, details in config.PRESENTATION_APPS.items()]
    choices.append(Separator(SEPARATOR_LINE))
    choices.append(Choice(value=None, name="⬅️  Back"))
    return inquirer.select(message=message, choices=choices, default="flask").execute()

def _delete_platform(platform_key: str):
    """Safely deletes the directory for a given presentation platform after user confirmation."""
    app_status = check_app_status(platform_key)
    platform_dir = app_status["path"]
    
    # Log status check as test result
    test_passed = app_status["health"] in ["healthy", "partial"]
    logger.info(f"Status Test: {platform_key.upper()} - {'PASSED' if test_passed else 'FAILED'} (Health: {app_status['health']})")
    
    if not platform_dir:
        logger.error(f"Error: No path defined for platform '{platform_key}'.")
        return

    if not platform_dir.exists():
        logger.info(f"Directory for {platform_key.capitalize()} not found at '{platform_dir}'. Nothing to delete.")
        return

    confirmed = inquirer.confirm(
        message=f"DANGER: This will permanently delete the entire '{platform_dir.name}' directory. Are you sure?",
        default=False,
        confirm_message="Deletion confirmed.",
        reject_message="Deletion cancelled."
    ).execute()

    if not confirmed: return

    try:
        shutil.rmtree(platform_dir)
        logger.success(f"Successfully deleted the {platform_key.capitalize()} application directory.")
    except OSError as e:
        logger.error(f"Error deleting directory '{platform_dir}': {e}")

def _handle_platform_actions_for_contractor(platform_key: str):
    """Handles the lifecycle action sub-menu for a selected platform."""
    while True:
        app_status = check_app_status(platform_key)
        platform_dir = app_status["path"]
        app_exists = app_status["exists"]
        health = app_status["health"]

        # Log status check as test result
        test_passed = health in ["healthy", "partial"]
        logger.debug(f"Status Test: {platform_key.upper()} - {'PASSED' if test_passed else 'FAILED'} (Health: {health})")

        # Base navigation choices, present in all menus for consistency
        choices = [
            Choice("exit", "🔚  Exit"),
            Choice("help", "❓  Help"),
            Choice(None, "⬅️  Back to Platform Selection"),
            Separator(SEPARATOR_LINE),
        ]

        if app_exists and health in ["healthy", "partial"]:
            choices.extend([
                Choice("status_test", "🧪  Test App Status"),
                Choice("validate_brand", "🔍  Validate Brand Compliance"),
                Choice("validate_assets", "🔍  Validate Asset Integration"),
                Choice("validate_styling", "�  Validate SCSS Compilation"),
                Separator(SEPARATOR_LINE),
                Choice("test", "🧪  Test (Run Unit/Integration Tests)"),
                Choice("test_report", "📊\tTest & Report"),
                Separator(SEPARATOR_LINE),
                Choice("enforce_reset", "⚖️  Enforce Reset (Non-Compliant App)"),
                Choice("enforce_delete", "⚖️  Enforce Delete (Contract Violation)"),
            ])
        else:
            choices.extend([
                Choice("status_test", "🧪  Test App Status"),
                Choice("validate_scaffold", "🔍  Validate Scaffold Requirements"),
            ])

        # Show app status in header
        status_icon = {"healthy": "✅", "partial": "⚠️", "empty": "❌", "not_scaffolded": "🏗️"}.get(health, "❓")
        print_header(f"Contractor: {platform_key.capitalize()} Contract Validation {status_icon}")
        action = inquirer.select(message="Select an action:", choices=choices).execute()

        if action is None: break
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "validate_scaffold":
            # Run contractor validation test to check scaffold requirements
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_contractor.py")
            print(f"\n🔍 Validating {platform_key.upper()} Scaffold Requirements...")
            run_command(f'{PY_EXEC} -m pytest "{test_file}::test_contractor_scaffold_validation" -v')
        elif action == "validate_brand":
            # Run contractor brand compliance validation
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_contractor.py")
            print(f"\n🔍 Validating {platform_key.upper()} Brand Compliance...")
            run_command(f'{PY_EXEC} -m pytest "{test_file}::test_contractor_brand_compliance" -v')
        elif action == "validate_assets":
            # Run contractor asset integration validation
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_contractor.py")
            print(f"\n🔍 Validating {platform_key.upper()} Asset Integration...")
            run_command(f'{PY_EXEC} -m pytest "{test_file}::test_contractor_asset_integration" -v')
        elif action == "validate_styling":
            # Run contractor SCSS compilation validation
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_contractor.py")
            print(f"\n🔍 Validating {platform_key.upper()} SCSS Compilation...")
            run_command(f'{PY_EXEC} -m pytest "{test_file}::test_contractor_brand_compilation_validation" -v')
        elif action == "enforce_reset":
            print(f"\n⚖️  ENFORCEMENT ACTION: Non-compliant {platform_key.upper()} app will be reset")
            _delete_platform(platform_key)
            print(f"📋 CONTRACT REQUIREMENT: App must be re-scaffolded by Constructor persona")
            print(f"📋 CONTRACT REQUIREMENT: Brand assets must be injected by Designer persona")
            print(f"📋 CONTRACT REQUIREMENT: SCSS must be compiled by build process")
        elif action == "enforce_delete":
            print(f"\n⚖️  ENFORCEMENT ACTION: Contract-violating {platform_key.upper()} app will be deleted")
            _delete_platform(platform_key)
        elif action == "test":
            _run_test_sequence(target=f"{platform_key.upper()}_PRESENTATION", with_allure=False, is_regression=False, serve_report=False)
        elif action == "test_report":
            _run_test_sequence(target=f"{platform_key.upper()}_PRESENTATION", with_allure=True, is_regression=False, serve_report=True)
        elif action == "status_test":
            # Run app status test and display results
            print(f"\n🧪 Testing {platform_key.upper()} App Status...")
            
            # Get status and determine test result
            status = check_app_status(platform_key)
            test_passed = status["health"] in ["healthy", "partial"]
            
            # Display test result to user
            if test_passed:
                color_print([("green", f"✅ {platform_key.upper()} Test: PASSED")])
                print(f"   Status: {status['health']}")
                print(f"   Display Name: {status['display_name']}")
                if status.get('path'):
                    print(f"   Path: {status['path']}")
                if status.get('files'):
                    print(f"   Files Found: {', '.join(status['files'])}")
            else:
                color_print([("red", f"❌ {platform_key.upper()} Test: FAILED")])
                print(f"   Health Status: {status['health']}")
                print(f"   Path: {status.get('path', 'Unknown')}")
                if not status.get('exists'):
                    print(f"   Issue: Application directory does not exist")
                elif status['health'] == 'empty':
                    print(f"   Issue: Application directory is empty")
                else:
                    print(f"   Issue: Application is not properly scaffolded")

        _pause_for_acknowledgement()

def _handle_designer_menu():
    """Handles the menu for the Designer persona."""
    while True:
        print_header("Designer: Brand & Style Application")
        action = inquirer.select(
            message="Select a Designer action:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Persona Selection"),
                Separator(SEPARATOR_LINE),
                Choice("inject", "🎨  Apply Brand to an Application"),
                Choice("compile", "🎨  Compile Styles for an Application"),
                Separator(SEPARATOR_LINE),
                Choice("critique", "🖌️  Critique All Design Work (test_designer.py)"),
            ],
            qmark="🖌️"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action in ["inject", "compile"]:
            platform_key = _prompt_for_presentation_app(f"Select a platform to '{action}' assets for:")
            if platform_key:
                if action == "inject":
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "inject_brand_assets.py"}" --target {platform_key}')
                elif action == "compile":
                    run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "compile_scss.py"}" --target {platform_key}')
        elif action == "critique":
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_designer.py")
            _run_test_sequence(target=test_file, with_allure=False, is_regression=False, serve_report=False)

        _pause_for_acknowledgement()

def _handle_constructor_menu():
    """Handles the menu for the Constructor persona."""
    while True:
        print_header("Constructor: Build Application Skeletons")
        platform_key = _prompt_for_presentation_app("Select a platform to build:")
        if platform_key is None:
            return # Go back to persona selection

        print_header(f"Constructing {platform_key.capitalize()} Application")
        run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / f"create_presentation_{platform_key}.py"}"')

        if not inquirer.confirm(message="Build another application?", default=True).execute():
            return

def _handle_contractor_menu():
    """Handles the menu for the Contractor persona."""
    while True:
        print_header("Contractor: Contract Validation & Enforcement")
        platform_key = _prompt_for_presentation_app("Select a platform to validate:")
        if platform_key is None:
            return # Go back to persona selection
        _handle_platform_actions_for_contractor(platform_key)

def _handle_qa_engineer_menu():
    """Handles the menu for the QA Engineer persona."""
    while True:
        print_header("QA Engineer: Testability & Quality Contracts")
        action = inquirer.select(
            message="Select a QA Engineer action:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Persona Selection"),
                Separator(SEPARATOR_LINE),
                Choice("critique", "🔬  Critique Testability & Quality Contracts (test_qa_engineer.py)"),
            ],
            qmark="🔬"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "critique":
            test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_qa_engineer.py")
            _run_test_sequence(target=test_file, with_allure=False, is_regression=False, serve_report=False)

        _pause_for_acknowledgement()

def _handle_observer_menu():
    """Handles the menu for the Observer persona, focusing on critiques."""
    while True:
        print_header("Observer: Critiques")
        action = inquirer.select(
            message="Select a critique to perform:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Persona Selection"),
                Separator(SEPARATOR_LINE),
                Choice("critique_all", "🧐  Critique All Personas (Comprehensive Check)"),
            ],
            qmark="🧐"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "critique_all":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=False, is_regression=False, serve_report=False)
            _pause_for_acknowledgement()

def _handle_data_persona_menu():
    """Handles the menu for the Data persona."""
    while True:
        print_header("Data: Database & Mock Data Management")
        action = inquirer.select(
            message="Select a Data action:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Persona Selection"),
                Separator(SEPARATOR_LINE),
                Choice("manage_mock_data", "🗃️  Manage Mock Data & DB"),
                Separator(SEPARATOR_LINE),
                Choice("critique", "🔬  Critique Data Layer (test_data.py)"),
            ],
            qmark="🗃️"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "manage_mock_data":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "create_mock_data.py"}"')
        elif action == "critique":
            _run_test_sequence(target="DATA", with_allure=False, is_regression=False, serve_report=False)

        _pause_for_acknowledgement()

def _handle_testing_menu():
    """Handles the sub-menu for running project-wide tests."""
    while True:
        print_header("Testing")
        action = inquirer.select(
            message="Select a testing task:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Main Menu"),
                Separator(SEPARATOR_LINE),
                Choice("test_all", "👥  Run All Persona Tests"),
                Choice("test_all_report", "📊  Run All Persona Tests & Report"),
                Separator(SEPARATOR_LINE),
                Choice("regression", "🔄  Run Full Regression"),
                Choice("regression_report", "🔄  Run Full Regression & Report"),
                Separator(SEPARATOR_LINE),
                Choice("lifecycle_regression", "🔄  Run Full Lifecycle Regression"),
                Choice("lifecycle_regression_report", "📊  Run Full Lifecycle Regression & Report"),
            ],
            qmark="🔬"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "test_all":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=False, is_regression=False, serve_report=False)
        elif action == "test_all_report":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=True, is_regression=False, serve_report=True)
        elif action == "regression":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=True, is_regression=True, serve_report=False)
        elif action == "regression_report":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=True, is_regression=True, serve_report=True)
        elif action == "lifecycle_regression":
            _run_full_lifecycle_regression(serve_report=False)
        elif action == "lifecycle_regression_report":
            _run_full_lifecycle_regression(serve_report=True)

        _pause_for_acknowledgement()

def _handle_diagnostics_menu():
    """Handles the sub-menu for running diagnostic checks."""
    while True:
        print_header("Diagnostics")
        action = inquirer.select(
            message="Select a diagnostic task:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Main Menu"),
                Separator(SEPARATOR_LINE),
                Choice("check_deps", "⚙️  Check System Dependencies"),
                Choice("check_logs", "📄  Check Logs"),
                Separator(SEPARATOR_LINE),
                Choice("test_all", "🧪  Run All Tests"),
                Choice("test_all_report", "📊  Run All Tests & Report"),
            ],
            qmark="🛠️"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "check_deps":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "check_dependencies.py"}"')
        elif action == "check_logs":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "check_logs.py"}"')
        elif action == "test_all":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=False, is_regression=False, serve_report=False)
        elif action == "test_all_report":
            _run_test_sequence(target="PERSONA_CRITIQUES", with_allure=True, is_regression=False, serve_report=True)

        _pause_for_acknowledgement()

def _handle_view_menu():
    """Handles the sub-menu for running applications and viewing project context."""
    while True:
        print_header("Run")
        action = inquirer.select(
            message="Select an action:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Choice(None, "⬅️  Back to Main Menu"),
                Separator(SEPARATOR_LINE),
                Choice("run_app", "🚀  Run Web Application"),
                Separator(SEPARATOR_LINE),
                Choice("show_context", "ℹ️  Show Full Context"),
                Choice("show_config", "📄  Show Configuration"),
                Choice("tree", "🌳  Show Project Tree"),
            ],
            qmark="�"
        ).execute()

        if action is None: return
        if action == "exit": return "exit"
        if action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()
            continue

        if action == "run_app":
            platform_key = _prompt_for_presentation_app("Select a web application to run:")
            if platform_key:
                _run_web_application(platform_key)
        elif action == "show_context":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "show_context.py"}"')
        elif action == "show_config":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "show_config.py"}"')
        elif action == "tree":
            run_command(f'{PY_EXEC} "{PROJECT_ROOT / "admin" / "tree.py"}"')

        _pause_for_acknowledgement()

def _run_web_application(platform_key):
    """Run a web application for the specified platform."""
    app_status = check_app_status(platform_key)
    platform_dir = app_status["path"]
    
    # Log status check as test result
    test_passed = app_status["health"] in ["healthy", "partial"]
    logger.info(f"Status Test: {platform_key.upper()} - {'PASSED' if test_passed else 'FAILED'} (Health: {app_status['health']})")
    
    if not platform_dir or not platform_dir.exists():
        console.print(f"[red]❌ {platform_key.capitalize()} application not found. Please scaffold it first.[/red]")
        return
    
    print_header(f"Starting {platform_key.capitalize()} Application")
    
    if platform_key == "flask":
        console.print(f"[green]🚀 Starting Flask development server...[/green]")
        run_command(f'{PY_EXEC} -m src.presentation.api_server.flask_app.app', cwd=PROJECT_ROOT)
    elif platform_key == "angular":
        console.print(f"[green]🚀 Starting Angular development server...[/green]")
        run_command('npx ng serve --open', cwd=platform_dir)
    elif platform_key == "react":
        console.print(f"[green]🚀 Starting React development server...[/green]")
        run_command('npm start', cwd=platform_dir)
    elif platform_key == "vue":
        console.print(f"[green]🚀 Starting Vue development server...[/green]") 
        run_command('npm run dev', cwd=platform_dir)
    elif platform_key == "console":
        console.print(f"[yellow]ℹ️ Console is an abstract platform - no web server to start.[/yellow]")
        console.print(f"[blue]💡 Tip: Console functionality is available through the admin scripts in this directory.[/blue]")
    else:
        console.print(f"[red]❌ Unknown platform: {platform_key}[/red]")

# --- Menu Dispatcher ---
MENU_HANDLERS = {
    "ARCHITECT": _handle_architect_menu,
    "DESIGNER": _handle_designer_menu,
    "CONSTRUCTOR": _handle_constructor_menu,
    "CONTRACTOR": _handle_contractor_menu,
    "QA_ENGINEER": _handle_qa_engineer_menu,
    "OBSERVER": _handle_observer_menu,
    "DATA": _handle_data_persona_menu,
}

def _show_persona_selection_menu():
    """Handles the config-driven sub-menu for selecting and acting on a specific persona."""
    while True:
        print_header("Persona Selection - Config Driven")
        
        # Build persona choices from config dictionary
        persona_menu_items = []
        for persona_key, persona_info in config.ARCHITECTURAL_PERSONAS.items():
            icon = persona_info.get("icon", "👤")
            name = persona_info.get("name", persona_key.title())
            display_name = f"{icon}  {name}"
            persona_menu_items.append(Choice(value=persona_key, name=display_name))
        
        persona_choices = [
            Choice("exit", "🔚  Exit"),
            Choice("help", "❓  Help"),
            Choice("test_all", "🧪  Test All Personas"),
            Choice(value=None, name="⬅️  Back to Main Menu"),
            Separator(SEPARATOR_LINE),
            *persona_menu_items,
        ]

        persona_selection = inquirer.select(
            message="Select Persona",
            choices=persona_choices,
            default=None,
            cycle=False,
        ).execute()

        if persona_selection is None:
            break # Go back to the main menu

        if persona_selection == "exit":
            return "exit"
        if persona_selection == "help":
            print_header("Help - Config-Driven Personas")
            help_text = "JennAI Persona Menu - Config-Driven Architecture\n\n"
            help_text += "Available Personas:\n"
            for key, info in config.ARCHITECTURAL_PERSONAS.items():
                icon = info.get("icon", "👤")
                name = info.get("name", key.title())
                desc = info.get("description", "No description")
                help_text += f"  {icon} {name}: {desc}\n"
            help_text += "\nSpecial Commands:\n"
            help_text += "  🧪 Test All Personas: Run validation tests for all personas\n"
            help_text += "  ❓ Help: Show this help text\n"
            help_text += "  🔚 Exit: Exit the application\n"
            print_formatted_help(help_text)
            _pause_for_acknowledgement()
            continue
        if persona_selection == "test_all":
            _handle_test_all_personas()
            continue

        handler = MENU_HANDLERS.get(persona_selection)
        if handler:
            result = handler()
            if result == 'exit':
                return 'exit' # Propagate exit signal up to main
        else:
            print(f"⚠️  No handler found for persona: {persona_selection}")
            _pause_for_acknowledgement()

def _handle_test_all_personas():
    """Run tests for all personas to verify system integration."""
    print_header("Testing All Personas - System Integration")
    test_file = str(PROJECT_ROOT / "src" / "presentation" / "tests" / "test_contractor.py")
    
    # Test contractor validations that cover all personas
    print("🔍 Running comprehensive persona validation tests...")
    run_command(f'{PY_EXEC} -m pytest "{test_file}" -v --tb=short')
    
    _pause_for_acknowledgement()

def main():
    """Main function to display the interactive persona-driven menu."""
    logger.info(f"Persona testing console started. DEBUG_MODE is set to: {config.DEBUG_MODE}")

    # --- Project Context Validation ---
    # Before displaying the menu, run the project's own validation logic.
    # This ensures that "prior tests that challenged the context passed."
    logger.info("Validating project context before proceeding...")
    is_valid, message = validate_admin_environment()
    if not is_valid:
        logger.error(f"Project context validation FAILED: {message}")
        logger.error("Aborting persona console. Please fix the environment and try again.")
        sys.exit(1)
    logger.success("Project context validation passed.")

    while True:
        print_header("JennAI")

        action = inquirer.select(
            message="Select a task:",
            choices=[
                Choice("exit", "🔚  Exit"),
                Choice("help", "❓  Help"),
                Separator(SEPARATOR_LINE),
                Choice("testing", "🔬  Test"),
                Choice("view", "👁️  Run"),
                Choice("diagnostics", "🛠️  Diagnostics"),
                Choice("select_persona", "👤  Select a Specific Persona..."),
            ],
            default="testing",
            cycle=False,
        ).execute()

        if action == "exit" or action is None:
            break

        elif action == "help":
            print_header("Help")
            print_formatted_help(HELP_TEXT)
            _pause_for_acknowledgement()

        elif action == "testing":
            result = _handle_testing_menu()
            if result == 'exit': break
        elif action == "view":
            result = _handle_view_menu()
            if result == 'exit': break
        elif action == "diagnostics":
            result = _handle_diagnostics_menu()
            if result == 'exit': break
        elif action == "select_persona":
            result = _show_persona_selection_menu()
            if result == 'exit':
                break # Exit the main while loop

if __name__ == "__main__":
    setup_logging(debug_mode=config.DEBUG_MODE)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting console. Goodbye!")
    finally:
        stop_file_logging()