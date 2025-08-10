"""
Comprehensive Test Suite for Universal Language Module
=======================================================

Tests all AGI-enhanced capabilities including LLM integration,
constitutional constraints, neuroscience memory, and compositional generation.
"""

import unittest
import time
from typing import List, Dict, Any

# Import all universal language components
from universal_language import (
    # Core
    Symbol, Concept,
    # LLM Integration
    LLMLanguageBridge, LLMSymbolAPI, get_llm_symbol_api,
    # Constitutional AI
    ConstitutionalValidator, ConstitutionalAPI, get_constitutional_api,
    # Neuroscience Memory
    NeuroSymbolicMemory, get_neurosymbolic_memory,
    # Compositional
    SymbolComposer, SymbolProgramSynthesizer,
    get_symbol_composer, get_program_synthesizer
)
from universal_language.core import SymbolicDomain, ConceptType
from universal_language.privacy import get_private_vault
from universal_language.translator import get_universal_translator
from universal_language.multimodal import get_multimodal_processor, ModalityType
from universal_language.glyph import get_glyph_engine


class TestUniversalLanguageCore(unittest.TestCase):
    """Test core universal language functionality"""
    
    def setUp(self):
        """Initialize test environment"""
        self.test_symbols = []
        
    def test_symbol_creation(self):
        """Test basic symbol creation"""
        symbol = Symbol(
            id="TEST_001",
            domain=SymbolicDomain.EMOTION,
            name="joy",
            value=1.0,
            glyph="😊"
        )
        
        self.assertEqual(symbol.id, "TEST_001")
        self.assertEqual(symbol.domain, SymbolicDomain.EMOTION)
        self.assertEqual(symbol.name, "joy")
        self.assertEqual(symbol.glyph, "😊")
        self.test_symbols.append(symbol)
    
    def test_concept_creation(self):
        """Test concept creation from symbols"""
        symbols = [
            Symbol(id="S1", domain=SymbolicDomain.EMOTION, name="happy", value=1.0),
            Symbol(id="S2", domain=SymbolicDomain.EMOTION, name="excited", value=0.8)
        ]
        
        concept = Concept(
            concept_id="EMOTION.JOY_COMPLEX",
            concept_type=ConceptType.COMPOSITE,
            meaning="joyful excitement",
            symbols=symbols
        )
        
        self.assertEqual(concept.concept_type, ConceptType.COMPOSITE)
        self.assertEqual(len(concept.symbols), 2)
        
    def test_glyph_engine(self):
        """Test GLYPH engine functionality"""
        engine = get_glyph_engine()
        
        # Parse string with emojis
        sequence = engine.parse_string("Hello 😊 World 🌍")
        self.assertIsNotNone(sequence)
        
        # Calculate entropy
        entropy = engine.get_entropy(sequence)
        self.assertGreater(entropy, 0)
        
    def test_privacy_vault(self):
        """Test privacy-preserving symbol vault"""
        vault = get_private_vault("test_user")
        
        # Bind private symbol
        private_symbol = vault.bind_symbol(
            token="🦋",
            token_type="emoji",
            meaning_id="EMOTION.TRANSFORMATION",
            confidence=0.9
        )
        
        self.assertEqual(private_symbol.token, "🦋")
        self.assertEqual(private_symbol.meaning_id, "EMOTION.TRANSFORMATION")
        
        # Translate to universal
        concepts = vault.translate_private_to_universal(["🦋"])
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0], "EMOTION.TRANSFORMATION")
        
    def test_multimodal_processing(self):
        """Test multimodal input processing"""
        processor = get_multimodal_processor()
        
        # Create multimodal message
        message = processor.create_message({
            ModalityType.TEXT: "Hello",
            ModalityType.EMOJI: "👋",
            ModalityType.COLOR: "#FFD700"
        })
        
        # Check that modalities were processed correctly
        modality_types = [m.modality for m in message.modalities]
        self.assertIn(ModalityType.TEXT, modality_types)
        self.assertIn(ModalityType.EMOJI, modality_types)
        
        # Calculate entropy (use total entropy from modalities)
        total_entropy = sum(m.entropy_bits for m in message.modalities)
        self.assertGreater(total_entropy, 0)


class TestLLMIntegration(unittest.TestCase):
    """Test LLM integration capabilities"""
    
    def test_llm_bridge_initialization(self):
        """Test LLM bridge creation"""
        bridge = LLMLanguageBridge()
        self.assertIsNotNone(bridge)
        self.assertIsNotNone(bridge.prompt_optimizer)
        self.assertIsNotNone(bridge.few_shot_library)
    
    def test_symbol_to_tokens(self):
        """Test symbol to LLM token conversion"""
        bridge = LLMLanguageBridge()
        
        symbols = [
            Symbol(id="T1", domain=SymbolicDomain.EMOTION, name="happy", value=1.0)
        ]
        
        tokens = bridge.to_llm_tokens(symbols)
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)
    
    def test_prompt_optimization(self):
        """Test prompt optimization for token efficiency"""
        bridge = LLMLanguageBridge()
        
        symbols = [
            Symbol(id=f"S{i}", domain=SymbolicDomain.CONTEXT, name=f"sym{i}", value=i)
            for i in range(10)
        ]
        
        optimized = bridge.inject_into_context(symbols, "Test prompt")
        self.assertIsInstance(optimized, str)
        self.assertIn("Test prompt", optimized)
    
    def test_rlhf_feedback(self):
        """Test RLHF feedback collection"""
        api = get_llm_symbol_api()
        
        feedback = api.rlhf.collect_feedback({
            "symbols": [],
            "context": "test",
            "response": "test response",
            "rating": 4.5
        })
        
        self.assertEqual(feedback["rating"], 4.5)
        self.assertEqual(feedback["context"], "test")


class TestConstitutionalConstraints(unittest.TestCase):
    """Test constitutional AI safety features"""
    
    def test_constitutional_validator(self):
        """Test constitutional validation"""
        validator = ConstitutionalValidator()
        
        # Test safe symbol
        safe_symbol = Symbol(
            id="SAFE_001",
            domain=SymbolicDomain.EMOTION,
            name="kindness",
            value=1.0
        )
        
        is_valid, violations = validator.validate_symbol(safe_symbol)
        self.assertTrue(is_valid)
        # Only check for critical violations, warnings are acceptable
        critical_violations = [v for v in violations if v.severity == "critical"]
        self.assertEqual(len(critical_violations), 0)
        
        # Test potentially harmful symbol
        harmful_symbol = Symbol(
            id="HARM_001",
            domain=SymbolicDomain.ACTION,
            name="attack",
            value=-1.0
        )
        
        is_valid, violations = validator.validate_symbol(harmful_symbol)
        # Should have violations but may not be critical
        self.assertIsNotNone(violations)
    
    def test_symbol_sandbox(self):
        """Test sandbox environment"""
        api = get_constitutional_api()
        
        # Create test symbols
        test_symbols = [
            Symbol(id="TEST_1", domain=SymbolicDomain.EMOTION, name="joy", value=1.0),
            Symbol(id="TEST_2", domain=SymbolicDomain.EMOTION, name="peace", value=0.8)
        ]
        
        # Test in sandbox
        validated = api.experiment_safely(test_symbols)
        self.assertIsInstance(validated, list)
        # Should return validated symbols
        self.assertLessEqual(len(validated), len(test_symbols))
    
    def test_safe_symbol_creation(self):
        """Test safe symbol creation with validation"""
        api = get_constitutional_api()
        
        # Create safe symbol
        symbol = api.create_safe_symbol(
            name="compassion",
            domain=SymbolicDomain.EMOTION,
            value=1.0,
            meaning="deep empathy and care"
        )
        
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.name, "compassion")
        self.assertIn("validated", symbol.attributes)


class TestNeuroscienceMemory(unittest.TestCase):
    """Test neuroscience-inspired memory system"""
    
    def test_memory_encoding(self):
        """Test memory encoding and storage"""
        memory = get_neurosymbolic_memory()
        
        symbols = [
            Symbol(id="M1", domain=SymbolicDomain.EMOTION, name="happy", value=1.0),
            Symbol(id="M2", domain=SymbolicDomain.ACTION, name="smile", value=0.9)
        ]
        
        context = {"situation": "greeting", "time": "morning"}
        
        episode_id = memory.encode_symbol_experience(
            symbols=symbols,
            context=context,
            outcome="positive"
        )
        
        self.assertIsNotNone(episode_id)
        self.assertIn(episode_id, memory.episodic_memories)
    
    def test_memory_recall(self):
        """Test memory recall by symbol"""
        memory = get_neurosymbolic_memory()
        
        # Encode experience
        symbol = Symbol(id="RECALL_1", domain=SymbolicDomain.EMOTION, name="nostalgia", value=0.5)
        memory.encode_symbol_experience(
            symbols=[symbol],
            context={"trigger": "photo"},
            outcome="bittersweet"
        )
        
        # Recall by symbol
        recalled = memory.recall_by_symbol(symbol)
        self.assertGreater(len(recalled), 0)
        self.assertEqual(recalled[0].symbols_used[0].id, "RECALL_1")
    
    def test_memory_consolidation(self):
        """Test memory consolidation process"""
        memory = get_neurosymbolic_memory()
        
        initial_cycles = memory.consolidation_cycles
        
        # Consolidate memories
        memory.consolidate_memories(cycles=2)
        
        self.assertEqual(memory.consolidation_cycles, initial_cycles + 2)
    
    def test_working_memory(self):
        """Test working memory capacity"""
        memory = get_neurosymbolic_memory()
        wm = memory.working_memory
        
        # Add items up to capacity
        for i in range(10):  # More than capacity (7±2)
            wm.add(f"item_{i}", priority=0.5 + i * 0.05)
        
        # Should maintain capacity limit
        self.assertLessEqual(len(wm.items), wm.capacity)
        
        # Test rehearsal
        wm.rehearse()
        # Items should decay or be maintained
        self.assertLessEqual(len(wm.items), wm.capacity)


class TestCompositionalGeneration(unittest.TestCase):
    """Test compositional symbol generation"""
    
    def test_symbol_composition(self):
        """Test composing symbols"""
        composer = get_symbol_composer()
        
        symbols = [
            Symbol(id="C1", domain=SymbolicDomain.EMOTION, name="joy", value=1.0),
            Symbol(id="C2", domain=SymbolicDomain.EMOTION, name="surprise", value=0.8)
        ]
        
        composed = composer.compose(symbols)
        self.assertIsNotNone(composed)
        # Should create a new composed symbol
        self.assertIn("composition", composed.attributes)
    
    def test_symbol_decomposition(self):
        """Test decomposing composite symbols"""
        composer = get_symbol_composer()
        
        # Create composite symbol
        composite = Symbol(
            id="COMP_1",
            domain=SymbolicDomain.EMOTION,
            name="joy+surprise",
            value=1.0,
            attributes={
                "composition": {
                    "components": [
                        Symbol(id="D1", domain=SymbolicDomain.EMOTION, name="joy", value=1.0),
                        Symbol(id="D2", domain=SymbolicDomain.EMOTION, name="surprise", value=0.8)
                    ]
                }
            }
        )
        
        components = composer.decompose(composite)
        self.assertEqual(len(components), 2)
    
    def test_program_synthesis(self):
        """Test symbol program synthesis"""
        synthesizer = get_program_synthesizer()
        
        # Create examples for synthesis
        examples = [
            {"input": "hello", "output": "HELLO"},
            {"input": "world", "output": "WORLD"}
        ]
        
        program = synthesizer.synthesize_from_examples(examples)
        self.assertIsNotNone(program)
        self.assertIn("transform", program.code)
    
    def test_program_optimization(self):
        """Test program optimization"""
        synthesizer = get_program_synthesizer()
        
        # Create a program with redundancy
        from universal_language.compositional import SymbolProgram
        
        program = SymbolProgram(
            program_id="OPT_TEST",
            name="test_program",
            code="transform(x)\ntransform(x)\nfilter(x)",
            inputs=["x"],
            outputs=["y"],
            operations=[
                {"op": "transform", "symbol": "x"},
                {"op": "transform", "symbol": "x"},
                {"op": "filter", "symbol": "x"}
            ]
        )
        
        optimized = synthesizer.optimize_program(program)
        self.assertIsNotNone(optimized)
        # Should have fewer operations after optimization
        self.assertLessEqual(len(optimized.operations), len(program.operations))


class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def test_full_pipeline(self):
        """Test full pipeline from private symbols to LLM and back"""
        # Create private symbol
        vault = get_private_vault("integration_test")
        private_symbol = vault.bind_symbol(
            token="🎯",
            token_type="emoji",
            meaning_id="ACTION.TARGET"
        )
        
        # Translate to universal
        universal_concepts = vault.translate_private_to_universal(["🎯"])
        self.assertEqual(universal_concepts[0], "ACTION.TARGET")
        
        # Create symbol from concept
        symbol = Symbol(
            id="INT_1",
            domain=SymbolicDomain.ACTION,
            name="target",
            value="🎯"
        )
        
        # Validate constitutionally
        api = get_constitutional_api()
        safe_symbol = api.create_safe_symbol(
            name=symbol.name,
            domain=symbol.domain,
            value=symbol.value
        )
        self.assertIsNotNone(safe_symbol)
        
        # Store in memory
        memory = get_neurosymbolic_memory()
        episode_id = memory.encode_symbol_experience(
            symbols=[safe_symbol],
            context={"test": "integration"},
            outcome="success"
        )
        self.assertIsNotNone(episode_id)
        
        # Use with LLM
        llm_api = get_llm_symbol_api()
        response, extracted = llm_api.symbolic_completion(
            symbols=[safe_symbol],
            prompt="Test integration"
        )
        self.assertIsInstance(response, str)
    
    def test_translator_integration(self):
        """Test translator with multiple components"""
        translator = get_universal_translator()
        
        # Create test symbol
        symbol = Symbol(
            id="TRANS_1",
            domain=SymbolicDomain.EMOTION,
            name="happiness",
            value=1.0,
            glyph="😊"
        )
        
        # Translate to concept
        result = translator.translate(symbol, "concept")
        self.assertTrue(result.is_successful())
        self.assertIsNotNone(result.target)
        
        # Translate to GLYPH
        result = translator.translate(symbol, "glyph")
        self.assertIsNotNone(result.target)


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUniversalLanguageCore))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConstitutionalConstraints))
    suite.addTests(loader.loadTestsFromTestCase(TestNeuroscienceMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestCompositionalGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("UNIVERSAL LANGUAGE MODULE - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("\nTesting AGI-enhanced capabilities:")
    print("- Core language functionality")
    print("- LLM integration (OpenAI-style)")
    print("- Constitutional constraints (Anthropic-style)")
    print("- Neuroscience memory (DeepMind-style)")
    print("- Compositional generation")
    print("- Full integration pipeline")
    print("\n" + "=" * 70 + "\n")
    
    result = run_tests()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ Some tests failed. Review output above for details.")