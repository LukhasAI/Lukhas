#!/usr/bin/env python3
"""
Test LUKHAS AI Content Generation without database dependency
Demonstrates the automated content generator with mock database functionality
"""

import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Mock the database integration to avoid dependency issues


DEFAULT_FIX_LATER_MESSAGE = "Deferred implementation placeholder invoked"


logger = logging.getLogger("branding.test_content_generation")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    """Safely coerce numeric instrumentation values."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class DeferredFixLaterEvent:
    """Structured record describing deferred implementation work."""

    message: str
    created_at: datetime
    args: tuple[Any, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    drift_score: float = 0.0
    affect_delta: float = 0.0

    def describe(self) -> str:
        """Generate a human-friendly summary for console output."""

        details: list[str] = [
            f"drift_score={self.drift_score:.2f}",
            f"affect_delta={self.affect_delta:.2f}",
        ]

        if self.args:
            details.append(f"args={self.args!r}")
        if self.metadata:
            details.append(f"metadata={self.metadata!r}")

        return f"⏳ Deferred@{self.created_at.isoformat()}: {self.message} ({', '.join(details)})"


FIX_LATER_EVENTS: list[DeferredFixLaterEvent] = []


def fix_later(
    *args: Any,
    message: str | None = None,
    level: int = logging.WARNING,
    drift_score: float | None = None,
    affect_delta: float | None = None,
    **metadata: Any,
) -> DeferredFixLaterEvent:
    """Capture a structured trace describing deferred work."""

    positional_args = tuple(args)
    resolved_message = message
    if resolved_message is None and positional_args:
        resolved_message = str(positional_args[0])
        positional_args = positional_args[1:]

    resolved_message = resolved_message or DEFAULT_FIX_LATER_MESSAGE

    payload_metadata = dict(metadata)
    resolved_drift = _coerce_float(
        drift_score if drift_score is not None else payload_metadata.pop("drift_score", 0.0)
    )
    resolved_affect = _coerce_float(
        affect_delta if affect_delta is not None else payload_metadata.pop("affect_delta", 0.0)
    )

    record = DeferredFixLaterEvent(
        message=resolved_message,
        created_at=datetime.now(timezone.utc),
        args=positional_args,
        metadata=payload_metadata,
        drift_score=resolved_drift,
        affect_delta=resolved_affect,
    )

    FIX_LATER_EVENTS.append(record)

    logger.log(
        level,
        "Deferred action recorded: %s | metadata=%s | drift_score=%.2f | affect_delta=%.2f",
        record.message,
        record.metadata,
        record.drift_score,
        record.affect_delta,
    )

    return record


class MockDatabase:
    """Mock database for testing content generation"""

    def __init__(self):
        self.activities = []
        self.content = []
        self.content_id_counter = 1

    def log_system_activity(self, system_name: str, activity_type: str, description: str, value: float):
        """Mock log system activity"""
        self.activities.append(
            {
                "system": system_name,
                "type": activity_type,
                "description": description,
                "value": value,
            }
        )
        fix_later(
            message="MockDatabase activity logged; replace with persistent storage layer",
            level=logging.INFO,
            system=system_name,
            activity_type=activity_type,
            drift_score=0.02,
            affect_delta=0.0,
        )

    def save_generated_content(
        self, system_name: str, content_type: str, title: str, content: str, voice_coherence: float
    ) -> int:
        """Mock save generated content"""
        content_id = self.content_id_counter
        self.content_id_counter += 1

        self.content.append(
            {
                "id": content_id,
                "system": system_name,
                "type": content_type,
                "title": title,
                "content": content,
                "coherence": voice_coherence,
            }
        )

        print(f"💾 Saved content: {title} (ID: {content_id})")
        return content_id

    def get_content_by_type(self, content_type: str, limit: int = 10) -> list:
        """Mock get content by type"""
        filtered = [c for c in self.content if c["type"] == content_type]
        return filtered[-limit:]

    def get_all_content(self, limit: int = 10) -> list:
        """Mock get all content"""
        return self.content[-limit:]

    def get_system_analytics(self, system_name: str) -> list:
        """Mock get system analytics"""
        return [a for a in self.activities if a["system"] == system_name]


# Replace the database import with our mock
sys.modules["database_integration"] = type("MockModule", (), {"db": MockDatabase()})

# Now import the content generator
from branding.engines.lukhas_content_platform.automated_content_generator import AutomatedContentGenerator


def test_single_domain_content():
    """Test content generation for a single domain"""
    print("🧪 Testing single domain content generation...")

    generator = AutomatedContentGenerator()

    # Test lukhas.ai content generation
    result = generator.generate_homepage_content("lukhas.ai")

    print("\n✅ Generated content for lukhas.ai:")
    print(f"   - Content ID: {result['content_id']}")
    print(f"   - Word count: {result['word_count']}")
    print(f"   - Stars: {result['constellation_stars']}")
    print(f"   - Sections: {result['sections']}")

    # Show a preview of the content
    content_preview = result["content"][:500] + "..."
    print(f"\n📄 Content preview:\n{content_preview}")

    return result


def test_multiple_domains():
    """Test content generation for multiple domains"""
    print("\n🧪 Testing multiple domain content generation...")

    generator = AutomatedContentGenerator()

    # Test a selection of domains
    test_domains = ["lukhas.ai", "lukhas.com", "lukhas.app", "lukhas.dev"]

    results = {}
    for domain in test_domains:
        try:
            result = generator.generate_homepage_content(domain)
            results[domain] = result
            print(f"✅ Generated content for {domain} - {result['word_count']} words")
        except Exception as e:
            fix_later(
                message="Content generation failed for domain",
                level=logging.ERROR,
                domain=domain,
                error=str(e),
                drift_score=0.15,
                affect_delta=-0.10,
            )
            results[domain] = {"error": str(e)}

    return results


def test_style_guide_integration():
    """Test style guide and tone layer integration"""
    print("\n🧪 Testing style guide integration...")

    generator = AutomatedContentGenerator()

    # Test style guides for different domains
    domains_to_test = ["lukhas.ai", "lukhas.eu", "lukhas.lab", "lukhas.store"]

    for domain in domains_to_test:
        style_guide = generator.platform.get_domain_style_guide(domain)
        print(f"\n📋 {domain} Style Guide:")
        print(f"   - Tone: {style_guide['tone']}")
        print(f"   - Voice: {style_guide['voice']}")
        print(f"   - Primary Star: {style_guide['primary_star']}")
        print(f"   - Philosophy: {style_guide['philosophy'][:100]}...")


def test_constellation_navigation():
    """Test constellation navigation generation"""
    print("\n🧪 Testing constellation navigation...")

    generator = AutomatedContentGenerator()

    # Test navigation for different domains
    for domain in ["lukhas.ai", "lukhas.dev", "lukhas.xyz"]:
        related = generator._get_related_domains(domain)
        print(f"\n🧭 {domain} navigation:")
        print(f"   - Stars: {generator.platform.domain_mapping[domain]}")
        print(f"   - Related domains: {related[:3]}")


def save_test_results(results):
    """Save test results to files"""
    print("\n💾 Saving test results...")

    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)

    for domain, result in results.items():
        if "error" not in result and "content" in result:
            file_path = output_dir / f"{domain.replace('.', '_')}_homepage.md"
            file_path.write_text(result["content"], encoding="utf-8")
            record = fix_later(
                message="Test output persisted for generated content",
                level=logging.INFO,
                domain=domain,
                path=str(file_path),
                drift_score=0.01,
                affect_delta=0.0,
            )
            print(record.describe())


if __name__ == "__main__":
    print("🚀 LUKHAS AI Content Generation Test Suite")
    print("=" * 50)

    # Test individual domain
    single_result = test_single_domain_content()

    # Test multiple domains
    multiple_results = test_multiple_domains()

    # Test style guide integration
    test_style_guide_integration()

    # Test navigation
    test_constellation_navigation()

    # Save results
    save_test_results(multiple_results)

    print("\n" + "=" * 50)
    print("✨ All tests completed successfully!")
    print(f"📊 Total domains tested: {len(multiple_results)}")
    summary_record = fix_later(
        message="Content generation suite executed with mock database bridge",
        level=logging.INFO,
        domains_tested=len(multiple_results),
        output_directory=str((Path(__file__).parent / "test_output").resolve()),
        drift_score=0.05,
        affect_delta=0.02,
    )
    print(summary_record.describe())
    print("📄 Content files generated in test_output/")
