import os
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAND = PROJECT_ROOT / "Brand"
PUBLIC = PROJECT_ROOT / "react-app/public"
SRC = PROJECT_ROOT / "react-app/src"
ASSETS = SRC / "assets"
STYLES = SRC / "styles"

IMAGE_MAP = {
    "jennai-logo.png": "logo.png",
    "favicon_io/favicon.ico": "favicon.ico",
    "person.jpg": "person-interacting-ai.jpg",
    "circuit-dark.jpg": "circuit-dark-bg.jpg",
    "circuit-light.jpg": "circuit-light-bg.jpg",
    "background.jpg": "abstract-wave-bg.jpg",
    "heart-blackbackground.jpg": "neon-heart.jpg",
    "me.jpeg": "your-portrait.jpg",
    # Add more as needed
}

def copy_images():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for src, dest in IMAGE_MAP.items():
        src_path = BRAND / src
        dest_path = ASSETS / dest
        if src_path.exists():
            shutil.copyfile(src_path, dest_path)
            print(f"Copied: {src_path} -> {dest_path}")
        else:
            print(f"Missing: {src_path}")

def copy_theme_scss():
    src = BRAND / "theme.scss"
    dest = STYLES / "theme.scss"
    STYLES.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copyfile(src, dest)
        print(f"Copied: {src} -> {dest}")
    else:
        print(f"Missing: {src}")

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

STARTER_FILES = {
    # Example: App.js
    "react-app/src/App.js": '''\
import React from "react";
import "./styles/theme.scss";
import logo from "./assets/logo.png";

function App() {
  return (
    <div className="App">
      <header>
        <img src={logo} alt="JennAI Logo" />
        <h1>JennAI: Illuminating the Intelligent Frontier</h1>
      </header>
      {/* Add more sections/components as needed */}
    </div>
  );
}

export default App;
''',
    # Example: index.html
    "react-app/public/index.html": '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>JennAI React</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
''',
}

def main():
    copy_images()
    copy_theme_scss()
    for file_path, content in STARTER_FILES.items():
        ensure_and_write(PROJECT_ROOT / file_path, content)
    print("\n✅ Presentation React starter files and assets are in place.")

if __name__ == "__main__":
    main()