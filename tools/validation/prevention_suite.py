#!/usr/bin/env python3
"""
Prevention Validation Suite
===========================
Comprehensive validation suite that integrates all prevention tools and validates
the health of the automated fix pipeline infrastructure.

Components validated:
- F-string syntax prevention
- Test class collection validation
- Import bridge health
- Pytest configuration compliance
- Pipeline component availability

Features:
- End-to-end pipeline testing
- Health score calculation
- Detailed reporting
- Integration readiness assessment
"""

import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

# Import validation components
sys.path.insert(0, str(ROOT / "tools" / "automation"))
sys.path.insert(0, str(ROOT / "tools" / "monitoring"))

try:
    from precommit_fstring_validator import PrecommitFStringValidator
except ImportError:
    PrecommitFStringValidator = None

try:
    from pytest_class_fixer import PytestClassFixer
except ImportError:
    PytestClassFixer = None

try:
    from diagnostic_orchestrator import DiagnosticOrchestrator
except ImportError:
    DiagnosticOrchestrator = None

try:
    from diagnostic_monitor import DiagnosticMonitor
except ImportError:
    DiagnosticMonitor = None


class ValidationResult:
    """Result of a validation test"""
    def __init__(self, name: str, passed: bool, message: str, details: Dict = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()


class PreventionValidationSuite:
    """Main prevention validation suite"""
    
    def __init__(self):
        self.results = []
        self.component_health = {}
    
    def validate_component_imports(self) -> List[ValidationResult]:
        """Validate that all prevention components can be imported"""
        results = []
        
        components = {
            "F-String Validator": PrecommitFStringValidator,
            "Pytest Class Fixer": PytestClassFixer, 
            "Diagnostic Orchestrator": DiagnosticOrchestrator,
            "Diagnostic Monitor": DiagnosticMonitor
        }
        
        for name, component in components.items():
            if component is not None:
                results.append(ValidationResult(
                    f"Import {name}",
                    True,
                    f"{name} successfully imported"
                ))
            else:
                results.append(ValidationResult(
                    f"Import {name}",
                    False,
                    f"{name} could not be imported"
                ))
        
        return results
    
    def validate_file_structure(self) -> List[ValidationResult]:
        """Validate that required files and directories exist"""
        results = []
        
        required_files = [
            ("T4 Autofix Policy", ".t4autofix.toml"),
            ("Pytest Config", "pytest.ini"),
            ("Enhanced Autofix", "tools/ci/enhanced_auto_fix_safe.py"),
            ("Nightly Autofix", "tools/ci/nightly_autofix.sh"),
            ("F-String Validator", "tools/automation/precommit_fstring_validator.py"),
            ("Test Class Fixer", "tools/automation/pytest_class_fixer.py"),
            ("Diagnostic Orchestrator", "tools/automation/diagnostic_orchestrator.py"),
            ("Diagnostic Monitor", "tools/monitoring/diagnostic_monitor.py")
        ]
        
        for name, path in required_files:
            file_path = ROOT / path
            if file_path.exists():
                results.append(ValidationResult(
                    f"File Structure: {name}",
                    True,
                    f"{path} exists"
                ))
            else:
                results.append(ValidationResult(
                    f"File Structure: {name}",
                    False,
                    f"{path} missing"
                ))
        
        # Check directory structure
        required_dirs = [
            ("Reports Directory", "reports"),
            ("Autofix Reports", "reports/autofix"),
            ("Monitoring Reports", "reports/monitoring"),
            ("Deep Search Reports", "reports/deep_search")
        ]
        
        for name, dir_path in required_dirs:
            directory = ROOT / dir_path
            if directory.exists() and directory.is_dir():
                results.append(ValidationResult(
                    f"Directory: {name}",
                    True,
                    f"{dir_path}/ exists"
                ))
            else:
                results.append(ValidationResult(
                    f"Directory: {name}",
                    False,
                    f"{dir_path}/ missing"
                ))
        
        return results
    
    def validate_fstring_prevention(self) -> List[ValidationResult]:
        """Validate f-string syntax prevention system"""
        results = []
        
        if PrecommitFStringValidator is None:
            results.append(ValidationResult(
                "F-String Prevention",
                False,
                "F-string validator not available"
            ))
            return results
        
        # Test validator functionality
        try:
            validator = PrecommitFStringValidator(auto_fix=False)
            
            # Create a test file with known f-string issues
            test_content = '''
def test_fstring():
    value = 42
    print(f"Value: {value}:.2f}")  # Extra brace error
    print(f"ID: {uuid.uuid4().hex[:8}]")  # Bracket mismatch
'''
            
            test_file = ROOT / "tmp_test_fstring.py"
            test_file.write_text(test_content)
            
            try:
                # Test validation
                errors = validator.validate_file(test_file)
                
                if len(errors) > 0:
                    results.append(ValidationResult(
                        "F-String Validation Detection",
                        True,
                        f"Detected {len(errors)} f-string errors as expected",
                        {"detected_errors": len(errors)}
                    ))
                else:
                    results.append(ValidationResult(
                        "F-String Validation Detection", 
                        False,
                        "Failed to detect known f-string errors"
                    ))
                
                # Test with valid content
                valid_content = '''
def test_valid():
    value = 42
    print(f"Value: {value:.2f}")
    print(f"Valid f-string")
'''
                test_file.write_text(valid_content)
                valid_errors = validator.validate_file(test_file)
                
                if len(valid_errors) == 0:
                    results.append(ValidationResult(
                        "F-String Valid Detection",
                        True,
                        "Correctly identified valid f-strings"
                    ))
                else:
                    results.append(ValidationResult(
                        "F-String Valid Detection",
                        False,
                        f"False positives on valid f-strings: {len(valid_errors)}"
                    ))
                
            finally:
                # Cleanup test file
                if test_file.exists():
                    test_file.unlink()
            
        except Exception as e:
            results.append(ValidationResult(
                "F-String Prevention Test",
                False,
                f"F-string prevention test failed: {e}"
            ))
        
        return results
    
    def validate_pytest_collection_prevention(self) -> List[ValidationResult]:
        """Validate pytest class collection prevention"""
        results = []
        
        if PytestClassFixer is None:
            results.append(ValidationResult(
                "Pytest Collection Prevention",
                False,
                "Pytest class fixer not available"
            ))
            return results
        
        try:
            fixer = PytestClassFixer(dry_run=True)
            
            # Test detection capability
            test_content = '''
class TestExample:
    def __init__(self):
        self.data = "test"
    
    def test_something(self):
        assert self.data == "test"
'''
            
            test_file = ROOT / "tmp_test_class.py"
            test_file.write_text(test_content)
            
            try:
                has_init = fixer.file_has_test_class_with_init(test_file)
                
                if has_init:
                    results.append(ValidationResult(
                        "Pytest Collection Detection",
                        True,
                        "Detected test class with __init__ as expected"
                    ))
                else:
                    results.append(ValidationResult(
                        "Pytest Collection Detection",
                        False,
                        "Failed to detect test class __init__ issue"
                    ))
                    
            finally:
                if test_file.exists():
                    test_file.unlink()
                    
        except Exception as e:
            results.append(ValidationResult(
                "Pytest Collection Prevention Test",
                False,
                f"Pytest prevention test failed: {e}"
            ))
        
        return results
    
    def validate_import_bridge_health(self) -> List[ValidationResult]:
        """Validate import bridge functionality"""
        results = []
        
        try:
            # Test auth_integration import
            from lukhas.governance.identity import auth_integration
            results.append(ValidationResult(
                "Import Bridge: auth_integration",
                True,
                "auth_integration import bridge working"
            ))
        except ImportError as e:
            results.append(ValidationResult(
                "Import Bridge: auth_integration", 
                False,
                f"auth_integration import failed: {e}"
            ))
        
        return results
    
    def validate_pytest_configuration(self) -> List[ValidationResult]:
        """Validate pytest configuration"""
        results = []
        
        pytest_ini = ROOT / "pytest.ini"
        if not pytest_ini.exists():
            results.append(ValidationResult(
                "Pytest Config Exists",
                False,
                "pytest.ini not found"
            ))
            return results
        
        try:
            content = pytest_ini.read_text()
            
            # Check for audit_safe marker
            if "audit_safe:" in content:
                results.append(ValidationResult(
                    "Pytest Marker: audit_safe",
                    True,
                    "audit_safe marker configured"
                ))
            else:
                results.append(ValidationResult(
                    "Pytest Marker: audit_safe",
                    False,
                    "audit_safe marker missing"
                ))
            
            # Check for other critical markers
            required_markers = ["contract:", "nias_transcendence:", "benchmark:"]
            for marker in required_markers:
                if marker in content:
                    results.append(ValidationResult(
                        f"Pytest Marker: {marker[:-1]}",
                        True,
                        f"{marker[:-1]} marker configured"
                    ))
                else:
                    results.append(ValidationResult(
                        f"Pytest Marker: {marker[:-1]}",
                        False,
                        f"{marker[:-1]} marker missing"
                    ))
            
        except Exception as e:
            results.append(ValidationResult(
                "Pytest Config Validation",
                False,
                f"Failed to validate pytest.ini: {e}"
            ))
        
        return results
    
    def validate_pipeline_integration(self) -> List[ValidationResult]:
        """Validate pipeline integration points"""
        results = []
        
        # Check nightly autofix script
        nightly_script = ROOT / "tools/ci/nightly_autofix.sh"
        if nightly_script.exists():
            content = nightly_script.read_text()
            
            # Check for orchestrator integration
            if "diagnostic_orchestrator.py" in content:
                results.append(ValidationResult(
                    "Pipeline: Orchestrator Integration",
                    True,
                    "Diagnostic orchestrator integrated in pipeline"
                ))
            else:
                results.append(ValidationResult(
                    "Pipeline: Orchestrator Integration",
                    False,
                    "Diagnostic orchestrator not integrated"
                ))
            
            # Check for monitoring integration  
            if "diagnostic_monitor.py" in content:
                results.append(ValidationResult(
                    "Pipeline: Monitoring Integration",
                    True,
                    "Diagnostic monitoring integrated in pipeline"
                ))
            else:
                results.append(ValidationResult(
                    "Pipeline: Monitoring Integration",
                    False,
                    "Diagnostic monitoring not integrated"
                ))
                
        else:
            results.append(ValidationResult(
                "Pipeline: Nightly Script",
                False,
                "Nightly autofix script missing"
            ))
        
        return results
    
    def calculate_health_score(self) -> float:
        """Calculate overall prevention system health score"""
        if not self.results:
            return 0.0
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        return (passed / total) * 100.0
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        health_score = self.calculate_health_score()
        
        # Categorize results
        categories = {}
        for result in self.results:
            category = result.name.split(":")[0] if ":" in result.name else "General"
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "results": []}
            
            if result.passed:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            
            categories[category]["results"].append({
                "name": result.name,
                "passed": result.passed,
                "message": result.message,
                "details": result.details
            })
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health_score": health_score,
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.passed),
            "failed_tests": sum(1 for r in self.results if not r.passed),
            "categories": categories,
            "status": "healthy" if health_score >= 90 else "degraded" if health_score >= 70 else "unhealthy"
        }
    
    def run_full_validation(self) -> Dict:
        """Run complete prevention validation suite"""
        logger.info("🛡️ Starting prevention validation suite")
        
        # Run all validation tests
        self.results.extend(self.validate_component_imports())
        self.results.extend(self.validate_file_structure()) 
        self.results.extend(self.validate_fstring_prevention())
        self.results.extend(self.validate_pytest_collection_prevention())
        self.results.extend(self.validate_import_bridge_health())
        self.results.extend(self.validate_pytest_configuration())
        self.results.extend(self.validate_pipeline_integration())
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        self.save_report(report)
        
        logger.info(f"🛡️ Validation complete: {report['health_score']:.1f}% health score")
        return report
    
    def save_report(self, report: Dict):
        """Save validation report"""
        reports_dir = ROOT / "reports" / "validation"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save latest report
        latest_report = reports_dir / "prevention_validation.json"
        latest_report.write_text(json.dumps(report, indent=2))
        
        # Save timestamped report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_report = reports_dir / f"prevention_validation_{timestamp}.json"
        timestamped_report.write_text(json.dumps(report, indent=2))


def main():
    """CLI interface for prevention validation suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prevention validation suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--category", help="Run specific validation category")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    suite = PreventionValidationSuite()
    report = suite.run_full_validation()
    
    # Print detailed results
    print(f"\n🛡️ PREVENTION VALIDATION RESULTS")
    print(f"================================")
    print(f"Overall Health Score: {report['health_score']:.1f}%")
    print(f"Status: {report['status'].upper()}")
    print(f"Tests: {report['passed_tests']}/{report['total_tests']} passed")
    
    # Print category breakdown
    for category, data in report['categories'].items():
        total_cat = data['passed'] + data['failed']
        pass_rate = (data['passed'] / total_cat * 100) if total_cat > 0 else 0
        status_icon = "✅" if data['failed'] == 0 else "⚠️" if pass_rate >= 70 else "❌"
        print(f"\n{status_icon} {category}: {data['passed']}/{total_cat} passed ({pass_rate:.1f}%)")
        
        # Show failures
        for result in data['results']:
            if not result['passed']:
                print(f"  ❌ {result['name']}: {result['message']}")
    
    return 0 if report['health_score'] >= 90 else 1


if __name__ == "__main__":
    sys.exit(main())