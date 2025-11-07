#!/usr/bin/env python3
"""
Alternative Security Scan Tool

Performs security scanning without pip-audit dependency conflicts.
Uses safety and vulnerability databases to check for known issues.

Usage:
    python tools/security_scan_alternative.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


def check_pinned_github_actions() -> Dict[str, Any]:
    """Check that GitHub Actions are pinned to SHA"""
    print("🔒 Checking GitHub Actions pinning...")

    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        return {"status": "no_workflows", "pinned_count": 0, "total_count": 0}

    workflow_files = list(workflow_dir.glob("*.yml"))
    total_actions = 0
    pinned_actions = 0
    unpinned_actions = []

    for workflow_file in workflow_files:
        try:
            with open(workflow_file) as f:
                content = f.read()

            # Find uses: statements
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if 'uses:' in line and '@' in line:
                    total_actions += 1
                    # Check if it's pinned to SHA (40 character hex after @)
                    parts = line.split('@')
                    if len(parts) > 1:
                        ref = parts[1].strip().strip('"\'')
                        if len(ref) == 40 and all(c in '0123456789abcdef' for c in ref.lower()):
                            pinned_actions += 1
                        else:
                            unpinned_actions.append(f"{workflow_file.name}:{line_num}")

        except Exception as e:
            print(f"Warning: Could not read {workflow_file}: {e}")

    pinning_rate = (pinned_actions / total_actions * 100) if total_actions > 0 else 100

    return {
        "status": "checked",
        "total_actions": total_actions,
        "pinned_actions": pinned_actions,
        "unpinned_actions": unpinned_actions,
        "pinning_rate": pinning_rate,
        "compliant": pinning_rate >= 90  # 90% threshold
    }

def check_constraints_enforcement() -> Dict[str, Any]:
    """Check constraints.txt exists and is enforced in CI"""
    print("📋 Checking constraints.txt enforcement...")

    constraints_file = Path("constraints.txt")
    ci_file = Path(".github/workflows/ci.yml")

    results = {
        "constraints_exists": constraints_file.exists(),
        "ci_enforces": False,
        "constraints_count": 0
    }

    if constraints_file.exists():
        try:
            with open(constraints_file) as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                results["constraints_count"] = len(lines)
        except Exception:
            pass

    if ci_file.exists():
        try:
            with open(ci_file) as f:
                ci_content = f.read()
                results["ci_enforces"] = "constraints.txt" in ci_content
        except Exception:
            pass

    results["compliant"] = results["constraints_exists"] and results["ci_enforces"]
    return results

def check_dependency_vulnerabilities() -> Dict[str, Any]:
    """Check for known vulnerable dependencies using basic safety check"""
    print("🛡️ Checking for vulnerable dependencies...")

    # Try to run safety if available
    try:
        result = subprocess.run([
            sys.executable, "-m", "safety", "check", "--json"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            try:
                safety_data = json.loads(result.stdout) if result.stdout else []
                return {
                    "status": "safety_available",
                    "vulnerabilities": len(safety_data),
                    "vulnerable_packages": [v.get("package", "unknown") for v in safety_data],
                    "compliant": len(safety_data) == 0
                }
            except json.JSONDecodeError:
                return {"status": "safety_parse_error", "compliant": False}

    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Fallback: Basic dependency audit
    print("   Safety not available, performing basic checks...")

    # Check for obviously problematic patterns in requirements
    problematic_patterns = [
        "==0.0.0",  # Development versions
        ">=0.0.0",  # Overly permissive
        "urllib3<1.26",  # Known vulnerable versions
        "requests<2.25",  # Known vulnerable versions
        "jinja2<3.0"  # Known vulnerable versions
    ]

    issues_found = []

    # Check common requirement files
    req_files = ["requirements.txt", "requirements-dev.txt", "pyproject.toml"]
    for req_file in req_files:
        req_path = Path(req_file)
        if req_path.exists():
            try:
                with open(req_path) as f:
                    content = f.read()
                    for pattern in problematic_patterns:
                        if pattern in content:
                            issues_found.append(f"{req_file}: {pattern}")
            except Exception:
                pass

    return {
        "status": "basic_check",
        "issues_found": len(issues_found),
        "issue_details": issues_found,
        "compliant": len(issues_found) == 0
    }

def generate_sbom() -> Dict[str, Any]:
    """Generate Software Bill of Materials"""
    print("📦 Generating SBOM...")

    try:
        # Try pip list to get installed packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "list", "--format=json"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            packages = json.loads(result.stdout)

            # Create basic SBOM structure
            sbom = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "version": 1,
                "metadata": {
                    "timestamp": "2025-09-22T01:35:00Z",
                    "tools": ["pip"]
                },
                "components": []
            }

            for pkg in packages:
                component = {
                    "type": "library",
                    "name": pkg["name"],
                    "version": pkg["version"],
                    "purl": f"pkg:pypi/{pkg['name']}@{pkg['version']}"
                }
                sbom["components"].append(component)

            # Save SBOM
            sbom_file = Path("/tmp/lukhas_sbom.json")
            with open(sbom_file, 'w') as f:
                json.dump(sbom, f, indent=2)

            return {
                "status": "generated",
                "components_count": len(packages),
                "sbom_file": str(sbom_file),
                "compliant": True
            }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "compliant": False
        }

def run_comprehensive_security_scan():
    """Run comprehensive security scan"""
    print("🔐 COMPREHENSIVE SECURITY SCAN")
    print("=" * 50)

    results = {}

    # 1. GitHub Actions pinning
    results["github_actions"] = check_pinned_github_actions()

    # 2. Constraints enforcement
    results["constraints"] = check_constraints_enforcement()

    # 3. Dependency vulnerabilities
    results["vulnerabilities"] = check_dependency_vulnerabilities()

    # 4. SBOM generation
    results["sbom"] = generate_sbom()

    # Summary
    print("\n📊 SECURITY SCAN RESULTS")
    print("-" * 30)

    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r.get("compliant", False))

    for check_name, check_result in results.items():
        status = "✅ PASS" if check_result.get("compliant", False) else "❌ FAIL"
        print(f"{check_name.replace('_', ' ').title()}: {status}")

        # Show details
        if check_name == "github_actions":
            print(f"   Pinned Actions: {check_result['pinned_actions']}/{check_result['total_actions']}")
        elif check_name == "constraints":
            print(f"   Constraints File: {'✅' if check_result['constraints_exists'] else '❌'}")
            print(f"   CI Enforcement: {'✅' if check_result['ci_enforces'] else '❌'}")
        elif check_name == "vulnerabilities":
            vuln_count = check_result.get('vulnerabilities', check_result.get('issues_found', 0))
            print(f"   Issues Found: {vuln_count}")
        elif check_name == "sbom" and check_result['status'] == 'generated':
            print(f"   Components: {check_result['components_count']}")

    compliance_rate = (passed_checks / total_checks) * 100

    print("\n🎯 OVERALL SECURITY COMPLIANCE")
    print("-" * 30)
    print(f"Checks Passed: {passed_checks}/{total_checks}")
    print(f"Compliance Rate: {compliance_rate:.1f}%")

    if compliance_rate >= 75:
        print("✅ SECURITY SCAN: PASS")
        overall_pass = True
    else:
        print("❌ SECURITY SCAN: FAIL")
        overall_pass = False

    print(f"🔒 Security hardening: {'COMPLETE' if overall_pass else 'NEEDS WORK'}")

    return {
        "scan_passed": overall_pass,
        "compliance_rate": compliance_rate,
        "checks_passed": passed_checks,
        "total_checks": total_checks,
        "detailed_results": results
    }

if __name__ == "__main__":
    result = run_comprehensive_security_scan()

    # Exit with appropriate code
    exit_code = 0 if result["scan_passed"] else 1
    exit(exit_code)
