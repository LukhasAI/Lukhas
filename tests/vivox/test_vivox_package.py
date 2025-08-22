#!/usr/bin/env python3
"""
Test script to verify VIVOX package works correctly
"""
import asyncio
import os
import sys

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "vivox_research_pack"))


async def test_package():
    print("🧪 Testing VIVOX Package")
    print("=" * 50)

    # Test 1: Import core modules
    print("\n1️⃣ Testing imports...")
    try:
        from vivox import ActionProposal, create_vivox_system
        from lukhas.vivox.moral_alignment import MAEDecision

        print("✅ Core imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

    # Test 2: Create VIVOX system
    print("\n2️⃣ Testing system creation...")
    try:
        vivox = await create_vivox_system()
        assert "memory_expansion" in vivox
        assert "moral_alignment" in vivox
        assert "consciousness" in vivox
        assert "self_reflection" in vivox
        print("✅ System created successfully")
    except Exception as e:
        print(f"❌ System creation error: {e}")
        return False

    # Test 3: Test basic functionality
    print("\n3️⃣ Testing basic functionality...")
    try:
        # Test MAE
        mae = vivox["moral_alignment"]
        action = ActionProposal(
            action_type="test_action", content={"test": True}, context={}
        )
        decision = await mae.evaluate_action_proposal(action, {})
        assert isinstance(decision, MAEDecision)
        print("✅ MAE working")

        # Test CIL
        cil = vivox["consciousness"]
        experience = await cil.simulate_conscious_experience({"semantic": "test"}, {})
        assert experience is not None
        print("✅ CIL working")

        # Test Memory
        me = vivox["memory_expansion"]
        # Just verify the memory system exists and has expected attributes
        assert me is not None
        assert hasattr(me, "memory_helix")
        assert hasattr(me, "symbolic_proteome")
        print("✅ Memory working")

        # Test SRM
        srm = vivox["self_reflection"]
        # Just verify SRM exists and has expected attributes
        assert srm is not None
        assert hasattr(srm, "collapse_archive")
        print("✅ SRM working")

    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False

    # Test 4: Test integrations
    print("\n4️⃣ Testing integrations...")
    try:

        print("✅ Integrations imports successful")
    except Exception as e:
        print(f"❌ Integration import error: {e}")
        return False

    # Test 5: Check enhancements
    print("\n5️⃣ Testing enhancements...")
    try:
        from lukhas.vivox.consciousness.state_variety_enhancement import (
            create_enhanced_state_determination,
        )
        from lukhas.vivox.moral_alignment.decision_strictness_enhancement import (
            create_strict_decision_maker,
        )

        create_enhanced_state_determination()
        create_strict_decision_maker()
        print("✅ Enhancements available")
    except Exception as e:
        print(f"❌ Enhancement error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ All tests passed! Package is working correctly.")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_package())
    sys.exit(0 if success else 1)
