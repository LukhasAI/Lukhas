#!/usr/bin/env python3
"""
Codex Test Validation Script
============================

This script validates that the test environment is properly set up
for Codex to run tests successfully. It checks dependencies, imports,
and provides clear feedback about what's missing.

# ΛTAG: codex, test_validation
"""

import importlib
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version compatible")
        return True


def check_critical_imports():
    """Check if critical packages can be imported"""
    critical_packages = [
        ("numpy", "numpy>=1.20.0"),
        ("structlog", "structlog>=25.0.0"),
        ("pytest", "pytest>=8.0.0"),
        ("pandas", "pandas>=1.0.0"),
        ("requests", "requests>=2.25.0"),
        ("yaml", "PyYAML>=6.0.0"),
        ("aiohttp", "aiohttp>=3.8.0"),
        ("fastapi", "fastapi>=0.100.0"),
        ("pydantic", "pydantic>=2.0.0"),
    ]

    missing_packages = []

    for package, requirement in critical_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package} v{version}")
        except ImportError:
            print(f"❌ {package} missing ({requirement})")
            missing_packages.append(requirement)

    return missing_packages


def check_test_files():
    """Check if test files exist and are accessible"""
    test_dir = Path("tests")

    if not test_dir.exists():
        print("❌ tests/ directory not found")
        return False

    test_files = list(test_dir.rglob("test_*.py"))
    print(f"📁 Found {len(test_files)} test files")

    if len(test_files) == 0:
        print("❌ No test files found")
        return False

    # Check for problematic imports in test files
    problematic_files = []
    for test_file in test_files[:5]:  # Check first 5 files
        try:
            with open(test_file) as f:
                content = f.read()
                if "import numpy" in content or "import structlog" in content:
                    print(f"📄 {test_file.name} uses numpy/structlog")
        except Exception as e:
            problematic_files.append((test_file, str(e)))

    if problematic_files:
        print(f"⚠️ {len(problematic_files)} files have issues")
        for file, error in problematic_files:
            print(f"   {file}: {error}")

    return True


def run_basic_test():
    """Run a basic test to verify pytest works"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print(f"✅ pytest available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ pytest check failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ pytest check timed out")
        return False
    except Exception as e:
        print(f"❌ pytest check error: {e}")
        return False


def check_make_command():
    """Check if make command works"""
    try:
        result = subprocess.run(
            ["make", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ make command available")
            return True
        else:
            print("❌ make command not available")
            return False
    except Exception as e:
        print(f"❌ make command check failed: {e}")
        return False


def generate_fix_instructions(missing_packages):
    """Generate instructions for fixing issues"""
    print("\n🔧 FIX INSTRUCTIONS:")
    print("=" * 50)

    if missing_packages:
        print("📦 Missing packages - run one of these commands:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("   OR")
        print("   ./install_container_deps.sh")
        print("   OR")
        print("   make install-container")

    print("\n🐳 For containerized environments:")
    print("   1. Run: make install-container")
    print("   2. Run: make test-container")
    print("   3. Or run: ./install_container_deps.sh && make test")

    print("\n📋 Manual verification:")
    print("   python3 -c \"import numpy, structlog, pytest; print('✅ All good')\"")


def main():
    """Main validation function"""
    print("🔍 CODEX TEST ENVIRONMENT VALIDATION")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check critical imports
    missing_packages = check_critical_imports()

    # Check test files
    test_files_ok = check_test_files()

    # Check pytest
    pytest_ok = run_basic_test()

    # Check make command
    make_ok = check_make_command()

    # Summary
    print("\n📊 VALIDATION SUMMARY:")
    print("=" * 30)

    issues = []
    if missing_packages:
        issues.append(f"Missing packages: {len(missing_packages)}")
    if not test_files_ok:
        issues.append("Test files issues")
    if not pytest_ok:
        issues.append("pytest not working")
    if not make_ok:
        issues.append("make not available")

    if issues:
        print(f"❌ Issues found: {', '.join(issues)}")
        generate_fix_instructions(missing_packages)
        sys.exit(1)
    else:
        print("✅ All checks passed - ready for testing!")
        print("\n🚀 Run 'make test' or 'make test-container' to run tests")


if __name__ == "__main__":
    main()
