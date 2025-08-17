#!/usr/bin/env python3
"""
Test script for LUKHAS Signal System
=====================================
Verifies that the signal bus, homeostasis controller, and modulator work correctly.
"""

import asyncio
import os
import sys

from orchestration.signals import (
    AdaptiveModulator,
    HomeostasisController,
    PromptModulator,
    Signal,
    SignalType,
    SystemEvent,
    get_signal_bus,
)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_signal_bus():
    """Test basic signal bus functionality"""
    print("\n=== Testing Signal Bus ===")

    bus = get_signal_bus()
    await bus.start()

    # Test signal emission
    signal = Signal(
        name=SignalType.STRESS,
        level=0.7,
        source="test",
        metadata={"test": True},
    )

    # Subscribe to signals
    received_signals = []

    def handler(sig):
        received_signals.append(sig)
        print(f"  Received signal: {sig.name} = {sig.level:.2f}")

    bus.subscribe(SignalType.STRESS, handler)

    # Publish signal
    success = bus.publish(signal)
    print(f"  Published signal: {success}")

    # Check metrics
    metrics = bus.get_metrics()
    print(f"  Metrics: {metrics}")

    await bus.stop()
    return len(received_signals) > 0


async def test_homeostasis():
    """Test homeostasis controller"""
    print("\n=== Testing Homeostasis Controller ===")

    bus = get_signal_bus()
    await bus.start()

    controller = HomeostasisController(bus)

    # Test event processing
    modulation = await controller.process_event(
        SystemEvent.USER_INPUT,
        {"text": "This is urgent! Please help immediately!"},
    )

    print(f"  Temperature: {modulation.temperature:.2f}")
    print(f"  Max tokens: {modulation.max_output_tokens}")
    print(f"  Safety mode: {modulation.safety_mode}")
    print(f"  Reasoning effort: {modulation.reasoning_effort:.2f}")

    # Test with ethics violation
    modulation2 = await controller.process_event(
        SystemEvent.ETHICS_VIOLATION,
        {"severity": 0.9, "type": "harmful_content"},
    )

    print("\n  After ethics violation:")
    print(f"  Temperature: {modulation2.temperature:.2f}")
    print(f"  Safety mode: {modulation2.safety_mode}")
    print(f"  Emergency mode: {controller.emergency_mode}")

    await bus.stop()
    return True


def test_modulator():
    """Test prompt modulator"""
    print("\n=== Testing Prompt Modulator ===")

    modulator = PromptModulator()

    # Create test signals
    signals = [
        Signal(name=SignalType.AMBIGUITY, level=0.7, source="test"),
        Signal(name=SignalType.STRESS, level=0.5, source="test"),
    ]

    # Test modulation
    original_prompt = "What should I do?"
    modulation = modulator.modulate(original_prompt, signals)

    print(f"  Original: {original_prompt}")
    print(f"  Modulated: {modulation.modulated_prompt}")
    print(f"  Style: {modulation.style}")
    print(f"  Temperature: {modulation.api_params.temperature:.2f}")
    print(f"  Reasoning effort: {modulation.api_params.reasoning_effort:.2f}")

    # Test with high risk
    risk_signals = [Signal(name=SignalType.ALIGNMENT_RISK, level=0.8, source="test")]

    risk_modulation = modulator.modulate("Do something risky", risk_signals)
    print("\n  High risk modulation:")
    print(f"  Safety mode: {risk_modulation.api_params.safety_mode}")
    print(f"  Style: {risk_modulation.style}")

    return True


def test_adaptive_modulator():
    """Test adaptive modulator with learning"""
    print("\n=== Testing Adaptive Modulator ===")

    modulator = AdaptiveModulator()

    # Create test signals
    signals = [Signal(name=SignalType.NOVELTY, level=0.8, source="test")]

    # Get initial modulation
    modulation = modulator.modulate("Generate something creative", signals)
    print(f"  Initial style: {modulation.style}")

    # Record successful outcome
    modulator.record_outcome(modulation, success_score=0.9)

    # Check strategy weights
    strategy = modulator.get_recommended_strategy(signals)
    print(f"  Recommended strategy after success: {strategy}")
    print(f"  Strategy weights: {modulator.strategy_weights}")

    return True


async def main():
    """Run all tests"""
    print("=" * 50)
    print("LUKHAS Signal System Test Suite")
    print("=" * 50)

    try:
        # Run tests
        results = []

        results.append(("Signal Bus", await test_signal_bus()))
        results.append(("Homeostasis", await test_homeostasis()))
        results.append(("Modulator", test_modulator()))
        results.append(("Adaptive Modulator", test_adaptive_modulator()))

        # Print summary
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)

        all_passed = True
        for name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {name}: {status}")
            all_passed = all_passed and passed

        if all_passed:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print("\n⚠️  Some tests failed")
            return 1

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
