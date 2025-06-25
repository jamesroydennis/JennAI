import os
from pathlib import Path

# Define the starter files and their content
STARTER_FILES = {
    # Flask app
    "src/presentation/api_server/flask_app/app.py": '''\
from flask import Flask, render_template, Markup
import markdown

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown.markdown(text))

@app.route('/')
def index():
    vision_content = """
### Vision: Illuminating the Intelligent Frontier

In a universe driven by patterns, where evolution is not an option but an imperative, intelligence confronts its own fundamental flaws. Current AI, despite its super-adult capabilities, is designed to infer without wisdom, often generating plausible fallacy or operating in silos that render profound truths unreachable. This leads to a critical chasm: the absence of genuine understanding, where algorithms prioritize profit over value, and where automated systems can amplify the very human frailties of bias and ignorance.

**JennAI** (gen-a, with a strong 'a') is founded upon a mission to **seed the next evolutionary leap**—not through grand claims, but through a **single, focused experiment** in the realm of artificial intelligence. It will create the instrumentation necessary to illuminate AI's core inferential process, precisely identifying its inherent uncertainties and biases, and thereby equipping it to genuinely acknowledge its limits. This endeavor is built for the sake of shared existence, and its light, we trust, will inspire good 'most of the time'.

This endeavor transcends a mere technical solution. It is the genesis of a platform—a collective dedicated to discovering the fundamental question that equals **42**.
"""
    mission_statement = "To bridge the unyielding question."
    return render_template('index.html', vision=vision_content, mission=mission_statement)

if __name__ == '__main__':
    app.run(debug=True)
''',

    # Jinja templates
    "src/presentation/api_server/flask_app/templates/base.html": '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}JennAI{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <link rel="icon" href="{{ url_for('static', filename='img/favicon.ico') }}" type="image/x-icon">
    <link rel="preload" as="font" type="font/woff2" href="https://fonts.gstatic.com/s/inter/v13/UcCO3FZYIDFWav0x495nZAuGxpg.woff2" crossorigin>
    <link rel="preload" as="font" type="font/woff2" href="https://fonts.gstatic.com/s/opensans/v34/memvYaGs126MiZpBA-MtmW-Pihc.woff2" crossorigin>
    {% block head_extra %}{% endblock %}
</head>
<body>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script src="{{ url_for('static', filename='js/scripts.js') }}"></script>
    {% block body_extra %}{% endblock %}
</body>
</html>
''',

    "src/presentation/api_server/flask_app/templates/index.html": '''\
{% extends "base.html" %}
{% block title %}JennAI - Illuminating the Intelligent Frontier{% endblock %}
{% block content %}
<section>
    <h1>JennAI: Illuminating the Intelligent Frontier</h1>
    <div>{{ vision|markdown }}</div>
    <h2>Our Core Mission</h2>
    <div>{{ mission }}</div>
</section>
{% endblock %}
''',

    # SCSS and JS
    "src/presentation/api_server/flask_app/static/css/main.scss": '''\
@import 'variables';
// Add your main styles here
body { font-family: 'Open Sans', sans-serif; }
''',

    "src/presentation/api_server/flask_app/static/css/_variables.scss": '''\
// Theme variables
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Open+Sans:wght@400;600;700&display=swap');
$font-heading: 'Inter', sans-serif;
$font-body: 'Open Sans', sans-serif;
$theme-background: #87CEEB;
$theme-font: #333333;
''',

    "src/presentation/api_server/flask_app/static/js/scripts.js": '''\
// Basic JS placeholder
document.addEventListener('DOMContentLoaded', () => {
    console.log("JennAI presentation site loaded.");
});
''',
}

def ensure_and_write(path, content):
    path = Path(path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {path}")
    else:
        print(f"Exists:  {path}")

def main():
    for file_path, content in STARTER_FILES.items():
        ensure_and_write(file_path, content)
    print("\n✅ Presentation Flask starter files are in place.")

if __name__ == "__main__":
    main()