#!/usr/bin/env python3
"""
Test Migration Script for LUKHAS Repository Reorganization
=========================================================

Systematically migrate 144+ test files from scattered structure to clean categories:
- unit/: Fast, isolated tests
- integration/: I/O, database, API tests  
- contracts/: API contract validation
- e2e/: End-to-end comprehensive tests

Preserves lukhas/ and candidate/ structure within each category.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


def analyze_test_file(file_path: Path) -> Tuple[str, str]:
    """
    Analyze test file to determine category and reason.
    
    Returns:
        Tuple of (category, reason) where category is one of:
        unit, integration, contract, e2e
    """
    content = file_path.read_text()
    filename = file_path.name
    
    # E2E indicators (highest priority)
    e2e_patterns = [
        r'comprehensive.*test',
        r'test.*comprehensive',
        r'e2e',
        r'end.to.end',
        r'@pytest\.mark\.e2e',
        r'test.*all.*systems',
        r'test.*complete.*system',
        r'test.*full.*integration'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) or 
           re.search(pattern, filename, re.IGNORECASE) for pattern in e2e_patterns):
        return "e2e", "comprehensive/system test patterns"
    
    # Integration indicators
    integration_patterns = [
        r'integration',
        r'database|db_|sql|postgres|sqlite',
        r'api.*call|http|requests',
        r'file.*system|filesystem',
        r'network|socket|server',
        r'@pytest\.mark\.integration',
        r'orchestration.*integration',
        r'bridge.*integration'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) or 
           re.search(pattern, filename, re.IGNORECASE) for pattern in integration_patterns):
        return "integration", "I/O or network operations detected"
    
    # Contract indicators  
    contract_patterns = [
        r'contract|api.*schema|schema.*validation',
        r'backwards.*compatibility',
        r'provider.*consumer',
        r'@pytest\.mark\.contract',
        r'interface.*compliance'
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) or 
           re.search(pattern, filename, re.IGNORECASE) for pattern in contract_patterns):
        return "contract", "API contract or interface validation"
    
    # Unit test indicators (default for simple tests)
    unit_patterns = [
        r'@pytest\.mark\.unit',
        r'test.*unit',
        r'unit.*test',
        r'fast.*isolated',
        r'mock|Mock',
        r'no.*io|isolated',
    ]
    
    if any(re.search(pattern, content, re.IGNORECASE) or 
           re.search(pattern, filename, re.IGNORECASE) for pattern in unit_patterns):
        return "unit", "fast isolated test patterns"
    
    # Default categorization based on complexity heuristics
    lines = content.split('\n')
    
    # Smoke tests are usually unit tests
    if 'smoke' in filename or 'smoke' in str(file_path):
        return "unit", "smoke test classification"
        
    # Files with many test methods are likely comprehensive
    test_method_count = len([line for line in lines if re.search(r'def test_', line)])
    if test_method_count > 10:
        return "e2e", "many test methods (comprehensive)"
    
    # Files with database/API setup are integration
    if any(keyword in content.lower() for keyword in ['database', 'api', 'server', 'client', 'engine', 'connection']):
        return "integration", "database/API keywords detected"
    
    # Default to unit for simple tests
    return "unit", "default classification (simple test)"


def get_source_path(test_path: Path) -> str:
    """
    Determine source path structure to preserve in new location.
    
    Maps test structure to preserve lukhas/ and candidate/ hierarchies.
    """
    parts = test_path.parts
    
    # Find key structural elements
    if 'candidate' in parts:
        idx = parts.index('candidate')
        return '/'.join(parts[idx:parts.index(test_path.name)])
    elif 'lukhas' in parts:
        idx = parts.index('lukhas')  
        return '/'.join(parts[idx:parts.index(test_path.name)])
    elif 'core' in parts:
        idx = parts.index('core')
        return '/'.join(parts[idx:parts.index(test_path.name)])
    else:
        # For root-level tests, use direct classification
        if test_path.parent.name == 'tests':
            return 'root'
        return test_path.parent.name


def migrate_tests(source_dir: Path, target_dir: Path) -> Dict[str, List[str]]:
    """
    Migrate all tests from source_dir to target_dir with categorization.
    
    Returns migration report with statistics.
    """
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    
    # Find all test files
    test_files = list(source_dir.rglob("test_*.py"))
    test_files.extend(list(source_dir.rglob("*_test.py")))
    
    migration_report = {
        "unit": [],
        "integration": [], 
        "contract": [],
        "e2e": [],
        "errors": []
    }
    
    print(f"Found {len(test_files)} test files to migrate")
    
    for test_file in test_files:
        try:
            # Skip if already in target directory
            if str(target_dir) in str(test_file):
                continue
                
            # Analyze test file
            category, reason = analyze_test_file(test_file)
            source_path = get_source_path(test_file)
            
            # Create target directory structure
            if source_path == 'root':
                target_path = target_dir / category / test_file.name
            else:
                target_path = target_dir / category / source_path / test_file.name
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(test_file, target_path)
            
            migration_entry = f"{test_file} -> {target_path} ({reason})"
            migration_report[category].append(migration_entry)
            
            print(f"✅ {category}: {test_file.name}")
            
        except Exception as e:
            error_msg = f"❌ {test_file}: {str(e)}"
            migration_report["errors"].append(error_msg)
            print(error_msg)
    
    return migration_report


def copy_support_files(source_dir: Path, target_dir: Path):
    """Copy conftest.py and other support files maintaining structure."""
    
    support_patterns = ["conftest.py", "*.ini", "*.cfg", "fixtures"]
    
    for pattern in support_patterns:
        support_files = list(source_dir.rglob(pattern))
        
        for support_file in support_files:
            if support_file.is_file():
                # Preserve relative path structure
                rel_path = support_file.relative_to(source_dir)
                
                # Copy to each category that needs it
                categories = ["unit", "integration", "contract", "e2e"]
                for category in categories:
                    target_path = target_dir / category / rel_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(support_file, target_path)
                    
                print(f"📋 Support: {support_file.name} -> {category}/")


if __name__ == "__main__":
    source = Path("tests")
    target = Path("tests_new")
    
    print("🚀 Starting LUKHAS test migration...")
    print(f"Source: {source}")
    print(f"Target: {target}")
    print()
    
    # Migrate tests
    report = migrate_tests(source, target)
    
    print("\n📋 Copying support files...")
    copy_support_files(source, target)
    
    # Print summary
    print("\n📊 Migration Summary:")
    print("=" * 50)
    for category, files in report.items():
        if category != "errors":
            print(f"{category.upper()}: {len(files)} files")
    
    if report["errors"]:
        print(f"\n❌ ERRORS: {len(report['errors'])} files failed")
        for error in report["errors"][:5]:  # Show first 5 errors
            print(f"   {error}")
    
    print(f"\n✅ Migration complete: {sum(len(files) for cat, files in report.items() if cat != 'errors')} files migrated")