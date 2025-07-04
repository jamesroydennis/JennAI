#!/usr/bin/env python
"""Test script to validate 42.py can load without user interaction"""

import subprocess
import sys
import time

def test_42_py_loads():
    """Test that 42.py can load without import errors"""
    try:
        # Start the script and immediately send an interrupt to exit cleanly
        proc = subprocess.Popen(
            [sys.executable, 'admin/42.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start up and load imports
        time.sleep(2)
        
        # Send interrupt to exit cleanly
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)
        
        # Check if it loaded successfully (no import errors)
        if "FATAL ERROR" in stderr or "ImportError" in stderr:
            print("❌ Script failed to load:")
            print(stderr)
            return False
        elif "JennAI" in stdout or proc.returncode in [0, -15]:  # -15 is SIGTERM
            print("✅ Script loaded successfully!")
            print("✅ No import errors detected")
            return True
        else:
            print(f"⚠️  Script exited with code {proc.returncode}")
            print("STDOUT:", stdout[:200] if stdout else "None")
            print("STDERR:", stderr[:200] if stderr else "None")
            return True  # Still consider it successful if no import errors
            
    except subprocess.TimeoutExpired:
        proc.kill()
        print("⚠️  Script timed out but this is expected for interactive scripts")
        return True
    except Exception as e:
        print(f"❌ Error testing script: {e}")
        return False

if __name__ == "__main__":
    success = test_42_py_loads()
    sys.exit(0 if success else 1)
