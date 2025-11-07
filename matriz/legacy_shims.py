"""
Legacy Shim Registry (T4)
=========================
Purpose:
    Centralized registry for wrapping legacy CognitiveNode-style implementations
    behind the frozen MATRIZ v1.0.0 contract, via `LegacyShim`.

Usage:
    from matriz.legacy_shims import register_legacy_node, shim_for, get_shimmed_nodes
    from legacy_pkg.nodes import OldBioNode

    # Register once at startup (e.g., router bootstrap)
    register_legacy_node("bio", OldBioNode())

    # Later, fetch the shimmed node for routing
    node = shim_for("bio")
    result = node.handle(msg)

Design notes:
    - This module is intentionally minimal: it does not import or introspect
      any legacy packages automatically. Callers must pass concrete instances.
    - Re-registration of the same name overwrites the previous entry (with a log).
    - All shims are instances of `LegacyShim` and thus conform to `MatrizNode`.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from matriz.legacy_shim import LegacyShim  # shim and interface

logger = logging.getLogger(__name__)

# In-memory registry of name -> LegacyShim
_REGISTRY: dict[str, LegacyShim] = {}


def register_legacy_node(name: str, legacy_node: Any) -> LegacyShim:
    """
    Wrap a legacy node instance with LegacyShim and register it by name.

    Args:
        name: Stable, unique key for the node (used by router/topics).
        legacy_node: A legacy implementation (e.g., CognitiveNode) instance.

    Returns:
        The created LegacyShim instance.

    Behavior:
        - Overwrites existing entry of the same name (logs a warning).
        - Does not validate the legacy_node here; validation occurs on handle().
    """
    if name in _REGISTRY:
        logger.warning("legacy_shims: overwriting existing registration for '%s'", name)

    shim = LegacyShim(legacy_node)
    _REGISTRY[name] = shim
    logger.info("legacy_shims: registered legacy node '%s' as shim '%s'", name, shim.name)
    return shim


def register_many(mapping: dict[str, Any]) -> dict[str, LegacyShim]:
    """
    Bulk-register multiple legacy nodes.

    Args:
        mapping: Dict of {name: legacy_node_instance}

    Returns:
        Dict of {name: LegacyShim} that were registered.
    """
    out: dict[str, LegacyShim] = {}
    for name, node in mapping.items():
        out[name] = register_legacy_node(name, node)
    return out


def shim_for(name: str) -> LegacyShim | None:
    """
    Retrieve a registered LegacyShim by name.

    Returns:
        LegacyShim if present, else None.
    """
    return _REGISTRY.get(name)


def get_shimmed_nodes() -> dict[str, LegacyShim]:
    """
    Return a shallow copy of the current registry.
    Useful for diagnostics and router bootstrap.
    """
    return dict(_REGISTRY)


# --- Router bootstrap utility ---
def bootstrap_router(router: Any, mapping: dict[str, Any]) -> dict[str, LegacyShim]:
    """
    Bootstrap a router by registering legacy nodes through LegacyShim.

    Args:
        router: An object exposing `register(topic: str, node: MatrizNode)`; typically the SymbolicMeshRouter.
        mapping: Dict of {name: legacy_node_instance}. Each name becomes the registration key.

    Returns:
        dict[str, LegacyShim]: The shimmed nodes that were registered.

    Notes:
        - This function does NOT publish or dispatch messages. It only registers handlers.
        - Registration keys (names) are router topics or keys, depending on the router's API.
        - If a name already exists in the internal registry, it will be overwritten.
    """
    shims = register_many(mapping)
    for name, shim in shims.items():
        try:
            # Router is expected to expose a 'register' method
            router.register(name, shim)
            logger.info("legacy_shims: router registered '%s' -> shim '%s'", name, shim.name)
        except Exception as e:
            logger.error("legacy_shims: failed to register '%s' with router: %s", name, e)
    return shims


__all__ = [
    "bootstrap_router",
    "get_shimmed_nodes",
    "logger",
    "register_legacy_node",
    "register_many",
    "shim_for",
]
