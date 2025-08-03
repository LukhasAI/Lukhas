#!/usr/bin/env python3
"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony


LUKHAS PWM Current Connectivity Analysis
Analyzes the current state of module connectivity and identifies isolated files
"""

import os
import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

class ConnectivityAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.module_imports = defaultdict(set)
        self.module_imported_by = defaultdict(set)
        self.file_metrics = {}
        self.isolated_files = []
        self.connected_components = []
        
    def analyze_directory(self) -> Dict[str, Any]:
        """Perform complete connectivity analysis"""
        print("🔍 Starting connectivity analysis...")
        
        # Collect all Python files
        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)
        print(f"📁 Found {total_files} Python files")
        
        # Analyze each file
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"  Processing file {i}/{total_files}...")
            self._analyze_file(file_path)
            
        # Identify connectivity
        self._analyze_connectivity()
        
        # Create report
        report = self._create_report()
        
        print("✅ Analysis complete!")
        return report
        
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        relative_path = file_path.relative_to(self.root_path)
        module_name = str(relative_path).replace('/', '.').replace('.py', '')
        
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'venv', 'env', '.pytest_cache', 'htmlcov', '.mypy_cache'}
        if any(skip_dir in str(relative_path) for skip_dir in skip_dirs):
            return
            
        metrics = {
            'path': str(relative_path),
            'module_name': module_name,
            'imports_out': set(),
            'imports_in': set(),
            'has_main': False,
            'has_class': False,
            'has_function': False,
            'is_init': file_path.name == '__init__.py',
            'lines_of_code': 0,
            'file_size': file_path.stat().st_size
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            metrics['lines_of_code'] = len(content.splitlines())
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metrics['imports_out'].add(alias.name)
                        self.module_imports[module_name].add(alias.name)
                        self.module_imported_by[alias.name].add(module_name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        base_module = node.module
                        # Handle relative imports
                        if node.level > 0:
                            parts = module_name.split('.')
                            if len(parts) > node.level:
                                parent_parts = parts[:-node.level]
                                if base_module:
                                    base_module = '.'.join(parent_parts) + '.' + base_module
                                else:
                                    base_module = '.'.join(parent_parts)
                        
                        metrics['imports_out'].add(base_module)
                        self.module_imports[module_name].add(base_module)
                        self.module_imported_by[base_module].add(module_name)
                        
                elif isinstance(node, ast.ClassDef):
                    metrics['has_class'] = True
                    
                elif isinstance(node, ast.FunctionDef):
                    metrics['has_function'] = True
                    if node.name == 'main':
                        metrics['has_main'] = True
                        
            # Check for if __name__ == "__main__"
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    if isinstance(node.test, ast.Compare):
                        if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                            metrics['has_main'] = True
                            
        except Exception as e:
            print(f"  ⚠️  Error analyzing {relative_path}: {e}")
            
        self.file_metrics[str(relative_path)] = metrics
        
    def _analyze_connectivity(self):
        """Analyze connectivity between modules"""
        all_modules = set(self.file_metrics.keys())
        
        # Build connectivity graph
        for file_path, metrics in self.file_metrics.items():
            module_name = metrics['module_name']
            
            # Count incoming imports
            metrics['imports_in'] = set()
            for other_module, imports in self.module_imports.items():
                if module_name in imports or file_path.replace('.py', '') in imports:
                    metrics['imports_in'].add(other_module)
                    
            # Calculate connectivity score
            imports_out_count = len(metrics['imports_out'])
            imports_in_count = len(metrics['imports_in'])
            metrics['connectivity_score'] = imports_out_count + imports_in_count
            
            # Check if isolated
            is_isolated = (
                imports_out_count == 0 and 
                imports_in_count == 0 and 
                not metrics['is_init'] and
                not metrics['has_main']
            )
            
            metrics['is_isolated'] = is_isolated
            if is_isolated:
                self.isolated_files.append(file_path)
                
    def _create_report(self) -> Dict[str, Any]:
        """Create comprehensive connectivity report"""
        # Sort files by connectivity
        sorted_files = sorted(
            self.file_metrics.items(),
            key=lambda x: x[1]['connectivity_score'],
            reverse=True
        )
        
        # Identify hubs (high connectivity)
        hubs = []
        for file_path, metrics in sorted_files[:50]:  # Top 50 connected files
            if metrics['connectivity_score'] > 10:
                hubs.append({
                    'file': file_path,
                    'module': metrics['module_name'],
                    'imports_out': len(metrics['imports_out']),
                    'imports_in': len(metrics['imports_in']),
                    'connectivity_score': metrics['connectivity_score'],
                    'lines_of_code': metrics['lines_of_code']
                })
                
        # Find truly isolated files (refined criteria)
        truly_isolated = []
        for file_path in self.isolated_files:
            metrics = self.file_metrics[file_path]
            # Additional checks for truly isolated files
            if (metrics['lines_of_code'] > 10 and  # Not empty
                not any(skip in file_path for skip in ['test', '__pycache__', 'example']) and
                metrics['file_size'] > 100):  # Not trivial
                truly_isolated.append({
                    'file': file_path,
                    'lines_of_code': metrics['lines_of_code'],
                    'has_class': metrics['has_class'],
                    'has_function': metrics['has_function'],
                    'file_size': metrics['file_size']
                })
                
        # Create report
        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'analysis_summary': {
                'total_python_files': len(self.file_metrics),
                'connected_files': len(self.file_metrics) - len(truly_isolated),
                'isolated_files': len(truly_isolated),
                'hub_files': len(hubs),
                'average_connectivity': sum(m['connectivity_score'] for m in self.file_metrics.values()) / len(self.file_metrics) if self.file_metrics else 0
            },
            'connectivity_metrics': {
                'highly_connected_threshold': 10,
                'isolated_threshold': 0,
                'average_imports_per_file': sum(len(m['imports_out']) for m in self.file_metrics.values()) / len(self.file_metrics) if self.file_metrics else 0
            },
            'critical_hubs': hubs[:20],  # Top 20 hubs
            'isolated_files': truly_isolated,
            'module_statistics': self._calculate_module_stats()
        }
        
        return report
        
    def _calculate_module_stats(self) -> Dict[str, Any]:
        """Calculate statistics per module"""
        module_stats = defaultdict(lambda: {
            'file_count': 0,
            'total_lines': 0,
            'connected_files': 0,
            'isolated_files': 0,
            'avg_connectivity': 0
        })
        
        for file_path, metrics in self.file_metrics.items():
            # Get top-level module
            parts = file_path.split('/')
            if len(parts) > 0:
                module = parts[0]
                stats = module_stats[module]
                stats['file_count'] += 1
                stats['total_lines'] += metrics['lines_of_code']
                if metrics['connectivity_score'] > 0:
                    stats['connected_files'] += 1
                if metrics['is_isolated']:
                    stats['isolated_files'] += 1
                    
        # Calculate averages
        for module, stats in module_stats.items():
            if stats['file_count'] > 0:
                total_connectivity = sum(
                    m['connectivity_score'] 
                    for f, m in self.file_metrics.items() 
                    if f.startswith(module + '/')
                )
                stats['avg_connectivity'] = total_connectivity / stats['file_count']
                
        return dict(module_stats)


def main():
    analyzer = ConnectivityAnalyzer()
    report = analyzer.analyze_directory()
    
    # Save report
    output_path = Path('docs/reports/analysis/PWM_CURRENT_CONNECTIVITY_ANALYSIS.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
        
    print(f"\n📊 Report saved to: {output_path}")
    
    # Print summary
    print("\n🔍 CONNECTIVITY SUMMARY:")
    print(f"   Total Python files: {report['analysis_summary']['total_python_files']}")
    print(f"   Connected files: {report['analysis_summary']['connected_files']}")
    print(f"   Isolated files: {report['analysis_summary']['isolated_files']}")
    print(f"   Critical hubs: {report['analysis_summary']['hub_files']}")
    print(f"   Average connectivity: {report['analysis_summary']['average_connectivity']:.2f}")
    
    if report['isolated_files']:
        print(f"\n⚠️  Found {len(report['isolated_files'])} isolated files:")
        for file_info in report['isolated_files'][:10]:  # Show first 10
            print(f"   - {file_info['file']} ({file_info['lines_of_code']} lines)")
            
    print("\n✅ Analysis complete!")
    

if __name__ == '__main__':
    main()