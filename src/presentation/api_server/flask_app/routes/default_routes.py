from flask import Blueprint, render_template, current_app, jsonify
from loguru import logger

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
    return render_template('index.html', title="Welcome to JennAI")

@default_bp.route('/health')
def health_check():
    """
    A simple health check endpoint.
    """
    logger.info("Route '/health' accessed for health check.")
    return jsonify({"status": "ok", "message": "JennAI Flask API is healthy"}), 200