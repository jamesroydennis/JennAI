import pytest
import sys
from pathlib import Path

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import config

def test_data_directory_exists():
    """OBSERVER-DATA TEST: Verifies that the primary data directory exists."""
    assert config.DATA_DIR.exists(), f"Critique failed: The main data directory is missing at '{config.DATA_DIR}'."
    assert config.DATA_DIR.is_dir(), f"Critique failed: The path for the data directory '{config.DATA_DIR}' is not a directory."