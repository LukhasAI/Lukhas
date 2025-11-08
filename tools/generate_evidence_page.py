#!/usr/bin/env python3
"""
tools/generate_evidence_page.py

Generates evidence page stubs from claims_registry.yaml (or .json) with:
- Prefilled front-matter from claims data
- Skeleton methodology sections
- Links to artifact files
- Bidirectional page links

Usage:
  python3 tools/generate_evidence_page.py
  python3 tools/generate_evidence_page.py --registry release_artifacts/claims_registry.json
  python3 tools/generate_evidence_page.py --claim-id matriz-p95-latency-2025-q3
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("❌ Missing PyYAML. Install with: pip install pyyaml")
    sys.exit(1)


# Paths
DEFAULT_REGISTRY_YAML = Path("release_artifacts/claims_registry.yaml")
DEFAULT_REGISTRY_JSON = Path("branding/governance/claims_registry.json")
EVIDENCE_DIR = Path("release_artifacts/evidence")
TEMPLATE_PATH = Path("branding/templates/evidence_page.md")


class EvidencePageGenerator:
    """Generate evidence pages from claims registry with full metadata."""

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or self._find_registry()
        self.template = self._load_template()
        self.evidence_dir = EVIDENCE_DIR
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _find_registry(self) -> Path:
        """Find claims registry file (YAML or JSON)."""
        if DEFAULT_REGISTRY_YAML.exists():
            return DEFAULT_REGISTRY_YAML
        if DEFAULT_REGISTRY_JSON.exists():
            return DEFAULT_REGISTRY_JSON
        print("❌ No claims registry found.")
        print(f"   Checked: {DEFAULT_REGISTRY_YAML}")
        print(f"   Checked: {DEFAULT_REGISTRY_JSON}")
        print("\n💡 Generate registry first:")
        print("   python3 tools/generate_claims_registry.py")
        sys.exit(1)

    def _load_template(self) -> str:
        """Load evidence page template."""
        if not TEMPLATE_PATH.exists():
            print(f"❌ Template not found: {TEMPLATE_PATH}")
            sys.exit(1)
        return TEMPLATE_PATH.read_text(encoding="utf-8")

    def _load_registry(self) -> Dict[str, Any]:
        """Load claims registry from YAML or JSON."""
        content = self.registry_path.read_text(encoding="utf-8")

        if self.registry_path.suffix == ".json":
            return json.loads(content)
        else:
            return yaml.safe_load(content) or {}

    def generate_evidence_id(self, claim: Dict[str, Any]) -> str:
        """
        Generate unique evidence ID from claim data.

        Format: {domain}-{claim-type}-{claim-snippet}-{quarter}
        Example: lukhas-ai-performance-p95-latency-2025-q4
        """
        # Extract domain (clean for filename)
        domain = claim.get("domain", "unknown")
        domain_slug = domain.replace(".", "-").replace("/", "-")

        # Infer claim type from claims text
        claims_found = claim.get("claims_found", [])
        claim_type = self._infer_claim_type(claims_found)

        # Create snippet from first claim
        claim_snippet = ""
        if claims_found:
            first_claim = claims_found[0]
            # Extract key terms (numbers, units, technical terms)
            snippet_parts = []

            # Extract percentages
            percentages = re.findall(r'\d+%', first_claim)
            snippet_parts.extend(percentages)

            # Extract latency measurements
            latency_match = re.search(r'p\d+|latency|ms|seconds?', first_claim.lower())
            if latency_match:
                snippet_parts.append("latency")

            # Extract other key terms (max 3 words)
            words = re.findall(r'\b[a-z]{4,}\b', first_claim.lower())
            technical_terms = [w for w in words if w in {
                'accuracy', 'performance', 'security', 'compliance',
                'matriz', 'lukhas', 'reasoning', 'cognitive', 'throughput',
                'uptime', 'availability', 'encryption'
            }]
            snippet_parts.extend(technical_terms[:2])

            claim_snippet = "-".join(snippet_parts[:4])

        if not claim_snippet:
            # Fallback: use hash of claim text
            claim_text = " ".join(claims_found[:2])
            claim_hash = hashlib.md5(claim_text.encode()).hexdigest()[:8]
            claim_snippet = claim_hash

        # Add quarter
        now = datetime.now()
        quarter = f"{now.year}-q{(now.month - 1) // 3 + 1}"

        # Combine parts
        evidence_id = f"{domain_slug}-{claim_type}-{claim_snippet}-{quarter}"

        # Clean and truncate
        evidence_id = self._slugify(evidence_id)
        return evidence_id[:80]  # Max 80 chars

    def _infer_claim_type(self, claims: List[str]) -> str:
        """Infer claim type from claim text."""
        claims_text = " ".join(claims).lower()

        # Pattern matching for claim types
        if any(term in claims_text for term in ['latency', 'throughput', 'p95', 'p99', 'ms', 'performance', 'speed']):
            return "performance"
        if any(term in claims_text for term in ['accuracy', 'precision', 'f1', 'score', 'correct']):
            return "accuracy"
        if any(term in claims_text for term in ['security', 'encryption', 'aes', 'tls', 'secure']):
            return "security"
        if any(term in claims_text for term in ['compliance', 'gdpr', 'wcag', 'iso', 'soc2', 'certified']):
            return "compliance"
        if any(term in claims_text for term in ['users', 'requests', 'operations', 'capacity', 'scale']):
            return "usage"

        return "general"

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\-]+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    def _extract_page_path(self, claim: Dict[str, Any]) -> str:
        """Extract relative page path from claim data."""
        page = claim.get("page", "")
        if not page:
            return "branding/websites/lukhas.ai/homepage.md"

        # Normalize to relative path from repo root
        page_path = Path(page)
        try:
            # Try to make relative to current dir
            if page_path.is_absolute():
                page_path = page_path.relative_to(Path.cwd())
        except ValueError:
            pass

        return str(page_path)

    def _format_claim_excerpt(self, claim_text: str) -> str:
        """Format claim text for excerpt (max 100 chars)."""
        if len(claim_text) <= 100:
            return claim_text
        return claim_text[:97] + "..."

    def prefill_template(
        self,
        claim: Dict[str, Any],
        evidence_id: str
    ) -> str:
        """
        Prefill template with claim data and metadata.

        Replaces {{PLACEHOLDERS}} with actual values or sensible defaults.
        """
        content = self.template

        # Basic claim info
        claims_found = claim.get("claims_found", [])
        claim_statement = "; ".join(claims_found) if claims_found else "[Describe claim here]"
        claim_type = self._infer_claim_type(claims_found)
        domain = claim.get("domain", "lukhas.ai")

        # Pages using this claim
        page_path = self._extract_page_path(claim)
        claim_excerpt = self._format_claim_excerpt(claims_found[0] if claims_found else "")

        # Dates
        today = datetime.now()
        verified_date = today.strftime("%Y-%m-%d")
        legal_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        next_review = (today + timedelta(days=90)).strftime("%Y-%m-%d")

        # Front-matter replacements
        replacements = {
            "{{EVIDENCE_ID}}": evidence_id,
            "{{CLAIM_TYPE}}": claim_type,
            "{{CLAIM_STATEMENT}}": claim_statement,
            "{{DOMAIN}}": domain,
            "{{VERIFIED_DATE}}": verified_date,
            "{{LEGAL_DATE}}": legal_date,
            "{{NEXT_REVIEW_DATE}}": next_review,

            # Methodology placeholders
            "{{TEST_ENVIRONMENT}}": "[Describe test environment]",
            "{{DATA_COLLECTION}}": "[Specify data collection period]",
            "{{TOOL_1}}": "Tool 1",
            "{{TOOL_2}}": "Tool 2",
            "{{SAMPLE_SIZE}}": "[Specify sample size]",

            # Artifacts
            "{{ARTIFACT_FILE}}": f"{evidence_id}",
            "{{ARTIFACT_HASH}}": "[Generate SHA256 hash]",
            "{{IMAGE_HASH}}": "[Generate SHA256 hash]",

            # Body replacements
            "{{DOMAINS_LIST}}": domain,
            "{{TEST_ENVIRONMENT_DESCRIPTION}}": "[Provide detailed test environment description]",

            # Results placeholders
            "{{P50_VALUE}}": "[Measure]",
            "{{P50_TARGET}}": "[Specify]",
            "{{P50_STATUS}}": "⏳ TBD",
            "{{P95_VALUE}}": "[Measure]",
            "{{P95_TARGET}}": "[Specify]",
            "{{P95_STATUS}}": "⏳ TBD",
            "{{P99_VALUE}}": "[Measure]",
            "{{P99_TARGET}}": "[Specify]",
            "{{P99_STATUS}}": "⏳ TBD",
            "{{SUCCESS_RATE}}": "[Measure]",
            "{{SUCCESS_TARGET}}": "[Specify]",
            "{{SUCCESS_STATUS}}": "⏳ TBD",

            # Statistical confidence
            "{{MARGIN_ERROR}}": "[Calculate]",
            "{{STD_DEV}}": "[Calculate]",
            "{{OUTLIER_COUNT}}": "0",
            "{{OUTLIER_CRITERIA}}": "[Define criteria]",

            # Percentile distribution
            "{{P0_VALUE}}": "[Min]",
            "{{P25_VALUE}}": "[Q1]",
            "{{P75_VALUE}}": "[Q3]",
            "{{P90_VALUE}}": "[P90]",
            "{{P100_VALUE}}": "[Max]",

            # Artifacts
            "{{ARTIFACT_1_NAME}}": f"{evidence_id}-raw-data",
            "{{ARTIFACT_1_PATH}}": f"perf/{evidence_id}-raw-data.json",
            "{{ARTIFACT_1_HASH}}": "[Generate SHA256]",
            "{{ARTIFACT_1_SIZE}}": "[File size]",

            "{{ARTIFACT_2_NAME}}": f"{evidence_id}-dashboard",
            "{{ARTIFACT_2_PATH}}": f"perf/{evidence_id}-dashboard.png",
            "{{ARTIFACT_2_HASH}}": "[Generate SHA256]",
            "{{ARTIFACT_2_SIZE}}": "[File size]",
            "{{IMAGE_RESOLUTION}}": "1920x1080",

            "{{ARTIFACT_3_NAME}}": f"{evidence_id}-summary",
            "{{ARTIFACT_3_PATH}}": f"perf/{evidence_id}-summary.csv",
            "{{ARTIFACT_3_HASH}}": "[Generate SHA256]",

            # Verification
            "{{INITIAL_VERIFICATION_DATE}}": verified_date,
            "{{INITIAL_VERIFIER}}": "@web-architect",
            "{{INITIAL_NOTES}}": "Initial evidence page created",
            "{{LEGAL_APPROVAL_DATE}}": legal_date,
            "{{LEGAL_NOTES}}": "Pending legal review",

            # Limitations
            "{{COVERAGE_ITEM_1}}": "[What is covered by this claim]",
            "{{COVERAGE_ITEM_2}}": "[Additional coverage]",
            "{{COVERAGE_ITEM_3}}": "[Additional coverage]",
            "{{LIMITATION_1}}": "[What is NOT covered]",
            "{{LIMITATION_2}}": "[Additional limitation]",
            "{{LIMITATION_3}}": "[Additional limitation]",

            "{{CAVEAT_1_TITLE}}": "Test Environment Differences",
            "{{CAVEAT_1_DESCRIPTION}}": "[Describe how test differs from production]",
            "{{CAVEAT_2_TITLE}}": "Workload Assumptions",
            "{{CAVEAT_2_DESCRIPTION}}": "[Describe workload assumptions]",
            "{{CAVEAT_3_TITLE}}": "Measurement Variance",
            "{{CAVEAT_3_DESCRIPTION}}": "[Expected variance in measurements]",

            "{{NORMAL_VARIANCE}}": "[e.g., ±10%]",
            "{{DEGRADATION_TRIGGERS}}": "[Conditions that affect performance]",
            "{{REMEASUREMENT_TRIGGERS}}": "[When to remeasure]",

            # Review
            "{{REVIEW_OWNER}}": "@qa-lead",
            "{{NOTIFICATION_METHOD}}": "GitHub issue + email",

            # Reproducibility
            "{{SETUP_COMMANDS}}": "# Add setup commands here",
            "{{LOAD_TEST_COMMANDS}}": "# Add load test commands here",
            "{{DATA_COLLECTION_COMMANDS}}": "# Add data collection commands here",
            "{{ANALYSIS_COMMANDS}}": "# Add analysis commands here",
            "{{REPRODUCTION_TOLERANCE}}": "±15%",
        }

        # Apply replacements
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Handle Mustache-style conditional sections (remove for now, or add basic support)
        # Remove {{#THIRD_PARTY_AUDIT}}...{{/THIRD_PARTY_AUDIT}} sections
        content = re.sub(
            r'\{\{#THIRD_PARTY_AUDIT\}\}.*?\{\{/THIRD_PARTY_AUDIT\}\}',
            '',
            content,
            flags=re.DOTALL
        )

        # Expand {{^THIRD_PARTY_AUDIT}}...{{/THIRD_PARTY_AUDIT}} (negation)
        content = re.sub(
            r'\{\{\^THIRD_PARTY_AUDIT\}\}(.*?)\{\{/THIRD_PARTY_AUDIT\}\}',
            r'\1',
            content,
            flags=re.DOTALL
        )

        # Remove other Mustache loops for now ({{#PAGES_USING_CLAIM}}, etc.)
        content = re.sub(r'\{\{#.*?\}\}.*?\{\{/.*?\}\}', '', content, flags=re.DOTALL)

        # Add bidirectional link section
        pages_section = f"\n- [{Path(page_path).name}](../../{page_path}) - \"{claim_excerpt}\"\n"
        content = content.replace(
            "### Bidirectional Link Validation",
            f"{pages_section}\n### Bidirectional Link Validation"
        )

        return content

    def generate_page(
        self,
        claim: Dict[str, Any],
        force: bool = False
    ) -> Optional[Path]:
        """Generate evidence page for a single claim."""
        evidence_id = self.generate_evidence_id(claim)
        output_path = self.evidence_dir / f"{evidence_id}.md"

        if output_path.exists() and not force:
            print(f"⏭️  Skipping (exists): {output_path}")
            return None

        # Generate content
        content = self.prefill_template(claim, evidence_id)

        # Write file
        output_path.write_text(content, encoding="utf-8")

        action = "Updated" if output_path.exists() else "Created"
        print(f"✅ {action}: {output_path}")
        return output_path

    def generate_all(self, force: bool = False) -> List[Path]:
        """Generate evidence pages for all claims in registry."""
        registry_data = self._load_registry()
        claims = registry_data.get("claims", [])

        if not claims:
            print("⚠️  No claims found in registry")
            return []

        print(f"📋 Found {len(claims)} claims in registry")
        print(f"📁 Output directory: {self.evidence_dir}\n")

        generated = []
        for i, claim in enumerate(claims, 1):
            print(f"[{i}/{len(claims)}] ", end="")
            result = self.generate_page(claim, force=force)
            if result:
                generated.append(result)

        print(f"\n✅ Generated {len(generated)} evidence pages")
        print(f"⏭️  Skipped {len(claims) - len(generated)} existing pages")

        return generated


def main():
    parser = argparse.ArgumentParser(
        description="Generate evidence pages from claims registry"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        help="Path to claims registry (YAML or JSON)"
    )
    parser.add_argument(
        "--claim-id",
        help="Generate only for specific claim ID"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing evidence pages"
    )

    args = parser.parse_args()

    # Initialize generator
    generator = EvidencePageGenerator(registry_path=args.registry)

    if args.claim_id:
        print(f"⚠️  Single claim ID generation not yet implemented")
        print(f"💡 Run without --claim-id to generate all pages")
        sys.exit(1)

    # Generate all pages
    generated = generator.generate_all(force=args.force)

    if generated:
        print(f"\n📝 Next steps:")
        print(f"   1. Review generated pages in {EVIDENCE_DIR}")
        print(f"   2. Fill in methodology sections with actual data")
        print(f"   3. Link artifacts and calculate SHA256 hashes")
        print(f"   4. Run: python3 tools/validate_evidence_pages.py")


if __name__ == "__main__":
    main()
