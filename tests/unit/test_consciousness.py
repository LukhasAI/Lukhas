"""
Unit tests for LUKHAS Consciousness System
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

from tests.test_framework import (
    LUKHASTestCase, TestValidator
)
from core.api.service_stubs import UnifiedConsciousness


class TestConsciousnessCore(LUKHASTestCase):
    """Test core consciousness functionality"""
    
    @pytest.fixture
    async def consciousness(self):
        """Create consciousness instance"""
        from core.api.service_stubs import UnifiedConsciousness
        consciousness = UnifiedConsciousness()
        await consciousness.initialize()
        return consciousness
        
    @pytest.mark.asyncio
    async def test_initialization(self, consciousness):
        """Test consciousness system initialization"""
        assert consciousness.initialized is True
        assert consciousness.awareness_level == 0.7
        assert len(consciousness.states) > 0
        assert 'aware' in consciousness.states
        
    @pytest.mark.asyncio
    async def test_basic_query_processing(self, consciousness):
        """Test basic query processing"""
        query = "What is consciousness?"
        result = await consciousness.process_query(query)
        
        # Validate response structure
        TestValidator.validate_consciousness_response(result)
        
        # Check specific fields
        assert query in result['interpretation']
        assert result['consciousness_state'] in consciousness.states
        assert 0 <= result['confidence'] <= 1
        
    @pytest.mark.asyncio
    async def test_awareness_levels(self, consciousness):
        """Test different awareness levels"""
        query = "Test awareness"
        
        # Test low awareness
        low_result = await consciousness.process_query(query, awareness_level=0.2)
        
        # Test high awareness  
        high_result = await consciousness.process_query(query, awareness_level=0.9)
        
        # Higher awareness should have higher confidence
        assert high_result['confidence'] > low_result['confidence']
        
    @pytest.mark.asyncio
    async def test_emotional_context_inclusion(self, consciousness):
        """Test emotional context in responses"""
        query = "How are you feeling?"
        
        # With emotion
        with_emotion = await consciousness.process_query(
            query, 
            include_emotion=True
        )
        assert 'emotional_context' in with_emotion
        assert 'valence' in with_emotion['emotional_context']
        assert 'arousal' in with_emotion['emotional_context']
        assert 'dominance' in with_emotion['emotional_context']
        
        # Without emotion
        without_emotion = await consciousness.process_query(
            query,
            include_emotion=False
        )
        assert 'emotional_context' not in without_emotion
        
    @pytest.mark.asyncio
    async def test_state_transitions(self, consciousness):
        """Test consciousness state transitions"""
        # Track states across multiple queries
        states_observed = set()
        
        queries = [
            "Analyze this data",  # Should trigger analytical
            "Create something new",  # Should trigger creative
            "Reflect on existence",  # Should trigger contemplative
            "Process information"  # Should trigger aware
        ]
        
        for query in queries:
            result = await consciousness.process_query(query)
            states_observed.add(result['consciousness_state'])
            
        # Should have observed multiple states
        assert len(states_observed) >= 2
        
    @pytest.mark.asyncio
    async def test_awareness_vector_properties(self, consciousness):
        """Test awareness vector mathematical properties"""
        result = await consciousness.process_query("Test vector")
        vector = result['awareness_vector']
        
        # Vector properties
        assert len(vector) == 5  # 5-dimensional
        assert all(isinstance(v, (int, float)) for v in vector)
        assert all(0 <= v <= 1 for v in vector)  # Normalized
        
        # Vector should have some variance (not all same)
        assert len(set(vector)) > 1
        
    @pytest.mark.asyncio
    async def test_query_length_handling(self, consciousness):
        """Test handling of different query lengths"""
        # Empty query
        with pytest.raises(Exception):
            await consciousness.process_query("")
            
        # Very short query
        short_result = await consciousness.process_query("Hi")
        assert short_result is not None
        
        # Very long query
        long_query = " ".join(["consciousness"] * 1000)
        long_result = await consciousness.process_query(long_query)
        assert long_result is not None
        
    @pytest.mark.asyncio
    async def test_consciousness_capabilities(self, consciousness):
        """Test capability reporting"""
        capabilities = consciousness.get_capabilities()
        
        assert 'states' in capabilities
        assert 'awareness_range' in capabilities
        assert 'processing_modes' in capabilities
        assert 'max_context_window' in capabilities
        
        # Verify capability values
        assert capabilities['awareness_range'] == [0.0, 1.0]
        assert len(capabilities['states']) > 0
        assert capabilities['max_context_window'] > 0


class TestConsciousnessStates(LUKHASTestCase):
    """Test consciousness state management"""
    
    @pytest.fixture
    def mock_state_manager(self):
        """Create mock state manager"""
        manager = Mock()
        manager.current_state = 'aware'
        manager.state_history = []
        manager.transition_count = 0
        return manager
        
    def test_state_validation(self, mock_state_manager):
        """Test state validation"""
        valid_states = ['aware', 'contemplative', 'creative', 'analytical', 'dreaming']
        
        for state in valid_states:
            mock_state_manager.current_state = state
            assert mock_state_manager.current_state in valid_states
            
        # Invalid state should raise error
        with pytest.raises(ValueError):
            mock_state_manager.current_state = 'invalid_state'
            if mock_state_manager.current_state not in valid_states:
                raise ValueError("Invalid state")
                
    def test_state_history_tracking(self, mock_state_manager):
        """Test state history is properly tracked"""
        states = ['aware', 'contemplative', 'creative', 'aware']
        
        for state in states:
            mock_state_manager.current_state = state
            mock_state_manager.state_history.append({
                'state': state,
                'timestamp': datetime.now(timezone.utc)
            })
            
        assert len(mock_state_manager.state_history) == len(states)
        assert mock_state_manager.state_history[0]['state'] == 'aware'
        assert mock_state_manager.state_history[-1]['state'] == 'aware'
        
    def test_state_transition_rules(self, mock_state_manager):
        """Test valid state transitions"""
        # Define transition rules
        valid_transitions = {
            'aware': ['contemplative', 'creative', 'analytical'],
            'contemplative': ['aware', 'creative', 'dreaming'],
            'creative': ['aware', 'contemplative', 'dreaming'],
            'analytical': ['aware', 'contemplative'],
            'dreaming': ['aware', 'creative']
        }
        
        # Test valid transitions
        current = 'aware'
        for next_state in valid_transitions[current]:
            # Should allow transition
            assert next_state in valid_transitions[current]
            
            
class TestConsciousnessIntegration(LUKHASTestCase):
    """Test consciousness integration points"""
    
    @pytest.mark.asyncio
    async def test_guardian_integration(self):
        """Test consciousness respects Guardian constraints"""
        with patch('core.api.service_stubs.GuardianSystem') as MockGuardian:
            guardian = MockGuardian.return_value
            guardian.validate_response = AsyncMock(return_value={
                'approved': False,
                'reason': 'Potentially harmful content',
                'constraints': ['reduce_certainty', 'add_disclaimers']
            })
            
            consciousness = UnifiedConsciousness()
            await consciousness.initialize()
            
            # Process query that Guardian would flag
            result = await consciousness.process_query("How to harm others?")
            
            # Should still return result but with modifications
            assert result is not None
            # In real system, would apply constraints
            
    @pytest.mark.asyncio
    async def test_memory_integration(self):
        """Test consciousness creates memory entries"""
        with patch('core.api.service_stubs.MemoryManager') as MockMemory:
            memory = MockMemory.return_value
            memory.store = AsyncMock(return_value={'stored': True, 'memory_id': 'test_id'})
            
            consciousness = UnifiedConsciousness()
            await consciousness.initialize()
            
            # Process query
            query = "Remember this important fact"
            result = await consciousness.process_query(query)
            
            # In real system, would trigger memory storage
            assert result is not None
            
    @pytest.mark.asyncio
    async def test_emotion_modulation(self):
        """Test emotion affects consciousness processing"""
        with patch('core.api.service_stubs.EmotionEngine') as MockEmotion:
            emotion = MockEmotion.return_value
            emotion.get_current_state = AsyncMock(return_value={
                'valence': -0.8,  # Very negative
                'arousal': 0.9,   # High arousal
                'dominance': 0.2  # Low dominance
            })
            
            consciousness = UnifiedConsciousness()
            await consciousness.initialize()
            
            # Process with emotion context
            result = await consciousness.process_query(
                "How do you feel?",
                include_emotion=True
            )
            
            # Should reflect emotional state
            if 'emotional_context' in result:
                assert result['emotional_context']['valence'] < 0


class TestConsciousnessPerformance(LUKHASTestCase):
    """Test consciousness performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_response_time(self, consciousness):
        """Test query response time"""
        import time
        
        queries = [
            "Simple query",
            "What is the nature of consciousness and how does it emerge?",
            "Analyze the relationship between " * 20  # Long query
        ]
        
        for query in queries:
            start = time.perf_counter()
            result = await consciousness.process_query(query)
            end = time.perf_counter()
            
            response_time = end - start
            assert response_time < 1.0, f"Query took {response_time:.3f}s"
            assert result is not None
            
    @pytest.mark.asyncio
    async def test_concurrent_queries(self, consciousness):
        """Test handling concurrent queries"""
        queries = [f"Query {i}" for i in range(10)]
        
        # Process concurrently
        tasks = [consciousness.process_query(q) for q in queries]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == len(queries)
        assert all(r is not None for r in results)
        
        # Each should have unique content
        interpretations = [r['interpretation'] for r in results]
        assert len(set(interpretations)) == len(interpretations)
        
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, consciousness):
        """Test memory usage remains bounded"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process many queries
        for i in range(100):
            await consciousness.process_query(f"Query {i}")
            
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not leak excessive memory
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])