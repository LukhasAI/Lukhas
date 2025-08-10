#!/usr/bin/env python3
"""
Simple test for dream engine integration without complex imports.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Simple test without importing the full reflection layer
def test_dream_imports():
    """Test if dream engines can be imported"""
    print("💭 Testing dream engine imports")

    # Test DreamDeliveryManager import
    try:
        from dream.core.dream_delivery_manager import DreamDeliveryManager

        print("✅ DreamDeliveryManager import successful")

        # Test basic initialization
        dream_config = {
            "output_channels": ["voice", "screen"],
            "use_symbolic_world": False,
        }
        dream_delivery = DreamDeliveryManager(dream_config)
        print("✅ DreamDeliveryManager initialization successful")

        # Test dream delivery
        test_dream = {
            "dream_id": "test_001",
            "content": "Test dream content",
            "intent": "test",
            "emotional_context": {"primary_emotion": "neutral", "intensity": 0.5},
        }

        result = dream_delivery.deliver_dream(test_dream, channels=["screen"])
        print(f"✅ Dream delivery test successful: {result['status']}")

        return True

    except Exception as e:
        print(f"⚠️ DreamDeliveryManager test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_dream_imports()
    if success:
        print("\n✨ Simple dream integration test passed!")
    else:
        print("\n❌ Simple dream integration test failed!")
        sys.exit(1)
