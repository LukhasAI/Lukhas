#!/usr/bin/env python3
"""
Package Validation Script
Ensures all components are present and functional
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()

def check_directory_exists(dirpath: str) -> bool:
    """Check if a directory exists"""
    return Path(dirpath).is_dir()

def check_python_import(module: str) -> bool:
    """Check if a Python module can be imported"""
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def validate_structure() -> Tuple[bool, List[str]]:
    """Validate package directory structure"""
    required_dirs = [
        'src',
        'data',
        'test_results',
        'api_docs',
        'visualizations',
        'logs',
        'research_data'
    ]

    required_files = [
        'README.md',
        'requirements.txt',
        '.env.example',
        'Makefile',
        'setup.py',
        'INSTALLATION_GUIDE.md',
        'EXECUTIVE_SUMMARY.md'
    ]

    missing = []

    for dir_name in required_dirs:
        if not check_directory_exists(dir_name):
            missing.append(f"Directory: {dir_name}")

    for file_name in required_files:
        if not check_file_exists(file_name):
            missing.append(f"File: {file_name}")

    return len(missing) == 0, missing

def validate_dependencies() -> Tuple[bool, List[str]]:
    """Validate Python dependencies"""
    required_modules = [
        'numpy',
        'asyncio',
        'json',
        'pathlib',
        'dataclasses',
        'enum',
        'typing',
        'statistics'
    ]

    optional_modules = [
        'openai',
        'pandas',
        'pytest'
    ]

    missing_required = []
    missing_optional = []

    for module in required_modules:
        if not check_python_import(module):
            missing_required.append(module)

    for module in optional_modules:
        if not check_python_import(module):
            missing_optional.append(module)

    return len(missing_required) == 0, missing_required, missing_optional

def validate_environment() -> Dict[str, bool]:
    """Validate environment configuration"""
    checks = {}

    # Check for .env file
    checks['env_file_exists'] = check_file_exists('.env')

    # Check for API key in environment
    checks['openai_key_set'] = bool(os.getenv('OPENAI_API_KEY'))

    # Check Python version
    py_version = sys.version_info
    checks['python_version_ok'] = py_version.major == 3 and py_version.minor >= 8

    return checks

def validate_test_files() -> Tuple[bool, List[str]]:
    """Validate test files are present"""
    test_files = [
        'src/test_innovation_quick_baseline.py',
        'src/test_innovation_research_baseline.py',
        'src/test_innovation_api_live.py',
        'src/analyze_pass_rate_factors.py'
    ]

    missing = []
    for file_path in test_files:
        if not check_file_exists(file_path):
            missing.append(file_path)

    return len(missing) == 0, missing

def validate_core_modules() -> Tuple[bool, List[str]]:
    """Validate core module files"""
    core_files = [
        'src/core/__init__.py',
        'src/core/common.py'
    ]

    missing = []
    for file_path in core_files:
        if not check_file_exists(file_path):
            missing.append(file_path)

    return len(missing) == 0, missing

def main():
    """Run all validation checks"""
    print("="*60)
    print("LUKHAS Innovation System - Package Validation")
    print("="*60)
    print()

    all_valid = True

    # 1. Check directory structure
    print("1. Checking Directory Structure...")
    structure_valid, missing_items = validate_structure()
    if structure_valid:
        print("   ✅ All directories and files present")
    else:
        print("   ❌ Missing items:")
        for item in missing_items:
            print(f"      - {item}")
        all_valid = False
    print()

    # 2. Check dependencies
    print("2. Checking Python Dependencies...")
    deps_valid, missing_req, missing_opt = validate_dependencies()
    if deps_valid:
        print("   ✅ All required dependencies installed")
    else:
        print("   ❌ Missing required dependencies:")
        for dep in missing_req:
            print(f"      - {dep}")
        all_valid = False

    if missing_opt:
        print("   ⚠️  Missing optional dependencies:")
        for dep in missing_opt:
            print(f"      - {dep}")
    print()

    # 3. Check environment
    print("3. Checking Environment Configuration...")
    env_checks = validate_environment()
    for check, passed in env_checks.items():
        status = "✅" if passed else "❌"
        check_name = check.replace('_', ' ').title()
        print(f"   {status} {check_name}")

    if not all(env_checks.values()):
        all_valid = False
    print()

    # 4. Check test files
    print("4. Checking Test Files...")
    tests_valid, missing_tests = validate_test_files()
    if tests_valid:
        print("   ✅ All test files present")
    else:
        print("   ❌ Missing test files:")
        for test in missing_tests:
            print(f"      - {test}")
        all_valid = False
    print()

    # 5. Check core modules
    print("5. Checking Core Modules...")
    core_valid, missing_core = validate_core_modules()
    if core_valid:
        print("   ✅ Core modules present")
    else:
        print("   ❌ Missing core modules:")
        for module in missing_core:
            print(f"      - {module}")
        all_valid = False
    print()

    # Summary
    print("="*60)
    if all_valid:
        print("✅ VALIDATION SUCCESSFUL - Package is ready for use!")
        print()
        print("Next steps:")
        print("1. Set up your OpenAI API key in .env file")
        print("2. Run 'make test' to execute quick baseline tests")
        print("3. Run 'make analyze' to generate analysis reports")
    else:
        print("❌ VALIDATION FAILED - Please address the issues above")
        print()
        print("To fix issues:")
        print("1. Run 'make setup' to install dependencies")
        print("2. Copy .env.example to .env and add your API key")
        print("3. Ensure all required files are present")

    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
