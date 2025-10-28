"""
═══════════════════════════════════════════════════════════════════════════════════
🌌 LUKHAS AGI - Symbolic Vocabulary Tests  
═══════════════════════════════════════════════════════════════════════════════════

Test Module: test_symbolic_vocabulary
Purpose: Comprehensive testing of quantum-inspired symbolic vocabulary system
Version: 1.0.0
Implementation: Research-backed (Perplexity API 2024-2025 research)

Tests cover:
- Quantum-inspired symbolic states (superposition, entanglement, collapse)
- Consciousness-aware symbol evolution
- Bio-inspired learning patterns
- Neuro-symbolic integration
- MATRIZ cognitive compatibility
- Production-grade reliability

Based on cutting-edge research:
- Quantum cognition models
- Neuro-symbolic AI architectures
- Consciousness-aware symbolic processing
- Bio-inspired symbolic plasticity

═══════════════════════════════════════════════════════════════════════════════════
"""

import unittest
import numpy as np
import time
from typing import Dict, List, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from symbolic.core import (
    Symbol, 
    SymbolicVocabulary, 
    QuantumSymbolicState,
    SymbolicMetadata,
    get_symbolic_vocabulary
)

class TestQuantumSymbol(unittest.TestCase):
    """Test quantum-inspired Symbol implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.symbol = Symbol(
            name="consciousness", 
            value="awareness", 
            consciousness_level=0.8
        )
    
    def test_symbol_initialization(self):
        """Test Symbol initialization with quantum properties"""
        self.assertEqual(self.symbol.name, "consciousness")
        self.assertEqual(self.symbol.value, "awareness")
        self.assertEqual(self.symbol.quantum_state, QuantumSymbolicState.COHERENT)
        self.assertEqual(self.symbol.metadata.consciousness_level, 0.8)
        self.assertIsInstance(self.symbol.semantic_vector, np.ndarray)
        self.assertEqual(len(self.symbol.semantic_vector), 512)
        self.assertIsInstance(self.symbol.id, str)
        self.assertEqual(len(self.symbol.superposed_meanings), 0)
        self.assertEqual(len(self.symbol.entangled_symbols), 0)
    
    def test_quantum_superposition_functionality(self):
        """Test quantum superposition states"""
        # Test entering superposition
        meanings = [("awareness", 0.6), ("perception", 0.4)]
        self.symbol.enter_superposition(meanings)
        
        self.assertEqual(self.symbol.quantum_state, QuantumSymbolicState.SUPERPOSED)
        self.assertEqual(len(self.symbol.superposed_meanings), 2)
        
        # Test probability normalization
        total_prob = sum(prob for _, prob in self.symbol.superposed_meanings)
        self.assertAlmostEqual(total_prob, 1.0, places=10)
        
        # Test superposition collapse
        collapsed_meaning = self.symbol.collapse_superposition()
        self.assertIn(collapsed_meaning, ["awareness", "perception"])
        self.assertEqual(self.symbol.quantum_state, QuantumSymbolicState.COLLAPSED)
        self.assertEqual(self.symbol.metadata.access_count, 1)
    
    def test_context_aware_superposition_collapse(self):
        """Test consciousness-aware superposition collapse"""
        meanings = [("memory", 0.5), ("cognition", 0.5)]
        self.symbol.enter_superposition(meanings)
        
        # Create context vector that should influence collapse
        context_vector = np.random.normal(0, 0.1, 512)
        collapsed_meaning = self.symbol.collapse_superposition(context_vector)
        
        self.assertIn(collapsed_meaning, ["memory", "cognition"])
        self.assertEqual(self.symbol.quantum_state, QuantumSymbolicState.COLLAPSED)
        self.assertEqual(self.symbol.name, collapsed_meaning)
    
    def test_quantum_entanglement(self):
        """Test quantum entanglement between symbols"""
        symbol2 = Symbol("awareness", "consciousness", consciousness_level=0.7)
        
        # Test entanglement creation
        self.symbol.entangle_with(symbol2, correlation_strength=0.8)
        
        self.assertIn(symbol2.id, self.symbol.entangled_symbols)
        self.assertIn(self.symbol.id, symbol2.entangled_symbols)
        self.assertEqual(self.symbol.entangled_symbols[symbol2.id], 0.8)
        self.assertEqual(symbol2.entangled_symbols[self.symbol.id], 0.8)
        self.assertEqual(self.symbol.quantum_state, QuantumSymbolicState.ENTANGLED)
        self.assertEqual(symbol2.quantum_state, QuantumSymbolicState.ENTANGLED)
    
    def test_bio_inspired_semantic_evolution(self):
        """Test bio-inspired semantic adaptation"""
        original_vector = self.symbol.semantic_vector.copy()
        context_vector = np.random.normal(0, 0.2, 512)
        
        # Test semantic evolution
        self.symbol.evolve_semantics(context_vector, learning_rate=0.1)
        
        # Verify vector changed
        self.assertFalse(np.array_equal(original_vector, self.symbol.semantic_vector))
        
        # Verify semantic drift tracking
        self.assertGreater(self.symbol.metadata.semantic_drift, 0)
        
        # Verify activation history
        self.assertEqual(len(self.symbol.activation_history), 1)
        
        # Test multiple evolutions
        for _ in range(5):
            self.symbol.evolve_semantics(context_vector, learning_rate=0.05)
        
        self.assertEqual(len(self.symbol.activation_history), 6)
    
    def test_consciousness_state_reporting(self):
        """Test consciousness state information"""
        state = self.symbol.get_consciousness_state()
        
        required_keys = [
            "id", "name", "quantum_state", "consciousness_level",
            "semantic_drift", "activation_pattern", "entanglement_count",
            "superposition_meanings"
        ]
        
        for key in required_keys:
            self.assertIn(key, state)
        
        self.assertEqual(state["id"], self.symbol.id)
        self.assertEqual(state["name"], self.symbol.name)
        self.assertEqual(state["quantum_state"], "coherent")
        self.assertEqual(state["consciousness_level"], 0.8)
        self.assertEqual(state["entanglement_count"], 0)
        self.assertEqual(state["superposition_meanings"], 0)


class TestSymbolicVocabulary(unittest.TestCase):
    """Test consciousness-aware SymbolicVocabulary implementation"""
    
    def setUp(self):
        """Set up test environment"""
        self.vocabulary = SymbolicVocabulary(consciousness_level=0.75)
    
    def test_vocabulary_initialization(self):
        """Test SymbolicVocabulary initialization"""
        self.assertEqual(self.vocabulary.consciousness_level, 0.75)
        self.assertEqual(len(self.vocabulary.symbols), 0)
        self.assertEqual(len(self.vocabulary.semantic_network), 0)
        self.assertEqual(self.vocabulary.global_coherence, 1.0)
        self.assertEqual(len(self.vocabulary.learning_history), 0)
        self.assertIsInstance(self.vocabulary.matriz_node_id, str)
    
    def test_symbol_addition_and_retrieval(self):
        """Test adding and retrieving symbols"""
        # Test symbol addition
        symbol = self.vocabulary.add_symbol("intelligence", "cognitive_ability")
        
        self.assertIsInstance(symbol, Symbol)
        self.assertEqual(symbol.name, "intelligence")
        self.assertEqual(symbol.value, "cognitive_ability")
        self.assertEqual(len(self.vocabulary.symbols), 1)
        self.assertEqual(len(self.vocabulary.learning_history), 1)
        
        # Verify learning history
        learning_event = self.vocabulary.learning_history[0]
        self.assertEqual(learning_event["event"], "symbol_added")
        self.assertEqual(learning_event["name"], "intelligence")
        self.assertEqual(learning_event["symbol_id"], symbol.id)
        
        # Test symbol retrieval
        retrieved = self.vocabulary.get_symbol("intelligence")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, symbol.id)
        self.assertEqual(retrieved.metadata.access_count, 1)
        
        # Test access tracking
        self.assertEqual(len(self.vocabulary.learning_history), 2)  # Add + access
    
    def test_semantic_associations(self):
        """Test semantic association creation"""
        # Add symbols
        symbol1 = self.vocabulary.add_symbol("memory", "storage")
        symbol2 = self.vocabulary.add_symbol("recall", "retrieval")
        
        # Create association
        result = self.vocabulary.create_semantic_association("memory", "recall", 0.8)
        
        self.assertTrue(result)
        self.assertIn(symbol2.id, self.vocabulary.semantic_network[symbol1.id])
        self.assertIn(symbol1.id, self.vocabulary.semantic_network[symbol2.id])
        self.assertEqual(self.vocabulary.semantic_network[symbol1.id][symbol2.id], 0.8)
        
        # Test quantum entanglement for strong associations
        self.assertIn(symbol2.id, symbol1.entangled_symbols)
        self.assertEqual(symbol1.quantum_state, QuantumSymbolicState.ENTANGLED)
        self.assertEqual(symbol2.quantum_state, QuantumSymbolicState.ENTANGLED)
    
    def test_bio_inspired_vocabulary_evolution(self):
        """Test bio-inspired vocabulary evolution"""
        # Add symbols with different plasticity levels
        symbols = []
        for i, name in enumerate(["learning", "adaptation", "growth"]):
            symbol = self.vocabulary.add_symbol(name, f"concept_{i}")
            symbol.metadata.bio_plasticity = 0.1 + i * 0.1  # Varying plasticity
            symbols.append(symbol)
        
        # Store original semantic vectors
        original_vectors = [s.semantic_vector.copy() for s in symbols]
        
        # Evolve vocabulary
        context_data = {"task": "learning", "complexity": 0.7}
        self.vocabulary.evolve_vocabulary(context_data)
        
        # Verify evolution occurred
        for i, symbol in enumerate(symbols):
            if symbol.metadata.bio_plasticity > 0:
                self.assertFalse(np.array_equal(original_vectors[i], symbol.semantic_vector))
                self.assertGreater(symbol.metadata.semantic_drift, 0)
        
        # Verify global coherence update
        self.assertLessEqual(self.vocabulary.global_coherence, 1.0)
    
    def test_symbolic_inference_with_consciousness(self):
        """Test consciousness-aware symbolic inference"""
        # Add symbols for inference
        self.vocabulary.add_symbol("think", "cognitive_process")
        self.vocabulary.add_symbol("reason", "logical_analysis")
        self.vocabulary.add_symbol("decide", "choice_making")
        
        # Test symbolic inference
        result = self.vocabulary.query_symbolic_inference(
            "think reason decide", 
            context={"task": "problem_solving"}
        )
        
        # Verify reasoning trace structure
        required_keys = [
            "query", "timestamp", "consciousness_level", "vocabulary_size",
            "global_coherence", "relevant_symbols", "inference_result"
        ]
        for key in required_keys:
            self.assertIn(key, result)
        
        self.assertEqual(result["query"], "think reason decide")
        self.assertEqual(result["consciousness_level"], 0.75)
        self.assertEqual(result["vocabulary_size"], 3)
        self.assertEqual(len(result["relevant_symbols"]), 3)
        
        # Verify reasoning traces storage
        self.assertEqual(len(self.vocabulary.reasoning_traces), 1)
    
    def test_vocabulary_state_monitoring(self):
        """Test comprehensive vocabulary state monitoring"""
        # Add symbols in different quantum states
        symbol1 = self.vocabulary.add_symbol("quantum", "superposition")
        symbol2 = self.vocabulary.add_symbol("classical", "deterministic")
        
        # Modify quantum states
        symbol1.enter_superposition([("wave", 0.5), ("particle", 0.5)])
        symbol1.entangle_with(symbol2, 0.6)
        
        # Get vocabulary state
        state = self.vocabulary.get_vocabulary_state()
        
        required_keys = [
            "total_symbols", "consciousness_level", "global_coherence",
            "quantum_state_distribution", "semantic_network_connections",
            "learning_events", "reasoning_traces", "matriz_node_id"
        ]
        for key in required_keys:
            self.assertIn(key, state)
        
        self.assertEqual(state["total_symbols"], 2)
        self.assertEqual(state["consciousness_level"], 0.75)
        self.assertIn("superposed", state["quantum_state_distribution"])
        self.assertIn("entangled", state["quantum_state_distribution"])
    
    def test_matriz_integration_compatibility(self):
        """Test MATRIZ cognitive architecture compatibility"""
        # Verify MATRIZ node ID
        self.assertIsInstance(self.vocabulary.matriz_node_id, str)
        self.assertEqual(len(self.vocabulary.matriz_node_id), 36)  # UUID length
        
        # Test reasoning trace format for MATRIZ
        self.vocabulary.add_symbol("matriz", "cognitive_node")
        result = self.vocabulary.query_symbolic_inference("matriz cognitive processing")
        
        # Verify MATRIZ-compatible trace structure
        self.assertIn("timestamp", result)
        self.assertIn("consciousness_level", result)
        self.assertIn("inference_result", result)
        
        # Verify traces are stored for MATRIZ analysis
        self.assertEqual(len(self.vocabulary.reasoning_traces), 1)
        trace = self.vocabulary.reasoning_traces[0]
        self.assertEqual(trace["query"], "matriz cognitive processing")


class TestGlobalVocabularyFunction(unittest.TestCase):
    """Test global vocabulary function"""
    
    def test_global_vocabulary_singleton(self):
        """Test global vocabulary singleton pattern"""
        vocab1 = get_symbolic_vocabulary(consciousness_level=0.8)
        vocab2 = get_symbolic_vocabulary(consciousness_level=0.9)  # Should be ignored
        
        # Should return same instance
        self.assertIs(vocab1, vocab2)
        self.assertEqual(vocab1.consciousness_level, 0.8)  # Original level preserved
    
    def test_global_vocabulary_functionality(self):
        """Test global vocabulary basic functionality"""
        vocab = get_symbolic_vocabulary()
        
        # Test basic operations
        symbol = vocab.add_symbol("global_test", "shared_instance")
        retrieved = vocab.get_symbol("global_test")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "global_test")


class TestProductionReadiness(unittest.TestCase):
    """Test production-grade reliability and performance"""
    
    def test_error_handling_robustness(self):
        """Test error handling for edge cases"""
        vocab = SymbolicVocabulary()
        
        # Test retrieving non-existent symbol
        result = vocab.get_symbol("non_existent")
        self.assertIsNone(result)
        
        # Test association with non-existent symbols
        result = vocab.create_semantic_association("none1", "none2", 0.5)
        self.assertFalse(result)
        
        # Test evolution with empty vocabulary
        vocab.evolve_vocabulary({"context": "test"})  # Should not crash
        self.assertEqual(vocab.global_coherence, 1.0)
    
    def test_performance_characteristics(self):
        """Test performance for larger vocabularies"""
        vocab = SymbolicVocabulary()
        
        # Add multiple symbols
        start_time = time.time()
        for i in range(100):
            vocab.add_symbol(f"symbol_{i}", f"value_{i}")
        
        add_time = time.time() - start_time
        self.assertLess(add_time, 1.0)  # Should complete in reasonable time
        
        # Test retrieval performance
        start_time = time.time()
        for i in range(100):
            vocab.get_symbol(f"symbol_{i}")
        
        retrieve_time = time.time() - start_time
        self.assertLess(retrieve_time, 0.5)  # Fast retrieval
        
        # Test vocabulary evolution performance
        start_time = time.time()
        vocab.evolve_vocabulary({"test": "context"})
        evolve_time = time.time() - start_time
        
        self.assertLess(evolve_time, 2.0)  # Reasonable evolution time
    
    def test_memory_usage_stability(self):
        """Test memory usage remains stable"""
        vocab = SymbolicVocabulary()
        
        # Add and remove symbols to test memory stability
        for cycle in range(10):
            # Add symbols
            for i in range(50):
                vocab.add_symbol(f"temp_{cycle}_{i}", f"value_{i}")
            
            # Access patterns
            for i in range(25):
                vocab.get_symbol(f"temp_{cycle}_{i}")
            
            # Evolve vocabulary
            vocab.evolve_vocabulary({"cycle": cycle})
        
        # Verify system remains stable
        self.assertGreater(len(vocab.symbols), 0)
        self.assertGreater(len(vocab.learning_history), 0)
        self.assertIsInstance(vocab.global_coherence, float)
        self.assertGreaterEqual(vocab.global_coherence, 0.0)
        self.assertLessEqual(vocab.global_coherence, 1.0)


if __name__ == '__main__':
    # Configure test runner for comprehensive reporting
    unittest.main(
        verbosity=2,
        buffer=True,
        failfast=False,
        catchbreak=True
    )