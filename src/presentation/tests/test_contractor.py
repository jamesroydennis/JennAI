"""
Test suite for the CONTRACTOR persona.

This file contains tests that verify the CONTRACTOR's ability to correctly
orchestrate and manage the various presentation platforms. It ensures that the
CONTRACTOR's tools and configurations are in sync with the ARCHITECT's master plan.
"""
import pytest
from pathlib import Path
import sys
import re

# --- Root Project Path Setup (CRITICAL for Imports) ---
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The OBSERVER needs access to the ARCHITECT's master plan (config)
# and the CONTRACTOR's testing configuration (conftest).
from config import config
from conftest import SCOPES

def test_contractor_has_test_scope_for_every_platform():
    """
    OBSERVER-CONTRACTOR TEST: Verifies that for every presentation platform
    defined by the ARCHITECT (in config.py), the CONTRACTOR has a corresponding
    test scope defined (in conftest.py).

    This ensures that the 'Test' command in the presentation console will work
    for every supported platform.
    """
    missing_scopes = []
    for platform_name in config.PRESENTATION_APPS.keys():
        # This enforces the convention for naming platform-specific test scopes.
        expected_scope_name = f"{platform_name.upper()}_PRESENTATION"
        if expected_scope_name not in SCOPES:
            missing_scopes.append(platform_name)

    assert not missing_scopes, \
        f"Critique failed: The Contractor's testing configuration (conftest.py) is missing " \
        f"test scopes for the following platforms defined by the Architect: {missing_scopes}.\n" \
        f"Please add a '{'<PLATFORM>'.upper()}_PRESENTATION' entry to the SCOPES dictionary in conftest.py."


def test_contractor_verifies_constructor_has_requirements():
    """
    OBSERVER-CONTRACTOR TEST: Verifies that for every CONSTRUCTOR script the
    CONTRACTOR can invoke (i.e., create_presentation_*.py files), a
    corresponding requirements test file (test_*_app.py) exists.

    This ensures the Contractor doesn't offer to build an application that
    has no defined quality contract.
    """
    admin_dir = config.ADMIN_DIR
    presentation_tests_dir = config.PRESENTATION_DIR / "tests"
    constructor_scripts = list(admin_dir.glob("create_presentation_*.py"))

    assert constructor_scripts, f"Contractor has no constructor scripts in {admin_dir} to test."

    missing_requirements = []
    for script in constructor_scripts:
        match = re.search(r"create_presentation_(.+)\.py", script.name)
        if not match:
            continue
        platform_name = match.group(1)

        expected_reqs_file = presentation_tests_dir / f"test_{platform_name}_app.py"
        if not expected_reqs_file.exists():
            missing_requirements.append(
                f"Constructor '{script.name}' is missing its requirements file: '{expected_reqs_file.relative_to(ROOT)}'"
            )

    assert not missing_requirements, \
        "Critique failed: The Contractor has constructor scripts that lack defined requirements (test files):\n" + "\n".join(missing_requirements)