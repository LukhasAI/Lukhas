#!/usr/bin/env python3
"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


LUKHAS PWM Isolated Files Assessment
Analyzes isolated files to identify valuable prototypes vs archive candidates
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class IsolatedFilesAssessor:
    def __init__(self):
        self.valuable_keywords = [
            "prototype",
            "experiment",
            "test",
            "demo",
            "poc",
            "proof",
            "research",
            "algorithm",
            "model",
            "engine",
            "processor",
            "analyzer",
            "generator",
            "optimizer",
            "transformer",
            "lukhas",
            "agi",
            "consciousness",
            "quantum",
            "bio",
            "emotion",
            "dream",
            "memory",
            "identity",
            "symbolic",
        ]

        self.archive_indicators = [
            "old",
            "backup",
            "temp",
            "tmp",
            "draft",
            "unused",
            "deprecated",
            "legacy",
            "test_",
            "_test",
            "example",
            "sample",
            "debug",
            "mock",
            "dummy",
            "placeholder",
        ]

    def assess_files(self, connectivity_report_path: str) -> Dict[str, Any]:
        """Assess isolated files from connectivity report"""
        # Load connectivity report
        with open(connectivity_report_path) as f:
            report = json.load(f)

        isolated_files = report.get("isolated_files", [])
        print(f"🔍 Assessing {len(isolated_files)} isolated files...")

        assessment = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_isolated": len(isolated_files),
            "valuable_prototypes": [],
            "archive_candidates": [],
            "syntax_errors": [],
            "needs_review": [],
        }

        for file_info in isolated_files:
            file_path = Path(file_info["file"])

            # Skip archive and backup directories
            if ".pwm_cleanup_archive" in str(file_path) or "BACKUP" in str(file_path):
                continue

            category = self._categorize_file(file_path, file_info)

            file_data = {
                "path": str(file_path),
                "lines": file_info["lines_of_code"],
                "size": file_info["file_size"],
                "has_class": file_info.get("has_class", False),
                "has_function": file_info.get("has_function", False),
                "reason": category["reason"],
            }

            if category["category"] == "valuable":
                assessment["valuable_prototypes"].append(file_data)
            elif category["category"] == "archive":
                assessment["archive_candidates"].append(file_data)
            elif category["category"] == "syntax_error":
                assessment["syntax_errors"].append(file_data)
            else:
                assessment["needs_review"].append(file_data)

        return assessment

    def _categorize_file(self, file_path: Path, file_info: Dict) -> Dict[str, str]:
        """Categorize a single file"""
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()

        # Check if it's a syntax error file (no class/function detected)
        if not file_info.get("has_class") and not file_info.get("has_function"):
            if file_info["lines_of_code"] > 50:  # Substantial file with parsing issues
                return {
                    "category": "syntax_error",
                    "reason": "Parsing failed - syntax errors",
                }

        # Check for valuable keywords
        valuable_score = sum(
            1 for keyword in self.valuable_keywords if keyword in path_str
        )

        # Check for archive indicators
        archive_score = sum(
            1 for indicator in self.archive_indicators if indicator in path_str
        )

        # Special cases
        if "tools/" in str(file_path):
            if any(
                k in file_name for k in ["analyzer", "auditor", "scanner", "resolver"]
            ):
                return {
                    "category": "valuable",
                    "reason": "Analysis/audit tool prototype",
                }
            elif "test" in file_name and file_info["lines_of_code"] > 100:
                return {"category": "valuable", "reason": "Test framework prototype"}

        # Decision logic
        if valuable_score > archive_score and valuable_score > 0:
            return {
                "category": "valuable",
                "reason": f"Contains valuable keywords (score: {valuable_score})",
            }
        elif archive_score > valuable_score:
            return {
                "category": "archive",
                "reason": f"Archive indicators found (score: {archive_score})",
            }
        elif file_info["lines_of_code"] < 50:
            return {"category": "archive", "reason": "Small file with no connectivity"}
        else:
            return {"category": "review", "reason": "Needs manual review"}


def main():
    assessor = IsolatedFilesAssessor()

    # Use the current connectivity analysis
    report_path = "docs/reports/analysis/PWM_CURRENT_CONNECTIVITY_ANALYSIS.json"

    assessment = assessor.assess_files(report_path)

    # Save assessment
    output_path = Path("docs/reports/analysis/ISOLATED_FILES_ASSESSMENT.json")
    with open(output_path, "w") as f:
        json.dump(assessment, f, indent=2)

    # Print summary
    print("\n📊 ASSESSMENT SUMMARY:")
    print(f"   Total isolated files: {assessment['total_isolated']}")
    print(f"   Valuable prototypes: {len(assessment['valuable_prototypes'])}")
    print(f"   Archive candidates: {len(assessment['archive_candidates'])}")
    print(f"   Syntax errors: {len(assessment['syntax_errors'])}")
    print(f"   Needs review: {len(assessment['needs_review'])}")

    # Show valuable prototypes
    if assessment["valuable_prototypes"]:
        print("\n✨ VALUABLE PROTOTYPES:")
        for proto in assessment["valuable_prototypes"][:10]:
            print(f"   - {proto['path']} ({proto['lines']} lines) - {proto['reason']}")

    # Show archive candidates
    if assessment["archive_candidates"]:
        print("\n📦 ARCHIVE CANDIDATES:")
        for arch in assessment["archive_candidates"][:10]:
            print(f"   - {arch['path']} ({arch['lines']} lines) - {arch['reason']}")

    print(f"\n📄 Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
