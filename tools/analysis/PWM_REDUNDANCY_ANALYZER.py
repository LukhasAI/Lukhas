#!/usr/bin/env python3
"""
PWM Redundancy Analyzer
======================
Identifies and analyzes redundant code across the LUKHAS PWM codebase.
"""

import os
import ast
import hashlib
import difflib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CodeDuplication:
    """Represents duplicated code between files"""
    file1: str
    file2: str
    function1: str
    function2: str
    similarity: float
    lines1: Tuple[int, int]
    lines2: Tuple[int, int]
    code_hash: str


@dataclass
class RedundantImport:
    """Represents redundant import patterns"""
    import_statement: str
    files: List[str]
    count: int


@dataclass
class RedundantClass:
    """Represents similar or duplicate class definitions"""
    class_name: str
    files: List[str]
    methods: List[str]
    similarity_groups: List[List[str]]


class RedundancyAnalyzer:
    """Analyzes LUKHAS PWM codebase for redundancies"""
    
    def __init__(self):
        self.root_path = Path("/Users/agi_dev/Lukhas_PWM")
        self.functions_by_hash = defaultdict(list)
        self.classes_by_name = defaultdict(list)
        self.imports_by_statement = defaultdict(list)
        self.duplications = []
        self.redundant_patterns = []
        
    def analyze(self) -> Dict[str, Any]:
        """Run comprehensive redundancy analysis"""
        logger.info("🔍 Analyzing LUKHAS PWM for redundancies...\n")
        
        # Collect code elements
        self._collect_code_elements()
        
        # Find duplications
        self._find_function_duplications()
        self._find_class_redundancies()
        self._find_import_redundancies()
        self._find_pattern_redundancies()
        
        # Generate report
        report = self._generate_report()
        
        # Save report
        report_path = self.root_path / "docs" / "reports" / "PWM_REDUNDANCY_REPORT.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _collect_code_elements(self):
        """Collect all functions, classes, and imports"""
        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)
        
        logger.info(f"📂 Analyzing {total_files} Python files...")
        
        for i, py_file in enumerate(python_files):
            if i % 100 == 0:
                logger.info(f"   Processing file {i}/{total_files}...")
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                relative_path = py_file.relative_to(self.root_path)
                
                # Collect functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_code = ast.get_source_segment(content, node)
                        if func_code:
                            # Normalize code for comparison
                            normalized = self._normalize_code(func_code)
                            func_hash = hashlib.md5(normalized.encode()).hexdigest()
                            
                            self.functions_by_hash[func_hash].append({
                                'file': str(relative_path),
                                'name': node.name,
                                'lines': (node.lineno, node.end_lineno),
                                'code': func_code,
                                'normalized': normalized
                            })
                    
                    elif isinstance(node, ast.ClassDef):
                        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        self.classes_by_name[node.name].append({
                            'file': str(relative_path),
                            'methods': methods,
                            'lines': (node.lineno, node.end_lineno)
                        })
                    
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        import_stmt = ast.get_source_segment(content, node)
                        if import_stmt:
                            self.imports_by_statement[import_stmt].append(str(relative_path))
                            
            except Exception as e:
                logger.warning(f"   Error parsing {relative_path}: {e}")
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison by removing comments and whitespace variations"""
        lines = code.split('\n')
        normalized = []
        
        for line in lines:
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')]
            # Strip whitespace
            line = line.strip()
            if line:
                normalized.append(line)
        
        return '\n'.join(normalized)
    
    def _find_function_duplications(self):
        """Find duplicate or near-duplicate functions"""
        logger.info("\n🔎 Finding function duplications...")
        
        for func_hash, functions in self.functions_by_hash.items():
            if len(functions) > 1:
                # Exact duplicates
                for i in range(len(functions)):
                    for j in range(i + 1, len(functions)):
                        func1, func2 = functions[i], functions[j]
                        
                        self.duplications.append(CodeDuplication(
                            file1=func1['file'],
                            file2=func2['file'],
                            function1=func1['name'],
                            function2=func2['name'],
                            similarity=1.0,
                            lines1=func1['lines'],
                            lines2=func2['lines'],
                            code_hash=func_hash
                        ))
        
        # Find near-duplicates using similarity comparison
        all_functions = []
        for funcs in self.functions_by_hash.values():
            all_functions.extend(funcs)
        
        for i in range(len(all_functions)):
            for j in range(i + 1, len(all_functions)):
                func1, func2 = all_functions[i], all_functions[j]
                
                # Skip if already identified as exact duplicate
                if func1['normalized'] == func2['normalized']:
                    continue
                
                # Calculate similarity
                similarity = difflib.SequenceMatcher(
                    None, 
                    func1['normalized'], 
                    func2['normalized']
                ).ratio()
                
                # Report high similarity (>80%)
                if similarity > 0.8:
                    self.duplications.append(CodeDuplication(
                        file1=func1['file'],
                        file2=func2['file'],
                        function1=func1['name'],
                        function2=func2['name'],
                        similarity=similarity,
                        lines1=func1['lines'],
                        lines2=func2['lines'],
                        code_hash=f"similar_{similarity:.2f}"
                    ))
    
    def _find_class_redundancies(self):
        """Find redundant class definitions"""
        logger.info("🔎 Finding class redundancies...")
        
        for class_name, occurrences in self.classes_by_name.items():
            if len(occurrences) > 1:
                # Group by similar method sets
                method_groups = defaultdict(list)
                for occ in occurrences:
                    method_key = ','.join(sorted(occ['methods']))
                    method_groups[method_key].append(occ['file'])
                
                similarity_groups = [files for files in method_groups.values() if len(files) > 1]
                
                if similarity_groups:
                    self.redundant_patterns.append({
                        'type': 'duplicate_class',
                        'class_name': class_name,
                        'occurrences': [occ['file'] for occ in occurrences],
                        'similarity_groups': similarity_groups
                    })
    
    def _find_import_redundancies(self):
        """Find redundant import patterns"""
        logger.info("🔎 Finding import redundancies...")
        
        # Find imports used in many files (potential for centralization)
        for import_stmt, files in self.imports_by_statement.items():
            if len(files) > 5:  # Threshold for common import
                self.redundant_patterns.append({
                    'type': 'common_import',
                    'import': import_stmt,
                    'files': files,
                    'count': len(files)
                })
    
    def _find_pattern_redundancies(self):
        """Find common code patterns that could be abstracted"""
        logger.info("🔎 Finding pattern redundancies...")
        
        # Common patterns to look for
        patterns = {
            'logger_setup': r'logger\s*=\s*get_logger',
            'error_handling': r'try:.*except.*logger\.error',
            'config_loading': r'with\s+open.*json\.load',
            'async_wrapper': r'async\s+def.*await.*return',
        }
        
        pattern_occurrences = defaultdict(list)
        
        python_files = list(self.root_path.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                relative_path = py_file.relative_to(self.root_path)
                
                # Check each pattern
                for pattern_name, pattern in patterns.items():
                    import re
                    if re.search(pattern, content):
                        pattern_occurrences[pattern_name].append(str(relative_path))
                        
            except Exception:
                pass
        
        # Report patterns that occur frequently
        for pattern_name, files in pattern_occurrences.items():
            if len(files) > 10:
                self.redundant_patterns.append({
                    'type': 'common_pattern',
                    'pattern': pattern_name,
                    'files': files[:20],  # Limit to first 20
                    'total_count': len(files)
                })
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive redundancy report"""
        logger.info("\n📊 Generating redundancy report...")
        
        # Sort duplications by similarity
        self.duplications.sort(key=lambda x: x.similarity, reverse=True)
        
        # Calculate statistics
        total_duplications = len(self.duplications)
        exact_duplicates = sum(1 for d in self.duplications if d.similarity == 1.0)
        near_duplicates = total_duplications - exact_duplicates
        
        # Estimate code savings
        total_duplicate_lines = sum(
            d.lines1[1] - d.lines1[0] 
            for d in self.duplications 
            if d.similarity > 0.9
        )
        
        report = {
            'summary': {
                'total_files_analyzed': len(list(self.root_path.rglob("*.py"))),
                'total_duplications': total_duplications,
                'exact_duplicates': exact_duplicates,
                'near_duplicates': near_duplicates,
                'estimated_duplicate_lines': total_duplicate_lines,
                'common_imports': len([p for p in self.redundant_patterns if p['type'] == 'common_import']),
                'duplicate_classes': len([p for p in self.redundant_patterns if p['type'] == 'duplicate_class']),
                'common_patterns': len([p for p in self.redundant_patterns if p['type'] == 'common_pattern'])
            },
            'duplications': [
                {
                    'file1': d.file1,
                    'file2': d.file2,
                    'function1': d.function1,
                    'function2': d.function2,
                    'similarity': d.similarity,
                    'lines': {
                        'file1': d.lines1,
                        'file2': d.lines2
                    }
                }
                for d in self.duplications[:50]  # Top 50 duplications
            ],
            'redundant_patterns': self.redundant_patterns,
            'recommendations': self._generate_recommendations()
        }
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Recommendation for exact duplicates
        exact_dups = [d for d in self.duplications if d.similarity == 1.0]
        if exact_dups:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'remove_exact_duplicates',
                'description': f"Remove {len(exact_dups)} exact duplicate functions",
                'impact': f"Reduce codebase by ~{len(exact_dups) * 20} lines",
                'examples': [
                    f"{d.function1} in {d.file1} and {d.function2} in {d.file2}"
                    for d in exact_dups[:3]
                ]
            })
        
        # Recommendation for common imports
        common_imports = [p for p in self.redundant_patterns if p['type'] == 'common_import' and p['count'] > 10]
        if common_imports:
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'centralize_imports',
                'description': "Create common import modules for frequently used imports",
                'impact': f"Reduce import redundancy in {sum(p['count'] for p in common_imports)} files",
                'examples': [p['import'] for p in common_imports[:3]]
            })
        
        # Recommendation for duplicate classes
        dup_classes = [p for p in self.redundant_patterns if p['type'] == 'duplicate_class']
        if dup_classes:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'consolidate_classes',
                'description': f"Consolidate {len(dup_classes)} duplicate class definitions",
                'impact': "Improve maintainability and reduce confusion",
                'examples': [
                    f"{p['class_name']} appears in {len(p['occurrences'])} files"
                    for p in dup_classes[:3]
                ]
            })
        
        # Recommendation for common patterns
        common_patterns = [p for p in self.redundant_patterns if p['type'] == 'common_pattern']
        if common_patterns:
            recommendations.append({
                'priority': 'LOW',
                'type': 'abstract_patterns',
                'description': "Create utility functions for common code patterns",
                'impact': "Improve consistency and reduce boilerplate",
                'patterns': [
                    f"{p['pattern']}: {p['total_count']} occurrences"
                    for p in common_patterns
                ]
            })
        
        return recommendations
    
    def _print_summary(self, report: Dict[str, Any]):
        """Print analysis summary"""
        summary = report['summary']
        
        print("\n" + "="*80)
        print("📊 REDUNDANCY ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n📈 Statistics:")
        print(f"   Total files analyzed: {summary['total_files_analyzed']}")
        print(f"   Exact duplicate functions: {summary['exact_duplicates']}")
        print(f"   Near-duplicate functions: {summary['near_duplicates']}")
        print(f"   Estimated duplicate lines: {summary['estimated_duplicate_lines']:,}")
        print(f"   Common imports (>5 files): {summary['common_imports']}")
        print(f"   Duplicate classes: {summary['duplicate_classes']}")
        print(f"   Common patterns: {summary['common_patterns']}")
        
        if report['duplications']:
            print(f"\n🔥 Top Duplications:")
            for dup in report['duplications'][:5]:
                print(f"   {dup['similarity']:.0%} similarity: {dup['function1']} ({dup['file1']}) ↔ {dup['function2']} ({dup['file2']})")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"\n   [{rec['priority']}] {rec['description']}")
                print(f"   Impact: {rec['impact']}")
                if 'examples' in rec:
                    print(f"   Examples:")
                    for ex in rec['examples'][:2]:
                        print(f"      - {ex}")
        
        print(f"\n📁 Full report saved to: docs/reports/PWM_REDUNDANCY_REPORT.json")
        print("="*80)


def main():
    """Run redundancy analysis"""
    analyzer = RedundancyAnalyzer()
    analyzer.analyze()


if __name__ == "__main__":
    main()