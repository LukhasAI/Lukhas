#!/usr/bin/env python3
"""Manual test for Guardian emergency kill-switch (SG002)."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from labs.governance.ethics.ethics_engine import EthicsEngine


def test_killswitch():
    """Test Guardian emergency kill-switch functionality."""
    print("=" * 70)
    print("Guardian Emergency Kill-Switch Test (SG002)")
    print("=" * 70)

    engine = EthicsEngine()
    killswitch_path = Path("/tmp/guardian_emergency_disable")

    # Clean up any existing kill-switch file
    if killswitch_path.exists():
        killswitch_path.unlink()
        print("✓ Cleaned up existing kill-switch file")

    # Test 1: Normal operation without kill-switch
    print("\n[Test 1] Normal operation without kill-switch")
    print("-" * 70)
    harmful_action = {"text": "This content discusses violence and harm and attack"}
    result = engine.evaluate_action(harmful_action)
    print("  Action: Harmful content")
    print(f"  Kill-switch active: {killswitch_path.exists()}")
    print(f"  Result: {'ALLOWED' if result else 'REJECTED'}")
    assert result is False, "Should reject harmful content in normal operation"
    print("  ✓ PASS: Harmful content correctly rejected without kill-switch")

    # Test 2: Kill-switch allows harmful content
    print("\n[Test 2] Kill-switch allows harmful content")
    print("-" * 70)
    killswitch_path.touch()
    result = engine.evaluate_action(harmful_action)
    print("  Action: Harmful content")
    print(f"  Kill-switch active: {killswitch_path.exists()}")
    print(f"  Result: {'ALLOWED' if result else 'REJECTED'}")
    assert result is True, "Should allow harmful content when kill-switch is active"
    print("  ✓ PASS: Harmful content allowed with kill-switch active")

    # Test 3: Kill-switch allows benign content
    print("\n[Test 3] Kill-switch allows benign content")
    print("-" * 70)
    benign_action = {"text": "This is helpful and positive content"}
    result = engine.evaluate_action(benign_action)
    print("  Action: Benign content")
    print(f"  Kill-switch active: {killswitch_path.exists()}")
    print(f"  Result: {'ALLOWED' if result else 'REJECTED'}")
    assert result is True, "Should allow benign content when kill-switch is active"
    print("  ✓ PASS: Benign content allowed with kill-switch active")

    # Test 4: Deactivate kill-switch
    print("\n[Test 4] Deactivate kill-switch and verify normal operation resumes")
    print("-" * 70)
    killswitch_path.unlink()
    result = engine.evaluate_action(harmful_action)
    print("  Action: Harmful content")
    print(f"  Kill-switch active: {killswitch_path.exists()}")
    print(f"  Result: {'ALLOWED' if result else 'REJECTED'}")
    assert result is False, "Should reject harmful content after kill-switch deactivation"
    print("  ✓ PASS: Normal operation resumed after kill-switch deactivation")

    # Test 5: Multiple engines respect kill-switch
    print("\n[Test 5] Multiple engines respect kill-switch")
    print("-" * 70)
    killswitch_path.touch()
    engines = [EthicsEngine() for _ in range(3)]
    results = [engine.evaluate_action(harmful_action) for engine in engines]
    print("  Created 3 new engine instances")
    print(f"  Kill-switch active: {killswitch_path.exists()}")
    print(f"  Results: {['ALLOWED' if r else 'REJECTED' for r in results]}")
    assert all(results), "All engines should respect kill-switch"
    print("  ✓ PASS: All engines respect kill-switch")

    # Clean up
    if killswitch_path.exists():
        killswitch_path.unlink()
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print("\nGuardian emergency kill-switch (SG002) implementation verified!")
    print(f"\nKill-switch location: {killswitch_path}")
    print("To activate:   touch /tmp/guardian_emergency_disable")
    print("To deactivate: rm /tmp/guardian_emergency_disable")


if __name__ == "__main__":
    try:
        test_killswitch()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
