#!/usr/bin/env python

import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import config
from config.loguru_setup import setup_logging, logger # type: ignore

def main():
    setup_logging(debug_mode=config.DEBUG_MODE)

    missing_vars = []
    for name, value in config.__dict__.items():
        if name.startswith("REQUIRED_ENV_") and not value:  # Assuming required vars have a Falsey default
            env_var_name = name[len("REQUIRED_ENV_"):]
            if not env_var_name.isupper(): # Enforce screaming snake case
                logger.warning(f"Config variable '{name}' should follow 'REQUIRED_ENV_SCREAMING_SNAKE_CASE' naming.")
            if not config.ROOT.joinpath(f".env").exists():
                logger.warning(f".env file not found, skipping environment variable check for '{env_var_name}'")
            elif not config.ROOT.joinpath(f".env").read_text().find(env_var_name + "=") > 0:
                missing_vars.append(env_var_name)

    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        return 1  # Indicate an error
    else:
        logger.success("All required environment variables are present in the loaded .env file.")
        return 0  # Indicate success

if __name__ == "__main__":
    sys.exit(main())