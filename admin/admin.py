import subprocess
import sys
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import color_print

# ==============================================================================
# JennAI Interactive Admin Console (Simplified)
# ==============================================================================
#
# This script provides a user-friendly command-line interface for managing
# and running development tasks for the JennAI project.
#
# ==============================================================================


# --- Configuration ---

# Determine the project root directory (assuming this script is in /admin)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
ALLURE_REPORT_DIR = PROJECT_ROOT / "allure-report"


# --- Helper Functions ---

def print_header(title: str):
    """Prints a styled header to the console."""
    print()
    color_print([("yellow", "=" * 70)])
    color_print([("yellow", f"  {title}")])
    color_print([("yellow", "=" * 70)])
    print()


def run_command(command: str, cwd: Path = PROJECT_ROOT) -> int:
    """
    Runs a command in the shell, streams its output, and returns the exit code.
    """
    try:
        # Use Popen to stream output in real-time, which is better for long tasks.
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=cwd, text=True, encoding='utf-8'
        )
        # Stream the output line by line
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        process.stdout.close()
        return process.wait()
    except FileNotFoundError:
        color_print([("red", f"Error: Command not found for '{command}'. Is it installed and in your PATH?")])
        return 1
    except Exception as e:
        color_print([("red", f"An unexpected error occurred: {e}")])
        return 1


# --- Menu Actions ---

def action_display_tree():
    """Displays the project structure using the tree.py script."""
    print_header("🌳 Displaying Project Tree")
    # The tree.py script is self-contained and handles its own logic.
    # Using sys.executable ensures we use the same python interpreter.
    command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "tree.py"}"'
    return_code = run_command(command)
    if return_code != 0:
        # The tree.py script logs its own errors, so we just add a simple note here.
        color_print([("red", "\n❌ The tree script reported an issue. Please check the logs above.")])


def action_cleanup():
    """Runs the project cleanup script."""
    print_header("🧹 Cleaning Project")
    command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "cleanup.py"}"'
    return_code = run_command(command)
    if return_code == 0:
        color_print([("green", "\n✅ Project cleanup completed successfully.")])
    else:
        color_print([("red", "\n❌ The cleanup script reported an issue. Please check the logs above.")])

def action_run_tests():
    """Runs the pytest test suite and collects Allure results."""
    print_header("🧪 Running Tests (Pytest)")
    # Using -m pytest ensures we use the interpreter's installed pytest.
    # --clean-alluredir is good practice to remove old results.
    command = f'"{sys.executable}" -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'
    return_code = run_command(command)
    if return_code == 0:
        color_print([("green", "\n✅ Tests executed successfully.")])
    else:
        color_print([("red", f"\n❌ Tests failed. Check the output above for details.")])

def action_test_and_report():
    """Runs tests, then serves the Allure report, blocking further execution."""
    print_header("📊 Running Tests & Serving Allure Report")
    # First, run tests and collect results
    test_command = f'"{sys.executable}" -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'
    test_return_code = run_command(test_command)

    if test_return_code == 0:
        color_print([("green", "\n✅ Tests executed successfully. Now launching Allure report server...")])
        color_print([("cyan", "The server is running. Press Ctrl+C in this terminal to stop it and return to the menu.")])
        # Then, serve the Allure report. This is a blocking command.
        report_command = f"allure serve \"{ALLURE_RESULTS_DIR}\""
        run_command(report_command)
        # Execution will pause here until the user stops the Allure server.
    else:
        color_print([("red", f"\n❌ Tests failed, skipping Allure report. Check the output above.")])

def action_create_folders():
    """Runs the script to create the project's folder structure."""
    print_header("🏗️ Creating Project Folders")
    command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "create_project_folders.py"}"'
    return_code = run_command(command)
    if return_code == 0:
        color_print([("green", "\n✅ Project folder creation completed successfully.")])
    else:
        color_print([("red", "\n❌ The folder creation script reported an issue. Please check the logs above.")])

def action_regression():
    """Runs a full regression sequence: cleanup, folder creation, and testing."""
    print_header("🚀 Running Full Regression Sequence")

    # Step 1: Cleanup
    color_print([("cyan", "\n--- Step 1 of 3: Cleaning Project ---")])
    cleanup_command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "cleanup.py"}"'
    if run_command(cleanup_command) != 0:
        color_print([("red", "\n❌ Regression failed at cleanup step. Aborting.")])
        return  # Stop the sequence

    # Step 2: Create Folders
    color_print([("cyan", "\n--- Step 2 of 3: Creating Project Folders ---")])
    folders_command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "create_project_folders.py"}"'
    if run_command(folders_command) != 0:
        color_print([("red", "\n❌ Regression failed at folder creation step. Aborting.")])
        return  # Stop the sequence

    # Step 3: Run Tests
    color_print([("cyan", "\n--- Step 3 of 3: Running Tests ---")])
    test_command = f'"{sys.executable}" -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'
    if run_command(test_command) != 0:
        color_print([("red", "\n❌ Regression failed at testing step.")])
        return  # Stop the sequence

    color_print([("green", "\n✅ Full Regression sequence completed successfully!"])])


def action_install():
    """
    Runs the main project installation and setup script (setup.py).
    NOTE: This function is not included in the interactive menu by default.
    """
    print_header("⚙️ Running Project Installation")
    color_print(
        [("yellow", "This will execute 'setup.py', which may perform destructive actions like deleting files.")]
    )
    command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "setup.py"}"'
    return_code = run_command(command)
    if return_code == 0:
        color_print([("green", "\n✅ Project installation completed successfully.")])
    else:
        color_print([("red", "\n❌ The installation script reported an issue. Please check the logs above.")])


def action_destroy_create():
    """
    Runs a full destroy, create, and test sequence.
    NOTE: This function is not included in the interactive menu by default.
    """
    print_header("💥 Running Full Destroy, Create & Test Sequence")

    try:
        confirmed = inquirer.confirm(
            message="WARNING: This is a destructive reset. All logs, reports, and the database will be deleted. Continue?",
            default=False,
            confirm_message="Confirmed. Starting reset process...",
            reject_message="Operation cancelled by user."
        ).execute()

        if not confirmed:
            print() # Add a newline for cleaner exit
            return
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return

    # Step 1: Cleanup
    color_print([("cyan", "\n--- Step 1 of 5: Cleaning Project ---")])
    cleanup_command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "cleanup.py"}"'
    if run_command(cleanup_command) != 0:
        color_print([("red", "\n❌ Sequence failed at cleanup step. Aborting.")])
        return

    # Step 2: Create Folders
    color_print([("cyan", "\n--- Step 2 of 5: Creating Project Folders ---")])
    folders_command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "create_project_folders.py"}"'
    if run_command(folders_command) != 0:
        color_print([("red", "\n❌ Sequence failed at folder creation step. Aborting.")])
        return

    # Step 3: Setup Database
    color_print([("cyan", "\n--- Step 3 of 5: Setting up Database ---")])
    db_setup_command = f'"{sys.executable}" "{PROJECT_ROOT / "src" / "data" / "scripts" / "sql" / "setup_database.py"}"'
    if run_command(db_setup_command) != 0:
        color_print([("red", "\n❌ Sequence failed at database setup step. Aborting.")])
        return

    # Step 4: Display Tree
    color_print([("cyan", "\n--- Step 4 of 5: Displaying Project Tree ---")])
    tree_command = f'"{sys.executable}" "{PROJECT_ROOT / "admin" / "tree.py"}"'
    run_command(tree_command) # Run but don't abort on failure

    # Step 5: Run Tests and Serve Report
    color_print([("cyan", "\n--- Step 5 of 5: Running Tests & Serving Report ---")])
    test_command = f'"{sys.executable}" -m pytest --alluredir="{ALLURE_RESULTS_DIR}" --clean-alluredir'
    test_return_code = run_command(test_command)

    if test_return_code == 0:
        color_print([("green", "\n✅ Tests executed successfully. Now launching Allure report server...")])
    else:
        color_print([("red", f"\n❌ Tests failed. Launching Allure report server to view failures...")])

    if ALLURE_RESULTS_DIR.exists() and any(ALLURE_RESULTS_DIR.iterdir()):
        color_print([("cyan", "The server is running. Press Ctrl+C in this terminal to stop it.")])
        report_command = f"allure serve \"{ALLURE_RESULTS_DIR}\""
        run_command(report_command) # This is a blocking call
    else:
        color_print([("yellow", "No Allure results found to generate a report.")])
# --- Main Application ---

def main():
    """Displays the interactive menu and handles user choices."""
    action_map = {
        "tree": action_display_tree, "cleanup": action_cleanup, "test": action_run_tests,
        "test_and_report": action_test_and_report,
        "create_folders": action_create_folders, "regression": action_regression,
    }

    while True:
        try:
            choice = inquirer.select(
                message="Welcome to the JennAI Admin Console. Select a task:",
                choices=[
                    Choice("tree", name="🌳 Display Project Tree"),
                    Choice("cleanup", name="🧹 Clean-Up Project"),
                    Choice("test", name="🧪 Run Tests (No Report)"),
                    Choice("test_and_report", name="📊 Run Tests & Serve Report"),
                    Choice("create_folders", name="🏗️ Create Project Folders"),
                    Choice("regression", name="🚀 Run Full Regression"),
                    Choice(None, name="Exit"),
                ],
                default="test",
            ).execute()

            if choice is None:
                print("\nGoodbye!")
                break

            action_map[choice]()
            # For "tree" and "cleanup", we return to the menu immediately.
            if choice not in ["tree", "cleanup", "test", "test_and_report", "create_folders", "regression"]:
                input("\nPress Enter to return to the menu...")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()