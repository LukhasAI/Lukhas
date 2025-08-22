"""Memory Module Integration Tests

Tests for the LUKHAS fold-based memory system.
Verifies dry_run mode, feature flag activation, MATRIZ instrumentation,
and core functionality for memory module promotion from candidate/ to lukhas/.
"""
import os
import pytest
import json
import uuid
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from typing import Dict, Any, List, Optional

# Memory module imports
try:
    from candidate.memory import MemoryCore, MemoryFold
    from candidate.memory.fold import FoldManager
    from candidate.memory.service import MemoryService
    from candidate.memory.matriz_adapter import MemoryMatrizAdapter
    MEMORY_AVAILABLE = True
except ImportError:
    MemoryCore = None
    MemoryFold = None
    FoldManager = None
    MemoryService = None
    MemoryMatrizAdapter = None
    MEMORY_AVAILABLE = False

# Feature flags
try:
    from candidate.flags import FeatureFlagContext, is_enabled
    FLAGS_AVAILABLE = True
except ImportError:
    FLAGS_AVAILABLE = False
    FeatureFlagContext = None


class TestMemoryModuleIntegration:
    """Test memory module integration for promotion"""
    
    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Setup test environment variables"""
        # Ensure dry-run mode by default
        original_env = os.environ.copy()
        os.environ.pop('MEMORY_ACTIVE', None)
        os.environ.pop('LUKHAS_FLAG_memory_active', None)
        yield
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)
    
    def test_memory_module_availability(self):
        """Test that memory module can be imported"""
        assert MEMORY_AVAILABLE, "Memory module should be available for testing"
        assert MemoryCore is not None, "MemoryCore should be importable"
        assert MemoryFold is not None, "MemoryFold should be importable"
        assert FoldManager is not None, "FoldManager should be importable"
    
    def test_memory_fold_creation_dry_run(self):
        """Test memory fold creation in dry_run mode (default)"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Create fold in dry_run mode
        fold = fold_manager.create_fold(
            content={"test": "data"},
            causal_chain=["test_event"],
            mode="dry_run"
        )
        
        assert fold is not None
        assert fold.content == {"test": "data"}
        assert fold.causal_chain == ["test_event"]
        assert hasattr(fold, 'id')
        assert hasattr(fold, 'timestamp')
        
        # In dry_run mode, fold should not be persisted
        status = fold_manager.get_status(mode="dry_run")
        assert status["mode"] == "dry_run"
        assert status["dry_run_operations"] >= 1
    
    def test_memory_fold_limit_enforcement(self):
        """Test that memory fold limit (1000) is enforced"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Test cascade prevention at limit
        for i in range(FoldManager.MAX_FOLDS + 10):
            fold = fold_manager.create_fold(
                content={"index": i},
                mode="dry_run"
            )
            assert fold is not None
        
        # Should maintain cascade prevention rate of 99.7%
        status = fold_manager.get_status()
        assert status["cascade_prevention_rate"] >= 0.997
        assert len(fold_manager.folds) <= FoldManager.MAX_FOLDS
    
    def test_memory_feature_flag_activation(self):
        """Test memory system activation with feature flag"""
        if not MEMORY_AVAILABLE or not FLAGS_AVAILABLE:
            pytest.skip("Memory module or flags not available")
        
        # Test with feature flag enabled
        with FeatureFlagContext(memory_active=True):
            fold_manager = FoldManager()
            
            result = fold_manager.create_fold(
                content={"active": "test"},
                mode="live"
            )
            
            assert result is not None
            # When active, operations should be performed
            status = fold_manager.get_status(mode="live")
            assert status["active"] is True
    
    def test_memory_service_dry_run_mode(self):
        """Test memory service in dry_run mode"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        service = MemoryService()
        
        # Store memory in dry_run mode
        result = service.store(
            content={"service": "test"},
            metadata={"importance": 0.8},
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert "fold_id" in result
        assert result["stored"] is False  # Not actually stored in dry_run
    
    def test_memory_retrieval_dry_run(self):
        """Test memory retrieval in dry_run mode"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        service = MemoryService()
        
        # Retrieve in dry_run mode
        result = service.retrieve(
            query={"type": "test"},
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["results"] == []  # Empty in dry_run
        assert result["simulated"] is True
    
    def test_memory_consolidation_dry_run(self):
        """Test memory consolidation in dry_run mode"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        service = MemoryService()
        
        # Run consolidation in dry_run mode
        result = service.consolidate(
            threshold=0.5,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["consolidated_count"] >= 0
        assert result["simulated"] is True
    
    def test_matriz_instrumentation_memory(self):
        """Test that memory operations have MATRIZ instrumentation"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        # Check FoldManager methods have instrumentation
        fold_manager = FoldManager()
        assert hasattr(fold_manager.create_fold, "__wrapped__")
        assert hasattr(fold_manager.get_status, "__wrapped__")
        
        # Check MemoryService methods have instrumentation
        service = MemoryService()
        assert hasattr(service.store, "__wrapped__")
        assert hasattr(service.retrieve, "__wrapped__")
        assert hasattr(service.consolidate, "__wrapped__")
    
    def test_matriz_node_emission(self):
        """Test that MATRIZ nodes are emitted for memory operations"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        adapter = MemoryMatrizAdapter()
        
        # Test fold creation node
        node = adapter.create_node(
            node_type="memory:fold:create",
            state={"fold_count": 1, "importance": 0.8},
            labels=["test", "memory"]
        )
        
        assert node["version"] == 1
        assert node["type"] == "memory:fold:create"
        assert "LT-MEM-" in node["id"]
        assert node["state"]["fold_count"] == 1
        assert node["state"]["importance"] == 0.8
        assert "test" in node["labels"]
        assert "memory" in node["labels"]
    
    def test_memory_causal_chain_preservation(self):
        """Test that causal chains are preserved in memory folds"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Create fold with causal chain
        causal_chain = ["event_1", "event_2", "event_3"]
        fold = fold_manager.create_fold(
            content={"chain_test": True},
            causal_chain=causal_chain,
            mode="dry_run"
        )
        
        assert fold.causal_chain == causal_chain
        assert len(fold.causal_chain) == 3
        
        # Test chain extension
        extended_fold = fold_manager.extend_causal_chain(
            fold.id,
            "event_4",
            mode="dry_run"
        )
        
        assert extended_fold["ok"] is True
        assert extended_fold["mode"] == "dry_run"
    
    def test_memory_emotional_valence_tracking(self):
        """Test emotional valence tracking in memory folds"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Create fold with emotional valence
        fold = fold_manager.create_fold(
            content={"emotion": "joy"},
            emotional_valence=0.8,
            mode="dry_run"
        )
        
        assert fold.emotional_valence == 0.8
        assert -1.0 <= fold.emotional_valence <= 1.0
        
        # Test valence update
        result = fold_manager.update_valence(
            fold.id,
            new_valence=0.9,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
    
    def test_memory_importance_scoring(self):
        """Test importance scoring for memory folds"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Create folds with different importance
        high_importance = fold_manager.create_fold(
            content={"critical": "data"},
            importance=0.9,
            mode="dry_run"
        )
        
        low_importance = fold_manager.create_fold(
            content={"routine": "data"},
            importance=0.2,
            mode="dry_run"
        )
        
        assert high_importance.importance == 0.9
        assert low_importance.importance == 0.2
        assert 0.0 <= high_importance.importance <= 1.0
        assert 0.0 <= low_importance.importance <= 1.0
    
    def test_memory_access_counting(self):
        """Test access counting for memory folds"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Create fold
        fold = fold_manager.create_fold(
            content={"access_test": True},
            mode="dry_run"
        )
        
        assert fold.accessed_count == 0
        
        # Simulate access
        result = fold_manager.access_fold(
            fold.id,
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["access_count"] >= 1
    
    def test_memory_error_handling(self):
        """Test error handling in memory operations"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Test invalid fold access
        result = fold_manager.access_fold(
            "invalid_fold_id",
            mode="dry_run"
        )
        
        assert result["ok"] is False
        assert result["error"] == "fold_not_found"
        assert result["mode"] == "dry_run"
        
        # Test invalid causal chain extension
        result = fold_manager.extend_causal_chain(
            "invalid_fold_id",
            "new_event",
            mode="dry_run"
        )
        
        assert result["ok"] is False
        assert result["error"] == "fold_not_found"
    
    def test_memory_performance_metrics(self):
        """Test memory system performance metrics"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        fold_manager = FoldManager()
        
        # Create multiple folds
        for i in range(10):
            fold_manager.create_fold(
                content={"index": i},
                mode="dry_run"
            )
        
        # Get performance metrics
        metrics = fold_manager.get_performance_metrics()
        
        assert "total_folds" in metrics
        assert "average_creation_time" in metrics
        assert "memory_usage" in metrics
        assert "cascade_prevention_rate" in metrics
        assert metrics["total_folds"] >= 10
    
    def test_memory_module_manifest_validation(self):
        """Test that memory module manifest has required capabilities"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        import json
        import pathlib
        
        manifest_path = pathlib.Path("candidate/memory/MODULE_MANIFEST.json")
        assert manifest_path.exists(), "Memory module manifest should exist"
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check required capabilities
        expected_capabilities = [
            "memory:fold:create",
            "memory:fold:retrieve", 
            "memory:consolidation",
            "memory:causal_chain",
            "memory:emotional_valence"
        ]
        
        for cap in expected_capabilities:
            assert cap in manifest["capabilities"], f"Missing capability: {cap}"
        
        # Check MATRIZ emit points
        expected_emit_points = [
            "create_fold",
            "retrieve",
            "consolidate",
            "get_status"
        ]
        
        for point in expected_emit_points:
            assert point in manifest["matriz_emit_points"], f"Missing emit point: {point}"
    
    def test_memory_feature_flag_defaults(self):
        """Test that memory system defaults to dry_run when feature flags are off"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        # Without feature flag, should default to dry_run
        fold_manager = FoldManager()
        
        # Even when requesting live mode, should fall back to dry_run
        fold = fold_manager.create_fold(
            content={"fallback_test": True},
            mode="live"
        )
        
        status = fold_manager.get_status()
        # Should indicate dry_run behavior when feature is inactive
        assert status["effective_mode"] == "dry_run"
    
    def test_memory_integration_with_consciousness(self):
        """Test memory integration with consciousness module (interface)"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        service = MemoryService()
        
        # Test consciousness-memory bridge
        result = service.connect_consciousness(
            consciousness_id="test_consciousness",
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["connected"] is False  # Not actually connected in dry_run
        assert result["bridge_established"] is True  # Interface works
    
    def test_memory_integration_with_identity(self):
        """Test memory integration with identity module (interface)"""
        if not MEMORY_AVAILABLE:
            pytest.skip("Memory module not available")
        
        service = MemoryService()
        
        # Test identity-memory bridge
        result = service.associate_identity(
            identity_id="test_lambda_id",
            memory_scope="personal",
            mode="dry_run"
        )
        
        assert result["ok"] is True
        assert result["mode"] == "dry_run"
        assert result["associated"] is False  # Not actually associated in dry_run
        assert result["scope"] == "personal"