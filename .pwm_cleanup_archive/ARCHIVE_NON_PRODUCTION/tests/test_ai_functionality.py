#!/usr/bin/env python3
"""
Test actual AI functionality of LUKHAS modules
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the lukhas directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("LUKHAS AI FUNCTIONALITY TEST")
print("=" * 80)


async def test_core_functionality():
    """Test basic LUKHAS Core functionality"""
    print("\n1. Testing LUKHAS Core basic functionality...")
    try:
        from core import LukhasCore

        core = LukhasCore()
        status = core.get_status()

        print(f"   Core Status: {status['initialized']}")
        print(f"   State: {status['state']}")

        # Test processing
        response = await core.process({"input": "Hello LUKHAS"})
        print(f"   Response: {response['content']}")
        print("   ✓ Core functionality working")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_memory_creation():
    """Test memory system functionality"""
    print("\n2. Testing Memory System...")
    try:
        from memory.basic import InMemoryStore, MemoryEntry

        # Create a memory entry
        entry = MemoryEntry(
            content="LUKHAS AI test memory",
            metadata={"type": "test", "timestamp": datetime.now().isoformat()},
        )

        # Create memory store (use concrete implementation)
        store = InMemoryStore()
        memory_id = store.store(entry)

        # Retrieve memory
        retrieved = store.retrieve(memory_id)

        print(f"   Stored memory ID: {memory_id}")
        print(f"   Retrieved content: {retrieved.content}")
        print("   ✓ Memory system working")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_glyph_system():
    """Test GLYPH symbolic system"""
    print("\n3. Testing GLYPH Symbolic System...")
    try:
        from core.symbolic.glyphs import GlyphEngine

        engine = GlyphEngine()

        # Encode a concept
        concept = "consciousness"
        glyph = engine.encode_concept(concept)

        print(f"   Concept: {concept}")
        print(f"   GLYPH encoding: {glyph}")
        print("   ✓ GLYPH system working")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_consciousness_state():
    """Test consciousness module state"""
    print("\n4. Testing Consciousness Module...")
    try:
        from consciousness.systems.state import ConsciousnessState

        # Create consciousness state
        state = ConsciousnessState(
            level=0.5, awareness_type="focused", emotional_tone="neutral"
        )

        print(f"   Consciousness level: {state.level}")
        print(f"   Awareness type: {state.awareness_type}")
        print(f"   Emotional tone: {state.emotional_tone}")
        print("   ✓ Consciousness module working")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_ethics_compliance():
    """Test ethics engine"""
    print("\n5. Testing Ethics Engine...")
    try:
        from ethics.compliance import ComplianceValidator

        validator = ComplianceValidator()

        # Test an action
        action = {
            "type": "response",
            "content": "Hello, I'm here to help!",
            "context": {"user_intent": "greeting"},
        }

        is_compliant = validator.validate(action)

        print(f"   Action type: {action['type']}")
        print(f"   Compliance check: {'Passed' if is_compliant else 'Failed'}")
        print("   ✓ Ethics engine working")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


# Run all tests
async def main():
    results = []

    # Test 1: Core
    results.append(await test_core_functionality())

    # Test 2: Memory
    results.append(test_memory_creation())

    # Test 3: GLYPH
    results.append(test_glyph_system())

    # Test 4: Consciousness
    results.append(test_consciousness_state())

    # Test 5: Ethics
    results.append(test_ethics_compliance())

    # Summary
    print("\n" + "=" * 80)
    print("FUNCTIONALITY TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All functionality tests passed!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")

    return passed == total


# Run tests
if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
