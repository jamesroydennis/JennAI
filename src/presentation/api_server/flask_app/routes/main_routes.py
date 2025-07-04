from flask import Blueprint, render_template
from pathlib import Path
import markdown

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)

def load_brand_content():
    """Load brand content from the brand directory."""
    # Use the brand directory under src/presentation/brand
    brand_dir = Path(__file__).resolve().parent.parent.parent.parent / "brand"
    
    # Load mission statement
    mission_file = brand_dir / "mission.txt"
    mission_statement = ""
    if mission_file.exists():
        mission_statement = mission_file.read_text(encoding='utf-8').strip()
    
    # Load and convert vision markdown
    vision_file = brand_dir / "vision.md"
    vision_statement = ""
    if vision_file.exists():
        vision_md = vision_file.read_text(encoding='utf-8')
        vision_statement = markdown.markdown(vision_md)
    
    # Load problem statement if available
    problem_file = brand_dir / "problem_statement.md"
    problem_statement = ""
    if problem_file.exists():
        problem_md = problem_file.read_text(encoding='utf-8')
        problem_statement = markdown.markdown(problem_md)
    
    # Load seed content if available
    seed_file = brand_dir / "seed.txt"
    seed_content = ""
    if seed_file.exists():
        seed_content = seed_file.read_text(encoding='utf-8').strip()
    
    return {
        'mission_statement': mission_statement,
        'vision_statement': vision_statement,
        'problem_statement': problem_statement,
        'seed_content': seed_content
    }

@main_bp.route('/')
def index():
    """
    Serves the main index page of the application with integrated brand content.
    """
    brand_content = load_brand_content()
    return render_template('index.html', 
                         title='JennAI - Bridging the Unyielding Question',
                         **brand_content)