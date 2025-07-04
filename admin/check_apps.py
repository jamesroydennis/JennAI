#!/usr/bin/env python
"""
Application Status Checker

Provides comprehensive status checking for all PRESENTATION_APPS,
including path resolution, existence checks, and health status.
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Setup path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import PRESENTATION_APPS, PRESENTATION_DIR
from config.loguru_setup import setup_logging, logger

def get_platform_paths() -> Dict[str, Path]:
    """Returns the dictionary of all supported presentation platform paths."""
    return {
        "console": PRESENTATION_DIR / "console_app",
        "flask": PRESENTATION_DIR / "api_server" / "flask_app",
        "angular": PRESENTATION_DIR / "angular_app", 
        "react": PRESENTATION_DIR / "react_app",
        "vue": PRESENTATION_DIR / "vue_app",
    }

def check_app_status(platform_key: str) -> Dict[str, Any]:
    """
    Check the status of a specific presentation app.
    
    Returns:
        Dict containing:
        - exists: bool - whether the app directory exists
        - path: Path - the app directory path
        - name: str - the app name from config
        - display_name: str - the display name from config
        - files: list - key files found in the app
        - health: str - overall health status
    """
    platform_paths = get_platform_paths()
    app_config = PRESENTATION_APPS.get(platform_key, {})
    
    result = {
        "platform": platform_key,
        "name": app_config.get("name", f"Unknown-{platform_key}"),
        "display_name": app_config.get("display_name", platform_key.capitalize()),
        "path": platform_paths.get(platform_key),
        "exists": False,
        "files": [],
        "health": "unknown"
    }
    
    if not result["path"]:
        result["health"] = "no_path_defined"
        return result
    
    result["exists"] = result["path"].exists()
    
    if not result["exists"]:
        result["health"] = "not_scaffolded"
        return result
    
    # Check for key files based on platform type
    if platform_key == "flask":
        key_files = ["app.py", "routes", "templates", "static"]
    elif platform_key == "angular":
        key_files = ["src", "package.json", "angular.json"]
    elif platform_key == "react":
        key_files = ["src", "package.json", "public"]
    elif platform_key == "vue":
        key_files = ["src", "package.json", "vite.config.js"]
    elif platform_key == "console":
        # Console is abstract, just check if directory exists
        key_files = ["__init__.py"]
    else:
        key_files = []
    
    found_files = []
    for file_name in key_files:
        file_path = result["path"] / file_name
        if file_path.exists():
            found_files.append(file_name)
    
    result["files"] = found_files
    
    # Determine health status
    if len(found_files) == len(key_files):
        result["health"] = "healthy"
    elif len(found_files) > 0:
        result["health"] = "partial"
    else:
        result["health"] = "empty"
    
    return result

def check_all_apps() -> Dict[str, Dict[str, Any]]:
    """Check the status of all presentation apps."""
    results = {}
    for platform_key in PRESENTATION_APPS.keys():
        results[platform_key] = check_app_status(platform_key)
    return results

def print_app_status(platform_key: str = None):
    """Print the status of one or all apps."""
    if platform_key:
        status = check_app_status(platform_key)
        _print_single_status(status)
    else:
        statuses = check_all_apps()
        print("=" * 70)
        print("  PRESENTATION APPS STATUS")
        print("=" * 70)
        for platform, status in statuses.items():
            _print_single_status(status)
            print("-" * 70)

def _print_single_status(status: Dict[str, Any]):
    """Print status for a single app."""
    platform = status["platform"]
    health = status["health"]
    
    # Health status indicators
    health_icons = {
        "healthy": "✅",
        "partial": "⚠️ ",
        "empty": "❌",
        "not_scaffolded": "🏗️ ",
        "no_path_defined": "❓",
        "unknown": "❓"
    }
    
    health_messages = {
        "healthy": "Fully scaffolded and ready",
        "partial": "Partially scaffolded - missing some files",
        "empty": "Directory exists but empty",
        "not_scaffolded": "Not scaffolded - directory missing",
        "no_path_defined": "No path defined in configuration",
        "unknown": "Status unknown"
    }
    
    icon = health_icons.get(health, "❓")
    message = health_messages.get(health, "Unknown status")
    
    print(f"{icon} {status['display_name']:10} | {message}")
    print(f"   Path: {status['path']}")
    if status["exists"] and status["files"]:
        print(f"   Files: {', '.join(status['files'])}")

def test_app_status(platform_key: str = None) -> bool:
    """
    Test the status of one or all apps and return success/failure.
    This ensures status checks are also validated tests.
    """
    if platform_key:
        status = check_app_status(platform_key)
        return _test_single_status(status)
    else:
        statuses = check_all_apps()
        all_passed = True
        print("=" * 70)
        print("  PRESENTATION APPS STATUS TESTS")
        print("=" * 70)
        for platform, status in statuses.items():
            passed = _test_single_status(status)
            if not passed:
                all_passed = False
            print("-" * 70)
        
        if all_passed:
            print("✅ ALL APP STATUS TESTS PASSED")
        else:
            print("❌ SOME APP STATUS TESTS FAILED")
        
        return all_passed

def _test_single_status(status: Dict[str, Any]) -> bool:
    """Test status for a single app and return pass/fail."""
    platform = status["platform"]
    health = status["health"]
    
    # Health status indicators
    health_icons = {
        "healthy": "✅",
        "partial": "⚠️ ",
        "empty": "❌",
        "not_scaffolded": "🏗️ ",
        "no_path_defined": "❓",
        "unknown": "❓"
    }
    
    health_messages = {
        "healthy": "Fully scaffolded and ready",
        "partial": "Partially scaffolded - missing some files",
        "empty": "Directory exists but empty",
        "not_scaffolded": "Not scaffolded - directory missing",
        "no_path_defined": "No path defined in configuration",
        "unknown": "Status unknown"
    }
    
    # Determine test result
    test_passed = health in ["healthy", "partial"]  # Accept healthy and partial as passing
    test_icon = "✅ PASS" if test_passed else "❌ FAIL"
    
    icon = health_icons.get(health, "❓")
    message = health_messages.get(health, "Unknown status")
    
    print(f"{test_icon} | {icon} {status['display_name']:10} | {message}")
    print(f"       Path: {status['path']}")
    if status["exists"] and status["files"]:
        print(f"       Files: {', '.join(status['files'])}")
    
    if not test_passed:
        logger.warning(f"App status test FAILED for {platform}: {health}")
    
    return test_passed

def main():
    """Main function to run app status checks."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check presentation app status")
    parser.add_argument("--app", help="Check specific app (console, flask, angular, react, vue)")
    parser.add_argument("--test", action="store_true", help="Run as tests (return exit code based on results)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        setup_logging(debug_mode=True)
    
    try:
        if args.test:
            # Run as tests
            if args.app:
                if args.app not in PRESENTATION_APPS:
                    logger.error(f"Unknown app: {args.app}. Available: {list(PRESENTATION_APPS.keys())}")
                    sys.exit(1)
                success = test_app_status(args.app)
            else:
                success = test_app_status()
            
            # Exit with proper code for test mode
            sys.exit(0 if success else 1)
        else:
            # Run as status display
            if args.app:
                if args.app not in PRESENTATION_APPS:
                    logger.error(f"Unknown app: {args.app}. Available: {list(PRESENTATION_APPS.keys())}")
                    sys.exit(1)
                print_app_status(args.app)
            else:
                print_app_status()
    except Exception as e:
        logger.error(f"Error checking app status: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
