import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "admin" / "templates" / "flask"
DEST_ROOT = PROJECT_ROOT / "src" / "presentation" / "api_server" / "flask_app"

# Map template files to their destination relative to DEST_ROOT
TEMPLATE_MAP = {
    "app.py.template": "app.py",
    "templates/base.html.template": "templates/base.html",
    "templates/index.html.template": "templates/index.html",
    "templates/404.html.template": "templates/404.html",
    "templates/500.html.template": "templates/500.html",
    "static/css/main.scss.template": "static/css/main.scss",
    "static/css/_variables.scss.template": "static/css/_variables.scss",
    "static/js/scripts.js.template": "static/js/scripts.js",
}

def ensure_and_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)
        print(f"Created: {dst}")
    else:
        print(f"Exists:  {dst}")

def main():
    for template_rel, dest_rel in TEMPLATE_MAP.items():
        src = TEMPLATE_DIR / template_rel
        dst = DEST_ROOT / dest_rel
        if src.exists():
            ensure_and_copy(src, dst)
        else:
            print(f"Warning: Template {src} does not exist.")
    print("\n✅ Presentation Flask starter files are in place.")

if __name__ == "__main__":
    main()