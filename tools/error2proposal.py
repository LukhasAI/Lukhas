#!/usr/bin/env python3
"""
Test Failure to Proposal Converter

Parses pytest log output and generates actionable proposals for fixing test failures.
Identifies patterns in failures (missing dependencies, import errors, config issues)
and generates structured proposals with confidence scores.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TestFailure:
    """Represents a single test failure"""

    test_file: str
    error_type: str
    error_message: str
    traceback: list[str] = field(default_factory=list)
    markers: list[str] = field(default_factory=list)


@dataclass
class Proposal:
    """Represents a fix proposal for test failures"""

    id: str
    title: str
    description: str
    fix_type: str
    affected_files: list[str]
    confidence: float
    patch_content: str | None = None
    runbook_reference: str | None = None
    priority: str = "medium"
    estimated_effort: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ProposalReport:
    """Report of all proposals generated"""

    total_failures: int = 0
    unique_error_types: int = 0
    proposals_generated: int = 0
    high_confidence_proposals: int = 0
    proposals: list[Proposal] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_failures": self.total_failures,
            "unique_error_types": self.unique_error_types,
            "proposals_generated": self.proposals_generated,
            "high_confidence_proposals": self.high_confidence_proposals,
            "proposals": [p.to_dict() for p in self.proposals],
        }


class TestFailureParser:
    """Parses pytest output to extract test failures"""

    def __init__(self):
        self.failures: list[TestFailure] = []

    def parse_file(self, file_path: Path) -> list[TestFailure]:
        """Parse pytest output file"""
        logger.info(f"Parsing test results from {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []

        self.failures = self._extract_failures(content)
        logger.info(f"Found {len(self.failures)} test failures")
        return self.failures

    def _extract_failures(self, content: str) -> list[TestFailure]:
        """Extract test failures from pytest output"""
        failures = []

        # Split by error sections
        error_pattern = r"_ ERROR collecting ([^\s]+) _"
        sections = re.split(error_pattern, content)

        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                test_file = sections[i].strip()
                error_content = sections[i + 1]

                failure = self._parse_error_section(test_file, error_content)
                if failure:
                    failures.append(failure)

        # Also check for FAILED sections
        failed_pattern = r"FAILED ([^\s]+) - (.+)"
        for match in re.finditer(failed_pattern, content):
            test_file = match.group(1).strip()
            error_msg = match.group(2).strip()

            failures.append(
                TestFailure(
                    test_file=test_file,
                    error_type="TestFailure",
                    error_message=error_msg,
                    traceback=[],
                )
            )

        return failures

    def _parse_error_section(self, test_file: str, content: str) -> TestFailure | None:
        """Parse an individual error section"""
        # Extract error type
        error_type = "UnknownError"
        error_message = ""
        traceback = []

        # Look for ModuleNotFoundError
        module_not_found = re.search(
            r"E\s+ModuleNotFoundError: No module named '([^']+)'", content
        )
        if module_not_found:
            error_type = "ModuleNotFoundError"
            error_message = f"No module named '{module_not_found.group(1)}'"

        # Look for ImportError
        import_error = re.search(r"E\s+ImportError: (.+)", content)
        if import_error:
            error_type = "ImportError"
            error_message = import_error.group(1).strip()

        # Look for AttributeError
        attr_error = re.search(r"E\s+AttributeError: (.+)", content)
        if attr_error:
            error_type = "AttributeError"
            error_message = attr_error.group(1).strip()

        # Look for AssertionError
        assertion_error = re.search(r"E\s+AssertionError: (.+)", content)
        if assertion_error:
            error_type = "AssertionError"
            error_message = assertion_error.group(1).strip()

        # Extract traceback
        traceback_lines = re.findall(r"^[^\s].*:\d+: in .+$", content, re.MULTILINE)
        traceback = traceback_lines[:5]  # Limit to first 5 lines

        if not error_message:
            # Try to extract any error line
            error_lines = re.findall(r"E\s+(.+)", content)
            if error_lines:
                error_message = error_lines[0].strip()

        return TestFailure(
            test_file=test_file,
            error_type=error_type,
            error_message=error_message,
            traceback=traceback,
        )


class ProposalGenerator:
    """Generates fix proposals from test failures"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.runbooks = self._load_runbooks()

    def _load_runbooks(self) -> dict[str, str]:
        """Load available runbooks"""
        runbooks = {}
        runbook_dirs = [
            self.repo_root / "docs" / "runbooks",
            self.repo_root / "docs" / "collaboration" / "runbooks",
        ]

        for runbook_dir in runbook_dirs:
            if runbook_dir.exists():
                for runbook_file in runbook_dir.glob("*.md"):
                    runbooks[runbook_file.stem] = str(runbook_file.relative_to(self.repo_root))

        return runbooks

    def generate_proposals(
        self, failures: list[TestFailure], filter_marker: str | None = None
    ) -> ProposalReport:
        """Generate proposals from test failures"""
        logger.info(f"Generating proposals from {len(failures)} failures")

        report = ProposalReport()
        report.total_failures = len(failures)

        # Filter by marker if specified
        if filter_marker:
            failures = [f for f in failures if filter_marker in f.markers]
            logger.info(f"Filtered to {len(failures)} failures with marker '{filter_marker}'")

        # Group failures by error type
        errors_by_type: dict[str, list[TestFailure]] = {}
        for failure in failures:
            key = f"{failure.error_type}:{failure.error_message}"
            if key not in errors_by_type:
                errors_by_type[key] = []
            errors_by_type[key].append(failure)

        report.unique_error_types = len(errors_by_type)

        # Generate proposals for each error type
        for error_key, error_failures in errors_by_type.items():
            proposal = self._create_proposal(error_key, error_failures)
            if proposal:
                report.proposals.append(proposal)
                if proposal.confidence >= 0.8:
                    report.high_confidence_proposals += 1

        report.proposals_generated = len(report.proposals)
        logger.info(
            f"Generated {report.proposals_generated} proposals "
            f"({report.high_confidence_proposals} high-confidence)"
        )

        return report

    def _create_proposal(self, error_key: str, failures: list[TestFailure]) -> Proposal | None:
        """Create a proposal for a specific error type"""
        error_type = failures[0].error_type
        error_message = failures[0].error_message
        affected_files = list({f.test_file for f in failures})

        # Generate proposal based on error type
        if error_type == "ModuleNotFoundError":
            return self._create_missing_dependency_proposal(error_message, affected_files)
        elif error_type == "ImportError":
            return self._create_import_error_proposal(error_message, affected_files)
        elif error_type == "AttributeError":
            return self._create_attribute_error_proposal(error_message, affected_files)
        elif error_type == "AssertionError":
            return self._create_assertion_error_proposal(error_message, affected_files)
        else:
            return self._create_generic_proposal(error_type, error_message, affected_files)

    def _create_missing_dependency_proposal(
        self, error_message: str, affected_files: list[str]
    ) -> Proposal:
        """Create proposal for missing dependency"""
        # Extract module name
        match = re.search(r"No module named '([^']+)'", error_message)
        module_name = match.group(1) if match else "unknown"

        # Map common module names to packages
        package_map = {
            "pydantic": "pydantic",
            "pytest": "pytest",
            "numpy": "numpy",
            "pandas": "pandas",
            "requests": "requests",
            "flask": "flask",
            "django": "django",
            "streamlit": "streamlit",
        }

        base_module = module_name.split(".")[0]
        package_name = package_map.get(base_module, base_module)

        proposal_id = f"dep-{package_name}-{len(affected_files)}"

        # Generate patch content
        patch_content = f"""# Add to requirements.txt or pyproject.toml
{package_name}

# Or install directly:
# uv pip install {package_name}
# pip install {package_name}
"""

        return Proposal(
            id=proposal_id,
            title=f"Add missing dependency: {package_name}",
            description=f"Tests are failing due to missing Python package '{package_name}'. "
            f"This affects {len(affected_files)} test file(s). "
            f"Add the package to project dependencies and install it.",
            fix_type="dependency",
            affected_files=affected_files,
            confidence=0.9,
            patch_content=patch_content,
            priority="high" if len(affected_files) > 5 else "medium",
            estimated_effort="low",
        )

    def _create_import_error_proposal(
        self, error_message: str, affected_files: list[str]
    ) -> Proposal:
        """Create proposal for import error"""
        proposal_id = f"import-error-{len(affected_files)}"

        return Proposal(
            id=proposal_id,
            title="Fix import error",
            description=f"Tests are failing due to import error: {error_message}. "
            f"This affects {len(affected_files)} test file(s). "
            f"Review the import statements and ensure modules are correctly structured.",
            fix_type="import",
            affected_files=affected_files,
            confidence=0.7,
            priority="medium",
            estimated_effort="medium",
        )

    def _create_attribute_error_proposal(
        self, error_message: str, affected_files: list[str]
    ) -> Proposal:
        """Create proposal for attribute error"""
        proposal_id = f"attr-error-{len(affected_files)}"

        return Proposal(
            id=proposal_id,
            title="Fix attribute error",
            description=f"Tests are failing due to attribute error: {error_message}. "
            f"This affects {len(affected_files)} test file(s). "
            f"Review the code to ensure attributes/methods exist and are accessible.",
            fix_type="attribute",
            affected_files=affected_files,
            confidence=0.6,
            priority="medium",
            estimated_effort="medium",
        )

    def _create_assertion_error_proposal(
        self, error_message: str, affected_files: list[str]
    ) -> Proposal:
        """Create proposal for assertion error"""
        proposal_id = f"assertion-{len(affected_files)}"

        return Proposal(
            id=proposal_id,
            title="Fix test assertion",
            description=f"Tests are failing due to assertion error: {error_message}. "
            f"This affects {len(affected_files)} test file(s). "
            f"Review test expectations and actual implementation to identify discrepancies.",
            fix_type="assertion",
            affected_files=affected_files,
            confidence=0.5,
            priority="low",
            estimated_effort="high",
        )

    def _create_generic_proposal(
        self, error_type: str, error_message: str, affected_files: list[str]
    ) -> Proposal:
        """Create generic proposal for unknown error type"""
        proposal_id = f"error-{error_type.lower()}-{len(affected_files)}"

        return Proposal(
            id=proposal_id,
            title=f"Fix {error_type}",
            description=f"Tests are failing due to {error_type}: {error_message}. "
            f"This affects {len(affected_files)} test file(s). "
            f"Review the affected tests and code to identify the root cause.",
            fix_type="generic",
            affected_files=affected_files,
            confidence=0.4,
            priority="medium",
            estimated_effort="medium",
        )


class Error2ProposalConverter:
    """Main converter class"""

    def __init__(self, repo_root: Path, output_dir: Path):
        self.repo_root = repo_root
        self.output_dir = output_dir
        self.parser = TestFailureParser()
        self.generator = ProposalGenerator(repo_root)

    def convert(
        self, test_results_file: Path, filter_marker: str | None = None, generate_patches: bool = True
    ) -> ProposalReport:
        """Convert test failures to proposals"""
        # Parse test failures
        failures = self.parser.parse_file(test_results_file)

        if not failures:
            logger.warning("No test failures found")
            return ProposalReport()

        # Generate proposals
        report = self.generator.generate_proposals(failures, filter_marker)

        # Save proposals
        self._save_report(report)

        # Generate patch files for high-confidence proposals
        if generate_patches:
            self._generate_patches(report)

        return report

    def _save_report(self, report: ProposalReport) -> None:
        """Save proposal report to JSON"""
        output_file = self.output_dir / "proposals.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info(f"Saved proposals to {output_file}")

    def _generate_patches(self, report: ProposalReport) -> None:
        """Generate patch files for high-confidence proposals"""
        patch_dir = self.output_dir / "patches"
        patch_dir.mkdir(parents=True, exist_ok=True)

        patches_generated = 0
        for proposal in report.proposals:
            if proposal.confidence >= 0.8 and proposal.patch_content:
                patch_file = patch_dir / f"{proposal.id}.patch"
                with open(patch_file, "w", encoding="utf-8") as f:
                    f.write(f"# Proposal: {proposal.title}\n")
                    f.write(f"# Confidence: {proposal.confidence}\n")
                    f.write(f"# Affected files: {len(proposal.affected_files)}\n\n")
                    f.write(proposal.patch_content)
                patches_generated += 1

        if patches_generated > 0:
            logger.info(f"Generated {patches_generated} patch files in {patch_dir}")


def main() -> None:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert test failures to actionable proposals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test-results",
        type=Path,
        default=Path("release_artifacts/test_results_summary.txt"),
        help="Path to pytest output file (default: release_artifacts/test_results_summary.txt)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("release_artifacts/proposals"),
        help="Output directory for proposals (default: release_artifacts/proposals)",
    )
    parser.add_argument(
        "--filter-marker",
        type=str,
        help="Filter tests by pytest marker (e.g., 'unit', 'integration')",
    )
    parser.add_argument(
        "--no-patches",
        action="store_true",
        help="Do not generate patch files for high-confidence proposals",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine repo root
    repo_root = Path(__file__).resolve().parents[1]

    # Convert test failures to proposals
    converter = Error2ProposalConverter(
        repo_root=repo_root, output_dir=args.output_dir
    )

    report = converter.convert(
        test_results_file=args.test_results,
        filter_marker=args.filter_marker,
        generate_patches=not args.no_patches,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("Test Failure to Proposal Conversion Summary")
    print("=" * 60)
    print(f"Total failures: {report.total_failures}")
    print(f"Unique error types: {report.unique_error_types}")
    print(f"Proposals generated: {report.proposals_generated}")
    print(f"High-confidence proposals: {report.high_confidence_proposals}")
    print("=" * 60)

    if report.proposals:
        print("\nTop Proposals:")
        for i, proposal in enumerate(sorted(report.proposals, key=lambda p: p.confidence, reverse=True)[:5], 1):
            print(f"\n{i}. {proposal.title}")
            print(f"   Confidence: {proposal.confidence:.1%}")
            print(f"   Priority: {proposal.priority}")
            print(f"   Affected files: {len(proposal.affected_files)}")


if __name__ == "__main__":
    main()
