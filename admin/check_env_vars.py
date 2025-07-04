#!/usr/bin/env python

import sys
import os
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load environment variables from .env file so os.getenv() works as expected.
load_dotenv(dotenv_path=ROOT / ".env")

def main():
    """
    Checks for the presence of critical environment variables and displays their status.
    """
    console = Console()
    REQUIRED_VARS = [
        "GOOGLE_API_KEY",
        # Add other critical environment variables here as the project grows
    ]

    table = Table(title="Required Environment Variable Check", show_header=True, header_style="bold magenta")
    table.add_column("Variable", style="dim", width=30)
    table.add_column("Status")

    all_found = True
    for var in REQUIRED_VARS:
        value = os.getenv(var)
        if value:
            # For security, show that it's set but not the value itself.
            status = "[green]✅ Set[/green]"
        else:
            status = "[red]❌ MISSING[/red]"
            all_found = False
        table.add_row(var, status)

    console.print(table)
    if not all_found:
        console.print("[yellow]Warning: One or more required environment variables are not set. This may cause errors.[/yellow]")
        return 1 # Indicate an error
    return 0 # Indicate success

if __name__ == "__main__":
    sys.exit(main())