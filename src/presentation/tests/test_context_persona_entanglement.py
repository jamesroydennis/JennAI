#!/usr/bin/env python
"""
Context-Aware Persona Entanglement Tests

These tests validate that persona entanglement behavior is properly context-aware,
meaning that persona functionality and interdependencies are evaluated based on
the actual project context (files, directories, configurations, environment state).

This builds upon the show_context.py pattern to ensure persona entanglement
tests reflect real system state rather than theoretical dependencies.
"""

import sys
import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Minimal path setup to import config
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now import from config and ensure admin path is set
from config.config import ADMIN_DIR
if str(ADMIN_DIR) not in sys.path:
    sys.path.insert(0, str(ADMIN_DIR))

# Add admin directory to path for admin imports
if str(ADMIN_DIR) not in sys.path:
    sys.path.insert(0, str(ADMIN_DIR))

from config.config import ARCHITECTURAL_PERSONAS
from admin.show_context import main as show_context_main
from admin.show_env import show_env_file
from admin.show_config import show_configuration
from admin.check_env_vars import main as check_env_vars_main
from src.presentation.tests.test_persona_entanglement import PersonaEntanglementValidator


class ContextAwareEntanglementValidator(PersonaEntanglementValidator):
    """
    Extended validator that incorporates project context into entanglement testing.
    """
    
    def __init__(self):
        super().__init__()
        self.context_state = {}
        self.context_timestamp = None
        
    def capture_project_context(self) -> dict:
        """
        Capture full project context similar to show_context.py
        """
        self.context_timestamp = datetime.now().isoformat()
        
        context = {
            "timestamp": self.context_timestamp,
            "environment": self._capture_env_context(),
            "configuration": self._capture_config_context(),
            "dependencies": self._capture_dependency_context(),
            "validation": self._capture_validation_context(),
            "tree_structure": self._capture_tree_context()
        }
        
        self.context_state = context
        return context
    
    def _capture_env_context(self) -> dict:
        """Capture environment file state"""
        env_file = ROOT / ".env"
        return {
            "env_file_exists": env_file.exists(),
            "env_file_size": env_file.stat().st_size if env_file.exists() else 0,
            "env_file_modified": env_file.stat().st_mtime if env_file.exists() else None
        }
    
    def _capture_config_context(self) -> dict:
        """Capture configuration state"""
        config_file = ROOT / "config" / "config.py"
        return {
            "config_file_exists": config_file.exists(),
            "personas_defined": len(ARCHITECTURAL_PERSONAS),
            "persona_names": list(ARCHITECTURAL_PERSONAS.keys()),
            "config_file_size": config_file.stat().st_size if config_file.exists() else 0
        }
    
    def _capture_dependency_context(self) -> dict:
        """Capture dependency state"""
        env_yaml = ROOT / "environment.yaml"
        requirements_txt = ROOT / "requirements.txt"
        
        return {
            "environment_yaml_exists": env_yaml.exists(),
            "requirements_txt_exists": requirements_txt.exists(),
            "conda_env_size": env_yaml.stat().st_size if env_yaml.exists() else 0
        }
    
    def _capture_validation_context(self) -> dict:
        """Capture validation state"""
        try:
            # Simulate env var validation without printing
            with patch('builtins.print'):
                check_env_vars_main()
            validation_passed = True
        except Exception:
            validation_passed = False
            
        return {
            "env_vars_validated": validation_passed,
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def _capture_tree_context(self) -> dict:
        """Capture project tree structure state"""
        critical_dirs = [
            ROOT / "src",
            ROOT / "src" / "presentation",
            ROOT / "config",
            ROOT / "admin",
            ROOT / "tests",
            ROOT / "logs",
            ROOT / "allure-results"
        ]
        
        return {
            "critical_directories": {
                str(d.relative_to(ROOT)): d.exists() for d in critical_dirs
            },
            "total_critical_dirs": sum(1 for d in critical_dirs if d.exists())
        }
    
    def validate_context_dependent_persona(self, persona_name: str) -> dict:
        """
        Validate persona functionality based on captured context state.
        """
        if not self.context_state:
            self.capture_project_context()
            
        validation = super().validate_persona_dependencies(persona_name)
        
        # Add context-aware validations
        context_validations = {
            "context_timestamp": self.context_timestamp,
            "context_dependencies_met": [],
            "context_dependencies_failed": [],
            "context_specific_status": "UNKNOWN"
        }
        
        # Context-specific validation logic for each persona
        if persona_name == "ARCHITECT":
            context_validations.update(self._validate_architect_context())
        elif persona_name == "CONSTRUCTOR":
            context_validations.update(self._validate_constructor_context())
        elif persona_name == "DESIGNER":
            context_validations.update(self._validate_designer_context())
        elif persona_name == "CONTRACTOR":
            context_validations.update(self._validate_contractor_context())
        elif persona_name == "QA_ENGINEER":
            context_validations.update(self._validate_qa_context())
        elif persona_name == "OBSERVER":
            context_validations.update(self._validate_observer_context())
        elif persona_name == "DATA":
            context_validations.update(self._validate_data_context())
            
        # Merge context validations with standard validations
        validation["context_validation"] = context_validations
        validation["context_aware"] = True
        
        return validation
    
    def _validate_architect_context(self) -> dict:
        """Architect requires proper configuration and environment setup"""
        config_ok = self.context_state["configuration"]["config_file_exists"]
        env_ok = self.context_state["environment"]["env_file_exists"]
        personas_complete = self.context_state["configuration"]["personas_defined"] >= 7
        
        return {
            "context_dependencies_met": [dep for dep, ok in [
                ("config_file", config_ok),
                ("env_file", env_ok), 
                ("personas_defined", personas_complete)
            ] if ok],
            "context_dependencies_failed": [dep for dep, ok in [
                ("config_file", config_ok),
                ("env_file", env_ok),
                ("personas_defined", personas_complete)
            ] if not ok],
            "context_specific_status": "HEALTHY" if all([config_ok, env_ok, personas_complete]) else "DEGRADED"
        }
    
    def _validate_constructor_context(self) -> dict:
        """Constructor requires project structure and directories"""
        critical_dirs = self.context_state["tree_structure"]["total_critical_dirs"]
        src_exists = self.context_state["tree_structure"]["critical_directories"].get("src", False)
        
        return {
            "context_dependencies_met": [
                f"critical_dirs_{critical_dirs}",
                "src_directory" if src_exists else None
            ],
            "context_dependencies_failed": [] if critical_dirs >= 5 and src_exists else ["insufficient_structure"],
            "context_specific_status": "HEALTHY" if critical_dirs >= 5 and src_exists else "CRITICAL"
        }
    
    def _validate_designer_context(self) -> dict:
        """Designer requires SCSS compilation and brand assets"""
        # Check for CSS files in presentation apps
        css_files = list(ROOT.glob("src/presentation/*/static/css/main.css"))
        scss_files = list(ROOT.glob("src/presentation/*/static/scss/*.scss"))
        
        return {
            "context_dependencies_met": [
                f"css_files_{len(css_files)}",
                f"scss_files_{len(scss_files)}"
            ],
            "context_dependencies_failed": [] if css_files else ["css_compilation_missing"],
            "context_specific_status": "HEALTHY" if css_files else "FAILED"
        }
    
    def _validate_contractor_context(self) -> dict:
        """Contractor requires validation results and contracts"""
        allure_results = ROOT / "allure-results"
        contracts_dir = ROOT / "src" / "presentation" / "contracts"
        
        allure_exists = allure_results.exists()
        contracts_exist = contracts_dir.exists() and any(contracts_dir.glob("*.md"))
        
        return {
            "context_dependencies_met": [
                "allure_results" if allure_exists else None,
                "contracts" if contracts_exist else None
            ],
            "context_dependencies_failed": [
                dep for dep, ok in [("allure_results", allure_exists), ("contracts", contracts_exist)] if not ok
            ],
            "context_specific_status": "HEALTHY" if allure_exists and contracts_exist else "DEGRADED"
        }
    
    def _validate_qa_context(self) -> dict:
        """QA Engineer requires test infrastructure and results"""
        allure_dir = ROOT / "allure-results"
        test_files = list(ROOT.glob("src/**/test_*.py")) + list(ROOT.glob("tests/**/test_*.py"))
        
        return {
            "context_dependencies_met": [
                f"test_files_{len(test_files)}",
                "allure_dir" if allure_dir.exists() else None
            ],
            "context_dependencies_failed": [] if test_files and allure_dir.exists() else ["test_infrastructure_missing"],
            "context_specific_status": "HEALTHY" if test_files and allure_dir.exists() else "CRITICAL"
        }
    
    def _validate_observer_context(self) -> dict:
        """Observer requires cross-persona visibility and logging"""
        logs_dir = ROOT / "logs"
        config_ok = self.context_state["configuration"]["config_file_exists"]
        
        return {
            "context_dependencies_met": [
                "logs_directory" if logs_dir.exists() else None,
                "configuration" if config_ok else None
            ],
            "context_dependencies_failed": [
                dep for dep, ok in [("logs", logs_dir.exists()), ("config", config_ok)] if not ok
            ],
            "context_specific_status": "HEALTHY" if logs_dir.exists() and config_ok else "DEGRADED"
        }
    
    def _validate_data_context(self) -> dict:
        """Data persona requires data directories and mock data setup"""
        data_dir = ROOT / "src" / "data"
        mock_data = list(ROOT.glob("**/mock_*.py")) + list(ROOT.glob("**/test_data/*"))
        
        return {
            "context_dependencies_met": [
                "data_directory" if data_dir.exists() else None,
                f"mock_data_files_{len(mock_data)}"
            ],
            "context_dependencies_failed": [] if data_dir.exists() else ["data_infrastructure_missing"],
            "context_specific_status": "HEALTHY" if data_dir.exists() else "DEGRADED"
        }


# Global context-aware validator
context_validator = ContextAwareEntanglementValidator()


class TestContextPersonaEntanglement:
    """
    Test suite for context-aware persona entanglement validation.
    """
    
    def test_01_context_capture_completeness(self):
        """
        ENTANGLEMENT TEST: Verify that project context capture is comprehensive.
        """
        context = context_validator.capture_project_context()
        
        required_sections = ["environment", "configuration", "dependencies", "validation", "tree_structure"]
        for section in required_sections:
            assert section in context, f"Context missing required section: {section}"
        
        assert context["timestamp"] is not None
        assert isinstance(context["configuration"]["personas_defined"], int)
        assert context["configuration"]["personas_defined"] >= 7
    
    def test_02_architect_context_entanglement(self):
        """
        ENTANGLEMENT TEST: Architect functionality depends on configuration context.
        """
        validation = context_validator.validate_context_dependent_persona("ARCHITECT")
        
        assert validation["context_aware"] is True
        assert "context_validation" in validation
        
        context_val = validation["context_validation"]
        
        # Architect should depend on config file and environment setup
        expected_deps = ["config_file", "env_file", "personas_defined"]
        for dep in expected_deps:
            assert dep in context_val["context_dependencies_met"] or dep in context_val["context_dependencies_failed"]
    
    def test_03_constructor_context_entanglement(self):
        """
        ENTANGLEMENT TEST: Constructor functionality depends on directory structure context.
        """
        validation = context_validator.validate_context_dependent_persona("CONSTRUCTOR")
        
        context_val = validation["context_validation"]
        
        # Constructor should validate directory structure exists
        assert any("critical_dirs" in dep for dep in context_val["context_dependencies_met"])
        
        # Should check for src directory specifically
        deps_met = context_val["context_dependencies_met"]
        assert "src_directory" in deps_met or "insufficient_structure" in context_val["context_dependencies_failed"]
    
    def test_04_designer_context_entanglement(self):
        """
        ENTANGLEMENT TEST: Designer functionality depends on SCSS/CSS compilation context.
        """
        validation = context_validator.validate_context_dependent_persona("DESIGNER")
        
        context_val = validation["context_validation"]
        
        # Designer should check for CSS and SCSS files
        css_deps = [dep for dep in context_val["context_dependencies_met"] if "css_files" in dep]
        scss_deps = [dep for dep in context_val["context_dependencies_met"] if "scss_files" in dep]
        
        assert css_deps or "css_compilation_missing" in context_val["context_dependencies_failed"]
        assert scss_deps  # SCSS files should be tracked regardless
    
    def test_05_contractor_context_entanglement(self):
        """
        ENTANGLEMENT TEST: Contractor functionality depends on validation and contract context.
        """
        validation = context_validator.validate_context_dependent_persona("CONTRACTOR")
        
        context_val = validation["context_validation"]
        
        # Contractor should check for allure results and contracts
        expected_context_items = ["allure_results", "contracts"]
        for item in expected_context_items:
            assert (item in context_val["context_dependencies_met"] or 
                   item in context_val["context_dependencies_failed"])
    
    def test_06_qa_engineer_context_entanglement(self):
        """
        ENTANGLEMENT TEST: QA Engineer functionality depends on test infrastructure context.
        """
        validation = context_validator.validate_context_dependent_persona("QA_ENGINEER")
        
        context_val = validation["context_validation"]
        
        # QA should validate test files and allure directory
        test_file_deps = [dep for dep in context_val["context_dependencies_met"] if "test_files" in dep]
        assert test_file_deps or "test_infrastructure_missing" in context_val["context_dependencies_failed"]
        
        # Should check for allure directory
        allure_present = "allure_dir" in context_val["context_dependencies_met"]
        allure_missing = "test_infrastructure_missing" in context_val["context_dependencies_failed"]
        assert allure_present or allure_missing
    
    def test_07_observer_context_entanglement(self):
        """
        ENTANGLEMENT TEST: Observer functionality depends on cross-persona visibility context.
        """
        validation = context_validator.validate_context_dependent_persona("OBSERVER")
        
        context_val = validation["context_validation"]
        
        # Observer should check logs and configuration
        expected_items = ["logs_directory", "configuration"]
        for item in expected_items:
            assert (item in context_val["context_dependencies_met"] or 
                   any(item.startswith(failed.split('_')[0]) for failed in context_val["context_dependencies_failed"]))
    
    def test_08_data_context_entanglement(self):
        """
        ENTANGLEMENT TEST: Data persona functionality depends on data infrastructure context.
        """
        validation = context_validator.validate_context_dependent_persona("DATA")
        
        context_val = validation["context_validation"]
        
        # Data should validate data directory and mock data
        data_dir_present = "data_directory" in context_val["context_dependencies_met"]
        data_dir_missing = "data_infrastructure_missing" in context_val["context_dependencies_failed"]
        assert data_dir_present or data_dir_missing
        
        # Should track mock data files
        mock_data_deps = [dep for dep in context_val["context_dependencies_met"] if "mock_data_files" in dep]
        assert mock_data_deps
    
    def test_09_context_cascade_entanglement(self):
        """
        ENTANGLEMENT TEST: Context changes should trigger persona cascade effects.
        """
        # Capture initial context
        initial_context = context_validator.capture_project_context()
        
        # Validate all personas with current context
        all_validations = {}
        for persona_name in ARCHITECTURAL_PERSONAS.keys():
            all_validations[persona_name] = context_validator.validate_context_dependent_persona(persona_name)
        
        # Check that context-aware validations show proper entanglement
        failed_personas = [
            name for name, validation in all_validations.items()
            if validation["context_validation"]["context_specific_status"] in ["FAILED", "CRITICAL"]
        ]
        
        # If any persona fails due to context, their dependents should be affected
        for failed_persona in failed_personas:
            cascade_impact = context_validator._calculate_cascade_impact(failed_persona)
            assert isinstance(cascade_impact, list)
            
            # Verify cascaded personas show awareness of the failure
            for impacted_persona in cascade_impact:
                if impacted_persona in all_validations:
                    impacted_validation = all_validations[impacted_persona]
                    # The impacted persona should either be blocked or show degraded status
                    assert (not impacted_validation["can_execute"] or 
                           impacted_validation["context_validation"]["context_specific_status"] != "HEALTHY")
    
    def test_10_context_recovery_entanglement(self):
        """
        ENTANGLEMENT TEST: Context improvements should enable persona recovery and cascade recovery.
        """
        # First, capture current context and identify any failures
        current_context = context_validator.capture_project_context()
        
        # Validate Designer (often fails due to CSS compilation)
        designer_validation = context_validator.validate_context_dependent_persona("DESIGNER")
        
        if designer_validation["context_validation"]["context_specific_status"] == "FAILED":
            # Designer failure should cascade to dependents
            cascade_impact = context_validator._calculate_cascade_impact("DESIGNER")
            assert "CONTRACTOR" in cascade_impact or "OBSERVER" in cascade_impact
            
            # Simulate CSS compilation fix by checking what would happen if CSS files existed
            # This represents the context change that would occur after running compile_scss.py
            mock_css_files = [ROOT / "src" / "presentation" / "api_server" / "flask_app" / "static" / "css" / "main.css"]
            
            # Test what Designer validation would look like with CSS files present
            with patch.object(Path, 'glob') as mock_glob:
                mock_glob.return_value = mock_css_files
                
                # Re-validate Designer with simulated context improvement
                improved_validation = context_validator.validate_context_dependent_persona("DESIGNER")
                
                # Designer should show improvement
                improved_status = improved_validation["context_validation"]["context_specific_status"]
                assert improved_status in ["HEALTHY", "DEGRADED"]  # Better than FAILED
                
                # This demonstrates that context changes enable persona recovery
                assert improved_status != "FAILED"
        
        # Verify that the entanglement system properly models context-dependent recovery
        assert context_validator.context_state is not None
        assert context_validator.context_timestamp is not None


if __name__ == "__main__":
    # Run the context-aware entanglement tests
    pytest.main([__file__, "-v", "--tb=short"])
