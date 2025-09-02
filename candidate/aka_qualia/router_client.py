#!/usr/bin/env python3

"""
Router Client Protocol for Aka Qualia (Wave C - C2)
==================================================

Protocol definition and client implementation for routing PhenomenalGlyphs
to LUKHAS EQNOX SymbolicMeshRouter with priority weighting.

Implements Freud-2025 Wave C specification:
priority = min(1.0, max(0.0, narrative_gravity * 0.7 + risk_score * 0.3))
"""

import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from candidate.aka_qualia.models import PhenomenalGlyph, PhenomenalScene

logger = logging.getLogger(__name__)


class RouterClient(Protocol):
    """
    Protocol for routing PhenomenalGlyphs to symbolic mesh routers.

    Defines the interface contract for integrating Aka Qualia with
    LUKHAS EQNOX routing systems.
    """

    @abstractmethod
    def route(
        self,
        glyphs: list[PhenomenalGlyph],
        priority: float,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Route phenomenological glyphs through the symbolic mesh.

        Args:
            glyphs: List of PhenomenalGlyphs to route
            priority: Routing priority in [0.0, 1.0] range
            context: Optional context for routing decisions
        """
        ...

    @abstractmethod
    def get_routing_status(self) -> dict[str, Any]:
        """
        Get current routing system status and statistics.

        Returns:
            Dict containing routing metrics and health status
        """
        ...


class SymbolicMeshRouterClient:
    """
    Client adapter for LUKHAS SymbolicMeshRouter integration.

    Implements the RouterClient protocol to bridge Aka Qualia
    phenomenological processing with LUKHAS symbolic routing.
    """

    def __init__(
        self,
        router_module: Optional[Any] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize router client.

        Args:
            router_module: LUKHAS symbolic router module (injected)
            config: Router configuration overrides
        """
        self.router_module = router_module
        self.config = self._load_config(config)

        # Statistics tracking
        self.routes_sent = 0
        self.routes_failed = 0
        self.total_priority_weight = 0.0
        self.glyph_type_counts: dict[str, int] = {}

        # Import LUKHAS symbolic signal router
        if not router_module:
            try:
                from candidate.core.orchestration.core_modules.symbolic_signal_router import (
                    route_signal,
                )
                from candidate.orchestration.signals import (
                    DiagnosticSignalType,
                    SymbolicSignal,
                )

                self.route_signal_func = route_signal
                self.SymbolicSignal = SymbolicSignal
                self.DiagnosticSignalType = DiagnosticSignalType
                self.has_lukhas_router = True
            except ImportError as e:
                logger.warning(f"Could not import LUKHAS symbolic router: {e}")
                self.has_lukhas_router = False
        else:
            self.route_signal_func = router_module.route_signal
            self.SymbolicSignal = router_module.SymbolicSignal
            self.DiagnosticSignalType = router_module.DiagnosticSignalType
            self.has_lukhas_router = True

    def _load_config(self, config_override: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Load router client configuration"""
        default_config = {
            "enable_routing": True,
            "max_glyphs_per_route": 10,
            "priority_threshold": 0.1,  # Only route glyphs above this priority
            "glyph_batching": True,
            "route_timeout_ms": 100,
            "fallback_on_error": True,
            "log_routing_decisions": True,
        }

        if config_override:
            default_config.update(config_override)

        return default_config

    def route(
        self,
        glyphs: list[PhenomenalGlyph],
        priority: float,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Route phenomenological glyphs through LUKHAS symbolic mesh.

        Converts PhenomenalGlyphs to SymbolicSignals and routes them
        through the existing LUKHAS routing infrastructure.

        Args:
            glyphs: List of PhenomenalGlyphs to route
            priority: Routing priority in [0.0, 1.0] range
            context: Optional context for routing decisions
        """
        if not self.config["enable_routing"]:
            logger.debug("Routing disabled in configuration")
            return

        if not self.has_lukhas_router:
            logger.warning("LUKHAS router not available, skipping routing")
            return

        if priority < self.config["priority_threshold"]:
            logger.debug(
                f"Priority {priority:.3f} below threshold {self.config['priority_threshold']}, skipping routing"
            )
            return

        if not glyphs:
            logger.debug("No glyphs to route")
            return

        # Limit glyphs per route for performance
        if len(glyphs) > self.config["max_glyphs_per_route"]:
            logger.warning(f"Limiting {len(glyphs)} glyphs to {self.config['max_glyphs_per_route']} per route")
            glyphs = glyphs[: self.config["max_glyphs_per_route"]]

        try:
            # Convert glyphs to symbolic signals and route each
            for glyph in glyphs:
                signal = self._convert_glyph_to_signal(glyph, priority, context)

                if self.config["log_routing_decisions"]:
                    logger.info(f"Routing glyph {glyph.key} with priority {priority:.3f}")

                self.route_signal_func(signal)

                # Update statistics
                self.routes_sent += 1
                self.total_priority_weight += priority
                self.glyph_type_counts[glyph.key] = self.glyph_type_counts.get(glyph.key, 0) + 1

        except Exception as e:
            self.routes_failed += 1
            logger.error(f"Failed to route glyphs: {e}")

            if not self.config["fallback_on_error"]:
                raise

    def _convert_glyph_to_signal(
        self, glyph: PhenomenalGlyph, priority: float, context: Optional[dict[str, Any]]
    ) -> Any:
        """
        Convert PhenomenalGlyph to LUKHAS SymbolicSignal.

        Maps Aka Qualia glyph representation to LUKHAS symbolic
        routing format with priority-based routing hints.

        Args:
            glyph: PhenomenalGlyph to convert
            priority: Routing priority for weighting
            context: Optional routing context

        Returns:
            SymbolicSignal: LUKHAS-compatible signal for routing
        """
        import hashlib
        import time

        # Generate collapse hash for glyph (VIVOX compatibility)
        glyph_data = f"{glyph.key}:{glyph.attrs!s}"
        collapse_hash = hashlib.sha3_256(glyph_data.encode()).hexdigest()[:16]

        # Map priority to confidence score
        confidence_score = min(0.99, max(0.01, priority))  # Clamp to valid range

        # Determine diagnostic event type from glyph key
        diagnostic_event = self._map_glyph_to_diagnostic_event(glyph.key)

        # Create symbolic signal
        signal = self.SymbolicSignal(
            signal_type=diagnostic_event,
            source_module="aka_qualia",
            target_module="symbolic_mesh",
            timestamp=time.time(),
            drift_score=1.0 - priority,  # Inverse relationship
            collapse_hash=collapse_hash,
            confidence_score=confidence_score,
            diagnostic_event=diagnostic_event,
            payload={
                "glyph_key": glyph.key,
                "glyph_attrs": glyph.attrs,
                "priority": priority,
                "routing_context": context or {},
            },
        )

        return signal

    def _map_glyph_to_diagnostic_event(self, glyph_key: str):
        """Map glyph key to LUKHAS DiagnosticSignalType"""
        # Map specific glyph types to diagnostic events
        glyph_mappings = {
            "aka:vigilance": self.DiagnosticSignalType.PULSE,  # High-priority vigilance
            "aka:red_threshold": self.DiagnosticSignalType.PULSE,  # Activation threshold
            "aka:grounding_hint": self.DiagnosticSignalType.PULSE,  # Stabilization needed
            "aka:soothe_anchor": self.DiagnosticSignalType.PULSE,  # Positive anchor
            "aka:approach_avoid": self.DiagnosticSignalType.PULSE,  # Behavioral signal
        }

        return glyph_mappings.get(glyph_key, self.DiagnosticSignalType.PULSE)

    def get_routing_status(self) -> dict[str, Any]:
        """Get current routing system status and statistics"""
        avg_priority = self.total_priority_weight / self.routes_sent if self.routes_sent > 0 else 0.0

        failure_rate = (
            self.routes_failed / (self.routes_sent + self.routes_failed)
            if (self.routes_sent + self.routes_failed) > 0
            else 0.0
        )

        return {
            "router_available": self.has_lukhas_router,
            "routing_enabled": self.config["enable_routing"],
            "routes_sent": self.routes_sent,
            "routes_failed": self.routes_failed,
            "failure_rate": failure_rate,
            "average_priority": avg_priority,
            "glyph_type_distribution": self.glyph_type_counts.copy(),
            "configuration": self.config.copy(),
        }

    def reset_statistics(self) -> None:
        """Reset routing statistics counters"""
        self.routes_sent = 0
        self.routes_failed = 0
        self.total_priority_weight = 0.0
        self.glyph_type_counts.clear()


class MockRouterClient:
    """
    Mock router client for testing and development.

    Implements RouterClient protocol without actual routing,
    useful for unit tests and offline development.
    """

    def __init__(self):
        self.routed_glyphs: list[tuple[list[PhenomenalGlyph], float]] = []
        self.routing_calls = 0

    def route(
        self,
        glyphs: list[PhenomenalGlyph],
        priority: float,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Mock routing - just record the call"""
        self.routed_glyphs.append((glyphs.copy(), priority))
        self.routing_calls += 1

    def get_routing_status(self) -> dict[str, Any]:
        """Mock routing status"""
        return {
            "router_available": True,
            "routing_enabled": True,
            "routes_sent": self.routing_calls,
            "routes_failed": 0,
            "failure_rate": 0.0,
            "average_priority": (
                sum(p for _, p in self.routed_glyphs) / len(self.routed_glyphs) if self.routed_glyphs else 0.0
            ),
            "mock_mode": True,
        }

    def get_routed_glyphs(self) -> list[tuple[list[PhenomenalGlyph], float]]:
        """Get list of routed glyphs for testing"""
        return self.routed_glyphs.copy()

    def clear_history(self) -> None:
        """Clear routing history"""
        self.routed_glyphs.clear()
        self.routing_calls = 0


def create_router_client(router_type: str = "lukhas", config: Optional[dict[str, Any]] = None) -> RouterClient:
    """
    Factory function to create appropriate router client.

    Args:
        router_type: Type of router client ("lukhas", "mock")
        config: Optional configuration overrides

    Returns:
        RouterClient: Configured router client instance
    """
    if router_type == "mock":
        return MockRouterClient()
    elif router_type == "lukhas":
        return SymbolicMeshRouterClient(config=config)
    else:
        raise ValueError(f"Unknown router type: {router_type}")


def compute_routing_priority(scene: PhenomenalScene) -> float:
    """
    Compute routing priority using Freud-2025 Wave C formula.

    Formula: priority = min(1.0, max(0.0, narrative_gravity * 0.7 + risk_score * 0.3))

    Args:
        scene: PhenomenalScene for priority calculation

    Returns:
        float: Priority value in [0.0, 1.0] for router weighting
    """
    base_priority = scene.proto.narrative_gravity * 0.7 + scene.risk.score * 0.3
    return min(1.0, max(0.0, base_priority))
