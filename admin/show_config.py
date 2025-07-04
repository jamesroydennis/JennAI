#!/usr/bin/env python
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- Root Project Path Setup ---
# This must be done before importing from the project's config module.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env file (if it exists)
load_dotenv(dotenv_path=ROOT / ".env")

from config import config # Now we can import config
from rich.console import Console
from rich.table import Table

def show_configuration(console: Console):
    """
    Displays the project's configuration from config.py in a formatted table.
    """
    table = Table(
        title="[bold cyan]Configuration[/bold cyan]",
        header_style="bold magenta",
        show_header=True,
        box=None,
        title_justify="left", # Left-align the title
    )
    table.add_column("Configuration Key", style="grey50", width=30)
    table.add_column("Value", style="grey50")

    # Iterate through the config module's attributes
    for key in dir(config):
        # Filter for public, uppercase constants, which is the convention for config values.
        if not key.startswith("_") and key.isupper():
            value = getattr(config, key)
            # Pretty print lists for better readability
            if isinstance(value, list):
                value_str = "\n".join(f"• {item}" for item in value)
            else:
                value_str = str(value)
            table.add_row(key, value_str)
    console.print(table)

if __name__ == "__main__":
    show_configuration(Console())