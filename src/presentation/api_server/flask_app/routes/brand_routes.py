from flask import Blueprint, send_from_directory, current_app
from pathlib import Path

# Import the project's configuration to get asset paths
from config import config # Ensure config is imported

# Create a Blueprint for brand-related routes
brand_bp = Blueprint('brand', __name__, url_prefix='/brand')

@brand_bp.route('/logo.png')
def serve_logo():
    """Serves the main application logo from the path defined in config.py."""
    try:
        # LOGO_PATH is an absolute path to the file, e.g., C:\...\jennai-logo.png
        # We need the directory and the filename for send_from_directory
        logo_directory = config.LOGO_PATH.parent
        logo_filename = config.LOGO_PATH.name
        current_app.logger.info(f"Serving logo: {logo_filename} from {logo_directory}")
        return send_from_directory(logo_directory, logo_filename)
    except Exception as e:
        current_app.logger.error(f"Error serving logo: {e}")
        return "Logo not found", 404

@brand_bp.route('/favicon.ico')
def serve_favicon():
    """Serves the application's favicon.ico from the brand directory."""
    try:
        favicon_directory = config.FAVICON_PATH.parent
        favicon_filename = config.FAVICON_PATH.name
        return send_from_directory(favicon_directory, favicon_filename)
    except Exception as e:
        current_app.logger.error(f"Error serving favicon: {e}")
        return "Favicon not found", 404

@brand_bp.route('/css/main.css')
def serve_css():
    """Serves the main CSS file."""
    try:
        # Look for the CSS file in the Flask app's static directory
        css_path = Path(__file__).parent.parent / "static" / "css" / "main.css"
        if css_path.exists():
            return send_from_directory(css_path.parent, css_path.name)
        else:
            current_app.logger.warning(f"CSS file not found at {css_path}")
            return "/* CSS file not found */", 404, {'Content-Type': 'text/css'}
    except Exception as e:
        current_app.logger.error(f"Error serving CSS: {e}")
        return "/* CSS error */", 404, {'Content-Type': 'text/css'}