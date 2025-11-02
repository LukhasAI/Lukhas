"""
Interfaces for identity
==============================

This module provides abstract base classes and data classes that define the
interfaces for the identity module.

Other modules, such as `governance`, should import from this module
to avoid circular dependencies.
"""

from typing import Any, Optional
import abc


def ensure_both_id_keys(obj: dict[str, Any], lid: Optional[str]) -> None:
    """Ensure the mapping `obj` contains both `lid` and `lambda_id` keys.

    This is useful when returning data to callers that may expect the
    historical JSON key `lambda_id` while internal logic uses `lid`.
    """
    if lid is None:
        return

    # Canonical short name
    obj.setdefault("lid", lid)

    # Backwards-compatible historical key
    obj.setdefault("lambda_id", lid)


class AuthenticationIntegration(abc.ABC):
    """
    🎖️ LUKHAS Authentication Integration Bridge Interface

    Coordinates between:
    - Consolidated consciousness-aware auth system
    - WALLET identity management
    - QRG advanced authentication flows
    - Production nucleus components
    """

    @abc.abstractmethod
    async def initialize(self) -> None: ...

    @abc.abstractmethod
    def get_component_paths(self) -> dict[str, Any]: ...

    @abc.abstractmethod
    def get_bridge_paths(self) -> dict[str, str]: ...

    @abc.abstractmethod
    def get_integration_status(self) -> dict[str, Any]: ...
