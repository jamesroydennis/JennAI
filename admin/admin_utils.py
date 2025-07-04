#!/usr/bin/env python
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Dict

# --- Root Project Path Setup (CRITICAL for Imports) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.loguru_setup import logger
from InquirerPy.utils import color_print
from rich.console import Console

console = Console()
SEPARATOR_LINE = "──────────────────────────────────"

def print_header(title: str):
    """Prints a standardized header to the console."""
    print()
    color_print([("cyan", "=" * 70)])
    color_print([("cyan", f"  {title.strip()}")])
    color_print([("cyan", "=" * 70)])
    print()

def _pause_for_acknowledgement(message: str = "\nPress Enter to return to the menu..."):
    """Pauses execution and waits for the user to press Enter."""
    input(message)

def run_command(command: str, cwd: Path = PROJECT_ROOT, env: Optional[Dict[str, str]] = None) -> bool:
    """
    Runs a command, streams its output in real-time, and returns True on success.
    Handles KeyboardInterrupt gracefully.
    """
    process = None
    try:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=cwd, text=True, encoding="utf-8", env=merged_env
        )

        # Stream output in real-time
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
            process.stdout.close()

        return_code = process.wait()
        return return_code == 0

    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user. Terminating subprocess...")
        if process:
            process.terminate()
            # Wait for the process to finish terminating to avoid zombie processes
            process.wait()
        return False # Treat interruption as a failure for sequence control
    except FileNotFoundError:
        logger.error(f"Error: Command not found for '{command}'. Is it installed and in your PATH?")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while running command '{command}': {e}")
        return False

def print_formatted_help(text_block: str):
    """
    Parses and prints a multi-line string as formatted Markdown to the console.
    """
    console.print(text_block, markup=False)