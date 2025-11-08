#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Content Strategy Validator.

Validates pillar pages and content clusters for SEO compliance.
"""

from __future__ import annotations

import sys
import yaml
from pathlib import Path
from typing import Any


class ContentStrategyValidator:
    """Validate content strategy compliance."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Run all validation checks."""

        print("🔍 Validating Content Strategy...")
        print("=" * 60)

        # Load content clusters tracker
        tracker_file = self.project_root / "branding/seo/content_clusters.yaml"

        if not tracker_file.exists():
            self.issues.append("Content clusters tracker not found")
            return False

        with open(tracker_file) as f:
            tracker = yaml.safe_load(f)

        # Run validation checks
        self.check_pillar_pages(tracker)
        self.check_internal_linking(tracker)
        self.check_keyword_strategy(tracker)
        self.check_content_coverage(tracker)

        # Print results
        self.print_results()

        return len(self.issues) == 0

    def check_pillar_pages(self, tracker: dict[str, Any]) -> None:
        """Validate pillar pages."""

        print("\n📄 Checking Pillar Pages...")

        pillars = tracker.get("pillars", [])

        if len(pillars) < 5:
            self.issues.append(
                f"Expected 5 pillar pages, found {len(pillars)}"
            )

        for pillar in pillars:
            pillar_id = pillar.get("id", "unknown")

            # Check word count
            word_count = pillar.get("word_count", 0)
            if word_count < 2000:
                self.warnings.append(
                    f"Pillar '{pillar_id}' has {word_count} words (target: 2000+)"
                )

            # Check internal links
            internal_links = pillar.get("internal_links", 0)
            if internal_links < 10:
                self.warnings.append(
                    f"Pillar '{pillar_id}' has {internal_links} links (target: 10+)"
                )

            # Check cluster count
            clusters = pillar.get("clusters", [])
            if len(clusters) < 10:
                self.warnings.append(
                    f"Pillar '{pillar_id}' has {len(clusters)} clusters (target: 10-15)"
                )

            print(f"  ✓ {pillar_id}: {word_count} words, {len(clusters)} clusters")

    def check_internal_linking(self, tracker: dict[str, Any]) -> None:
        """Validate internal linking strategy."""

        print("\n🔗 Checking Internal Linking...")

        pillars = tracker.get("pillars", [])

        for pillar in pillars:
            pillar_id = pillar.get("id", "unknown")
            internal_links = pillar.get("internal_links", 0)

            # Each pillar should link to all its clusters
            clusters = pillar.get("clusters", [])
            expected_links = len(clusters) + 5  # Clusters + related pages

            if internal_links < expected_links:
                self.warnings.append(
                    f"Pillar '{pillar_id}' should have ~{expected_links} links, has {internal_links}"
                )

        print("  ✓ Internal linking structure validated")

    def check_keyword_strategy(self, tracker: dict[str, Any]) -> None:
        """Validate keyword targeting."""

        print("\n🔑 Checking Keyword Strategy...")

        pillars = tracker.get("pillars", [])

        for pillar in pillars:
            pillar_id = pillar.get("id", "unknown")
            keywords = pillar.get("target_keywords", [])

            if len(keywords) < 2:
                self.warnings.append(
                    f"Pillar '{pillar_id}' should target 2-4 keywords, has {len(keywords)}"
                )

            print(f"  ✓ {pillar_id}: {len(keywords)} target keywords")

    def check_content_coverage(self, tracker: dict[str, Any]) -> None:
        """Check content coverage gaps."""

        print("\n📊 Checking Content Coverage...")

        progress = tracker.get("progress", {})

        pillars_total = progress.get("pillars", {}).get("total", 0)
        pillars_published = progress.get("pillars", {}).get("published", 0)

        clusters_total = progress.get("clusters", {}).get("total", 0)
        clusters_published = progress.get("clusters", {}).get("published", 0)

        print(f"  Pillars: {pillars_published}/{pillars_total} published")
        print(f"  Clusters: {clusters_published}/{clusters_total} published")

        if clusters_published < clusters_total * 0.1:
            self.warnings.append(
                "Less than 10% of cluster articles published - increase production"
            )

    def print_results(self) -> None:
        """Print validation results."""

        print("\n" + "=" * 60)
        print("📊 Validation Results")
        print("=" * 60)

        if not self.issues and not self.warnings:
            print("\n✅ All checks passed! Content strategy is valid.")
            return

        if self.issues:
            print(f"\n❌ {len(self.issues)} Error(s):")
            for issue in self.issues:
                print(f"   • {issue}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warning(s):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.issues:
            print("\n✅ No critical errors found.")
            print("   Address warnings to optimize content strategy.")


def main() -> None:
    """Main entry point."""
    validator = ContentStrategyValidator()
    success = validator.validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
