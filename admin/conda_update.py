#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# ==============================================================================
# JennAI Conda Environment Update Script
# ==============================================================================
#
# This script automates the process of synchronizing the 'jennai-root' conda
# environment with the 'environment.yaml' file.
#
# USAGE:
# 1. Make sure you are in your 'base' conda environment.
#    (Do NOT run this from within the 'jennai-root' environment).
# 2. Run this script from the project root directory:
#    python admin/conda_update.py
#
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_update():
    """
    Executes the conda environment update command and streams the output.
    """
    print("=" * 70)
    print("🐍 JennAI Conda Environment Updater")
    print("=" * 70)
    print("\nINFO: This script will synchronize your 'jennai-root' environment with")
    print("      the 'environment.yaml' file using the '--prune' flag.")
    print("      This will add, update, and remove packages to match the file.")
    print("\nIMPORTANT: Please ensure you are running this from your 'base' conda environment.")
    print("-" * 70)
    
    try:
        # The command to execute. It targets the environment specified in the YAML file.
        command = f"conda env update --prune -f environment.yaml"
        
        # Use Popen to stream output in real-time, which is better for long tasks.
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT, text=True, encoding='utf-8'
        )
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        process.stdout.close()
        return_code = process.wait()

        if return_code == 0:
            print("\n✅ Environment update completed successfully!")
            print(f"   Activate your environment with: conda activate jennai-root")
        else:
            print(f"\n❌ Environment update failed with exit code: {return_code}")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_update()