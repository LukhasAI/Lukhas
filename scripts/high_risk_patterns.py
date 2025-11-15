#!/usr/bin/env python3
"""
High-Risk Semantic Pattern Scanner for LUKHAS Repository Audit

Finds dangerous patterns using optimized grep:
- eval(), exec() calls
- Raw SQL concatenation
- Subprocess with unsanitized input
- pickle.loads on external input
- Dangerous file operations

Output: reports/analysis/high_risk_patterns.json
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import re

from lukhas.security.safe_subprocess import safe_run_command


class HighRiskScanner:
    """Scans for high-risk semantic patterns"""

    PATTERNS = {
        'eval_usage': {
            'pattern': r'\beval\s*\(',
            'risk_level': 'CRITICAL',
            'description': 'Use of eval() can execute arbitrary code',
        },
        'exec_usage': {
            'pattern': r'\bexec\s*\(',
            'risk_level': 'CRITICAL',
            'description': 'Use of exec() can execute arbitrary code',
        },
        'compile_usage': {
            'pattern': r'\bcompile\s*\(',
            'risk_level': 'HIGH',
            'description': 'Dynamic code compilation',
        },
        'pickle_loads': {
            'pattern': r'\bpickle\.loads?\s*\(',
            'risk_level': 'HIGH',
            'description': 'Unpickling untrusted data can execute arbitrary code',
        },
        'subprocess_shell': {
            'pattern': r'shell\s*=\s*True',
            'risk_level': 'HIGH',
            'description': 'Subprocess with shell=True can enable command injection',
        },
        'os_system': {
            'pattern': r'\bos\.system\s*\(',
            'risk_level': 'HIGH',
            'description': 'os.system() can enable command injection',
        },
        'sql_concat': {
            'pattern': r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE).*[+%].*',
            'risk_level': 'HIGH',
            'description': 'SQL string concatenation risks SQL injection',
        },
        'sql_format': {
            'pattern': r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE).*\.format\s*\(',
            'risk_level': 'HIGH',
            'description': 'SQL with .format() risks SQL injection',
        },
        'dangerous_open': {
            'pattern': r'open\s*\([^)]*["\']w["\']',
            'risk_level': 'MEDIUM',
            'description': 'File write operations that could overwrite critical files',
        },
        '__import__': {
            'pattern': r'\b__import__\s*\(',
            'risk_level': 'MEDIUM',
            'description': 'Dynamic imports can be dangerous',
        },
        'yaml_unsafe': {
            'pattern': r'yaml\.(load|unsafe_load)\s*\(',
            'risk_level': 'HIGH',
            'description': 'yaml.load() without safe loader can execute code',
        },
    }

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.findings = {
            'patterns': {},
            'summary': {
                'critical_count': 0,
                'high_count': 0,
                'medium_count': 0,
                'total_count': 0,
            }
        }

    def grep_pattern(self, pattern: str) -> List[Dict[str, str]]:
        """Use grep to find pattern occurrences"""
        try:
            # Use grep for faster searching
            result = subprocess.run(
                [
                    'grep', '-r', '-n', '-E',
                    pattern,
                    '--include=*.py',
                    '--exclude-dir=.git',
                    '--exclude-dir=__pycache__',
                    '--exclude-dir=.pytest_cache',
                    '--exclude-dir=manifests',
                    str(self.repo_root)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            matches = []
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue

                # Parse grep output: file:line:content
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    file_path = Path(parts[0])
                    try:
                        rel_path = file_path.relative_to(self.repo_root)
                    except ValueError:
                        rel_path = file_path

                    matches.append({
                        'file': str(rel_path),
                        'line': parts[1],
                        'context': parts[2].strip()[:200],  # Limit context length
                    })

            return matches

        except subprocess.TimeoutExpired:
            print(f"Timeout while searching for pattern: {pattern}")
            return []
        except Exception as e:
            print(f"Error searching for pattern {pattern}: {e}")
            return []

    def scan_repository(self):
        """Scan repository for all high-risk patterns"""
        print("Scanning for high-risk patterns...")

        for pattern_name, pattern_info in self.PATTERNS.items():
            print(f"  Searching for {pattern_name}...", end=' ')

            matches = self.grep_pattern(pattern_info['pattern'])

            self.findings['patterns'][pattern_name] = {
                'description': pattern_info['description'],
                'risk_level': pattern_info['risk_level'],
                'count': len(matches),
                'occurrences': matches,
            }

            # Update summary
            risk_level = pattern_info['risk_level']
            if risk_level == 'CRITICAL':
                self.findings['summary']['critical_count'] += len(matches)
            elif risk_level == 'HIGH':
                self.findings['summary']['high_count'] += len(matches)
            elif risk_level == 'MEDIUM':
                self.findings['summary']['medium_count'] += len(matches)

            self.findings['summary']['total_count'] += len(matches)

            print(f"{len(matches)} found")

        print(f"\nHigh-risk pattern scan complete")
        print(f"CRITICAL: {self.findings['summary']['critical_count']}")
        print(f"HIGH: {self.findings['summary']['high_count']}")
        print(f"MEDIUM: {self.findings['summary']['medium_count']}")
        print(f"TOTAL: {self.findings['summary']['total_count']}")

        return self.findings


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    output_file = repo_root / 'reports' / 'analysis' / 'high_risk_patterns.json'

    # Scan repository
    scanner = HighRiskScanner(str(repo_root))
    findings = scanner.scan_repository()

    # Write findings to file
    with open(output_file, 'w') as f:
        json.dump(findings, f, indent=2)

    print(f"\nHigh-risk patterns report written to: {output_file}")


if __name__ == '__main__':
    main()
