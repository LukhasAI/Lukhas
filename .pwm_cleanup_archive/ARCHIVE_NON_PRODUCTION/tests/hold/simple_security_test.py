#!/usr/bin/env python3
"""
Simple security test runner without pytest dependency
"""

import re
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_no_hardcoded_passwords():
    """Test that no hardcoded passwords exist in the codebase"""
    print("Testing for hardcoded passwords...")

    # Pattern to match hardcoded passwords
    password_patterns = [
        r'password\s*=\s*["\'][^"\']*["\']',
        r'PASSWORD\s*=\s*["\'][^"\']*["\']',
        r'default_password\s*=\s*["\'][^"\']*["\']',
    ]

    violations = []

    for py_file in project_root.rglob("*.py"):
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue
        # Skip virtual environment directories
        if ".venv" in str(py_file) or "/venv/" in str(py_file):
            continue
        # Skip third-party packages
        if "site-packages" in str(py_file):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            for pattern in password_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Allow test passwords and environment variable fallbacks
                    if "test_password" in match or "getenv" in match:
                        continue
                    violations.append(f"{py_file}: {match}")

        except (OSError, UnicodeDecodeError):
            continue

    if violations:
        print(f"❌ FAILED: Hardcoded passwords found: {violations}")
        assert False, f"Hardcoded passwords found: {violations}"
    else:
        print("✅ PASSED: No hardcoded passwords found")
        assert True


def test_yubiseeder_security():
    """Test that YubiSeeder uses secure authentication"""
    print("Testing YubiSeeder security...")

    yubi_file = project_root / "lukhas-id" / "backend" / "verifold" / "yubi_seeder.py"

    if not yubi_file.exists():
        print("⚠️  SKIPPED: YubiSeeder file not found")
        assert True

    with open(yubi_file, encoding="utf-8") as f:
        content = f.read()

    # Check that hardcoded password is removed
    if 'password or "password"' in content:
        print("❌ FAILED: Hardcoded password still present")
        assert False, "Hardcoded password still present"

    # Check that environment variable is used
    if "os.getenv(" not in content:
        print("❌ FAILED: Environment variable usage not found")
        assert False, "Environment variable usage not found"

    # Check that proper error handling is in place
    if "ValueError" not in content and "Exception" not in content:
        print("❌ FAILED: Proper error handling not found")
        assert False, "Proper error handling not found"

    print("✅ PASSED: YubiSeeder security is good")
    assert True


def test_subprocess_security():
    """Test that subprocess usage is secure"""
    print("Testing subprocess security...")

    script_files = [
        project_root / "temporary-scripts" / "lambda_syntax_fixer.py",
        project_root / "orchestration" / "ΛDependaBoT_fixed.py",
    ]

    for script_file in script_files:
        if not script_file.exists():
            continue

        with open(script_file, encoding="utf-8") as f:
            content = f.read()

        # Check for subprocess usage
        if "subprocess." in content:
            # Check for timeout parameter
            if "timeout=" not in content:
                print(f"❌ FAILED: Subprocess timeout missing in {script_file}")
                assert False, f"Subprocess timeout missing in {script_file}"

            # Check for path validation
            if "resolve()" in content and "startswith(" not in content:
                print(f"❌ FAILED: Path validation missing in {script_file}")
                assert False, f"Path validation missing in {script_file}"

    print("✅ PASSED: Subprocess security is good")
    assert True


def test_dependency_versions():
    """Test that high-risk dependencies are updated"""
    print("Testing dependency versions...")

    req_file = project_root / "requirements.txt"

    if not req_file.exists():
        print("⚠️  SKIPPED: requirements.txt not found")
        assert True

    with open(req_file, encoding="utf-8") as f:
        content = f.read()

    # Check for updated versions
    version_checks = [
        ("PyYAML>=6.0.2", "PyYAML not updated to secure version"),
        ("cryptography>=41.0.0", "cryptography not updated to secure version"),
        ("requests>=2.31.0", "requests not updated to secure version"),
        ("urllib3>=2.0.0", "urllib3 not updated to secure version"),
        ("pillow>=10.0.0", "pillow not updated to secure version"),
    ]

    for version_check, error_msg in version_checks:
        if version_check not in content:
            print(f"❌ FAILED: {error_msg}")
            assert False, error_msg

    print("✅ PASSED: All dependency versions are updated")
    assert True


def test_no_shell_injection():
    """Test that shell injection vulnerabilities are not present"""
    print("Testing for shell injection vulnerabilities...")

    # Patterns that could indicate shell injection vulnerabilities
    dangerous_patterns = [
        r"os\.system\([^)]*\)",
        r"subprocess\.call\([^)]*shell=True[^)]*\)",
        r"subprocess\.run\([^)]*shell=True[^)]*\)",
        r"subprocess\.Popen\([^)]*shell=True[^)]*\)",
    ]

    violations = []

    for py_file in project_root.rglob("*.py"):
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue
        # Skip virtual environment directories
        if ".venv" in str(py_file) or "/venv/" in str(py_file):
            continue
        # Skip third-party packages
        if "site-packages" in str(py_file):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            for pattern in dangerous_patterns:
                if re.search(pattern, content):
                    violations.append(f"{py_file}: {pattern}")

        except (OSError, UnicodeDecodeError):
            continue

    if violations:
        print(f"❌ FAILED: Shell injection vulnerabilities found: {violations}")
        assert False, f"Shell injection vulnerabilities found: {violations}"
    else:
        print("✅ PASSED: No shell injection vulnerabilities found")
        assert True


def main():
    """Run all security tests"""
    print("🔒 Running Security Tests")
    print("=" * 50)

    tests = [
        test_no_hardcoded_passwords,
        test_yubiseeder_security,
        test_subprocess_security,
        test_dependency_versions,
        test_no_shell_injection,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAILED: {test.__name__} - {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All security tests passed!")
        return 0
    else:
        print("⚠️  Some security tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
