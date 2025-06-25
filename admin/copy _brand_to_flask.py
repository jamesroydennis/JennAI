import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = PROJECT_ROOT / "src" / "presentation" / "brand"
FLASK_STATIC_IMG = PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app" / "static" / "img"
FLASK_STATIC_CSS = PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app" / "static" / "css"
FLASK_TEMPLATES = PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app" / "templates"

# List of files to copy (add more as needed)
FILES_TO_COPY = [
    ("jennai-logo.png", FLASK_STATIC_IMG),
    ("favicon_io/favicon.ico", FLASK_STATIC_IMG),
    ("under_construction.png", FLASK_STATIC_IMG),
    ("theme.scss", FLASK_STATIC_CSS),
    ("mission.txt", FLASK_TEMPLATES),
    ("vision.md", FLASK_TEMPLATES),
]

def main():
    for rel_file, dest_dir in FILES_TO_COPY:
        src = BRAND_DIR / rel_file
        dest_dir.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy2(src, dest_dir / src.name)
            print(f"Copied {src} -> {dest_dir / src.name}")
        else:
            print(f"Warning: {src} does not exist.")

if __name__ == "__main__":
    main()