"""
Test suite for the CONTRACTOR persona.

This file contains tests that verify the CONTRACTOR's knowledge and
preparedness. It ensures the main orchestration tool (the admin console)
is correctly configured to manage all known platforms and blueprints.
"""
import pytest
from pathlib import Path
import sys

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the CONTRACTOR's tools and the ARCHITECT's config.
from config import config
from admin.presentation_utils import get_platform_paths

PLATFORM_PATHS = get_platform_paths()


def get_constructed_platforms():
    """
    Helper function to get a list of platform keys for applications that
    have actually been constructed (i.e., their directory exists).
    The OBSERVER uses this to know what to critique.
    """
    return [key for key, path in PLATFORM_PATHS.items() if path.exists()]


@pytest.mark.parametrize("platform_key", get_constructed_platforms())
def test_observer_verifies_contractor_has_blueprint_for_constructed_platform(platform_key):
    """
    OBSERVER TEST: Verifies the CONTRACTOR has a construction script (blueprint)
    for every platform that has actually been constructed.
    """
    constructor_script = config.ADMIN_DIR / f"create_presentation_{platform_key}.py"
    assert constructor_script.exists(), \
        f"Critique failed: A constructed platform '{platform_key}' exists, but the CONTRACTOR is missing its construction blueprint at '{constructor_script}'."