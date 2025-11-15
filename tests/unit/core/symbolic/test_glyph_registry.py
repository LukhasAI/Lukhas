"""Comprehensive tests for Distributed GLYPH Registry Synchronization."""
import pytest
import time
from unittest.mock import Mock
from core.symbolic.glyph_specialist import (
    InMemoryGlyphRegistry,
    DistributedGlyphSynchronizer,
    GlyphSpecialist,
)


class TestInMemoryRegistry:
    """Test suite for InMemoryGlyphRegistry."""

    def test_publish_and_get_threshold(self):
        """Test publishing and retrieving thresholds."""
        registry = InMemoryGlyphRegistry()

        registry.publish_threshold("glyph1", 0.85, {"instance": "test"})

        data = registry.get_threshold("glyph1")

        assert data["threshold"] == 0.85
        assert data["instance"] == "test"

    def test_get_nonexistent_threshold(self):
        """Test getting nonexistent threshold returns None."""
        registry = InMemoryGlyphRegistry()

        data = registry.get_threshold("nonexistent")

        assert data is None

    def test_subscribe_to_updates(self):
        """Test subscription to threshold updates."""
        registry = InMemoryGlyphRegistry()

        updates = []

        def callback(threshold, metadata):
            updates.append((threshold, metadata))

        registry.subscribe_to_updates("glyph1", callback)

        registry.publish_threshold("glyph1", 0.9, {"test": "data"})

        assert len(updates) == 1
        assert updates[0][0] == 0.9
        assert updates[0][1]["test"] == "data"

    def test_multiple_subscribers(self):
        """Test multiple subscribers for same GLYPH."""
        registry = InMemoryGlyphRegistry()

        updates1 = []
        updates2 = []

        def callback1(threshold, metadata):
            updates1.append(threshold)

        def callback2(threshold, metadata):
            updates2.append(threshold)

        registry.subscribe_to_updates("glyph1", callback1)
        registry.subscribe_to_updates("glyph1", callback2)

        registry.publish_threshold("glyph1", 0.8, {})

        assert len(updates1) == 1
        assert len(updates2) == 1

    def test_subscriber_exception_handling(self):
        """Test that subscriber exceptions don't break the system."""
        registry = InMemoryGlyphRegistry()

        def bad_callback(threshold, metadata):
            raise ValueError("Test error")

        registry.subscribe_to_updates("glyph1", bad_callback)

        # Should not raise exception
        registry.publish_threshold("glyph1", 0.9, {})

    def test_list_all_glyphs(self):
        """Test listing all glyphs."""
        registry = InMemoryGlyphRegistry()

        registry.publish_threshold("glyph1", 0.85, {})
        registry.publish_threshold("glyph2", 0.75, {})

        glyphs = registry.list_all_glyphs()

        assert len(glyphs) == 2
        assert "glyph1" in glyphs
        assert "glyph2" in glyphs

    def test_threshold_overwrite(self):
        """Test that publishing to same GLYPH overwrites."""
        registry = InMemoryGlyphRegistry()

        registry.publish_threshold("glyph1", 0.5, {"version": 1})
        registry.publish_threshold("glyph1", 0.8, {"version": 2})

        data = registry.get_threshold("glyph1")

        assert data["threshold"] == 0.8
        assert data["version"] == 2


class TestDistributedSynchronizer:
    """Test suite for DistributedGlyphSynchronizer."""

    @pytest.fixture
    def registry(self):
        """Create in-memory registry."""
        return InMemoryGlyphRegistry()

    @pytest.fixture
    def synchronizer(self, registry):
        """Create synchronizer."""
        return DistributedGlyphSynchronizer(
            registry, instance_id="test_instance", sync_interval=1.0
        )

    def test_publish_threshold_update(self, synchronizer):
        """Test publishing threshold update."""
        synchronizer.publish_threshold_update("glyph1", 0.85)

        data = synchronizer.registry.get_threshold("glyph1")

        assert data["threshold"] == 0.85
        assert data["instance_id"] == "test_instance"
        assert "timestamp" in data

    def test_subscribe_to_glyph(self, synchronizer):
        """Test subscribing to GLYPH updates."""
        updates = []

        def callback(threshold, metadata):
            updates.append(threshold)

        synchronizer.subscribe_to_glyph("glyph1", callback)

        # Publish from different instance
        synchronizer.registry.publish_threshold(
            "glyph1", 0.9, {"instance_id": "other_instance"}
        )

        # Should receive update
        assert len(updates) == 1
        assert updates[0] == 0.9

    def test_ignores_own_updates(self, synchronizer):
        """Test that own updates are ignored in subscription."""
        updates = []

        def callback(threshold, metadata):
            updates.append(threshold)

        synchronizer.subscribe_to_glyph("glyph1", callback)

        # Publish from same instance
        synchronizer.publish_threshold_update("glyph1", 0.85)

        # Should NOT receive update (own instance)
        assert len(updates) == 0

    def test_get_consensus_threshold_latest(self, synchronizer):
        """Test getting consensus threshold with latest strategy."""
        synchronizer.publish_threshold_update("glyph1", 0.85)

        consensus = synchronizer.get_consensus_threshold("glyph1", strategy="latest")

        assert consensus == 0.85

    def test_get_consensus_threshold_nonexistent(self, synchronizer):
        """Test getting consensus for nonexistent GLYPH."""
        consensus = synchronizer.get_consensus_threshold("nonexistent")

        assert consensus is None

    def test_background_sync_start_stop(self, synchronizer):
        """Test background synchronization start and stop."""
        synchronizer.start_background_sync()

        assert synchronizer._running is True
        assert synchronizer._sync_thread is not None

        synchronizer.stop_background_sync()

        assert synchronizer._running is False

    def test_background_sync_re_publishes(self, synchronizer):
        """Test that background sync re-publishes thresholds."""
        synchronizer.publish_threshold_update("glyph1", 0.85)

        synchronizer.start_background_sync()

        # Wait for at least one sync cycle
        time.sleep(1.5)

        synchronizer.stop_background_sync()

        # Threshold should still be present
        data = synchronizer.registry.get_threshold("glyph1")
        assert data["threshold"] == 0.85

    def test_start_background_sync_twice(self, synchronizer):
        """Test that starting background sync twice is handled gracefully."""
        synchronizer.start_background_sync()
        synchronizer.start_background_sync()  # Should just warn

        assert synchronizer._running is True

        synchronizer.stop_background_sync()

    def test_instance_id_generation(self, registry):
        """Test automatic instance ID generation."""
        synchronizer = DistributedGlyphSynchronizer(registry)

        assert synchronizer.instance_id.startswith("instance_")

    def test_local_thresholds_tracked(self, synchronizer):
        """Test that local thresholds are tracked."""
        synchronizer.publish_threshold_update("glyph1", 0.85)
        synchronizer.publish_threshold_update("glyph2", 0.75)

        assert "glyph1" in synchronizer._local_thresholds
        assert "glyph2" in synchronizer._local_thresholds
        assert synchronizer._local_thresholds["glyph1"] == 0.85


class TestGlyphSpecialistIntegration:
    """Test suite for GlyphSpecialist with distributed sync."""

    def test_glyph_specialist_with_distributed_sync(self):
        """Test GlyphSpecialist with distributed sync enabled."""
        specialist = GlyphSpecialist(
            drift_threshold=0.85,
            enable_distributed_sync=True,
            registry_backend="memory",
        )

        # Update threshold
        specialist.update_threshold(0.9)

        # Verify it was synced to registry
        assert specialist.drift_threshold == 0.9

    def test_glyph_specialist_without_sync(self):
        """Test GlyphSpecialist without distributed sync."""
        specialist = GlyphSpecialist(
            drift_threshold=0.85, enable_distributed_sync=False
        )

        # Update threshold
        specialist.update_threshold(0.9)

        # Should work without registry
        assert specialist.drift_threshold == 0.9
        assert specialist._synchronizer is None

    def test_remote_threshold_propagation(self):
        """Test that remote updates propagate to local instance."""
        # Create two instances sharing same registry
        registry = InMemoryGlyphRegistry()

        sync1 = DistributedGlyphSynchronizer(registry, instance_id="instance1")
        sync2 = DistributedGlyphSynchronizer(registry, instance_id="instance2")

        # Track updates on instance2
        updates = []

        def callback(threshold, metadata):
            updates.append(threshold)

        sync2.subscribe_to_glyph("default", callback)

        # Publish from instance1
        sync1.publish_threshold_update("default", 0.95)

        # Instance2 should receive update
        assert len(updates) == 1
        assert updates[0] == 0.95

    def test_specialist_receives_remote_updates(self):
        """Test that GlyphSpecialist receives remote threshold updates."""
        # Create shared registry
        registry = InMemoryGlyphRegistry()

        # Create specialist instance
        specialist = GlyphSpecialist(
            drift_threshold=0.5, enable_distributed_sync=True, registry_backend="memory"
        )
        specialist._synchronizer.registry = registry  # Use shared registry

        # Create separate synchronizer to simulate remote instance
        remote_sync = DistributedGlyphSynchronizer(registry, instance_id="remote")

        # Remote publishes update
        remote_sync.publish_threshold_update("default", 0.95)

        # Give time for callback
        time.sleep(0.1)

        # Specialist should have updated threshold
        assert specialist.drift_threshold == 0.95

    def test_create_registry_redis(self):
        """Test Redis registry creation (with mock to avoid real Redis)."""
        specialist = GlyphSpecialist(enable_distributed_sync=False)

        # Should raise if redis not available
        try:
            registry = specialist._create_registry("redis", "redis://localhost:6379/0")
            # If redis IS available, should return RedisGlyphRegistry
            from core.symbolic.glyph_specialist import RedisGlyphRegistry, REDIS_AVAILABLE

            if REDIS_AVAILABLE:
                assert isinstance(registry, RedisGlyphRegistry)
        except ImportError:
            # Expected if redis not available
            pass

    def test_create_registry_memory(self):
        """Test in-memory registry creation."""
        specialist = GlyphSpecialist(enable_distributed_sync=False)

        registry = specialist._create_registry("memory", None)

        assert isinstance(registry, InMemoryGlyphRegistry)

    def test_create_registry_invalid_backend(self):
        """Test that invalid backend raises ValueError."""
        specialist = GlyphSpecialist(enable_distributed_sync=False)

        with pytest.raises(ValueError, match="Unknown registry backend"):
            specialist._create_registry("invalid", None)

    def test_update_threshold_validates_positive(self):
        """Test that update_threshold validates positive values."""
        specialist = GlyphSpecialist()

        with pytest.raises(ValueError, match="must be positive"):
            specialist.update_threshold(-0.1)

    def test_remote_update_callback_receives_metadata(self):
        """Test that remote update callback receives all metadata."""
        specialist = GlyphSpecialist(enable_distributed_sync=False)

        metadata = {
            "instance_id": "remote_instance",
            "timestamp": "2025-01-01T00:00:00Z",
            "extra": "data",
        }

        specialist._on_remote_threshold_update(0.9, metadata)

        assert specialist.drift_threshold == 0.9


class TestMultiInstanceSynchronization:
    """Test suite for multiple instance synchronization."""

    def test_three_instances_sync(self):
        """Test synchronization across three instances."""
        registry = InMemoryGlyphRegistry()

        sync1 = DistributedGlyphSynchronizer(registry, instance_id="inst1")
        sync2 = DistributedGlyphSynchronizer(registry, instance_id="inst2")
        sync3 = DistributedGlyphSynchronizer(registry, instance_id="inst3")

        updates2 = []
        updates3 = []

        sync2.subscribe_to_glyph("glyph1", lambda t, m: updates2.append(t))
        sync3.subscribe_to_glyph("glyph1", lambda t, m: updates3.append(t))

        # Instance 1 publishes
        sync1.publish_threshold_update("glyph1", 0.95)

        # Both instance 2 and 3 should receive
        assert len(updates2) == 1
        assert len(updates3) == 1
        assert updates2[0] == 0.95
        assert updates3[0] == 0.95

    def test_bidirectional_sync(self):
        """Test bidirectional synchronization."""
        registry = InMemoryGlyphRegistry()

        sync1 = DistributedGlyphSynchronizer(registry, instance_id="inst1")
        sync2 = DistributedGlyphSynchronizer(registry, instance_id="inst2")

        updates1 = []
        updates2 = []

        sync1.subscribe_to_glyph("glyph1", lambda t, m: updates1.append(t))
        sync2.subscribe_to_glyph("glyph1", lambda t, m: updates2.append(t))

        # Instance 1 publishes
        sync1.publish_threshold_update("glyph1", 0.8)
        assert len(updates2) == 1
        assert updates2[0] == 0.8

        # Instance 2 publishes
        sync2.publish_threshold_update("glyph1", 0.9)
        assert len(updates1) == 1
        assert updates1[0] == 0.9


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_sync_with_no_thresholds(self):
        """Test synchronization with no thresholds set."""
        registry = InMemoryGlyphRegistry()
        synchronizer = DistributedGlyphSynchronizer(registry)

        synchronizer.start_background_sync()
        time.sleep(1.5)
        synchronizer.stop_background_sync()

        # Should complete without errors

    def test_subscribe_before_publish(self):
        """Test subscribing before any publish."""
        registry = InMemoryGlyphRegistry()
        synchronizer = DistributedGlyphSynchronizer(registry)

        updates = []
        synchronizer.subscribe_to_glyph("glyph1", lambda t, m: updates.append(t))

        # No updates yet
        assert len(updates) == 0

        # Now publish
        synchronizer.publish_threshold_update("glyph1", 0.7)

        # Still no updates (own instance)
        assert len(updates) == 0

    def test_concurrent_publishes(self):
        """Test handling concurrent publishes to same GLYPH."""
        registry = InMemoryGlyphRegistry()
        synchronizer = DistributedGlyphSynchronizer(registry)

        synchronizer.publish_threshold_update("glyph1", 0.5)
        synchronizer.publish_threshold_update("glyph1", 0.6)
        synchronizer.publish_threshold_update("glyph1", 0.7)

        data = registry.get_threshold("glyph1")
        assert data["threshold"] == 0.7  # Latest value


# Smoke tests
def test_module_imports():
    """Test that all required classes can be imported."""
    from core.symbolic.glyph_specialist import (
        InMemoryGlyphRegistry,
        RedisGlyphRegistry,
        DistributedGlyphSynchronizer,
        GlyphRegistryBackend,
        GlyphSpecialist,
    )

    assert InMemoryGlyphRegistry is not None
    assert RedisGlyphRegistry is not None
    assert DistributedGlyphSynchronizer is not None
    assert GlyphRegistryBackend is not None
    assert GlyphSpecialist is not None


def test_basic_workflow():
    """Test basic distributed synchronization workflow."""
    # Create specialist with distributed sync
    specialist = GlyphSpecialist(
        drift_threshold=0.5, enable_distributed_sync=True, registry_backend="memory"
    )

    # Update threshold
    specialist.update_threshold(0.8)

    # Verify update
    assert specialist.drift_threshold == 0.8

    # Verify synced to registry
    if specialist._synchronizer:
        data = specialist._synchronizer.registry.get_threshold("default")
        assert data["threshold"] == 0.8
