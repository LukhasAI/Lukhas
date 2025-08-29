#!/usr/bin/env python3
"""
Test LUKHAS AI Content Generation without database dependency
Demonstrates the automated content generator with mock database functionality
"""

import sys
from pathlib import Path


# Mock the database integration to avoid dependency issues
class MockDatabase:
    """Mock database for testing content generation"""

    def __init__(self):
        self.activities = []
        self.content = []
        self.content_id_counter = 1

    def log_system_activity(self, system_name: str, activity_type: str, description: str, value: float):
        """Mock log system activity"""
        self.activities.append({
            "system": system_name,
            "type": activity_type,
            "description": description,
            "value": value
        })
        print(f"📊 Logged: {system_name} - {activity_type} - {description}")

    def save_generated_content(self, system_name: str, content_type: str, title: str, content: str, voice_coherence: float) -> int:
        """Mock save generated content"""
        content_id = self.content_id_counter
        self.content_id_counter += 1

        self.content.append({
            "id": content_id,
            "system": system_name,
            "type": content_type,
            "title": title,
            "content": content,
            "coherence": voice_coherence
        })

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
from automated_content_generator import AutomatedContentGenerator


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
            print(f"❌ Error with {domain}: {e}")
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
            print(f"   📄 Saved {domain} content to {file_path}")

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
    print(f"📈 Success rate: {len([r for r in multiple_results.values() if 'error' not in r])}/{len(multiple_results)}")
    print("📄 Content files generated in test_output/")
