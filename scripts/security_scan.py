#!/usr/bin/env python3
"""
Security Surface Scanner for LUKHAS Repository Audit

Identifies:
- Dependency risks (parsing requirements.txt, pyproject.toml)
- High-risk patterns (eval, exec, shell commands, pickle)
- Network calls and external dependencies
- Hardcoded secrets/tokens (patterns)
- SQL injection risks

Output: reports/analysis/security_surface.json
"""

import ast
import json
import re
import toml
from pathlib import Path
from typing import Dict, List, Any, Set
import sys


class SecurityScanner:
    """Scans repository for security risks"""

    HIGH_RISK_PATTERNS = {
        'eval': r'\beval\s*\(',
        'exec': r'\bexec\s*\(',
        'compile': r'\bcompile\s*\(',
        '__import__': r'\b__import__\s*\(',
        'pickle_loads': r'\bpickle\.loads?\s*\(',
        'subprocess': r'\bsubprocess\.(run|call|Popen|check_output)\s*\(',
        'os_system': r'\bos\.system\s*\(',
        'shell_true': r'shell\s*=\s*True',
        'sql_format': r'(SELECT|INSERT|UPDATE|DELETE).*\.format\(',
        'sql_concat': r'(SELECT|INSERT|UPDATE|DELETE).*\+.*',
    }

    SECRET_PATTERNS = {
        'api_key': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']{10,}["\']',
        'secret_key': r'["\']?secret[_-]?key["\']?\s*[:=]\s*["\'][^"\']{10,}["\']',
        'password': r'["\']?password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
        'token': r'["\']?token["\']?\s*[:=]\s*["\'][^"\']{20,}["\']',
        'private_key': r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
        'aws_key': r'AKIA[0-9A-Z]{16}',
    }

    NETWORK_PATTERNS = {
        'http_request': r'\b(requests|httpx|aiohttp|urllib)\.',
        'socket': r'\bsocket\.',
        'telnetlib': r'\btelnetlib\.',
        'ftplib': r'\bftplib\.',
    }

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.findings = {
            'high_risk_patterns': [],
            'secret_patterns': [],
            'network_calls': [],
            'dependencies': {
                'core': [],
                'dev': [],
                'optional': [],
                'risks': []
            },
            'summary': {
                'total_high_risk': 0,
                'total_secrets_found': 0,
                'total_network_calls': 0,
                'total_dependencies': 0,
            }
        }

    def scan_file_for_patterns(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for security patterns"""
        findings = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check high-risk patterns
            for pattern_name, pattern in self.HIGH_RISK_PATTERNS.items():
                matches = list(re.finditer(pattern, content))
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        'type': 'high_risk',
                        'pattern': pattern_name,
                        'file': str(file_path.relative_to(self.repo_root)),
                        'line': line_num,
                        'context': content.split('\n')[line_num - 1].strip()[:100],
                    })

            # Check for secrets (be careful with false positives)
            for pattern_name, pattern in self.SECRET_PATTERNS.items():
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    # Skip if it's in comments, tests, or examples
                    line_content = content.split('\n')[line_num - 1]
                    if any(marker in str(file_path).lower() for marker in ['test', 'example', '.env.example']):
                        continue
                    if line_content.strip().startswith('#'):
                        continue

                    findings.append({
                        'type': 'secret_pattern',
                        'pattern': pattern_name,
                        'file': str(file_path.relative_to(self.repo_root)),
                        'line': line_num,
                        'context': '[REDACTED]',  # Don't expose potential secrets
                    })

            # Check for network calls
            for pattern_name, pattern in self.NETWORK_PATTERNS.items():
                matches = list(re.finditer(pattern, content))
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        'type': 'network_call',
                        'pattern': pattern_name,
                        'file': str(file_path.relative_to(self.repo_root)),
                        'line': line_num,
                        'context': content.split('\n')[line_num - 1].strip()[:100],
                    })

        except Exception as e:
            pass  # Skip files that can't be read

        return findings

    def scan_dependencies(self):
        """Scan dependency files for risks"""
        # Parse pyproject.toml
        pyproject_path = self.repo_root / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r') as f:
                    pyproject = toml.load(f)

                # Extract dependencies
                if 'project' in pyproject and 'dependencies' in pyproject['project']:
                    self.findings['dependencies']['core'] = pyproject['project']['dependencies']

                if 'project' in pyproject and 'optional-dependencies' in pyproject['project']:
                    for group, deps in pyproject['project']['optional-dependencies'].items():
                        self.findings['dependencies']['optional'].extend([
                            {'group': group, 'package': dep} for dep in deps
                        ])

            except Exception as e:
                print(f"Error parsing pyproject.toml: {e}", file=sys.stderr)

        # Parse requirements files
        for req_file in ['requirements.txt', 'requirements-dev.txt', 'requirements-prod.txt']:
            req_path = self.repo_root / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        deps = [
                            line.strip() for line in f
                            if line.strip() and not line.strip().startswith('#')
                        ]

                    if 'dev' in req_file:
                        self.findings['dependencies']['dev'].extend(deps)
                    else:
                        self.findings['dependencies']['core'].extend(deps)

                except Exception as e:
                    print(f"Error parsing {req_file}: {e}", file=sys.stderr)

        # Identify risky dependencies
        risky_packages = {
            'pickle', 'yaml', 'eval', 'exec', 'subprocess',
            # Add more known risky packages
        }

        all_deps = (
            self.findings['dependencies']['core'] +
            self.findings['dependencies']['dev'] +
            [d['package'] for d in self.findings['dependencies']['optional']]
        )

        for dep in all_deps:
            dep_name = dep.split('[')[0].split('>=')[0].split('==')[0].split('<')[0].strip()
            if any(risky in dep_name.lower() for risky in risky_packages):
                self.findings['dependencies']['risks'].append({
                    'package': dep,
                    'reason': 'Known risky package'
                })

    def scan_repository(self):
        """Scan entire repository"""
        print("Scanning repository for security risks...")

        # Scan all Python files
        python_files = list(self.repo_root.rglob('*.py'))
        excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'manifests'}

        processed = 0
        for py_file in python_files:
            # Skip excluded directories
            if any(exc in py_file.parts for exc in excluded_dirs):
                continue

            findings = self.scan_file_for_patterns(py_file)

            for finding in findings:
                if finding['type'] == 'high_risk':
                    self.findings['high_risk_patterns'].append(finding)
                    self.findings['summary']['total_high_risk'] += 1
                elif finding['type'] == 'secret_pattern':
                    self.findings['secret_patterns'].append(finding)
                    self.findings['summary']['total_secrets_found'] += 1
                elif finding['type'] == 'network_call':
                    self.findings['network_calls'].append(finding)
                    self.findings['summary']['total_network_calls'] += 1

            processed += 1
            if processed % 500 == 0:
                print(f"  Scanned {processed} files...", file=sys.stderr)

        # Scan dependencies
        self.scan_dependencies()
        self.findings['summary']['total_dependencies'] = (
            len(self.findings['dependencies']['core']) +
            len(self.findings['dependencies']['dev']) +
            len(self.findings['dependencies']['optional'])
        )

        print(f"\nSecurity scan complete: {processed} files scanned")

        return self.findings


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    output_file = repo_root / 'reports' / 'analysis' / 'security_surface.json'

    # Scan repository
    scanner = SecurityScanner(str(repo_root))
    findings = scanner.scan_repository()

    # Write findings to file
    with open(output_file, 'w') as f:
        json.dump(findings, f, indent=2)

    print(f"\nSecurity surface report written to: {output_file}")
    print(f"High-risk patterns: {findings['summary']['total_high_risk']}")
    print(f"Secret patterns found: {findings['summary']['total_secrets_found']}")
    print(f"Network calls: {findings['summary']['total_network_calls']}")
    print(f"Total dependencies: {findings['summary']['total_dependencies']}")


if __name__ == '__main__':
    main()
