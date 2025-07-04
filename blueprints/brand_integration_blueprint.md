# Brand Integration Blueprint
*Architect: Brand-Theme Integration Specifications*

## 1. Brand Asset Inventory

### Available Assets (from src/presentation/brand/):
```
ai.jpg                      # AI-themed imagery
background.jpg              # Primary background
background-light.jpg        # Light variant background  
circuit-dark.jpg           # Dark technical background
circuit-light.jpg          # Light technical background
heart-blackbackground.jpg  # Emotional connection (dark)
heart-blueforeground.jpg   # Emotional connection (light)
jennai-logo.png           # Primary brand logo
me.jpeg                   # Personal/founder image
person.jpg                # Human element imagery
under_construction.png    # Development status indicator

jennai-favicon_io/        # Complete favicon package
error_templates/          # Branded error pages
```

### Content Assets:
```
mission.txt              # "To bridge the unyielding question"
vision.md               # Complete vision statement
problem_statement.md    # Problem definition
theme.scss             # Brand styling source
seed.txt               # Foundational concepts
```

## 2. SCSS Theme Analysis

From `src/presentation/brand/theme.scss`:

### Typography Stack:
- **Headings:** Inter (400, 600, 700 weights)
- **Body:** Open Sans (400, 600, 700 weights)
- **Source:** Google Fonts

### Color Palette:
```scss
$theme-background: #87CEEB;    // Sky Blue (body background)
$theme-font: #333333;          // Dark grey (text)
$theme-primary: #87CEEB;       // Primary (matches background)
$theme-accent-1: rgb(197, 71, 78);  // Reddish accent
$theme-accent-2: rgb(135, 206, 235); // Light Sky Blue
$jennai-primary-comp: #008B8B;      // Dark Cyan
$jennai-secondary-comp: #FF6F61;    // Vibrant Coral Red
$jennai-neutral-dark: #1A1A1A;      // Very Dark Gray
```

### Status Colors:
```scss
$status-success: #28a745;
$status-warning: #ffc107;
$status-error: #dc3545;
$status-info: #17a2b8;
```

## 3. Asset Integration Strategy

### 3.1 Static Asset Distribution
```
Brand Source → Flask Destination
src/presentation/brand/jennai-logo.png → static/img/jennai-logo.png
src/presentation/brand/jennai-favicon_io/* → static/img/*
src/presentation/brand/theme.scss → static/css/theme.scss
src/presentation/brand/circuit-*.jpg → static/img/
src/presentation/brand/background*.jpg → static/img/
```

### 3.2 Content Integration
```
Brand Source → Flask Usage
mission.txt → Loaded into index template
vision.md → Rendered as HTML in index template  
problem_statement.md → Rendered as HTML in index template
```

### 3.3 SCSS Compilation Pipeline
1. Copy `theme.scss` from brand to `static/css/theme.scss`
2. Compile `theme.scss` → `main.css` using Dart Sass
3. Link compiled CSS in base template
4. Ensure font imports functional
5. Validate color variables applied

## 4. Template Integration Requirements

### 4.1 Base Template (`templates/base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}JennAI{% endblock %}</title>
    
    <!-- Brand Favicon Integration -->
    <link rel="icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/apple-touch-icon.png') }}">
    
    <!-- Compiled Brand Theme -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
</head>
<body>
    <header>
        <!-- Brand Logo Integration -->
        <a href="{{ url_for('main.index') }}" class="site-logo">
            <img src="{{ url_for('static', filename='img/jennai-logo.png') }}" alt="JennAI Logo">
        </a>
        <nav>
            <ul>
                <li><a href="#vision">Vision</a></li>
                <li><a href="#mission">Mission</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2025 JennAI - To bridge the unyielding question</p>
    </footer>
</body>
</html>
```

### 4.2 Index Template (`templates/index.html`)
```html
{% extends "base.html" %}

{% block content %}
    <!-- Hero Section with Brand Background -->
    <section id="hero" class="hero-section">
        <h1>Welcome to JennAI</h1>
        <p class="mission-statement">{{ mission }}</p>
    </section>
    
    <!-- Vision Section -->
    <section id="vision" class="content-section">
        <h2>Vision</h2>
        <div class="vision-content">
            {{ vision | safe }}
        </div>
    </section>
    
    <!-- Problem Statement -->
    <section id="problem" class="content-section">
        <h2>The Problem</h2>
        <div class="problem-content">
            {{ problem | safe }}
        </div>
    </section>
{% endblock %}
```

## 5. Flask Application Brand Loading

### 5.1 Brand Content Loader (`routes/main_routes.py`)
```python
from flask import Blueprint, render_template
from pathlib import Path
import markdown

main_bp = Blueprint('main', __name__)

def load_brand_content():
    """Load brand content from src/presentation/brand/"""
    brand_dir = Path('src/presentation/brand')
    
    # Load mission
    mission_file = brand_dir / 'mission.txt'
    mission = mission_file.read_text().strip() if mission_file.exists() else ''
    
    # Load and convert vision markdown
    vision_file = brand_dir / 'vision.md'
    if vision_file.exists():
        vision_md = vision_file.read_text()
        vision = markdown.markdown(vision_md)
    else:
        vision = ''
    
    # Load and convert problem statement markdown
    problem_file = brand_dir / 'problem_statement.md'
    if problem_file.exists():
        problem_md = problem_file.read_text()
        problem = markdown.markdown(problem_md)
    else:
        problem = ''
    
    return {
        'mission': mission,
        'vision': vision,
        'problem': problem
    }

@main_bp.route('/')
def index():
    brand_content = load_brand_content()
    return render_template('index.html', **brand_content)
```

## 6. Visual Design Requirements

### 6.1 Color Application
- Background: Sky blue (#87CEEB) for primary sections
- Headers: Dark cyan (#008B8B) for navigation and titles  
- Accents: Coral red (#FF6F61) for CTAs and highlights
- Text: Dark grey (#333333) for readability

### 6.2 Typography Application
- H1-H6: Inter font family, various weights
- Body text: Open Sans, 400 weight
- Navigation: Inter, 600 weight
- Emphasis: Inter, 700 weight

### 6.3 Layout Guidelines
- Max content width: 1200px
- Section padding: 4em 2em
- Header height: 80px desktop, 60px mobile
- Responsive breakpoints follow mobile-first approach

## 7. Asset Optimization Requirements

### 7.1 Image Assets
- Logo: PNG format, multiple sizes for different contexts
- Backgrounds: JPG format, optimized for web (<500kb)
- Favicon: Complete set (16x16, 32x32, 192x192, 512x512)

### 7.2 CSS Optimization
- SCSS compilation with minification
- Font loading optimization
- Critical CSS inlining for above-fold content

## 8. Testing Requirements

### 8.1 Brand Compliance Tests
- [ ] Logo displays correctly across all templates
- [ ] Brand colors match specification
- [ ] Typography renders with correct fonts
- [ ] Mission/vision content loads properly
- [ ] Favicon appears in browser tabs

### 8.2 Technical Tests
- [ ] SCSS compiles without errors
- [ ] All static assets serve correctly
- [ ] Responsive design functions properly
- [ ] Cross-browser compatibility verified

## 9. Handoff Specifications

### For Contractor:
- Complete asset inventory provided
- Integration requirements documented
- Technical feasibility confirmed
- Implementation timeline realistic

### For Constructor:
- Exact file structure specified
- Asset copying procedures defined
- Flask integration points documented
- Template requirements detailed

### For Designer:
- Brand guidelines established
- SCSS compilation instructions provided
- Visual consistency standards defined
- Asset optimization requirements set

### For Observer:
- Brand compliance checkpoints defined
- Visual quality standards established
- Content accuracy requirements specified
- Final approval criteria documented

---

**Status:** Complete and Ready for Contractor Review  
**Next Persona:** Contractor (for feasibility validation and contract creation)
