from flask import Flask, render_template
from flask_cors import CORS
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

    # Register the new brand routes blueprint
    from .routes.brand_routes import brand_bp
    app.register_blueprint(brand_bp)

    # Example of a simple root route
    @app.route('/')
    def index():
        return render_template("index.html", app_name=config.APP_NAME)

    return app