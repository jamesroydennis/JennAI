"""
REAL-WORLD PERSONA FAILURE VALIDATION TESTS

This test suite validates persona health against the actual project state,
detecting real failures that exist in the current codebase and infrastructure.

Unlike synthetic failure mode tests, these tests check for actual issues:
- Missing files and directories that should exist
- Incomplete configurations or setup
- Broken dependencies or tool chains
- Platform-specific issues in the current environment

These tests serve as both validation and documentation of the current project state.
"""

import pytest
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

# Import project configuration and validators
from config.config import (
    ARCHITECTURAL_PERSONAS, ROOT, BRAND_DIR, DATA_DIR, PRESENTATION_DIR,
    ADMIN_DIR, CONFIG_DIR, SRC_DIR, NOTEBOOKS_DIR, LOGS_DIR,
    DB_PATH, LOG_FILE
)
from src.presentation.tests.test_persona_entanglement import PersonaEntanglementValidator
from src.presentation.tests.test_context_persona_entanglement import ContextAwareEntanglementValidator


class TestRealWorldArchitectFailures:
    """Test actual Architect persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_architect_root_directory_accessibility(self, validator):
        """
        REAL FAILURE CHECK: Verify project root is accessible and readable.
        
        Architect needs full access to project root for blueprint creation.
        """
        assert ROOT.exists(), f"Project root directory missing: {ROOT}"
        assert ROOT.is_dir(), f"Project root is not a directory: {ROOT}"
        assert os.access(ROOT, os.R_OK), f"Project root not readable: {ROOT}"
        assert os.access(ROOT, os.W_OK), f"Project root not writable: {ROOT}"
        
        # Validate Architect can see critical project files
        critical_files = ["pyproject.toml", "requirements.txt", "main.py", "README.md"]
        missing_files = []
        
        for file_name in critical_files:
            file_path = ROOT / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            health = validator.validate_persona_health("ARCHITECT")
            # Document this as expected failure if files are actually missing
            pytest.fail(f"Architect missing critical files: {missing_files}")
    
    def test_architect_configuration_completeness(self, validator):
        """
        REAL FAILURE CHECK: Verify all configuration files are complete and valid.
        
        Architect depends on complete configuration for blueprint accuracy.
        """
        config_file = CONFIG_DIR / "config.py"
        assert config_file.exists(), f"Main configuration file missing: {config_file}"
        
        # Check if ARCHITECTURAL_PERSONAS is properly defined
        assert len(ARCHITECTURAL_PERSONAS) >= 7, "Incomplete persona definitions in config"
        
        # Verify each persona has required fields
        required_fields = ["name", "description", "icon", "responsibilities"]
        incomplete_personas = []
        
        for persona_name, persona_config in ARCHITECTURAL_PERSONAS.items():
            for field in required_fields:
                if field not in persona_config:
                    incomplete_personas.append(f"{persona_name}.{field}")
        
        assert not incomplete_personas, f"Incomplete persona configs: {incomplete_personas}"
    
    def test_architect_admin_tools_availability(self, validator):
        """
        REAL FAILURE CHECK: Verify admin tools are present and functional.
        
        Architect delegates work through admin tools and scripts.
        """
        critical_admin_tools = [
            "admin_utils.py",
            "create_directories.py",
            "show_context.py",
            "setup_environment.py"
        ]
        
        missing_tools = []
        for tool in critical_admin_tools:
            tool_path = ADMIN_DIR / tool
            if not tool_path.exists():
                missing_tools.append(tool)
        
        if missing_tools:
            health = validator.validate_persona_health("ARCHITECT")
            pytest.fail(f"Architect missing admin tools: {missing_tools}")


class TestRealWorldConstructorFailures:
    """Test actual Constructor persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_constructor_package_json_validity(self, validator):
        """
        REAL FAILURE CHECK: Verify package.json exists and is valid.
        
        Constructor needs package.json for framework scaffolding.
        """
        package_json = ROOT / "package.json"
        assert package_json.exists(), "package.json missing - Constructor cannot scaffold"
        
        # Try to parse package.json
        import json
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            # Check for essential fields
            essential_fields = ["name", "version"]
            missing_fields = [field for field in essential_fields if field not in package_data]
            
            if missing_fields:
                pytest.fail(f"package.json missing essential fields: {missing_fields}")
                
        except json.JSONDecodeError as e:
            pytest.fail(f"package.json is invalid JSON: {e}")
    
    def test_constructor_python_environment(self, validator):
        """
        REAL FAILURE CHECK: Verify Python environment is properly configured.
        
        Constructor needs working Python environment for development.
        """
        # Check Python version
        python_version = sys.version_info
        assert python_version.major >= 3, f"Python major version too old: {python_version.major}"
        assert python_version.minor >= 7, f"Python minor version too old: {python_version.minor}"
        
        # Check if virtual environment is active (optional but recommended)
        venv_active = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if not venv_active:
            # Document this as a warning, not a failure
            print("WARNING: No virtual environment detected - recommended for isolation")
    
    def test_constructor_requirements_satisfaction(self, validator):
        """
        REAL FAILURE CHECK: Verify all Python requirements are installed.
        
        Constructor cannot scaffold without required dependencies.
        """
        requirements_file = ROOT / "requirements.txt"
        if not requirements_file.exists():
            pytest.skip("requirements.txt not found - skipping dependency check")
        
        # Read requirements
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing_packages = []
        for requirement in requirements:
            # Parse package name (handle versions, extras, etc.)
            package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('[')[0]
            
            try:
                __import__(package_name.replace('-', '_'))
            except ImportError:
                try:
                    __import__(package_name)
                except ImportError:
                    missing_packages.append(package_name)
        
        if missing_packages:
            pytest.fail(f"Constructor missing required packages: {missing_packages}")
    
    def test_constructor_directory_structure(self, validator):
        """
        REAL FAILURE CHECK: Verify core directory structure exists.
        
        Constructor should have created essential project directories.
        """
        essential_dirs = [SRC_DIR, CONFIG_DIR, ADMIN_DIR, LOGS_DIR]
        missing_dirs = []
        
        for dir_path in essential_dirs:
            if not dir_path.exists():
                missing_dirs.append(str(dir_path))
            elif not dir_path.is_dir():
                missing_dirs.append(f"{dir_path} (not a directory)")
        
        if missing_dirs:
            pytest.fail(f"Constructor missing essential directories: {missing_dirs}")


class TestRealWorldDesignerFailures:
    """Test actual Designer persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_designer_brand_assets_availability(self, validator):
        """
        REAL FAILURE CHECK: Verify brand assets directory and contents.
        
        Designer cannot apply branding without brand assets.
        """
        if not BRAND_DIR.exists():
            pytest.fail(f"Brand directory missing: {BRAND_DIR}")
        
        # Check for common brand asset types
        expected_asset_types = ['.css', '.scss', '.png', '.svg', '.jpg', '.jpeg']
        found_assets = []
        
        for asset_file in BRAND_DIR.rglob('*'):
            if asset_file.is_file() and asset_file.suffix.lower() in expected_asset_types:
                found_assets.append(asset_file.suffix.lower())
        
        if not found_assets:
            pytest.fail(f"No brand assets found in {BRAND_DIR}")
    
    def test_designer_scss_compilation_capability(self, validator):
        """
        REAL FAILURE CHECK: Verify SCSS compilation tools are available.
        
        Designer needs SCSS compilation for styling workflow.
        """
        # Check if SCSS compiler is available
        scss_tools = ['sass', 'node-sass', 'dart-sass']
        available_tool = None
        
        for tool in scss_tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    available_tool = tool
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        if not available_tool:
            pytest.fail("No SCSS compilation tool available (sass, node-sass, dart-sass)")
    
    def test_designer_presentation_directories(self, validator):
        """
        REAL FAILURE CHECK: Verify presentation platform directories exist.
        
        Designer needs target directories for different presentation platforms.
        """
        presentation_platforms = [
            PRESENTATION_DIR / "api_server" / "flask_app",
            PRESENTATION_DIR / "webapp" / "react_app",
            PRESENTATION_DIR / "webapp" / "vue_app",
            PRESENTATION_DIR / "webapp" / "angular_app",
            PRESENTATION_DIR / "console_app"
        ]
        
        missing_platforms = []
        for platform_dir in presentation_platforms:
            if not platform_dir.exists():
                missing_platforms.append(str(platform_dir.relative_to(ROOT)))
        
        # Some platforms may be optional, but at least one should exist
        if len(missing_platforms) == len(presentation_platforms):
            pytest.fail("No presentation platform directories found")


class TestRealWorldContractorFailures:
    """Test actual Contractor persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_contractor_integration_readiness(self, validator):
        """
        REAL FAILURE CHECK: Verify all components are ready for integration.
        
        Contractor validates that Constructor and Designer work is complete.
        """
        # Check if Constructor work is complete
        constructor_artifacts = [
            ROOT / "pyproject.toml",
            SRC_DIR / "__init__.py",
            CONFIG_DIR / "__init__.py"
        ]
        
        missing_constructor_work = []
        for artifact in constructor_artifacts:
            if not artifact.exists():
                missing_constructor_work.append(str(artifact.relative_to(ROOT)))
        
        if missing_constructor_work:
            pytest.fail(f"Constructor work incomplete: {missing_constructor_work}")
        
        # Check if Designer work has target locations
        designer_targets = [
            PRESENTATION_DIR / "brand",
            # Add other expected designer output locations
        ]
        
        missing_designer_targets = []
        for target in designer_targets:
            if not target.exists():
                missing_designer_targets.append(str(target.relative_to(ROOT)))
        
        # This might be expected if Designer hasn't run yet
        if missing_designer_targets:
            print(f"INFO: Designer targets not yet created: {missing_designer_targets}")
    
    def test_contractor_dependency_resolution(self, validator):
        """
        REAL FAILURE CHECK: Verify all project dependencies are resolved.
        
        Contractor ensures no dependency conflicts or missing requirements.
        """
        # Check for common dependency issues
        potential_conflicts = []
        
        # Check if there are multiple requirements files that might conflict
        req_files = list(ROOT.glob("*requirements*.txt")) + list(ROOT.glob("*requirements*.in"))
        if len(req_files) > 1:
            potential_conflicts.append(f"Multiple requirements files: {[f.name for f in req_files]}")
        
        # Check if pyproject.toml and requirements.txt both exist (potential conflict)
        if (ROOT / "pyproject.toml").exists() and (ROOT / "requirements.txt").exists():
            potential_conflicts.append("Both pyproject.toml and requirements.txt exist")
        
        if potential_conflicts:
            print(f"WARNING: Potential dependency conflicts: {potential_conflicts}")


class TestRealWorldQAEngineerFailures:
    """Test actual QA Engineer persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_qa_test_infrastructure(self, validator):
        """
        REAL FAILURE CHECK: Verify test infrastructure is properly set up.
        
        QA Engineer needs complete test infrastructure for validation.
        """
        # Check for test configuration files
        test_configs = [
            ROOT / "pytest.ini",
            ROOT / "conftest.py",
            # Could also check for .coverage, tox.ini, etc.
        ]
        
        missing_configs = []
        for config in test_configs:
            if not config.exists():
                missing_configs.append(config.name)
        
        if missing_configs:
            pytest.fail(f"Test configuration missing: {missing_configs}")
        
        # Check for test directories
        test_dirs = list(ROOT.rglob("*test*"))
        test_dirs = [d for d in test_dirs if d.is_dir()]
        
        if not test_dirs:
            pytest.fail("No test directories found")
    
    def test_qa_pytest_functionality(self, validator):
        """
        REAL FAILURE CHECK: Verify pytest is installed and functional.
        
        QA Engineer depends on pytest for test execution.
        """
        try:
            import pytest as pytest_module
            
            # Check pytest version
            pytest_version = pytest_module.__version__
            print(f"INFO: pytest version {pytest_version} available")
            
        except ImportError:
            pytest.fail("pytest not installed - QA Engineer cannot function")
    
    def test_qa_coverage_tools(self, validator):
        """
        REAL FAILURE CHECK: Verify code coverage tools are available.
        
        QA Engineer needs coverage tools for comprehensive testing.
        """
        coverage_tools = ['coverage', 'pytest-cov']
        available_tools = []
        
        for tool in coverage_tools:
            try:
                __import__(tool.replace('-', '_'))
                available_tools.append(tool)
            except ImportError:
                continue
        
        if not available_tools:
            print("WARNING: No coverage tools available (coverage, pytest-cov)")


class TestRealWorldObserverFailures:
    """Test actual Observer persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_observer_cross_validation_capability(self, validator):
        """
        REAL FAILURE CHECK: Verify Observer can access all persona outputs.
        
        Observer needs visibility into all other persona work for validation.
        """
        # Check access to key directories for cross-validation
        validation_targets = [
            CONFIG_DIR,      # Architect outputs
            SRC_DIR,         # Constructor outputs  
            BRAND_DIR,       # Designer outputs
            ROOT / "tests",  # QA Engineer outputs
            LOGS_DIR         # General system outputs
        ]
        
        inaccessible_targets = []
        for target in validation_targets:
            if target.exists():
                if not os.access(target, os.R_OK):
                    inaccessible_targets.append(f"{target} (not readable)")
            else:
                inaccessible_targets.append(f"{target} (missing)")
        
        if inaccessible_targets:
            pytest.fail(f"Observer cannot access: {inaccessible_targets}")
    
    def test_observer_compliance_checking_tools(self, validator):
        """
        REAL FAILURE CHECK: Verify tools for compliance checking are available.
        
        Observer needs linting, formatting, and validation tools.
        """
        compliance_tools = ['flake8', 'black', 'mypy', 'pylint']
        available_tools = []
        
        for tool in compliance_tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    available_tools.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        if not available_tools:
            print("WARNING: No compliance checking tools available")


class TestRealWorldDataFailures:
    """Test actual Data persona failures in current project state."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    def test_data_directory_structure(self, validator):
        """
        REAL FAILURE CHECK: Verify data directory structure exists.
        
        Data persona needs proper directory structure for data management.
        """
        if not DATA_DIR.exists():
            pytest.fail(f"Data directory missing: {DATA_DIR}")
        
        # Check for expected data subdirectories
        expected_subdirs = ["samples", "mock", "schemas"]
        missing_subdirs = []
        
        for subdir in expected_subdirs:
            subdir_path = DATA_DIR / subdir
            if not subdir_path.exists():
                missing_subdirs.append(subdir)
        
        # Some subdirectories might be created on demand
        if missing_subdirs:
            print(f"INFO: Data subdirectories not yet created: {missing_subdirs}")
    
    def test_data_database_configuration(self, validator):
        """
        REAL FAILURE CHECK: Verify database configuration and connectivity.
        
        Data persona needs working database configuration.
        """
        # Check if database path is configured
        assert DB_PATH is not None, "Database path not configured"
        
        # Check if database directory is writable
        db_dir = DB_PATH.parent
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True)
            except OSError as e:
                pytest.fail(f"Cannot create database directory: {e}")
        
        assert os.access(db_dir, os.W_OK), f"Database directory not writable: {db_dir}"
    
    def test_data_mock_generation_tools(self, validator):
        """
        REAL FAILURE CHECK: Verify mock data generation tools are available.
        
        Data persona needs tools for generating test and mock data.
        """
        mock_tools = ['faker', 'factory_boy']
        available_tools = []
        
        for tool in mock_tools:
            try:
                __import__(tool)
                available_tools.append(tool)
            except ImportError:
                continue
        
        if not available_tools:
            print("WARNING: No mock data generation tools available")


# ============================================================================
# INTEGRATION TESTS FOR REAL FAILURES
# ============================================================================

class TestRealWorldSystemIntegration:
    """Test real-world system integration and cross-persona failures."""
    
    @pytest.fixture
    def validator(self):
        return PersonaEntanglementValidator()
    
    @pytest.fixture
    def context_validator(self):
        return ContextAwareEntanglementValidator()
    
    def test_complete_system_health_check(self, validator, context_validator):
        """
        INTEGRATION TEST: Comprehensive real-world system health check.
        
        Validates all personas against actual project state and identifies
        real failures that need attention.
        """
        health_report = {}
        
        for persona_name in ARCHITECTURAL_PERSONAS.keys():
            try:
                # Test basic persona health
                basic_health = validator.validate_persona_health(persona_name)
                
                # Test context-aware health
                context = context_validator._capture_project_context()
                context_health = context_validator._validate_persona_context_health(persona_name, context)
                
                health_report[persona_name] = {
                    "basic_health": basic_health,
                    "context_health": context_health,
                    "can_proceed": validator._check_persona_can_proceed(persona_name)
                }
                
            except Exception as e:
                health_report[persona_name] = {
                    "error": str(e),
                    "basic_health": {"healthy": False, "issues": [f"Exception: {e}"]},
                    "context_health": {"healthy": False, "issues": [f"Exception: {e}"]},
                    "can_proceed": False
                }
        
        # Analyze overall system health
        healthy_personas = sum(1 for health in health_report.values() 
                             if health.get("basic_health", {}).get("healthy", False))
        total_personas = len(ARCHITECTURAL_PERSONAS)
        
        print(f"\nSystem Health Report:")
        print(f"Healthy personas: {healthy_personas}/{total_personas}")
        
        for persona_name, health in health_report.items():
            status = "✓" if health.get("basic_health", {}).get("healthy", False) else "✗"
            print(f"{status} {persona_name}")
            
            if not health.get("basic_health", {}).get("healthy", False):
                issues = health.get("basic_health", {}).get("issues", [])
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"    - {issue}")
        
        # System should have at least some healthy personas
        assert healthy_personas > 0, "Complete system failure - no healthy personas"
        
        # Document any widespread failures
        if healthy_personas < total_personas * 0.5:
            print(f"WARNING: System health below 50% ({healthy_personas}/{total_personas})")
    
    def test_cascade_impact_with_real_failures(self, validator):
        """
        INTEGRATION TEST: Test cascade impacts with actual project failures.
        
        Identifies real failure cascades that are currently affecting the system.
        """
        # First identify actually failed personas
        failed_personas = []
        
        for persona_name in ARCHITECTURAL_PERSONAS.keys():
            health = validator.validate_persona_health(persona_name)
            if not health.get("healthy", True):
                failed_personas.append(persona_name)
        
        if not failed_personas:
            print("INFO: No persona failures detected")
            return
        
        print(f"Detected failed personas: {failed_personas}")
        
        # Calculate real cascade impacts
        total_cascade_impact = set()
        
        for failed_persona in failed_personas:
            cascade = validator._calculate_cascade_impact(failed_persona)
            total_cascade_impact.update(cascade)
            print(f"{failed_persona} failure cascades to: {cascade}")
        
        # Calculate recovery order for real failures
        if failed_personas:
            recovery_order = validator._calculate_recovery_order(failed_personas)
            print(f"Recommended recovery order: {recovery_order}")
        
        # Document the scope of real failures
        cascade_percentage = len(total_cascade_impact) / len(ARCHITECTURAL_PERSONAS) * 100
        print(f"Total cascade impact: {len(total_cascade_impact)}/{len(ARCHITECTURAL_PERSONAS)} personas ({cascade_percentage:.1f}%)")


# ============================================================================
# PYTEST CONFIGURATION FOR REAL-WORLD TESTS
# ============================================================================

def pytest_configure(config):
    """Configure pytest for real-world failure testing."""
    # Add custom markers
    config.addinivalue_line("markers", "real_failure: mark test as checking real project failures")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "health_check: mark test as system health check")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to properly categorize real-world tests."""
    for item in items:
        # Mark all tests in this file as real failure tests
        item.add_marker(pytest.mark.real_failure)
        
        # Mark integration tests
        if "integration" in item.name.lower() or "system" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark health check tests
        if "health" in item.name.lower():
            item.add_marker(pytest.mark.health_check)
