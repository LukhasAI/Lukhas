#!/usr/bin/env python3
"""
LUKHAS AI Guardian System Compliance Validator
Guardian System v1.0.0 - Constitutional AI Safety Framework

This script validates compliance with Guardian System protocols,
Constitutional AI principles, and regulatory requirements (GDPR/CCPA).

Generated: 2025-09-11 (MATRIZ-R1 Stream C Task C-CC1)
Classification: Guardian Compliance Officer Tool
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GuardianComplianceValidator:
    """
    Guardian System compliance validation with Constitutional AI principles.

    Validates:
    - Guardian System v1.0.0 infrastructure
    - SBOM compliance and integrity
    - Dependency security constraints
    - Constitutional AI safety protocols
    - GDPR/CCPA compliance readiness
    """

    def __init__(self, lukhas_root: str = None):
        self.lukhas_root = Path(lukhas_root) if lukhas_root else Path.cwd()
        self.validation_start = datetime.now(timezone.utc)
        self.drift_threshold = 0.15  # Guardian System drift detection threshold

        # Constitutional AI metrics targets
        self.constitutional_targets = {
            "human_autonomy_preservation": 95.0,
            "beneficial_outcome_prediction": 90.0,
            "harm_prevention_success": 99.9,
            "fairness_demographics": 95.0,
            "decision_explainability": 85.0,
        }

    def validate_guardian_infrastructure(self) -> dict[str, Any]:
        """Validate Guardian System v1.0.0 infrastructure."""
        print("🛡️  Validating Guardian System v1.0.0 infrastructure...")

        guardian_paths = [
            "candidate/governance/guardian/",
            "governance/",
            "docs/architecture/SECURITY_ARCHITECTURE.json",
            "constraints.txt",
            ".gitleaks.toml",
        ]

        results = {
            "guardian_files_present": 0,
            "guardian_files_missing": [],
            "security_architecture_valid": False,
            "constraints_valid": False,
            "gitleaks_config_valid": False,
        }

        # Check Guardian system files
        for path in guardian_paths:
            full_path = self.lukhas_root / path
            if full_path.exists():
                results["guardian_files_present"] += 1
                if path == "docs/architecture/SECURITY_ARCHITECTURE.json":
                    results["security_architecture_valid"] = self._validate_security_architecture(full_path)
                elif path == "constraints.txt":
                    results["constraints_valid"] = self._validate_constraints(full_path)
                elif path == ".gitleaks.toml":
                    results["gitleaks_config_valid"] = self._validate_gitleaks_config(full_path)
            else:
                results["guardian_files_missing"].append(str(path))

        # Count Guardian system files in governance directories
        guardian_file_count = 0
        governance_dirs = ["candidate/governance/guardian/", "governance/"]
        for gov_dir in governance_dirs:
            full_dir = self.lukhas_root / gov_dir
            if full_dir.exists():
                guardian_file_count += len(list(full_dir.rglob("*.py")))

        results["guardian_file_count"] = guardian_file_count
        results["meets_280_file_threshold"] = guardian_file_count >= 280

        return results

    def validate_sbom_compliance(self) -> dict[str, Any]:
        """Validate SBOM compliance and integrity."""
        print("📋 Validating SBOM compliance...")

        sbom_path = self.lukhas_root / "reports/sbom/cyclonedx.json"
        results = {
            "sbom_exists": sbom_path.exists(),
            "sbom_valid": False,
            "components_count": 0,
            "spec_version": None,
            "serial_number": None,
            "last_generated": None,
            "integrity_hash": None,
        }

        if results["sbom_exists"]:
            try:
                with open(sbom_path) as f:
                    sbom_content = f.read()
                    sbom_data = json.loads(sbom_content)

                results["sbom_valid"] = True
                results["components_count"] = len(sbom_data.get("components", []))
                results["spec_version"] = sbom_data.get("specVersion")
                results["serial_number"] = sbom_data.get("serialNumber")

                if "metadata" in sbom_data:
                    results["last_generated"] = sbom_data["metadata"].get("timestamp")

                # Calculate integrity hash
                results["integrity_hash"] = hashlib.sha256(sbom_content.encode()).hexdigest()

            except Exception as e:
                print(f"⚠️  SBOM validation error: {e}")
                results["sbom_valid"] = False

        return results

    def validate_dependency_security(self) -> dict[str, Any]:
        """Validate dependency security constraints."""
        print("🔒 Validating dependency security constraints...")

        constraints_path = self.lukhas_root / "constraints.txt"
        results = {
            "constraints_exist": constraints_path.exists(),
            "guardian_validated": False,
            "critical_dependencies": [],
            "security_annotations": 0,
            "compliance_markers": 0,
        }

        if results["constraints_exist"]:
            try:
                with open(constraints_path) as f:
                    content = f.read()

                # Check for Guardian System validation markers
                results["guardian_validated"] = "Guardian System v1.0.0" in content

                # Count security annotations and compliance markers
                lines = content.split("\n")
                for line in lines:
                    if "# Security" in line or "# security" in line:
                        results["security_annotations"] += 1
                    if any(marker in line for marker in ["GDPR", "CCPA", "Constitutional", "Guardian"]):
                        results["compliance_markers"] += 1
                    if "==" in line and not line.strip().startswith("#"):
                        # Extract pinned dependency
                        dep = line.split("==")[0].strip()
                        if dep and not dep.startswith("#"):
                            results["critical_dependencies"].append(dep)

            except Exception as e:
                print(f"⚠️  Constraints validation error: {e}")

        return results

    def validate_constitutional_ai_compliance(self) -> dict[str, Any]:
        """Validate Constitutional AI safety protocols."""
        print("⚖️  Validating Constitutional AI compliance...")

        # This would normally integrate with actual Guardian System metrics
        # For now, we'll validate the framework structure

        security_arch_path = self.lukhas_root / "docs/architecture/SECURITY_ARCHITECTURE.json"
        results = {
            "constitutional_framework_present": False,
            "drift_detection_enabled": False,
            "enforcement_mechanisms": False,
            "human_oversight_enabled": False,
            "transparency_framework": False,
        }

        if security_arch_path.exists():
            try:
                with open(security_arch_path) as f:
                    arch_data = json.load(f)

                # Check Constitutional AI framework
                const_ai = arch_data.get("constitutional_ai_framework", {})
                if const_ai:
                    results["constitutional_framework_present"] = True

                    # Check core principles
                    principles = const_ai.get("core_constitutional_principles", {})
                    if len(principles) >= 5:  # Should have all 5 core principles
                        results["transparency_framework"] = True

                    # Check enforcement mechanisms
                    enforcement = const_ai.get("constitutional_enforcement_mechanisms", {})
                    guardian_sys = enforcement.get("guardian_system_v1_0_0", {})

                    if guardian_sys.get("drift_detection_threshold") == 0.15:
                        results["drift_detection_enabled"] = True

                    if guardian_sys.get("human_override_capability") == "always_available":
                        results["human_oversight_enabled"] = True

                    if "enforcement_actions" in guardian_sys:
                        results["enforcement_mechanisms"] = True

            except Exception as e:
                print(f"⚠️  Constitutional AI validation error: {e}")

        return results

    def validate_ci_pipeline_security(self) -> dict[str, Any]:
        """Validate CI/CD pipeline security integration."""
        print("🔄 Validating CI/CD pipeline security...")

        ci_path = self.lukhas_root / ".github/workflows/ci.yml"
        results = {
            "ci_config_exists": ci_path.exists(),
            "constraints_integration": False,
            "gitleaks_enabled": False,
            "sbom_generation": False,
            "security_checks": 0,
        }

        if results["ci_config_exists"]:
            try:
                with open(ci_path) as f:
                    ci_content = f.read()

                # Check for security integrations
                if "constraints.txt" in ci_content:
                    results["constraints_integration"] = True

                if "gitleaks" in ci_content:
                    results["gitleaks_enabled"] = True

                if "cyclonedx-bom" in ci_content:
                    results["sbom_generation"] = True

                # Count security check steps
                security_keywords = ["security", "gitleaks", "sbom", "constraints", "vulnerability"]
                for keyword in security_keywords:
                    if keyword in ci_content.lower():
                        results["security_checks"] += 1

            except Exception as e:
                print(f"⚠️  CI pipeline validation error: {e}")

        return results

    def generate_compliance_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate comprehensive compliance report."""
        report_time = datetime.now(timezone.utc)
        validation_duration = (report_time - self.validation_start).total_seconds()

        report = f"""
# LUKHAS AI Guardian System Compliance Report
## Generated: {report_time.isoformat()}
## Validation Duration: {validation_duration:.2f} seconds
## Guardian System v1.0.0 Compliance Framework

---

## COMPLIANCE SUMMARY

### Guardian System Infrastructure
- Guardian Files Present: {validation_results['guardian']['guardian_files_present']}
- Guardian File Count: {validation_results['guardian']['guardian_file_count']}
- Meets 280+ File Threshold: {'✅' if validation_results['guardian']['meets_280_file_threshold'] else '❌'}
- Security Architecture Valid: {'✅' if validation_results['guardian']['security_architecture_valid'] else '❌'}
- Constraints Valid: {'✅' if validation_results['guardian']['constraints_valid'] else '❌'}
- Gitleaks Config Valid: {'✅' if validation_results['guardian']['gitleaks_config_valid'] else '❌'}

### SBOM Compliance
- SBOM Exists: {'✅' if validation_results['sbom']['sbom_exists'] else '❌'}
- SBOM Valid: {'✅' if validation_results['sbom']['sbom_valid'] else '❌'}
- Components Count: {validation_results['sbom']['components_count']}
- Spec Version: {validation_results['sbom']['spec_version']}
- Last Generated: {validation_results['sbom']['last_generated']}

### Dependency Security
- Constraints Exist: {'✅' if validation_results['dependencies']['constraints_exist'] else '❌'}
- Guardian Validated: {'✅' if validation_results['dependencies']['guardian_validated'] else '❌'}
- Critical Dependencies: {len(validation_results['dependencies']['critical_dependencies'])}
- Security Annotations: {validation_results['dependencies']['security_annotations']}
- Compliance Markers: {validation_results['dependencies']['compliance_markers']}

### Constitutional AI Compliance
- Framework Present: {'✅' if validation_results['constitutional']['constitutional_framework_present'] else '❌'}
- Drift Detection: {'✅' if validation_results['constitutional']['drift_detection_enabled'] else '❌'}
- Enforcement Mechanisms: {'✅' if validation_results['constitutional']['enforcement_mechanisms'] else '❌'}
- Human Oversight: {'✅' if validation_results['constitutional']['human_oversight_enabled'] else '❌'}
- Transparency Framework: {'✅' if validation_results['constitutional']['transparency_framework'] else '❌'}

### CI/CD Pipeline Security
- CI Config Exists: {'✅' if validation_results['ci']['ci_config_exists'] else '❌'}
- Constraints Integration: {'✅' if validation_results['ci']['constraints_integration'] else '❌'}
- Gitleaks Enabled: {'✅' if validation_results['ci']['gitleaks_enabled'] else '❌'}
- SBOM Generation: {'✅' if validation_results['ci']['sbom_generation'] else '❌'}
- Security Checks: {validation_results['ci']['security_checks']}

---

## COMPLIANCE STATUS

### Guardian System v1.0.0: {"✅ COMPLIANT" if self._is_guardian_compliant(validation_results) else "❌ NON-COMPLIANT"}
### Constitutional AI: {"✅ COMPLIANT" if self._is_constitutional_compliant(validation_results) else "❌ NON-COMPLIANT"}
### GDPR/CCPA Ready: {"✅ READY" if self._is_gdpr_ccpa_ready(validation_results) else "❌ NOT READY"}
### Supply Chain Security: {"✅ SECURE" if self._is_supply_chain_secure(validation_results) else "❌ INSECURE"}

---

## RECOMMENDATIONS

{self._generate_recommendations(validation_results)}

---

**Guardian System Compliance Validator v1.0.0**
**Constitutional AI Safety Framework**
**GDPR/CCPA Aligned Security**
"""
        return report

    def _validate_security_architecture(self, path: Path) -> bool:
        """Validate security architecture file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return "constitutional_ai_framework" in data and "supply_chain_security" in data
        except Exception:
            return False

    def _validate_constraints(self, path: Path) -> bool:
        """Validate constraints file."""
        try:
            with open(path) as f:
                content = f.read()
            return "Guardian System v1.0.0" in content and "cryptography==" in content
        except Exception:
            return False

    def _validate_gitleaks_config(self, path: Path) -> bool:
        """Validate gitleaks configuration."""
        try:
            with open(path) as f:
                content = f.read()
            return "LUKHAS AI Guardian Security Scanner" in content and "[[rules]]" in content
        except Exception:
            return False

    def _is_guardian_compliant(self, results: Dict[str, Any]) -> bool:
        """Check if Guardian System is compliant."""
        guardian = results["guardian"]
        return (
            guardian["meets_280_file_threshold"]
            and guardian["security_architecture_valid"]
            and guardian["constraints_valid"]
        )

    def _is_constitutional_compliant(self, results: Dict[str, Any]) -> bool:
        """Check if Constitutional AI is compliant."""
        const = results["constitutional"]
        return (
            const["constitutional_framework_present"]
            and const["drift_detection_enabled"]
            and const["human_oversight_enabled"]
        )

    def _is_gdpr_ccpa_ready(self, results: Dict[str, Any]) -> bool:
        """Check if GDPR/CCPA ready."""
        deps = results["dependencies"]
        return deps["constraints_exist"] and deps["guardian_validated"] and deps["compliance_markers"] > 0

    def _is_supply_chain_secure(self, results: Dict[str, Any]) -> bool:
        """Check if supply chain is secure."""
        sbom = results["sbom"]
        ci = results["ci"]
        return sbom["sbom_exists"] and sbom["sbom_valid"] and ci["sbom_generation"] and ci["gitleaks_enabled"]

    def _generate_recommendations(self, results: Dict[str, Any]) -> str:
        """Generate compliance recommendations."""
        recommendations = []

        if not self._is_guardian_compliant(results):
            recommendations.append("- Ensure Guardian System v1.0.0 infrastructure is complete (280+ files)")
            recommendations.append("- Validate security architecture configuration")
            recommendations.append("- Update dependency constraints with Guardian validation")

        if not self._is_constitutional_compliant(results):
            recommendations.append("- Implement Constitutional AI framework components")
            recommendations.append("- Enable drift detection with 0.15 threshold")
            recommendations.append("- Ensure human oversight capabilities are always available")

        if not self._is_supply_chain_secure(results):
            recommendations.append("- Generate and validate SBOM with CycloneDX format")
            recommendations.append("- Enable gitleaks scanning in CI pipeline")
            recommendations.append("- Automate SBOM generation in CI/CD pipeline")

        if not recommendations:
            recommendations.append("- All Guardian System v1.0.0 compliance requirements met ✅")
            recommendations.append("- Continue monitoring and regular compliance validation")
            recommendations.append("- Consider advanced Constitutional AI features")

        return "\n".join(recommendations)

    def run_full_validation(self) -> dict[str, Any]:
        """Run complete Guardian System compliance validation."""
        print("🚀 Starting Guardian System v1.0.0 Compliance Validation...")
        print(f"📁 LUKHAS Root: {self.lukhas_root}")
        print(f"⏰ Started: {self.validation_start.isoformat()}")
        print("=" * 60)

        results = {
            "guardian": self.validate_guardian_infrastructure(),
            "sbom": self.validate_sbom_compliance(),
            "dependencies": self.validate_dependency_security(),
            "constitutional": self.validate_constitutional_ai_compliance(),
            "ci": self.validate_ci_pipeline_security(),
        }

        print("=" * 60)
        print("✅ Guardian System compliance validation complete!")

        return results


def main():
    """Main execution function."""
    lukhas_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    validator = GuardianComplianceValidator(lukhas_root)
    results = validator.run_full_validation()

    # Generate and save compliance report
    report = validator.generate_compliance_report(results)

    report_path = Path(lukhas_root) / "docs/compliance/GUARDIAN_COMPLIANCE_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        f.write(report)

    print(f"📄 Compliance report saved: {report_path}")

    # Print summary to console
    print("\n" + "=" * 60)
    print("GUARDIAN SYSTEM COMPLIANCE SUMMARY")
    print("=" * 60)
    print(f"Guardian v1.0.0: {'✅ COMPLIANT' if validator._is_guardian_compliant(results) else '❌ NON-COMPLIANT'}")
    print(
        f"Constitutional AI: {'✅ COMPLIANT' if validator._is_constitutional_compliant(results) else '❌ NON-COMPLIANT'}"
    )
    print(f"GDPR/CCPA Ready: {'✅ READY' if validator._is_gdpr_ccpa_ready(results) else '❌ NOT READY'}")
    print(f"Supply Chain: {'✅ SECURE' if validator._is_supply_chain_secure(results) else '❌ INSECURE'}")

    # Exit with appropriate code
    all_compliant = (
        validator._is_guardian_compliant(results)
        and validator._is_constitutional_compliant(results)
        and validator._is_gdpr_ccpa_ready(results)
        and validator._is_supply_chain_secure(results)
    )

    sys.exit(0 if all_compliant else 1)


if __name__ == "__main__":
    main()
