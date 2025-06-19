# /home/jdennis/Projects/JennAI/src/presentation/api_server/flask_app/routes/main_routes.py

from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    """Serves the main index.html page."""
    # Assumes index.html is in a 'templates' folder sibling to this routes directory or configured in app
    return render_template('index.html')