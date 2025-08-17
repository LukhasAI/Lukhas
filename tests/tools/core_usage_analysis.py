#!/usr/bin/env python3
"""
Core Directory Usage Analysis for LUKHAS
Identifies which core subdirectories are actually used
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_core_usage():
    """Analyze usage of core subdirectories"""
    
    # Get all subdirectories in core/
    core_dirs = []
    core_path = Path('core')
    
    if not core_path.exists():
        print("❌ core/ directory not found")
        return
    
    for item in core_path.iterdir():
        if item.is_dir() and not item.name.startswith('__'):
            core_dirs.append(item.name)
    
    print(f"📁 Found {len(core_dirs)} subdirectories in core/")
    print("=" * 60)
    
    # Track usage
    usage_count = defaultdict(int)
    importing_files = defaultdict(set)
    
    # Search for imports
    for py_file in Path('.').rglob('*.py'):
        # Skip test files and cache
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Find imports from core.xxx
            imports = re.findall(r'from\s+core\.([a-zA-Z_]+)', content)
            for module in imports:
                if module in core_dirs:
                    usage_count[module] += 1
                    importing_files[module].add(str(py_file))
                    
        except Exception:
            continue
    
    # Categorize directories
    heavily_used = []
    moderately_used = []
    rarely_used = []
    unused = []
    
    for dir_name in sorted(core_dirs):
        count = usage_count.get(dir_name, 0)
        
        if count == 0:
            unused.append(dir_name)
        elif count < 5:
            rarely_used.append((dir_name, count))
        elif count < 20:
            moderately_used.append((dir_name, count))
        else:
            heavily_used.append((dir_name, count))
    
    # Print results
    print("\n✅ HEAVILY USED (20+ imports):")
    print("-" * 40)
    for name, count in sorted(heavily_used, key=lambda x: x[1], reverse=True):
        print(f"  {name:20} - {count:3} imports")
    
    print("\n📊 MODERATELY USED (5-19 imports):")
    print("-" * 40)
    for name, count in sorted(moderately_used, key=lambda x: x[1], reverse=True):
        print(f"  {name:20} - {count:3} imports")
    
    print("\n⚠️  RARELY USED (1-4 imports):")
    print("-" * 40)
    for name, count in sorted(rarely_used, key=lambda x: x[1], reverse=True):
        print(f"  {name:20} - {count:3} imports")
        # Show which files import it
        importers = list(importing_files[name])[:3]
        for importer in importers:
            print(f"      ← {importer}")
    
    print("\n❌ UNUSED DIRECTORIES (0 imports):")
    print("-" * 40)
    for name in sorted(unused):
        # Check if directory has any Python files
        dir_path = core_path / name
        py_files = list(dir_path.rglob('*.py'))
        non_init_files = [f for f in py_files if f.name != '__init__.py']
        
        if non_init_files:
            print(f"  {name:20} - {len(non_init_files)} Python files")
        else:
            print(f"  {name:20} - Empty or only __init__.py")
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 SUMMARY:")
    print(f"  Total directories: {len(core_dirs)}")
    print(f"  Heavily used: {len(heavily_used)}")
    print(f"  Moderately used: {len(moderately_used)}")
    print(f"  Rarely used: {len(rarely_used)}")
    print(f"  Unused: {len(unused)}")
    print(f"  Unused percentage: {len(unused) / len(core_dirs) * 100:.1f}%")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if len(unused) > 10:
        print(f"  ⚠️  {len(unused)} directories are completely unused!")
        print("  Consider:")
        print("    1. Removing unused directories")
        print("    2. Consolidating rarely-used modules")
        print("    3. Documenting why unused code exists")
    
    # List candidates for removal
    print("\n🗑️  CANDIDATES FOR REMOVAL (unused with content):")
    for name in sorted(unused):
        dir_path = core_path / name
        py_files = list(dir_path.rglob('*.py'))
        non_init_files = [f for f in py_files if f.name != '__init__.py']
        
        if non_init_files:
            total_lines = 0
            for f in non_init_files:
                try:
                    with open(f, 'r') as file:
                        total_lines += len(file.readlines())
                except:
                    pass
            
            if total_lines > 100:
                print(f"  core/{name}/ - {len(non_init_files)} files, {total_lines} lines")

if __name__ == "__main__":
    analyze_core_usage()