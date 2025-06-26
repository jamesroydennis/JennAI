import subprocess
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
jennai_root_for_path = Path(__file__).resolve().parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))
from config.config import SRC_DIR

REACT_APP_DIR = SRC_DIR / "presentation" / "react_app"

def main():
    """Orchestrates the scaffolding of the React presentation layer."""
    print("--- React Presentation Layer Scaffolder ---")

    # 1. Check for Node/npm/npx
    try:
        subprocess.run(["npx", "--version"], check=True, capture_output=True, text=True)
        print("\n✅ npx (Node.js) found.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ npx (Node.js) not found.")
        print("   Please install Node.js and npm (preferably using nvm) before proceeding.")
        sys.exit(1)

    # 2. Guide user to run create-react-app if project doesn't exist
    if not REACT_APP_DIR.exists() or not (REACT_APP_DIR / "package.json").exists():
        print(f"\nINFO: React project not found at '{REACT_APP_DIR}'.")
        print("      You need to scaffold the React project first using create-react-app.")
        print("\n--- MANUAL STEP REQUIRED ---")
        print(f"1. Navigate to the parent directory: cd {REACT_APP_DIR.parent}")
        print(f"2. Run create-react-app: npx create-react-app {REACT_APP_DIR.name}")
        print("3. Once complete, run this admin task again to inject brand assets.")
        print("-" * 70)
        sys.exit(0)  # Exit gracefully, as the next step (asset injection) will be done on the next run.

    print(f"\n✅ React project already exists at '{REACT_APP_DIR}'.")
    print("   The asset injection step will run next if called from the main console.")

if __name__ == "__main__":
    main()