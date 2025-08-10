#!/usr/bin/env python3
"""
Test suite for LUKHAS Adaptive AI Features
Tests the endocrine system, feedback cards, personal symbols, and audit trail
"""

import unittest
import asyncio
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEndocrineSystem(unittest.TestCase):
    """Test the AI endocrine system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from orchestration.signals.signal_bus import SignalBus
        from orchestration.signals.homeostasis_controller import HomeostasisController
        
        self.signal_bus = SignalBus()
        self.homeostasis = HomeostasisController(
            signal_bus=self.signal_bus,
            audit_path=Path("/tmp/test_homeostasis.jsonl")
        )
    
    def test_signal_emission(self):
        """Test that signals are emitted correctly"""
        # Process a high-stress event
        signals = self.homeostasis.process_event(
            event_type="resource",
            event_data={"cpu": 0.9, "memory": 0.8},
            source="test"
        )
        
        # Should emit stress signal
        self.assertTrue(any(s.name == "stress" for s in signals))
        
        # Check stress level
        stress_signal = next(s for s in signals if s.name == "stress")
        self.assertGreater(stress_signal.value, 0.5)
    
    def test_cooldown_mechanism(self):
        """Test hormone cooldown periods"""
        # Emit signal
        signals1 = self.homeostasis.process_event(
            event_type="novelty",
            event_data={"pattern": "unknown", "confidence": 0.2},
            source="test"
        )
        
        # Immediate re-emission should be limited
        signals2 = self.homeostasis.process_event(
            event_type="novelty",
            event_data={"pattern": "unknown", "confidence": 0.2},
            source="test"
        )
        
        # Second emission should be dampened or empty due to cooldown
        self.assertTrue(
            len(signals2) == 0 or 
            (len(signals2) > 0 and signals2[0].value < signals1[0].value)
        )


class TestPromptModulation(unittest.TestCase):
    """Test signal-to-prompt modulation"""
    
    def setUp(self):
        """Set up test fixtures"""
        from orchestration.signals.prompt_modulator import PromptModulator
        from orchestration.signals.signal_bus import Signal
        
        self.modulator = PromptModulator()
        self.Signal = Signal
    
    def test_stress_modulation(self):
        """Test that stress reduces temperature"""
        signals = [
            self.Signal(name="stress", value=0.8, source="test")
        ]
        
        params = self.modulator.combine_signals(signals)
        
        # High stress should reduce temperature
        self.assertLess(params.get("temperature", 1.0), 0.5)
    
    def test_novelty_modulation(self):
        """Test that novelty increases creativity"""
        signals = [
            self.Signal(name="novelty", value=0.9, source="test")
        ]
        
        params = self.modulator.combine_signals(signals)
        
        # High novelty should increase temperature
        self.assertGreater(params.get("temperature", 0), 0.7)
    
    def test_combined_signals(self):
        """Test combining multiple signals"""
        signals = [
            self.Signal(name="stress", value=0.6, source="test"),
            self.Signal(name="trust", value=0.8, source="test")
        ]
        
        params = self.modulator.combine_signals(signals)
        
        # Should have modulated parameters
        self.assertIn("temperature", params)
        self.assertIn("max_tokens", params)


class TestFeedbackCards(unittest.TestCase):
    """Test the feedback card system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from feedback.feedback_cards import FeedbackCardsManager
        
        self.manager = FeedbackCardsManager(
            storage_path=Path("/tmp/test_feedback.jsonl")
        )
    
    def test_create_rating_card(self):
        """Test creating a rating feedback card"""
        card = self.manager.create_rating_card(
            user_input="Test question",
            ai_response="Test answer",
            session_id="test_session"
        )
        
        self.assertIsNotNone(card.card_id)
        self.assertEqual(card.feedback_type, "rating")
        self.assertEqual(card.session_id, "test_session")
    
    def test_submit_feedback(self):
        """Test submitting feedback"""
        card = self.manager.create_rating_card(
            user_input="Test",
            ai_response="Response",
            session_id="test"
        )
        
        success = self.manager.submit_feedback(
            card_id=card.card_id,
            rating=4,
            comment="Good response"
        )
        
        self.assertTrue(success)
        self.assertNotIn(card.card_id, self.manager.active_cards)
    
    def test_impact_calculation(self):
        """Test impact score calculation"""
        card = self.manager.create_correction_card(
            user_input="What is 2+2?",
            ai_response="5",
            session_id="test"
        )
        
        self.manager.submit_feedback(
            card_id=card.card_id,
            correction="4",
            reason="Math error"
        )
        
        # Check that impact was calculated
        completed = self.manager.completed_cards[-1]
        self.assertGreater(completed.impact_score, 0)


class TestPersonalSymbols(unittest.TestCase):
    """Test personal symbol dictionary"""
    
    def setUp(self):
        """Set up test fixtures"""
        from core.glyph.personal_symbol_dictionary import PersonalSymbolDictionary
        
        self.dictionary = PersonalSymbolDictionary(
            storage_path=Path("/tmp/test_symbols.json")
        )
    
    def test_add_symbol(self):
        """Test adding a personal symbol"""
        symbol = self.dictionary.add_symbol(
            user_id="test_user",
            symbol="🚀",
            meaning="start project"
        )
        
        self.assertEqual(symbol.symbol, "🚀")
        self.assertEqual(symbol.meaning, "start project")
        self.assertEqual(symbol.user_id, "test_user")
    
    def test_interpret_symbols(self):
        """Test interpreting text with symbols"""
        self.dictionary.add_symbol("test_user", "🚀", "launch")
        self.dictionary.add_symbol("test_user", "🎯", "target")
        
        result = self.dictionary.interpret_symbols(
            user_id="test_user",
            text="Let's 🚀 the new 🎯"
        )
        
        self.assertIn("launch", result["translated"])
        self.assertIn("target", result["translated"])
        self.assertEqual(len(result["symbols_found"]), 2)
    
    def test_symbol_evolution(self):
        """Test symbol confidence evolution"""
        symbol = self.dictionary.add_symbol("test_user", "🔧", "fix")
        initial_confidence = symbol.confidence
        
        # Use the symbol successfully
        for _ in range(5):
            self.dictionary.learn_from_usage(
                user_id="test_user",
                symbol="🔧",
                context="Let's 🔧 the bug",
                success=True
            )
        
        # Get updated symbol
        updated = self.dictionary.get_symbol("test_user", "🔧")
        self.assertGreater(updated.confidence, initial_confidence)
        self.assertGreater(updated.frequency, 5)


class TestAuditTrail(unittest.TestCase):
    """Test the audit trail system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from governance.audit_trail import AuditTrail
        
        self.audit = AuditTrail(
            db_path=Path("/tmp/test_audit.db")
        )
    
    def test_log_decision(self):
        """Test logging a decision"""
        entry = self.audit.log_decision(
            decision_type="response",
            decision="Generated response",
            reasoning="Based on user query",
            confidence=0.85,
            session_id="test_session"
        )
        
        self.assertIsNotNone(entry.audit_id)
        self.assertEqual(entry.decision_type, "response")
        self.assertEqual(entry.confidence, 0.85)
    
    def test_decision_explanation(self):
        """Test generating explanations"""
        entry = self.audit.log_decision(
            decision_type="moderation",
            decision="Blocked content",
            reasoning="Safety concerns detected",
            confidence=0.95,
            signals={"alignment_risk": 0.8}
        )
        
        explanation = self.audit.explain_decision(entry.audit_id)
        
        self.assertIn("human_readable", explanation)
        self.assertIn("safety", explanation["human_readable"].lower())
    
    def test_session_trail(self):
        """Test retrieving session audit trail"""
        # Log multiple decisions
        for i in range(3):
            self.audit.log_decision(
                decision_type="test",
                decision=f"Decision {i}",
                reasoning=f"Reason {i}",
                confidence=0.5 + i * 0.1,
                session_id="test_session"
            )
        
        # Get session trail
        trail = self.audit.get_session_trail("test_session")
        
        self.assertEqual(len(trail), 3)
        self.assertEqual(trail[0].decision, "Decision 0")


class TestOptimizedCache(unittest.TestCase):
    """Test the caching optimization"""
    
    @patch('openai.ChatCompletion.create')
    def test_exact_match_cache(self, mock_openai):
        """Test exact match caching"""
        from bridge.llm_wrappers.openai_optimized import OptimizedOpenAIClient
        
        # Mock OpenAI response
        mock_openai.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 100}
        }
        
        client = OptimizedOpenAIClient(
            cache_strategy="exact_match",
            cache_ttl=3600
        )
        
        # First call - should hit API
        response1 = asyncio.run(client.complete("Test prompt"))
        self.assertEqual(mock_openai.call_count, 1)
        
        # Second call - should hit cache
        response2 = asyncio.run(client.complete("Test prompt"))
        self.assertEqual(mock_openai.call_count, 1)  # No additional API call
        
        # Responses should be identical
        self.assertEqual(response1["content"], response2["content"])
        self.assertTrue(response2.get("cached", False))


class TestIntegration(unittest.TestCase):
    """Test integration of all components"""
    
    def test_full_flow(self):
        """Test complete adaptive flow"""
        from orchestration.signals.signal_bus import SignalBus
        from orchestration.signals.homeostasis_controller import HomeostasisController
        from orchestration.signals.prompt_modulator import PromptModulator
        from feedback.feedback_cards import FeedbackCardsManager
        from governance.audit_trail import AuditTrail
        
        # Initialize components
        signal_bus = SignalBus()
        homeostasis = HomeostasisController(signal_bus)
        modulator = PromptModulator()
        feedback = FeedbackCardsManager()
        audit = AuditTrail()
        
        # Simulate system under stress
        signals = homeostasis.process_event(
            event_type="resource",
            event_data={"cpu": 0.8, "memory": 0.7},
            source="system"
        )
        
        # Modulate parameters based on signals
        params = modulator.combine_signals(signals)
        
        # Log the decision
        audit_entry = audit.log_decision(
            decision_type="parameter_modulation",
            decision="Adjusted parameters for high load",
            reasoning="System stress detected",
            confidence=0.8,
            signals={s.name: s.value for s in signals}
        )
        
        # Create feedback card
        card = feedback.create_rating_card(
            user_input="Test under stress",
            ai_response="Conservative response",
            session_id="integration_test",
            system_state={"stress": 0.7}
        )
        
        # Verify integration
        self.assertIsNotNone(params)
        self.assertIsNotNone(audit_entry)
        self.assertIsNotNone(card)
        self.assertLess(params.get("temperature", 1.0), 0.6)  # Stress reduces temperature


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEndocrineSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestPromptModulation))
    suite.addTests(loader.loadTestsFromTestCase(TestFeedbackCards))
    suite.addTests(loader.loadTestsFromTestCase(TestPersonalSymbols))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditTrail))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimizedCache))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("ADAPTIVE AI FEATURES TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)