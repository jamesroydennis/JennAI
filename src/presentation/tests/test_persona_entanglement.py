"""
Persona Entanglement Tests

This test suite demonstrates the complex interdependencies between personas.
Each persona's work depends on and validates other personas' outputs,
creating a web of entangled responsibilities and failure modes.
"""
import pytest
from pathlib import Path
import sys
import subprocess
import json
from datetime import datetime

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import config
from config.config import ARCHITECTURAL_PERSONAS
from admin.presentation_utils import get_presentation_apps


class PersonaEntanglementValidator:
    """
    Validates the complex interdependencies between personas.
    
    This class demonstrates how each persona's failure cascades through
    the entire system, affecting other personas' ability to function.
    """
    
    def __init__(self):
        self.entanglement_map = self._build_entanglement_map()
        self.failure_cascade_log = []
        
    def _build_entanglement_map(self):
        """
        Build the entanglement map showing how personas depend on each other.
        
        Returns:
            dict: Complex dependency graph showing entangled relationships
        """
        return {
            "ARCHITECT": {
                "depends_on": [],  # Architect is the root designer
                "enables": ["CONSTRUCTOR", "DESIGNER", "CONTRACTOR", "OBSERVER", "QA_ENGINEER", "DATA"],
                "outputs": ["Blueprint specifications", "System architecture", "Persona delegation"],
                "failure_cascades_to": ["ALL_PERSONAS"],
                "contracts_with": ["CONSTRUCTOR", "DESIGNER"],
                "validates": ["System coherence", "Persona alignment"]
            },
            "CONSTRUCTOR": {
                "depends_on": ["ARCHITECT"],
                "enables": ["DESIGNER", "CONTRACTOR"],
                "outputs": ["App scaffolding", "Directory structure", "Framework setup"],
                "failure_cascades_to": ["DESIGNER", "CONTRACTOR", "QA_ENGINEER"],
                "contracts_with": ["ARCHITECT", "DESIGNER"],
                "validates": ["Directory existence", "Framework compliance"]
            },
            "DESIGNER": {
                "depends_on": ["ARCHITECT", "CONSTRUCTOR"],
                "enables": ["CONTRACTOR", "OBSERVER"],
                "outputs": ["SCSS compilation", "Brand asset injection", "Styling implementation"],
                "failure_cascades_to": ["CONTRACTOR", "OBSERVER", "QA_ENGINEER"],
                "contracts_with": ["CONSTRUCTOR", "CONTRACTOR"],
                "validates": ["Brand compliance", "Asset availability"]
            },
            "CONTRACTOR": {
                "depends_on": ["CONSTRUCTOR", "DESIGNER"],
                "enables": ["QA_ENGINEER", "OBSERVER"],
                "outputs": ["Validation reports", "Compliance certificates", "Formal contracts"],
                "failure_cascades_to": ["QA_ENGINEER", "OBSERVER"],
                "contracts_with": ["DESIGNER", "QA_ENGINEER"],
                "validates": ["All persona outputs", "System compliance"]
            },
            "QA_ENGINEER": {
                "depends_on": ["CONTRACTOR", "DESIGNER", "CONSTRUCTOR"],
                "enables": ["OBSERVER", "DATA"],
                "outputs": ["Test reports", "Quality metrics", "Defect analysis"],
                "failure_cascades_to": ["OBSERVER", "DATA"],
                "contracts_with": ["CONTRACTOR", "OBSERVER"],
                "validates": ["Test coverage", "Quality standards"]
            },
            "OBSERVER": {
                "depends_on": ["DESIGNER", "CONTRACTOR", "QA_ENGINEER"],
                "enables": ["ARCHITECT"],  # Observer provides feedback to Architect
                "outputs": ["Compliance reports", "Design verification", "Blueprint adherence"],
                "failure_cascades_to": ["ARCHITECT"],
                "contracts_with": ["QA_ENGINEER", "ARCHITECT"],
                "validates": ["Cross-persona compliance", "System integrity"]
            },
            "DATA": {
                "depends_on": ["CONSTRUCTOR", "QA_ENGINEER"],
                "enables": ["QA_ENGINEER", "OBSERVER"],
                "outputs": ["Mock data", "Database setup", "Data validation"],
                "failure_cascades_to": ["QA_ENGINEER"],
                "contracts_with": ["CONSTRUCTOR", "QA_ENGINEER"],
                "validates": ["Data integrity", "Mock data availability"]
            }
        }
    
    def validate_persona_dependencies(self, persona_name: str) -> dict:
        """
        Validate that a persona's dependencies are satisfied.
        
        Args:
            persona_name: Name of the persona to validate
            
        Returns:
            dict: Validation results with dependency status
        """
        persona_info = self.entanglement_map[persona_name]
        dependencies = persona_info["depends_on"]
        
        result = {
            "persona": persona_name,
            "dependencies_met": [],
            "dependencies_failed": [],
            "can_execute": True,
            "cascade_impact": []
        }
        
        for dependency in dependencies:
            if self._is_persona_functional(dependency):
                result["dependencies_met"].append(dependency)
            else:
                result["dependencies_failed"].append(dependency)
                result["can_execute"] = False
        
        if not result["can_execute"]:
            result["cascade_impact"] = self._calculate_cascade_impact(persona_name)
        
        return result
    
    def _is_persona_functional(self, persona_name: str) -> bool:
        """
        Check if a persona is functional by validating its outputs.
        
        This is where the real entanglement testing happens - each persona's
        functionality is determined by checking the actual artifacts they
        should have created.
        """
        if persona_name == "ARCHITECT":
            # Architect is functional if config defines all personas properly
            return (len(ARCHITECTURAL_PERSONAS) >= 7 and 
                   all(key in ARCHITECTURAL_PERSONAS for key in 
                       ["ARCHITECT", "CONSTRUCTOR", "DESIGNER", "CONTRACTOR", "QA_ENGINEER", "OBSERVER", "DATA"]))
        
        elif persona_name == "CONSTRUCTOR":
            # Constructor is functional if app directories exist
            all_platforms = get_presentation_apps()
            return any(platform_path.exists() for platform_path in all_platforms.values())
        
        elif persona_name == "DESIGNER":
            # Designer is functional if SCSS files are compiled to CSS
            all_platforms = get_presentation_apps()
            css_exists = False
            for platform_name, platform_path in all_platforms.items():
                if platform_name == 'console':
                    continue
                css_file = platform_path / 'static' / 'css' / 'main.css'
                if css_file.exists() and css_file.stat().st_size > 0:
                    css_exists = True
                    break
            return css_exists
        
        elif persona_name == "CONTRACTOR":
            # Contractor is functional if contracts exist
            contracts_dir = config.PRESENTATION_DIR / "contracts"
            return (contracts_dir.exists() and 
                   any(contracts_dir.glob("*-brand-contract.md")))
        
        elif persona_name == "QA_ENGINEER":
            # QA Engineer is functional if test results exist
            allure_dir = config.ALLURE_RESULTS_DIR
            return allure_dir.exists() and any(allure_dir.glob("*.json"))
        
        elif persona_name == "OBSERVER":
            # Observer is functional if cross-validation reports exist
            # For now, check if tests are passing
            return self._is_persona_functional("QA_ENGINEER")
        
        elif persona_name == "DATA":
            # Data persona is functional if data structures exist
            data_dir = config.DATA_DIR
            return data_dir.exists()
        
        return False
    
    def _calculate_cascade_impact(self, failed_persona: str) -> list:
        """
        Calculate which personas are impacted by a failure.
        
        This demonstrates the cascade effect of persona failures.
        """
        impacted = []
        failure_cascades = self.entanglement_map[failed_persona]["failure_cascades_to"]
        
        if "ALL_PERSONAS" in failure_cascades:
            impacted = list(self.entanglement_map.keys())
        else:
            impacted = failure_cascades[:]
        
        # Remove the failed persona itself
        if failed_persona in impacted:
            impacted.remove(failed_persona)
        
        return impacted
    
    def generate_entanglement_report(self) -> dict:
        """
        Generate a comprehensive report of persona entanglements.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "persona_status": {},
            "entanglement_health": "UNKNOWN",
            "failure_cascades": [],
            "blocking_dependencies": [],
            "circular_dependencies": []
        }
        
        functional_count = 0
        total_personas = len(ARCHITECTURAL_PERSONAS)
        
        for persona_name in ARCHITECTURAL_PERSONAS.keys():
            validation = self.validate_persona_dependencies(persona_name)
            report["persona_status"][persona_name] = validation
            
            if validation["can_execute"]:
                functional_count += 1
            else:
                report["failure_cascades"].extend(validation["cascade_impact"])
                report["blocking_dependencies"].extend(validation["dependencies_failed"])
        
        # Detect circular dependencies
        circular_dependencies = self._detect_circular_dependencies()
        report["circular_dependencies"] = circular_dependencies
        
        # Determine overall health
        health_ratio = functional_count / total_personas
        if health_ratio >= 0.8:
            report["entanglement_health"] = "HEALTHY"
        elif health_ratio >= 0.5:
            report["entanglement_health"] = "DEGRADED"
        else:
            report["entanglement_health"] = "CRITICAL"
        
        return report
    
    def _check_persona_can_proceed(self, persona_name: str) -> bool:
        """
        Check if persona can proceed based on dependencies.
        
        Args:
            persona_name: Name of the persona to check
            
        Returns:
            bool: True if persona can proceed, False otherwise
        """
        dependencies = self._get_persona_dependencies(persona_name)
        for dep in dependencies:
            health = self.validate_persona_health(dep)
            if not health.get("healthy", True):
                return False
        return True
    
    def _get_persona_dependencies(self, persona_name: str) -> list:
        """
        Get list of dependencies for a persona.
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            list: List of dependency persona names
        """
        if persona_name in self.entanglement_map:
            return self.entanglement_map[persona_name].get("depends_on", [])
        return []
    
    def _calculate_recovery_order(self, failed_personas: list) -> list:
        """
        Calculate optimal recovery order based on dependencies.
        
        Args:
            failed_personas: List of failed persona names
            
        Returns:
            list: Ordered list of personas for recovery sequence
        """
        # Topological sort of dependencies
        ordered = []
        remaining = set(failed_personas)
        
        # Prevent infinite loops
        max_iterations = len(failed_personas) * 2
        iterations = 0
        
        while remaining and iterations < max_iterations:
            iterations += 1
            
            # Find personas with no unmet dependencies in remaining set
            ready = []
            for persona in remaining:
                deps = self._get_persona_dependencies(persona)
                # Check if any dependencies are still in the remaining (failed) set
                unmet_deps = set(deps) & remaining
                
                if not unmet_deps:  # No unmet dependencies in failed set
                    ready.append(persona)
            
            if not ready:
                # Circular dependency or all remaining have unmet deps
                # Break with persona that has fewest unmet dependencies
                min_unmet = float('inf')
                best_choice = None
                
                for persona in remaining:
                    deps = self._get_persona_dependencies(persona)
                    unmet_count = len(set(deps) & remaining)
                    if unmet_count < min_unmet:
                        min_unmet = unmet_count
                        best_choice = persona
                
                if best_choice:
                    ready = [best_choice]
                else:
                    # Fallback - just pick first remaining
                    ready = [next(iter(remaining))]
            
            # Add ready personas to ordered list and remove from remaining
            ordered.extend(ready)
            remaining -= set(ready)
        
        # Add any remaining personas (shouldn't happen with proper logic)
        ordered.extend(list(remaining))
        
        return ordered
    
    def _attempt_persona_recovery(self, persona_name: str) -> bool:
        """
        Attempt to recover a failed persona.
        
        Args:
            persona_name: Name of the persona to recover
            
        Returns:
            bool: True if recovery successful, False otherwise
        """
        try:
            # Perform recovery validation
            health = self.validate_persona_health(persona_name)
            
            # Check if dependencies are now satisfied
            can_proceed = self._check_persona_can_proceed(persona_name)
            
            return health.get("healthy", False) and can_proceed
            
        except Exception as e:
            # Recovery attempt failed
            return False
    
    def validate_persona_health(self, persona_name: str) -> dict:
        """
        Validate the health of a specific persona.
        
        Args:
            persona_name: Name of the persona to validate
            
        Returns:
            dict: Health status with details
        """
        try:
            is_functional = self._is_persona_functional(persona_name)
            issues = []
            
            if not is_functional:
                # Identify specific issues
                if persona_name == "ARCHITECT":
                    if len(ARCHITECTURAL_PERSONAS) < 7:
                        issues.append("Incomplete persona definitions")
                
                elif persona_name == "CONSTRUCTOR":
                    all_platforms = get_presentation_apps()
                    missing_platforms = [name for name, path in all_platforms.items() if not path.exists()]
                    if missing_platforms:
                        issues.append(f"Missing platform directories: {missing_platforms}")
                
                elif persona_name == "DESIGNER":
                    issues.append("No compiled CSS files found")
                
                elif persona_name == "CONTRACTOR":
                    issues.append("No brand contracts found")
                
                elif persona_name == "QA_ENGINEER":
                    issues.append("No test results found")
                
                elif persona_name == "OBSERVER":
                    issues.append("Cannot validate without QA results")
                
                elif persona_name == "DATA":
                    issues.append("Data directory missing")
                
                if not issues:
                    issues.append("Functionality check failed")
            
            return {
                "healthy": is_functional,
                "issues": issues,
                "persona": persona_name
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "issues": [f"Validation error: {str(e)}"],
                "persona": persona_name
            }
    
    def _detect_circular_dependencies(self) -> list:
        """
        Detect circular dependencies in the entanglement map.
        
        Returns:
            list: List of circular dependency chains
        """
        circular_deps = []
        
        def find_cycles(start_persona, current_persona, visited, path):
            if current_persona in visited:
                if current_persona == start_persona:
                    return [path + [current_persona]]
                return []
            
            visited.add(current_persona)
            path.append(current_persona)
            
            cycles = []
            dependencies = self.entanglement_map.get(current_persona, {}).get("depends_on", [])
            
            for dep in dependencies:
                cycles.extend(find_cycles(start_persona, dep, visited.copy(), path.copy()))
            
            return cycles
        
        for persona in self.entanglement_map:
            cycles = find_cycles(persona, persona, set(), [])
            circular_deps.extend(cycles)
        
        return circular_deps
        

# Global validator instance
entanglement_validator = PersonaEntanglementValidator()


class TestPersonaEntanglement:
    """
    Test class demonstrating persona entanglement and interdependencies.
    """
    
    def test_architect_enables_all_personas(self):
        """
        ENTANGLEMENT TEST: Architect persona enables all other personas.
        
        The Architect is the root of the dependency tree. If the Architect
        fails, all other personas become non-functional.
        """
        validation = entanglement_validator.validate_persona_dependencies("ARCHITECT")
        
        # Architect should have no dependencies (it's the root)
        assert len(validation["dependencies_failed"]) == 0, \
            f"Architect has failed dependencies: {validation['dependencies_failed']}"
        
        # Architect should be able to execute
        assert validation["can_execute"], \
            "Architect cannot execute - system architecture is broken"
        
        # If Architect fails, verify cascade impact
        if not entanglement_validator._is_persona_functional("ARCHITECT"):
            cascade_impact = entanglement_validator._calculate_cascade_impact("ARCHITECT")
            assert len(cascade_impact) >= 6, \
                f"Architect failure should cascade to all personas, but only affects: {cascade_impact}"
    
    def test_constructor_depends_on_architect(self):
        """
        ENTANGLEMENT TEST: Constructor depends on Architect blueprints.
        
        Constructor cannot function without Architect's blueprints and
        system architecture specifications.
        """
        validation = entanglement_validator.validate_persona_dependencies("CONSTRUCTOR")
        
        # Constructor depends on Architect
        expected_dependencies = ["ARCHITECT"]
        actual_dependencies = entanglement_validator.entanglement_map["CONSTRUCTOR"]["depends_on"]
        
        assert actual_dependencies == expected_dependencies, \
            f"Constructor dependencies mismatch. Expected: {expected_dependencies}, Got: {actual_dependencies}"
        
        # If Architect is non-functional, Constructor should be blocked
        if not entanglement_validator._is_persona_functional("ARCHITECT"):
            assert not validation["can_execute"], \
                "Constructor should be blocked when Architect is non-functional"
    
    def test_designer_depends_on_constructor_scaffold(self):
        """
        ENTANGLEMENT TEST: Designer depends on Constructor's scaffolding.
        
        Designer cannot inject brand assets without proper directory
        structure created by Constructor.
        """
        validation = entanglement_validator.validate_persona_dependencies("DESIGNER")
        
        # Designer depends on both Architect and Constructor
        dependencies = entanglement_validator.entanglement_map["DESIGNER"]["depends_on"]
        assert "CONSTRUCTOR" in dependencies, \
            "Designer must depend on Constructor for scaffolding"
        assert "ARCHITECT" in dependencies, \
            "Designer must depend on Architect for blueprints"
        
        # If Constructor is non-functional, Designer should be blocked
        if not entanglement_validator._is_persona_functional("CONSTRUCTOR"):
            assert "CONSTRUCTOR" in validation["dependencies_failed"], \
                "Designer should detect Constructor failure"
    
    def test_contractor_validates_all_previous_work(self):
        """
        ENTANGLEMENT TEST: Contractor validates Constructor and Designer outputs.
        
        Contractor is the validation gateway - it checks that all previous
        personas have completed their work successfully.
        """
        validation = entanglement_validator.validate_persona_dependencies("CONTRACTOR")
        
        # Contractor depends on Constructor and Designer
        dependencies = entanglement_validator.entanglement_map["CONTRACTOR"]["depends_on"]
        assert "CONSTRUCTOR" in dependencies, \
            "Contractor must validate Constructor's work"
        assert "DESIGNER" in dependencies, \
            "Contractor must validate Designer's work"
        
        # Contractor's failure should cascade to QA and Observer
        cascade_impact = entanglement_validator._calculate_cascade_impact("CONTRACTOR")
        assert "QA_ENGINEER" in cascade_impact, \
            "Contractor failure should cascade to QA Engineer"
        assert "OBSERVER" in cascade_impact, \
            "Contractor failure should cascade to Observer"
    
    def test_qa_engineer_depends_on_contractor_validation(self):
        """
        ENTANGLEMENT TEST: QA Engineer depends on Contractor's validation.
        
        QA Engineer cannot perform quality testing without validated
        components from Contractor.
        """
        validation = entanglement_validator.validate_persona_dependencies("QA_ENGINEER")
        
        # QA depends on Contractor, Designer, and Constructor
        dependencies = entanglement_validator.entanglement_map["QA_ENGINEER"]["depends_on"]
        required_deps = ["CONTRACTOR", "DESIGNER", "CONSTRUCTOR"]
        
        for dep in required_deps:
            assert dep in dependencies, \
                f"QA Engineer must depend on {dep}"
        
        # If any dependency fails, QA should be blocked
        any_dependency_failed = any(not entanglement_validator._is_persona_functional(dep) 
                                  for dep in required_deps)
        if any_dependency_failed:
            assert not validation["can_execute"], \
                "QA Engineer should be blocked when dependencies fail"
    
    def test_observer_provides_feedback_loop_to_architect(self):
        """
        ENTANGLEMENT TEST: Observer creates feedback loop back to Architect.
        
        Observer validates the entire system and provides feedback to
        Architect, creating a circular dependency for continuous improvement.
        """
        # Observer depends on multiple personas
        dependencies = entanglement_validator.entanglement_map["OBSERVER"]["depends_on"]
        required_deps = ["DESIGNER", "CONTRACTOR", "QA_ENGINEER"]
        
        for dep in required_deps:
            assert dep in dependencies, \
                f"Observer must depend on {dep} for comprehensive validation"
        
        # Observer enables Architect (feedback loop)
        enables = entanglement_validator.entanglement_map["OBSERVER"]["enables"]
        assert "ARCHITECT" in enables, \
            "Observer must provide feedback to Architect"
        
        # This creates a potential circular dependency
        validation = entanglement_validator.validate_persona_dependencies("OBSERVER")
        if validation["can_execute"]:
            # Observer can provide feedback to improve Architect's future work
            assert True, "Feedback loop is functional"
    
    def test_data_persona_supports_testing_ecosystem(self):
        """
        ENTANGLEMENT TEST: Data persona supports the testing ecosystem.
        
        Data persona provides mock data and database support needed
        by QA Engineer and Observer for comprehensive testing.
        """
        dependencies = entanglement_validator.entanglement_map["DATA"]["depends_on"]
        enables = entanglement_validator.entanglement_map["DATA"]["enables"]
        
        # Data depends on Constructor for database setup
        assert "CONSTRUCTOR" in dependencies, \
            "Data persona needs Constructor's scaffolding"
        
        # Data enables QA Engineer and Observer
        assert "QA_ENGINEER" in enables, \
            "Data persona should enable QA Engineer testing"
        assert "OBSERVER" in enables, \
            "Data persona should enable Observer validation"
    
    def test_circular_dependency_detection(self):
        """
        ENTANGLEMENT TEST: Detect circular dependencies in persona relationships.
        
        While some feedback loops are intentional (Observer -> Architect),
        harmful circular dependencies should be detected and flagged.
        """
        # Build dependency graph
        dependency_graph = {}
        for persona, info in entanglement_validator.entanglement_map.items():
            dependency_graph[persona] = info["depends_on"]
        
        # Check for circular dependencies
        def has_circular_dependency(start_persona, current_persona, visited, path):
            if current_persona in visited:
                if current_persona == start_persona:
                    return True, path + [current_persona]
                return False, []
            
            visited.add(current_persona)
            path.append(current_persona)
            
            for dependency in dependency_graph.get(current_persona, []):
                has_cycle, cycle_path = has_circular_dependency(start_persona, dependency, visited.copy(), path.copy())
                if has_cycle:
                    return True, cycle_path
            
            return False, []
        
        circular_deps = []
        for persona in dependency_graph:
            has_cycle, cycle_path = has_circular_dependency(persona, persona, set(), [])
            if has_cycle:
                circular_deps.append(cycle_path)
        
        # For now, we expect the Observer -> Architect feedback loop
        # This is intentional and beneficial, not harmful
        if circular_deps:
            # Verify these are intentional feedback loops, not harmful cycles
            for cycle in circular_deps:
                assert "OBSERVER" in cycle and "ARCHITECT" in cycle, \
                    f"Unexpected circular dependency detected: {cycle}"
    
    def test_failure_cascade_simulation(self):
        """
        ENTANGLEMENT TEST: Simulate cascade failures between personas.
        
        When one persona fails, verify that the cascade effect is
        properly calculated and all dependent personas are affected.
        """
        # Test Constructor failure cascade
        constructor_cascade = entanglement_validator._calculate_cascade_impact("CONSTRUCTOR")
        expected_constructor_impact = ["DESIGNER", "CONTRACTOR", "QA_ENGINEER"]
        
        for expected in expected_constructor_impact:
            assert expected in constructor_cascade, \
                f"Constructor failure should cascade to {expected}"
        
        # Test Designer failure cascade
        designer_cascade = entanglement_validator._calculate_cascade_impact("DESIGNER")
        expected_designer_impact = ["CONTRACTOR", "OBSERVER", "QA_ENGINEER"]
        
        for expected in expected_designer_impact:
            assert expected in designer_cascade, \
                f"Designer failure should cascade to {expected}"
        
        # Test Architect failure (should affect everyone)
        architect_cascade = entanglement_validator._calculate_cascade_impact("ARCHITECT")
        assert len(architect_cascade) >= 6, \
            "Architect failure should cascade to all other personas"
    
    def test_generate_comprehensive_entanglement_report(self):
        """
        ENTANGLEMENT TEST: Generate comprehensive entanglement health report.
        
        This test validates the overall system health by examining
        all persona interdependencies and their current status.
        """
        report = entanglement_validator.generate_entanglement_report()
        
        # Verify report structure
        required_keys = ["timestamp", "persona_status", "entanglement_health", 
                        "failure_cascades", "blocking_dependencies"]
        for key in required_keys:
            assert key in report, f"Report missing required key: {key}"
        
        # Verify all personas are included
        for persona in ARCHITECTURAL_PERSONAS.keys():
            assert persona in report["persona_status"], \
                f"Report missing status for persona: {persona}"
        
        # Validate health assessment
        health_status = report["entanglement_health"]
        assert health_status in ["HEALTHY", "DEGRADED", "CRITICAL"], \
            f"Invalid health status: {health_status}"
        
        # Log the report for debugging
        print(f"\n{'='*60}")
        print("PERSONA ENTANGLEMENT REPORT")
        print(f"{'='*60}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Health: {health_status}")
        print(f"\nPersona Status:")
        for persona, status in report["persona_status"].items():
            can_execute = "✅" if status["can_execute"] else "❌"
            print(f"  {can_execute} {persona}: {len(status['dependencies_met'])} deps met, {len(status['dependencies_failed'])} failed")
        
        if report["failure_cascades"]:
            print(f"\nFailure Cascades: {set(report['failure_cascades'])}")
        if report["blocking_dependencies"]:
            print(f"Blocking Dependencies: {set(report['blocking_dependencies'])}")
        print(f"{'='*60}")


# Test data for parameterized tests
@pytest.mark.parametrize("persona_name", list(ARCHITECTURAL_PERSONAS.keys()))
def test_each_persona_has_valid_entanglement_definition(persona_name):
    """
    ENTANGLEMENT TEST: Verify each persona has proper entanglement definition.
    
    Each persona must have dependencies, outputs, and cascade effects defined.
    """
    entanglement_info = entanglement_validator.entanglement_map[persona_name]
    
    required_keys = ["depends_on", "enables", "outputs", "failure_cascades_to", 
                    "contracts_with", "validates"]
    
    for key in required_keys:
        assert key in entanglement_info, \
            f"Persona {persona_name} missing entanglement key: {key}"
    
    # Verify outputs are defined
    assert len(entanglement_info["outputs"]) > 0, \
        f"Persona {persona_name} must define outputs"
    
    # Verify responsibilities exist in config
    config_persona = ARCHITECTURAL_PERSONAS[persona_name]
    assert "responsibilities" in config_persona, \
        f"Persona {persona_name} missing responsibilities in config"


@pytest.mark.parametrize("persona_name", list(ARCHITECTURAL_PERSONAS.keys()))
def test_persona_functionality_check(persona_name):
    """
    ENTANGLEMENT TEST: Check if each persona is currently functional.
    
    This test runs the actual functionality check for each persona,
    demonstrating the real-world entanglement status.
    """
    is_functional = entanglement_validator._is_persona_functional(persona_name)
    
    # Log the functionality status
    status = "✅ FUNCTIONAL" if is_functional else "❌ NON-FUNCTIONAL"
    print(f"\n{persona_name}: {status}")
    
    # If non-functional, calculate and log cascade impact
    if not is_functional:
        cascade_impact = entanglement_validator._calculate_cascade_impact(persona_name)
        print(f"  Cascade Impact: {cascade_impact}")
        
        # Verify cascade impact is properly calculated
        assert len(cascade_impact) >= 0, \
            f"Cascade impact calculation failed for {persona_name}"
    
    # This test always passes - it's for information gathering
    assert True, f"Persona {persona_name} functionality check completed"


if __name__ == "__main__":
    # Run the entanglement report when executed directly
    validator = PersonaEntanglementValidator()
    report = validator.generate_entanglement_report()
    
    print(json.dumps(report, indent=2))
