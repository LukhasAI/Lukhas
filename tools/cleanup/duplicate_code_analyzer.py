#!/usr/bin/env python3
"""
Duplicate Code Analyzer for LUKHAS PWM
=======================================
Identifies duplicate and conflicting code patterns for cleanup.
"""

import ast
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DuplicateCodeAnalyzer:
    """Analyzes codebase for duplicates and conflicts"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.duplicates = defaultdict(list)
        self.function_signatures = defaultdict(list)
        self.class_definitions = defaultdict(list)
        self.similar_files = []
        self.conflicting_imports = defaultdict(list)
        
    def analyze(self) -> Dict:
        """Run complete duplicate analysis"""
        print("🔍 Analyzing codebase for duplicates...")
        
        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)
        
        print(f"📁 Found {total_files} Python files")
        
        for i, file_path in enumerate(python_files):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{total_files} files...")
            
            # Skip certain directories
            if any(skip in str(file_path) for skip in [
                "__pycache__", ".git", ".venv", "venv", 
                ".pwm_cleanup_archive", "archive"
            ]):
                continue
                
            self._analyze_file(file_path)
        
        return self._generate_report()
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single file for duplicates"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Analyze functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._analyze_function(node, file_path)
                elif isinstance(node, ast.ClassDef):
                    self._analyze_class(node, file_path)
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    self._analyze_import(node, file_path)
                    
        except Exception:
            pass
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path):
        """Analyze function for duplicates"""
        # Create signature
        params = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(params)})"
        
        # Store by signature
        self.function_signatures[signature].append({
            'file': str(file_path.relative_to(self.root_path)),
            'line': node.lineno,
            'name': node.name,
            'params': params,
            'body_hash': self._hash_node(node)
        })
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path):
        """Analyze class for duplicates"""
        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        self.class_definitions[node.name].append({
            'file': str(file_path.relative_to(self.root_path)),
            'line': node.lineno,
            'methods': methods,
            'bases': [self._get_name(base) for base in node.bases]
        })
    
    def _analyze_import(self, node, file_path: Path):
        """Analyze imports for conflicts"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                self.conflicting_imports[module].append({
                    'file': str(file_path.relative_to(self.root_path)),
                    'line': node.lineno,
                    'as': alias.asname
                })
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    import_str = f"{node.module}.{alias.name}"
                    self.conflicting_imports[import_str].append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': node.lineno,
                        'from': node.module,
                        'import': alias.name,
                        'as': alias.asname
                    })
    
    def _hash_node(self, node) -> str:
        """Create hash of AST node"""
        try:
            # Simple hash based on AST dump
            dump = ast.dump(node)
            return hashlib.md5(dump.encode()).hexdigest()[:8]
        except:
            return "unknown"
    
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"
    
    def _generate_report(self) -> Dict:
        """Generate duplicate analysis report"""
        report = {
            'summary': {},
            'duplicate_functions': [],
            'duplicate_classes': [],
            'conflicting_imports': [],
            'recommendations': []
        }
        
        # Find duplicate functions
        duplicate_count = 0
        for signature, locations in self.function_signatures.items():
            if len(locations) > 1:
                # Check if actually duplicate (same body hash)
                hash_groups = defaultdict(list)
                for loc in locations:
                    hash_groups[loc['body_hash']].append(loc)
                
                for body_hash, group in hash_groups.items():
                    if len(group) > 1:
                        duplicate_count += len(group) - 1
                        report['duplicate_functions'].append({
                            'signature': signature,
                            'locations': [
                                f"{g['file']}:{g['line']}" for g in group
                            ],
                            'count': len(group)
                        })
        
        # Find duplicate classes
        for class_name, locations in self.class_definitions.items():
            if len(locations) > 1:
                report['duplicate_classes'].append({
                    'class': class_name,
                    'locations': [
                        {
                            'file': loc['file'],
                            'line': loc['line'],
                            'methods': loc['methods']
                        } for loc in locations
                    ],
                    'count': len(locations)
                })
        
        # Find problematic imports
        for module, imports in self.conflicting_imports.items():
            if len(imports) > 5:  # Same module imported in many places
                report['conflicting_imports'].append({
                    'module': module,
                    'import_count': len(imports),
                    'files': list(set(imp['file'] for imp in imports))[:10]
                })
        
        # Summary
        report['summary'] = {
            'total_duplicate_functions': duplicate_count,
            'total_duplicate_classes': len(report['duplicate_classes']),
            'heavily_imported_modules': len(report['conflicting_imports']),
            'estimated_lines_saveable': duplicate_count * 10  # Rough estimate
        }
        
        # Recommendations
        if duplicate_count > 0:
            report['recommendations'].append(
                f"Found {duplicate_count} duplicate functions. Consider creating shared utilities."
            )
        
        if report['duplicate_classes']:
            report['recommendations'].append(
                f"Found {len(report['duplicate_classes'])} duplicate class definitions. Consider consolidation."
            )
            
        if report['conflicting_imports']:
            report['recommendations'].append(
                "Some modules are imported excessively. Consider creating facade modules."
            )
        
        return report


def main():
    """Run duplicate analysis and generate report"""
    analyzer = DuplicateCodeAnalyzer()
    report = analyzer.analyze()
    
    print("\n" + "="*60)
    print("📊 DUPLICATE CODE ANALYSIS REPORT")
    print("="*60)
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"  Duplicate functions: {report['summary']['total_duplicate_functions']}")
    print(f"  Duplicate classes: {report['summary']['total_duplicate_classes']}")
    print(f"  Heavily imported modules: {report['summary']['heavily_imported_modules']}")
    print(f"  Estimated lines saveable: ~{report['summary']['estimated_lines_saveable']}")
    
    # Top duplicates
    if report['duplicate_functions']:
        print(f"\n🔄 Top Duplicate Functions:")
        for dup in report['duplicate_functions'][:10]:
            print(f"  • {dup['signature']}: {dup['count']} copies")
            for loc in dup['locations'][:3]:
                print(f"    - {loc}")
    
    if report['duplicate_classes']:
        print(f"\n🔄 Duplicate Classes:")
        for dup in report['duplicate_classes'][:10]:
            print(f"  • {dup['class']}: {dup['count']} definitions")
            for loc in dup['locations'][:3]:
                print(f"    - {loc['file']}:{loc['line']}")
    
    # Recommendations
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    # Save detailed report
    import json
    report_path = Path("docs/reports/analysis/DUPLICATE_CODE_REPORT.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Generate cleanup script
    if report['duplicate_functions']:
        generate_cleanup_script(report)


def generate_cleanup_script(report: Dict):
    """Generate a cleanup script for duplicates"""
    script = """#!/usr/bin/env python3
\"\"\"
Auto-generated cleanup script for duplicate code
\"\"\"

import os
import shutil
from pathlib import Path

def cleanup_duplicates():
    \"\"\"Remove or consolidate duplicate code\"\"\"
    
    # Duplicate functions to consolidate
    duplicates = {
"""
    
    for dup in report['duplicate_functions'][:20]:
        script += f"        '{dup['signature']}': {dup['locations']},\n"
    
    script += """    }
    
    print("🧹 Cleaning up duplicates...")
    
    # TODO: Implement actual consolidation logic
    # For now, just report what would be cleaned
    
    for signature, locations in duplicates.items():
        print(f"  Would consolidate {signature} from {len(locations)} locations")
    
    print("\\n✅ Cleanup analysis complete!")
    print("⚠️  Manual review required before actual deletion")

if __name__ == "__main__":
    cleanup_duplicates()
"""
    
    script_path = Path("tools/cleanup/cleanup_duplicates.py")
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script)
    
    os.chmod(script_path, 0o755)
    print(f"\n🔧 Cleanup script generated: {script_path}")


if __name__ == "__main__":
    main()