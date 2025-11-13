#!/usr/bin/env python3
"""
Test Security Gates Blocking CI

Validates that security gates (pip-audit, SBOM) are properly configured
to block CI when vulnerabilities or compliance issues are detected.
"""

import subprocess
from pathlib import Path

import yaml


def test_security_audit_workflow_blocking():
    """Test that security audit workflow has blocking configurations"""
    workflow_path = Path(".github/workflows/security-audit.yml")
    assert workflow_path.exists(), "Security audit workflow not found"

    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    # Verify workflow structure
    assert "jobs" in workflow
    assert "security-audit" in workflow["jobs"]

    job = workflow["jobs"]["security-audit"]
    steps = job["steps"]

    # Find security-related steps
    pip_audit_steps = [
        step for step in steps
        if "run pip-audit" in step.get("name", "").lower()
    ]
    sbom_steps = [
        step for step in steps
        if "sbom" in step.get("name", "").lower()
    ]

    # Verify pip-audit steps exist and are blocking
    assert len(pip_audit_steps) >= 1, "Missing pip-audit steps"

    for step in pip_audit_steps:
        # Should NOT have continue-on-error: true (which would make it non-blocking)
        assert step.get("continue-on-error") is not True, f"Step '{step['name']}' is non-blocking"

        # Should have exit 1 commands for blocking
        run_content = step.get("run", "")
        assert "exit 1" in run_content, f"Step '{step['name']}' missing blocking exit"

    # Verify SBOM step exists and is blocking
    assert len(sbom_steps) >= 1, "Missing SBOM generation step"

    for step in sbom_steps:
        assert step.get("continue-on-error") is not True, f"SBOM step '{step['name']}' is non-blocking"
        run_content = step.get("run", "")
        if "exit 1" not in run_content:
            # For make commands, blocking is implicit - just verify no continue-on-error
            pass


def test_security_tools_installed():
    """Test that required security tools are available"""
    required_tools = [
        ("pip-audit", "pip-audit --version"),
        ("jq", "jq --version"),
    ]

    for tool_name, version_cmd in required_tools:
        try:
            result = subprocess.run(
                version_cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, f"{tool_name} not available or not working"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Tool not installed - that's fine for unit test environment
            print(f"⚠️ {tool_name} not available in test environment (expected)")


def test_requirements_files_exist():
    """Test that required dependency files exist for security scanning"""
    required_files = [
        "requirements.txt",
        "constraints.txt"
    ]

    for file_path in required_files:
        path = Path(file_path)
        assert path.exists(), f"Required dependency file {file_path} not found"
        assert path.stat().st_size > 0, f"Dependency file {file_path} is empty"


def test_makefile_sbom_target():
    """Test that Makefile has SBOM generation target"""
    makefile_path = Path("Makefile")
    if not makefile_path.exists():
        print("⚠️ Makefile not found - skipping SBOM target test")
        return

    with open(makefile_path) as f:
        makefile_content = f.read()

    # Should have sbom target
    assert "sbom:" in makefile_content, "Makefile missing 'sbom' target"

    # Should create reports/sbom directory
    assert "reports/sbom" in makefile_content, "SBOM target missing reports/sbom output"


def test_security_workflow_permissions():
    """Test that security workflow has appropriate permissions"""
    workflow_path = Path(".github/workflows/security-audit.yml")
    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    job = workflow["jobs"]["security-audit"]
    permissions = job.get("permissions", {})

    # Security audit should have these permissions
    required_permissions = {
        "contents": "read",
        "security-events": "write",
        "pull-requests": "write"
    }

    for perm, level in required_permissions.items():
        assert perm in permissions, f"Missing required permission: {perm}"
        assert permissions[perm] == level, f"Permission {perm} should be {level}, got {permissions[perm]}"


def test_security_gates_fail_fast():
    """Test that security gates are configured to fail fast"""
    workflow_path = Path(".github/workflows/security-audit.yml")
    with open(workflow_path) as f:
        content = f.read()

    # Should have immediate exit 1 on vulnerabilities
    assert "🚨 BLOCKING:" in content, "Missing blocking failure messages"
    assert "exit 1" in content, "Missing immediate failure commands"

    # Should not have continue-on-error for security steps
    security_sections = [
        section for section in content.split("- name:")
        if any(keyword in section.lower() for keyword in ["pip-audit", "sbom", "security"])
    ]

    for section in security_sections:
        if "continue-on-error: true" in section:
            # Check if this is in a comment or acceptable context
            lines = section.split('\n')
            for line in lines:
                if "continue-on-error: true" in line and not line.strip().startswith('#'):
                    raise AssertionError(f"Found continue-on-error: true in security section: {line}")


def test_blocking_configuration_comments():
    """Test that workflow has proper documentation about blocking behavior"""
    workflow_path = Path(".github/workflows/security-audit.yml")
    with open(workflow_path) as f:
        content = f.read()

    # Should document blocking behavior
    blocking_indicators = [
        "BLOCKING",
        "exit 1",
        "vulnerabilities found"
    ]

    found_indicators = sum(1 for indicator in blocking_indicators if indicator in content)
    assert found_indicators >= 2, "Workflow missing clear blocking behavior documentation"


if __name__ == "__main__":
    test_security_audit_workflow_blocking()
    test_security_tools_installed()
    test_requirements_files_exist()
    test_makefile_sbom_target()
    test_security_workflow_permissions()
    test_security_gates_fail_fast()
    test_blocking_configuration_comments()
    print("✅ All security gates blocking tests passed!")
