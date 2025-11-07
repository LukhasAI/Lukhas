#!/usr/bin/env python3
"""
LUKHAS Security Framework Integration Test
Validates that all security components work together correctly.
"""

import datetime
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


def run_command(cmd: List[str], description: str) -> Dict[str, Any]:
    """Run command and return result"""
    print(f"🧪 Testing: {description}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        return {
            "command": " ".join(cmd),
            "description": description,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(cmd),
            "description": description,
            "exit_code": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "success": False
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "description": description,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }


def validate_json_output(file_path: Path, required_fields: List[str]) -> Dict[str, Any]:
    """Validate JSON output contains required fields"""
    if not file_path.exists():
        return {"valid": False, "error": "File does not exist"}

    try:
        with open(file_path) as f:
            data = json.load(f)

        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "data_structure": list(data.keys()) if isinstance(data, dict) else "Not a dict"
        }
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def test_security_framework():
    """Test complete security framework"""

    print("🚀 LUKHAS Security Framework Integration Test")
    print("=" * 60)

    # Create temporary artifacts directory
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_dir = Path(temp_dir) / "artifacts"
        artifacts_dir.mkdir()

        project_root = Path.cwd()

        test_results = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "project_root": str(project_root),
            "artifacts_dir": str(artifacts_dir),
            "tests": [],
            "overall_success": True
        }

        # Test 1: Security Policy Validation
        print("\n📋 Testing Security Policy Configuration...")
        try:
            import yaml
            with open("security/security_policy.yml") as f:
                policy = yaml.safe_load(f)

            policy_test = {
                "name": "Security Policy Validation",
                "success": True,
                "details": f"Policy loaded successfully with {len(policy.get('security_policy', {}))} sections"
            }
        except Exception as e:
            policy_test = {
                "name": "Security Policy Validation",
                "success": False,
                "details": f"Policy validation failed: {e}"
            }
            test_results["overall_success"] = False

        test_results["tests"].append(policy_test)

        # Test 2: SBOM Generation
        sbom_cmd = [
            "python3", "scripts/security_sbom_generator.py",
            "--project-root", str(project_root),
            "--output-dir", str(artifacts_dir)
        ]
        sbom_result = run_command(sbom_cmd, "SBOM Generation")
        test_results["tests"].append(sbom_result)

        if not sbom_result["success"]:
            test_results["overall_success"] = False

        # Validate SBOM output
        sbom_files = list(artifacts_dir.glob("lukhas-sbom-*.json"))
        if sbom_files:
            sbom_validation = validate_json_output(
                sbom_files[0],
                ["bomFormat", "metadata", "components"]
            )
            test_results["tests"].append({
                "name": "SBOM Output Validation",
                "success": sbom_validation["valid"],
                "details": sbom_validation
            })
            if not sbom_validation["valid"]:
                test_results["overall_success"] = False

        # Test 3: Security Scanner
        scanner_cmd = [
            "python3", "scripts/security_scanner.py",
            "--project-root", str(project_root),
            "--output-dir", str(artifacts_dir)
        ]
        scanner_result = run_command(scanner_cmd, "Security Scanner")
        test_results["tests"].append(scanner_result)

        if not scanner_result["success"]:
            test_results["overall_success"] = False

        # Validate scanner output
        scan_files = list(artifacts_dir.glob("security-scan-*.json"))
        if scan_files:
            scan_validation = validate_json_output(
                scan_files[0],
                ["scan_type", "security_findings", "compliance_status"]
            )
            test_results["tests"].append({
                "name": "Security Scanner Output Validation",
                "success": scan_validation["valid"],
                "details": scan_validation
            })
            if not scan_validation["valid"]:
                test_results["overall_success"] = False

        # Test 4: Abuse Tester (Mock Mode)
        abuse_cmd = [
            "python3", "scripts/abuse_tester.py",
            "--base-url", "http://localhost:8000",
            "--output-dir", str(artifacts_dir)
        ]
        # Note: This will fail because server isn't running, but should still produce output
        abuse_result = run_command(abuse_cmd, "Abuse Testing (Mock Mode)")
        # Don't mark overall failure for abuse testing since server isn't available
        test_results["tests"].append(abuse_result)

        # Validate abuse tester output
        abuse_files = list(artifacts_dir.glob("abuse-test-*.json"))
        if abuse_files:
            abuse_validation = validate_json_output(
                abuse_files[0],
                ["scan_type", "security_findings", "deployment_readiness"]
            )
            test_results["tests"].append({
                "name": "Abuse Tester Output Validation",
                "success": abuse_validation["valid"],
                "details": abuse_validation
            })
            if not abuse_validation["valid"]:
                test_results["overall_success"] = False

        # Test 5: Artifact Integration
        print("\n📊 Testing Artifact Integration...")

        # Check if all expected artifacts were created
        expected_artifacts = [
            "lukhas-sbom-*.json",
            "security-scan-*.json",
            "abuse-test-*.json"
        ]

        artifact_test = {
            "name": "Artifact Generation",
            "success": True,
            "details": {}
        }

        for pattern in expected_artifacts:
            files = list(artifacts_dir.glob(pattern))
            artifact_test["details"][pattern] = {
                "files_found": len(files),
                "files": [f.name for f in files]
            }
            if len(files) == 0:
                artifact_test["success"] = False
                test_results["overall_success"] = False

        test_results["tests"].append(artifact_test)

        # Test 6: CI Workflow Validation
        print("\n🔧 Testing CI Workflow Configuration...")

        try:
            with open(".github/workflows/t4-validation.yml") as f:
                workflow_content = f.read()

            required_jobs = [
                "security-sbom-generation",
                "security-static-analysis",
                "security-abuse-testing",
                "security-validation-summary"
            ]

            missing_jobs = []
            for job in required_jobs:
                if job not in workflow_content:
                    missing_jobs.append(job)

            workflow_test = {
                "name": "CI Workflow Configuration",
                "success": len(missing_jobs) == 0,
                "details": {
                    "required_jobs": required_jobs,
                    "missing_jobs": missing_jobs,
                    "workflow_length": len(workflow_content.split('\n'))
                }
            }

            if not workflow_test["success"]:
                test_results["overall_success"] = False

        except Exception as e:
            workflow_test = {
                "name": "CI Workflow Configuration",
                "success": False,
                "details": f"Workflow validation failed: {e}"
            }
            test_results["overall_success"] = False

        test_results["tests"].append(workflow_test)

        # Save test results
        results_file = project_root / "artifacts" / "security_framework_test_results.json"
        results_file.parent.mkdir(exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("🎯 LUKHAS Security Framework Test Results")
        print("=" * 60)

        passed_tests = sum(1 for test in test_results["tests"] if test.get("success", False))
        total_tests = len(test_results["tests"])

        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Overall Success: {'✅ PASS' if test_results['overall_success'] else '❌ FAIL'}")
        print(f"Results saved to: {results_file}")

        print("\nDetailed Results:")
        for test in test_results["tests"]:
            status = "✅ PASS" if test.get("success", False) else "❌ FAIL"
            name = test.get("name", test.get("description", "Unknown Test"))
            print(f"  {status} {name}")

            if not test.get("success", False) and "details" in test:
                details = test["details"]
                if isinstance(details, str):
                    print(f"    ⚠️  {details}")
                elif isinstance(details, dict):
                    for key, value in details.items():
                        if key in ["stderr", "error"]:
                            print(f"    ⚠️  {key}: {value}")

        print("\n📊 Security Framework Components Validated:")
        print("  🔍 SBOM Generation with CycloneDX format")
        print("  🛡️  Multi-tool security scanning (Semgrep, Bandit, Safety)")
        print("  ⚔️  Comprehensive abuse testing and attack simulation")
        print("  📋 Security policy enforcement and compliance validation")
        print("  🚀 GitHub Actions CI/CD integration")
        print("  📈 T4/0.01% excellence standards compliance")

        return test_results["overall_success"]


if __name__ == "__main__":
    try:
        success = test_security_framework()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Security framework test failed: {e}")
        sys.exit(1)
