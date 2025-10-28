"""Tests for :mod:`core.module_registry`."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.module_registry import ModuleInfo, ModuleRegistry, TierLevel


class DummyModule:
    """Simple module stub used in tests."""

    def __init__(self, name: str) -> None:
        self.name = name

    def ping(self) -> str:
        return f"pong:{self.name}"


@pytest.fixture()
def registry() -> ModuleRegistry:
    """Create a fresh :class:`ModuleRegistry` for each test."""

    return ModuleRegistry()


def register_sample_module(
    registry: ModuleRegistry,
    module_id: str = "test",
    *,
    min_tier: int | None = None,
) -> DummyModule:
    """Helper to register a module and return the underlying instance."""

    instance = DummyModule(module_id)
    assert registry.register_module(
        module_id=module_id,
        module_instance=instance,
        name=f"Module {module_id}",
        version="1.0.0",
        path=f"memory.{module_id}",
        min_tier=min_tier,
        permissions={"read"},
        dependencies=["core"],
    )
    return instance


def test_register_module_stores_metadata(registry: ModuleRegistry) -> None:
    """Registering a module stores it in the registry and logs the action."""

    instance = register_sample_module(registry)

    assert "test" in registry.modules
    module_info = registry.modules["test"]
    assert isinstance(module_info, ModuleInfo)
    assert module_info.instance is instance
    assert module_info.health_status == "healthy"
    assert registry.audit_log[-1]["action"] == "module_registered"


def test_get_module_updates_access_metadata(registry: ModuleRegistry) -> None:
    """Fetching a module updates access statistics and returns the instance."""

    instance = register_sample_module(registry)

    result = registry.get_module("test", user_id="user-123")
    assert result is instance

    module_info = registry.modules["test"]
    assert module_info.access_count == 1
    assert module_info.last_accessed is not None
    assert registry.audit_log[-1]["action"] == "module_accessed"


def test_get_module_denied_when_tier_check_fails(registry: ModuleRegistry) -> None:
    """When the tier check fails the registry denies access and logs it."""

    register_sample_module(registry)

    def deny_access(_user_id: str, _module: ModuleInfo) -> bool:
        return False

    registry._check_tier_access = deny_access  # type: ignore[method-assign]

    result = registry.get_module("test", user_id="user-123")
    assert result is None
    assert registry.audit_log[-1]["action"] == "module_access_denied"


def test_list_modules_respects_access_checks(registry: ModuleRegistry) -> None:
    """The list endpoint only returns modules visible to the user."""

    register_sample_module(registry, module_id="open")
    register_sample_module(registry, module_id="restricted", min_tier=TierLevel.TRUSTED)

    def filter_access(_user_id: str, module: ModuleInfo) -> bool:
        return module.module_id != "restricted"

    registry._check_tier_access = filter_access  # type: ignore[method-assign]

    visible = registry.list_modules(user_id="user-123")
    module_ids = {module["module_id"] for module in visible}
    assert module_ids == {"open"}


def test_get_module_health_returns_expected_fields(registry: ModuleRegistry) -> None:
    """Health information contains status, timestamps and counters."""

    register_sample_module(registry)
    registry.get_module("test", user_id="user-123")

    module_info = registry.modules["test"]
    module_info.registered_at = datetime.now(timezone.utc)

    health = registry.get_module_health("test")
    assert health["module_id"] == "test"
    assert health["health_status"] == "healthy"
    assert health["access_count"] == 1
    assert "last_accessed" in health
    assert "uptime" in health


def test_register_core_connections_returns_known_services(registry: ModuleRegistry) -> None:
    """Core connections register expected service descriptors."""

    connections = registry.register_core_connections()
    expected = {"orchestration", "ethics", "bridge", "memory", "identity"}
    assert set(connections) == expected
    assert registry.audit_log[-1]["action"] == "connection_registered"
