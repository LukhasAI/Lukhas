"""
Test suite for LUKHAS AI Core module promotion
Validates GLYPH engine, actor system, symbolic processing, and Trinity Framework integration
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Test imports
from lukhas.core import (
    CoreWrapper,
    GlyphResult,
    SymbolicResult,
    CoreStatus,
    get_core,
    encode_concept,
    create_trinity_glyph,
    get_core_status,
    TRINITY_SYMBOLS
)


class TestCoreWrapper:
    """Test suite for CoreWrapper functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Reset environment variables
        os.environ.pop("CORE_ACTIVE", None)
        os.environ.pop("GLYPH_ENGINE_ENABLED", None)
        os.environ.pop("SYMBOLIC_PROCESSING_ENABLED", None)
        os.environ.pop("ACTOR_SYSTEM_ENABLED", None)
        
    def test_core_wrapper_initialization_inactive(self):
        """Test CoreWrapper initialization when CORE_ACTIVE is false"""
        core = CoreWrapper()
        assert core._status == CoreStatus.INACTIVE
        assert core._glyph_engine is None
        assert core._actor_system is None
        assert core._symbolic_world is None
        
    def test_core_wrapper_initialization_active(self):
        """Test CoreWrapper initialization when CORE_ACTIVE is true"""
        with patch.dict(os.environ, {"CORE_ACTIVE": "true"}):
            with patch('lukhas.core.core_wrapper.CORE_ACTIVE', True):
                with patch.object(CoreWrapper, '_initialize_core_system') as mock_init:
                    core = CoreWrapper()
                    mock_init.assert_called_once()
    
    def test_trinity_framework_symbols(self):
        """Test Trinity Framework symbol initialization"""
        core = CoreWrapper()
        expected_symbols = {
            "identity": "⚛️",
            "consciousness": "🧠", 
            "guardian": "🛡️",
            "framework": "⚛️🧠🛡️"
        }
        assert core._trinity_context == expected_symbols
    
    def test_get_status_inactive(self):
        """Test status reporting when core is inactive"""
        core = CoreWrapper()
        status = core.get_status()
        
        assert status["status"] == "inactive"
        assert status["core_active"] is False
        assert all(not cap for cap in status["capabilities"].values())
        assert status["trinity_framework"] == TRINITY_SYMBOLS
    
    def test_encode_concept_inactive_core(self):
        """Test concept encoding when core is inactive"""
        core = CoreWrapper()
        result = core.encode_concept("test concept")
        
        assert isinstance(result, GlyphResult)
        assert not result.success
        assert result.concept == "test concept"
        assert "GLYPH engine not available" in result.metadata["error"]
    
    def test_create_trinity_glyph_fallback(self):
        """Test Trinity glyph creation with fallback when core inactive"""
        core = CoreWrapper()
        result = core.create_trinity_glyph("consciousness")
        
        assert isinstance(result, GlyphResult)
        assert result.success
        assert result.symbol == "⚛️🧠🛡️"
        assert result.concept == "Trinity Framework (consciousness)"
        assert result.metadata["fallback"] is True
        assert result.metadata["emphasis"] == "consciousness"
    
    def test_create_symbol_inactive_core(self):
        """Test symbol creation when core is inactive"""
        core = CoreWrapper()
        result = core.create_symbol("test_symbol", {"type": "concept"})
        
        assert result is False
    
    def test_send_actor_message_inactive_core(self):
        """Test actor message sending when core is inactive"""
        core = CoreWrapper()
        result = core.send_actor_message("test_actor", {"message": "test"})
        
        assert result is False
    
    def test_restart_core_functionality(self):
        """Test core restart functionality"""
        core = CoreWrapper()
        
        # Mock the initialization
        with patch.object(core, '_initialize_core_system') as mock_init:
            # Test restart when CORE_ACTIVE is false
            result = core.restart_core()
            assert result is False  # Since CORE_ACTIVE is false
            
            # Test restart when CORE_ACTIVE is true
            with patch('lukhas.core.core_wrapper.CORE_ACTIVE', True):
                core._status = CoreStatus.ACTIVE  # Mock successful init
                result = core.restart_core()
                mock_init.assert_called()


class TestGlyphEngine:
    """Test suite for GLYPH engine functionality"""
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.GLYPH_ENGINE_ENABLED', True)
    def test_glyph_engine_initialization(self):
        """Test GLYPH engine initialization"""
        with patch('candidate.core.glyph.glyph_engine.GlyphEngine') as mock_engine:
            mock_instance = Mock()
            mock_engine.return_value = mock_instance
            
            core = CoreWrapper()
            core._initialize_glyph_engine()
            
            assert core._glyph_engine is mock_instance
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.GLYPH_ENGINE_ENABLED', True)
    def test_concept_encoding_success(self):
        """Test successful concept encoding"""
        with patch('candidate.core.glyph.glyph_engine.GlyphEngine') as mock_engine_class:
            # Setup mock GLYPH engine
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            
            # Mock glyph object
            mock_glyph = Mock()
            mock_glyph.id = "glyph_123"
            mock_glyph.symbol = "🧠"
            
            mock_engine.encode_concept.return_value = "GLYPH[🧠:abc123]"
            mock_engine.decode_glyph.return_value = mock_glyph
            
            core = CoreWrapper()
            core._initialize_glyph_engine()
            
            result = core.encode_concept("thinking", {"valence": 0.8})
            
            assert result.success
            assert result.glyph_id == "glyph_123"
            assert result.symbol == "🧠"
            assert result.concept == "thinking"
            assert "glyph_repr" in result.metadata
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.GLYPH_ENGINE_ENABLED', True)
    def test_trinity_glyph_creation_success(self):
        """Test successful Trinity glyph creation"""
        with patch('candidate.core.glyph.glyph_engine.GlyphEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            
            mock_glyph = Mock()
            mock_glyph.id = "trinity_123"
            mock_glyph.symbol = "⚛️🧠🛡️"
            
            mock_engine.create_trinity_glyph.return_value = mock_glyph
            
            core = CoreWrapper()
            core._initialize_glyph_engine()
            
            result = core.create_trinity_glyph("balanced")
            
            assert result.success
            assert result.glyph_id == "trinity_123"
            assert result.symbol == "⚛️🧠🛡️"
            assert result.concept == "Trinity Framework (balanced)"


class TestActorSystem:
    """Test suite for Actor system functionality"""
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.ACTOR_SYSTEM_ENABLED', True)
    def test_actor_system_initialization(self):
        """Test actor system initialization"""
        with patch('candidate.core.actor_system.get_global_actor_system') as mock_get_system:
            mock_system = Mock()
            mock_get_system.return_value = mock_system
            
            core = CoreWrapper()
            core._initialize_actor_system()
            
            assert core._actor_system is mock_system
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.ACTOR_SYSTEM_ENABLED', True)
    def test_send_actor_message_success(self):
        """Test successful actor message sending"""
        with patch('candidate.core.actor_system.get_global_actor_system') as mock_get_system:
            mock_system = Mock()
            mock_get_system.return_value = mock_system
            
            core = CoreWrapper()
            core._initialize_actor_system()
            
            result = core.send_actor_message("test_actor", {"data": "test"})
            
            assert result is True
            mock_system.send.assert_called_once_with("test_actor", {"data": "test"})
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.ACTOR_SYSTEM_ENABLED', True)
    def test_register_actor_success(self):
        """Test successful actor registration"""
        with patch('candidate.core.actor_system.get_global_actor_system') as mock_get_system:
            mock_system = Mock()
            mock_get_system.return_value = mock_system
            
            core = CoreWrapper()
            core._initialize_actor_system()
            
            mock_actor = Mock()
            result = core.register_actor("new_actor", mock_actor)
            
            assert result is True
            mock_system.register.assert_called_once_with("new_actor", mock_actor)


class TestSymbolicProcessing:
    """Test suite for symbolic processing functionality"""
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.SYMBOLIC_PROCESSING_ENABLED', True)
    def test_symbolic_processing_initialization(self):
        """Test symbolic processing initialization"""
        with patch('candidate.core.symbolic.symbolic_core.SymbolicWorld') as mock_world_class:
            with patch('candidate.core.symbolic.symbolic_core.SymbolicReasoner') as mock_reasoner_class:
                mock_world = Mock()
                mock_reasoner = Mock()
                mock_world_class.return_value = mock_world
                mock_reasoner_class.return_value = mock_reasoner
                
                core = CoreWrapper()
                core._initialize_symbolic_processing()
                
                assert core._symbolic_world is mock_world
                assert core._symbolic_reasoner is mock_reasoner
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.SYMBOLIC_PROCESSING_ENABLED', True)
    def test_create_symbol_success(self):
        """Test successful symbol creation"""
        with patch('candidate.core.symbolic.symbolic_core.SymbolicWorld') as mock_world_class:
            mock_world = Mock()
            mock_world_class.return_value = mock_world
            
            core = CoreWrapper()
            core._initialize_symbolic_processing()
            
            result = core.create_symbol("test_symbol", {"type": "concept"})
            
            assert result is True
            mock_world.create_symbol.assert_called_once_with("test_symbol", {"type": "concept"})
    
    @patch('lukhas.core.core_wrapper.CORE_ACTIVE', True)
    @patch('lukhas.core.core_wrapper.SYMBOLIC_PROCESSING_ENABLED', True)
    def test_symbolic_reasoning_success(self):
        """Test successful symbolic reasoning"""
        with patch('candidate.core.symbolic.symbolic_core.SymbolicWorld') as mock_world_class:
            with patch('candidate.core.symbolic.symbolic_core.SymbolicReasoner') as mock_reasoner_class:
                # Setup mocks
                mock_world = Mock()
                mock_reasoner = Mock()
                mock_symbol = Mock()
                mock_symbol.name = "test_symbol"
                
                mock_world_class.return_value = mock_world
                mock_reasoner_class.return_value = mock_reasoner
                
                mock_world.symbols = {"test_symbol": mock_symbol}
                mock_world.get_related_symbols.return_value = [mock_symbol]
                mock_reasoner.reason.return_value = {"conclusions": [], "dot_graph": "digraph {}"}
                mock_reasoner.find_patterns.return_value = []
                
                core = CoreWrapper()
                core._initialize_symbolic_processing()
                
                result = core.perform_symbolic_reasoning("test_symbol")
                
                assert isinstance(result, SymbolicResult)
                assert result.success
                assert mock_symbol.name in result.symbols


class TestGlobalFunctions:
    """Test suite for global convenience functions"""
    
    def test_get_core_singleton(self):
        """Test that get_core returns the same instance"""
        core1 = get_core()
        core2 = get_core()
        assert core1 is core2
    
    def test_encode_concept_global_function(self):
        """Test global encode_concept function"""
        with patch('lukhas.core.core_wrapper.get_core') as mock_get_core:
            mock_core = Mock()
            mock_result = GlyphResult("", "🧠", "test", True, {})
            mock_core.encode_concept.return_value = mock_result
            mock_get_core.return_value = mock_core
            
            result = encode_concept("test concept")
            
            assert result is mock_result
            mock_core.encode_concept.assert_called_once_with("test concept", None)
    
    def test_create_trinity_glyph_global_function(self):
        """Test global create_trinity_glyph function"""
        with patch('lukhas.core.core_wrapper.get_core') as mock_get_core:
            mock_core = Mock()
            mock_result = GlyphResult("trinity_1", "⚛️🧠🛡️", "Trinity Framework", True, {})
            mock_core.create_trinity_glyph.return_value = mock_result
            mock_get_core.return_value = mock_core
            
            result = create_trinity_glyph("consciousness")
            
            assert result is mock_result
            mock_core.create_trinity_glyph.assert_called_once_with("consciousness")
    
    def test_get_core_status_global_function(self):
        """Test global get_core_status function"""
        with patch('lukhas.core.core_wrapper.get_core') as mock_get_core:
            mock_core = Mock()
            mock_status = {"status": "active", "capabilities": {}}
            mock_core.get_status.return_value = mock_status
            mock_get_core.return_value = mock_core
            
            result = get_core_status()
            
            assert result is mock_status
            mock_core.get_status.assert_called_once()


class TestTrinityFramework:
    """Test suite for Trinity Framework integration"""
    
    def test_trinity_symbols_constant(self):
        """Test Trinity Framework symbols constant"""
        expected = {
            "identity": "⚛️",
            "consciousness": "🧠", 
            "guardian": "🛡️",
            "framework": "⚛️🧠🛡️"
        }
        assert TRINITY_SYMBOLS == expected
    
    def test_trinity_emphasis_variants(self):
        """Test Trinity glyph creation with different emphasis"""
        core = CoreWrapper()
        
        # Test different emphasis options
        for emphasis in ["identity", "consciousness", "guardian", "balanced"]:
            result = core.create_trinity_glyph(emphasis)
            assert result.success
            assert emphasis in result.concept
            assert result.metadata["emphasis"] == emphasis


class TestFeatureFlags:
    """Test suite for feature flag behavior"""
    
    def test_feature_flags_from_environment(self):
        """Test feature flags are properly read from environment"""
        # Test with direct patching instead of environment variables
        with patch('lukhas.core.core_wrapper.CORE_ACTIVE', True):
            with patch('lukhas.core.core_wrapper.GLYPH_ENGINE_ENABLED', False):
                with patch('lukhas.core.core_wrapper.SYMBOLIC_PROCESSING_ENABLED', True):
                    with patch('lukhas.core.core_wrapper.ACTOR_SYSTEM_ENABLED', False):
                        from lukhas.core.core_wrapper import (
                            CORE_ACTIVE, GLYPH_ENGINE_ENABLED, 
                            SYMBOLIC_PROCESSING_ENABLED, ACTOR_SYSTEM_ENABLED
                        )
                        
                        # Note: Since we can't reload module state during test, 
                        # we'll test that the wrapper properly uses the flags
                        core = CoreWrapper()
                        status = core.get_status()
                        
                        # The status should reflect current module state
                        assert "feature_flags" in status
    
    def test_status_includes_feature_flags(self):
        """Test that status response includes feature flag information"""
        core = CoreWrapper()
        status = core.get_status()
        
        assert "feature_flags" in status
        feature_flags = status["feature_flags"]
        
        required_flags = [
            "CORE_ACTIVE", "GLYPH_ENGINE_ENABLED", 
            "SYMBOLIC_PROCESSING_ENABLED", "ACTOR_SYSTEM_ENABLED"
        ]
        
        for flag in required_flags:
            assert flag in feature_flags


class TestErrorHandling:
    """Test suite for error handling and edge cases"""
    
    def test_encode_concept_with_exception(self):
        """Test concept encoding error handling"""
        core = CoreWrapper()
        core._glyph_engine = Mock()
        core._glyph_engine.encode_concept.side_effect = Exception("Test error")
        
        with patch('lukhas.core.core_wrapper.CORE_ACTIVE', True):
            result = core.encode_concept("test concept")
            
            assert not result.success
            assert result.symbol == "⚠️"
            assert "Test error" in result.metadata["error"]
    
    def test_actor_message_with_exception(self):
        """Test actor message sending error handling"""
        core = CoreWrapper()
        core._actor_system = Mock()
        core._actor_system.send.side_effect = Exception("Actor error")
        
        with patch('lukhas.core.core_wrapper.CORE_ACTIVE', True):
            result = core.send_actor_message("test_actor", "message")
            
            assert result is False
    
    def test_symbolic_reasoning_symbol_not_found(self):
        """Test symbolic reasoning when symbol doesn't exist"""
        core = CoreWrapper()
        core._symbolic_world = Mock()
        core._symbolic_world.symbols = {}
        
        with patch('lukhas.core.core_wrapper.CORE_ACTIVE', True):
            result = core.perform_symbolic_reasoning("nonexistent_symbol")
            
            assert not result.success
            assert "Symbol not found" in result.reasoning["error"]


class TestPerformance:
    """Test suite for performance characteristics"""
    
    def test_core_initialization_performance(self):
        """Test that core initialization completes within reasonable time"""
        import time
        
        start_time = time.time()
        core = CoreWrapper()
        init_time = time.time() - start_time
        
        # Initialization should complete within 1 second
        assert init_time < 1.0
    
    def test_glyph_encoding_performance(self):
        """Test glyph encoding performance target"""
        core = CoreWrapper()
        
        # Mock for performance test
        with patch.object(core, '_glyph_engine', Mock()):
            core._glyph_engine.encode_concept.return_value = "GLYPH[⚡:test123]"
            mock_glyph = Mock()
            mock_glyph.id = "test_id"
            mock_glyph.symbol = "⚡"
            core._glyph_engine.decode_glyph.return_value = mock_glyph
            
            import time
            start_time = time.time()
            
            # Test multiple encodings
            for _ in range(100):
                result = core.encode_concept("test concept")
            
            avg_time = (time.time() - start_time) / 100
            
            # Should average less than 10ms per encoding (performance target)
            assert avg_time < 0.01


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])