#!/usr/bin/env python

import re
from pathlib import Path
import argparse
from typing import Optional, List

# --- Root Project Path Setup (if importing project modules like logger config) ---
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from loguru import logger # Using logger for this script's own messages
from config.loguru_setup import setup_logging
# from config.config import DEBUG_MODE # If you want to use global debug mode

def parse_log_file(log_file_path: Path, error_patterns: List[str], warning_patterns: Optional[List[str]] = None):
    """
    Parses a log file for specified error and warning patterns.
    """
    if not log_file_path.exists():
        logger.error(f"Log file not found: {log_file_path}")
        return False, 0, 0, [], []

    errors_found = []
    warnings_found = []
    error_count = 0
    warning_count = 0

    logger.info(f"Scanning log file: {log_file_path}")

    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors_found.append(f"L{line_number}: {line.strip()}")
                    error_count += 1
                    break # Move to next line once an error pattern is found
            
            if warning_patterns:
                for pattern in warning_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        warnings_found.append(f"L{line_number}: {line.strip()}")
                        warning_count +=1
                        break # Move to next line

    if error_count > 0:
        logger.error(f"Found {error_count} error(s) in {log_file_path}:")
        for err in errors_found[:10]: # Print first 10 errors
            logger.error(f"  {err}")
        if error_count > 10:
            logger.error(f"  ...and {error_count - 10} more errors.")
        
    if warning_patterns and warning_count > 0:
        logger.warning(f"Found {warning_count} warning(s) in {log_file_path}:")
        for warn in warnings_found[:10]: # Print first 10 warnings
            logger.warning(f"  {warn}")
        if warning_count > 10:
            logger.warning(f"  ...and {warning_count - 10} more warnings.")

    if error_count == 0 and warning_count == 0:
        logger.success(f"No critical errors or specified warnings found in {log_file_path}.")
    
    return error_count == 0, error_count, warning_count, errors_found, warnings_found

if __name__ == "__main__":
    # Setup logging for this script
    # Let's assume we want this script to be verbose by default
    setup_logging(debug_mode=True) # Or use DEBUG_MODE from config.config

    parser = argparse.ArgumentParser(description="Scan log files for errors and warnings.")
    parser.add_argument(
        "log_file", 
        nargs='?',
        default="logs/jennai.log",  # Default to the main application/session log
        help="Path to the log file to scan (relative to project root, or absolute)."
    )
    args = parser.parse_args()

    # Use the standardized ROOT variable
    log_file_to_scan = ROOT / args.log_file

    # Define patterns to look for.
    # These are case-insensitive regular expressions.
    CRITICAL_ERROR_PATTERNS = [
        r"ERROR",
        r"CRITICAL",
        r"Traceback \(most recent call last\)",
        r"ModuleNotFoundError",
        r"Exception:",
        # Add more specific critical error messages or patterns relevant to your app
    ]
    
    WARNING_PATTERNS = [
        r"WARNING",
        # Add specific warning messages you want to track
    ]

    all_ok, num_errors, num_warnings, _, _ = parse_log_file(log_file_to_scan, CRITICAL_ERROR_PATTERNS, WARNING_PATTERNS)

    if not all_ok:
        logger.error("Log scan finished with errors.")
        sys.exit(1) # Exit with a non-zero code if errors are found
    else:
        logger.success("Log scan finished successfully. No critical issues detected.")
        sys.exit(0)
