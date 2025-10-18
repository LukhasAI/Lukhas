#!/usr/bin/env python3
"""
Concern-Based Commit Splitter
=============================
Analyzes git changes and automatically creates separate PRs based on concern areas.
Helps break down large commits into manageable, reviewable chunks.

Concern Categories:
- schemas: Schema definitions, validation rules
- discovery: File discovery, pattern detection
- ci: CI/CD workflows, automation scripts
- contracts: Contract definitions, API specs
- dashboard: Dashboard, monitoring, reporting
- testing: Test files, test utilities
- docs: Documentation, README files
- config: Configuration files, settings

Features:
- Automated concern detection
- Dependency analysis
- PR template generation
- Safe splitting with validation
"""

import json
import logging
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class FileChange:
    """Represents a file change in git"""

    path: str
    status: str  # M, A, D, R
    lines_added: int
    lines_removed: int
    concern: str = "unknown"
    dependencies: list[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ConcernGroup:
    """Group of files by concern area"""

    name: str
    description: str
    files: list[FileChange]
    total_lines: int = 0
    risk_level: str = "low"  # low/medium/high
    dependencies: list[str] = None
    pr_template: str = ""

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        self.total_lines = sum(f.lines_added + f.lines_removed for f in self.files)

        # Calculate risk level
        if self.total_lines > 500 or len(self.files) > 20:
            self.risk_level = "high"
        elif self.total_lines > 100 or len(self.files) > 10:
            self.risk_level = "medium"


class ConcernSplitter:
    """Main concern-based commit splitter"""

    def __init__(self):
        self.concern_patterns = {
            "schemas": [
                r".*schema.*\.py$",
                r".*schema.*\.json$",
                r".*validation.*\.py$",
                r".*/schema/.*",
                r".*_schema\.py$",
                r".*schema_.*\.py$",
            ],
            "discovery": [
                r".*discovery.*\.py$",
                r".*finder.*\.py$",
                r".*search.*\.py$",
                r".*pattern.*\.py$",
                r".*detect.*\.py$",
                r".*analyzer.*\.py$",
            ],
            "ci": [
                r"\.github/workflows/.*",
                r".*ci.*\.yml$",
                r".*ci.*\.yaml$",
                r"tools/ci/.*",
                r"scripts/.*\.sh$",
                r"Makefile$",
                r".*pipeline.*\.py$",
                r".*autofix.*\.py$",
                r".*automation.*\.py$",
            ],
            "contracts": [
                r".*contract.*\.py$",
                r".*api.*\.py$",
                r".*interface.*\.py$",
                r".*protocol.*\.py$",
                r".*spec.*\.py$",
            ],
            "dashboard": [
                r".*dashboard.*\.py$",
                r".*monitor.*\.py$",
                r".*reporting.*\.py$",
                r"tools/dashboard/.*",
                r".*metrics.*\.py$",
                r".*health.*\.py$",
            ],
            "testing": [
                r"test_.*\.py$",
                r".*_test\.py$",
                r"tests/.*",
                r".*testing.*\.py$",
                r".*smoke.*\.py$",
                r"pytest\.ini$",
                r"conftest\.py$",
            ],
            "docs": [r".*\.md$", r".*\.rst$", r"docs/.*", r"README.*", r"CHANGELOG.*", r".*\.txt$"],
            "config": [r".*\.toml$", r".*\.ini$", r".*\.cfg$", r".*config.*\.py$", r".*settings.*\.py$", r".*\.json$"],
        }

        self.concern_descriptions = {
            "schemas": "Schema definitions and validation rules",
            "discovery": "File discovery and pattern detection systems",
            "ci": "CI/CD workflows and automation scripts",
            "contracts": "API contracts and interface definitions",
            "dashboard": "Monitoring, dashboard, and reporting systems",
            "testing": "Test files and testing infrastructure",
            "docs": "Documentation and README files",
            "config": "Configuration files and settings",
        }

    def get_git_changes(self, base_ref: str = "HEAD") -> list[FileChange]:
        """Get list of changed files from git"""
        logger.info(f"🔍 Analyzing git changes from {base_ref}")

        try:
            # Get changed files with stats
            cmd = ["git", "diff", "--numstat", "--name-status", base_ref]
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Git command failed: {result.stderr}")
                return []

            changes = []
            lines = result.stdout.strip().split("\n")

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split("\t")
                if len(parts) >= 3:
                    try:
                        added = int(parts[0]) if parts[0] != "-" else 0
                        removed = int(parts[1]) if parts[1] != "-" else 0
                        status = parts[2][:1]  # M, A, D, etc.
                        file_path = parts[3] if len(parts) > 3 else parts[2][1:]

                        changes.append(
                            FileChange(path=file_path, status=status, lines_added=added, lines_removed=removed)
                        )
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Skipping malformed line: {line} ({e})")
                        continue

            logger.info(f"📋 Found {len(changes)} changed files")
            return changes

        except Exception as e:
            logger.error(f"Failed to get git changes: {e}")
            return []

    def classify_file_concern(self, file_path: str) -> str:
        """Classify a file into a concern category"""
        for concern, patterns in self.concern_patterns.items():
            for pattern in patterns:
                if re.match(pattern, file_path, re.IGNORECASE):
                    return concern

        # Special cases based on directory structure
        if file_path.startswith("candidate/"):
            return "labs"
        elif file_path.startswith("core/"):
            return "core"
        elif file_path.startswith("matriz/"):
            return "matriz"
        elif file_path.startswith("tools/"):
            # Further classify tools
            if "test" in file_path:
                return "testing"
            elif "ci" in file_path or "automation" in file_path:
                return "ci"
            elif "dashboard" in file_path or "monitor" in file_path:
                return "dashboard"
            else:
                return "tools"

        return "misc"

    def group_changes_by_concern(self, changes: list[FileChange]) -> dict[str, ConcernGroup]:
        """Group file changes by concern area"""
        logger.info("🏷️ Classifying files by concern...")

        # Classify each file
        for change in changes:
            change.concern = self.classify_file_concern(change.path)

        # Group by concern
        concern_files = defaultdict(list)
        for change in changes:
            concern_files[change.concern].append(change)

        # Create concern groups
        groups = {}
        for concern, files in concern_files.items():
            description = self.concern_descriptions.get(concern, f"{concern.title()} related changes")

            groups[concern] = ConcernGroup(name=concern, description=description, files=files)

        logger.info(f"📊 Grouped into {len(groups)} concern areas")
        return groups

    def analyze_dependencies(self, groups: dict[str, ConcernGroup]) -> dict[str, ConcernGroup]:
        """Analyze dependencies between concern groups"""
        logger.info("🔗 Analyzing inter-concern dependencies...")

        # Simple heuristic-based dependency analysis
        dependency_rules = {
            "schemas": [],  # Usually independent
            "config": [],  # Usually independent
            "contracts": ["schemas"],  # May depend on schemas
            "ci": ["testing", "dashboard"],  # Uses testing and dashboard
            "dashboard": ["contracts", "schemas"],  # May use contracts and schemas
            "testing": ["contracts", "schemas"],  # Tests use contracts and schemas
            "discovery": ["schemas"],  # May use schemas
            "docs": [],  # Usually independent
        }

        for concern_name, group in groups.items():
            # Add rule-based dependencies
            if concern_name in dependency_rules:
                for dep in dependency_rules[concern_name]:
                    if dep in groups and dep not in group.dependencies:
                        group.dependencies.append(dep)

            # Analyze file imports for dependencies (simplified)
            for file_change in group.files:
                if file_change.path.endswith(".py"):
                    deps = self._analyze_file_imports(file_change.path)
                    for dep in deps:
                        dep_concern = self.classify_file_concern(dep)
                        if dep_concern != concern_name and dep_concern in groups:
                            if dep_concern not in group.dependencies:
                                group.dependencies.append(dep_concern)

        return groups

    def _analyze_file_imports(self, file_path: str) -> list[str]:
        """Analyze imports in a Python file to detect dependencies"""
        try:
            full_path = ROOT / file_path
            if not full_path.exists():
                return []

            content = full_path.read_text(errors="ignore")
            imports = []

            # Simple regex-based import detection
            import_patterns = [r"from\s+(\S+)\s+import", r"import\s+(\S+)"]

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)

            # Convert to file paths (simplified)
            file_deps = []
            for imp in imports[:10]:  # Limit analysis
                # Convert module path to file path
                file_path_guess = imp.replace(".", "/") + ".py"
                if (ROOT / file_path_guess).exists():
                    file_deps.append(file_path_guess)

            return file_deps

        except Exception as e:
            logger.debug(f"Import analysis failed for {file_path}: {e}")
            return []

    def generate_pr_templates(self, groups: dict[str, ConcernGroup]) -> dict[str, ConcernGroup]:
        """Generate PR templates for each concern group"""
        logger.info("📝 Generating PR templates...")

        for group in groups.values():
            template = f"""# {group.description}

## Summary
This PR contains {group.description.lower()} with {len(group.files)} file changes.

## Changes
"""

            # List files by change type
            added_files = [f for f in group.files if f.status == "A"]
            modified_files = [f for f in group.files if f.status == "M"]
            deleted_files = [f for f in group.files if f.status == "D"]

            if added_files:
                template += "\n### ✅ Added Files\n"
                for f in added_files[:10]:  # Limit list
                    template += f"- `{f.path}` (+{f.lines_added} lines)\n"

            if modified_files:
                template += "\n### 📝 Modified Files\n"
                for f in modified_files[:10]:  # Limit list
                    template += f"- `{f.path}` (+{f.lines_added}/-{f.lines_removed} lines)\n"

            if deleted_files:
                template += "\n### ❌ Deleted Files\n"
                for f in deleted_files[:10]:  # Limit list
                    template += f"- `{f.path}`\n"

            if len(group.files) > 10:
                template += f"\n... and {len(group.files) - 10} more files\n"

            # Add dependencies
            if group.dependencies:
                template += f"\n## Dependencies\nThis PR depends on: {', '.join(group.dependencies)}\n"

            # Add risk assessment
            template += f"""
## Risk Assessment
- **Risk Level**: {group.risk_level}
- **Total Lines Changed**: {group.total_lines}
- **Files Changed**: {len(group.files)}

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated if needed
- [ ] Breaking changes documented

Generated by concern-based commit splitter.
"""

            group.pr_template = template

        return groups

    def create_concern_branches_and_prs(
        self, groups: dict[str, ConcernGroup], base_branch: str = "main"
    ) -> dict[str, dict]:
        """Create separate branches and PRs for each concern group"""
        logger.info("🌿 Creating concern-based branches and PRs...")

        results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for concern_name, group in groups.items():
            branch_name = f"concern/{concern_name}-{timestamp}"
            pr_title = f"{concern_name}: {group.description}"

            try:
                # Create branch
                subprocess.run(["git", "checkout", "-b", branch_name], cwd=ROOT, check=True, capture_output=True)

                # Add only files for this concern
                file_paths = [f.path for f in group.files]
                for file_path in file_paths:
                    subprocess.run(["git", "add", file_path], cwd=ROOT, check=True, capture_output=True)

                # Create commit
                commit_msg = f"{concern_name}: {group.description}\n\n{len(group.files)} files changed, {group.total_lines} lines"
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT, check=True, capture_output=True)

                # Push branch
                subprocess.run(["git", "push", "origin", branch_name], cwd=ROOT, check=True, capture_output=True)

                results[concern_name] = {
                    "branch": branch_name,
                    "status": "success",
                    "files": len(group.files),
                    "lines": group.total_lines,
                    "pr_title": pr_title,
                    "pr_template": group.pr_template,
                }

                logger.info(f"✅ Created branch {branch_name} for {concern_name}")

            except subprocess.CalledProcessError as e:
                results[concern_name] = {
                    "branch": branch_name,
                    "status": "failed",
                    "error": str(e),
                    "files": len(group.files),
                    "lines": group.total_lines,
                }

                logger.error(f"❌ Failed to create branch for {concern_name}: {e}")

                # Try to clean up
                try:
                    subprocess.run(["git", "checkout", base_branch], cwd=ROOT, capture_output=True)
                    subprocess.run(["git", "branch", "-D", branch_name], cwd=ROOT, capture_output=True)
                except:
                    pass

        return results

    def save_analysis_report(self, groups: dict[str, ConcernGroup], results: dict[str, dict]):
        """Save concern analysis report"""
        reports_dir = ROOT / "reports" / "git"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_concerns": len(groups),
            "total_files": sum(len(g.files) for g in groups.values()),
            "total_lines": sum(g.total_lines for g in groups.values()),
            "concern_groups": {name: asdict(group) for name, group in groups.items()},
            "branch_results": results,
        }

        # Save report
        report_file = reports_dir / "concern-analysis.json"
        report_file.write_text(json.dumps(report, indent=2))

        # Save summary
        summary_file = reports_dir / "concern-summary.md"
        self._generate_summary_markdown(groups, results, summary_file)

        logger.info(f"💾 Analysis report saved to {report_file}")

    def _generate_summary_markdown(self, groups: dict[str, ConcernGroup], results: dict[str, dict], output_file: Path):
        """Generate markdown summary"""
        content = f"""# Concern-Based Commit Analysis

**Generated**: {datetime.now().isoformat()}

## Summary
- **Total Concern Areas**: {len(groups)}
- **Total Files Changed**: {sum(len(g.files) for g in groups.values())}
- **Total Lines Changed**: {sum(g.total_lines for g in groups.values())}

## Concern Groups

| Concern | Files | Lines | Risk | Dependencies |
|---------|-------|-------|------|--------------|
"""

        for name, group in groups.items():
            deps = ", ".join(group.dependencies) if group.dependencies else "None"
            content += f"| {name} | {len(group.files)} | {group.total_lines} | {group.risk_level} | {deps} |\n"

        content += "\n## Branch Creation Results\n\n"

        for concern, result in results.items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            content += f"- {status_icon} **{concern}**: {result['status']}"
            if result["status"] == "success":
                content += f" (branch: `{result['branch']}`)"
            content += "\n"

        content += """
## Next Steps
1. Review each concern-based PR individually
2. Address any dependencies between PRs
3. Merge PRs in dependency order
4. Verify integration after all merges

Generated by concern-based commit splitter.
"""

        output_file.write_text(content)


def main():
    """CLI interface for concern splitter"""
    import argparse

    parser = argparse.ArgumentParser(description="Concern-based commit splitter")
    parser.add_argument("--base", default="HEAD~1", help="Base reference for git diff (default: HEAD~1)")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't create branches")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create splitter
    splitter = ConcernSplitter()

    # Get changes
    changes = splitter.get_git_changes(args.base)
    if not changes:
        logger.info("No changes found")
        return 0

    # Group by concern
    groups = splitter.group_changes_by_concern(changes)

    # Analyze dependencies
    groups = splitter.analyze_dependencies(groups)

    # Generate PR templates
    groups = splitter.generate_pr_templates(groups)

    # Print analysis
    print("\n📊 CONCERN ANALYSIS")
    print("=" * 40)
    for name, group in groups.items():
        print(f"{name}: {len(group.files)} files, {group.total_lines} lines ({group.risk_level} risk)")
        if group.dependencies:
            print(f"  Dependencies: {', '.join(group.dependencies)}")

    results = {}

    if not args.analyze_only:
        # Create branches and PRs
        results = splitter.create_concern_branches_and_prs(groups)

    # Save analysis
    splitter.save_analysis_report(groups, results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
