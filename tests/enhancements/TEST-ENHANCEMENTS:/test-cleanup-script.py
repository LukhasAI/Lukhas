#!/usr/bin/env python3
"""
AGI Test Suite Cleanup and Organization Script
Identifies obsolete tests, maps coverage, and reorganizes test structure
"""

import os
import ast
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import importlib.util

class TestAuditor:
    """Comprehensive test suite auditor and organizer"""
    
    def __init__(self, project_root: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas"):
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.src_dirs = self._identify_source_dirs()
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "obsolete_tests": [],
            "untested_functions": [],
            "test_coverage": {},
            "reorganization_plan": {},
            "statistics": {}
        }
    
    def _identify_source_dirs(self) -> List[Path]:
        """Identify all source code directories"""
        src_dirs = []
        exclude_dirs = {'.git', '.venv', '__pycache__', 'tests', 'docs', 'scripts'}
        
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                if any(p.suffix == '.py' for p in item.rglob('*.py')):
                    src_dirs.append(item)
        
        return src_dirs
    
    def find_obsolete_tests(self) -> List[Dict]:
        """Identify obsolete and stub tests"""
        obsolete = []
        
        # Patterns indicating obsolete tests
        obsolete_patterns = [
            'STUB_',
            'test_STUB',
            '_old',
            '_deprecated',
            '_backup',
            'test_dummy',
            'test_example'
        ]
        
        for test_file in self.tests_dir.rglob('test_*.py'):
            # Check filename patterns
            if any(pattern in test_file.name for pattern in obsolete_patterns):
                obsolete.append({
                    "file": str(test_file.relative_to(self.project_root)),
                    "reason": "Obsolete naming pattern",
                    "recommendation": "Remove or update"
                })
                continue
            
            # Check file content
            try:
                content = test_file.read_text()
                
                # Check for empty or minimal tests
                tree = ast.parse(content)
                test_functions = [
                    node for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
                ]
                
                if len(test_functions) == 0:
                    obsolete.append({
                        "file": str(test_file.relative_to(self.project_root)),
                        "reason": "No test functions found",
                        "recommendation": "Remove empty test file"
                    })
                elif all('pass' in ast.unparse(func) or 'NotImplemented' in ast.unparse(func) 
                        for func in test_functions):
                    obsolete.append({
                        "file": str(test_file.relative_to(self.project_root)),
                        "reason": "All tests are stubs",
                        "recommendation": "Implement or remove"
                    })
                
                # Check for outdated imports
                imports = [
                    node for node in ast.walk(tree)
                    if isinstance(node, (ast.Import, ast.ImportFrom))
                ]
                
                for imp in imports:
                    if isinstance(imp, ast.ImportFrom):
                        module = imp.module or ''
                        if any(old in module for old in ['old', 'legacy', 'deprecated']):
                            obsolete.append({
                                "file": str(test_file.relative_to(self.project_root)),
                                "reason": f"Imports deprecated module: {module}",
                                "recommendation": "Update imports"
                            })
                            break
                            
            except Exception as e:
                print(f"Error analyzing {test_file}: {e}")
        
        self.audit_results["obsolete_tests"] = obsolete
        return obsolete
    
    def map_test_coverage(self) -> Dict[str, Dict]:
        """Map which functions have tests and which don't"""
        coverage_map = {}
        
        # First, collect all functions from source code
        all_functions = self._collect_all_functions()
        
        # Then, collect all tested functions
        tested_functions = self._collect_tested_functions()
        
        # Calculate coverage
        for module, functions in all_functions.items():
            coverage_map[module] = {
                "total_functions": len(functions),
                "tested_functions": len(functions & tested_functions.get(module, set())),
                "untested_functions": list(functions - tested_functions.get(module, set())),
                "coverage_percentage": 0
            }
            
            if coverage_map[module]["total_functions"] > 0:
                coverage_map[module]["coverage_percentage"] = (
                    coverage_map[module]["tested_functions"] / 
                    coverage_map[module]["total_functions"] * 100
                )
        
        self.audit_results["test_coverage"] = coverage_map
        
        # Identify top untested functions
        untested = []
        for module, data in coverage_map.items():
            for func in data["untested_functions"][:5]:  # Top 5 per module
                untested.append({
                    "module": module,
                    "function": func,
                    "priority": self._calculate_priority(module, func)
                })
        
        self.audit_results["untested_functions"] = sorted(
            untested, 
            key=lambda x: x["priority"], 
            reverse=True
        )[:20]  # Top 20 overall
        
        return coverage_map
    
    def _collect_all_functions(self) -> Dict[str, Set[str]]:
        """Collect all functions from source code"""
        functions = {}
        
        for src_dir in self.src_dirs:
            for py_file in src_dir.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                    
                module_name = str(py_file.relative_to(self.project_root).with_suffix(''))
                module_name = module_name.replace('/', '.')
                
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    module_functions = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if not node.name.startswith('_'):  # Skip private functions
                                module_functions.add(node.name)
                        elif isinstance(node, ast.ClassDef):
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    if not item.name.startswith('_'):
                                        module_functions.add(f"{node.name}.{item.name}")
                    
                    if module_functions:
                        functions[module_name] = module_functions
                        
                except Exception as e:
                    print(f"Error parsing {py_file}: {e}")
        
        return functions
    
    def _collect_tested_functions(self) -> Dict[str, Set[str]]:
        """Collect all functions that have tests"""
        tested = {}
        
        for test_file in self.tests_dir.rglob('test_*.py'):
            try:
                content = test_file.read_text()
                tree = ast.parse(content)
                
                # Extract imports to understand what's being tested
                imports = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports[node.module] = [
                                alias.name for alias in node.names
                            ]
                
                # Extract test functions and map to source functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        # Try to infer what function is being tested
                        tested_func = node.name.replace('test_', '')
                        
                        # Map to appropriate module
                        for module in imports:
                            if module not in tested:
                                tested[module] = set()
                            tested[module].add(tested_func)
                            
            except Exception as e:
                print(f"Error analyzing test file {test_file}: {e}")
        
        return tested
    
    def _calculate_priority(self, module: str, function: str) -> int:
        """Calculate priority for testing a function"""
        priority = 0
        
        # Core modules get higher priority
        core_modules = ['core', 'consciousness', 'quantum', 'bio', 'governance', 'identity']
        for core in core_modules:
            if core in module:
                priority += 10
        
        # Public API functions get higher priority
        if not function.startswith('_'):
            priority += 5
        
        # Main entry points get highest priority
        if function in ['__init__', 'main', 'run', 'execute', 'process']:
            priority += 15
        
        return priority
    
    def create_reorganization_plan(self) -> Dict:
        """Create a plan to reorganize tests"""
        plan = {
            "moves": [],
            "creates": [],
            "deletes": []
        }
        
        # Plan deletion of obsolete tests
        for obsolete in self.audit_results["obsolete_tests"]:
            plan["deletes"].append(obsolete["file"])
        
        # Plan creation of new test directories
        new_structure = [
            "tests/unit/core",
            "tests/unit/consciousness",
            "tests/unit/quantum",
            "tests/unit/bio",
            "tests/integration/api",
            "tests/integration/workflow",
            "tests/performance/load",
            "tests/performance/memory",
            "tests/security/auth",
            "tests/e2e/user_flows"
        ]
        
        for dir_path in new_structure:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                plan["creates"].append(str(dir_path))
        
        # Plan moves for existing tests
        test_categories = {
            "unit": ["test_adapters", "test_glyph_system", "test_math_formula"],
            "integration": ["test_integration", "test_colony_integration", "test_openai_connection"],
            "performance": ["STRESS_TEST", "test_performance"],
            "security": ["test_enhanced_security", "test_red_team"],
            "e2e": ["test_e2e_workflows", "test_full_system_flow"]
        }
        
        for test_file in self.tests_dir.rglob('test_*.py'):
            filename = test_file.name
            
            for category, patterns in test_categories.items():
                if any(pattern in filename for pattern in patterns):
                    new_location = f"tests/{category}/{filename}"
                    if str(test_file.relative_to(self.project_root)) != new_location:
                        plan["moves"].append({
                            "from": str(test_file.relative_to(self.project_root)),
                            "to": new_location
                        })
                    break
        
        self.audit_results["reorganization_plan"] = plan
        return plan
    
    def generate_statistics(self) -> Dict:
        """Generate overall statistics"""
        stats = {
            "total_test_files": len(list(self.tests_dir.rglob('test_*.py'))),
            "obsolete_tests": len(self.audit_results["obsolete_tests"]),
            "total_source_modules": len(self.audit_results["test_coverage"]),
            "average_coverage": 0,
            "fully_tested_modules": 0,
            "untested_modules": 0
        }
        
        if self.audit_results["test_coverage"]:
            coverages = [
                data["coverage_percentage"] 
                for data in self.audit_results["test_coverage"].values()
            ]
            stats["average_coverage"] = sum(coverages) / len(coverages)
            stats["fully_tested_modules"] = sum(1 for c in coverages if c == 100)
            stats["untested_modules"] = sum(1 for c in coverages if c == 0)
        
        self.audit_results["statistics"] = stats
        return stats
    
    def save_audit_report(self, output_file: str = "test_audit_report.json"):
        """Save audit results to file"""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        print(f"Audit report saved to {output_path}")
    
    def execute_reorganization(self, dry_run: bool = True):
        """Execute the reorganization plan"""
        plan = self.audit_results.get("reorganization_plan", {})
        
        if dry_run:
            print("DRY RUN - No changes will be made")
            print("-" * 50)
        
        # Create new directories
        for dir_path in plan.get("creates", []):
            full_path = self.project_root / dir_path
            if dry_run:
                print(f"Would create: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                (full_path / "__init__.py").touch()
                print(f"Created: {dir_path}")
        
        # Move files
        for move in plan.get("moves", []):
            src = self.project_root / move["from"]
            dst = self.project_root / move["to"]
            if dry_run:
                print(f"Would move: {move['from']} -> {move['to']}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print(f"Moved: {move['from']} -> {move['to']}")
        
        # Delete obsolete files
        for file_path in plan.get("deletes", []):
            full_path = self.project_root / file_path
            if dry_run:
                print(f"Would delete: {file_path}")
            else:
                if full_path.exists():
                    full_path.unlink()
                    print(f"Deleted: {file_path}")
    
    def print_summary(self):
        """Print audit summary"""
        stats = self.audit_results["statistics"]
        
        print("\n" + "=" * 60)
        print("TEST AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Test Files: {stats['total_test_files']}")
        print(f"Obsolete Tests: {stats['obsolete_tests']}")
        print(f"Average Coverage: {stats['average_coverage']:.1f}%")
        print(f"Fully Tested Modules: {stats['fully_tested_modules']}")
        print(f"Untested Modules: {stats['untested_modules']}")
        
        print("\n" + "-" * 60)
        print("TOP PRIORITY UNTESTED FUNCTIONS:")
        print("-" * 60)
        for func in self.audit_results["untested_functions"][:10]:
            print(f"  {func['module']}.{func['function']} (Priority: {func['priority']})")
        
        print("\n" + "-" * 60)
        print("OBSOLETE TESTS TO REMOVE:")
        print("-" * 60)
        for test in self.audit_results["obsolete_tests"][:10]:
            print(f"  {test['file']}")
            print(f"    Reason: {test['reason']}")


def main():
    """Main execution"""
    auditor = TestAuditor()
    
    print("Starting test audit...")
    
    # Run audit
    auditor.find_obsolete_tests()
    auditor.map_test_coverage()
    auditor.create_reorganization_plan()
    auditor.generate_statistics()
    
    # Print summary
    auditor.print_summary()
    
    # Save report
    auditor.save_audit_report()
    
    # Ask about reorganization
    response = input("\nExecute reorganization? (dry-run/execute/skip): ").lower()
    if response == "dry-run":
        auditor.execute_reorganization(dry_run=True)
    elif response == "execute":
        confirm = input("This will move/delete files. Are you sure? (yes/no): ").lower()
        if confirm == "yes":
            auditor.execute_reorganization(dry_run=False)
    
    print("\nAudit complete!")


if __name__ == "__main__":
    main()