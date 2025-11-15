"""GLYPH specialist consensus evaluation utilities."""
from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

# Optional Redis dependency (graceful degradation)
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger("Lukhas.GLYPH.Specialist")


@dataclass(frozen=True)
class GlyphSignal:
    """Represents a symbolic consciousness layer measurement."""

    layer_id: str
    driftScore: float
    affect_delta: float
    glyph_markers: Sequence[str] = field(default_factory=list)
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class GlyphConsensusResult:
    """Result of GLYPH consensus evaluation."""

    consensus: bool
    driftScore: float
    affect_delta: float
    agreement_ratio: float
    dissenting_layers: list[str]
    glyph_signature: list[str]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GlyphRegistryBackend(Protocol):
    """Protocol for distributed GLYPH registry backends."""

    def publish_threshold(
        self, glyph_id: str, threshold: float, metadata: dict[str, Any]
    ) -> None:
        """Publish threshold update to registry."""
        ...

    def get_threshold(self, glyph_id: str) -> dict[str, Any] | None:
        """Get threshold from registry."""
        ...

    def subscribe_to_updates(
        self, glyph_id: str, callback: Callable[[float, dict[str, Any]], None]
    ) -> None:
        """Subscribe to threshold updates for a GLYPH."""
        ...

    def list_all_glyphs(self) -> list[str]:
        """List all registered GLYPHs."""
        ...


class InMemoryGlyphRegistry:
    """In-memory implementation of GLYPH registry (for testing/single-instance)."""

    def __init__(self):
        """Initialize in-memory registry."""
        self._thresholds: dict[str, dict[str, Any]] = {}
        self._subscribers: dict[str, list[Callable[[float, dict[str, Any]], None]]] = {}

    def publish_threshold(
        self, glyph_id: str, threshold: float, metadata: dict[str, Any]
    ) -> None:
        """Publish threshold to in-memory registry."""
        self._thresholds[glyph_id] = {
            "threshold": threshold,
            **metadata,
        }

        # Notify subscribers
        if glyph_id in self._subscribers:
            for callback in self._subscribers[glyph_id]:
                try:
                    callback(threshold, metadata)
                except Exception as e:
                    logger.error(f"Subscriber callback failed: {e}")

    def get_threshold(self, glyph_id: str) -> dict[str, Any] | None:
        """Get threshold from in-memory registry."""
        return self._thresholds.get(glyph_id)

    def subscribe_to_updates(
        self, glyph_id: str, callback: Callable[[float, dict[str, Any]], None]
    ) -> None:
        """Subscribe to threshold updates."""
        if glyph_id not in self._subscribers:
            self._subscribers[glyph_id] = []
        self._subscribers[glyph_id].append(callback)

    def list_all_glyphs(self) -> list[str]:
        """List all registered GLYPHs."""
        return list(self._thresholds.keys())


class RedisGlyphRegistry:
    """Redis-based distributed GLYPH registry implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis registry.

        Args:
            redis_url: Redis connection URL
        """
        if not REDIS_AVAILABLE:
            raise ImportError("Redis features require redis: pip install redis")

        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._pubsub = self._redis.pubsub()
        self._subscribers: dict[str, list[Callable[[float, dict[str, Any]], None]]] = {}
        self._pubsub_thread = None

    def publish_threshold(
        self, glyph_id: str, threshold: float, metadata: dict[str, Any]
    ) -> None:
        """Publish threshold to Redis registry."""
        import json

        data = {"threshold": threshold, **metadata}

        # Store in Redis hash
        self._redis.hset(f"glyph:{glyph_id}", "data", json.dumps(data))

        # Publish to pubsub channel
        self._redis.publish(f"glyph:updates:{glyph_id}", json.dumps(data))

    def get_threshold(self, glyph_id: str) -> dict[str, Any] | None:
        """Get threshold from Redis registry."""
        import json

        data = self._redis.hget(f"glyph:{glyph_id}", "data")
        if data:
            return json.loads(data)
        return None

    def subscribe_to_updates(
        self, glyph_id: str, callback: Callable[[float, dict[str, Any]], None]
    ) -> None:
        """Subscribe to threshold updates via Redis pubsub."""
        import json

        if glyph_id not in self._subscribers:
            self._subscribers[glyph_id] = []
        self._subscribers[glyph_id].append(callback)

        # Subscribe to pubsub channel
        channel = f"glyph:updates:{glyph_id}"
        self._pubsub.subscribe(channel)

        # Start pubsub listener thread if not already running
        if self._pubsub_thread is None:
            self._pubsub_thread = threading.Thread(
                target=self._pubsub_listener, daemon=True
            )
            self._pubsub_thread.start()

    def _pubsub_listener(self):
        """Listen for pubsub messages and invoke callbacks."""
        import json

        for message in self._pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                # Extract glyph_id from channel name
                glyph_id = channel.replace("glyph:updates:", "")

                try:
                    data = json.loads(message["data"])
                    threshold = data["threshold"]

                    # Invoke subscribers
                    if glyph_id in self._subscribers:
                        for callback in self._subscribers[glyph_id]:
                            try:
                                callback(threshold, data)
                            except Exception as e:
                                logger.error(f"Subscriber callback failed: {e}")
                except Exception as e:
                    logger.error(f"Error processing pubsub message: {e}")

    def list_all_glyphs(self) -> list[str]:
        """List all registered GLYPHs in Redis."""
        keys = self._redis.keys("glyph:*")
        return [k.replace("glyph:", "") for k in keys if not k.startswith("glyph:updates:")]


class DistributedGlyphSynchronizer:
    """
    Synchronize GLYPH thresholds across distributed instances.

    Manages pub/sub updates and ensures threshold consistency across
    multiple LUKHAS instances.
    """

    def __init__(
        self,
        registry: GlyphRegistryBackend,
        instance_id: str | None = None,
        sync_interval: float = 5.0,
    ):
        """
        Initialize synchronizer.

        Args:
            registry: Registry backend (Redis, in-memory, etc.)
            instance_id: Unique identifier for this instance
            sync_interval: Seconds between sync checks
        """
        self.registry = registry
        self.instance_id = instance_id or f"instance_{int(time.time())}"
        self.sync_interval = sync_interval

        self._local_thresholds: dict[str, float] = {}
        self._sync_thread = None
        self._running = False
        self._logger = logging.getLogger(__name__)

    def publish_threshold_update(self, glyph_id: str, threshold: float) -> None:
        """
        Publish threshold update to distributed registry.

        Args:
            glyph_id: GLYPH identifier
            threshold: New threshold value
        """
        self._local_thresholds[glyph_id] = threshold

        metadata = {
            "instance_id": self.instance_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.registry.publish_threshold(glyph_id, threshold, metadata)

        self._logger.info(
            f"Published threshold for {glyph_id}",
            extra={"threshold": threshold, "instance": self.instance_id},
        )

    def subscribe_to_glyph(
        self, glyph_id: str, callback: Callable[[float, dict[str, Any]], None]
    ) -> None:
        """
        Subscribe to updates for a specific GLYPH.

        Args:
            glyph_id: GLYPH to subscribe to
            callback: Function to call when threshold updates
        """

        def wrapped_callback(threshold: float, metadata: dict[str, Any]):
            # Don't process our own updates
            if metadata.get("instance_id") == self.instance_id:
                return

            self._logger.info(
                f"Received threshold update for {glyph_id}",
                extra={
                    "threshold": threshold,
                    "from_instance": metadata.get("instance_id"),
                },
            )

            callback(threshold, metadata)

        self.registry.subscribe_to_updates(glyph_id, wrapped_callback)

    def get_consensus_threshold(
        self, glyph_id: str, strategy: str = "latest"
    ) -> float | None:
        """
        Get consensus threshold from registry.

        Args:
            glyph_id: GLYPH identifier
            strategy: Consensus strategy ("latest", "average", "max", "min")

        Returns:
            Consensus threshold value or None
        """
        data = self.registry.get_threshold(glyph_id)

        if not data:
            return None

        if strategy == "latest":
            return data.get("threshold")

        # For other strategies, would need to query multiple instances
        # This is simplified for now
        return data.get("threshold")

    def start_background_sync(self) -> None:
        """Start background synchronization thread."""
        if self._running:
            self._logger.warning("Background sync already running")
            return

        self._running = True

        def sync_loop():
            while self._running:
                try:
                    self._perform_sync()
                except Exception as e:
                    self._logger.error(f"Error in sync loop: {e}")

                time.sleep(self.sync_interval)

        self._sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self._sync_thread.start()

        self._logger.info("Started background synchronization")

    def _perform_sync(self) -> None:
        """Perform periodic synchronization check."""
        # Re-publish local thresholds to ensure freshness
        for glyph_id, threshold in self._local_thresholds.items():
            self.publish_threshold_update(glyph_id, threshold)

    def stop_background_sync(self) -> None:
        """Stop background synchronization."""
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=2.0)

        self._logger.info("Stopped background synchronization")


class GlyphSpecialist:
    """Perform GLYPH-weighted consensus over consciousness layer signals."""

    def __init__(
        self,
        drift_threshold: float = 0.3,
        enable_distributed_sync: bool = False,
        registry_backend: str = "memory",
        redis_url: str | None = None,
    ) -> None:
        """
        Initialize GLYPH specialist.

        Args:
            drift_threshold: Local drift threshold
            enable_distributed_sync: Enable distributed registry sync
            registry_backend: "redis" or "memory"
            redis_url: Redis connection URL (if using Redis)
        """
        self.drift_threshold = drift_threshold
        self._logger = logger

        # Distributed synchronization
        self._enable_distributed_sync = enable_distributed_sync
        if enable_distributed_sync:
            registry = self._create_registry(registry_backend, redis_url)
            self._synchronizer = DistributedGlyphSynchronizer(registry)

            # Subscribe to threshold updates
            glyph_id = "default"  # Could be made configurable
            self._synchronizer.subscribe_to_glyph(
                glyph_id, self._on_remote_threshold_update
            )

            self._synchronizer.start_background_sync()
        else:
            self._synchronizer = None

    def _create_registry(
        self, backend_type: str, redis_url: str | None
    ) -> GlyphRegistryBackend:
        """Create registry backend."""
        if backend_type == "redis":
            return RedisGlyphRegistry(redis_url or "redis://localhost:6379/0")
        elif backend_type == "memory":
            return InMemoryGlyphRegistry()
        else:
            raise ValueError(f"Unknown registry backend: {backend_type}")

    def evaluate(self, signals: Sequence[GlyphSignal]) -> GlyphConsensusResult:
        """Evaluate consensus across signals using GLYPH weighting."""
        if not signals:
            raise ValueError("signals must not be empty")

        weights = [self._compute_weight(signal) for signal in signals]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        drift_score = sum(s.driftScore * w for s, w in zip(signals, normalized_weights))
        affect_delta = sum(s.affect_delta * w for s, w in zip(signals, normalized_weights))

        dissenting_layers = [s.layer_id for s in signals if s.driftScore > self.drift_threshold]
        agreement_ratio = 1.0 - (len(dissenting_layers) / len(signals))
        glyph_signature = sorted({marker for s in signals for marker in s.glyph_markers})

        consensus = drift_score <= self.drift_threshold and not dissenting_layers

        self._logger.debug(
            "# ΛTAG: glyph_consensus -- evaluated consensus",
            extra={
                "driftScore": drift_score,
                "affect_delta": affect_delta,
                "agreement_ratio": agreement_ratio,
                "dissenting_layers": dissenting_layers,
                "glyph_signature": glyph_signature,
            },
        )

        return GlyphConsensusResult(
            consensus=consensus,
            driftScore=drift_score,
            affect_delta=affect_delta,
            agreement_ratio=agreement_ratio,
            dissenting_layers=dissenting_layers,
            glyph_signature=glyph_signature,
        )

    def _compute_weight(self, signal: GlyphSignal) -> float:
        """Compute GLYPH weighting for a signal."""
        base_weight = 1.0 + abs(signal.affect_delta)
        symbolic_weight = max(1.0, len(signal.glyph_markers) * 0.25)
        # ΛTAG: glyph_weighting
        return base_weight * symbolic_weight

    def update_threshold(self, new_threshold: float) -> None:
        """
        Update drift threshold used for consensus.

        Syncs to distributed registry if enabled.
        """
        if new_threshold <= 0:
            raise ValueError("new_threshold must be positive")

        self.drift_threshold = new_threshold
        self._logger.info(
            "# ΛTAG: glyph_threshold_update -- updated drift threshold",
            extra={"drift_threshold": new_threshold},
        )

        # Sync to distributed registry
        if self._enable_distributed_sync and self._synchronizer:
            self._synchronizer.publish_threshold_update("default", new_threshold)

    def _on_remote_threshold_update(
        self, threshold: float, metadata: dict[str, Any]
    ) -> None:
        """
        Handle threshold update from remote instance.

        Args:
            threshold: Updated threshold value
            metadata: Update metadata (instance_id, timestamp, etc.)
        """
        self._logger.info(
            "Received remote threshold update",
            extra={
                "new_threshold": threshold,
                "from_instance": metadata.get("instance_id"),
                "timestamp": metadata.get("timestamp"),
            },
        )

        # Apply update (could add conflict resolution logic here)
        self.drift_threshold = threshold
