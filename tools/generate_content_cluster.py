#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Content Cluster Generator.

Generates content cluster specifications for SEO pillar pages.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class ContentClusterGenerator:
    """Generate content cluster specifications."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent

    def generate_cluster(
        self,
        pillar_topic: str,
        primary_keyword: str,
        cluster_count: int = 15,
        target_word_count: int = 1000,
    ) -> dict[str, Any]:
        """Generate a content cluster specification."""

        # Generate cluster article ideas
        cluster_articles = self._generate_article_ideas(
            pillar_topic, primary_keyword, cluster_count
        )

        # Generate keyword map
        keyword_map = self._generate_keyword_map(cluster_articles, primary_keyword)

        # Generate internal linking suggestions
        linking_strategy = self._generate_linking_strategy(pillar_topic, cluster_articles)

        # Generate content calendar
        calendar = self._generate_calendar(cluster_articles)

        # Build complete specification
        spec = {
            "pillar": {
                "topic": pillar_topic,
                "primary_keyword": primary_keyword,
                "target_word_count": target_word_count * 2,  # Pillars are 2x longer
                "internal_links": cluster_count + 5,  # Link to all clusters + related
            },
            "clusters": cluster_articles,
            "keywords": keyword_map,
            "linking_strategy": linking_strategy,
            "content_calendar": calendar,
            "generated_at": datetime.now().isoformat(),
        }

        return spec

    def _generate_article_ideas(
        self, pillar_topic: str, primary_keyword: str, count: int
    ) -> list[dict[str, Any]]:
        """Generate cluster article ideas."""

        # Article type templates
        article_types = [
            ("What is {topic}?", "foundation", "what is {keyword}"),
            ("{topic} Explained", "educational", "{keyword} explained"),
            ("How {topic} Works", "technical", "how {keyword} works"),
            ("{topic} vs Alternatives", "comparison", "{keyword} vs"),
            ("Benefits of {topic}", "commercial", "{keyword} benefits"),
            ("Implementing {topic}", "tutorial", "implement {keyword}"),
            ("{topic} Best Practices", "guide", "{keyword} best practices"),
            ("Case Study: {topic}", "use_case", "{keyword} case study"),
            ("{topic} for {industry}", "industry", "{keyword} for"),
            ("Advanced {topic} Techniques", "advanced", "advanced {keyword}"),
            ("Common {topic} Mistakes", "troubleshooting", "{keyword} mistakes"),
            ("{topic} ROI Calculator", "tool", "{keyword} ROI"),
            ("Future of {topic}", "thought_leadership", "future {keyword}"),
            ("{topic} FAQ", "support", "{keyword} FAQ"),
            ("Research: {topic}", "research", "{keyword} research"),
        ]

        articles = []

        for i in range(min(count, len(article_types))):
            title_template, article_type, keyword_template = article_types[i]

            article = {
                "id": f"cluster_{i + 1:02d}",
                "title": title_template.format(topic=pillar_topic),
                "type": article_type,
                "primary_keyword": keyword_template.format(keyword=primary_keyword),
                "target_word_count": 800 + (i * 50),  # Varying lengths
                "status": "planned",
                "priority": "P1" if i < 5 else "P2" if i < 10 else "P3",
            }

            articles.append(article)

        return articles

    def _generate_keyword_map(
        self, articles: list[dict[str, Any]], primary_keyword: str
    ) -> dict[str, list[str]]:
        """Generate keyword map for each article."""

        keyword_map = {"primary": primary_keyword, "secondary": [], "long_tail": []}

        # Generate secondary keywords from article titles
        for article in articles:
            keyword_map["secondary"].append(article["primary_keyword"])

        # Generate some long-tail keywords
        keyword_map["long_tail"] = [
            f"how to use {primary_keyword}",
            f"{primary_keyword} tutorial",
            f"{primary_keyword} implementation guide",
            f"best {primary_keyword} practices",
            f"{primary_keyword} examples",
        ]

        return keyword_map

    def _generate_linking_strategy(
        self, pillar_topic: str, articles: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate internal linking strategy."""

        return {
            "pillar_to_clusters": {
                "anchor_text_pattern": "Learn more about {article_title}",
                "links": [article["title"] for article in articles],
            },
            "clusters_to_pillar": {
                "anchor_text_pattern": f"Complete guide to {pillar_topic}",
                "frequency": "2-3 times per article",
            },
            "cross_cluster_linking": {
                "strategy": "Link related clusters based on semantic relevance",
                "target": "2-3 cross-links per article",
            },
        }

    def _generate_calendar(self, articles: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Generate content publishing calendar."""

        calendar = []

        # Schedule 3-4 articles per week
        week = 1
        for i, article in enumerate(articles):
            if i % 4 == 0 and i > 0:
                week += 1

            calendar.append(
                {
                    "week": f"Week {week}",
                    "article_id": article["id"],
                    "title": article["title"],
                    "type": article["type"],
                    "priority": article["priority"],
                }
            )

        return calendar

    def save_spec(self, spec: dict[str, Any], output_file: Path) -> None:
        """Save cluster specification to YAML file."""

        with open(output_file, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Cluster specification saved to: {output_file}")

    def print_summary(self, spec: dict[str, Any]) -> None:
        """Print cluster specification summary."""

        print("\n📊 Content Cluster Specification Summary")
        print("=" * 60)
        print(f"\nPillar Topic: {spec['pillar']['topic']}")
        print(f"Primary Keyword: {spec['pillar']['primary_keyword']}")
        print(f"Target Word Count (Pillar): {spec['pillar']['target_word_count']}")
        print(f"\nCluster Articles: {len(spec['clusters'])}")

        print("\nArticle Breakdown by Type:")
        type_counts: dict[str, int] = {}
        for article in spec["clusters"]:
            article_type = article["type"]
            type_counts[article_type] = type_counts.get(article_type, 0) + 1

        for article_type, count in sorted(type_counts.items()):
            print(f"  • {article_type}: {count}")

        print(f"\nTotal Keywords:")
        print(f"  • Primary: 1")
        print(f"  • Secondary: {len(spec['keywords']['secondary'])}")
        print(f"  • Long-tail: {len(spec['keywords']['long_tail'])}")

        print(f"\nPublishing Schedule: {len(spec['content_calendar'])} weeks")

        print("\n✨ Next Steps:")
        print("  1. Review and customize cluster article titles")
        print("  2. Begin writing pillar page")
        print("  3. Follow content calendar for cluster articles")
        print("  4. Implement internal linking strategy")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate content cluster specification")

    parser.add_argument("pillar_topic", help="Pillar page topic (e.g., 'AI Ethics')")
    parser.add_argument(
        "primary_keyword", help="Primary target keyword (e.g., 'ai ethics')"
    )
    parser.add_argument(
        "--count", type=int, default=15, help="Number of cluster articles (default: 15)"
    )
    parser.add_argument(
        "--word-count",
        type=int,
        default=1000,
        help="Target word count for clusters (default: 1000)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: cluster_{topic}.yaml)",
    )

    args = parser.parse_args()

    # Create generator
    generator = ContentClusterGenerator()

    # Generate cluster spec
    spec = generator.generate_cluster(
        pillar_topic=args.pillar_topic,
        primary_keyword=args.primary_keyword,
        cluster_count=args.count,
        target_word_count=args.word_count,
    )

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        safe_topic = args.pillar_topic.lower().replace(" ", "_")
        output_file = Path(f"cluster_{safe_topic}.yaml")

    # Save spec
    generator.save_spec(spec, output_file)

    # Print summary
    generator.print_summary(spec)


if __name__ == "__main__":
    main()
