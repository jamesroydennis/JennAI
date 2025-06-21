from flask import Blueprint, render_template, current_app, jsonify, flash, redirect, url_for
from loguru import logger
import subprocess
from pathlib import Path
import html

# Create a Blueprint for default routes
default_bp = Blueprint(
    'default_bp',
    __name__,
    template_folder='../templates',  # Relative path to the flask_app/templates directory
    static_folder='../static'        # Relative path to the flask_app/static directory
)

@default_bp.route('/')
def index():
    """
    Serves the main index page.
    """
    logger.info(f"Route '/' accessed. Rendering index.html.")
    # Example of accessing the DI container if it was attached to current_app
    # if hasattr(current_app, 'container'):
    #     # Example: ai_service = current_app.container.resolve(IAIService)
    #     logger.debug("DI container is available on current_app.")
    return render_template('index.html', title="Welcome to PyRepo-Pal!")

@default_bp.route('/health')
def health_check():
    """
    A simple health check endpoint.
    """
    logger.info("Route '/health' accessed for health check.")
    return jsonify({"status": "ok", "message": "PyRepo-Pal Flask API is healthy"}), 200

@default_bp.route('/run_tests', methods=['POST'])
def run_tests():
    """
    Triggers the test execution script as a background process.
    """
    logger.info("Route '/run_tests' accessed. Triggering test script.")
    
    # Project root is 6 levels up from this file's directory
    # src/presentation/api_server/flask_app/routes/default_routes.py
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    script_path = project_root / "admin" / "run_tests_and_report.sh"

    # Clean up any previous status files before starting a new run
    for status_file in project_root.glob(".test_run_status_*"):
        status_file.unlink()

    if not script_path.exists():
        logger.error(f"Test script not found at: {script_path}")
        flash(f"Error: Test script not found at {script_path}", "error")
        return redirect(url_for('default_bp.index'))

    try:
        # Use Popen for non-blocking execution
        subprocess.Popen(
            ["bash", str(script_path)],
            cwd=project_root
        )
        flash("Test run started in the background. Check the Allure report in a few minutes.", "success")

    except Exception as e:
        logger.critical(f"Failed to execute test script: {e}")
        flash(f"An unexpected error occurred while trying to run the test script: {e}", "error")

    return redirect(url_for('default_bp.index'))

@default_bp.route('/test_status')
def test_status():
    """API endpoint for the frontend to poll for test run status."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    success_file = project_root / ".test_run_status_success"
    failure_file = project_root / ".test_run_status_failure"

    if success_file.exists():
        success_file.unlink()  # Clean up the file so we don't get stale results
        return jsonify({"status": "success", "message": "Test run completed successfully. Report is ready."})
    elif failure_file.exists():
        failure_file.unlink()  # Clean up the file
        return jsonify({"status": "failure", "message": "Test run completed with errors. Check the report."})
    else:
        return jsonify({"status": "running", "message": "Test run is in progress..."})