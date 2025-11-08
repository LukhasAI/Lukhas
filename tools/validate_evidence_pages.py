#!/usr/bin/env python3
"""
tools/validate_evidence_pages.py

Validates evidence pages for:
- Required front-matter fields
- Bidirectional links between pages and evidence
- Artifact file existence and SHA256 hash format
- Legal approval for customer-facing claims
- Verification dates and review schedules

Usage:
  python3 tools/validate_evidence_pages.py
  python3 tools/validate_evidence_pages.py --check-bidirectional
  python3 tools/validate_evidence_pages.py --evidence-dir release_artifacts/evidence
  python3 tools/validate_evidence_pages.py --strict  # Exit 1 on any warning
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    print("❌ Missing PyYAML. Install with: pip install pyyaml")
    sys.exit(1)


# Default paths
DEFAULT_EVIDENCE_DIR = Path("release_artifacts/evidence")
BRANDING_DIR = Path("branding")

# Required front-matter fields
REQUIRED_FIELDS = {
    "evidence_id",
    "claim_type",
    "claim_statement",
    "domains",
    "verified_by",
    "verified_date",
}

# Optional but recommended fields
RECOMMENDED_FIELDS = {
    "legal_approved",
    "legal_approved_by",
    "legal_approved_date",
    "next_review",
    "pages_using_claim",
    "methodology",
    "artifacts",
}

# Valid claim types
VALID_CLAIM_TYPES = {
    "performance",
    "security",
    "compliance",
    "usage",
    "accuracy",
    "general"
}


class EvidencePageValidator:
    """Validate evidence pages for completeness and correctness."""

    def __init__(
        self,
        evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
        check_bidirectional: bool = False,
        strict: bool = False
    ):
        self.evidence_dir = evidence_dir
        self.check_bidirectional = check_bidirectional
        self.strict = strict

        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def log_error(self, message: str):
        """Log an error message."""
        self.errors.append(f"❌ {message}")

    def log_warning(self, message: str):
        """Log a warning message."""
        self.warnings.append(f"⚠️  {message}")

    def log_info(self, message: str):
        """Log an info message."""
        self.info.append(f"ℹ️  {message}")

    def parse_evidence_page(self, page_path: Path) -> Optional[Tuple[Dict[str, Any], str]]:
        """Parse evidence page and extract front-matter and body."""
        try:
            content = page_path.read_text(encoding="utf-8")
        except Exception as e:
            self.log_error(f"{page_path.name}: Cannot read file - {e}")
            return None

        # Extract front-matter
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            self.log_error(f"{page_path.name}: No valid YAML front-matter found")
            return None

        fm_content, body = match.groups()

        try:
            front_matter = yaml.safe_load(fm_content)
            if not isinstance(front_matter, dict):
                self.log_error(f"{page_path.name}: Front-matter is not a dictionary")
                return None
        except yaml.YAMLError as e:
            self.log_error(f"{page_path.name}: Invalid YAML front-matter - {e}")
            return None

        return front_matter, body

    def validate_required_fields(
        self,
        page_path: Path,
        front_matter: Dict[str, Any]
    ) -> bool:
        """Validate required front-matter fields are present."""
        valid = True
        missing = REQUIRED_FIELDS - set(front_matter.keys())

        if missing:
            self.log_error(
                f"{page_path.name}: Missing required fields: {', '.join(sorted(missing))}"
            )
            valid = False

        # Check recommended fields
        missing_recommended = RECOMMENDED_FIELDS - set(front_matter.keys())
        if missing_recommended:
            self.log_warning(
                f"{page_path.name}: Missing recommended fields: {', '.join(sorted(missing_recommended))}"
            )

        return valid

    def validate_claim_type(
        self,
        page_path: Path,
        claim_type: Optional[str]
    ) -> bool:
        """Validate claim type is valid."""
        if not claim_type:
            return True  # Already caught by required fields check

        if claim_type not in VALID_CLAIM_TYPES:
            self.log_error(
                f"{page_path.name}: Invalid claim_type '{claim_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_CLAIM_TYPES))}"
            )
            return False

        return True

    def validate_dates(
        self,
        page_path: Path,
        front_matter: Dict[str, Any]
    ) -> bool:
        """Validate date fields are properly formatted."""
        valid = True
        date_fields = ["verified_date", "legal_approved_date", "next_review"]

        for field in date_fields:
            date_value = front_matter.get(field)
            if not date_value or date_value == f"{{{{{field.upper()}}}}}":
                continue  # Skip missing or placeholder dates

            # Validate date format (YYYY-MM-DD)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_value)):
                self.log_error(
                    f"{page_path.name}: Invalid {field} format: '{date_value}'. "
                    "Expected YYYY-MM-DD"
                )
                valid = False
                continue

            # Parse date
            try:
                parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d")

                # Warn if next_review is in the past
                if field == "next_review" and parsed_date < datetime.now():
                    self.log_warning(
                        f"{page_path.name}: next_review date is in the past: {date_value}"
                    )
            except ValueError:
                self.log_error(
                    f"{page_path.name}: Invalid {field} date: '{date_value}'"
                )
                valid = False

        return valid

    def validate_legal_approval(
        self,
        page_path: Path,
        front_matter: Dict[str, Any]
    ) -> bool:
        """Validate legal approval is set for customer-facing claims."""
        legal_approved = front_matter.get("legal_approved")

        # If legal_approved is explicitly True, check required fields
        if legal_approved is True:
            if not front_matter.get("legal_approved_by"):
                self.log_warning(
                    f"{page_path.name}: legal_approved is True but legal_approved_by is missing"
                )

            if not front_matter.get("legal_approved_date"):
                self.log_warning(
                    f"{page_path.name}: legal_approved is True but legal_approved_date is missing"
                )

        # If legal_approved is False or missing, warn for customer-facing domains
        elif legal_approved is False or legal_approved is None:
            domains = front_matter.get("domains", [])
            customer_domains = {"lukhas.ai", "lukhas.eu", "lukhas.com"}

            if any(d in customer_domains for d in domains):
                self.log_warning(
                    f"{page_path.name}: Customer-facing claim without legal approval. "
                    f"Domains: {domains}"
                )

        return True

    def validate_artifacts(
        self,
        page_path: Path,
        front_matter: Dict[str, Any]
    ) -> bool:
        """Validate artifact references and SHA256 hashes."""
        valid = True
        artifacts = front_matter.get("artifacts", [])

        if not artifacts:
            self.log_info(f"{page_path.name}: No artifacts specified")
            return True

        if not isinstance(artifacts, list):
            self.log_error(f"{page_path.name}: artifacts field must be a list")
            return False

        for i, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                self.log_error(
                    f"{page_path.name}: artifact[{i}] must be a dictionary"
                )
                valid = False
                continue

            # Check required artifact fields
            artifact_path = artifact.get("path")
            artifact_type = artifact.get("type")
            artifact_hash = artifact.get("hash")

            if not artifact_path:
                self.log_error(
                    f"{page_path.name}: artifact[{i}] missing 'path' field"
                )
                valid = False

            if not artifact_type:
                self.log_warning(
                    f"{page_path.name}: artifact[{i}] missing 'type' field"
                )

            # Validate SHA256 hash format
            if artifact_hash:
                # Should be "sha256-" followed by 64 hex chars or "[...]" placeholder
                if not re.match(r'^sha256-([a-fA-F0-9]{64}|\[.*\])$', artifact_hash):
                    self.log_warning(
                        f"{page_path.name}: artifact[{i}] has invalid hash format: {artifact_hash}"
                    )
            else:
                self.log_warning(
                    f"{page_path.name}: artifact[{i}] missing 'hash' field"
                )

            # Check if artifact file exists (optional, might not be committed yet)
            if artifact_path and not artifact_path.startswith("{{"):
                artifact_file = Path(artifact_path)
                if not artifact_file.exists():
                    self.log_info(
                        f"{page_path.name}: artifact file does not exist: {artifact_path}"
                    )

        return valid

    def validate_bidirectional_links(
        self,
        page_path: Path,
        front_matter: Dict[str, Any]
    ) -> bool:
        """
        Validate bidirectional links between evidence pages and content pages.

        Check that:
        1. Evidence page lists pages_using_claim
        2. Each listed page exists and references this evidence page
        """
        if not self.check_bidirectional:
            return True

        valid = True
        evidence_id = front_matter.get("evidence_id", "")
        pages_using_claim = front_matter.get("pages_using_claim", [])

        if not pages_using_claim:
            self.log_info(
                f"{page_path.name}: No pages_using_claim specified (consider adding)"
            )
            return True

        for page_ref in pages_using_claim:
            # Parse page reference (may include line numbers)
            page_file = re.sub(r'#L\d+$', '', page_ref)
            content_page = Path(page_file)

            # Check if page exists
            if not content_page.exists():
                self.log_error(
                    f"{page_path.name}: Referenced page does not exist: {page_file}"
                )
                valid = False
                continue

            # Check if page references this evidence page
            try:
                page_content = content_page.read_text(encoding="utf-8")

                # Extract front-matter
                match = re.match(r'^---\n(.*?)\n---\n', page_content, re.DOTALL)
                if match:
                    page_fm = yaml.safe_load(match.group(1))
                    if isinstance(page_fm, dict):
                        evidence_links = page_fm.get("evidence_links", [])

                        # Check if this evidence page is referenced
                        evidence_ref = f"release_artifacts/evidence/{page_path.name}"
                        if evidence_ref not in evidence_links and str(page_path) not in evidence_links:
                            self.log_warning(
                                f"{page_path.name}: Page {page_file} does not reference "
                                f"this evidence page in evidence_links"
                            )
            except Exception as e:
                self.log_warning(
                    f"{page_path.name}: Cannot read page {page_file}: {e}"
                )

        return valid

    def validate_placeholders(
        self,
        page_path: Path,
        body: str
    ) -> bool:
        """Warn about unfilled placeholders in body text."""
        # Find all {{PLACEHOLDER}} patterns
        placeholders = re.findall(r'\{\{([A-Z_]+)\}\}', body)

        if placeholders:
            # Filter out acceptable placeholders in template documentation
            skip_patterns = {
                'CLAIM_ID', 'SHORT_CLAIM', 'EXACT_CLAIM_TEXT',  # Template examples
            }
            real_placeholders = [p for p in placeholders if p not in skip_patterns]

            if real_placeholders:
                self.log_warning(
                    f"{page_path.name}: Contains unfilled placeholders: "
                    f"{', '.join(set(real_placeholders[:5]))}"
                    f"{' ...' if len(real_placeholders) > 5 else ''}"
                )

        return True

    def validate_page(self, page_path: Path) -> bool:
        """Validate a single evidence page."""
        # Parse page
        result = self.parse_evidence_page(page_path)
        if not result:
            return False

        front_matter, body = result

        # Run all validations
        valid = True
        valid &= self.validate_required_fields(page_path, front_matter)
        valid &= self.validate_claim_type(page_path, front_matter.get("claim_type"))
        valid &= self.validate_dates(page_path, front_matter)
        valid &= self.validate_legal_approval(page_path, front_matter)
        valid &= self.validate_artifacts(page_path, front_matter)
        valid &= self.validate_bidirectional_links(page_path, front_matter)
        valid &= self.validate_placeholders(page_path, body)

        return valid

    def validate_all(self) -> bool:
        """Validate all evidence pages in directory."""
        if not self.evidence_dir.exists():
            print(f"❌ Evidence directory does not exist: {self.evidence_dir}")
            return False

        # Find all markdown files
        evidence_pages = list(self.evidence_dir.glob("*.md"))

        if not evidence_pages:
            print(f"⚠️  No evidence pages found in {self.evidence_dir}")
            return True

        print(f"📋 Validating {len(evidence_pages)} evidence pages...\n")

        all_valid = True
        for page_path in sorted(evidence_pages):
            page_valid = self.validate_page(page_path)
            all_valid &= page_valid

        return all_valid

    def print_summary(self) -> bool:
        """Print validation summary and return overall status."""
        print()

        # Print all messages
        for msg in self.info:
            print(msg)

        for msg in self.warnings:
            print(msg)

        for msg in self.errors:
            print(msg)

        # Summary
        print("\n" + "=" * 60)
        print("📊 Validation Summary:")
        print(f"   Errors:   {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Info:     {len(self.info)}")

        # Determine overall status
        if self.errors:
            print("\n❌ Validation FAILED - fix errors before proceeding")
            return False
        elif self.warnings and self.strict:
            print("\n⚠️  Validation FAILED (strict mode) - fix warnings")
            return False
        elif self.warnings:
            print("\n⚠️  Validation passed with warnings")
            return True
        else:
            print("\n✅ Validation PASSED - all evidence pages valid")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate evidence pages for completeness and correctness"
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR,
        help=f"Evidence directory (default: {DEFAULT_EVIDENCE_DIR})"
    )
    parser.add_argument(
        "--check-bidirectional",
        action="store_true",
        help="Check bidirectional links between evidence and content pages"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit code 1)"
    )

    args = parser.parse_args()

    # Run validation
    validator = EvidencePageValidator(
        evidence_dir=args.evidence_dir,
        check_bidirectional=args.check_bidirectional,
        strict=args.strict
    )

    validator.validate_all()
    success = validator.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
