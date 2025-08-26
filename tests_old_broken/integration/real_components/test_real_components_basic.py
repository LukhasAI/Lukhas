#!/usr/bin/env python3
"""
Basic Real Components Integration Tests
Simple tests to verify actual LUKHAS components can be imported and used
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestRealComponentsBasic:
    """Basic tests for real LUKHAS components"""
    
    def test_import_symbolic_kernel_bus(self):
        """Test that we can import and use the real symbolic kernel bus"""
        try:
            from candidate.orchestration.symbolic_kernel_bus import SymbolicKernelBus, SymbolicEvent, emit, subscribe
            
            # Create instances
            bus = SymbolicKernelBus()
            event = SymbolicEvent(event_type="test", payload={"data": "test"})
            
            # Basic functionality test
            assert bus is not None
            assert event is not None
            assert event.event_type == "test"
            assert event.payload["data"] == "test"
            
            print("✅ SymbolicKernelBus: Real component working")
            
        except Exception as e:
            pytest.fail(f"SymbolicKernelBus real component failed: {e}")
    
    def test_import_memory_folds(self):
        """Test that we can import and use real memory folds"""
        try:
            from candidate.memory.folds.memory_fold import MemoryFold
            
            # Create a memory fold
            fold = MemoryFold(
                fold_id="test_fold",
                content="test content", 
                emotional_weight=0.5,
                timestamp=1234567890.0
            )
            
            # Basic validation
            assert fold is not None
            assert fold.fold_id == "test_fold"
            assert fold.content == "test content"
            
            print("✅ MemoryFold: Real component working")
            
        except Exception as e:
            pytest.fail(f"MemoryFold real component failed: {e}")
    
    def test_import_emotion_models(self):
        """Test that we can import and use real emotion models"""
        try:
            from emotion.models import VADModel, EmotionalState, Affect
            
            # Create VAD model
            vad = VADModel(valence=0.7, arousal=0.3, dominance=0.5)
            assert vad is not None
            assert vad.valence == 0.7
            
            # Create emotional state
            state = EmotionalState(
                primary_emotion="joy",
                intensity=0.8,
                vad_model=vad
            )
            assert state is not None
            assert state.primary_emotion == "joy"
            
            # Create affect
            affect = Affect(emotion="happiness", intensity=0.9)
            assert affect is not None
            assert affect.emotion == "happiness"
            
            print("✅ Emotion Models: Real components working")
            
        except Exception as e:
            pytest.fail(f"Emotion models real components failed: {e}")
    
    def test_import_consciousness(self):
        """Test that we can import candidate.consciousness module"""
        try:
            import candidate.consciousness
            
            # Basic import test
            assert consciousness is not None
            
            print("✅ Consciousness: Real module importable")
            
        except Exception as e:
            pytest.fail(f"Consciousness real module failed: {e}")
    
    def test_import_reasoning(self):
        """Test that we can import reasoning module"""
        try:
            import reasoning
            
            # Basic import test
            assert reasoning is not None
            
            print("✅ Reasoning: Real module importable")
            
        except Exception as e:
            pytest.fail(f"Reasoning real module failed: {e}")
    
    def test_import_orchestration_brain(self):
        """Test that we can import candidate.orchestration brain"""
        try:
            import candidate.orchestration.brain
            
            # Basic import test
            assert orchestration.brain is not None
            
            print("✅ Orchestration Brain: Real module importable")
            
        except Exception as e:
            pytest.fail(f"Orchestration brain real module failed: {e}")
    
    def test_real_symbolic_event_creation(self):
        """Test creating real symbolic events"""
        try:
            from candidate.orchestration.symbolic_kernel_bus import SymbolicEvent, EventPriority
            
            # Test basic event
            event1 = SymbolicEvent(
                event_type="test.basic",
                payload={"message": "hello world"}
            )
            assert event1.event_type == "test.basic"
            assert event1.payload["message"] == "hello world"
            
            # Test event with all parameters
            event2 = SymbolicEvent(
                event_type="test.advanced",
                payload={"data": [1, 2, 3]},
                source="test_source",
                target="test_target",
                priority=EventPriority.HIGH
            )
            assert event2.source == "test_source"
            assert event2.target == "test_target"
            assert event2.priority == EventPriority.HIGH
            
            print("✅ SymbolicEvent: Advanced creation working")
            
        except Exception as e:
            pytest.fail(f"SymbolicEvent creation failed: {e}")
    
    def test_real_vad_model_functionality(self):
        """Test real VAD model functionality"""
        try:
            from emotion.models import VADModel
            
            # Create VAD models
            vad1 = VADModel(valence=0.8, arousal=0.6, dominance=0.4)
            vad2 = VADModel(valence=-0.6, arousal=0.6, dominance=-0.4)
            
            # Test basic properties
            assert vad1.valence == 0.8
            assert vad1.arousal == 0.6
            assert vad1.dominance == 0.4
            
            # Test methods if they exist
            if hasattr(vad1, 'to_emotion_label'):
                label1 = vad1.to_emotion_label()
                label2 = vad2.to_emotion_label()
                print(f"Emotion labels: {label1}, {label2}")
            
            if hasattr(vad1, 'distance_from'):
                distance = vad1.distance_from(vad2)
                assert distance >= 0
                print(f"Emotional distance: {distance}")
            
            print("✅ VADModel: Real functionality working")
            
        except Exception as e:
            pytest.fail(f"VADModel functionality failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])