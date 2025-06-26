#!/usr/bin/env python
import subprocess
import os
import yaml
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

def get_env_name_from_yaml(yaml_path: Path) -> str | None:
    """Parses the environment name from a conda environment.yaml file."""
    if not yaml_path.is_file():
        print(f"\n\033[91mERROR: Environment file not found at '{yaml_path}'.\033[0m")
        return None
    try:
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f).get('name')
    except (IOError, yaml.YAMLError) as e:
        print(f"\n\033[91mERROR: Could not read or parse '{yaml_path}': {e}\033[0m")
        return None

def run_update():
    """
    Executes the conda environment update command and streams the output.
    """
    print("=" * 70)
    print("🐍 JennAI Conda Environment Updater")
    print("=" * 70)

    # --- Dynamically get environment name ---
    yaml_file_path = PROJECT_ROOT / "environment.yaml"
    env_name = get_env_name_from_yaml(yaml_file_path)
    if not env_name:
        return

    # --- Safety Check ---
    current_env = os.getenv("CONDA_DEFAULT_ENV")
    if current_env == env_name:
        print(f"\n\033[91mERROR: This script should not be run from within the '{env_name}' environment.\033[0m")
        print("       Please deactivate and run it from your 'base' environment.")
        print("       Command: conda deactivate")
        return

    print(f"\nINFO: This script will synchronize your '{env_name}' environment with")
    print("      the 'environment.yaml' file using the '--prune' flag.")
    print("      This will add, update, and remove packages to match the file.")
    print("\nIMPORTANT: Please ensure you are running this from your 'base' conda environment.")
    print("-" * 70)
    
    try:
        # The command to execute, passed as a list for better security and robustness.
        command = [
            "conda", "env", "update",
            "--name", env_name,
            "--prune",
            "-f", str(yaml_file_path) # Use the full path for reliability
        ]
        
        # Use Popen to stream output in real-time, which is better for long tasks.
        process = subprocess.Popen(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT, text=True, encoding='utf-8'
        )
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        process.stdout.close()
        return_code = process.wait()

        if return_code == 0:
            print("\n✅ Environment update completed successfully!")
            print(f"   Activate your environment with: conda activate {env_name}")
        else:
            print(f"\n❌ Environment update failed with exit code: {return_code}")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_update()