#!/usr/bin/env python3
"""
Component Usage Analyzer for LUKHAS AI
Identifies orphaned modules and component usage patterns
"""

import os
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
import subprocess
import re

class LUKHASComponentAnalyzer:
    """Analyze LUKHAS component usage and identify orphaned modules"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.modules = {}
        self.imports = defaultdict(set)
        self.usage_map = defaultdict(set)
        self.orphaned_modules = []
        self.integration_opportunities = []
        
    def analyze_repository(self) -> Dict[str, Any]:
        """Perform comprehensive repository analysis"""
        print("🔍 Analyzing LUKHAS repository structure...")
        
        # Step 1: Discover all Python modules
        self._discover_modules()
        
        # Step 2: Analyze imports and dependencies
        self._analyze_imports()
        
        # Step 3: Identify orphaned modules
        self._identify_orphaned_modules()
        
        # Step 4: Find integration opportunities
        self._find_integration_opportunities()
        
        # Step 5: Generate report
        return self._generate_report()
    
    def _discover_modules(self):
        """Discover all Python modules in the repository"""
        print("📁 Discovering Python modules...")
        
        # Exclude certain directories
        exclude_dirs = {'.venv', 'node_modules', '__pycache__', '.git', 'TEST-ENHANCEMENTS'}
        
        for py_file in self.repo_root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in exclude_dirs):
                continue
                
            relative_path = py_file.relative_to(self.repo_root)
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse AST to extract module information
                try:
                    tree = ast.parse(content)
                    module_info = self._extract_module_info(tree, str(relative_path))
                    self.modules[str(relative_path)] = module_info
                except SyntaxError:
                    # Skip files with syntax errors
                    continue
                    
            except (UnicodeDecodeError, PermissionError):
                continue
    
    def _extract_module_info(self, tree: ast.AST, file_path: str) -> Dict[str, Any]:
        """Extract information from module AST"""
        info = {
            "path": file_path,
            "classes": [],
            "functions": [],
            "imports": [],
            "docstring": ast.get_docstring(tree),
            "lines_of_code": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                info["classes"].append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.FunctionDef):
                info["functions"].append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "docstring": ast.get_docstring(node),
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                        self.imports[file_path].add(alias.name)
                else:  # ImportFrom
                    if node.module:
                        info["imports"].append(node.module)
                        self.imports[file_path].add(node.module)
        
        # Count lines of code (approximate)
        try:
            with open(self.repo_root / file_path, 'r') as f:
                info["lines_of_code"] = len([line for line in f if line.strip() and not line.strip().startswith('#')])
        except:
            pass
            
        return info
    
    def _analyze_imports(self):
        """Analyze import patterns and dependencies"""
        print("🔗 Analyzing import patterns...")
        
        for module_path, module_info in self.modules.items():
            for import_name in module_info["imports"]:
                # Find modules that might be imported by this import
                for other_path in self.modules.keys():
                    # Simple heuristic: if import name matches part of path
                    if self._import_matches_module(import_name, other_path):
                        self.usage_map[other_path].add(module_path)
    
    def _import_matches_module(self, import_name: str, module_path: str) -> bool:
        """Check if an import name matches a module path"""
        # Convert module path to import-like format
        module_parts = module_path.replace('.py', '').replace('/', '.').split('.')
        import_parts = import_name.split('.')
        
        # Check for partial matches
        return any(
            all(imp_part in mod_part for imp_part, mod_part in zip(import_parts, module_parts[i:]))
            for i in range(len(module_parts) - len(import_parts) + 1)
        )
    
    def _identify_orphaned_modules(self):
        """Identify modules that appear to be orphaned"""
        print("🏚️ Identifying orphaned modules...")
        
        for module_path, module_info in self.modules.items():
            # Skip test files and __init__.py files
            if '/tests/' in module_path or module_path.endswith('__init__.py'):
                continue
                
            # Check if module is used by others
            used_by = self.usage_map.get(module_path, set())
            
            # Check if module has main functionality
            has_classes = len(module_info["classes"]) > 0
            has_functions = len(module_info["functions"]) > 0
            has_substantial_code = module_info["lines_of_code"] > 10
            
            # Consider orphaned if:
            # 1. Not used by other modules (or used by very few)
            # 2. Has some functionality
            # 3. Not a configuration or utility file
            if (len(used_by) <= 1 and 
                (has_classes or has_functions) and 
                has_substantial_code and
                not self._is_utility_file(module_path)):
                
                self.orphaned_modules.append({
                    "path": module_path,
                    "used_by": list(used_by),
                    "classes": len(module_info["classes"]),
                    "functions": len(module_info["functions"]),
                    "lines_of_code": module_info["lines_of_code"],
                    "docstring": module_info["docstring"]
                })
    
    def _is_utility_file(self, module_path: str) -> bool:
        """Check if file appears to be a utility/config file"""
        utility_patterns = ['config', 'settings', 'constants', 'utils', '__main__']
        return any(pattern in module_path.lower() for pattern in utility_patterns)
    
    def _find_integration_opportunities(self):
        """Find potential integration opportunities"""
        print("🔗 Finding integration opportunities...")
        
        # Group modules by functionality (based on path and names)
        functionality_groups = defaultdict(list)
        
        for module_path, module_info in self.modules.items():
            # Extract functional area from path
            path_parts = module_path.split('/')
            if len(path_parts) > 1:
                functional_area = path_parts[0]
                functionality_groups[functional_area].append(module_path)
        
        # Find opportunities within each functional area
        for area, modules in functionality_groups.items():
            if len(modules) > 1:
                self.integration_opportunities.append({
                    "functional_area": area,
                    "modules": modules,
                    "module_count": len(modules),
                    "integration_potential": self._assess_integration_potential(modules)
                })
    
    def _assess_integration_potential(self, modules: List[str]) -> str:
        """Assess integration potential for a group of modules"""
        total_classes = sum(len(self.modules[m]["classes"]) for m in modules if m in self.modules)
        total_functions = sum(len(self.modules[m]["functions"]) for m in modules if m in self.modules)
        
        if total_classes > 5 or total_functions > 10:
            return "high"
        elif total_classes > 2 or total_functions > 5:
            return "medium"
        else:
            return "low"
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("📊 Generating analysis report...")
        
        report = {
            "analysis_summary": {
                "total_modules": len(self.modules),
                "orphaned_modules": len(self.orphaned_modules),
                "integration_opportunities": len(self.integration_opportunities),
                "functional_areas": len(set(m.split('/')[0] for m in self.modules.keys() if '/' in m))
            },
            "orphaned_modules": self.orphaned_modules,
            "integration_opportunities": self.integration_opportunities,
            "module_usage_map": {
                path: list(used_by) for path, used_by in self.usage_map.items()
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommendations for orphaned modules
        if self.orphaned_modules:
            recommendations.append({
                "type": "orphaned_cleanup",
                "priority": "medium",
                "action": f"Review {len(self.orphaned_modules)} orphaned modules for potential removal or integration",
                "details": f"Found {len(self.orphaned_modules)} modules with minimal usage"
            })
        
        # Recommendations for integration opportunities
        high_potential_areas = [
            opp for opp in self.integration_opportunities 
            if opp["integration_potential"] == "high"
        ]
        
        if high_potential_areas:
            recommendations.append({
                "type": "integration_opportunity",
                "priority": "high", 
                "action": f"Consider consolidating modules in {len(high_potential_areas)} functional areas",
                "details": f"Areas with high integration potential: {[area['functional_area'] for area in high_potential_areas]}"
            })
        
        return recommendations


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    else:
        repo_root = "."
    
    analyzer = LUKHASComponentAnalyzer(repo_root)
    report = analyzer.analyze_repository()
    
    # Output report as JSON
    print("\n" + "="*50)
    print("LUKHAS Component Usage Analysis Report")
    print("="*50)
    print(json.dumps(report, indent=2))
    
    return report


if __name__ == "__main__":
    main()