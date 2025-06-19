# /home/jdennis/Projects/JennAI/src/presentation/api_server/flask_app/__init__.py

from flask import Flask
from pathlib import Path

# Import the global dependency container if you plan to inject dependencies into routes
# from core.dependency_container import DependencyContainer # Assuming global_container is accessible

def create_app(container=None): # Pass container if needed for DI in routes
    """
    Application factory for the Flask app.
    """
    # Calculate path to templates and static folders relative to this file
    base_dir = Path(__file__).resolve().parent
    template_folder = base_dir / 'templates'
    static_folder = base_dir / 'static'

    app = Flask(__name__, template_folder=str(template_folder), static_folder=str(static_folder))

    # Register blueprints
    from .routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    # app.container = container # Make container accessible if needed: app.container.resolve(...)
    return app

# Add this at the end of flask_app/__init__.py for quick testing
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
