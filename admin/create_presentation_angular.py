from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAND = PROJECT_ROOT / "Brand"
ANGULAR = PROJECT_ROOT / "angular-app"
SRC = ANGULAR / "src"
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
    # Angular main style import
    "angular-app/src/styles.scss": '''@import "styles/theme.scss";''',

    # Example Angular component (home)
    "angular-app/src/app/home/home.component.html": '''\
<header>
  <img src="assets/logo.png" alt="JennAI Logo" />
  <h1>JennAI: Illuminating the Intelligent Frontier</h1>
</header>
<!-- Add more sections/components as needed -->
''',

    "angular-app/src/app/home/home.component.ts": '''\
import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {}
''',

    "angular-app/src/app/home/home.component.scss": '''\
@import "../../styles/theme.scss";
/* Add component-specific styles here */
''',

    # Example Angular app module
    "angular-app/src/app/app.module.ts": '''\
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent
  ],
  imports: [
    BrowserModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
''',

    # Example Angular app component
    "angular-app/src/app/app.component.ts": '''\
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: '<app-home></app-home>',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {}
''',

    "angular-app/src/app/app.component.scss": '''\
/* Global app styles can go here */
''',

    # Example Angular index.html
    "angular-app/src/index.html": '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>JennAI Angular</title>
  <base href="/" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" type="image/x-icon" href="assets/favicon.ico" />
</head>
<body>
  <app-root></app-root>
</body>
</html>
''',
}

def main():
    copy_images()
    copy_theme_scss()
    for file_path, content in STARTER_FILES.items():
        ensure_and_write(PROJECT_ROOT / file_path, content)
    print("\n✅ Presentation Angular starter files and assets are in place.")

if __name__ == "__main__":
    main()