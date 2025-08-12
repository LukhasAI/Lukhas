#!/usr/bin/env python3
"""
LUKHAS Tag Registry Demonstration
Shows how the tag system provides human interpretability
"""

import os
import sys

from core.tags import (
    explain_tag,
    get_decision_tags,
    get_hormone_tags,
    get_tag_registry,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demonstrate_tag_registry():
    """Demonstrate the tag registry capabilities"""
    print("=" * 60)
    print("LUKHAS TAG REGISTRY DEMONSTRATION")
    print("=" * 60)

    registry = get_tag_registry()

    # 1. Show total tags
    print(f"\n📊 Total tags in system: {len(registry.tags)}")

    # 2. Show categories
    print("\n📁 Tag Categories:")
    from core.tags import TagCategory

    for category in TagCategory:
        tags = registry.get_tags_by_category(category)
        print(f"  - {category.value}: {len(tags)} tags")

    # 3. Explain a specific tag
    print("\n🏷️  Tag Explanation Example:")
    print(explain_tag("#TAG:neuroplastic"))

    # 4. Show tag with context
    print("\n🔍 Tag Activation with Context:")
    context = {
        "situation": "system overload",
        "memory_usage": "95%",
        "response_time": "slow",
    }
    print(f"Context: {context}")
    print(explain_tag("#TAG:neuroplastic", context))

    # 5. Show hormone tags
    print("\n🧪 Hormone System Tags:")
    hormones = get_hormone_tags()
    for hormone in hormones:
        tag = registry.get_tag(hormone)
        if tag:
            print(f"\n  {hormone}:")
            print(f"    Meaning: {tag.human_meaning}")
            if tag.triggers:
                print(f"    Triggers: {', '.join(tag.triggers[:2])}...")
            if tag.effects:
                print(f"    Effects: {', '.join(tag.effects[:2])}...")

    # 6. Decision-related tags
    print("\n🤔 Decision Tags for 'ethical risk assessment':")
    decision_tags = get_decision_tags("ethical risk assessment")
    for tag_name in decision_tags:
        tag = registry.get_tag(tag_name)
        if tag:
            print(f"  - {tag_name}: {tag.description}")

    # 7. Show tag relationships
    print("\n🔗 Tag Relationships for #TAG:consciousness:")
    consciousness_tag = registry.get_tag("#TAG:consciousness")
    if consciousness_tag:
        print(f"  Related: {consciousness_tag.related_tags}")
        print(f"  Children: {consciousness_tag.child_tags}")
        related_depth2 = registry.get_related_tags("#TAG:consciousness", depth=2)
        print(f"  All related (depth 2): {related_depth2}")

    # 8. High priority tags
    print("\n⚡ High Priority Tags (priority <= 3):")
    report = registry.generate_tag_report()
    for tag_info in report["high_priority_tags"]:
        print(
            f"  - {tag_info['name']} (priority {tag_info['priority']}): {tag_info['meaning']}"
        )

    # 9. Simulate a decision with tags
    print("\n💭 Simulating Decision Process:")
    print("Decision: Should we reorganize memory systems due to high load?")

    # Check relevant tags
    relevant_tags = [
        "#TAG:neuroplastic",
        "#TAG:memory",
        "#TAG:cortisol",
        "#TAG:decision",
    ]
    print("\nChecking relevant tags:")

    decision_context = {
        "memory_load": "high",
        "system_stress": "elevated",
        "available_resources": "limited",
    }

    for tag_name in relevant_tags:
        tag = registry.get_tag(tag_name)
        if tag:
            print(f"\n  {tag_name}:")
            # Check if any triggers match
            triggered = False
            for trigger in tag.triggers:
                if any(
                    word in str(decision_context).lower()
                    for word in trigger.lower().split()
                ):
                    print(f"    ✓ Triggered by: {trigger}")
                    triggered = True
                    break

            if triggered and tag.effects:
                print(f"    → Will cause: {tag.effects[0]}")

    # 10. Export capability
    print("\n💾 Tag Registry Export:")
    print("  The registry can be exported to JSON for documentation")
    print("  Use: registry.export_to_json('tag_registry.json')")

    print("\n" + "=" * 60)
    print("Tag registry provides human-readable explanations for all")
    print("system behaviors, making LUKHAS decisions interpretable!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_tag_registry()
