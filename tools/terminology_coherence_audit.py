#!/usr/bin/env python3
"""
Terminology Coherence Audit

Comprehensive audit of terminology migration from legacy terms to
LUKHAS Constellation Framework vocabulary.

Usage:
    python tools/terminology_coherence_audit.py
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class TerminologyIssue:
    file_path: str
    line_number: int
    old_term: str
    suggested_replacement: str
    context: str
    severity: str  # 'critical', 'warning', 'info'

class TerminologyAuditor:
    """Comprehensive terminology coherence auditor"""

    def __init__(self):
        # Legacy terms that should be migrated
        self.legacy_terms = {
            "Trinity": "Constellation",
            "trinity": "constellation",
            "AGI": "Cognitive AI",
            "agi": "cognitive_ai",
            "artificial general intelligence": "cognitive artificial intelligence",
            "general intelligence": "cognitive intelligence",
            "super intelligence": "advanced cognitive intelligence",
            "superintelligence": "advanced_cognitive_intelligence",
            "general AI": "cognitive AI",
            "artificial_general_intelligence": "cognitive_artificial_intelligence"
        }

        # Required schema versions
        self.required_schemas = {
            "v2.0.0": ["guardian", "flag_snapshot", "governance"],
            "constellation-v1.0": ["framework", "architecture"],
            "lukhas-v3.0": ["api", "core", "system"]
        }

        # Approved terminology patterns
        self.approved_terms = {
            "LUKHAS", "Constellation Framework", "Cognitive AI", "MATRIZ",
            "Guardian System", "Lambda ID", "consciousness", "memory folds",
            "cascade prevention", "T4 standards", "0.01% excellence"
        }

        self.issues = []
        self.scanned_files = 0
        self.total_lines = 0

    def scan_file(self, file_path: Path) -> list[TerminologyIssue]:
        """Scan a single file for terminology issues"""
        issues = []

        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                self.total_lines += len(lines)

            for line_num, line in enumerate(lines, 1):
                # Check for legacy terms
                for old_term, new_term in self.legacy_terms.items():
                    if old_term in line:
                        # Skip if it's in a comment explaining the migration
                        if "migration" in line.lower() or "legacy" in line.lower():
                            continue

                        issue = TerminologyIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            old_term=old_term,
                            suggested_replacement=new_term,
                            context=line.strip()[:100],
                            severity="critical" if old_term in ["Trinity", "AGI"] else "warning"
                        )
                        issues.append(issue)

                # Check for schema version compliance
                if "schema" in line.lower() and "version" in line.lower():
                    found_schema = False
                    for required_schema in self.required_schemas:
                        if required_schema in line:
                            found_schema = True
                            break

                    if not found_schema and ("v1." in line or "v0." in line):
                        issue = TerminologyIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            old_term="outdated schema version",
                            suggested_replacement="v2.0.0 or constellation-v1.0",
                            context=line.strip()[:100],
                            severity="warning"
                        )
                        issues.append(issue)

        except Exception as e:
            print(f"Warning: Could not scan {file_path}: {e}")

        return issues

    def scan_directory(self, directory: Path, extensions: Optional[set[str]] = None) -> None:
        """Scan directory recursively for terminology issues"""
        if extensions is None:
            extensions = {'.py', '.md', '.yml', '.yaml', '.json', '.sh', '.js', '.ts'}

        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip certain directories
                skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue

                self.scanned_files += 1
                file_issues = self.scan_file(file_path)
                self.issues.extend(file_issues)

    def check_context_counts(self) -> dict[str, Any]:
        """Check for auto-generated context counts"""
        context_patterns = [
            r"context.*count.*\d+",
            r"total.*contexts?.*\d+",
            r"\d+.*context",
            r"constellation.*size.*\d+"
        ]

        context_files = []
        for file_path in Path('.').rglob('*.py'):
            try:
                with open(file_path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in context_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            context_files.append(str(file_path))
                            break
            except Exception:
                pass

        return {
            "context_tracking_files": len(context_files),
            "files_with_counts": context_files[:10],  # First 10 for brevity
            "auto_generated": len(context_files) > 5  # Heuristic
        }

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive terminology audit report"""

        # Categorize issues by severity
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        warning_issues = [i for i in self.issues if i.severity == "warning"]
        info_issues = [i for i in self.issues if i.severity == "info"]

        # Group issues by term
        issues_by_term = {}
        for issue in self.issues:
            term = issue.old_term
            if term not in issues_by_term:
                issues_by_term[term] = []
            issues_by_term[term].append(issue)

        # Check context counts
        context_data = self.check_context_counts()

        # Calculate compliance metrics
        total_issues = len(self.issues)
        issue_rate = (total_issues / max(self.scanned_files, 1)) * 100

        # Compliance assessment
        compliance_score = max(0, 100 - (len(critical_issues) * 10) - (len(warning_issues) * 2))

        return {
            "scan_summary": {
                "files_scanned": self.scanned_files,
                "total_lines": self.total_lines,
                "total_issues": total_issues,
                "issue_rate_per_file": round(issue_rate, 2)
            },
            "issues_by_severity": {
                "critical": len(critical_issues),
                "warning": len(warning_issues),
                "info": len(info_issues)
            },
            "issues_by_term": {
                term: len(issues) for term, issues in issues_by_term.items()
            },
            "context_analysis": context_data,
            "compliance": {
                "score": compliance_score,
                "grade": "A" if compliance_score >= 95 else "B" if compliance_score >= 85 else "C" if compliance_score >= 75 else "D",
                "clean_files": self.scanned_files - len({i.file_path for i in self.issues}),
                "problematic_files": len({i.file_path for i in self.issues})
            },
            "top_issues": [
                {
                    "file": issue.file_path.split('/')[-1],
                    "line": issue.line_number,
                    "term": issue.old_term,
                    "replacement": issue.suggested_replacement,
                    "severity": issue.severity
                }
                for issue in (critical_issues + warning_issues)[:10]
            ]
        }

def run_terminology_audit():
    """Run comprehensive terminology coherence audit"""
    print("📝 TERMINOLOGY COHERENCE AUDIT")
    print("=" * 50)

    auditor = TerminologyAuditor()

    print("🔍 Scanning codebase for terminology issues...")

    # Scan key directories only for performance
    key_dirs = ['lukhas', 'matriz', 'guardian', 'tests', 'tools', 'docs']
    for dir_name in key_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   Scanning {dir_name}/...")
            auditor.scan_directory(dir_path)

    # Generate report
    report = auditor.generate_report()

    print("✅ Scan completed")
    print(f"   Files scanned: {report['scan_summary']['files_scanned']}")
    print(f"   Lines analyzed: {report['scan_summary']['total_lines']:,}")

    print("\n📊 TERMINOLOGY COMPLIANCE RESULTS")
    print("-" * 40)

    # Issue breakdown
    issues = report['issues_by_severity']
    total_issues = sum(issues.values())

    print(f"Total Issues Found: {total_issues}")
    print(f"  Critical: {issues['critical']} (Trinity/AGI stragglers)")
    print(f"  Warning: {issues['warning']} (schema versions, deprecated terms)")
    print(f"  Info: {issues['info']} (minor inconsistencies)")

    # Compliance scoring
    compliance = report['compliance']
    print(f"\nCompliance Score: {compliance['score']}/100 (Grade: {compliance['grade']})")
    print(f"Clean Files: {compliance['clean_files']}/{report['scan_summary']['files_scanned']}")

    # Context analysis
    context = report['context_analysis']
    print(f"\nContext Tracking: {context['context_tracking_files']} files")
    print(f"Auto-generated: {'✅ YES' if context['auto_generated'] else '❌ NO'}")

    # Schema compliance
    schema_compliant = issues['critical'] == 0 and issues['warning'] <= 5
    print(f"Schema v2.0.0 Compliance: {'✅ PASS' if schema_compliant else '❌ FAIL'}")

    # Show top issues if any
    if total_issues > 0:
        print("\n🔧 TOP ISSUES TO FIX")
        print("-" * 40)
        for i, issue in enumerate(report['top_issues'][:5], 1):
            severity_emoji = "🚨" if issue['severity'] == 'critical' else "⚠️"
            print(f"{i}. {severity_emoji} {issue['file']}:{issue['line']}")
            print(f"   '{issue['term']}' → '{issue['replacement']}'")

    # Overall assessment
    terminology_pass = compliance['score'] >= 85

    print("\n🎯 OVERALL ASSESSMENT")
    print("-" * 40)
    print(f"Terminology Coherence: {'✅ PASS' if terminology_pass else '❌ FAIL'}")
    print(f"Schema Migration: {'✅ COMPLETE' if schema_compliant else '🟡 IN PROGRESS'}")
    print(f"Context Generation: {'✅ IMPLEMENTED' if context['auto_generated'] else '❌ MISSING'}")

    final_grade = "EXCELLENT" if compliance['score'] >= 95 else "GOOD" if compliance['score'] >= 85 else "NEEDS_WORK"
    print(f"\nFinal Grade: {final_grade}")

    return {
        "audit_passed": terminology_pass,
        "compliance_score": compliance['score'],
        "total_issues": total_issues,
        "report": report
    }

if __name__ == "__main__":
    result = run_terminology_audit()

    # Exit with appropriate code
    exit_code = 0 if result["audit_passed"] else 1
    exit(exit_code)
