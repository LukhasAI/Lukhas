#!/usr/bin/env python3
"""
Security Scanner for LUKHAS Repository

Scans for:
- High-risk code patterns (eval, exec, etc.)
- Potential secrets (API keys, passwords)
- Network calls
- Dependencies and their risks
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List
import json


class SecurityScanner:
    """Scans repository for security issues"""

    HIGH_RISK_PATTERNS = {
        'eval': r'\beval\(',
        'exec': r'\bexec\(',
        'pickle': r'\bpickle\.loads?\(',
        'yaml_unsafe': r'yaml\.load\(',
        'shell_true': r'shell\s*=\s*True',
        'sql_injection': r'execute\([\'"].*%s',
        'hardcoded_password': r'password\s*=\s*[\'"][^\'"]+[\'"]',
    }

    SECRET_PATTERNS = {
        'api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'"][a-zA-Z0-9_\-]{20,}[\'"]',
        'secret_key': r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*[\'"][a-zA-Z0-9_\-]{20,}[\'"]',
        'aws_key': r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*[\'"][A-Z0-9]{20,}[\'"]',
        'github_token': r'(?i)(github[_-]?token|gh[_-]?token)\s*[:=]\s*[\'"]ghp_[a-zA-Z0-9]{36,}[\'"]',
        'private_key': r'-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----',
        'jwt_token': r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
    }

    NETWORK_PATTERNS = {
        'requests': r'\brequests\.',
        'urllib': r'\burllib\.',
        'http_client': r'\bhttp\.client\.',
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

    def _should_skip_secret_scan(self, file_path: Path) -> bool:
        """Determine if a file should be excluded from secret scanning."""
        try:
            relative_path = file_path.relative_to(self.repo_root)
        except ValueError:
            relative_path = file_path

        lowered_parts: List[str] = [part.lower() for part in relative_path.parts]
        if not lowered_parts:
            return False

        directories = lowered_parts[:-1]
        filename = lowered_parts[-1]

        if any(part in {'tests', 'test', 'testing', 'examples', 'example'} for part in directories):
            return True

        if filename.startswith('test_') or filename.endswith('_test.py'):
            return True

        if filename == '.env.example' or filename.endswith('.example'):
            return True

        return False

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
                    if self._should_skip_secret_scan(file_path):
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
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)

        return findings

    def scan_directory(self, directory: Path = None):
        """Scan all Python files in directory"""
        if directory is None:
            directory = self.repo_root

        python_files = list(directory.rglob('*.py'))

        # Exclude common directories
        exclude_patterns = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}

        for py_file in python_files:
            # Skip if in excluded directory
            if any(part in exclude_patterns for part in py_file.parts):
                continue

            file_findings = self.scan_file_for_patterns(py_file)

            # Categorize findings
            for finding in file_findings:
                if finding['type'] == 'high_risk':
                    self.findings['high_risk_patterns'].append(finding)
                elif finding['type'] == 'secret_pattern':
                    self.findings['secret_patterns'].append(finding)
                elif finding['type'] == 'network_call':
                    self.findings['network_calls'].append(finding)

        # Update summary
        self.findings['summary']['total_high_risk'] = len(self.findings['high_risk_patterns'])
        self.findings['summary']['total_secrets_found'] = len(self.findings['secret_patterns'])
        self.findings['summary']['total_network_calls'] = len(self.findings['network_calls'])

    def scan_dependencies(self):
        """Scan requirements files for dependencies"""
        requirements_files = [
            'requirements.txt',
            'requirements-prod.txt',
            'requirements-dev.txt',
        ]

        for req_file in requirements_files:
            req_path = self.repo_root / req_file
            if req_path.exists():
                with open(req_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse package name
                            pkg = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                            category = 'dev' if 'dev' in req_file else 'core'
                            self.findings['dependencies'][category].append(pkg)

        self.findings['summary']['total_dependencies'] = (
            len(self.findings['dependencies']['core']) +
            len(self.findings['dependencies']['dev'])
        )

    def generate_report(self, output_format: str = 'json') -> str:
        """Generate security report"""
        if output_format == 'json':
            return json.dumps(self.findings, indent=2)
        elif output_format == 'text':
            report = []
            report.append("=" * 80)
            report.append("LUKHAS SECURITY SCAN REPORT")
            report.append("=" * 80)
            report.append("")

            # Summary
            report.append("SUMMARY:")
            report.append(f"  High-Risk Patterns: {self.findings['summary']['total_high_risk']}")
            report.append(f"  Potential Secrets: {self.findings['summary']['total_secrets_found']}")
            report.append(f"  Network Calls: {self.findings['summary']['total_network_calls']}")
            report.append(f"  Dependencies: {self.findings['summary']['total_dependencies']}")
            report.append("")

            # High-risk findings
            if self.findings['high_risk_patterns']:
                report.append("HIGH-RISK PATTERNS:")
                for finding in self.findings['high_risk_patterns']:
                    report.append(f"  [{finding['pattern']}] {finding['file']}:{finding['line']}")
                    report.append(f"    {finding['context']}")
                report.append("")

            # Secret findings
            if self.findings['secret_patterns']:
                report.append("POTENTIAL SECRETS:")
                for finding in self.findings['secret_patterns']:
                    report.append(f"  [{finding['pattern']}] {finding['file']}:{finding['line']}")
                report.append("")

            return "\n".join(report)

        return ""


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Security scanner for LUKHAS')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                        help='Output format')
    parser.add_argument('--output', type=str, help='Output file (default: stdout)')

    args = parser.parse_args()

    # Find repo root
    repo_root = Path(__file__).parent.parent

    scanner = SecurityScanner(str(repo_root))
    print("Scanning Python files...", file=sys.stderr)
    scanner.scan_directory()
    print("Scanning dependencies...", file=sys.stderr)
    scanner.scan_dependencies()

    report = scanner.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == '__main__':
    main()
