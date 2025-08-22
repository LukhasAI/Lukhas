#!/usr/bin/env python3

"""
Integration Tests for LUKHAS AI Emotion Module
=============================================

Budget-optimized integration tests focusing on core functionality
and dry-run safety. Tests all key emotion functions while maintaining
minimal API usage.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from lukhas.emotion import (
    EmotionWrapper,
    get_emotion_wrapper,
    process_emotion,
    regulate_mood,
    track_valence,
    EMOTION_ACTIVE
)
from lukhas.emotion.emotion_wrapper import (
    AdvancedEmotionWrapper,
    get_advanced_emotion_wrapper
)

class TestEmotionModule:
    """Test suite for emotion module core functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        # Ensure we start in dry-run mode for safe testing
        self.original_emotion_active = os.getenv("EMOTION_ACTIVE", "false")
        os.environ["EMOTION_ACTIVE"] = "false"
    
    def teardown_method(self):
        """Cleanup after each test"""
        os.environ["EMOTION_ACTIVE"] = self.original_emotion_active
    
    def test_emotion_wrapper_initialization(self):
        """Test emotion wrapper initializes correctly"""
        wrapper = EmotionWrapper()
        assert wrapper is not None
        
        # Test initialization
        result = wrapper.initialize()
        assert result is True
        assert wrapper._initialized is True
        
        # Test feature flag status
        status = wrapper.get_feature_flag_status()
        assert status["EMOTION_ACTIVE"] is False
        assert status["dry_run_mode"] is True
        assert status["initialized"] is True
    
    def test_process_emotion_dry_run(self):
        """Test emotion processing in dry-run mode"""
        test_input = {
            "text": "I am feeling really happy today!",
            "context": {"user_id": "test_user"},
            "timestamp": "2025-08-22T00:00:00Z"
        }
        
        result = process_emotion(test_input)
        
        # Verify dry-run response
        assert result["dry_run"] is True
        assert "valence" in result
        assert "arousal" in result
        assert "dominance" in result
        assert result["emotion"] == "neutral"  # Safe default
        assert result["confidence"] == 0.5
    
    def test_regulate_mood_dry_run(self):
        """Test mood regulation in dry-run mode"""
        result = regulate_mood(
            target_state="positive",
            hormone_context={"serotonin": 0.8, "cortisol": 0.3}
        )
        
        # Verify dry-run response
        assert result["dry_run"] is True
        assert result["regulation_applied"] is False
        assert result["mood"] == "neutral"
        assert result["hormone_influence"] == "none"
        assert result["stability"] == 1.0
    
    def test_track_valence_dry_run(self):
        """Test valence tracking in dry-run mode"""
        result = track_valence(window_size=5)
        
        # Verify dry-run response
        assert result["dry_run"] is True
        assert result["current_valence"] == 0.0
        assert result["trend"] == "stable"
        assert result["variance"] == 0.0
        assert result["window_size"] == 5
    
    @patch.dict(os.environ, {"EMOTION_ACTIVE": "true"})
    def test_emotion_processing_active_mode(self):
        """Test emotion processing in active mode (mocked for budget)"""
        # Create new wrapper with active mode
        wrapper = EmotionWrapper()
        wrapper.initialize()
        
        test_input = {
            "text": "I love this amazing day!",
            "context": {"mood": "positive"}
        }
        
        result = wrapper.process_emotion(test_input)
        
        # Verify active mode response
        assert "dry_run" not in result or result["dry_run"] is False
        assert isinstance(result["valence"], (int, float))
        assert isinstance(result["arousal"], (int, float))
        assert isinstance(result["dominance"], (int, float))
        assert "emotion" in result
        assert "confidence" in result
    
    def test_vad_calculation_accuracy(self):
        """Test VAD calculation accuracy with known inputs"""
        # Use active mode for real calculations
        with patch.dict(os.environ, {"EMOTION_ACTIVE": "true"}):
            wrapper = EmotionWrapper()
            wrapper.initialize()
            
            # Test positive emotion
            positive_input = {"text": "wonderful excellent great happy joy"}
            result = wrapper.process_emotion(positive_input)
            assert result["valence"] > 0.0, "Should detect positive valence"
            
            # Test negative emotion  
            negative_input = {"text": "terrible awful bad sad angry hate"}
            result = wrapper.process_emotion(negative_input)
            assert result["valence"] < 0.0, "Should detect negative valence"
            
            # Test high arousal
            arousal_input = {"text": "excited thrilled intense passionate urgent"}
            result = wrapper.process_emotion(arousal_input)
            assert result["arousal"] > 0.5, "Should detect high arousal"
    
    def test_singleton_pattern(self):
        """Test that wrapper uses singleton pattern correctly"""
        wrapper1 = get_emotion_wrapper()
        wrapper2 = get_emotion_wrapper()
        
        assert wrapper1 is wrapper2, "Should return same instance"
        assert id(wrapper1) == id(wrapper2), "Should be identical objects"
    
    def test_emotional_state_management(self):
        """Test emotional state tracking and updates"""
        wrapper = EmotionWrapper()
        wrapper.initialize()
        
        # Get initial state
        initial_state = wrapper.get_emotional_state()
        assert "valence" in initial_state
        assert "arousal" in initial_state
        assert "dominance" in initial_state
        assert "mood" in initial_state
        
        # Process emotion to update state (in active mode)
        with patch.dict(os.environ, {"EMOTION_ACTIVE": "true"}):
            test_input = {"text": "happy content wonderful"}
            wrapper.process_emotion(test_input)
            
            updated_state = wrapper.get_emotional_state()
            # State should potentially change (depending on implementation)
            assert isinstance(updated_state["valence"], (int, float))

class TestAdvancedEmotionWrapper:
    """Test suite for advanced emotion wrapper with integrations"""
    
    def setup_method(self):
        """Setup for each test"""
        os.environ["EMOTION_ACTIVE"] = "false"  # Safe testing
    
    @patch('lukhas.emotion.emotion_wrapper.EmotionMemoryIntegration')
    def test_advanced_wrapper_initialization(self, mock_integration):
        """Test advanced wrapper initialization"""
        wrapper = AdvancedEmotionWrapper()
        assert wrapper is not None
        
        result = wrapper.initialize()
        assert result is True
    
    @patch('lukhas.emotion.emotion_wrapper.EmotionMemoryIntegration')
    def test_advanced_emotion_processing(self, mock_integration):
        """Test advanced emotion processing with mocked integrations"""
        # Mock integration methods
        mock_integration.return_value.recall_emotional_patterns.return_value = [
            {"emotion": "happy", "valence": 0.8}
        ]
        mock_integration.return_value.store_emotional_memory.return_value = True
        mock_integration.return_value.sync_with_consciousness.return_value = {
            "synced": True, "status": "success"
        }
        
        wrapper = AdvancedEmotionWrapper()
        wrapper.initialize()
        
        test_input = {"text": "feeling great today", "context": {}}
        result = wrapper.process_emotion_with_memory(test_input)
        
        # Should include pattern and memory information
        assert "pattern_match" in result
        assert "memory_stored" in result
        assert "consciousness_sync" in result
    
    def test_singleton_advanced_wrapper(self):
        """Test advanced wrapper singleton pattern"""
        wrapper1 = get_advanced_emotion_wrapper()
        wrapper2 = get_advanced_emotion_wrapper()
        
        assert wrapper1 is wrapper2, "Should return same instance"

class TestEmotionIntegration:
    """Test emotion module integration with other systems"""
    
    def setup_method(self):
        """Setup for integration tests"""
        os.environ["EMOTION_ACTIVE"] = "false"
    
    @patch('lukhas.memory.get_memory_wrapper')
    def test_memory_integration_mock(self, mock_memory):
        """Test emotion-memory integration with mocked memory system"""
        # Mock memory wrapper
        mock_memory_wrapper = MagicMock()
        mock_memory_wrapper.store_memory.return_value = {"success": True}
        mock_memory_wrapper.query_memories.return_value = {"memories": []}
        mock_memory.return_value = mock_memory_wrapper
        
        from lukhas.emotion.emotion_wrapper import EmotionMemoryIntegration
        integration = EmotionMemoryIntegration()
        integration.initialize_integrations()
        
        # Test memory storage
        emotion_data = {
            "emotion": "happy",
            "valence": 0.7,
            "arousal": 0.6,
            "dominance": 0.5
        }
        
        result = integration.store_emotional_memory(emotion_data)
        assert result is True
        mock_memory_wrapper.store_memory.assert_called_once()
    
    @patch('lukhas.consciousness.get_consciousness_wrapper')  
    def test_consciousness_integration_mock(self, mock_consciousness):
        """Test emotion-consciousness integration with mocked consciousness system"""
        # Mock consciousness wrapper
        mock_consciousness_wrapper = MagicMock()
        mock_consciousness_wrapper.process_awareness.return_value = {"status": "processed"}
        mock_consciousness.return_value = mock_consciousness_wrapper
        
        from lukhas.emotion.emotion_wrapper import EmotionMemoryIntegration
        integration = EmotionMemoryIntegration()
        integration.initialize_integrations()
        
        # Test consciousness sync
        emotion_data = {"emotion": "excited", "valence": 0.8}
        result = integration.sync_with_consciousness(emotion_data)
        
        assert result["synced"] is True
        assert "consciousness_response" in result
        mock_consciousness_wrapper.process_awareness.assert_called_once()

class TestBudgetOptimization:
    """Test budget optimization features"""
    
    def test_dry_run_safety(self):
        """Test that dry-run mode prevents expensive operations"""
        # Ensure dry-run mode
        os.environ["EMOTION_ACTIVE"] = "false"
        
        wrapper = EmotionWrapper()
        wrapper.initialize()
        
        # All operations should be safe and fast
        test_cases = [
            {"text": "happy"},
            {"text": "sad"},
            {"text": "angry"},
            {"text": "excited"},
            {"text": ""},  # Edge case
        ]
        
        for test_input in test_cases:
            result = process_emotion(test_input)
            assert result["dry_run"] is True
            assert result["emotion"] == "neutral"  # Safe default
            assert isinstance(result["valence"], (int, float))
    
    def test_feature_flag_behavior(self):
        """Test feature flag controls behavior correctly"""
        # Test with flag disabled
        os.environ["EMOTION_ACTIVE"] = "false"
        wrapper = EmotionWrapper()
        wrapper.initialize()
        
        result = wrapper.process_emotion({"text": "test"})
        assert result["dry_run"] is True
        
        # Test with flag enabled
        os.environ["EMOTION_ACTIVE"] = "true"
        wrapper2 = EmotionWrapper()
        wrapper2.initialize()
        
        result2 = wrapper2.process_emotion({"text": "test"})
        assert "dry_run" not in result2 or result2["dry_run"] is False

# Test execution efficiency
def test_execution_time():
    """Test that operations complete quickly for budget optimization"""
    import time
    
    wrapper = EmotionWrapper()
    wrapper.initialize()
    
    start_time = time.time()
    
    # Run multiple operations
    for i in range(10):
        process_emotion({"text": f"test message {i}"})
        regulate_mood("positive")
        track_valence(5)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Should complete quickly in dry-run mode
    assert execution_time < 1.0, f"Operations took {execution_time}s, should be under 1s"

if __name__ == "__main__":
    # Run basic tests for verification
    test_suite = TestEmotionModule()
    test_suite.setup_method()
    
    try:
        test_suite.test_emotion_wrapper_initialization()
        test_suite.test_process_emotion_dry_run()
        test_suite.test_regulate_mood_dry_run()
        test_suite.test_track_valence_dry_run()
        print("✅ All basic emotion tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        test_suite.teardown_method()