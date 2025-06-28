#!/usr/bin/env python
import sys
import subprocess
from pathlib import Path
from rich.console import Console

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the callable functions from the other diagnostic scripts
from admin.show_env import show_env_file
from admin.show_config import show_configuration

def main():
    """
    Displays the full project context: environment, configuration, and tree.
    This provides a comprehensive snapshot of the project's state before a test run.
    """
    console = Console()

    # Run the imported functions to display tables
    show_env_file()
    console.print() # Add spacing
    show_configuration()
    console.print() # Add spacing

    # tree.py is best called as a subprocess to capture its rich output correctly.
    try:
        tree_script_path = ROOT / "admin" / "tree.py"
        if tree_script_path.exists():
            subprocess.run([sys.executable, str(tree_script_path)], check=True)
        else:
            console.print(f"[yellow]Warning: tree.py not found at {tree_script_path}[/yellow]")
    except (subprocess.CalledProcessError, Exception) as e:
        console.print(f"[red]Error running tree.py: {e}[/red]")

if __name__ == "__main__":
    main()