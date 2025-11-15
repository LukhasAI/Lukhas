#!/usr/bin/env python3
"""
Comprehensive File Index Builder for LUKHAS Repository Audit

Generates a complete index of all Python files with:
- File metadata (path, lines, size, last commit)
- AST analysis (exports, imports, docstrings)
- TODO comments and complexity indicators
- Module paths and public API surface

Output: reports/analysis/file_index.json
"""

import ast
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import sys


class FileIndexer:
    """Indexes Python files in the repository"""

    EXCLUDE_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
        'node_modules', '.tox', '.venv', 'venv', 'env', '.env',
        'manifests',  # Exclude manifests as requested
        'build', 'dist', '*.egg-info'
    }

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.index = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'files_with_docstrings': 0,
            'files_with_todos': 0,
            'total_exports': 0,
            'total_imports': 0,
        }

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded"""
        parts = path.parts
        return any(exclude_dir in parts for exclude_dir in self.EXCLUDE_DIRS)

    def get_git_info(self, file_path: Path) -> Optional[str]:
        """Get last commit hash for file"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H', '--', str(file_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or None
        except Exception:
            return None

    def get_module_path(self, file_path: Path) -> str:
        """Convert file path to Python module path"""
        try:
            rel_path = file_path.relative_to(self.repo_root)
            parts = list(rel_path.parts)

            # Remove .py extension from last part
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]

            # Remove __init__ from path
            if parts[-1] == '__init__':
                parts = parts[:-1]

            return '.'.join(parts) if parts else str(rel_path)
        except ValueError:
            return str(file_path)

    def extract_shebang(self, content: str) -> Optional[str]:
        """Extract shebang line if present"""
        first_line = content.split('\n')[0] if content else ''
        if first_line.startswith('#!'):
            return first_line
        return None

    def count_todos(self, content: str) -> List[Dict[str, Any]]:
        """Extract TODO comments with line numbers"""
        todos = []
        for i, line in enumerate(content.split('\n'), 1):
            # Match TODO, FIXME, XXX, HACK, NOTE patterns
            if re.search(r'#\s*(TODO|FIXME|XXX|HACK|NOTE)', line, re.IGNORECASE):
                todos.append({
                    'line': i,
                    'text': line.strip(),
                    'type': re.search(r'(TODO|FIXME|XXX|HACK|NOTE)', line, re.IGNORECASE).group(1)
                })
        return todos

    def analyze_ast(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Python AST to extract exports, imports, docstrings"""
        result = {
            'exports': [],
            'imports': [],
            'has_module_docstring': False,
            'classes': [],
            'functions': [],
            'complexity_indicators': {
                'num_classes': 0,
                'num_functions': 0,
                'num_imports': 0,
                'max_nesting_depth': 0,
            }
        }

        try:
            tree = ast.parse(content, filename=str(file_path))

            # Check for module docstring
            if (ast.get_docstring(tree) is not None):
                result['has_module_docstring'] = True

            # Track nesting depth
            max_depth = 0

            for node in ast.walk(tree):
                # Track classes
                if isinstance(node, ast.ClassDef):
                    result['classes'].append(node.name)
                    result['complexity_indicators']['num_classes'] += 1

                    # Check if it's exported (doesn't start with _)
                    if not node.name.startswith('_'):
                        result['exports'].append({
                            'name': node.name,
                            'type': 'class',
                            'lineno': node.lineno,
                            'has_docstring': ast.get_docstring(node) is not None
                        })

                # Track functions
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    result['functions'].append(node.name)
                    result['complexity_indicators']['num_functions'] += 1

                    # Only top-level functions are exports
                    if not node.name.startswith('_') and node.col_offset == 0:
                        result['exports'].append({
                            'name': node.name,
                            'type': 'async_function' if isinstance(node, ast.AsyncFunctionDef) else 'function',
                            'lineno': node.lineno,
                            'has_docstring': ast.get_docstring(node) is not None
                        })

                # Track imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append({
                            'module': alias.name,
                            'name': alias.asname or alias.name,
                            'lineno': node.lineno
                        })
                        result['complexity_indicators']['num_imports'] += 1

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        result['imports'].append({
                            'module': module,
                            'name': alias.name,
                            'as': alias.asname,
                            'lineno': node.lineno
                        })
                        result['complexity_indicators']['num_imports'] += 1

            # Limit imports to top 20 by line number
            result['imports'] = sorted(result['imports'], key=lambda x: x['lineno'])[:20]

        except SyntaxError as e:
            result['parse_error'] = f"SyntaxError: {str(e)}"
        except Exception as e:
            result['parse_error'] = f"Error: {str(e)}"

        return result

    def index_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Index a single Python file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.split('\n')
            num_lines = len(lines)

            # Extract information
            shebang = self.extract_shebang(content)
            todos = self.count_todos(content)
            ast_info = self.analyze_ast(content, file_path)

            # Get git info
            last_commit = self.get_git_info(file_path)

            # Build index entry
            entry = {
                'path': str(file_path.relative_to(self.repo_root)),
                'absolute_path': str(file_path),
                'module_path': self.get_module_path(file_path),
                'size_bytes': file_path.stat().st_size,
                'lines': num_lines,
                'last_commit': last_commit,
                'shebang': shebang,
                'has_module_docstring': ast_info['has_module_docstring'],
                'exports': ast_info['exports'],
                'imports': ast_info['imports'],
                'todos': todos,
                'complexity': ast_info['complexity_indicators'],
                'parse_error': ast_info.get('parse_error'),
            }

            # Update stats
            self.stats['total_files'] += 1
            self.stats['total_lines'] += num_lines
            if ast_info['has_module_docstring']:
                self.stats['files_with_docstrings'] += 1
            if todos:
                self.stats['files_with_todos'] += 1
            self.stats['total_exports'] += len(ast_info['exports'])
            self.stats['total_imports'] += len(ast_info['imports'])

            return entry

        except Exception as e:
            print(f"Error indexing {file_path}: {e}", file=sys.stderr)
            return None

    def build_index(self) -> Dict[str, Any]:
        """Build complete file index"""
        print(f"Indexing Python files in {self.repo_root}...")

        # Find all Python files
        for py_file in self.repo_root.rglob('*.py'):
            if self.should_exclude(py_file):
                continue

            entry = self.index_file(py_file)
            if entry:
                self.index.append(entry)

            # Progress indicator
            if self.stats['total_files'] % 100 == 0:
                print(f"  Indexed {self.stats['total_files']} files...", file=sys.stderr)

        print(f"\nIndexing complete: {self.stats['total_files']} files indexed")

        return {
            'metadata': {
                'repository': 'LukhasAI/Lukhas',
                'index_date': subprocess.run(
                    ['date', '-Iseconds'],
                    capture_output=True,
                    text=True
                ).stdout.strip(),
                'total_files': self.stats['total_files'],
                'statistics': self.stats,
            },
            'files': self.index,
        }


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    output_file = repo_root / 'reports' / 'analysis' / 'file_index.json'

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Build index
    indexer = FileIndexer(repo_root)
    index_data = indexer.build_index()

    # Write index to file
    with open(output_file, 'w') as f:
        json.dump(index_data, f, indent=2)

    print(f"\nFile index written to: {output_file}")
    print(f"Total files: {index_data['metadata']['total_files']}")
    print(f"Total lines: {index_data['metadata']['statistics']['total_lines']}")
    print(f"Files with docstrings: {index_data['metadata']['statistics']['files_with_docstrings']}")
    print(f"Files with TODOs: {index_data['metadata']['statistics']['files_with_todos']}")
    print(f"Total exports: {index_data['metadata']['statistics']['total_exports']}")


if __name__ == '__main__':
    main()
