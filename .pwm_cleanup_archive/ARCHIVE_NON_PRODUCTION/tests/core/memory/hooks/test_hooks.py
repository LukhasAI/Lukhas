"""Tests for memory hook system

ΛTAG: test_memory_hooks
"""

from datetime import datetime

import pytest

from memory.hooks.base import HookExecutionError, MemoryHook, MemoryItem
from memory.hooks.registry import (
    HookPriority,
    HookRegistrationError,
    HookRegistry,
)


class TestMemoryItem:
    """Test MemoryItem dataclass"""

    def test_memory_item_creation(self):
        """Test basic memory item creation"""
        item = MemoryItem(
            content="test content",
            metadata={"source": "test"},
            fold_level=2,
            glyphs=["Λ", "Ω"],
        )

        assert item.content == "test content"
        assert item.metadata["source"] == "test"
        assert item.fold_level == 2
        assert len(item.glyphs) == 2
        assert isinstance(item.timestamp, datetime)
        assert isinstance(item.memory_id, str)

    def test_memory_item_validation(self):
        """Test memory item validation"""
        # None content should fail
        with pytest.raises(ValueError, match="content cannot be None"):
            MemoryItem(content=None)

        # Invalid entropy
        with pytest.raises(ValueError, match="Entropy must be between"):
            MemoryItem(content="test", entropy=1.5)

        # Invalid emotional valence
        with pytest.raises(ValueError, match="Emotional valence must be between"):
            MemoryItem(content="test", emotional_valence=2.0)

    def test_memory_item_lineage(self):
        """Test causal lineage management"""
        item = MemoryItem(content="test")

        # Add ancestors
        item.add_to_lineage("ancestor1")
        item.add_to_lineage("ancestor2")
        item.add_to_lineage("ancestor1")  # Duplicate

        assert len(item.causal_lineage) == 2
        assert "ancestor1" in item.causal_lineage
        assert "ancestor2" in item.causal_lineage

    def test_memory_item_glyphs(self):
        """Test glyph management"""
        item = MemoryItem(content="test")

        item.add_glyph("Λ")
        item.add_glyph("Ω")
        item.add_glyph("Λ")  # Duplicate

        assert len(item.glyphs) == 2
        assert "Λ" in item.glyphs

    def test_symbolic_weight_calculation(self):
        """Test symbolic weight calculation"""
        # High coherence, high resonance, low entropy = high weight
        item1 = MemoryItem(content="test", coherence=0.9, resonance=0.8, entropy=0.1)
        weight1 = item1.calculate_symbolic_weight()
        assert weight1 > 0.8

        # Low coherence, low resonance, high entropy = low weight
        item2 = MemoryItem(content="test", coherence=0.2, resonance=0.1, entropy=0.9)
        weight2 = item2.calculate_symbolic_weight()
        assert weight2 < 0.3

        # With emotional intensity
        item3 = MemoryItem(
            content="test",
            coherence=0.5,
            resonance=0.5,
            entropy=0.5,
            emotional_intensity=0.8,
        )
        weight3 = item3.calculate_symbolic_weight()
        assert weight3 > 0.5


class MockHook(MemoryHook):
    """Mock hook for testing"""

    def __init__(
        self,
        name="MockHook",
        version="1.0.0",
        transform_before=None,
        transform_after=None,
    ):
        super().__init__()
        self.name = name
        self.version = version
        self.transform_before = transform_before
        self.transform_after = transform_after
        self.before_count = 0
        self.after_count = 0

    def before_store(self, item: MemoryItem) -> MemoryItem:
        self.before_count += 1
        if self.transform_before:
            return self.transform_before(item)
        return item

    def after_recall(self, item: MemoryItem) -> MemoryItem:
        self.after_count += 1
        if self.transform_after:
            return self.transform_after(item)
        return item

    def get_hook_name(self) -> str:
        return self.name

    def get_hook_version(self) -> str:
        return self.version


class TestMemoryHook:
    """Test MemoryHook abstract base class"""

    def test_hook_metrics(self):
        """Test hook metrics tracking"""
        hook = MockHook()
        item = MemoryItem(content="test")

        # Initial metrics
        metrics = hook.get_metrics()
        assert metrics["before_store_count"] == 0
        assert metrics["after_recall_count"] == 0

        # Execute operations
        hook.before_store(item)
        hook.after_recall(item)

        # Manually update metrics for testing
        hook._update_metrics("before_store", 0.01)
        hook._update_metrics("after_recall", 0.02)

        metrics = hook.get_metrics()
        assert metrics["before_store_count"] == 1
        assert metrics["after_recall_count"] == 1
        assert metrics["average_processing_time_ms"] > 0

    def test_hook_enable_disable(self):
        """Test hook enable/disable functionality"""
        hook = MockHook()

        assert hook.is_enabled()

        hook.disable()
        assert not hook.is_enabled()

        hook.enable()
        assert hook.is_enabled()

    def test_fold_integrity_validation(self):
        """Test fold integrity validation"""
        hook = MockHook()

        # Uncompressed item - always valid
        item1 = MemoryItem(content="test", is_compressed=False)
        assert hook.validate_fold_integrity(item1)

        # Compressed with valid data
        item2 = MemoryItem(
            content="compressed",
            is_compressed=True,
            compression_ratio=2.5,
            fold_signature="sig123",
            causal_lineage=["ancestor1"],
        )
        assert hook.validate_fold_integrity(item2)

        # Compressed with invalid ratio
        item3 = MemoryItem(
            content="compressed",
            is_compressed=True,
            compression_ratio=150.0,  # Too high
            fold_signature="sig123",
            causal_lineage=["ancestor1"],
        )
        assert not hook.validate_fold_integrity(item3)

        # Compressed without signature
        item4 = MemoryItem(
            content="compressed",
            is_compressed=True,
            compression_ratio=2.0,
            fold_signature=None,
            causal_lineage=["ancestor1"],
        )
        assert not hook.validate_fold_integrity(item4)

    def test_symbolic_consistency_validation(self):
        """Test symbolic consistency validation"""
        hook = MockHook()

        # Consistent glyphs
        item1 = MemoryItem(content="test", glyphs=["🌱", "✓", "🛡️"])
        assert hook.validate_symbolic_consistency(item1)

        # Contradictory glyphs
        item2 = MemoryItem(content="test", glyphs=["🌱", "💀"])
        assert not hook.validate_symbolic_consistency(item2)

        # Inconsistent metrics
        item3 = MemoryItem(
            content="test",
            entropy=0.9,  # High
            coherence=0.9,  # Also high - inconsistent
        )
        assert not hook.validate_symbolic_consistency(item3)


class TestHookRegistry:
    """Test HookRegistry functionality"""

    def test_registry_registration(self):
        """Test hook registration"""
        registry = HookRegistry()
        hook = MockHook("TestHook")

        registry.register_hook(hook)

        hooks_info = registry.get_registered_hooks()
        assert "TestHook" in hooks_info
        assert hooks_info["TestHook"]["priority"] == "NORMAL"

    def test_registry_priority_registration(self):
        """Test registration with different priorities"""
        registry = HookRegistry()

        critical_hook = MockHook("CriticalHook")
        normal_hook = MockHook("NormalHook")
        low_hook = MockHook("LowHook")

        registry.register_hook(critical_hook, priority=HookPriority.CRITICAL)
        registry.register_hook(normal_hook, priority=HookPriority.NORMAL)
        registry.register_hook(low_hook, priority=HookPriority.LOW)

        hooks_info = registry.get_registered_hooks()
        assert hooks_info["CriticalHook"]["priority"] == "CRITICAL"
        assert hooks_info["NormalHook"]["priority"] == "NORMAL"
        assert hooks_info["LowHook"]["priority"] == "LOW"

    def test_registry_duplicate_registration(self):
        """Test duplicate registration handling"""
        registry = HookRegistry()
        hook1 = MockHook("TestHook")
        hook2 = MockHook("TestHook")

        registry.register_hook(hook1)

        with pytest.raises(HookRegistrationError, match="already registered"):
            registry.register_hook(hook2)

    def test_registry_max_hooks_limit(self):
        """Test maximum hooks per priority limit"""
        registry = HookRegistry(max_hooks_per_priority=2)

        hook1 = MockHook("Hook1")
        hook2 = MockHook("Hook2")
        hook3 = MockHook("Hook3")

        registry.register_hook(hook1, priority=HookPriority.NORMAL)
        registry.register_hook(hook2, priority=HookPriority.NORMAL)

        with pytest.raises(HookRegistrationError, match="Maximum hooks"):
            registry.register_hook(hook3, priority=HookPriority.NORMAL)

    def test_registry_unregistration(self):
        """Test hook unregistration"""
        registry = HookRegistry()
        hook = MockHook("TestHook")

        registry.register_hook(hook)
        assert "TestHook" in registry.get_registered_hooks()

        success = registry.unregister_hook("TestHook")
        assert success
        assert "TestHook" not in registry.get_registered_hooks()

        # Unregistering again should return False
        assert not registry.unregister_hook("TestHook")

    def test_hook_execution_order(self):
        """Test hooks execute in priority order"""
        registry = HookRegistry()
        execution_order = []

        def make_transform(name):
            def transform(item):
                execution_order.append(name)
                return item

            return transform

        critical_hook = MockHook(
            "Critical", transform_before=make_transform("critical")
        )
        high_hook = MockHook("High", transform_before=make_transform("high"))
        normal_hook = MockHook("Normal", transform_before=make_transform("normal"))
        low_hook = MockHook("Low", transform_before=make_transform("low"))

        # Register in random order
        registry.register_hook(normal_hook, priority=HookPriority.NORMAL)
        registry.register_hook(critical_hook, priority=HookPriority.CRITICAL)
        registry.register_hook(low_hook, priority=HookPriority.LOW)
        registry.register_hook(high_hook, priority=HookPriority.HIGH)

        # Execute
        item = MemoryItem(content="test")
        registry.execute_before_store(item)

        # Check execution order
        assert execution_order == ["critical", "high", "normal", "low"]

    def test_hook_transformation(self):
        """Test hooks can transform memory items"""
        registry = HookRegistry()

        def add_metadata(item):
            item.metadata["processed"] = True
            item.add_glyph("✓")
            return item

        def add_lineage(item):
            item.add_to_lineage("hook_processor")
            return item

        hook1 = MockHook("MetadataHook", transform_before=add_metadata)
        hook2 = MockHook("LineageHook", transform_before=add_lineage)

        registry.register_hook(hook1)
        registry.register_hook(hook2)

        # Process item
        item = MemoryItem(content="test")
        processed = registry.execute_before_store(item)

        assert processed.metadata.get("processed") is True
        assert "✓" in processed.glyphs
        assert "hook_processor" in processed.causal_lineage

    def test_hook_failure_handling(self):
        """Test handling of hook failures"""
        registry = HookRegistry()

        def failing_transform(item):
            raise HookExecutionError("Intentional failure")

        # Non-critical hook - should not stop execution
        non_critical = MockHook("NonCritical", transform_before=failing_transform)
        registry.register_hook(non_critical, fail_on_error=False)

        item = MemoryItem(content="test")
        # Should not raise
        processed = registry.execute_before_store(item)
        assert processed.content == "test"

        # Critical hook - should stop execution
        registry2 = HookRegistry()
        critical = MockHook("Critical", transform_before=failing_transform)
        registry2.register_hook(critical, fail_on_error=True)

        with pytest.raises(HookExecutionError):
            registry2.execute_before_store(item)

    def test_circuit_breaker(self):
        """Test circuit breaker functionality"""
        registry = HookRegistry()

        fail_count = 0

        def sometimes_failing_transform(item):
            nonlocal fail_count
            fail_count += 1
            if fail_count < 6:  # Fail first 5 times
                raise Exception("Temporary failure")
            return item

        hook = MockHook("FlakyHook", transform_before=sometimes_failing_transform)
        registry.register_hook(hook, max_retries=1)  # Quick failure

        item = MemoryItem(content="test")

        # Execute multiple times to trigger circuit breaker
        for i in range(6):
            try:
                registry.execute_before_store(item)
            except:
                pass

        # Circuit should be broken now
        metrics = registry.get_registry_metrics()
        assert metrics["disabled_by_circuit_breaker"] > 0

        # Reset circuit breaker
        registry.reset_circuit_breaker("FlakyHook")
        metrics = registry.get_registry_metrics()
        assert metrics["disabled_by_circuit_breaker"] == 0

    def test_hook_tags_filtering(self):
        """Test filtering hooks by tags"""
        registry = HookRegistry()

        hook1 = MockHook("Hook1")
        hook2 = MockHook("Hook2")
        hook3 = MockHook("Hook3")

        registry.register_hook(hook1, tags={"security", "validation"})
        registry.register_hook(hook2, tags={"compression", "optimization"})
        registry.register_hook(hook3, tags={"security", "audit"})

        item = MemoryItem(content="test")

        # Execute only security hooks
        registry.execute_before_store(item, tags={"security"})

        assert hook1.before_count == 1
        assert hook2.before_count == 0  # Not tagged with security
        assert hook3.before_count == 1

    def test_registry_metrics(self):
        """Test registry metrics collection"""
        registry = HookRegistry()

        hook1 = MockHook("Hook1")
        hook2 = MockHook("Hook2")

        registry.register_hook(hook1, priority=HookPriority.HIGH)
        registry.register_hook(hook2, priority=HookPriority.NORMAL)

        # Execute some operations
        item = MemoryItem(content="test")
        for i in range(5):
            registry.execute_before_store(item)
            registry.execute_after_recall(item)

        metrics = registry.get_registry_metrics()
        assert metrics["total_hooks"] == 2
        assert metrics["enabled_hooks"] == 2
        assert metrics["execution_metrics"]["total_executions"] == 10
        assert metrics["execution_metrics"]["successful_executions"] == 10


@pytest.mark.integration
class TestHookIntegration:
    """Integration tests for hook system"""

    def test_complex_hook_chain(self):
        """Test complex chain of hooks working together"""
        registry = HookRegistry()

        # Hook 1: Add timestamp
        def add_timestamp(item):
            item.metadata["processed_at"] = datetime.now().isoformat()
            return item

        # Hook 2: Validate content
        def validate_content(item):
            if not item.content:
                raise HookExecutionError("Empty content not allowed")
            return item

        # Hook 3: Add symbolic state
        def add_symbolic_state(item):
            item.entropy = 0.3
            item.coherence = 0.8
            item.add_glyph("Λ")
            return item

        # Hook 4: Compress if needed
        def compress_if_large(item):
            if len(str(item.content)) > 100:
                item.is_compressed = True
                item.compression_ratio = 2.0
                item.fold_signature = f"fold_{item.memory_id[:8]}"
            return item

        registry.register_hook(
            MockHook("Validator", transform_before=validate_content),
            priority=HookPriority.CRITICAL,
            fail_on_error=True,
        )
        registry.register_hook(
            MockHook("Timestamper", transform_before=add_timestamp),
            priority=HookPriority.HIGH,
        )
        registry.register_hook(
            MockHook("SymbolicEnricher", transform_before=add_symbolic_state),
            priority=HookPriority.NORMAL,
        )
        registry.register_hook(
            MockHook("Compressor", transform_before=compress_if_large),
            priority=HookPriority.LOW,
        )

        # Test with valid content
        item = MemoryItem(content="A" * 150)  # Large content
        processed = registry.execute_before_store(item)

        assert "processed_at" in processed.metadata
        assert processed.entropy == 0.3
        assert "Λ" in processed.glyphs
        assert processed.is_compressed
        assert processed.compression_ratio == 2.0

        # Test with invalid content
        invalid_item = MemoryItem(content="")
        with pytest.raises(HookExecutionError, match="Empty content"):
            registry.execute_before_store(invalid_item)
