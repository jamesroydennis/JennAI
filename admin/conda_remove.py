#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

try:
    from InquirerPy import inquirer
except ImportError:
    # This allows the script to run and provide a basic prompt
    # even if run from an environment without InquirerPy (like 'base').
    inquirer = None

# ==============================================================================
# JennAI Conda Environment Removal Script
# ==============================================================================
#
# This script automates the complete removal of the 'jennai-root' conda
# environment. This is a DESTRUCTIVE and IRREVERSIBLE action.
#
# USAGE:
# 1. Make sure you are in your 'base' conda environment.
#    (Do NOT run this from within the 'jennai-root' environment).
# 2. Run this script from the project root directory:
#    python admin/conda_remove.py
#
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_NAME = "jennai-root"

def run_removal():
    """
    Prompts for confirmation and then executes the conda environment remove command.
    """
    print("=" * 70)
    print("🐍 JennAI Conda Environment Remover")
    print("=" * 70)
    # Use ANSI escape codes for a more prominent danger message
    print("\n\033[91mDANGER: THIS IS A DESTRUCTIVE AND IRREVERSIBLE ACTION.\033[0m")
    print(f"This script will permanently remove the '{ENV_NAME}' Conda environment.")
    print("All installed packages within it will be deleted.")
    print("\nIMPORTANT: Please ensure you are running this from your 'base' conda environment.")
    print("-" * 70)

    try:
        if inquirer:
            confirmed = inquirer.confirm(
                message=[
                    ("class:danger", "WARNING: This is a DESTRUCTIVE and IRREVERSIBLE action.\n"),
                    ("class:danger", f"All packages and data within the '{ENV_NAME}' environment will be permanently deleted.\n"),
                    ("class:default", "Are you absolutely sure you want to proceed?")
                ],
                default=False,
                confirm_message="Confirmed. Proceeding with environment removal...",
                reject_message="Operation cancelled by user."
            ).execute()
        else:
            print("\n[WARNING] InquirerPy not found. Using basic text confirmation.")
            response = input(f"Type '{ENV_NAME}' to confirm deletion: ")
            confirmed = response.strip() == ENV_NAME

        if not confirmed:
            print("Confirmation failed. Operation cancelled.")
            return

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user.")
        return

    try:
        command = f"conda env remove --name {ENV_NAME}"
        print(f"\nExecuting command: {command}\n")
        subprocess.run(command, shell=True, check=True, cwd=PROJECT_ROOT)
        print(f"\n✅ Environment '{ENV_NAME}' removed successfully!")
        print("   You can recreate it using: python admin/conda_update.py")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Environment removal failed with exit code: {e.returncode}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_removal()