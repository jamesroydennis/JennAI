from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import markdown
from core.dependency_container import DependencyContainer
from config import config

def create_app(container: DependencyContainer) -> Flask:
    """
    Application factory for the Flask app.
    Configures and returns the Flask application instance.
    """
    # The static_folder is set to None because we are serving assets
    # from custom routes. The template_folder points to the correct location.
    app = Flask(__name__, static_folder=None, template_folder="templates")
    CORS(app) # Enable CORS for all routes

    # Register the brand routes blueprint
    from routes.brand_routes import brand_bp
    app.register_blueprint(brand_bp)

    # Route for favicon.ico at the root, as browsers expect it there
    @app.route('/favicon.ico')
    def serve_favicon():
        """Serves the application's favicon.ico from the brand directory."""
        try:
            favicon_directory = config.FAVICON_PATH.parent
            favicon_filename = config.FAVICON_PATH.name
            return send_from_directory(favicon_directory, favicon_filename)
        except Exception as e:
            app.logger.error(f"Error serving favicon: {e}")
            return "Favicon not found", 404

    # Example of a simple root route
    @app.route('/')
    def index():
        vision_content = ""
        mission_content = ""
        if config.BRAND_DIR.joinpath("vision.md").exists():
            vision_content = markdown.markdown(config.BRAND_DIR.joinpath("vision.md").read_text(encoding="utf-8"))
        if config.BRAND_DIR.joinpath("mission.txt").exists():
            mission_content = config.BRAND_DIR.joinpath("mission.txt").read_text(encoding="utf-8")
        return render_template("index.html", app_name=config.APP_NAME, vision_statement=vision_content, mission_statement=mission_content)

    # Register error handlers for common HTTP errors
    @app.errorhandler(404)
    def page_not_found(e):
        # The 'e' argument is the error instance, which we don't need to use here.
        return render_template('404.html', app_name=config.APP_NAME), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', app_name=config.APP_NAME), 500

    return app