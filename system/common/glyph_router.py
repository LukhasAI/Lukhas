"""
GLYPH Communication Router
=========================
Optimized routing and caching for GLYPH-based communication.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from lukhas.core.common import GLYPHSymbol

logger = logging.getLogger(__name__)


@dataclass
class GLYPHRoute:
    """Represents a GLYPH routing rule"""

    glyph_type: str
    source_pattern: str
    target_module: str
    priority: int = 0
    cache_ttl: int = 60  # seconds


class GLYPHRouter:
    """Intelligent GLYPH routing system"""

    def __init__(self):
        self._routes: dict[str, list[GLYPHRoute]] = defaultdict(list)
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._cache: dict[str, Any] = {}
        self._cache_timestamps: dict[str, datetime] = {}
        self._metrics = {
            "glyphs_routed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "routing_errors": 0,
        }

        # Initialize default routes
        self._initialize_default_routes()

    def _initialize_default_routes(self):
        """Set up default GLYPH routes"""
        default_routes = [
            # Core system routes
            GLYPHRoute("SYSTEM_*", "core.*", "orchestration", priority=10),
            GLYPHRoute("CONFIG_*", "core.*", "governance", priority=5),
            # Consciousness routes
            GLYPHRoute("AWARENESS_*", "consciousness.*", "consciousness.unified", priority=10),
            GLYPHRoute("DREAM_*", "consciousness.dream.*", "consciousness.dream", priority=10),
            # Memory routes
            GLYPHRoute("MEMORY_*", "memory.*", "memory.core", priority=10),
            GLYPHRoute("FOLD_*", "memory.folds.*", "memory.folds", priority=10),
            # Cross-module routes
            GLYPHRoute("SYNC_*", "*", "orchestration.brain", priority=20),
            GLYPHRoute("ERROR_*", "*", "governance.guardian", priority=30),
        ]

        for route in default_routes:
            self.add_route(route)

    def add_route(self, route: GLYPHRoute):
        """Add a GLYPH route"""
        self._routes[route.glyph_type].append(route)
        # Sort by priority
        self._routes[route.glyph_type].sort(key=lambda r: r.priority, reverse=True)

    def register_handler(self, glyph_pattern: str, handler: Callable):
        """Register a GLYPH handler"""
        self._handlers[glyph_pattern].append(handler)
        logger.info(f"Registered handler for pattern: {glyph_pattern}")

    async def route_glyph(self, glyph: GLYPHSymbol, source_module: str) -> Optional[str]:
        """Route a GLYPH to appropriate handler"""
        glyph_type = glyph.symbol_type

        # Check cache first
        cache_key = f"{glyph_type}:{source_module}"
        cached_result = self._get_cached_route(cache_key)
        if cached_result:
            self._metrics["cache_hits"] += 1
            return cached_result

        self._metrics["cache_misses"] += 1

        # Find matching routes
        target_module = None
        for pattern, routes in self._routes.items():
            if self._matches_pattern(glyph_type, pattern):
                for route in routes:
                    if self._matches_pattern(source_module, route.source_pattern):
                        target_module = route.target_module
                        # Cache the result
                        self._cache_route(cache_key, target_module, route.cache_ttl)
                        break

        if target_module:
            self._metrics["glyphs_routed"] += 1
            await self._deliver_glyph(glyph, target_module)
            return target_module
        else:
            self._metrics["routing_errors"] += 1
            logger.warning(f"No route found for GLYPH {glyph_type} from {source_module}")
            return None

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches pattern (supports wildcards)"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        return value == pattern

    def _get_cached_route(self, cache_key: str) -> Optional[str]:
        """Get cached route if valid"""
        if cache_key in self._cache:
            timestamp = self._cache_timestamps[cache_key]
            if datetime.now(timezone.utc) - timestamp < timedelta(seconds=60):
                return self._cache[cache_key]
        return None

    def _cache_route(self, cache_key: str, target: str, ttl: int):
        """Cache a routing decision"""
        self._cache[cache_key] = target
        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)

    async def _deliver_glyph(self, glyph: GLYPHSymbol, target_module: str):
        """Deliver GLYPH to target module handlers"""
        # Find matching handlers
        for pattern, handlers in self._handlers.items():
            if self._matches_pattern(glyph.symbol_type, pattern):
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(glyph, target_module)
                        else:
                            handler(glyph, target_module)
                    except Exception as e:
                        logger.error(f"Error in GLYPH handler: {e}")

    def get_metrics(self) -> dict[str, int]:
        """Get routing metrics"""
        return self._metrics.copy()

    def clear_cache(self):
        """Clear routing cache"""
        self._cache.clear()
        self._cache_timestamps.clear()


# Global GLYPH router instance
glyph_router = GLYPHRouter()


# Helper functions
async def emit_glyph(glyph: GLYPHSymbol, source_module: str):
    """Emit a GLYPH through the router"""
    await glyph_router.route_glyph(glyph, source_module)


def create_glyph(symbol_type: str, payload: dict[str, Any], metadata: Optional[dict[str, Any]] = None) -> GLYPHSymbol:
    """Create a GLYPH with standard format"""
    return GLYPHSymbol(
        symbol_type=symbol_type,
        symbol_data=payload,
        metadata=metadata or {},
        timestamp=datetime.now(timezone.utc),
    )
