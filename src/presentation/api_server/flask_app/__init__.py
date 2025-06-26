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

    # Register error handlers for common HTTP errors
    @app.errorhandler(404)
    def page_not_found(e):
        # The 'e' argument is the error instance, which we don't need to use here.
        return render_template('404.html', app_name=config.APP_NAME), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html', app_name=config.APP_NAME), 500

    return app