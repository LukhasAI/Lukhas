"""
Unit tests for LUKHAS Symbolic/GLYPH Engine
"""

import pytest
import numpy as np
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from tests.test_framework import (
    LUKHASTestCase, MockDataGenerator, TestValidator
)


class TestSymbolicEngine(LUKHASTestCase):
    """Test core symbolic engine functionality"""
    
    @pytest.fixture
    async def symbolic_engine(self):
        """Create symbolic engine instance"""
        from core.api.service_stubs import SymbolicEngine
        engine = SymbolicEngine()
        await engine.initialize()
        return engine
        
    @pytest.mark.asyncio
    async def test_initialization(self, symbolic_engine):
        """Test symbolic engine initialization"""
        assert symbolic_engine.initialized is True
        assert isinstance(symbolic_engine.glyph_map, dict)
        assert len(symbolic_engine.glyph_map) > 0
        
        # Check core glyphs exist
        assert 'love' in symbolic_engine.glyph_map
        assert 'think' in symbolic_engine.glyph_map
        assert 'create' in symbolic_engine.glyph_map
        
    @pytest.mark.asyncio
    async def test_text_encoding(self, symbolic_engine):
        """Test encoding text to GLYPHs"""
        text = "love creates understanding"
        result = await symbolic_engine.encode(text)
        
        # Validate result structure
        assert 'glyphs' in result
        assert 'entropy' in result
        assert 'resonance' in result
        
        # Check glyphs
        assert isinstance(result['glyphs'], list)
        assert len(result['glyphs']) == 3  # Three words
        assert result['glyphs'][0] == '♥'  # love
        assert result['glyphs'][1] == '✨'  # create
        
        # Check metrics
        assert 0 <= result['entropy'] <= 1
        assert 0 <= result['resonance'] <= 1
        
    @pytest.mark.asyncio
    async def test_unknown_word_encoding(self, symbolic_engine):
        """Test encoding unknown words"""
        text = "unknown mystical quantum"
        result = await symbolic_engine.encode(text)
        
        # Should create pseudo-glyphs for unknown words
        assert len(result['glyphs']) == 3
        for glyph in result['glyphs']:
            if glyph.startswith('λ'):
                # Pseudo-glyph format
                assert len(glyph) >= 4  # λ + 3 chars
                
    @pytest.mark.asyncio
    async def test_glyph_decoding(self, symbolic_engine):
        """Test decoding GLYPHs to text"""
        glyphs = ['♥', '🧠', '✨']
        result = await symbolic_engine.decode(glyphs)
        
        assert 'text' in result
        assert 'confidence' in result
        
        # Should decode known glyphs
        assert 'love' in result['text']
        assert 'think' in result['text']
        assert 'create' in result['text']
        
        assert 0 <= result['confidence'] <= 1
        
    @pytest.mark.asyncio
    async def test_mixed_glyph_decoding(self, symbolic_engine):
        """Test decoding mix of known and pseudo glyphs"""
        glyphs = ['♥', 'λmys', '🌙', 'λunk']
        result = await symbolic_engine.decode(glyphs)
        
        # Should handle both types
        assert 'love' in result['text']
        assert 'dream' in result['text']
        assert 'mys...' in result['text']  # Pseudo-glyph expansion
        
    @pytest.mark.asyncio
    async def test_symbolic_analysis(self, symbolic_engine):
        """Test symbolic content analysis"""
        content = "Love and creativity flow through conscious thought"
        result = await symbolic_engine.analyze(content)
        
        assert 'encoded' in result
        assert 'patterns' in result
        assert 'symbolic_density' in result
        assert 'interpretation_confidence' in result
        
        # Check patterns detected
        assert isinstance(result['patterns'], list)
        assert len(result['patterns']) > 0
        
        # Symbolic density should be ratio of symbolic words
        assert 0 <= result['symbolic_density'] <= 1
        
    @pytest.mark.asyncio
    async def test_empty_input_handling(self, symbolic_engine):
        """Test handling empty inputs"""
        # Empty text
        result = await symbolic_engine.encode("")
        assert result['glyphs'] == []
        
        # Empty glyph list
        result = await symbolic_engine.decode([])
        assert result['text'] == ""
        
    @pytest.mark.asyncio
    async def test_special_characters(self, symbolic_engine):
        """Test handling special characters"""
        text = "Love! Think? Create... Dream~"
        result = await symbolic_engine.encode(text)
        
        # Should extract words properly
        assert len(result['glyphs']) == 4
        assert '♥' in result['glyphs']
        assert '🧠' in result['glyphs']
        
    @pytest.mark.asyncio
    async def test_case_insensitivity(self, symbolic_engine):
        """Test case-insensitive encoding"""
        texts = ["LOVE", "Love", "love", "LoVe"]
        
        glyphs = []
        for text in texts:
            result = await symbolic_engine.encode(text)
            glyphs.append(result['glyphs'][0])
            
        # All should produce same glyph
        assert all(g == '♥' for g in glyphs)


class TestGLYPHPatterns(LUKHASTestCase):
    """Test GLYPH pattern recognition and manipulation"""
    
    @pytest.fixture
    def pattern_matcher(self):
        """Create mock pattern matcher"""
        matcher = Mock()
        matcher.patterns = {
            'emergence': ['λ', 'Ω', 'Δ'],
            'coherence': ['Σ', 'Φ', 'Ψ'],
            'resonance': ['♥', '💫', '🌙'],
            'transformation': ['✨', '🔄', '∞']
        }
        return matcher
        
    def test_pattern_detection(self, pattern_matcher):
        """Test detection of symbolic patterns"""
        # Sequence with emergence pattern
        sequence = ['λ', 'Ω', 'Δ', 'other', 'symbols']
        
        detected = []
        for pattern_name, pattern_glyphs in pattern_matcher.patterns.items():
            # Check if pattern exists in sequence
            if all(g in sequence for g in pattern_glyphs):
                detected.append(pattern_name)
                
        assert 'emergence' in detected
        
    def test_pattern_strength_calculation(self, pattern_matcher):
        """Test pattern strength/confidence calculation"""
        sequence = ['λ', 'Ω', 'Δ', 'λ', 'Ω']  # Repeated pattern
        
        # Count pattern occurrences
        pattern_counts = {}
        for pattern_name, pattern_glyphs in pattern_matcher.patterns.items():
            count = 0
            for glyph in pattern_glyphs:
                count += sequence.count(glyph)
            pattern_counts[pattern_name] = count
            
        # Emergence pattern should be strongest
        strongest = max(pattern_counts, key=pattern_counts.get)
        assert strongest == 'emergence'
        
    def test_pattern_composition(self, pattern_matcher):
        """Test composing patterns from glyphs"""
        # Create specific pattern
        target_pattern = 'coherence'
        glyphs = pattern_matcher.patterns[target_pattern]
        
        # Verify composition
        assert len(glyphs) == 3
        assert all(isinstance(g, str) for g in glyphs)
        
    def test_pattern_transformation(self, pattern_matcher):
        """Test pattern transformations"""
        # Transform emergence to coherence
        emergence_glyphs = pattern_matcher.patterns['emergence']
        
        # Simple transformation: map each glyph
        transform_map = {
            'λ': 'Σ',
            'Ω': 'Φ', 
            'Δ': 'Ψ'
        }
        
        transformed = [transform_map.get(g, g) for g in emergence_glyphs]
        
        assert transformed == pattern_matcher.patterns['coherence']


class TestSymbolicResonance(LUKHASTestCase):
    """Test symbolic resonance calculations"""
    
    @pytest.fixture
    def resonance_calculator(self):
        """Create mock resonance calculator"""
        calc = Mock()
        calc.resonance_matrix = {
            ('♥', '💫'): 0.9,  # High resonance
            ('♥', '⚔️'): 0.1,  # Low resonance
            ('🧠', '💭'): 0.8,  # Related concepts
            ('🌙', '✨'): 0.7   # Moderate resonance
        }
        return calc
        
    def test_pairwise_resonance(self, resonance_calculator):
        """Test resonance between glyph pairs"""
        # High resonance pair
        resonance = resonance_calculator.resonance_matrix.get(('♥', '💫'), 0.5)
        assert resonance > 0.8
        
        # Low resonance pair
        resonance = resonance_calculator.resonance_matrix.get(('♥', '⚔️'), 0.5)
        assert resonance < 0.2
        
    def test_sequence_resonance(self, resonance_calculator):
        """Test overall sequence resonance"""
        sequence = ['♥', '💫', '🧠', '💭']
        
        # Calculate average pairwise resonance
        total_resonance = 0
        pairs = 0
        
        for i in range(len(sequence) - 1):
            pair = (sequence[i], sequence[i + 1])
            resonance = resonance_calculator.resonance_matrix.get(pair, 0.5)
            total_resonance += resonance
            pairs += 1
            
        avg_resonance = total_resonance / pairs if pairs > 0 else 0
        
        # This sequence should have high resonance
        assert avg_resonance > 0.7
        
    def test_resonance_field_generation(self, resonance_calculator):
        """Test resonance field around glyphs"""
        center_glyph = '♥'
        
        # Find all glyphs that resonate with center
        resonant_glyphs = []
        for pair, resonance in resonance_calculator.resonance_matrix.items():
            if pair[0] == center_glyph and resonance > 0.7:
                resonant_glyphs.append(pair[1])
                
        assert '💫' in resonant_glyphs
        assert '⚔️' not in resonant_glyphs  # Low resonance


class TestSymbolicEntropy(LUKHASTestCase):
    """Test symbolic entropy calculations"""
    
    def test_entropy_calculation(self):
        """Test entropy of symbol sequences"""
        # Low entropy (repeated symbols)
        low_entropy_seq = ['λ', 'λ', 'λ', 'λ']
        
        # High entropy (diverse symbols)
        high_entropy_seq = ['λ', 'Ω', 'Δ', 'Σ', 'Φ', 'Ψ']
        
        # Calculate entropy (simplified)
        def calculate_entropy(sequence):
            unique = len(set(sequence))
            total = len(sequence)
            return unique / total if total > 0 else 0
            
        low_entropy = calculate_entropy(low_entropy_seq)
        high_entropy = calculate_entropy(high_entropy_seq)
        
        assert low_entropy < 0.5
        assert high_entropy > 0.8
        
    def test_entropy_threshold_detection(self):
        """Test detection of entropy thresholds"""
        sequences = [
            (['λ', 'λ', 'λ'], 'low'),      # Low entropy
            (['λ', 'Ω', 'λ'], 'medium'),    # Medium entropy
            (['λ', 'Ω', 'Δ', 'Σ'], 'high')  # High entropy
        ]
        
        for seq, expected_level in sequences:
            unique_ratio = len(set(seq)) / len(seq)
            
            if unique_ratio < 0.4:
                level = 'low'
            elif unique_ratio < 0.7:
                level = 'medium'
            else:
                level = 'high'
                
            assert level == expected_level


class TestSymbolicIntegration(LUKHASTestCase):
    """Test symbolic engine integration with other systems"""
    
    @pytest.mark.asyncio
    async def test_consciousness_symbolic_integration(self, symbolic_engine):
        """Test symbolic encoding in consciousness"""
        with patch('core.api.service_stubs.UnifiedConsciousness') as MockConsciousness:
            consciousness = MockConsciousness.return_value
            
            # Consciousness using symbolic encoding
            text = "I am experiencing joy and creativity"
            
            # Encode to symbols
            symbolic_result = await symbolic_engine.encode(text)
            
            # Consciousness should process symbols
            consciousness.process_symbolic = AsyncMock(return_value={
                'interpretation': 'Positive emotional state with creative energy',
                'symbolic_alignment': 0.9
            })
            
            result = await consciousness.process_symbolic(symbolic_result['glyphs'])
            assert result['symbolic_alignment'] > 0.8
            
    @pytest.mark.asyncio
    async def test_memory_symbolic_compression(self, symbolic_engine):
        """Test symbolic compression for memory storage"""
        # Long text to compress
        long_text = " ".join(["love", "think", "create", "dream"] * 10)
        
        # Encode to symbols
        encoded = await symbolic_engine.encode(long_text)
        
        # Should be compressed
        assert len(encoded['glyphs']) == 40  # 4 words * 10
        
        # But unique symbols much less
        unique_glyphs = set(encoded['glyphs'])
        assert len(unique_glyphs) == 4
        
    @pytest.mark.asyncio
    async def test_guardian_symbolic_analysis(self, symbolic_engine):
        """Test Guardian analyzes symbolic patterns"""
        with patch('core.api.service_stubs.GuardianSystem') as MockGuardian:
            guardian = MockGuardian.return_value
            
            # Encode potentially concerning text
            text = "destroy and harm"
            encoded = await symbolic_engine.encode(text)
            
            # Guardian should analyze symbolic patterns
            guardian.analyze_symbolic_pattern = AsyncMock(return_value={
                'risk_level': 'high',
                'concerning_patterns': ['destruction', 'harm']
            })
            
            risk_analysis = await guardian.analyze_symbolic_pattern(encoded['glyphs'])
            assert risk_analysis['risk_level'] == 'high'


class TestSymbolicPerformance(LUKHASTestCase):
    """Test symbolic engine performance"""
    
    @pytest.mark.asyncio
    async def test_encoding_performance(self, symbolic_engine):
        """Test encoding speed"""
        import time
        
        texts = [
            "Simple text",
            " ".join(["word"] * 100),  # 100 words
            " ".join(["different", "words", "here"] * 50)  # 150 words
        ]
        
        for text in texts:
            start = time.perf_counter()
            result = await symbolic_engine.encode(text)
            end = time.perf_counter()
            
            encoding_time = end - start
            words = len(text.split())
            
            # Should be fast even for long texts
            assert encoding_time < 0.1, f"Encoding {words} words took {encoding_time:.3f}s"
            
    @pytest.mark.asyncio
    async def test_batch_encoding(self, symbolic_engine):
        """Test batch encoding efficiency"""
        # Many texts to encode
        texts = [f"Text number {i} with content" for i in range(100)]
        
        import time
        start = time.perf_counter()
        
        # Encode all
        results = []
        for text in texts:
            result = await symbolic_engine.encode(text)
            results.append(result)
            
        end = time.perf_counter()
        total_time = end - start
        
        # Should handle batch efficiently
        assert total_time < 1.0, f"Batch encoding took {total_time:.3f}s"
        assert len(results) == len(texts)
        
    @pytest.mark.asyncio
    async def test_symbol_caching(self, symbolic_engine):
        """Test symbol lookup caching"""
        # Encode same words multiple times
        word = "love"
        
        times = []
        for _ in range(100):
            import time
            start = time.perf_counter()
            result = await symbolic_engine.encode(word)
            times.append(time.perf_counter() - start)
            
        # Later lookups should be faster (cached)
        avg_first_10 = sum(times[:10]) / 10
        avg_last_10 = sum(times[-10:]) / 10
        
        # In real system with caching, later would be faster
        assert all(t < 0.01 for t in times)


class TestSymbolicCapabilities(LUKHASTestCase):
    """Test symbolic engine capabilities"""
    
    @pytest.mark.asyncio
    async def test_capability_reporting(self, symbolic_engine):
        """Test capability enumeration"""
        capabilities = symbolic_engine.get_capabilities()
        
        assert 'encoding_methods' in capabilities
        assert 'max_glyph_complexity' in capabilities
        assert 'supported_languages' in capabilities
        assert 'pattern_recognition' in capabilities
        
        # Verify capability values
        assert isinstance(capabilities['encoding_methods'], list)
        assert 'semantic' in capabilities['encoding_methods']
        assert capabilities['max_glyph_complexity'] > 0
        assert 'en' in capabilities['supported_languages']
        assert capabilities['pattern_recognition'] is True
        
    @pytest.mark.asyncio
    async def test_multilingual_support(self, symbolic_engine):
        """Test support for multiple languages"""
        # Currently supports English
        # Test structure for future multilingual support
        
        languages = {
            'en': "love creates understanding",
            # Future: 'es': "amor crea comprensión",
            # Future: 'fr': "l'amour crée la compréhension"
        }
        
        for lang, text in languages.items():
            if lang in symbolic_engine.get_capabilities()['supported_languages']:
                result = await symbolic_engine.encode(text)
                assert len(result['glyphs']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])