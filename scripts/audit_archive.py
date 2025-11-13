#!/usr/bin/env python3
"""Archive Salvage Audit Tool.

This tool analyzes the archive/ directory to identify valuable files
that could be restored to the active codebase.

Analysis criteria:
- File exists in archive but not in active code
- File has unique algorithms/patterns
- File has comprehensive tests
- File has active GitHub issue references
- File was archived recently (< 6 months)

Output: release_artifacts/archive/archive_review.csv
"""

from __future__ import annotations

import ast
import csv
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class ArchiveCandidate:
    """Represents a file candidate for restoration."""

    archived_path: str
    candidate_status: str  # P1, P2, P3, or SKIP
    reason: str
    restore_to: str
    priority: int


class ArchiveAuditor:
    """Analyzes archive files and identifies restoration candidates."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.archive_dir = repo_root / "archive"
        self.active_dirs = [
            repo_root / "lukhas",
            repo_root / "scripts",
            repo_root / "tests",
        ]
        self.candidates: list[ArchiveCandidate] = []
        from datetime import timezone
        self.six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)

    def run_audit(self) -> None:
        """Execute complete archive audit."""
        print("Starting archive salvage audit...")
        print(f"Archive directory: {self.archive_dir}")
        print(f"Active code directories: {[str(d) for d in self.active_dirs]}")

        # Find all Python files in archive
        archive_files = list(self.archive_dir.rglob("*.py"))
        print(f"\nFound {len(archive_files)} Python files in archive")

        for archive_file in archive_files:
            self._analyze_file(archive_file)

        # Sort by priority (P1 highest)
        self.candidates.sort(key=lambda x: (x.priority, x.archived_path))

        self._write_csv()
        self._generate_restoration_proposals()
        self._print_summary()

    def _analyze_file(self, archive_file: Path) -> None:
        """Analyze a single archive file."""
        # Skip __pycache__ and other non-source files
        if "__pycache__" in str(archive_file) or archive_file.name.startswith("."):
            return

        rel_path = archive_file.relative_to(self.archive_dir)

        # Check archive date from directory name or git log
        archive_date = self._get_archive_date(archive_file)
        # Make naive datetime aware for comparison
        from datetime import timezone
        if archive_date and archive_date.tzinfo is None:
            archive_date = archive_date.replace(tzinfo=timezone.utc)
        is_recent = archive_date and archive_date > self.six_months_ago

        # Check if equivalent file exists in active code
        has_active_equivalent = self._has_active_equivalent(rel_path, archive_file)

        # Analyze file content
        has_tests = self._has_comprehensive_tests(archive_file)
        has_unique_patterns = self._has_unique_patterns(archive_file)
        has_github_refs = self._has_github_references(archive_file)

        # Determine restoration status
        status, priority, reason = self._calculate_priority(
            has_active_equivalent=has_active_equivalent,
            has_tests=has_tests,
            has_unique_patterns=has_unique_patterns,
            has_github_refs=has_github_refs,
            is_recent=is_recent,
            archive_file=archive_file,
        )

        if status != "SKIP":
            restore_to = self._suggest_restore_path(rel_path, archive_file)
            candidate = ArchiveCandidate(
                archived_path=str(rel_path),
                candidate_status=status,
                reason=reason,
                restore_to=restore_to,
                priority=priority,
            )
            self.candidates.append(candidate)

    def _get_archive_date(self, archive_file: Path) -> datetime | None:
        """Extract archive date from directory name or git log."""
        # Try to extract date from directory name (e.g., quarantine_2025-10-26)
        parts = str(archive_file.relative_to(self.archive_dir)).split("/")
        for part in parts:
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", part)
            if date_match:
                try:
                    return datetime.strptime(date_match.group(1), "%Y-%m-%d")
                except ValueError:
                    pass

        # Try git log
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%aI", "--", str(archive_file)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                date_str = result.stdout.strip()
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        return None

    def _has_active_equivalent(self, rel_path: Path, archive_file: Path) -> bool:
        """Check if an equivalent file exists in active codebase."""
        filename = archive_file.name

        # Check if exact file exists in active dirs
        for active_dir in self.active_dirs:
            if not active_dir.exists():
                continue

            # Check for same filename
            matching_files = list(active_dir.rglob(filename))
            if matching_files:
                # Compare content similarity
                for match in matching_files:
                    if self._are_files_similar(archive_file, match):
                        return True

        return False

    def _are_files_similar(self, file1: Path, file2: Path) -> bool:
        """Check if two files are similar (>70% match)."""
        try:
            content1 = file1.read_text(encoding="utf-8", errors="ignore")
            content2 = file2.read_text(encoding="utf-8", errors="ignore")

            # Simple similarity check: compare non-whitespace lines
            lines1 = {
                line.strip()
                for line in content1.splitlines()
                if line.strip() and not line.strip().startswith("#")
            }
            lines2 = {
                line.strip()
                for line in content2.splitlines()
                if line.strip() and not line.strip().startswith("#")
            }

            if not lines1 or not lines2:
                return False

            common = lines1 & lines2
            similarity = len(common) / max(len(lines1), len(lines2))
            return similarity > 0.7

        except (OSError, UnicodeDecodeError):
            return False

    def _has_comprehensive_tests(self, archive_file: Path) -> bool:
        """Check if file has comprehensive tests."""
        # Check if it's a test file itself
        if "test" in archive_file.name.lower():
            try:
                content = archive_file.read_text(encoding="utf-8", errors="ignore")
                # Count test functions
                test_count = len(re.findall(r"def test_\w+", content))
                # Count assertions
                assert_count = len(re.findall(r"\bassert\b", content))
                return test_count >= 3 and assert_count >= 5
            except (OSError, UnicodeDecodeError):
                return False

        # Check if corresponding test file exists
        test_variants = [
            f"test_{archive_file.stem}.py",
            f"{archive_file.stem}_test.py",
        ]

        test_dir = archive_file.parent / "tests"
        if test_dir.exists():
            for variant in test_variants:
                if (test_dir / variant).exists():
                    return True

        return False

    def _has_unique_patterns(self, archive_file: Path) -> bool:
        """Check if file contains unique algorithms or patterns."""
        try:
            content = archive_file.read_text(encoding="utf-8", errors="ignore")

            # Skip if file is too small
            if len(content) < 200:
                return False

            # Parse AST to analyze complexity
            try:
                tree = ast.parse(content)

                # Count classes and functions
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

                # Check for unique patterns
                has_complex_classes = len(classes) >= 2
                has_complex_functions = len(functions) >= 3

                # Check for interesting imports
                interesting_imports = {
                    "ast",
                    "anthropic",
                    "openai",
                    "streamlit",
                    "fastapi",
                    "redis",
                    "sqlalchemy",
                }
                imports = {
                    n.names[0].name.split(".")[0]
                    for n in ast.walk(tree)
                    if isinstance(n, (ast.Import, ast.ImportFrom))
                    and hasattr(n, "names")
                    and n.names
                }
                has_interesting_imports = bool(imports & interesting_imports)

                return has_complex_classes or has_complex_functions or has_interesting_imports

            except SyntaxError:
                # If syntax error, check for docstrings and comments
                has_docstrings = '"""' in content or "'''" in content
                comment_ratio = len(re.findall(r"^\s*#", content, re.MULTILINE)) / max(
                    len(content.splitlines()), 1
                )
                return has_docstrings and comment_ratio > 0.1

        except (OSError, UnicodeDecodeError):
            return False

        return False

    def _has_github_references(self, archive_file: Path) -> bool:
        """Check if file references GitHub issues."""
        try:
            content = archive_file.read_text(encoding="utf-8", errors="ignore")

            # Look for GitHub issue references
            github_patterns = [
                r"#\d{3,}",  # Issue numbers
                r"github\.com/[^/]+/[^/]+/issues/\d+",  # Full URLs
                r"TODO.*#\d+",  # TODOs with issue numbers
                r"FIXME.*#\d+",  # FIXMEs with issue numbers
            ]

            for pattern in github_patterns:
                if re.search(pattern, content):
                    return True

        except (OSError, UnicodeDecodeError):
            pass

        return False

    def _calculate_priority(
        self,
        has_active_equivalent: bool,
        has_tests: bool,
        has_unique_patterns: bool,
        has_github_refs: bool,
        is_recent: bool,
        archive_file: Path,
    ) -> tuple[str, int, str]:
        """Calculate restoration priority."""
        reasons = []

        # Skip if has active equivalent
        if has_active_equivalent:
            return "SKIP", 99, "Active equivalent exists"

        # Calculate score
        score = 0
        if has_tests:
            score += 3
            reasons.append("comprehensive tests")
        if has_unique_patterns:
            score += 2
            reasons.append("unique algorithms")
        if has_github_refs:
            score += 2
            reasons.append("GitHub issue refs")
        if is_recent:
            score += 1
            reasons.append("recent archive (<6mo)")

        # Check for special indicators
        if "debt_ratchet" in str(archive_file):
            score += 2
            reasons.append("CI/tooling utility")
        if "delegation" in str(archive_file):
            score += 1
            reasons.append("delegation tool")

        # Determine priority
        if score >= 6:
            status = "P1"
            priority = 1
        elif score >= 4:
            status = "P2"
            priority = 2
        elif score >= 2:
            status = "P3"
            priority = 3
        else:
            return "SKIP", 99, "Low value"

        reason = "; ".join(reasons) if reasons else "Restoration candidate"
        return status, priority, reason

    def _suggest_restore_path(self, rel_path: Path, archive_file: Path) -> str:
        """Suggest where file should be restored."""
        # Map archive structure to active structure
        parts = list(rel_path.parts)

        # Remove archive timestamp directories
        cleaned_parts = [p for p in parts if not re.search(r"\d{4}-\d{2}-\d{2}", p)]

        # Map quarantine/phase2_syntax/ci -> scripts/
        if "ci" in cleaned_parts:
            return f"scripts/{cleaned_parts[-1]}"

        # Map quarantine/phase2_syntax/dev -> scripts/
        if "dev" in cleaned_parts:
            return f"scripts/{cleaned_parts[-1]}"

        # Map delegation_reports -> scripts/
        if "delegation_reports" in cleaned_parts:
            return f"scripts/{cleaned_parts[-1]}"

        # Map test files
        if "test" in archive_file.name.lower():
            return f"tests/{cleaned_parts[-1]}"

        # Default to scripts
        return f"scripts/{cleaned_parts[-1]}"

    def _write_csv(self) -> None:
        """Write audit results to CSV."""
        output_file = self.repo_root / "release_artifacts" / "archive" / "archive_review.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with output_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["archived_path", "candidate_status", "reason", "restore_to", "priority"]
            )

            for candidate in self.candidates:
                writer.writerow(
                    [
                        candidate.archived_path,
                        candidate.candidate_status,
                        candidate.reason,
                        candidate.restore_to,
                        candidate.priority,
                    ]
                )

        print(f"\nCSV report written to: {output_file}")

    def _generate_restoration_proposals(self) -> None:
        """Generate detailed restoration proposals for P1/P2 items."""
        high_priority = [c for c in self.candidates if c.priority <= 2]

        if not high_priority:
            print("\nNo high-priority restoration candidates found.")
            return

        output_file = (
            self.repo_root / "release_artifacts" / "archive" / "restoration_proposals.md"
        )

        with output_file.open("w", encoding="utf-8") as f:
            f.write("# Archive Restoration Proposals\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- Total candidates: {len(self.candidates)}\n")
            f.write(f"- P1 candidates: {len([c for c in self.candidates if c.priority == 1])}\n")
            f.write(f"- P2 candidates: {len([c for c in self.candidates if c.priority == 2])}\n")
            f.write(f"- P3 candidates: {len([c for c in self.candidates if c.priority == 3])}\n\n")

            f.write("## High Priority Restoration Candidates\n\n")

            for candidate in high_priority:
                f.write(f"### {candidate.candidate_status}: {candidate.archived_path}\n\n")
                f.write(f"**Reason**: {candidate.reason}\n\n")
                f.write(f"**Restore to**: `{candidate.restore_to}`\n\n")
                f.write("**Action items**:\n")
                f.write(f"1. Review file: `archive/{candidate.archived_path}`\n")
                f.write("2. Validate functionality and tests\n")
                f.write("3. Update imports and dependencies\n")
                f.write(f"4. Copy to: `{candidate.restore_to}`\n")
                f.write(f"5. Run tests: `pytest {candidate.restore_to}`\n\n")
                f.write("---\n\n")

        print(f"Restoration proposals written to: {output_file}")

    def _print_summary(self) -> None:
        """Print audit summary."""
        print("\n" + "=" * 60)
        print("ARCHIVE AUDIT SUMMARY")
        print("=" * 60)

        p1_count = len([c for c in self.candidates if c.priority == 1])
        p2_count = len([c for c in self.candidates if c.priority == 2])
        p3_count = len([c for c in self.candidates if c.priority == 3])

        print(f"\nTotal candidates found: {len(self.candidates)}")
        print(f"  - P1 (Critical): {p1_count}")
        print(f"  - P2 (High): {p2_count}")
        print(f"  - P3 (Medium): {p3_count}")

        if p1_count > 0:
            print("\nP1 Candidates:")
            for c in [c for c in self.candidates if c.priority == 1][:5]:
                print(f"  - {c.archived_path}: {c.reason}")

        print("\nNext steps:")
        print("  1. Review: release_artifacts/archive/archive_review.csv")
        print("  2. Read proposals: release_artifacts/archive/restoration_proposals.md")
        print("  3. Restore high-priority files as needed")
        print("=" * 60)


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).resolve().parents[1]

    auditor = ArchiveAuditor(repo_root)
    auditor.run_audit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
