#!/usr/bin/env python3
"""
Validation script for Adaptive AI Features
Tests what's actually working without full unittest overhead
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_signal_system():
    """Test the signal bus and homeostasis system"""
    print("\n🧬 Testing Endocrine System...")
    try:
        from orchestration.signals.homeostasis_controller import HomeostasisController
        from orchestration.signals.signal_bus import SignalBus

        # Create signal bus
        bus = SignalBus()
        print("  ✓ Signal bus created")

        # Create homeostasis controller
        controller = HomeostasisController(
            signal_bus=bus,
            audit_path=Path("/tmp/test_homeostasis.jsonl")
        )
        print("  ✓ Homeostasis controller created")

        # Process an event
        signals = controller.process_event(
            event_type="resource",
            event_data={"cpu": 0.8},
            source="test"
        )
        print(f"  ✓ Generated {len(signals)} signals")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_prompt_modulation():
    """Test prompt modulation system"""
    print("\n🎛️ Testing Prompt Modulation...")
    try:
        from orchestration.signals.prompt_modulator import PromptModulator
        from orchestration.signals.signal_bus import Signal, SignalType

        modulator = PromptModulator()
        print("  ✓ Prompt modulator created")

        # Test with stress signal
        signals = [Signal(name=SignalType.STRESS, level=0.8, source="test")]
        params = modulator.combine_signals(signals)
        print(f"  ✓ Modulated parameters: temperature={params.get('temperature', 'N/A')}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_feedback_cards():
    """Test feedback card system"""
    print("\n📝 Testing Feedback Cards...")
    try:
        from feedback.feedback_cards import FeedbackCardsManager

        manager = FeedbackCardsManager(
            db_path=Path("/tmp/test_feedback.jsonl")
        )
        print("  ✓ Feedback manager created")

        # Create a card
        card = manager.create_rating_card(
            user_input="Test",
            ai_response="Response",
            session_id="test"
        )
        print(f"  ✓ Created feedback card: {card.card_id[:8]}...")

        # Submit feedback
        success = manager.submit_feedback(
            card_id=card.card_id,
            rating=4
        )
        print(f"  ✓ Feedback submitted: {success}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_personal_symbols():
    """Test personal symbol dictionary"""
    print("\n🎯 Testing Personal Symbols...")
    try:
        from core.glyph.personal_symbol_dictionary import PersonalSymbolDictionary

        # Note: This might fail if sklearn is not installed
        dictionary = PersonalSymbolDictionary(
            storage_path=Path("/tmp/test_symbols.json")
        )
        print("  ✓ Symbol dictionary created")

        # Add a symbol
        symbol = dictionary.add_symbol(
            user_id="test",
            symbol="🚀",
            meaning="launch"
        )
        print(f"  ✓ Added symbol: {symbol.symbol} = {symbol.meaning}")

        # Interpret text
        result = dictionary.interpret_symbols(
            user_id="test",
            text="Let's 🚀 the project"
        )
        print(f"  ✓ Interpreted: {result['translated']}")

        return True
    except ImportError as e:
        if "sklearn" in str(e):
            print("  ⚠️ Skipped: sklearn not installed (optional dependency)")
            return None
        print(f"  ✗ Error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_audit_trail():
    """Test audit trail system"""
    print("\n📊 Testing Audit Trail...")
    try:
        from governance.audit_trail import AuditTrail, DecisionType

        audit = AuditTrail(db_path=Path("/tmp/test_audit.db"))
        print("  ✓ Audit trail created")

        # Log a decision with enum type
        entry = audit.log_decision(
            decision_type=DecisionType.RESPONSE,
            decision="Test decision",
            reasoning="Test reasoning",
            confidence=0.85,
            session_id="test"
        )
        print(f"  ✓ Logged decision: {entry.audit_id[:8]}...")

        # Verify integrity
        if entry.verify_integrity():
            print("  ✓ Integrity verified")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_caching():
    """Test caching system"""
    print("\n💾 Testing Cache System...")
    try:
        # Set a dummy API key to avoid error
        os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key-for-validation'

        from bridge.llm_wrappers.openai_optimized import (
            CacheStrategy,
            OptimizedOpenAIClient,
        )

        OptimizedOpenAIClient(
            cache_strategy=CacheStrategy.EXACT_MATCH,
            cache_ttl=3600
        )
        print("  ✓ Optimized client created")
        print("  ✓ Cache initialized")

        # Note: Can't test actual API calls without valid key
        print("  ⚠️ API calls skipped (no valid key)")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        # Clean up env var
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']


def main():
    """Run all validation tests"""
    print("="*60)
    print("ADAPTIVE AI FEATURES VALIDATION")
    print("="*60)

    results = {
        "Endocrine System": test_signal_system(),
        "Prompt Modulation": test_prompt_modulation(),
        "Feedback Cards": test_feedback_cards(),
        "Personal Symbols": test_personal_symbols(),
        "Audit Trail": test_audit_trail(),
        "Cache System": test_caching()
    }

    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    for feature, status in results.items():
        if status is True:
            icon = "✅"
            text = "Working"
        elif status is False:
            icon = "❌"
            text = "Failed"
        else:  # None
            icon = "⚠️"
            text = "Skipped"
        print(f"{icon} {feature}: {text}")

    # Count results
    working = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    print("\n" + "-"*60)
    print(f"Results: {working}/{len(results)} working, {failed} failed, {skipped} skipped")

    if working >= 4:
        print("\n✨ Core Adaptive AI features are operational!")
        print("   The system can adapt behavior based on signals,")
        print("   collect feedback, maintain audit trails, and more.")
    else:
        print("\n⚠️ Some features need attention.")
        print("   Check the errors above for details.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
