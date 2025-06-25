import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANGULAR_APP_DIR = PROJECT_ROOT / "src" / "presentation" / "angular_app"

def main():
    """Orchestrates the scaffolding of the Angular presentation layer."""
    print("--- Angular Presentation Layer Scaffolder ---")

    # 1. Check for Angular CLI
    try:
        subprocess.run(["ng", "--version"], check=True, capture_output=True, text=True)
        print("\n✅ Angular CLI ('ng' command) found.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ Angular CLI ('ng' command) not found.")
        print("   Please install it globally: npm install -g @angular/cli")
        print("   Then try again.")
        sys.exit(1)

    # 2. Guide user to run ng new if project doesn't exist
    if not ANGULAR_APP_DIR.exists() or not (ANGULAR_APP_DIR / "angular.json").exists():
        print(f"\nINFO: Angular project not found at '{ANGULAR_APP_DIR}'.")
        print("      You need to scaffold the Angular project first using the Angular CLI.")
        print("\n--- MANUAL STEP REQUIRED ---")
        print(f"1. Navigate to the parent directory: cd {ANGULAR_APP_DIR.parent}")
        print(f"2. Run Angular CLI to create the app: ng new {ANGULAR_APP_DIR.name} --directory {ANGULAR_APP_DIR.name} --skip-git")
        print("   (Choose 'SCSS' for stylesheet format when prompted).")
        print("3. Once 'ng new' completes, run this admin task again to inject brand assets.")
        print("-" * 70)
        sys.exit(0)  # Exit gracefully, as the next step (asset injection) will be done on the next run.

    print(f"\n✅ Angular project already exists at '{ANGULAR_APP_DIR}'.")
    print("   The asset injection step will run next if called from the main console.")

if __name__ == "__main__":
    main()