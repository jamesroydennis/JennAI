#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

# ==============================================================================
# JennAI Conda Environment Creation Script
# ==============================================================================
#
# This script automates the initial creation of the 'jennai-root' conda
# environment from the 'environment.yaml' file.
#
# USAGE:
# 1. Make sure you are in your 'base' conda environment.
# 2. Run this script from the project root directory:
#    python admin/conda_create.py
#
# NOTE: If the 'jennai-root' environment already exists, this command will fail.
#       Use 'python admin/conda_update.py' to update an existing environment.
#
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_NAME = "jennai-root" # Assuming this is the name in environment.yaml

def run_creation():
    """
    Executes the conda environment creation command and streams the output.
    """
    print("=" * 70)
    print("🐍 JennAI Conda Environment Creator")
    print("=" * 70)
    print(f"\nINFO: This script will create the '{ENV_NAME}' Conda environment")
    print("      from the 'environment.yaml' file.")
    print("\nIMPORTANT: Please ensure you are running this from your 'base' conda environment.")
    print("           If the environment already exists, this script will fail.")
    print("           Use 'python admin/conda_update.py' to update an existing environment.")
    print("-" * 70)
    
    try:
        # The command to execute. It targets the environment specified in the YAML file.
        command = f"conda env create -f environment.yaml"
        
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
            print(f"\n✅ Environment '{ENV_NAME}' created successfully!")
            print(f"   Activate your environment with: conda activate {ENV_NAME}")
        else:
            print(f"\n❌ Environment creation failed with exit code: {return_code}")
            print(f"   If '{ENV_NAME}' already exists, use 'python admin/conda_update.py' instead.")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_creation()