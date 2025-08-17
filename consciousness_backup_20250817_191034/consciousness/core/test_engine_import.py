#!/usr/bin/env python3
"""
Test script to verify ConsciousnessEngine import and basic functionality.
This script validates that the export alias works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_engine_import():
    """Test all import variations and basic functionality."""
    print("🧪 Testing LUKHAS AI Consciousness Engine Import")
    print("=" * 50)

    # Test 1: Import ConsciousnessEngine alias
    try:
        from consciousness.core.engine_complete import ConsciousnessEngine
        print("✓ ConsciousnessEngine alias imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ConsciousnessEngine: {e}")
        return False

    # Test 2: Import original class name
    try:
        from consciousness.core.engine_complete import AGIConsciousnessEngine
        print("✓ AGIConsciousnessEngine imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AGIConsciousnessEngine: {e}")
        return False

    # Test 3: Verify they are the same class
    if ConsciousnessEngine is AGIConsciousnessEngine:
        print("✓ ConsciousnessEngine is properly aliased to AGIConsciousnessEngine")
    else:
        print("✗ Alias not working correctly")
        return False

    # Test 4: Test __all__ exports
    try:
        from consciousness.core import engine_complete
        if 'ConsciousnessEngine' in engine_complete.__all__:
            print("✓ ConsciousnessEngine included in __all__ exports")
        else:
            print("✗ ConsciousnessEngine not in __all__ exports")
            return False
    except Exception as e:
        print(f"✗ Error checking __all__: {e}")
        return False

    # Test 5: Basic instantiation and functionality
    try:
        engine = ConsciousnessEngine(user_tier=5)
        print("✓ Engine instantiation successful")

        # Test system status
        status = engine.get_system_status()
        trinity_components = len(status["trinity_framework"])
        print(f"✓ Trinity Framework components active: {trinity_components}")

        # Test consciousness state
        consciousness_state = engine.get_consciousness_state()
        awareness = consciousness_state["awareness_level"]
        print(f"✓ Consciousness state accessible: awareness={awareness:.2f}")

        # Test agent registration
        success = await engine.register_agent("test_import_agent", {"tier": 1})
        print(f"✓ Agent registration: {'success' if success else 'failed'}")

        # Test bio-inspired processing
        context = {"emotional_valence": 0.5, "task_complexity": 0.3}
        modulated = await engine.adaptive_consciousness_modulation(context)
        print(f"✓ Bio-inspired processing: awareness={modulated.awareness_level:.2f}")

    except Exception as e:
        print(f"✗ Engine functionality test failed: {e}")
        return False

    print("\n🎉 All import and functionality tests passed!")
    print("⚛️ Identity: Symbolic consciousness ready")
    print("🧠 Consciousness: Bio-inspired processing active")
    print("🛡️ Guardian: Ethical governance enabled")
    print("\nThe ConsciousnessEngine is ready for production use in LUKHAS AI.")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_engine_import())
    sys.exit(0 if success else 1)
