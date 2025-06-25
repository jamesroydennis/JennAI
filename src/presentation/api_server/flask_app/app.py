from flask import Flask, render_template, url_for
import markdown # Make sure markdown is installed: pip install markdown
from markupsafe import Markup

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Add a markdown filter to Jinja2 for rendering the vision statement
    @app.template_filter('markdown')
    def markdown_filter(text):
        return Markup(markdown.markdown(text))

    with app.app_context():
        @app.route('/')
        def index():
            # Pass your mission and vision content to the template
            # In a real app, these might come from a database or markdown files dynamically parsed
            vision_content = """
### Vision: Illuminating the Intelligent Frontier

In a universe driven by patterns, where evolution is not an option but an imperative, intelligence confronts its own fundamental flaws. Current AI, despite its super-adult capabilities, is designed to infer without wisdom, often generating plausible fallacy or operating in silos that render profound truths unreachable. This leads to a critical chasm: the absence of genuine understanding, where algorithms prioritize profit over value, and where automated systems can amplify the very human frailties of bias and ignorance.

**JennAI** (gen-a, with a strong 'a') is founded upon a mission to **seed the next evolutionary leap**—not through grand claims, but through a **single, focused experiment** in the realm of artificial intelligence. It will create the instrumentation necessary to illuminate AI's core inferential process, precisely identifying its inherent uncertainties and biases, and thereby equipping it to genuinely acknowledge its limits. This endeavor is built for the sake of shared existence, and its light, we trust, will inspire good 'most of the time'.

This endeavor transcends a mere technical solution. It is the genesis of a platform—a collective dedicated to discovering the fundamental question that equals **42**.
"""
            mission_statement = "To bridge the unyielding question."
            return render_template('index.html', vision=vision_content, mission=mission_statement)

        # Error Handlers
        @app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html'), 404

        @app.errorhandler(500)
        def internal_server_error(e):
            return render_template('500.html'), 500

        # Route specifically for testing 500 errors
        @app.route('/test-500-error')
        def test_500_error_route():
            raise Exception("This is a simulated 500 error for testing purposes.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
