#!/usr/bin/env python3
"""
Static Analysis and Metrics Computation for LUKHAS Repository Audit

Computes:
- Cyclomatic complexity per function (using simple heuristics)
- Lines of code (LOC) metrics
- Docstring coverage
- Type annotation coverage
- Code quality indicators

Output: reports/analysis/static_metrics.json
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
import sys


class StaticAnalyzer:
    """Performs static analysis on Python files"""

    def __init__(self, file_index_path: str):
        """Initialize with file index"""
        with open(file_index_path, 'r') as f:
            self.file_index = json.load(f)

        self.metrics = {
            'repository_metrics': {
                'total_files': 0,
                'total_loc': 0,
                'total_sloc': 0,  # Source lines (non-blank, non-comment)
                'total_functions': 0,
                'total_classes': 0,
                'avg_complexity': 0.0,
                'docstring_coverage': 0.0,
                'type_annotation_coverage': 0.0,
            },
            'files': []
        }

    def calculate_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate cyclomatic complexity using simple heuristics"""
        complexity_indicators = {
            'if_statements': len(re.findall(r'\bif\b', content)),
            'for_loops': len(re.findall(r'\bfor\b', content)),
            'while_loops': len(re.findall(r'\bwhile\b', content)),
            'try_blocks': len(re.findall(r'\btry\b', content)),
            'except_blocks': len(re.findall(r'\bexcept\b', content)),
            'with_statements': len(re.findall(r'\bwith\b', content)),
            'boolean_operators': len(re.findall(r'\b(and|or)\b', content)),
            'lambda_functions': len(re.findall(r'\blambda\b', content)),
        }

        # Estimate complexity (McCabe complexity approximation)
        estimated_complexity = 1 + sum([
            complexity_indicators['if_statements'],
            complexity_indicators['for_loops'],
            complexity_indicators['while_loops'],
            complexity_indicators['except_blocks'],
            complexity_indicators['boolean_operators'] // 2,  # Each pair adds 1
        ])

        return {
            'estimated_complexity': estimated_complexity,
            'indicators': complexity_indicators
        }

    def count_type_annotations(self, content: str) -> Dict[str, Any]:
        """Count type annotations in code"""
        try:
            tree = ast.parse(content)

            total_functions = 0
            annotated_functions = 0
            total_params = 0
            annotated_params = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1

                    # Check return annotation
                    if node.returns is not None:
                        annotated_functions += 1

                    # Check parameter annotations
                    for arg in node.args.args:
                        total_params += 1
                        if arg.annotation is not None:
                            annotated_params += 1

            return {
                'total_functions': total_functions,
                'annotated_functions': annotated_functions,
                'total_params': total_params,
                'annotated_params': annotated_params,
                'function_annotation_rate': annotated_functions / total_functions if total_functions > 0 else 0.0,
                'param_annotation_rate': annotated_params / total_params if total_params > 0 else 0.0,
            }

        except Exception:
            return {
                'total_functions': 0,
                'annotated_functions': 0,
                'total_params': 0,
                'annotated_params': 0,
                'function_annotation_rate': 0.0,
                'param_annotation_rate': 0.0,
            }

    def count_code_lines(self, content: str) -> Dict[str, int]:
        """Count different types of lines"""
        lines = content.split('\n')

        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))

        # Source lines (non-blank, non-comment)
        sloc = total_lines - blank_lines - comment_lines

        return {
            'total_lines': total_lines,
            'blank_lines': blank_lines,
            'comment_lines': comment_lines,
            'source_lines': sloc,
            'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0.0,
        }

    def analyze_file(self, file_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single file"""
        try:
            file_path = Path(file_entry['absolute_path'])

            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Calculate metrics
            complexity = self.calculate_complexity(content)
            type_annotations = self.count_type_annotations(content)
            line_counts = self.count_code_lines(content)

            # Extract complexity indicators from file index
            file_complexity = file_entry.get('complexity', {})

            return {
                'path': file_entry['path'],
                'module_path': file_entry['module_path'],
                'lines': line_counts,
                'complexity': {
                    **complexity,
                    'num_classes': file_complexity.get('num_classes', 0),
                    'num_functions': file_complexity.get('num_functions', 0),
                },
                'type_annotations': type_annotations,
                'docstring_metrics': {
                    'has_module_docstring': file_entry.get('has_module_docstring', False),
                    'num_exports': len(file_entry.get('exports', [])),
                    'exports_with_docstrings': sum(
                        1 for exp in file_entry.get('exports', [])
                        if exp.get('has_docstring', False)
                    ),
                },
                'quality_score': self.calculate_quality_score(
                    file_entry, complexity, type_annotations, line_counts
                ),
            }

        except Exception as e:
            print(f"Error analyzing {file_entry['path']}: {e}", file=sys.stderr)
            return None

    def calculate_quality_score(
        self,
        file_entry: Dict[str, Any],
        complexity: Dict[str, Any],
        type_annotations: Dict[str, Any],
        line_counts: Dict[str, int]
    ) -> float:
        """Calculate a simple quality score (0-100)"""
        score = 100.0

        # Penalize for high complexity
        complexity_score = min(100, complexity['estimated_complexity'])
        score -= complexity_score * 0.1

        # Reward for type annotations
        score += type_annotations['function_annotation_rate'] * 10
        score += type_annotations['param_annotation_rate'] * 5

        # Reward for docstrings
        if file_entry.get('has_module_docstring'):
            score += 5

        num_exports = len(file_entry.get('exports', []))
        if num_exports > 0:
            docstring_rate = sum(
                1 for exp in file_entry.get('exports', [])
                if exp.get('has_docstring', False)
            ) / num_exports
            score += docstring_rate * 10

        # Reward for comments
        score += line_counts['comment_ratio'] * 10

        # Clamp to 0-100
        return max(0.0, min(100.0, score))

    def analyze_repository(self) -> Dict[str, Any]:
        """Analyze all files in repository"""
        print("Analyzing repository files...")

        total_complexity = 0
        total_functions = 0
        total_annotated_functions = 0
        total_files_with_docstrings = 0

        for i, file_entry in enumerate(self.file_index['files']):
            if i % 500 == 0:
                print(f"  Analyzed {i} files...", file=sys.stderr)

            analysis = self.analyze_file(file_entry)
            if analysis:
                self.metrics['files'].append(analysis)

                # Update repository metrics
                self.metrics['repository_metrics']['total_files'] += 1
                self.metrics['repository_metrics']['total_loc'] += analysis['lines']['total_lines']
                self.metrics['repository_metrics']['total_sloc'] += analysis['lines']['source_lines']

                complexity_val = analysis['complexity']['estimated_complexity']
                total_complexity += complexity_val

                num_functions = analysis['complexity']['num_functions']
                num_classes = analysis['complexity']['num_classes']
                self.metrics['repository_metrics']['total_functions'] += num_functions
                self.metrics['repository_metrics']['total_classes'] += num_classes

                total_functions += analysis['type_annotations']['total_functions']
                total_annotated_functions += analysis['type_annotations']['annotated_functions']

                if analysis['docstring_metrics']['has_module_docstring']:
                    total_files_with_docstrings += 1

        # Calculate averages
        total_files = self.metrics['repository_metrics']['total_files']
        if total_files > 0:
            self.metrics['repository_metrics']['avg_complexity'] = total_complexity / total_files
            self.metrics['repository_metrics']['docstring_coverage'] = (
                total_files_with_docstrings / total_files * 100
            )

        if total_functions > 0:
            self.metrics['repository_metrics']['type_annotation_coverage'] = (
                total_annotated_functions / total_functions * 100
            )

        print(f"\nAnalysis complete: {total_files} files analyzed")

        return self.metrics


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    file_index_path = repo_root / 'reports' / 'analysis' / 'file_index.json'
    output_file = repo_root / 'reports' / 'analysis' / 'static_metrics.json'

    # Analyze repository
    analyzer = StaticAnalyzer(str(file_index_path))
    metrics = analyzer.analyze_repository()

    # Write metrics to file
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nStatic metrics written to: {output_file}")
    print(f"Total files: {metrics['repository_metrics']['total_files']}")
    print(f"Total LOC: {metrics['repository_metrics']['total_loc']}")
    print(f"Total SLOC: {metrics['repository_metrics']['total_sloc']}")
    print(f"Avg complexity: {metrics['repository_metrics']['avg_complexity']:.2f}")
    print(f"Docstring coverage: {metrics['repository_metrics']['docstring_coverage']:.2f}%")
    print(f"Type annotation coverage: {metrics['repository_metrics']['type_annotation_coverage']:.2f}%")


if __name__ == '__main__':
    main()
