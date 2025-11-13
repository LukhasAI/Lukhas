#!/usr/bin/env python3
"""
LUKHAS Quickstart Example 3: Memory Persistence
================================================

Demonstrates context preservation across multiple interactions.
Shows how LUKHAS maintains conversation state and recalls previous context.

Expected output:
- Creation of memory fold
- Storage and retrieval of context
- Demonstration of memory recall

Troubleshooting:
- Ensure database is initialized: check lukhas_dev.db exists
- Check memory module imports correctly
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def main() -> None:
    """Demonstrate memory persistence."""
    print("🤖 LUKHAS Quickstart Example 3: Memory Persistence")
    print("=" * 60)
    print()

    print("📚 Demonstrating Memory Folds - Bio-Inspired Context Preservation")
    print()

    # Simulated conversation with memory
    conversation = [
        {
            "turn": 1,
            "user": "My favorite color is blue.",
            "assistant": "I'll remember that your favorite color is blue.",
            "memory_action": "STORE: user_preference.favorite_color = blue",
        },
        {
            "turn": 2,
            "user": "I'm working on a Python project.",
            "assistant": "Great! Tell me more about your Python project.",
            "memory_action": "STORE: user_context.current_project = Python",
        },
        {
            "turn": 3,
            "user": "What was my favorite color again?",
            "assistant": "Your favorite color is blue, as you mentioned earlier.",
            "memory_action": "RETRIEVE: user_preference.favorite_color → blue",
        },
    ]

    # Display conversation with memory operations
    for turn in conversation:
        print(f"\n{'─' * 60}")
        print(f"Turn {turn['turn']}")
        print(f"{'─' * 60}")
        print(f"\n👤 User: {turn['user']}")
        print(f"\n🤖 LUKHAS: {turn['assistant']}")
        print(f"\n🧠 Memory: {turn['memory_action']}")

    print(f"\n{'=' * 60}")
    print("\n📊 Memory Fold Statistics:")
    print()

    # Simulated memory fold structure
    memory_fold = {
        "fold_id": "mf_20250108_quickstart",
        "created_at": datetime.now().isoformat(),
        "entries": 2,
        "categories": {
            "user_preferences": {"favorite_color": "blue"},
            "user_context": {"current_project": "Python"},
        },
        "access_count": 3,
        "consolidation_status": "short_term",
    }

    print(f"   Fold ID: {memory_fold['fold_id']}")
    print(f"   Created: {memory_fold['created_at']}")
    print(f"   Entries: {memory_fold['entries']}")
    print(f"   Access Count: {memory_fold['access_count']}")
    print(f"   Status: {memory_fold['consolidation_status']}")
    print()

    print("📁 Stored Memories:")
    for category, data in memory_fold["categories"].items():
        print(f"\n   {category}:")
        for key, value in data.items():
            print(f"      • {key}: {value}")

    print("\n\n🔄 Memory Lifecycle:")
    print("""
    1. Short-term (current): Fast access, stored in memory
       ↓ (5 minutes of no access)
    2. Consolidation: Importance scoring
       ↓ (high importance score)
    3. Long-term: Persistent storage with semantic indexing
       ↓ (Ebbinghaus forgetting curve)
    4. Gradual forgetting: Strength decay unless accessed
    """)

    print("✅ Success! You've seen how LUKHAS preserves context.")
    print()
    print("💡 Key Concepts:")
    print("   - Memory Folds: Inspired by protein folding, memories fold into compact representations")
    print("   - Temporal Decay: Unused memories gradually fade (like biological forgetting)")
    print("   - Consolidation: Important memories get promoted to long-term storage")
    print()
    print("📚 Next steps:")
    print("   - Try example 04: python3 examples/quickstart/04_guardian_ethics.py")
    print("   - Deep dive: docs/ARCHITECTURE.md#memory-system")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("💡 Run 'lukhas troubleshoot' for help")
        sys.exit(1)
