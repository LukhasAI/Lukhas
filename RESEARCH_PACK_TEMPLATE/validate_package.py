#!/usr/bin/env python3
"""
Research Package Validation Script
Ensures all components meet research standards
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()

def check_directory_exists(dirpath: str) -> bool:
    """Check if a directory exists"""
    return Path(dirpath).is_dir()

def validate_structure() -> Tuple[bool, List[str]]:
    """Validate package directory structure"""
    required_dirs = [
        'src',
        'tests',
        'data',
        'test_results',
        'api_docs',
        'visualizations',
        'docs'
    ]
    
    required_files = [
        'README.md',
        'EXECUTIVE_SUMMARY.md',
        'requirements.txt',
        '.env.example',
        'Makefile',
        'Dockerfile',
        'RESEARCH_MANIFEST.yaml',
        'RESEARCH_RELEASE_NOTES.md',
        'RESEARCH_QUALITY_CHECKLIST.md',
        'MODEL_CARD.md',
        'DATA_STATEMENT.md'
    ]
    
    missing = []
    
    for dir_name in required_dirs:
        if not check_directory_exists(dir_name):
            missing.append(f"Directory: {dir_name}")
    
    for file_name in required_files:
        if not check_file_exists(file_name):
            missing.append(f"File: {file_name}")
    
    return len(missing) == 0, missing

def validate_manifest() -> Tuple[bool, List[str]]:
    """Validate RESEARCH_MANIFEST.yaml contents"""
    issues = []
    
    if not check_file_exists('RESEARCH_MANIFEST.yaml'):
        return False, ["RESEARCH_MANIFEST.yaml not found"]
    
    try:
        with open('RESEARCH_MANIFEST.yaml', 'r') as f:
            manifest = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['package', 'artifacts', 'safety_and_ethics', 'reproducibility', 'metrics']
        for section in required_sections:
            if section not in manifest:
                issues.append(f"Missing section: {section}")
        
        # Check package metadata
        if 'package' in manifest:
            required_fields = ['name', 'version', 'date', 'owner', 'contact']
            for field in required_fields:
                if field not in manifest['package']:
                    issues.append(f"Missing package field: {field}")
        
    except Exception as e:
        issues.append(f"Error parsing manifest: {e}")
    
    return len(issues) == 0, issues

def validate_safety_compliance() -> Tuple[bool, List[str]]:
    """Validate safety and compliance documentation"""
    issues = []
    
    # Check for safety disclaimers
    files_to_check = ['README.md', 'EXECUTIVE_SUMMARY.md', 'DATA_STATEMENT.md']
    
    for file_path in files_to_check:
        if check_file_exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().lower()
                
                # Check for required safety language
                if 'synthetic' not in content and 'test' in file_path:
                    issues.append(f"{file_path}: Missing 'synthetic' data disclaimer")
                
                if 'research' not in content:
                    issues.append(f"{file_path}: Missing 'research' disclaimer")
    
    return len(issues) == 0, issues

def validate_reproducibility() -> Tuple[bool, List[str]]:
    """Check reproducibility requirements"""
    issues = []
    
    # Check for seed configuration
    if check_file_exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            if 'SEED' not in content and 'seed' not in content.lower():
                issues.append(".env.example: Missing seed configuration")
    
    # Check for requirements.txt
    if not check_file_exists('requirements.txt'):
        issues.append("requirements.txt: Missing dependency specification")
    
    return len(issues) == 0, issues

def check_humble_tone() -> Tuple[bool, List[str]]:
    """Check for inappropriate promotional language"""
    issues = []
    promotional_terms = [
        'breakthrough',
        'revolutionary',
        'patent-pending',
        'first-to-market',
        'cutting-edge',
        'state-of-the-art',
        'world-class',
        'industry-leading'
    ]
    
    docs_to_check = ['README.md', 'EXECUTIVE_SUMMARY.md']
    
    for file_path in docs_to_check:
        if check_file_exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().lower()
                for term in promotional_terms:
                    if term in content:
                        issues.append(f"{file_path}: Contains promotional term '{term}'")
    
    return len(issues) == 0, issues

def main():
    """Run all validation checks"""
    print("="*60)
    print("LUKHAS Innovation System - Research Package Validation")
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
        for item in missing_items[:10]:  # Show first 10
            print(f"      - {item}")
        if len(missing_items) > 10:
            print(f"      ... and {len(missing_items) - 10} more")
        all_valid = False
    print()
    
    # 2. Validate manifest
    print("2. Validating Research Manifest...")
    manifest_valid, manifest_issues = validate_manifest()
    if manifest_valid:
        print("   ✅ Manifest structure valid")
    else:
        print("   ❌ Manifest issues:")
        for issue in manifest_issues:
            print(f"      - {issue}")
        all_valid = False
    print()
    
    # 3. Check safety compliance
    print("3. Checking Safety & Compliance...")
    safety_valid, safety_issues = validate_safety_compliance()
    if safety_valid:
        print("   ✅ Safety documentation present")
    else:
        print("   ⚠️  Safety documentation issues:")
        for issue in safety_issues:
            print(f"      - {issue}")
    print()
    
    # 4. Validate reproducibility
    print("4. Checking Reproducibility...")
    repro_valid, repro_issues = validate_reproducibility()
    if repro_valid:
        print("   ✅ Reproducibility requirements met")
    else:
        print("   ❌ Reproducibility issues:")
        for issue in repro_issues:
            print(f"      - {issue}")
        all_valid = False
    print()
    
    # 5. Check tone
    print("5. Checking Documentation Tone...")
    tone_valid, tone_issues = check_humble_tone()
    if tone_valid:
        print("   ✅ Documentation uses appropriate research tone")
    else:
        print("   ⚠️  Tone adjustments recommended:")
        for issue in tone_issues:
            print(f"      - {issue}")
    print()
    
    # Summary
    print("="*60)
    if all_valid:
        print("✅ VALIDATION SUCCESSFUL - Package meets research standards!")
        print()
        print("Next steps:")
        print("1. Run 'make test' to execute quick baseline tests")
        print("2. Run 'make analyze' to generate analysis reports")
        print("3. Review RESEARCH_QUALITY_CHECKLIST.md")
    else:
        print("❌ VALIDATION FAILED - Please address the issues above")
        print()
        print("To fix issues:")
        print("1. Review missing files/directories")
        print("2. Update documentation tone if needed")
        print("3. Ensure all safety disclaimers are present")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())