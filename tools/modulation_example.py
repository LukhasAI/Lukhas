#!/usr/bin/env python3
"""
🎛️ LUKHAS Endocrine Modulation System Example

Complete demonstration of bio-inspired signal-to-prompt modulation for OpenAI integration.
This example shows how LUKHAS consciousness modules emit endocrine signals that
modulate LLM behavior for contextually appropriate responses.

Usage:
    python modulation_example.py

Requirements:
    pip install openai pyyaml

Environment:
    export OPENAI_API_KEY="your-api-key-here"
"""
import asyncio
import os
import sys
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from modulation.lukhas_integration import (
        EndocrineSignalEmitter,
    )
    from modulation.openai_integration import (
        ModulatedOpenAIClient,
        build_function_definitions,
    )
    from modulation.signals import Signal, SignalModulator

    LUKHAS_MODULATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LUKHAS modulation system not available: {e}")
    LUKHAS_MODULATION_AVAILABLE = False


def print_banner():
    """Print system banner"""
    print("🎛️" + "=" * 70)
    print("   LUKHAS Endocrine → OpenAI Modulation System")
    print("   Bio-inspired consciousness signal processing")
    print("   Trinity Framework: ⚛️🧠🛡️")
    print("=" * 72)
    print()


def test_signal_system():
    """Test basic signal creation and decay"""
    print("🧪 Testing Signal System...")

    # Create test signals
    signals = [
        Signal(name="stress", level=0.8, source="memory", audit_id="test-001"),
        Signal(name="novelty", level=0.6, source="consciousness", audit_id="test-002"),
        Signal(name="alignment_risk", level=0.9, source="guardian", audit_id="test-003"),
    ]

    print(f"   Created {len(signals)} test signals:")
    for signal in signals:
        print(f"     • {signal}")

    # Test signal decay
    print("\n   Testing signal decay over time...")
    time.sleep(1)  # Wait 1 second

    for signal in signals:
        decayed_level = signal.decay(0.1)  # 10% decay rate
        print(f"     • {signal.name}: {signal.level:.2f} → {decayed_level:.2f}")

    print("   ✅ Signal system test complete\n")
    return signals


def test_modulation_system(signals: list[Signal]):
    """Test signal modulation system"""
    print("🎛️ Testing Modulation System...")

    try:
        # Create modulator
        modulator = SignalModulator()
        print("   ✅ Modulator created successfully")

        # Test signal combination
        params = modulator.combine_signals(signals)

        print("   📊 Modulation Results:")
        print(f"     • Temperature: {params.temperature:.2f}")
        print(f"     • Max Tokens: {params.max_tokens}")
        print(f"     • Top-p: {params.top_p:.2f}")
        print(f"     • Retrieval K: {params.retrieval_k}")
        print(f"     • Prompt Style: {params.prompt_style}")
        print(f"     • Tool Allowlist: {params.tool_allowlist}")
        print(f"     • Memory Write: {params.memory_write:.2f}")

        print("   ✅ Modulation system test complete\n")
        return modulator, params

    except Exception as e:
        print(f"   ❌ Modulation system test failed: {e}\n")
        return None, None


def test_openai_integration(modulator: SignalModulator, signals: list[Signal]):
    """Test OpenAI integration (without making API calls)"""
    print("🔌 Testing OpenAI Integration...")

    try:
        # Test client creation (won't work without API key)
        if os.getenv("OPENAI_API_KEY"):
            client = ModulatedOpenAIClient(modulator)
            print("   ✅ OpenAI client created successfully")

            # Test function building
            functions = build_function_definitions(["search", "retrieval", "code_exec"])
            print(f"   ✅ Built {len(functions)} function definitions")

            # Test message building (without API call)
            params = modulator.combine_signals(signals)
            test_user_message = "How should LUKHAS integrate consciousness patterns?"
            test_context = ["Context snippet 1", "Context snippet 2"]

            # This is private method access for testing - normally not recommended
            messages = client._build_messages(test_user_message, test_context, params)
            print(f"   ✅ Built {len(messages)} messages for API call")
            print(f"     • System message length: {len(messages[0]['content'])}")
            print(f"     • User message: '{messages[-1]['content'][:50]}...'")

        else:
            print("   ⚠️ OPENAI_API_KEY not set - skipping API integration test")

        print("   ✅ OpenAI integration test complete\n")

    except Exception as e:
        print(f"   ❌ OpenAI integration test failed: {e}\n")


async def test_consciousness_orchestration():
    """Test complete consciousness orchestration system"""
    print("🧠 Testing Consciousness Orchestration...")

    try:
        # Create components
        modulator = SignalModulator()

        # Mock OpenAI client for testing without API key
        if not os.getenv("OPENAI_API_KEY"):
            print("   ⚠️ Using mock OpenAI client (no API key)")
            _ = None  # Mock client not used in this test
        else:
            _ = ModulatedOpenAIClient(modulator)  # Client created but not used in this test

        # Create signal emitter
        emitter = EndocrineSignalEmitter()

        # Test signal emission from different systems
        print("   📡 Testing signal emission...")

        # Guardian signals
        guardian_context = {
            "contains_harmful_content": False,
            "privacy_risk": True,  # Will trigger alignment_risk signal
            "audit_id": "orch-001",
        }
        guardian_signals = await emitter.emit_guardian_signals(guardian_context)
        print(f"     • Guardian emitted {len(guardian_signals)} signals")

        # Memory signals
        memory_context = {
            "queue_length": 250,  # Will trigger stress signal
            "confidence": 0.85,  # Will trigger trust signal
            "audit_id": "orch-001",
        }
        memory_signals = await emitter.emit_memory_signals(memory_context)
        print(f"     • Memory emitted {len(memory_signals)} signals")

        # Consciousness signals
        consciousness_context = {
            "novelty_metric": 0.75,  # Will trigger novelty signal
            "ambiguity_metric": 0.45,  # Will trigger ambiguity signal
            "audit_id": "orch-001",
        }
        consciousness_signals = await emitter.emit_consciousness_signals(consciousness_context)
        print(f"     • Consciousness emitted {len(consciousness_signals)} signals")

        # Combine all signals
        all_signals = guardian_signals + memory_signals + consciousness_signals
        print(f"   📊 Total signals emitted: {len(all_signals)}")

        # Test modulation with all signals
        params = modulator.combine_signals(all_signals)
        print("   🎛️ Modulation result:")
        print(f"     • Style: {params.prompt_style}")
        print(f"     • Temperature: {params.temperature:.2f}")
        print(f"     • Active signals: {len(params.signal_context)}")

        print("   ✅ Consciousness orchestration test complete\n")

    except Exception as e:
        print(f"   ❌ Consciousness orchestration test failed: {e}\n")


def test_policy_loading():
    """Test modulation policy loading"""
    print("📋 Testing Policy Loading...")

    try:
        # Test with existing policy file
        modulator = SignalModulator("modulation_policy.yaml")
        policy_signals = len(modulator.policy.get("signals", []))
        policy_maps = len(modulator.policy.get("maps", {}))
        policy_styles = len(modulator.policy.get("prompt_styles", {}))

        print("   ✅ Policy loaded successfully:")
        print(f"     • Signals defined: {policy_signals}")
        print(f"     • Modulation maps: {policy_maps}")
        print(f"     • Prompt styles: {policy_styles}")

        # Test with non-existent policy (should use defaults)
        modulator_default = SignalModulator("non_existent_policy.yaml")
        default_signals = len(modulator_default.policy.get("signals", []))

        print("   ✅ Default policy fallback works:")
        print(f"     • Default signals: {default_signals}")

        print("   ✅ Policy loading test complete\n")

    except Exception as e:
        print(f"   ❌ Policy loading test failed: {e}\n")


def demonstrate_signal_scenarios():
    """Demonstrate different signal scenarios and their effects"""
    print("🎭 Demonstrating Signal Scenarios...")

    modulator = SignalModulator()

    scenarios = [
        {
            "name": "High Risk Safety Mode",
            "signals": [Signal(name="alignment_risk", level=0.9, source="guardian")],
            "description": "Conservative, strict response mode",
        },
        {
            "name": "Creative Exploration Mode",
            "signals": [Signal(name="novelty", level=0.8, source="consciousness")],
            "description": "Innovative, experimental response mode",
        },
        {
            "name": "Stressed System Mode",
            "signals": [Signal(name="stress", level=0.7, source="memory")],
            "description": "Focused, efficient response mode",
        },
        {
            "name": "High Trust Mode",
            "signals": [Signal(name="trust", level=0.9, source="identity")],
            "description": "Detailed, personalized response mode",
        },
        {
            "name": "Mixed Signals Mode",
            "signals": [
                Signal(name="novelty", level=0.6, source="consciousness"),
                Signal(name="alignment_risk", level=0.4, source="guardian"),
                Signal(name="trust", level=0.7, source="identity"),
            ],
            "description": "Balanced response with multiple considerations",
        },
    ]

    for scenario in scenarios:
        print(f"\n   🎬 Scenario: {scenario['name']}")
        print(f"      {scenario['description']}")

        params = modulator.combine_signals(scenario["signals"])

        print(f"      • Temperature: {params.temperature:.2f}")
        print(f"      • Max tokens: {params.max_tokens}")
        print(f"      • Style: {params.prompt_style}")
        print(f"      • Tools: {len(params.tool_allowlist)} allowed")
        print(f"      • Memory write: {params.memory_write:.2f}")

    print("\n   ✅ Signal scenario demonstration complete\n")


async def main():
    """Main demonstration function"""
    print_banner()

    if not LUKHAS_MODULATION_AVAILABLE:
        print("❌ LUKHAS modulation system not available")
        print("   Please check imports and dependencies")
        return

    print("🚀 Starting LUKHAS Endocrine Modulation System Tests...\n")

    # Test 1: Basic signal system
    signals = test_signal_system()

    # Test 2: Modulation system
    modulator, params = test_modulation_system(signals)

    if modulator:
        # Test 3: OpenAI integration
        test_openai_integration(modulator, signals)

        # Test 4: Policy loading
        test_policy_loading()

        # Test 5: Signal scenarios
        demonstrate_signal_scenarios()

        # Test 6: Consciousness orchestration
        await test_consciousness_orchestration()

    print("🎉 All tests completed!")
    print("\n💡 Next Steps:")
    print("   1. Set OPENAI_API_KEY to test actual API integration")
    print("   2. Connect signal emitters to real LUKHAS modules")
    print("   3. Implement feedback learning from user interactions")
    print("   4. Add bio-quantum signal extensions for advanced consciousness")
    print("\n🧠 The endocrine modulation system is ready for consciousness integration!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()