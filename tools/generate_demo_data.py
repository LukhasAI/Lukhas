#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
LUKHAS Demo Data Generator.

Generates sample data for quickstart demos:
- Reasoning traces
- Memory folds
- Evidence pages
- Sample claims
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class DemoDataGenerator:
    """Generate demo data for LUKHAS quickstart."""

    def __init__(self, size: str = "small"):
        """
        Initialize generator.

        Args:
            size: Data size - small (10 items), medium (50), large (200)
        """
        self.size = size
        self.project_root = Path(__file__).parent.parent
        self.output_dir = self.project_root / "demo_data"

        # Size configurations
        self.sizes = {
            "small": {"traces": 10, "memories": 5, "evidence": 3, "claims": 5},
            "medium": {"traces": 50, "memories": 20, "evidence": 10, "claims": 20},
            "large": {"traces": 200, "memories": 100, "evidence": 30, "claims": 50},
        }

    def generate_all(self) -> None:
        """Generate all demo data."""
        print(f"🎲 Generating {self.size} demo data set...")
        print()

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Generate each type
        self.generate_reasoning_traces()
        self.generate_memory_folds()
        self.generate_evidence_pages()
        self.generate_claims()

        print()
        print("✅ Demo data generation complete!")
        print(f"📁 Output directory: {self.output_dir}")

    def generate_reasoning_traces(self) -> None:
        """Generate sample reasoning traces."""
        count = self.sizes[self.size]["traces"]
        print(f"🧠 Generating {count} reasoning traces...")

        traces = []

        sample_queries = [
            "Explain quantum computing concepts",
            "Design a memory system",
            "Solve an ethical dilemma",
            "Optimize algorithm performance",
            "Explain consciousness theories",
            "Design API architecture",
            "Implement feature flag system",
            "Create GDPR compliance framework",
            "Build recommendation system",
            "Analyze sentiment in text",
        ]

        for i in range(count):
            query = sample_queries[i % len(sample_queries)]

            trace = {
                "trace_id": f"trace_{i + 1:04d}",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "query": query,
                "steps": [
                    {
                        "step": 1,
                        "thought": "Parse query and identify intent",
                        "confidence": 0.95,
                    },
                    {
                        "step": 2,
                        "thought": "Retrieve relevant knowledge",
                        "confidence": 0.88,
                    },
                    {
                        "step": 3,
                        "thought": "Apply reasoning patterns",
                        "confidence": 0.92,
                    },
                    {
                        "step": 4,
                        "thought": "Generate response",
                        "confidence": 0.90,
                    },
                ],
                "response": f"Sample response to: {query}",
                "execution_time_ms": 150 + (i * 10),
            }

            traces.append(trace)

        # Save to file
        output_file = self.output_dir / "reasoning_traces.json"
        with open(output_file, "w") as f:
            json.dump(traces, f, indent=2)

        print(f"   ✓ Saved to {output_file.name}")

    def generate_memory_folds(self) -> None:
        """Generate sample memory folds."""
        count = self.sizes[self.size]["memories"]
        print(f"💾 Generating {count} memory folds...")

        memories = []

        for i in range(count):
            memory = {
                "fold_id": f"mf_{datetime.now().strftime('%Y%m%d')}_{i + 1:04d}",
                "created_at": (datetime.now() - timedelta(hours=i * 2)).isoformat(),
                "status": "short_term" if i < count // 2 else "long_term",
                "entries": [
                    {
                        "key": "user_preference.theme",
                        "value": "dark" if i % 2 else "light",
                        "timestamp": datetime.now().isoformat(),
                    },
                    {
                        "key": "user_context.last_query",
                        "value": f"Query about topic {i}",
                        "timestamp": datetime.now().isoformat(),
                    },
                ],
                "access_count": i + 1,
                "importance_score": 0.5 + (i * 0.01),
            }

            memories.append(memory)

        # Save to file
        output_file = self.output_dir / "memory_folds.json"
        with open(output_file, "w") as f:
            json.dump(memories, f, indent=2)

        print(f"   ✓ Saved to {output_file.name}")

    def generate_evidence_pages(self) -> None:
        """Generate sample evidence pages."""
        count = self.sizes[self.size]["evidence"]
        print(f"📄 Generating {count} evidence pages...")

        evidence_dir = self.output_dir / "evidence"
        evidence_dir.mkdir(exist_ok=True)

        sample_pages = [
            ("reasoning_performance", "Reasoning Performance Metrics"),
            ("memory_accuracy", "Memory Recall Accuracy"),
            ("ethical_compliance", "Ethical Decision Compliance"),
        ]

        for i in range(count):
            page_id, title = sample_pages[i % len(sample_pages)]
            page_id = f"{page_id}_{i + 1}"

            content = f"""# {title}

**Evidence ID**: {page_id}
**Generated**: {datetime.now().isoformat()}
**Status**: Sample Data

## Overview

This is a sample evidence page for demonstration purposes.

## Metrics

| Metric | Value | Target |
|--------|-------|--------|
| Accuracy | 94.{i}% | >90% |
| Latency | {100 + i}ms | <200ms |
| Success Rate | 98.{i}% | >95% |

## Validation

- ✅ Automated tests passing
- ✅ Manual review completed
- ✅ Stakeholder approval received

## References

- Internal testing: test_run_{i + 1:04d}
- External validation: peer_review_{i + 1}
"""

            output_file = evidence_dir / f"{page_id}.md"
            with open(output_file, "w") as f:
                f.write(content)

        print(f"   ✓ Saved {count} pages to {evidence_dir.name}/")

    def generate_claims(self) -> None:
        """Generate sample claims with evidence links."""
        count = self.sizes[self.size]["claims"]
        print(f"📝 Generating {count} claims...")

        claims = []

        sample_claims = [
            "LUKHAS achieves 94%+ reasoning accuracy",
            "Memory system supports 10K+ concurrent folds",
            "Response latency under 200ms (p95)",
            "GDPR-compliant data processing",
            "Ethical decision rate >99%",
        ]

        for i in range(count):
            claim_text = sample_claims[i % len(sample_claims)]

            claim = {
                "claim_id": f"claim_{i + 1:04d}",
                "claim": claim_text,
                "status": "verified" if i % 3 == 0 else "pending",
                "evidence_links": [
                    f"evidence/reasoning_performance_{(i % 3) + 1}.md",
                    f"evidence/memory_accuracy_{(i % 3) + 1}.md",
                ],
                "created_at": datetime.now().isoformat(),
                "last_verified": datetime.now().isoformat() if i % 3 == 0 else None,
            }

            claims.append(claim)

        # Save to file
        output_file = self.output_dir / "claims.json"
        with open(output_file, "w") as f:
            json.dump(claims, f, indent=2)

        print(f"   ✓ Saved to {output_file.name}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate LUKHAS demo data")

    parser.add_argument(
        "--size",
        choices=["small", "medium", "large"],
        default="small",
        help="Size of demo data set (default: small)",
    )

    args = parser.parse_args()

    generator = DemoDataGenerator(size=args.size)
    generator.generate_all()


if __name__ == "__main__":
    main()
