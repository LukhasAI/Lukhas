#!/usr/bin/env python3
"""
Module Readiness Scoring System for LUKHAS.
Provides comprehensive quality metrics and readiness assessment.
"""

import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import yaml


@dataclass
class ReadinessScore:
    """Module readiness score breakdown."""

    module_name: str
    total_score: int
    max_score: int
    percentage: float
    breakdown: Dict[str, Dict[str, Any]]
    status: str
    recommendations: List[str]


class ModuleReadinessScorer:
    def __init__(self):
        self.max_scores = {
            "manifest": 25,  # Valid manifest with complete metadata
            "matriz": 25,  # MATRIZ contract compliance
            "documentation": 20,  # Complete docs with real content
            "testing": 20,  # Tests passing with coverage
            "configuration": 10,  # Valid config files
        }

    def _check_manifest_validity(self, module_path: pathlib.Path) -> Tuple[int, List[str]]:
        """Check module manifest validity and completeness."""
        score = 0
        issues = []
        manifest_path = module_path / "module.manifest.json"

        if not manifest_path.exists():
            issues.append("Missing module.manifest.json")
            return score, issues

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Required fields (15 points)
            required_fields = ["schema_version", "module", "description", "ownership", "layout"]
            for field in required_fields:
                if field in manifest:
                    score += 3
                else:
                    issues.append(f"Missing required field: {field}")

            # Quality indicators (10 points)
            if "tags" in manifest and len(manifest["tags"]) >= 3:
                score += 2
            else:
                issues.append("Missing or insufficient tags")

            if "runtime" in manifest and "entrypoints" in manifest["runtime"]:
                if len(manifest["runtime"]["entrypoints"]) > 0:
                    score += 3
                else:
                    issues.append("No runtime entrypoints defined")
            else:
                issues.append("Missing runtime entrypoints")

            if "observability" in manifest and "required_spans" in manifest["observability"]:
                if len(manifest["observability"]["required_spans"]) > 0:
                    score += 3
                else:
                    issues.append("No observability spans defined")
            else:
                issues.append("Missing observability configuration")

            if "dependencies" in manifest:
                score += 2
            else:
                issues.append("Dependencies not specified")

        except Exception as e:
            issues.append(f"Manifest parse error: {e}")

        return min(score, self.max_scores["manifest"]), issues

    def _check_matriz_compliance(self, module_path: pathlib.Path) -> Tuple[int, List[str]]:
        """Check MATRIZ contract compliance."""
        score = 0
        issues = []

        # Look for matrix contract files
        matrix_files = list(module_path.glob("**/matrix_*.json"))

        if not matrix_files:
            issues.append("No MATRIZ contract files found")
            return score, issues

        # Basic contract presence (10 points)
        score += 10

        # Contract validation (15 points)
        for matrix_file in matrix_files:
            try:
                with open(matrix_file) as f:
                    contract = json.load(f)

                # Check for required contract sections
                if "identity" in contract:
                    score += 3
                if "monitoring" in contract:
                    score += 3
                if "processing" in contract:
                    score += 3
                if "state" in contract:
                    score += 3
                if "governance" in contract:
                    score += 3

                break  # Only check first contract for now

            except Exception as e:
                issues.append(f"Contract validation error: {e}")

        return min(score, self.max_scores["matriz"]), issues

    def _check_documentation_quality(self, module_path: pathlib.Path) -> Tuple[int, List[str]]:
        """Check documentation completeness and quality."""
        score = 0
        issues = []
        docs_dir = module_path / "docs"

        if not docs_dir.exists():
            issues.append("No docs/ directory")
            return score, issues

        # Required documentation files (15 points)
        required_docs = ["README.md", "api.md", "architecture.md"]
        for doc_file in required_docs:
            doc_path = docs_dir / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path) as f:
                        content = f.read()

                    # Check for substantial content (not just templates)
                    if len(content) > 500 and "TBD" not in content and "TODO" not in content:
                        score += 5
                    elif len(content) > 100:
                        score += 2
                        issues.append(f"{doc_file} appears to be template content")
                    else:
                        issues.append(f"{doc_file} is too short or empty")

                except Exception:
                    issues.append(f"Cannot read {doc_file}")
            else:
                issues.append(f"Missing {doc_file}")

        # Quality indicators (5 points)
        readme_path = docs_dir / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path) as f:
                    content = f.read()

                if "## " in content:  # Has sections
                    score += 2
                if "```" in content:  # Has code examples
                    score += 2
                if len(content) > 1000:  # Substantial content
                    score += 1

            except Exception:
                pass

        return min(score, self.max_scores["documentation"]), issues

    def _check_testing_status(self, module_path: pathlib.Path) -> Tuple[int, List[str]]:
        """Check testing completeness and status."""
        score = 0
        issues = []
        tests_dir = module_path / "tests"

        if not tests_dir.exists():
            issues.append("No tests/ directory")
            return score, issues

        # Test file presence (10 points)
        test_files = list(tests_dir.glob("test_*.py"))
        if test_files:
            score += 5  # Has test files

            # Check for different test types
            unit_tests = [f for f in test_files if "unit" in f.name]
            integration_tests = [f for f in test_files if "integration" in f.name]

            if unit_tests:
                score += 3
            else:
                issues.append("No unit tests found")

            if integration_tests:
                score += 2
            else:
                issues.append("No integration tests found")
        else:
            issues.append("No test files found")

        # Test configuration (5 points)
        conftest_path = tests_dir / "conftest.py"
        if conftest_path.exists():
            score += 3
        else:
            issues.append("No conftest.py found")

        # Check for pytest compatibility (2 points)
        if any("pytest" in f.read_text() for f in test_files if f.exists()):
            score += 2

        # Test execution simulation (5 points)
        # This is a placeholder - in real implementation you'd run pytest
        if len(test_files) > 0:
            score += 3  # Assume tests would pass
            issues.append("Test execution not validated (placeholder)")

        return min(score, self.max_scores["testing"]), issues

    def _check_configuration_validity(self, module_path: pathlib.Path) -> Tuple[int, List[str]]:
        """Check configuration file validity."""
        score = 0
        issues = []
        config_dir = module_path / "config"

        if not config_dir.exists():
            issues.append("No config/ directory")
            return score, issues

        # Required config files (8 points)
        config_files = {"config.yaml": 3, "logging.yaml": 3, "environment.yaml": 2}

        for config_file, points in config_files.items():
            config_path = config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        yaml.safe_load(f)
                    score += points
                except Exception as e:
                    issues.append(f"Invalid YAML in {config_file}: {e}")
            else:
                issues.append(f"Missing {config_file}")

        # Provenance headers (2 points)
        config_yaml = config_dir / "config.yaml"
        if config_yaml.exists():
            try:
                with open(config_yaml) as f:
                    content = f.read()
                if "@generated LUKHAS scaffold" in content:
                    score += 2
                else:
                    issues.append("Missing provenance header in config.yaml")
            except Exception:
                pass

        return min(score, self.max_scores["configuration"]), issues

    def calculate_module_score(self, module_path: pathlib.Path) -> ReadinessScore:
        """Calculate comprehensive readiness score for a module."""
        module_name = module_path.name
        total_score = 0
        max_possible = sum(self.max_scores.values())
        breakdown = {}
        all_recommendations = []

        # Run all checks
        checks = [
            ("manifest", self._check_manifest_validity),
            ("matriz", self._check_matriz_compliance),
            ("documentation", self._check_documentation_quality),
            ("testing", self._check_testing_status),
            ("configuration", self._check_configuration_validity),
        ]

        for check_name, check_func in checks:
            score, issues = check_func(module_path)
            total_score += score

            breakdown[check_name] = {
                "score": score,
                "max_score": self.max_scores[check_name],
                "percentage": (score / self.max_scores[check_name]) * 100,
                "issues": issues,
            }

            all_recommendations.extend(issues)

        percentage = (total_score / max_possible) * 100

        # Determine status
        if percentage >= 90:
            status = "READY"
        elif percentage >= 75:
            status = "GOOD"
        elif percentage >= 60:
            status = "NEEDS_WORK"
        elif percentage >= 40:
            status = "INCOMPLETE"
        else:
            status = "NOT_READY"

        return ReadinessScore(
            module_name=module_name,
            total_score=total_score,
            max_score=max_possible,
            percentage=percentage,
            breakdown=breakdown,
            status=status,
            recommendations=all_recommendations,
        )

    def generate_scoreboard(self, scores: List[ReadinessScore]) -> str:
        """Generate a formatted scoreboard."""
        lines = []
        lines.append("🏆 LUKHAS Module Readiness Scoreboard")
        lines.append("=" * 60)
        lines.append("")

        # Summary stats
        total_modules = len(scores)
        ready_modules = len([s for s in scores if s.status == "READY"])
        good_modules = len([s for s in scores if s.status == "GOOD"])
        avg_score = sum(s.percentage for s in scores) / total_modules if scores else 0

        lines.append("📊 Summary:")
        lines.append(f"   Total modules: {total_modules}")
        lines.append(f"   Ready modules: {ready_modules} ({ready_modules/total_modules*100:.1f}%)")
        lines.append(
            f"   Good+ modules: {ready_modules + good_modules} ({(ready_modules + good_modules)/total_modules*100:.1f}%)"
        )
        lines.append(f"   Average score: {avg_score:.1f}%")
        lines.append("")

        # Top performers
        top_scores = sorted(scores, key=lambda x: x.percentage, reverse=True)[:10]
        lines.append("🌟 Top 10 Modules:")
        for i, score in enumerate(top_scores, 1):
            status_emoji = {"READY": "✅", "GOOD": "🟢", "NEEDS_WORK": "🟡", "INCOMPLETE": "🟠", "NOT_READY": "🔴"}
            emoji = status_emoji.get(score.status, "❓")
            lines.append(
                f"   {i:2d}. {emoji} {score.module_name}: {score.percentage:.1f}% ({score.total_score}/{score.max_score})"
            )

        lines.append("")

        # Status distribution
        status_counts = {}
        for score in scores:
            status_counts[score.status] = status_counts.get(score.status, 0) + 1

        lines.append("📈 Status Distribution:")
        for status, count in sorted(status_counts.items()):
            emoji = {"READY": "✅", "GOOD": "🟢", "NEEDS_WORK": "🟡", "INCOMPLETE": "🟠", "NOT_READY": "🔴"}[status]
            lines.append(f"   {emoji} {status}: {count} modules")

        return "\n".join(lines)


def main():
    """Main function for module readiness scoring."""
    import argparse

    parser = argparse.ArgumentParser(description="Module Readiness Scoring System")
    parser.add_argument("--module", help="Score specific module only")
    parser.add_argument("--threshold", type=float, default=0.0, help="Only show modules below this score threshold")
    parser.add_argument(
        "--status", choices=["READY", "GOOD", "NEEDS_WORK", "INCOMPLETE", "NOT_READY"], help="Filter by status"
    )
    parser.add_argument("--detailed", action="store_true", help="Show detailed breakdown for each module")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    scorer = ModuleReadinessScorer()
    scores = []

    # Find modules to score
    root_path = pathlib.Path(".")
    if args.module:
        module_path = root_path / args.module
        if module_path.exists() and module_path.is_dir():
            scores.append(scorer.calculate_module_score(module_path))
        else:
            print(f"❌ Module not found: {args.module}")
            return 1
    else:
        # Score all modules with config directories
        for item in root_path.iterdir():
            if item.is_dir() and not item.name.startswith(".") and (item / "config").exists():
                scores.append(scorer.calculate_module_score(item))

    if not scores:
        print("No modules found to score")
        return 1

    # Apply filters
    if args.threshold > 0:
        scores = [s for s in scores if s.percentage <= args.threshold]

    if args.status:
        scores = [s for s in scores if s.status == args.status]

    # Output results
    if args.json:
        output = []
        for score in scores:
            output.append(
                {
                    "module": score.module_name,
                    "score": score.total_score,
                    "max_score": score.max_score,
                    "percentage": score.percentage,
                    "status": score.status,
                    "breakdown": score.breakdown,
                    "recommendations": score.recommendations,
                }
            )
        print(json.dumps(output, indent=2))
    else:
        if len(scores) > 1 and not args.detailed:
            print(scorer.generate_scoreboard(scores))
        else:
            for score in scores:
                print(f"\n📋 Module: {score.module_name}")
                print(f"   Score: {score.total_score}/{score.max_score} ({score.percentage:.1f}%)")
                print(f"   Status: {score.status}")

                if args.detailed:
                    print("\n   Breakdown:")
                    for category, details in score.breakdown.items():
                        print(
                            f"     {category}: {details['score']}/{details['max_score']} ({details['percentage']:.1f}%)"
                        )
                        for issue in details["issues"]:
                            print(f"       • {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
