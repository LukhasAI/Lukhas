"""Unit tests for the idempotency cache helpers."""
from __future__ import annotations

import pytest

from core.reliability import idempotency


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure the idempotency cache is reset between tests."""
    idempotency.clear()
    yield
    idempotency.clear()


def test_idempotency_ttl_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    base = 1_000.0
    monkeypatch.setattr(idempotency.time, "time", lambda: base)

    key = idempotency.cache_key("/v1/responses", "abc", b"{}")
    idempotency.put(key, 200, b"ok", "application/json")

    monkeypatch.setattr(idempotency.time, "time", lambda: base + idempotency._TTL + 1)

    assert idempotency.get(key) is None


def test_idempotency_different_body_is_miss() -> None:
    key = idempotency.cache_key("/v1/responses", "replay-key", b"body-1")
    idempotency.put(key, 201, b"first", "application/json")

    other_key = idempotency.cache_key("/v1/responses", "replay-key", b"body-2")

    assert idempotency.get(other_key) is None
    assert idempotency.get(key) == (201, b"first", "application/json")
