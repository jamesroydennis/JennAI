#!/usr/bin/env python
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def show_env_file():
    """
    Reads and displays the contents of the .env file in a formatted table.
    Masks values for keys containing sensitive keywords for security.
    """
    console = Console()
    env_file_path = ROOT / ".env"

    table = Table(
        title="[bold cyan]Environment[/bold cyan]",
        header_style="bold magenta",
        show_header=True,
        box=None,
        title_justify="left",  # Left-align the title
    )
    table.add_column("Variable", style="grey50", width=30)
    table.add_column("Value", style="grey50")

    if not env_file_path.exists():
        table.add_row("[i]File not found[/i]", f"[grey50]{env_file_path}[/grey50]")
        console.print(table)
        return

    sensitive_keywords = ["KEY", "SECRET", "TOKEN", "PASSWORD"]

    with open(env_file_path, "r") as f:
        lines = [line for line in f.readlines() if line.strip() and not line.strip().startswith("#")]
        if not lines:
            table.add_row("[i]File is empty or contains only comments[/i]", "")

        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                # Mask sensitive values
                if any(keyword in key.upper() for keyword in sensitive_keywords):
                    value_display = "[red]******** (masked for security)[/red]"
                else:
                    value_display = value
                table.add_row(key, value_display)

    console.print(table)

if __name__ == "__main__":
    show_env_file()