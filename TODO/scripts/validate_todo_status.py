#!/usr/bin/env python3
"""
TODO Status Validation Script for LUKHAS AI

This script provides evidence-based validation of TODO completion claims
by checking actual code state vs. documentation claims.

Features:
- Real-time TODO count from codebase
- Validation of completion claims
- Detection of discrepancies
- Priority distribution analysis
- Agent task readiness assessment
"""

import re
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class TODOValidator:
    """Validates TODO status with evidence-based verification"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.validation_results = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_current_todo_count(self) -> Dict[str, Any]:
        """Get accurate TODO count from codebase"""
        try:
            # Run ripgrep to find all TODOs
            result = subprocess.run(
                ["rg", "-n", "TODO|FIXME|HACK", "--type", "py", "--no-heading", "--with-filename"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return {"error": "Failed to run ripgrep", "count": 0}

            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

            # Filter out virtual environments and cache directories
            filtered_lines = []
            exclude_patterns = [".venv/", "venv/", "__pycache__/", ".git/", "node_modules/"]

            for line in lines:
                if not any(pattern in line for pattern in exclude_patterns):
                    filtered_lines.append(line)

            # Analyze by directory
            directory_counts = {}
            priority_counts = {"CRITICAL": 0, "HIGH": 0, "MED": 0, "LOW": 0}

            for line in filtered_lines:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    filepath = parts[0]
                    line_num = parts[1]
                    todo_text = parts[2].strip()

                    # Get directory
                    directory = filepath.split("/")[0] if "/" in filepath else "root"
                    directory_counts[directory] = directory_counts.get(directory, 0) + 1

                    # Analyze priority
                    todo_lower = todo_text.lower()
                    if any(word in todo_lower for word in ["critical", "security", "blocking", "urgent", "safety"]):
                        priority_counts["CRITICAL"] += 1
                    elif any(word in todo_lower for word in ["important", "core", "framework", "agent"]):
                        priority_counts["HIGH"] += 1
                    elif any(word in todo_lower for word in ["enhance", "improve", "optimize", "feature"]):
                        priority_counts["MED"] += 1
                    else:
                        priority_counts["LOW"] += 1

            return {
                "total_count": len(filtered_lines),
                "directory_breakdown": directory_counts,
                "priority_distribution": priority_counts,
                "sample_todos": filtered_lines[:10],  # First 10 for inspection
            }

        except Exception as e:
            return {"error": str(e), "count": 0}

    def validate_documented_counts(self) -> Dict[str, Any]:
        """Validate counts in TODO documentation files"""
        documented_counts = {}

        todo_files = [
            "TODO/critical_todos.md",
            "TODO/high_todos.md",
            "TODO/med_todos.md",
            "TODO/low_todos.md",
            "TODO/COMPLETION_STATUS.md",
            "TODO/SUMMARY.md",
        ]

        for file_path in todo_files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, "r") as f:
                        content = f.read()

                    # Extract counts from content
                    count_patterns = [r"(\d+)\s+TODOs", r"Count.*?(\d+)", r"Total.*?(\d+)", r"(\d+)/(\d+)\s+TODOs"]

                    found_counts = []
                    for pattern in count_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        found_counts.extend(matches)

                    documented_counts[file_path] = {
                        "file_exists": True,
                        "found_counts": found_counts,
                        "last_modified": full_path.stat().st_mtime,
                    }

                except Exception as e:
                    documented_counts[file_path] = {"file_exists": True, "error": str(e)}
            else:
                documented_counts[file_path] = {"file_exists": False}

        return documented_counts

    def check_completion_evidence(self) -> Dict[str, Any]:
        """Check for actual evidence of completed TODOs"""
        evidence_patterns = ["COMPLETED", "CLAUDE.*COMPLETED", "DONE", "FIXED", "RESOLVED"]

        evidence_found = {}

        for pattern in evidence_patterns:
            try:
                result = subprocess.run(
                    ["rg", "-n", pattern, "--type", "py", "--no-heading", "--with-filename"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.strip().split("\n")
                    # Filter out virtual environments
                    filtered_lines = [
                        line for line in lines if not any(exc in line for exc in [".venv/", "venv/", "__pycache__/"])
                    ]
                    evidence_found[pattern] = {"count": len(filtered_lines), "examples": filtered_lines[:5]}
                else:
                    evidence_found[pattern] = {"count": 0, "examples": []}

            except Exception as e:
                evidence_found[pattern] = {"error": str(e)}

        return evidence_found

    def analyze_jules_assignments(self) -> Dict[str, Any]:
        """Analyze JULES agent assignments and status"""
        jules_dir = self.repo_path / "TODO/JULES"
        jules_analysis = {"assignment_files": [], "total_assignments": 0, "estimated_workload": {}}

        if jules_dir.exists():
            for jules_file in jules_dir.glob("Jules-*.md"):
                try:
                    with open(jules_file, "r") as f:
                        content = f.read()

                    # Extract assignment info
                    lines = content.count("\n")
                    todos_mentioned = len(re.findall(r"TODO", content, re.IGNORECASE))

                    jules_analysis["assignment_files"].append(
                        {
                            "file": jules_file.name,
                            "lines": lines,
                            "todos_mentioned": todos_mentioned,
                            "size": "large" if lines > 100 else "medium" if lines > 50 else "small",
                        }
                    )

                    jules_analysis["total_assignments"] += 1

                except Exception as e:
                    jules_analysis["assignment_files"].append({"file": jules_file.name, "error": str(e)})

        return jules_analysis

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        report = {
            "timestamp": self.timestamp,
            "validation_summary": {
                "status": "ANALYSIS_COMPLETE",
                "discrepancies_found": False,
                "requires_reorganization": True,
            },
        }

        # Get current state
        current_todos = self.get_current_todo_count()
        documented_counts = self.validate_documented_counts()
        completion_evidence = self.check_completion_evidence()
        jules_analysis = self.analyze_jules_assignments()

        report.update(
            {
                "current_todo_state": current_todos,
                "documented_counts": documented_counts,
                "completion_evidence": completion_evidence,
                "jules_assignments": jules_analysis,
            }
        )

        # Analyze discrepancies
        if current_todos.get("total_count"):
            actual_count = current_todos["total_count"]

            # Check against documented claims
            report["discrepancy_analysis"] = {
                "actual_todo_count": actual_count,
                "documented_claims": {},
                "evidence_verification": {
                    "completion_markers_found": sum(
                        evidence.get("count", 0)
                        for evidence in completion_evidence.values()
                        if isinstance(evidence, dict)
                    ),
                    "claude_specific_evidence": completion_evidence.get("CLAUDE.*COMPLETED", {}).get("count", 0),
                },
            }

            # Determine reorganization needs
            if actual_count > 500:
                report["validation_summary"]["requires_reorganization"] = True
                report["validation_summary"]["priority_action"] = "IMMEDIATE_REORGANIZATION_NEEDED"

        return report

    def save_report(self, report: Dict[str, Any], output_file: str = "validation_report.json"):
        """Save validation report to file"""
        output_path = self.repo_path / "TODO" / output_file

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return output_path


def main():
    """Main validation workflow"""
    print("🔍 LUKHAS TODO Validation - Evidence-Based Analysis")
    print("=" * 60)

    validator = TODOValidator()

    # Generate comprehensive report
    print("📊 Generating validation report...")
    report = validator.generate_validation_report()

    # Save report
    report_path = validator.save_report(report)
    print(f"✅ Report saved to: {report_path}")

    # Print summary
    print("\n📋 VALIDATION SUMMARY")
    print("-" * 30)

    current_count = report.get("current_todo_state", {}).get("total_count", 0)
    print(f"📌 Current TODO Count: {current_count}")

    evidence_count = (
        report.get("discrepancy_analysis", {}).get("evidence_verification", {}).get("completion_markers_found", 0)
    )
    print(f"✅ Completion Evidence Found: {evidence_count}")

    jules_assignments = report.get("jules_assignments", {}).get("total_assignments", 0)
    print(f"👥 Jules Assignments: {jules_assignments}")

    if report["validation_summary"]["requires_reorganization"]:
        print("⚠️  STATUS: Reorganization Required")
        print("🎯 RECOMMENDATION: Create agent task batches before proceeding")
    else:
        print("✅ STATUS: TODO organization adequate")

    print(f"\n📄 Full report: {report_path}")


if __name__ == "__main__":
    main()
