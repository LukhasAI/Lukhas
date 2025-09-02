#!/usr/bin/env python3

"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Glyph Sentinel

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Glyph Sentinel: Comprehensive decay and persistence tracking system for
symbolic integrity management, providing decay detection, retention policy
enforcement, integrity monitoring, and automated maintenance operations for
the GLYPH subsystem.

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: Glyph Sentinel initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 14

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

# Internal imports
from .glyph import Glyph, GlyphPriority, GlyphType

# Configure logger
logger = logging.getLogger(__name__)


class DecayState(Enum):
    """States of glyph decay progression."""

    FRESH = "fresh"  # Recently created, no decay
    STABLE = "stable"  # Mature but stable
    AGING = "aging"  # Showing signs of age
    DEGRADING = "degrading"  # Active degradation
    CRITICAL = "critical"  # Near expiration
    EXPIRED = "expired"  # Past expiration threshold


class PersistencePolicy(Enum):
    """Persistence policy types for glyphs."""

    EPHEMERAL = "ephemeral"  # Short-term storage
    STANDARD = "standard"  # Normal retention
    PERSISTENT = "persistent"  # Long-term storage
    PERMANENT = "permanent"  # Never expires
    CONDITIONAL = "conditional"  # Depends on usage/conditions


@dataclass
class DecayMetrics:
    """Metrics tracking glyph decay progression."""

    glyph_id: str
    decay_state: DecayState
    decay_rate: float  # Rate of decay (0.0-1.0 per day)
    integrity_score: float  # Current integrity (0.0-1.0)
    last_accessed: datetime
    access_frequency: float  # Accesses per day
    stability_trend: list[float]  # Recent stability measurements
    predicted_expiry: Optional[datetime]  # Predicted expiration date

    def update_trend(self, stability: float):
        """Update stability trend with new measurement."""
        self.stability_trend.append(stability)
        # Keep only last 10 measurements
        if len(self.stability_trend) > 10:
            self.stability_trend.pop(0)


@dataclass
class PersistenceProfile:
    """Profile defining persistence behavior for a glyph."""

    glyph_id: str
    policy: PersistencePolicy
    retention_period: Optional[timedelta]  # None for permanent
    importance_weight: float  # Importance multiplier
    usage_threshold: int  # Min accesses to maintain
    conditions: dict[str, Any]  # Custom persistence conditions
    auto_refresh: bool = False  # Auto-refresh on access
    backup_priority: int = 3  # Backup priority (1-5)


class GlyphSentinel:
    """
    Glyph decay and persistence tracking sentinel.

    Monitors glyph lifecycle, enforces retention policies, and maintains
    symbolic integrity through continuous background operations.
    """

    def __init__(
        self,
        monitoring_interval: float = 300.0,  # 5 minutes
        cleanup_interval: float = 3600.0,
    ):  # 1 hour
        """
        Initialize the Glyph Sentinel.

        Args:
            monitoring_interval: Seconds between monitoring cycles
            cleanup_interval: Seconds between cleanup operations
        """
        self.monitoring_interval = monitoring_interval
        self.cleanup_interval = cleanup_interval

        # Glyph tracking
        self.monitored_glyphs: dict[str, Glyph] = {}
        self.decay_metrics: dict[str, DecayMetrics] = {}
        self.persistence_profiles: dict[str, PersistenceProfile] = {}

        # Operational state
        self.is_monitoring = False
        self.last_cleanup = datetime.now()
        self.monitoring_thread: Optional[threading.Thread] = None

        # Event handlers
        self.decay_handlers: dict[DecayState, list[Callable]] = defaultdict(list)
        self.expiry_handlers: list[Callable] = []
        self.integrity_handlers: list[Callable] = []

        # Statistics
        self.monitoring_cycles = 0
        self.cleanup_operations = 0
        self.expired_glyphs = 0
        self.integrity_violations = 0

        logger.info("Glyph Sentinel initialized")

    def register_glyph(
        self,
        glyph: Glyph,
        persistence_policy: PersistencePolicy = PersistencePolicy.STANDARD,
        custom_conditions: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Register a glyph for monitoring and persistence management.

        Args:
            glyph: Glyph instance to monitor
            persistence_policy: Retention policy to apply
            custom_conditions: Custom persistence conditions

        Returns:
            True if registration successful
        """
        if glyph.id in self.monitored_glyphs:
            logger.warning(f"Glyph {glyph.id} already registered with sentinel")
            return False

        # Register glyph
        self.monitored_glyphs[glyph.id] = glyph

        # Initialize decay metrics
        self.decay_metrics[glyph.id] = DecayMetrics(
            glyph_id=glyph.id,
            decay_state=DecayState.FRESH,
            decay_rate=self._calculate_initial_decay_rate(glyph),
            integrity_score=1.0,
            last_accessed=datetime.now(),
            access_frequency=0.0,
            stability_trend=[glyph.stability_index],
            predicted_expiry=None,
        )

        # Create persistence profile
        self.persistence_profiles[glyph.id] = self._create_persistence_profile(
            glyph, persistence_policy, custom_conditions
        )

        logger.debug(f"Registered glyph {glyph.id} with policy {persistence_policy.value}")
        return True

    def unregister_glyph(self, glyph_id: str) -> bool:
        """
        Unregister a glyph from monitoring.

        Args:
            glyph_id: ID of glyph to unregister

        Returns:
            True if unregistration successful
        """
        if glyph_id not in self.monitored_glyphs:
            logger.warning(f"Glyph {glyph_id} not registered with sentinel")
            return False

        del self.monitored_glyphs[glyph_id]
        del self.decay_metrics[glyph_id]
        del self.persistence_profiles[glyph_id]

        logger.debug(f"Unregistered glyph {glyph_id}")
        return True

    def record_access(self, glyph_id: str) -> bool:
        """
        Record access to a glyph for persistence tracking.

        Args:
            glyph_id: ID of accessed glyph

        Returns:
            True if access recorded successfully
        """
        if glyph_id not in self.decay_metrics:
            logger.warning(f"Access recorded for unmonitored glyph {glyph_id}")
            return False

        metrics = self.decay_metrics[glyph_id]
        current_time = datetime.now()

        # Update access metrics
        time_since_last = (current_time - metrics.last_accessed).total_seconds()
        if time_since_last > 0:
            # Update access frequency (exponential moving average)
            daily_factor = 86400.0 / time_since_last  # Convert to per-day
            metrics.access_frequency = metrics.access_frequency * 0.7 + daily_factor * 0.3

        metrics.last_accessed = current_time

        # Check for auto-refresh
        profile = self.persistence_profiles[glyph_id]
        if profile.auto_refresh:
            self._refresh_glyph(glyph_id)

        logger.debug(f"Recorded access for glyph {glyph_id}")
        return True

    def start_monitoring(self) -> bool:
        """
        Start background monitoring operations.

        Returns:
            True if monitoring started successfully
        """
        if self.is_monitoring:
            logger.warning("Glyph Sentinel already monitoring")
            return False

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info("Glyph Sentinel monitoring started")
        return True

    def stop_monitoring(self) -> bool:
        """
        Stop background monitoring operations.

        Returns:
            True if monitoring stopped successfully
        """
        if not self.is_monitoring:
            logger.warning("Glyph Sentinel not monitoring")
            return False

        self.is_monitoring = False

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)

        logger.info("Glyph Sentinel monitoring stopped")
        return True

    def get_decay_status(self, glyph_id: str) -> Optional[dict[str, Any]]:
        """
        Get current decay status for a glyph.

        Args:
            glyph_id: ID of glyph to query

        Returns:
            Decay status dictionary or None if not found
        """
        if glyph_id not in self.decay_metrics:
            return None

        metrics = self.decay_metrics[glyph_id]
        profile = self.persistence_profiles[glyph_id]

        return {
            "glyph_id": glyph_id,
            "decay_state": metrics.decay_state.value,
            "integrity_score": metrics.integrity_score,
            "decay_rate": metrics.decay_rate,
            "access_frequency": metrics.access_frequency,
            "last_accessed": metrics.last_accessed.isoformat(),
            "predicted_expiry": (metrics.predicted_expiry.isoformat() if metrics.predicted_expiry else None),
            "persistence_policy": profile.policy.value,
            "importance_weight": profile.importance_weight,
            "stability_trend": metrics.stability_trend,
        }

    def get_endangered_glyphs(self) -> list[str]:
        """
        Get list of glyphs at risk of expiration.

        Returns:
            List of glyph IDs in critical or degrading state
        """
        endangered = []

        for glyph_id, metrics in self.decay_metrics.items():
            if metrics.decay_state in [
                DecayState.CRITICAL,
                DecayState.DEGRADING,
            ]:
                endangered.append(glyph_id)

        return endangered

    def force_refresh(self, glyph_id: str) -> bool:
        """
        Force refresh a glyph to reset decay state.

        Args:
            glyph_id: ID of glyph to refresh

        Returns:
            True if refresh successful
        """
        if glyph_id not in self.monitored_glyphs:
            logger.error(f"Cannot refresh unmonitored glyph {glyph_id}")
            return False

        return self._refresh_glyph(glyph_id)

    def add_decay_handler(self, decay_state: DecayState, handler: Callable[[str], None]):
        """
        Add event handler for decay state transitions.

        Args:
            decay_state: Decay state to handle
            handler: Callback function (receives glyph_id)
        """
        self.decay_handlers[decay_state].append(handler)

    def add_expiry_handler(self, handler: Callable[[str], None]):
        """
        Add event handler for glyph expiration.

        Args:
            handler: Callback function (receives glyph_id)
        """
        self.expiry_handlers.append(handler)

    def add_integrity_handler(self, handler: Callable[[str, str], None]):
        """
        Add event handler for integrity violations.

        Args:
            handler: Callback function (receives glyph_id, violation_type)
        """
        self.integrity_handlers.append(handler)

    def _create_persistence_profile(
        self,
        glyph: Glyph,
        policy: PersistencePolicy,
        conditions: Optional[dict[str, Any]],
    ) -> PersistenceProfile:
        """Create persistence profile for a glyph."""
        # Calculate importance weight based on glyph properties
        importance = self._calculate_importance_weight(glyph)

        # Set retention period based on policy
        retention_periods = {
            PersistencePolicy.EPHEMERAL: timedelta(hours=1),
            PersistencePolicy.STANDARD: timedelta(days=30),
            PersistencePolicy.PERSISTENT: timedelta(days=365),
            PersistencePolicy.PERMANENT: None,
            PersistencePolicy.CONDITIONAL: timedelta(days=7),  # Default for conditional
        }

        # Usage thresholds
        usage_thresholds = {
            PersistencePolicy.EPHEMERAL: 1,
            PersistencePolicy.STANDARD: 5,
            PersistencePolicy.PERSISTENT: 2,
            PersistencePolicy.PERMANENT: 0,
            PersistencePolicy.CONDITIONAL: 10,
        }

        return PersistenceProfile(
            glyph_id=glyph.id,
            policy=policy,
            retention_period=retention_periods[policy],
            importance_weight=importance,
            usage_threshold=usage_thresholds[policy],
            conditions=conditions or {},
            auto_refresh=(policy in [PersistencePolicy.PERSISTENT, PersistencePolicy.PERMANENT]),
            backup_priority=min(5, max(1, int(importance * 5))),
        )

    def _calculate_importance_weight(self, glyph: Glyph) -> float:
        """Calculate importance weight for a glyph."""
        weight = 0.5  # Base weight

        # Priority bonus
        priority_weights = {
            GlyphPriority.CRITICAL: 1.0,
            GlyphPriority.HIGH: 0.8,
            GlyphPriority.MEDIUM: 0.5,
            GlyphPriority.LOW: 0.3,
            GlyphPriority.EPHEMERAL: 0.1,
        }
        weight += priority_weights.get(glyph.priority, 0.5) * 0.3

        # Type importance
        type_importance = {
            GlyphType.ETHICAL: 0.9,
            GlyphType.MEMORY: 0.8,
            GlyphType.CAUSAL: 0.7,
            GlyphType.DRIFT: 0.6,
            GlyphType.COLLAPSE: 0.8,
            GlyphType.EMOTION: 0.4,
            GlyphType.DREAM: 0.3,
            GlyphType.ACTION: 0.5,
            GlyphType.TEMPORAL: 0.6,
        }
        weight += type_importance.get(glyph.glyph_type, 0.5) * 0.2

        # Memory associations boost
        if glyph.memory_keys:
            weight += min(0.3, len(glyph.memory_keys) * 0.05)

        # Stability contribution
        weight += glyph.stability_index * 0.1

        return min(1.0, weight)

    def _calculate_initial_decay_rate(self, glyph: Glyph) -> float:
        """Calculate initial decay rate for a glyph."""
        base_rate = 0.01  # 1% per day baseline

        # Type-based decay rates
        type_rates = {
            GlyphType.EPHEMERAL: 0.1,  # 10% per day
            GlyphType.DREAM: 0.05,  # 5% per day
            GlyphType.EMOTION: 0.03,  # 3% per day
            GlyphType.ACTION: 0.02,  # 2% per day
            GlyphType.MEMORY: 0.005,  # 0.5% per day
            GlyphType.CAUSAL: 0.003,  # 0.3% per day
            GlyphType.ETHICAL: 0.001,  # 0.1% per day
        }

        rate = type_rates.get(glyph.glyph_type, base_rate)

        # Stability modifier
        stability_modifier = (1.0 - glyph.stability_index) * 0.02
        rate += stability_modifier

        # Priority modifier
        priority_modifiers = {
            GlyphPriority.CRITICAL: -0.005,
            GlyphPriority.HIGH: -0.003,
            GlyphPriority.MEDIUM: 0.0,
            GlyphPriority.LOW: 0.002,
            GlyphPriority.EPHEMERAL: 0.05,
        }
        rate += priority_modifiers.get(glyph.priority, 0.0)

        return max(0.001, min(0.2, rate))  # Clamp between 0.1% and 20% per day

    def _monitoring_loop(self):
        """Main monitoring loop running in background thread."""
        logger.info("Glyph Sentinel monitoring loop started")

        while self.is_monitoring:
            try:
                start_time = time.time()

                # Perform monitoring cycle
                self._perform_monitoring_cycle()

                # Check if cleanup is needed
                if (datetime.now() - self.last_cleanup).total_seconds() >= self.cleanup_interval:
                    self._perform_cleanup_cycle()
                    self.last_cleanup = datetime.now()

                # Calculate sleep time
                cycle_time = time.time() - start_time
                sleep_time = max(0, self.monitoring_interval - cycle_time)

                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Brief pause before retry

        logger.info("Glyph Sentinel monitoring loop stopped")

    def _perform_monitoring_cycle(self):
        """Perform one monitoring cycle."""
        self.monitoring_cycles += 1
        current_time = datetime.now()

        for glyph_id, glyph in self.monitored_glyphs.items():
            try:
                # Update decay metrics
                self._update_decay_metrics(glyph_id, glyph, current_time)

                # Check integrity
                self._check_integrity(glyph_id, glyph)

                # Check for state transitions
                self._check_decay_transitions(glyph_id)

                # Check expiration
                self._check_expiration(glyph_id, current_time)

            except Exception as e:
                logger.error(f"Error monitoring glyph {glyph_id}: {e}")

    def _update_decay_metrics(self, glyph_id: str, glyph: Glyph, current_time: datetime):
        """Update decay metrics for a glyph."""
        metrics = self.decay_metrics[glyph_id]

        # Calculate time since last access
        time_since_access = (current_time - metrics.last_accessed).total_seconds()
        days_since_access = time_since_access / 86400.0

        # Apply decay
        decay_amount = metrics.decay_rate * days_since_access
        metrics.integrity_score = max(0.0, metrics.integrity_score - decay_amount)

        # Update stability trend
        metrics.update_trend(glyph.stability_index)

        # Calculate predicted expiry
        if metrics.integrity_score > 0 and metrics.decay_rate > 0:
            days_to_expiry = metrics.integrity_score / metrics.decay_rate
            metrics.predicted_expiry = current_time + timedelta(days=days_to_expiry)

        # Update decay state based on integrity
        old_state = metrics.decay_state
        if metrics.integrity_score >= 0.9:
            metrics.decay_state = DecayState.FRESH
        elif metrics.integrity_score >= 0.7:
            metrics.decay_state = DecayState.STABLE
        elif metrics.integrity_score >= 0.5:
            metrics.decay_state = DecayState.AGING
        elif metrics.integrity_score >= 0.2:
            metrics.decay_state = DecayState.DEGRADING
        elif metrics.integrity_score > 0:
            metrics.decay_state = DecayState.CRITICAL
        else:
            metrics.decay_state = DecayState.EXPIRED

        # Fire decay state change handlers
        if old_state != metrics.decay_state:
            self._fire_decay_handlers(glyph_id, metrics.decay_state)

    def _check_integrity(self, glyph_id: str, glyph: Glyph):
        """Check symbolic integrity of a glyph."""
        try:
            # Recalculate symbolic hash
            expected_hash = glyph._generate_symbolic_hash()

            if expected_hash != glyph.symbolic_hash:
                self.integrity_violations += 1
                self._fire_integrity_handlers(glyph_id, "hash_mismatch")

                # Auto-repair if possible
                glyph.symbolic_hash = expected_hash
                logger.warning(f"Auto-repaired hash mismatch for glyph {glyph_id}")

        except Exception as e:
            self.integrity_violations += 1
            self._fire_integrity_handlers(glyph_id, f"integrity_check_failed: {e}")

    def _check_decay_transitions(self, glyph_id: str):
        """Check for decay state transitions requiring action."""
        metrics = self.decay_metrics[glyph_id]
        profile = self.persistence_profiles[glyph_id]

        # Check if glyph needs refreshing based on usage
        if metrics.access_frequency >= profile.usage_threshold and metrics.decay_state in [
            DecayState.DEGRADING,
            DecayState.CRITICAL,
        ]:
            self._refresh_glyph(glyph_id)

    def _check_expiration(self, glyph_id: str, current_time: datetime):
        """Check if a glyph has expired."""
        metrics = self.decay_metrics[glyph_id]
        profile = self.persistence_profiles[glyph_id]

        # Check integrity-based expiration
        if metrics.decay_state == DecayState.EXPIRED:
            self._handle_expiration(glyph_id)
            return

        # Check policy-based expiration
        if profile.retention_period:
            glyph = self.monitored_glyphs[glyph_id]
            age = current_time - glyph.temporal_stamp.created_at

            if age > profile.retention_period:
                # Check if usage warrants extension
                if metrics.access_frequency < profile.usage_threshold:
                    self._handle_expiration(glyph_id)

    def _perform_cleanup_cycle(self):
        """Perform cleanup operations."""
        self.cleanup_operations += 1

        # Collect expired glyphs
        expired_glyphs = []
        for glyph_id, metrics in self.decay_metrics.items():
            if metrics.decay_state == DecayState.EXPIRED:
                expired_glyphs.append(glyph_id)

        # Process expired glyphs
        for glyph_id in expired_glyphs:
            profile = self.persistence_profiles[glyph_id]

            # Final check for conditional persistence
            if profile.policy == PersistencePolicy.CONDITIONAL:
                if self._evaluate_conditional_persistence(glyph_id):
                    self._refresh_glyph(glyph_id)
                    continue

            # Remove expired glyph
            self._remove_expired_glyph(glyph_id)

        logger.debug(f"Cleanup cycle completed, removed {len(expired_glyphs)} expired glyphs")

    def _refresh_glyph(self, glyph_id: str) -> bool:
        """Refresh a glyph to reset decay state."""
        if glyph_id not in self.decay_metrics:
            return False

        metrics = self.decay_metrics[glyph_id]
        glyph = self.monitored_glyphs[glyph_id]

        # Reset decay metrics
        metrics.integrity_score = 1.0
        metrics.decay_state = DecayState.FRESH
        metrics.last_accessed = datetime.now()

        # Reset glyph temporal properties
        glyph.temporal_stamp.last_accessed = datetime.now()
        glyph.temporal_stamp.update_access()

        logger.debug(f"Refreshed glyph {glyph_id}")
        return True

    def _handle_expiration(self, glyph_id: str):
        """Handle glyph expiration."""
        self.expired_glyphs += 1

        # Fire expiry handlers
        for handler in self.expiry_handlers:
            try:
                handler(glyph_id)
            except Exception as e:
                logger.error(f"Error in expiry handler: {e}")

        logger.info(f"Glyph {glyph_id} has expired")

    def _remove_expired_glyph(self, glyph_id: str):
        """Remove an expired glyph from monitoring."""
        if glyph_id in self.monitored_glyphs:
            del self.monitored_glyphs[glyph_id]
            del self.decay_metrics[glyph_id]
            del self.persistence_profiles[glyph_id]
            logger.debug(f"Removed expired glyph {glyph_id}")

    def _evaluate_conditional_persistence(self, glyph_id: str) -> bool:
        """Evaluate whether a conditional glyph should persist."""
        profile = self.persistence_profiles[glyph_id]
        metrics = self.decay_metrics[glyph_id]
        glyph = self.monitored_glyphs[glyph_id]

        # Check custom conditions
        conditions = profile.conditions

        # Memory association condition
        if conditions.get("require_memory_associations", False) and not glyph.memory_keys:
            return False

        # Stability condition
        min_stability = conditions.get("min_stability", 0.0)
        if glyph.stability_index < min_stability:
            return False

        # Access frequency condition
        min_access_freq = conditions.get("min_access_frequency", 0.0)
        if metrics.access_frequency < min_access_freq:
            return False

        # Importance condition
        min_importance = conditions.get("min_importance", 0.0)
        return not profile.importance_weight < min_importance

    def _fire_decay_handlers(self, glyph_id: str, decay_state: DecayState):
        """Fire decay state change handlers."""
        for handler in self.decay_handlers[decay_state]:
            try:
                handler(glyph_id)
            except Exception as e:
                logger.error(f"Error in decay handler: {e}")

    def _fire_integrity_handlers(self, glyph_id: str, violation_type: str):
        """Fire integrity violation handlers."""
        for handler in self.integrity_handlers:
            try:
                handler(glyph_id, violation_type)
            except Exception as e:
                logger.error(f"Error in integrity handler: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """Get sentinel operation statistics."""
        total_glyphs = len(self.monitored_glyphs)

        # Count glyphs by decay state
        decay_counts = defaultdict(int)
        for metrics in self.decay_metrics.values():
            decay_counts[metrics.decay_state.value] += 1

        # Count glyphs by persistence policy
        policy_counts = defaultdict(int)
        for profile in self.persistence_profiles.values():
            policy_counts[profile.policy.value] += 1

        # Calculate average metrics
        avg_integrity = 0.0
        avg_access_freq = 0.0
        if total_glyphs > 0:
            avg_integrity = sum(m.integrity_score for m in self.decay_metrics.values()) / total_glyphs
            avg_access_freq = sum(m.access_frequency for m in self.decay_metrics.values()) / total_glyphs

        return {
            "total_monitored_glyphs": total_glyphs,
            "monitoring_cycles": self.monitoring_cycles,
            "cleanup_operations": self.cleanup_operations,
            "expired_glyphs": self.expired_glyphs,
            "integrity_violations": self.integrity_violations,
            "decay_state_distribution": dict(decay_counts),
            "persistence_policy_distribution": dict(policy_counts),
            "average_integrity_score": avg_integrity,
            "average_access_frequency": avg_access_freq,
            "is_monitoring": self.is_monitoring,
            "last_cleanup": self.last_cleanup.isoformat(),
        }


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🛡️ LUKHAS AI - GLYPH SENTINEL
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Decay Detection: Comprehensive glyph degradation monitoring
║ • Persistence Management: Automated retention policy enforcement
║ • Integrity Monitoring: Continuous symbolic hash validation
║ • Usage Tracking: Access pattern analysis and optimization
║ • Event System: Configurable handlers for decay and expiration events
║ • Background Operations: Continuous monitoring and cleanup
║ • Statistics Reporting: Detailed operational metrics and analytics
║ • Policy Management: Flexible persistence policies with custom conditions
╠═══════════════════════════════════════════════════════════════════════════════
║ INTEGRATION POINTS
╠═══════════════════════════════════════════════════════════════════════════════
║ • Core Glyph System: Full lifecycle monitoring for all glyph types
║ • Memory System: Access tracking integration for usage-based persistence
║ • Temporal System: Age-based decay calculations and expiration management
║ • Event Framework: Extensible handler system for system integration
║ • Statistics Engine: Comprehensive operational analytics and reporting
║ • Cleanup Systems: Automated memory management and optimization
╚═══════════════════════════════════════════════════════════════════════════════
"""
