import os
from typing import Tuple

# This module relies on the calling script (e.g., admin/42.py) having
# set up the system path correctly to find the 'config' module.
from config.config import WHITELIST_ENVIRONMENTS

def validate_admin_environment() -> Tuple[bool, str]:
    """
    Checks if the script is being run from an allowed Conda environment.

    Returns:
        A tuple containing:
        - bool: True if the environment is valid, False otherwise.
        - str: A message describing the status.
    """
    current_env = os.getenv("CONDA_DEFAULT_ENV")
    if not current_env:
        return (
            False,
            "Could not determine the current Conda environment. Please ensure it is active."
        )

    current_env_name = os.path.basename(current_env)
    if current_env_name not in WHITELIST_ENVIRONMENTS:
        message = f"Incorrect Conda Environment. Allowed: {WHITELIST_ENVIRONMENTS}, Current: '{current_env_name}'."
        return False, message

    return True, f"Environment '{current_env_name}' is valid."