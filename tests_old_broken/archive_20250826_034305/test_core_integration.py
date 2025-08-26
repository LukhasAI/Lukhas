"""Core Module Integration Tests

Tests for the LUKHAS core system including GLYPH engine and actor system.
Verifies dry_run mode, feature flag activation, MATRIZ instrumentation,
and core functionality for core module promotion from candidate/ to lukhas/.
"""
import os
import pytest
import json
import uuid
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from typing import Dict, Any, List, Optional

# Core module imports
try:
    from candidate.core import (
        TRINITY_FRAMEWORK, IDENTITY_SYMBOL, CONSCIOUSNESS_SYMBOL, GUARDIAN_SYMBOL
    )
    from candidate.core.glyph.glyph import Glyph, GlyphEngine, GlyphType
    from candidate.core.actor_system import ActorRef, ActorSystem, get_global_actor_system
    from candidate.core.matriz_adapter import CoreMatrizAdapter
    CORE_AVAILABLE = True
except ImportError:
    Glyph = None
    GlyphEngine = None
    GlyphType = None
    ActorRef = None
    ActorSystem = None
    CoreMatrizAdapter = None
    CORE_AVAILABLE = False

# Feature flags
try:
    from candidate.flags import FeatureFlagContext, is_enabled
    FLAGS_AVAILABLE = True
except ImportError:
    FLAGS_AVAILABLE = False
    FeatureFlagContext = None


class TestCoreModuleIntegration:
    """Test core module integration for promotion"""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Setup test environment variables"""
        # Ensure dry-run mode by default
        original_env = os.environ.copy()
        os.environ.pop('CORE_ACTIVE', None)
        os.environ.pop('GLYPH_ACTIVE', None)
        os.environ.pop('LUKHAS_FLAG_core_active', None)
        yield
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)
    
    def test_core_module_availability(self):
        """Test that core module can be imported"""
        assert CORE_AVAILABLE, "Core module should be available for testing"
        assert Glyph is not None, "Glyph should be importable"
        assert GlyphEngine is not None, "GlyphEngine should be importable"
        assert ActorSystem is not None, "ActorSystem should be importable"
    
    def test_trinity_framework_symbols(self):
        """Test Trinity Framework symbols are available"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        # Test Trinity Framework constants
        assert TRINITY_FRAMEWORK == "⚛️🧠🛡️"
        assert IDENTITY_SYMBOL == "⚛️"
        assert CONSCIOUSNESS_SYMBOL == "🧠"
        assert GUARDIAN_SYMBOL == "🛡️"
    
    def test_glyph_creation_dry_run(self):
        """Test glyph creation in dry_run mode (default)"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create glyph in dry_run mode
        glyph = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"test": "data"},
            emotional_valence=0.5,
            mode="dry_run"
        )
        
        assert glyph is not None
        assert glyph.content == {"test": "data"}
        assert glyph.emotional_valence == 0.5
        assert hasattr(glyph, 'id')
        assert hasattr(glyph, 'timestamp')
        
        # In dry_run mode, glyph should not be persisted
        status = engine.get_status(mode="dry_run")
        assert status["mode"] == "dry_run"
        assert status["dry_run_operations"] >= 1
    
    def test_glyph_types_enumeration(self):
        """Test that all glyph types are available"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        # Test glyph type enumeration
        expected_types = [
            GlyphType.SEMANTIC,
            GlyphType.EMOTIONAL,
            GlyphType.TEMPORAL,
            GlyphType.CAUSAL,
            GlyphType.IDENTITY
        ]
        
        for glyph_type in expected_types:
            assert glyph_type is not None
            
        # Test glyph creation with each type
        engine = GlyphEngine()
        for glyph_type in expected_types:
            glyph = engine.create_glyph(
                glyph_type=glyph_type,
                content={"type_test": glyph_type.value},
                mode="dry_run"
            )
            assert glyph.type == glyph_type
    
    def test_glyph_feature_flag_activation(self):
        """Test glyph system activation with feature flag"""
        if not CORE_AVAILABLE or not FLAGS_AVAILABLE:
            pytest.skip("Core module or flags not available")
        
        # Test with feature flag enabled
        with FeatureFlagContext(glyph_active=True):
            engine = GlyphEngine()
            
            result = engine.create_glyph(
                glyph_type=GlyphType.SEMANTIC,
                content={"active": "test"},
                mode="live"
            )
            
            assert result is not None
            # When active, operations should be performed
            status = engine.get_status(mode="live")
            assert status["active"] is True
    
    def test_glyph_symbolic_identity_encoding(self):
        """Test glyph symbolic identity encoding"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create identity glyph with Trinity Framework symbols
        glyph = engine.create_glyph(
            glyph_type=GlyphType.IDENTITY,
            content={
                "identity": "⚛️",
                "consciousness": "🧠", 
                "guardian": "🛡️"
            },
            symbolic_encoding=True,
            mode="dry_run"
        )
        
        assert glyph.type == GlyphType.IDENTITY
        assert glyph.symbolic_encoding is True
        assert glyph.content["identity"] == "⚛️"
        assert glyph.content["consciousness"] == "🧠"
        assert glyph.content["guardian"] == "🛡️"
    
    def test_glyph_emotional_valence_range(self):
        """Test glyph emotional valence is within valid range"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Test emotional valence range validation
        for valence in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            glyph = engine.create_glyph(
                glyph_type=GlyphType.EMOTIONAL,
                content={"emotion": "test"},
                emotional_valence=valence,
                mode="dry_run"
            )
            assert -1.0 <= glyph.emotional_valence <= 1.0
            assert glyph.emotional_valence == valence
    
    def test_glyph_temporal_context(self):
        """Test glyph temporal context handling"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create temporal glyph
        temporal_context = {
            "timestamp": datetime.now().isoformat(),
            "duration": 1000,
            "sequence": 1
        }
        
        glyph = engine.create_glyph(
            glyph_type=GlyphType.TEMPORAL,
            content={"event": "test"},
            temporal_context=temporal_context,
            mode="dry_run"
        )
        
        assert glyph.type == GlyphType.TEMPORAL
        assert glyph.temporal_context == temporal_context
        assert glyph.temporal_context["duration"] == 1000
        assert glyph.temporal_context["sequence"] == 1
    
    def test_glyph_causal_linkages(self):
        """Test glyph causal linkage creation"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create causal glyph with linkages
        causal_links = ["cause_1", "cause_2", "effect_1"]
        
        glyph = engine.create_glyph(
            glyph_type=GlyphType.CAUSAL,
            content={"effect": "result"},
            causal_links=causal_links,
            mode="dry_run"
        )
        
        assert glyph.type == GlyphType.CAUSAL
        assert glyph.causal_links == causal_links
        assert len(glyph.causal_links) == 3
    
    def test_actor_system_creation(self):
        """Test actor system creation and basic functionality"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        # Create actor system
        actor_system = ActorSystem()
        assert actor_system is not None
        assert len(actor_system.actors) == 0
        
        # Test global actor system
        global_system = get_global_actor_system()
        assert global_system is not None
        assert isinstance(global_system, ActorSystem)
    
    def test_actor_registration_dry_run(self):
        """Test actor registration in dry_run mode"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        actor_system = ActorSystem()
        
        # Mock actor
        mock_actor = Mock()
        mock_actor.receive = Mock()
        
        # Register actor
        actor_ref = actor_system.register(
            "test_actor",
            mock_actor,
            mode="dry_run"
        )
        
        assert isinstance(actor_ref, ActorRef)
        assert actor_ref.actor_id == "test_actor"
        assert actor_ref.actor_system == actor_system
        
        # In dry_run mode, actor should be registered but not activated
        status = actor_system.get_status(mode="dry_run")
        assert status["mode"] == "dry_run"
        assert status["registered_actors"] >= 1
    
    def test_actor_message_passing_dry_run(self):
        """Test actor message passing in dry_run mode"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        actor_system = ActorSystem()
        
        # Mock actor
        mock_actor = Mock()
        mock_actor.receive = Mock()
        
        # Register and send message
        actor_ref = actor_system.register("test_actor", mock_actor)
        
        result = actor_ref.send(
            {"message": "test"},
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["sent"] is False  # Not actually sent in dry_run
        assert result["simulated"] is True
    
    def test_matriz_instrumentation_core(self):
        """Test that core operations have MATRIZ instrumentation"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        # Check GlyphEngine methods have instrumentation
        engine = GlyphEngine()
        assert hasattr(engine.create_glyph, "__wrapped__")
        assert hasattr(engine.get_status, "__wrapped__")
        
        # Check ActorSystem methods have instrumentation
        actor_system = ActorSystem()
        assert hasattr(actor_system.register, "__wrapped__")
        assert hasattr(actor_system.send, "__wrapped__")
    
    def test_matriz_node_emission_core(self):
        """Test that MATRIZ nodes are emitted for core operations"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        adapter = CoreMatrizAdapter()
        
        # Test glyph creation node
        node = adapter.create_node(
            node_type="core:glyph:create",
            state={"glyph_count": 1, "emotional_valence": 0.5},
            labels=["test", "core", "glyph"]
        )
        
        assert node["version"] == 1
        assert node["type"] == "core:glyph:create"
        assert "LT-CORE-" in node["id"]
        assert node["state"]["glyph_count"] == 1
        assert node["state"]["emotional_valence"] == 0.5
        assert "core" in node["labels"]
        assert "glyph" in node["labels"]
        
        # Test actor system node
        actor_node = adapter.create_node(
            node_type="core:actor:register",
            state={"actor_count": 1, "system_load": 0.2},
            labels=["actor", "system"]
        )
        
        assert actor_node["type"] == "core:actor:register"
        assert actor_node["state"]["actor_count"] == 1
    
    def test_glyph_engine_performance_metrics(self):
        """Test glyph engine performance metrics"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create multiple glyphs
        for i in range(10):
            engine.create_glyph(
                glyph_type=GlyphType.SEMANTIC,
                content={"index": i},
                mode="dry_run"
            )
        
        # Get performance metrics
        metrics = engine.get_performance_metrics()
        
        assert "total_glyphs" in metrics
        assert "average_creation_time" in metrics
        assert "memory_usage" in metrics
        assert "encoding_efficiency" in metrics
        assert metrics["total_glyphs"] >= 10
    
    def test_actor_system_supervision(self):
        """Test actor system supervision and fault tolerance"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        actor_system = ActorSystem()
        
        # Test supervision strategy
        result = actor_system.configure_supervision(
            strategy="restart",
            max_retries=3,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["strategy"] == "restart"
        assert result["max_retries"] == 3
    
    def test_glyph_drift_detection(self):
        """Test glyph drift detection capabilities"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create baseline glyph
        baseline = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"baseline": "data"},
            mode="dry_run"
        )
        
        # Create drifted glyph
        drifted = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"drifted": "data"},
            mode="dry_run"
        )
        
        # Test drift detection
        drift_score = engine.calculate_drift(
            baseline.id,
            drifted.id,
            mode="dry_run"
        )
        
        assert drift_score["ok"] is True
        assert drift_score["mode"] == "dry_run"
        assert 0.0 <= drift_score["score"] <= 1.0
    
    def test_glyph_memory_indexing(self):
        """Test glyph memory indexing functionality"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create glyph with memory index
        glyph = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"indexed": "content"},
            memory_index_key="test_index",
            mode="dry_run"
        )
        
        assert glyph.memory_index_key == "test_index"
        
        # Test index retrieval
        result = engine.get_by_index(
            "test_index",
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["found"] is False  # Not actually indexed in dry_run
    
    def test_core_error_handling(self):
        """Test error handling in core operations"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Test invalid glyph type
        result = engine.create_glyph(
            glyph_type="invalid_type",
            content={"test": "data"},
            mode="dry_run"
        )
        
        assert result["ok"] is False
        assert result["error"] == "invalid_glyph_type"
        assert result["mode"] == "dry_run"
        
        # Test invalid emotional valence
        result = engine.create_glyph(
            glyph_type=GlyphType.EMOTIONAL,
            content={"test": "data"},
            emotional_valence=2.0,  # Invalid range
            mode="dry_run"
        )
        
        assert result["ok"] is False
        assert result["error"] == "invalid_emotional_valence"
    
    def test_core_module_manifest_validation(self):
        """Test that core module manifest has required capabilities"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        import json
        import pathlib
        
        manifest_path = pathlib.Path("candidate/core/MODULE_MANIFEST.json")
        assert manifest_path.exists(), "Core module manifest should exist"
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check required capabilities
        expected_capabilities = [
            "core:glyph:create",
            "core:glyph:encode",
            "core:actor:register",
            "core:actor:send",
            "core:trinity_framework"
        ]
        
        for cap in expected_capabilities:
            assert cap in manifest["capabilities"], f"Missing capability: {cap}"
        
        # Check MATRIZ emit points
        expected_emit_points = [
            "create_glyph",
            "register_actor",
            "send_message",
            "get_status"
        ]
        
        for point in expected_emit_points:
            assert point in manifest["matriz_emit_points"], f"Missing emit point: {point}"
    
    def test_core_feature_flag_defaults(self):
        """Test that core system defaults to dry_run when feature flags are off"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        # Without feature flag, should default to dry_run
        engine = GlyphEngine()
        
        # Even when requesting live mode, should fall back to dry_run
        glyph = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"fallback_test": True},
            mode="live"
        )
        
        status = engine.get_status()
        # Should indicate dry_run behavior when feature is inactive
        assert status["effective_mode"] == "dry_run"
    
    def test_glyph_semantic_relationships(self):
        """Test glyph semantic relationship creation"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Create related glyphs
        parent_glyph = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"concept": "parent"},
            mode="dry_run"
        )
        
        child_glyph = engine.create_glyph(
            glyph_type=GlyphType.SEMANTIC,
            content={"concept": "child"},
            semantic_parent=parent_glyph.id,
            mode="dry_run"
        )
        
        assert child_glyph.semantic_parent == parent_glyph.id
        
        # Test relationship queries
        result = engine.get_semantic_children(
            parent_glyph.id,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["simulated"] is True
    
    def test_core_integration_with_trinity_framework(self):
        """Test core integration with Trinity Framework principles"""
        if not CORE_AVAILABLE:
            pytest.skip("Core module not available")
        
        engine = GlyphEngine()
        
        # Test Trinity Framework glyph creation
        trinity_glyph = engine.create_trinity_glyph(
            identity_content={"id": "test"},
            consciousness_content={"state": "aware"},
            guardian_content={"ethics": "active"},
            mode="dry_run"
        )
        
        assert trinity_glyph["ok"] is True
        assert trinity_glyph["mode"] == "dry_run"
        assert trinity_glyph["identity_glyph"] is not None
        assert trinity_glyph["consciousness_glyph"] is not None
        assert trinity_glyph["guardian_glyph"] is not None