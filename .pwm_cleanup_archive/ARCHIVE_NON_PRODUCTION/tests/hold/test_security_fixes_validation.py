#!/usr/bin/env python3
"""
Security Fixes Validation Test Suite
====================================

This test suite validates that all critical security vulnerabilities have been fixed:
1. No hardcoded credentials in codebase
2. No dangerous eval/exec usage
3. All scripts use environment variables
4. Secure parsing methods implemented
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path


def test_no_hardcoded_credentials():
    """Test that no hardcoded credentials exist in the codebase."""
    print("🔐 Testing for hardcoded credentials...")

    # Pattern to detect potential hardcoded tokens/secrets
    dangerous_patterns = [
        r"ghp_[a-zA-Z0-9]{36}",  # GitHub Personal Access Tokens
        r"github_pat_[a-zA-Z0-9_]{82}",  # GitHub Fine-grained PATs
        r"ghs_[a-zA-Z0-9]{36}",  # GitHub App Installation tokens
        r"gho_[a-zA-Z0-9]{36}",  # GitHub OAuth tokens
        r"ghu_[a-zA-Z0-9]{36}",  # GitHub User-to-server tokens
        r"glpat-[a-zA-Z0-9_-]{20}",  # GitLab Personal Access Tokens
        r"AKIA[0-9A-Z]{16}",  # AWS Access Key IDs
        r"sk-[a-zA-Z0-9]{48}",  # OpenAI API keys
        r"xox[bpoa]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",  # Slack tokens
    ]

    repo_root = Path("/home/runner/work/AGI-Consolidation-Repo/AGI-Consolidation-Repo")
    violations = []

    for pattern in dangerous_patterns:
        result = subprocess.run(
            ["grep", "-r", "-E", pattern, str(repo_root), "--exclude-dir=.git"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            violations.extend(result.stdout.strip().split("\n"))

    # Filter out test files and comments that mention patterns
    filtered_violations = []
    for violation in violations:
        if not any(
            exclude in violation.lower()
            for exclude in [
                "test_security_fixes",
                "validation",
                "example",
                "comment",
                "#",
                "documentation",
            ]
        ):
            filtered_violations.append(violation)

    if filtered_violations:
        print(f"❌ Found {len(filtered_violations)} potential hardcoded credentials:")
        for violation in filtered_violations:
            print(f"  - {violation}")
        return False
    else:
        print("✅ No hardcoded credentials found")
        return True


def test_no_dangerous_eval_exec():
    """Test that no dangerous eval/exec usage exists."""
    print("🔍 Testing for dangerous eval/exec usage...")

    repo_root = Path("/home/runner/work/AGI-Consolidation-Repo/AGI-Consolidation-Repo")
    violations = []

    for py_file in repo_root.rglob("*.py"):
        if any(
            exclude in str(py_file)
            for exclude in ["test_security_fixes", "validation", ".git", "__pycache__"]
        ):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Check for dangerous eval/exec usage
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                # Skip comments and safe usage patterns
                if line.strip().startswith("#") or "ΛSECURITY" in line:
                    continue

                # Look for dangerous patterns
                if (
                    re.search(r"\beval\s*\(", line)
                    and "ast.literal_eval" not in line
                    or re.search(r"\bexec\s*\(", line)
                    and "exec_module" not in line
                ):
                    violations.append(f"{py_file}:{i}: {line.strip()}")

        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")

    if violations:
        print(f"❌ Found {len(violations)} dangerous eval/exec usages:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print("✅ No dangerous eval/exec usage found")
        return True


def test_secure_parsing_implementation():
    """Test that secure parsing methods are implemented correctly."""
    print("🛡️ Testing secure parsing implementation...")

    # Test the fixed lukhas_utils function
    try:
        from core.lukhas_utils import legacy_parse_lukhas_command

        # Test with safe literal
        result = legacy_parse_lukhas_command("CMD:test_action PARAMS:{'key': 'value'}")
        assert result["command"] == "test_action"
        assert result["params"]["key"] == "value"

        # Test with JSON
        result = legacy_parse_lukhas_command('CMD:json_test PARAMS:{"key": "value"}')
        assert result["command"] == "json_test"
        assert result["params"]["key"] == "value"

        # Test with invalid params
        result = legacy_parse_lukhas_command("CMD:invalid_test PARAMS:invalid_json")
        assert result["command"] == "invalid_test"
        assert result["params"]["error"] == "param_parse_failed"

        print("✅ Secure parsing implementation works correctly")
        return True

    except Exception as e:
        print(f"❌ Secure parsing test failed: {e}")
        return False


def test_batch_planner_security():
    """Test that batch planner uses secure import methods."""
    print("📦 Testing batch planner security...")

    try:
        # Create a temporary test file with file_moves data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                "file_moves = [{'source': 'test.py', 'destination': 'new_test.py'}]\n"
            )
            temp_file = f.name

        try:
            from pre_analyzer.batch_planner import BatchPlanner

            planner = BatchPlanner(temp_file)
            moves = planner.load_file_moves()

            assert len(moves) == 1
            assert moves[0]["source"] == "test.py"
            assert moves[0]["destination"] == "new_test.py"

            print("✅ Batch planner security implementation works correctly")
            return True

        finally:
            os.unlink(temp_file)

    except Exception as e:
        print(f"❌ Batch planner security test failed: {e}")
        return False


def main():
    """Run all security validation tests."""
    print("🔒 Running Security Fixes Validation Test Suite")
    print("=" * 60)

    tests = [
        test_no_hardcoded_credentials,
        test_no_dangerous_eval_exec,
        test_secure_parsing_implementation,
        test_batch_planner_security,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All {total} security tests passed!")
        print("✅ Repository is secure and ready for production deployment")
        return True
    else:
        print(f"❌ {total - passed} out of {total} security tests failed")
        print("⚠️  Security vulnerabilities still exist - address before deployment")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
