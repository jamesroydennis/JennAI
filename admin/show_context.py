#!/usr/bin/env python
import sys
import subprocess
import os
from pathlib import Path
from rich.console import Console

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import from centralized configuration
from config.config import ROOT, ADMIN_DIR

# Add admin directory to path for peer module imports
if str(ADMIN_DIR) not in sys.path:
    sys.path.insert(0, str(ADMIN_DIR))

# Import the callable functions from the modular diagnostic scripts
from show_env import show_env_file
from show_config import show_configuration
from check_env_vars import main as check_env_vars_main
from show_dependencies import show_dependencies

def main():
    """
    Orchestrates the display of the full project context by calling modular scripts
    for environment, configuration, validation, and the project tree.
    This provides a comprehensive snapshot of the project's state before a test run.
    """
    console = Console()

    # 1. Show .env file contents
    show_env_file()
    console.print() # Add spacing

    # 2. Show project dependencies from environment.yaml
    show_dependencies(console)
    console.print() # Add spacing

    # 3. Show config.py contents
    show_configuration(console)
    console.print() # Add spacing

    # 4. Show validation of required env vars
    check_env_vars_main()
    console.print() # Add spacing

    # 5. Show the project tree structure by calling tree.py
    # It's best to call this as a subprocess to correctly handle its rich output (e.g., from 'eza').
    try:
        tree_script_path = ADMIN_DIR / "tree.py"
        if tree_script_path.exists():
            subprocess.run([sys.executable, str(tree_script_path)], check=True)
        else:
            console.print(f"[yellow]Warning: tree.py not found at {tree_script_path}[/yellow]")
    except (subprocess.CalledProcessError, Exception) as e:
        console.print(f"[red]Error running tree.py: {e}[/red]")

if __name__ == "__main__":
    main()