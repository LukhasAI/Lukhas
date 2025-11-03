#!/usr/bin/env python3
"""
Vocabulary Sweep Tool for Constellation Framework

Performs comprehensive terminology normalization across LUKHAS codebase:
- Trinity → Constellation Framework migration
- Cognitive AI terminology standardization
- Inconsistent naming pattern detection
- Automated correction suggestions

Usage:
    python tools/docs/vocabulary_sweep.py --scan
    python tools/docs/vocabulary_sweep.py --fix --dry-run
    python tools/docs/vocabulary_sweep.py --fix --execute
"""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class TerminologyRule:
    """Rule for terminology standardization"""
    old_term: str
    new_term: str
    category: str
    pattern: str
    case_sensitive: bool = False
    whole_word: bool = True
    contexts: List[str] = None  # File extensions or paths where this applies

@dataclass
class VocabularyIssue:
    """Detected vocabulary inconsistency"""
    file_path: str
    line_number: int
    old_text: str
    suggested_text: str
    rule_applied: str
    category: str
    confidence: str  # high, medium, low

# Constellation Framework terminology rules
TERMINOLOGY_RULES = [
    # Core Framework Migration
    TerminologyRule(
        old_term="Trinity",
        new_term="Constellation Framework",
        category="framework",
        pattern=r'\bTrinity\b',
        contexts=[".py", ".md", ".yml", ".yaml", ".json"]
    ),
    TerminologyRule(
        old_term="trinity",
        new_term="constellation",
        category="framework",
        pattern=r'\btrinity\b',
        contexts=[".py", ".md", ".yml", ".yaml"]
    ),
    TerminologyRule(
        old_term="TRINITY",
        new_term="CONSTELLATION",
        category="framework",
        pattern=r'\bTRINITY\b',
        contexts=[".py", ".md", ".yml", ".yaml"]
    ),

    # AGI → Cognitive AI Migration
    TerminologyRule(
        old_term="AGI",
        new_term="Cognitive AI",
        category="ai_terminology",
        pattern=r'\bAGI\b',
        contexts=[".md", ".rst", ".txt"]
    ),
    TerminologyRule(
        old_term="Artificial General Intelligence",
        new_term="Cognitive AI",
        category="ai_terminology",
        pattern=r'\bArtificial General Intelligence\b',
        case_sensitive=True,
        contexts=[".md", ".rst", ".txt"]
    ),

    # Component Naming Consistency
    TerminologyRule(
        old_term="matriz_core",
        new_term="matriz.core",
        category="naming",
        pattern=r'\bmatriz_core\b',
        contexts=[".py"]
    ),
    TerminologyRule(
        old_term="lukhas_core",
        new_term="core",
        category="naming",
        pattern=r'\blukhas_core\b',
        contexts=[".py"]
    ),

    # Documentation Consistency
    TerminologyRule(
        old_term="consciousness framework",
        new_term="Constellation Framework",
        category="documentation",
        pattern=r'\bconsciousness framework\b',
        case_sensitive=False,
        contexts=[".md", ".rst"]
    ),
    TerminologyRule(
        old_term="cognitive architecture",
        new_term="Constellation Framework architecture",
        category="documentation",
        pattern=r'\bcognitive architecture\b',
        case_sensitive=False,
        contexts=[".md", ".rst"]
    ),

    # API Consistency
    TerminologyRule(
        old_term="CognitiveNode",
        new_term="ConstellationNode",
        category="api",
        pattern=r'\bCognitiveNode\b',
        contexts=[".py"]
    ),
    TerminologyRule(
        old_term="cognitive_node",
        new_term="constellation_node",
        category="api",
        pattern=r'\bcognitive_node\b',
        contexts=[".py"]
    ),

    # Configuration Consistency
    TerminologyRule(
        old_term="COGNITIVE_LANE",
        new_term="CONSTELLATION_LANE",
        category="config",
        pattern=r'\bCOGNITIVE_LANE\b',
        contexts=[".py", ".yml", ".yaml", ".env"]
    ),
    TerminologyRule(
        old_term="cognitive_mode",
        new_term="constellation_mode",
        category="config",
        pattern=r'\bcognitive_mode\b',
        contexts=[".py", ".yml", ".yaml"]
    ),
]

# File patterns to scan
SCAN_PATTERNS = [
    "**/*.py",
    "**/*.md",
    "**/*.rst",
    "**/*.txt",
    "**/*.yml",
    "**/*.yaml",
    "**/*.json",
    "**/*.toml",
]

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    ".git", ".github", "__pycache__", ".pytest_cache", "node_modules",
    ".venv", "venv", "env", "build", "dist", ".tox"
}

class VocabularySweeper:
    """Main vocabulary sweep and correction engine"""

    def __init__(self, root_path: Path = None):
        self.root_path = root_path or Path.cwd()
        self.issues: List[VocabularyIssue] = []
        self.files_scanned = 0
        self.rules_applied = 0

    def scan_codebase(self) -> List[VocabularyIssue]:
        """Scan entire codebase for vocabulary issues"""
        print(f"🔍 Scanning codebase from {self.root_path}...")

        for pattern in SCAN_PATTERNS:
            for file_path in self.root_path.glob(pattern):
                if self._should_skip_file(file_path):
                    continue

                try:
                    self._scan_file(file_path)
                    self.files_scanned += 1
                except Exception as e:
                    print(f"⚠️ Error scanning {file_path}: {e}")

        print(f"✅ Scanned {self.files_scanned} files, found {len(self.issues)} issues")
        return self.issues

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        # Skip if in excluded directory
        for part in file_path.parts:
            if part in EXCLUDE_DIRS:
                return True

        # Skip if file is too large (>1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except OSError:
            return True

        # Skip binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)  # Try to read first 100 chars
        except (UnicodeDecodeError, PermissionError):
            return True

        return False

    def _scan_file(self, file_path: Path):
        """Scan individual file for vocabulary issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return

        for line_num, line in enumerate(lines, 1):
            for rule in TERMINOLOGY_RULES:
                if not self._rule_applies_to_file(rule, file_path):
                    continue

                matches = self._find_pattern_matches(rule, line)
                for match in matches:
                    issue = VocabularyIssue(
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=line_num,
                        old_text=line.strip(),
                        suggested_text=self._apply_rule_to_line(rule, line).strip(),
                        rule_applied=f"{rule.old_term} → {rule.new_term}",
                        category=rule.category,
                        confidence=self._calculate_confidence(rule, line, match)
                    )
                    self.issues.append(issue)

    def _rule_applies_to_file(self, rule: TerminologyRule, file_path: Path) -> bool:
        """Check if rule should be applied to this file"""
        if not rule.contexts:
            return True

        file_suffix = file_path.suffix.lower()
        file_path.name.lower()

        for context in rule.contexts:
            if context.startswith('.') and file_suffix == context:
                return True
            elif context in str(file_path):
                return True

        return False

    def _find_pattern_matches(self, rule: TerminologyRule, line: str) -> List[re.Match]:
        """Find all matches of rule pattern in line"""
        flags = 0 if rule.case_sensitive else re.IGNORECASE
        if rule.whole_word and not rule.pattern.startswith(r'\b'):
            pattern = r'\b' + rule.pattern + r'\b'
        else:
            pattern = rule.pattern

        return list(re.finditer(pattern, line, flags))

    def _apply_rule_to_line(self, rule: TerminologyRule, line: str) -> str:
        """Apply terminology rule to a line"""
        flags = 0 if rule.case_sensitive else re.IGNORECASE

        if rule.whole_word and not rule.pattern.startswith(r'\b'):
            pattern = r'\b' + rule.pattern + r'\b'
        else:
            pattern = rule.pattern

        return re.sub(pattern, rule.new_term, line, flags=flags)

    def _calculate_confidence(self, rule: TerminologyRule, line: str, match: re.Match) -> str:
        """Calculate confidence level for suggested change"""
        # High confidence for exact matches in appropriate contexts
        if rule.case_sensitive and rule.old_term == match.group():
            return "high"

        # Medium confidence for case-insensitive matches
        if not rule.case_sensitive:
            return "medium"

        # Lower confidence for pattern matches
        return "low"

    def generate_report(self, output_file: Path = None) -> Dict:
        """Generate comprehensive vocabulary report"""
        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "files_scanned": self.files_scanned,
            "total_issues": len(self.issues),
            "issues_by_category": self._group_issues_by_category(),
            "issues_by_confidence": self._group_issues_by_confidence(),
            "top_issues": self._get_top_issues(),
            "issues": [asdict(issue) for issue in self.issues]
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Report saved to {output_file}")

        return report

    def _group_issues_by_category(self) -> Dict[str, int]:
        """Group issues by category"""
        categories = {}
        for issue in self.issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        return categories

    def _group_issues_by_confidence(self) -> Dict[str, int]:
        """Group issues by confidence level"""
        confidence = {}
        for issue in self.issues:
            confidence[issue.confidence] = confidence.get(issue.confidence, 0) + 1
        return confidence

    def _get_top_issues(self, limit: int = 10) -> List[Dict]:
        """Get top issues by frequency"""
        rule_counts = {}
        for issue in self.issues:
            rule = issue.rule_applied
            if rule not in rule_counts:
                rule_counts[rule] = {"count": 0, "category": issue.category, "files": set()}
            rule_counts[rule]["count"] += 1
            rule_counts[rule]["files"].add(issue.file_path)

        # Convert to list and sort by count
        top_issues = []
        for rule, data in rule_counts.items():
            top_issues.append({
                "rule": rule,
                "category": data["category"],
                "count": data["count"],
                "files_affected": len(data["files"])
            })

        return sorted(top_issues, key=lambda x: x["count"], reverse=True)[:limit]

    def apply_fixes(self, dry_run: bool = True, confidence_threshold: str = "medium") -> Dict:
        """Apply vocabulary fixes to files"""
        print(f"🔧 {'Simulating' if dry_run else 'Applying'} vocabulary fixes...")

        confidence_levels = {"low": 0, "medium": 1, "high": 2}
        min_confidence = confidence_levels.get(confidence_threshold, 1)

        applicable_issues = [
            issue for issue in self.issues
            if confidence_levels.get(issue.confidence, 0) >= min_confidence
        ]

        files_to_fix = {}
        for issue in applicable_issues:
            if issue.file_path not in files_to_fix:
                files_to_fix[issue.file_path] = []
            files_to_fix[issue.file_path].append(issue)

        fixes_applied = 0
        files_modified = 0

        for file_path, issues in files_to_fix.items():
            try:
                if self._apply_fixes_to_file(file_path, issues, dry_run):
                    files_modified += 1
                    fixes_applied += len(issues)
            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")

        result = {
            "dry_run": dry_run,
            "confidence_threshold": confidence_threshold,
            "applicable_issues": len(applicable_issues),
            "files_modified": files_modified,
            "fixes_applied": fixes_applied
        }

        status = "would be" if dry_run else "were"
        print(f"✅ {fixes_applied} fixes {status} applied to {files_modified} files")

        return result

    def _apply_fixes_to_file(self, file_path: str, issues: List[VocabularyIssue], dry_run: bool) -> bool:
        """Apply fixes to a single file"""
        full_path = self.root_path / file_path

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return False

        original_content = content

        # Apply all rules to the content
        for rule in TERMINOLOGY_RULES:
            if self._rule_applies_to_file(rule, full_path):
                content = self._apply_rule_to_content(rule, content)

        if content != original_content:
            if not dry_run:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            print(f"{'Would fix' if dry_run else 'Fixed'} {file_path}")
            return True

        return False

    def _apply_rule_to_content(self, rule: TerminologyRule, content: str) -> str:
        """Apply rule to entire file content"""
        flags = 0 if rule.case_sensitive else re.IGNORECASE

        if rule.whole_word and not rule.pattern.startswith(r'\b'):
            pattern = r'\b' + rule.pattern + r'\b'
        else:
            pattern = rule.pattern

        return re.sub(pattern, rule.new_term, content, flags=flags)


def main():
    parser = argparse.ArgumentParser(description="Vocabulary sweep for Constellation Framework")
    parser.add_argument("--scan", action="store_true", help="Scan for vocabulary issues")
    parser.add_argument("--fix", action="store_true", help="Apply vocabulary fixes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually apply changes")
    parser.add_argument("--confidence", choices=["low", "medium", "high"], default="medium",
                       help="Minimum confidence level for fixes")
    parser.add_argument("--output", type=Path, help="Output file for scan results")
    parser.add_argument("--root", type=Path, help="Root directory to scan", default=Path.cwd())

    args = parser.parse_args()

    sweeper = VocabularySweeper(args.root)

    if args.scan or (not args.fix):
        # Perform scan
        issues = sweeper.scan_codebase()

        if issues:
            print("\n📊 Vocabulary Issues Summary:")
            print(f"   Total Issues: {len(issues)}")

            categories = sweeper._group_issues_by_category()
            for category, count in categories.items():
                print(f"   {category.title()}: {count}")

            confidence = sweeper._group_issues_by_confidence()
            for level, count in confidence.items():
                print(f"   {level.title()} Confidence: {count}")

        # Generate report
        output_file = args.output or Path("vocabulary_sweep_report.json")
        sweeper.generate_report(output_file)

        if issues:
            print("\n💡 Run with --fix to apply corrections")
            return 1
        else:
            print("✅ No vocabulary issues found!")
            return 0

    elif args.fix:
        # First scan to find issues
        sweeper.scan_codebase()

        if not sweeper.issues:
            print("✅ No vocabulary issues to fix!")
            return 0

        dry_run = not args.execute
        if dry_run:
            print("🔍 Dry-run mode: showing what would be changed")

        result = sweeper.apply_fixes(dry_run, args.confidence)

        if dry_run and result["fixes_applied"] > 0:
            print("\n💡 Run with --execute to apply these changes")

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
