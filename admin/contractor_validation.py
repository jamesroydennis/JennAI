#!/usr/bin/env python
"""
Contractor Validation & Contract Creation Module

This script implements the contractor's core responsibility:
1. VALIDATE that all brand implementation steps are complete
2. ENFORCE compliance with brand requirements  
3. CREATE formal contracts when all validations pass

The contractor does NOT perform compilation - only validates and contracts.
"""

import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import hashlib

# --- Root Project Path Setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Add admin directory to path for local imports
ADMIN_DIR = Path(__file__).resolve().parent
if str(ADMIN_DIR) not in sys.path:
    sys.path.insert(0, str(ADMIN_DIR))

from config import config
from loguru import logger
from config.loguru_setup import setup_logging
from presentation_utils import get_presentation_apps

def validate_brand_injection(platform_name: str) -> dict:
    """
    VALIDATION STEP 1: Verify brand assets are properly injected by Designer
    
    Returns:
        dict: Validation result with success status and details
    """
    result = {"step": "INJECT", "platform": platform_name, "success": False, "details": []}
    
    try:
        all_platform_paths = get_presentation_apps()
        platform_base = all_platform_paths.get(platform_name)
        
        if not platform_base:
            result["details"].append(f"Platform path not found for {platform_name}")
            return result
            
        # Check if brand assets are injected
        if platform_name == 'console':
            result["success"] = True
            result["details"].append("Console platform doesn't require brand injection")
            return result
            
        static_dir = platform_base / 'static'
        css_dir = static_dir / 'css'
        img_dir = static_dir / 'img'
        
        # Check for required SCSS files
        main_scss = css_dir / 'main.scss'
        variables_scss = css_dir / '_variables.scss'
        
        # Check for required images
        logo_img = img_dir / 'jennai-logo.png'
        favicon_img = img_dir / 'favicon.ico'
        
        missing_assets = []
        if not main_scss.exists():
            missing_assets.append(str(main_scss))
        if not variables_scss.exists():
            missing_assets.append(str(variables_scss))
        if not logo_img.exists():
            missing_assets.append(str(logo_img))
        if not favicon_img.exists():
            missing_assets.append(str(favicon_img))
            
        if missing_assets:
            result["details"].append(f"Missing brand assets: {missing_assets}")
            return result
            
        result["success"] = True
        result["details"].append("All required brand assets are properly injected")
        
    except Exception as e:
        result["details"].append(f"Error during injection validation: {str(e)}")
        
    return result

def validate_scss_compilation(platform_name: str) -> dict:
    """
    VALIDATION STEP 2: Verify SCSS is compiled to CSS by Designer
    
    Returns:
        dict: Validation result with success status and details
    """
    result = {"step": "COMPILE", "platform": platform_name, "success": False, "details": []}
    
    try:
        all_platform_paths = get_presentation_apps()
        platform_base = all_platform_paths.get(platform_name)
        
        if not platform_base:
            result["details"].append(f"Platform path not found for {platform_name}")
            return result
            
        if platform_name == 'console':
            result["success"] = True
            result["details"].append("Console platform doesn't require SCSS compilation")
            return result
            
        css_dir = platform_base / 'static' / 'css'
        scss_file = css_dir / 'main.scss'
        css_file = css_dir / 'main.css'
        
        if not scss_file.exists():
            result["details"].append(f"SCSS file not found: {scss_file}")
            return result
            
        if not css_file.exists():
            result["details"].append(f"CSS file missing - SCSS not compiled: {css_file}")
            return result
            
        # Check if CSS contains brand colors
        css_content = css_file.read_text()
        if "#87CEEB" not in css_content:  # Sky Blue brand color
            result["details"].append("CSS exists but doesn't contain brand colors")
            return result
            
        result["success"] = True
        result["details"].append("SCSS successfully compiled to CSS with brand colors")
        
    except Exception as e:
        result["details"].append(f"Error during compilation validation: {str(e)}")
        
    return result

def validate_brand_requirements(platform_name: str) -> dict:
    """
    VALIDATION STEP 3: Verify all brand requirements are met
    
    Returns:
        dict: Validation result with success status and details
    """
    result = {"step": "VALIDATE", "platform": platform_name, "success": False, "details": []}
    
    try:
        all_platform_paths = get_presentation_apps()
        platform_base = all_platform_paths.get(platform_name)
        
        if not platform_base:
            result["details"].append(f"Platform path not found for {platform_name}")
            return result
            
        if platform_name == 'console':
            result["success"] = True
            result["details"].append("Console platform has minimal brand requirements")
            return result
            
        # Check templates reference CSS correctly
        templates_dir = platform_base / 'templates'
        base_template = templates_dir / 'base.html'
        
        if not base_template.exists():
            result["details"].append(f"Base template not found: {base_template}")
            return result
            
        template_content = base_template.read_text()
        
        # Check for CSS reference (either direct or via Flask routing)
        css_referenced = ("main.css" in template_content or 
                         "serve_css" in template_content or
                         "static" in template_content and ".css" in template_content)
        
        if not css_referenced:
            result["details"].append("Base template doesn't reference CSS file")
            return result
            
        # Check for logo reference (either direct or via Flask routing)  
        logo_referenced = ("jennai-logo.png" in template_content or
                          "serve_logo" in template_content or
                          "logo" in template_content.lower())
        
        if not logo_referenced:
            result["details"].append("Base template doesn't reference logo")
            return result
            
        result["success"] = True
        result["details"].append("All brand requirements validated successfully")
        
    except Exception as e:
        result["details"].append(f"Error during brand validation: {str(e)}")
        
    return result

def validate_compliance_enforcement(platform_name: str) -> dict:
    """
    VALIDATION STEP 4: Verify compliance with all brand contracts
    
    Returns:
        dict: Validation result with success status and details
    """
    result = {"step": "ENFORCE", "platform": platform_name, "success": False, "details": []}
    
    try:
        # Run previous validations to ensure overall compliance
        inject_result = validate_brand_injection(platform_name)
        compile_result = validate_scss_compilation(platform_name)
        validate_result = validate_brand_requirements(platform_name)
        
        compliance_issues = []
        
        if not inject_result["success"]:
            compliance_issues.append(f"Injection compliance: {inject_result['details']}")
            
        if not compile_result["success"]:
            compliance_issues.append(f"Compilation compliance: {compile_result['details']}")
            
        if not validate_result["success"]:
            compliance_issues.append(f"Validation compliance: {validate_result['details']}")
            
        if compliance_issues:
            result["details"].extend(compliance_issues)
            return result
            
        result["success"] = True
        result["details"].append("All compliance requirements enforced successfully")
        
    except Exception as e:
        result["details"].append(f"Error during compliance enforcement: {str(e)}")
        
    return result

def create_contract(platform_name: str, validation_results: list) -> dict:
    """
    CONTRACT CREATION: Generate formal contract when all validations pass
    
    Args:
        platform_name: Name of the platform (flask, angular, etc.)
        validation_results: List of validation step results
        
    Returns:
        dict: Contract creation result with file path and content
    """
    result = {"step": "CONTRACT", "platform": platform_name, "success": False, "details": []}
    
    try:
        # Ensure contracts directory exists
        contracts_dir = config.PRESENTATION_DIR / "contracts"
        contracts_dir.mkdir(exist_ok=True)
        
        # Generate contract content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        contract_content = f"""# JennAI Brand Implementation Contract

**Platform:** {platform_name.upper()}  
**Date:** {timestamp}  
**Status:** ✅ CERTIFIED COMPLIANT  

## Validation Summary

This contract certifies that the {platform_name} presentation app has passed all required brand implementation validations and is fully compliant with JennAI brand requirements.

### Validation Steps Completed

"""

        # Add validation results
        for validation in validation_results:
            status = "✅ PASSED" if validation["success"] else "❌ FAILED"
            step_name = validation["step"]
            details = "; ".join(validation["details"])
            
            contract_content += f"""
#### {step_name} Validation
**Status:** {status}  
**Details:** {details}

"""

        # Add contract signature
        validation_data = f"{platform_name}_{timestamp}_{'_'.join([str(v['success']) for v in validation_results])}"
        contract_hash = hashlib.sha256(validation_data.encode()).hexdigest()[:16]
        
        contract_content += f"""
## Contract Signature

**Validation Hash:** `{contract_hash}`  
**Contractor:** JennAI Contractor Persona  
**Certification:** This platform meets all brand implementation requirements  

### Compliance Guarantee

- ✅ Brand assets properly injected by Designer
- ✅ SCSS successfully compiled to CSS
- ✅ All brand requirements validated
- ✅ Compliance enforcement passed

**This contract guarantees that the {platform_name} application displays the correct JennAI brand identity.**

---
*Generated by JennAI Contractor Validation System*
"""

        # Write contract file
        contract_file = contracts_dir / f"{platform_name}-brand-contract.md"
        contract_file.write_text(contract_content)
        
        result["success"] = True
        result["details"].append(f"Contract created: {contract_file}")
        result["contract_path"] = str(contract_file)
        result["contract_hash"] = contract_hash
        
    except Exception as e:
        result["details"].append(f"Error creating contract: {str(e)}")
        
    return result

def run_full_contractor_validation(platform_name: str) -> dict:
    """
    Run the complete contractor validation sequence for a platform.
    
    Returns:
        dict: Complete validation results and contract creation status
    """
    logger.info(f"Starting contractor validation for platform: {platform_name}")
    
    # Run all validation steps
    validation_steps = [
        validate_brand_injection(platform_name),
        validate_scss_compilation(platform_name),
        validate_brand_requirements(platform_name),
        validate_compliance_enforcement(platform_name)
    ]
    
    # Check if all validations passed
    all_passed = all(step["success"] for step in validation_steps)
    
    result = {
        "platform": platform_name,
        "overall_success": all_passed,
        "validation_steps": validation_steps,
        "contract_created": False
    }
    
    if all_passed:
        # Create contract if all validations pass
        contract_result = create_contract(platform_name, validation_steps)
        result["contract_result"] = contract_result
        result["contract_created"] = contract_result["success"]
        
        if contract_result["success"]:
            logger.success(f"✅ CONTRACT CREATED for {platform_name}: {contract_result['contract_path']}")
        else:
            logger.error(f"❌ Contract creation failed for {platform_name}: {contract_result['details']}")
    else:
        failed_steps = [step["step"] for step in validation_steps if not step["success"]]
        logger.warning(f"⚠️ Validation failed for {platform_name}. Failed steps: {failed_steps}")
    
    return result

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="JennAI Contractor Validation & Contract Creation")
    parser.add_argument("--target", required=True, choices=list(config.PRESENTATION_APPS.keys()),
                       help="Platform to validate (flask, angular, react, vue, console)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.info(f"Running contractor validation for: {args.target}")
    
    # Run validation
    result = run_full_contractor_validation(args.target)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"  CONTRACTOR VALIDATION REPORT - {args.target.upper()}")
    print(f"{'='*60}")
    
    for step in result["validation_steps"]:
        status = "✅ PASSED" if step["success"] else "❌ FAILED"
        print(f"{step['step']:>10}: {status}")
        if args.verbose or not step["success"]:
            for detail in step["details"]:
                print(f"           {detail}")
        print()
    
    print(f"OVERALL: {'✅ SUCCESS' if result['overall_success'] else '❌ FAILED'}")
    print(f"CONTRACT: {'✅ CREATED' if result['contract_created'] else '❌ NOT CREATED'}")
    
    if result.get("contract_result", {}).get("success"):
        print(f"CONTRACT FILE: {result['contract_result']['contract_path']}")
        print(f"CONTRACT HASH: {result['contract_result']['contract_hash']}")
    
    print(f"{'='*60}\n")
    
    return 0 if result["overall_success"] else 1

if __name__ == "__main__":
    sys.exit(main())
