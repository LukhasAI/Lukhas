#!/usr/bin/env python3
"""
Quick Component Scan for LUKHAS AI Dashboard
Fast analysis without external dependencies
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict

def quick_scan():
    """Perform a quick scan of LUKHAS components"""
    results = {
        "timestamp": "2025-01-17T10:30:00Z",
        "total_modules": 0,
        "orphaned_candidates": [],
        "integration_opportunities": [],
        "module_categories": defaultdict(int),
        "recommendations": []
    }
    
    # Quick file scan
    exclude_dirs = {'.venv', 'node_modules', '__pycache__', '.git', 'TEST-ENHANCEMENTS'}
    py_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    results["total_modules"] = len(py_files)
    
    # Categorize modules by directory
    for file_path in py_files:
        parts = file_path.split(os.sep)
        if len(parts) > 1:
            category = parts[1] if parts[0] == '.' else parts[0]
            results["module_categories"][category] += 1
    
    # Find potential orphaned modules (heuristic)
    for file_path in py_files:
        if '/tests/' in file_path or '__init__.py' in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Simple heuristics for orphaned modules
            has_classes = 'class ' in content
            has_functions = 'def ' in content
            lines_of_code = len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])
            
            # Check if file is referenced elsewhere (simple search)
            filename = os.path.basename(file_path).replace('.py', '')
            is_referenced = False
            
            # Quick check in a few key files
            check_files = ['main.py', 'core/bootstrap.py', 'orchestration/brain/primary_hub.py']
            for check_file in check_files:
                if os.path.exists(check_file):
                    try:
                        with open(check_file, 'r', encoding='utf-8', errors='ignore') as f:
                            if filename in f.read():
                                is_referenced = True
                                break
                    except:
                        continue
            
            if (has_classes or has_functions) and lines_of_code > 20 and not is_referenced:
                results["orphaned_candidates"].append({
                    "path": file_path,
                    "lines_of_code": lines_of_code,
                    "has_classes": has_classes,
                    "has_functions": has_functions
                })
                
        except Exception:
            continue
    
    # Find integration opportunities
    categories = dict(results["module_categories"])
    for category, count in categories.items():
        if count > 3 and category not in ['tests', '__pycache__']:
            results["integration_opportunities"].append({
                "category": category,
                "module_count": count,
                "potential": "high" if count > 10 else "medium"
            })
    
    # Generate recommendations
    if len(results["orphaned_candidates"]) > 0:
        results["recommendations"].append({
            "type": "cleanup",
            "priority": "medium",
            "message": f"Found {len(results['orphaned_candidates'])} potentially orphaned modules"
        })
    
    if len(results["integration_opportunities"]) > 0:
        results["recommendations"].append({
            "type": "integration", 
            "priority": "high",
            "message": f"Found {len(results['integration_opportunities'])} categories with consolidation potential"
        })
    
    return results

if __name__ == "__main__":
    result = quick_scan()
    print(json.dumps(result, indent=2))