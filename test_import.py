#!/usr/bin/env python
"""Test script to validate 42.py imports work correctly"""

import sys
import os
from pathlib import Path

# Simulate the same setup as 42.py
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Test the imports from 42.py
    from config import config
    from config.config import ArchitecturalPersona, DEBUG_MODE
    from config.loguru_setup import setup_logging, logger
    
    # Test the check_apps import
    sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'admin'))
    from check_apps import check_app_status, test_app_status
    
    print("✅ All imports successful!")
    print("✅ check_app_status function imported correctly")
    print("✅ test_app_status function imported correctly")
    
    # Test a function call
    status = check_app_status('console')
    print(f"✅ Function call successful: Console app status = {status['health']}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
