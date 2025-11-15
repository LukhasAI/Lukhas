#!/usr/bin/env python3
"""
Symbolic Naming Consistency Analyzer for LUKHAS Repository Audit

Analyzes consistency of canonical names across the codebase:
- LUKHΛS, LUKHAS, Lucas, EQNOX, GLYPH, VIVOX, DAST, NIAS, OXN, etc.
- Detects alternate spellings and potential naming issues
- Provides suggestions for unification

Output: reports/analysis/symbolic_consistency.csv
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Set
import csv
import sys


class NamingAnalyzer:
    """Analyzes naming consistency across codebase"""

    # Canonical names that must be preserved
    CANONICAL_NAMES = {
        'LUKHAS': ['LUKHΛS', 'LUKHAS'],  # Both spellings canonical
        'LUCAS': ['Lucas', 'LUCAS'],
        'EQNOX': ['EQNOX', 'Eqnox'],
        'GLYPH': ['GLYPH', 'GLYPHs', 'Glyph', 'glyphs'],
        'VIVOX': ['VIVOX', 'Vivox'],
        'DAST': ['DAST', 'Dast'],
        'NIAS': ['NIAS', 'Nias'],
        'OXN': ['OXN'],
        'MATRIZ': ['MATRIZ', 'Matriz', 'matriz'],  # Note: case sensitivity issue
        'ONEIRIC': ['ONEIRIC', 'Oneiric Core', 'oneiric'],
        'L_ID': ['L_ID', 'ΛiD', 'Lambda ID', 'LambdaID'],
        'LUCAS_ID': ['LUCAS_ID'],
        'GUARDIAN': ['GUARDIAN', 'Guardian'],
        'CONSTELLATION': ['Constellation', 'CONSTELLATION'],
        'QUALIA': ['QUALIA', 'aka_qualia'],
    }

    # Patterns to detect variants
    VARIANT_PATTERNS = {
        'LUKHAS': r'\b(LUK[HΛ]?[A\u039b]S|lukhas|Lukhas)\b',
        'LUCAS': r'\b(LUCAS|Lucas|lucas)\b',
        'MATRIZ': r'\b(MATRIZ|Matriz|matriz|Matrix)\b',
        'GLYPH': r'\b(GLYPH|Glyph|glyph)s?\b',
        'VIVOX': r'\b(VIVOX|Vivox|vivox)\b',
        'DAST': r'\b(DAST|Dast|dast)\b',
        'NIAS': r'\b(NIAS|Nias|nias)\b',
        'EQNOX': r'\b(EQNOX|Eqnox|eqnox)\b',
        'OXN': r'\b(OXN|Oxn|oxn)\b',
        'ONEIRIC': r'\b(ONEIRIC|Oneiric|oneiric)\b',
        'GUARDIAN': r'\b(GUARDIAN|Guardian|guardian)\b',
    }

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.findings = []
        self.stats = {
            'total_files_scanned': 0,
            'files_with_variants': 0,
            'total_occurrences': 0,
        }

    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single file for naming consistency"""
        findings = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            # Check each canonical name pattern
            for canonical, pattern in self.VARIANT_PATTERNS.items():
                matches = list(re.finditer(pattern, content))

                for match in matches:
                    matched_text = match.group(0)
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()

                    # Determine if this is a canonical variant
                    is_canonical = matched_text in self.CANONICAL_NAMES.get(canonical, [])

                    # Suggest action
                    if is_canonical:
                        action = 'leave'  # Canonical variant, keep as is
                    else:
                        # Check context to suggest action
                        if 'import' in line_content.lower() or 'from' in line_content.lower():
                            action = 'review'  # Might be import path, needs review
                        elif file_path.name.lower().startswith('test'):
                            action = 'leave'  # Test files can have variants
                        else:
                            action = 'unify'  # Suggest unification

                    findings.append({
                        'file': str(file_path.relative_to(self.repo_root)),
                        'line': line_num,
                        'canonical': canonical,
                        'occurrence': matched_text,
                        'context': line_content[:100],
                        'is_canonical': is_canonical,
                        'suggested_action': action,
                        'confidence': 0.9 if is_canonical else 0.7,
                    })

        except Exception as e:
            pass  # Skip files that can't be read

        return findings

    def analyze_repository(self):
        """Analyze entire repository"""
        print("Analyzing naming consistency across repository...")

        # Scan all Python files
        python_files = list(self.repo_root.rglob('*.py'))
        excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'manifests'}

        for py_file in python_files:
            # Skip excluded directories
            if any(exc in py_file.parts for exc in excluded_dirs):
                continue

            file_findings = self.analyze_file(py_file)

            if file_findings:
                self.findings.extend(file_findings)
                self.stats['files_with_variants'] += 1

            self.stats['total_files_scanned'] += 1
            self.stats['total_occurrences'] += len(file_findings)

            if self.stats['total_files_scanned'] % 500 == 0:
                print(f"  Analyzed {self.stats['total_files_scanned']} files...", file=sys.stderr)

        print(f"\nNaming analysis complete: {self.stats['total_files_scanned']} files scanned")
        print(f"Files with variants: {self.stats['files_with_variants']}")
        print(f"Total occurrences: {self.stats['total_occurrences']}")

        return self.findings


def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent
    output_file = repo_root / 'reports' / 'analysis' / 'symbolic_consistency.csv'

    # Analyze repository
    analyzer = NamingAnalyzer(str(repo_root))
    findings = analyzer.analyze_repository()

    # Write findings to CSV
    with open(output_file, 'w', newline='') as f:
        if findings:
            fieldnames = ['file', 'line', 'canonical', 'occurrence', 'context',
                          'is_canonical', 'suggested_action', 'confidence']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(findings)

    print(f"\nNaming consistency report written to: {output_file}")
    print(f"Total findings: {len(findings)}")

    # Print summary by action
    actions = {}
    for finding in findings:
        action = finding['suggested_action']
        actions[action] = actions.get(action, 0) + 1

    print("\nSummary by action:")
    for action, count in sorted(actions.items()):
        print(f"  {action}: {count}")


if __name__ == '__main__':
    main()
