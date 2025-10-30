"""Tests for :mod:`qi.privacy.zero_knowledge_system` privacy statement helpers."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _install_proof_stubs():
    """Provide lightweight stubs for external proof systems used in tests."""

    bulletproofs = types.ModuleType("bulletproofs")

    class _BulletproofSystem:  # pragma: no cover - behavior is not exercised
        ...

    bulletproofs.BulletproofSystem = _BulletproofSystem
    sys.modules.setdefault("bulletproofs", bulletproofs)

    zksnark = types.ModuleType("zksnark")

    class _ZkSnark:  # pragma: no cover - behavior is not exercised
        ...

    zksnark.ZkSnark = _ZkSnark
    sys.modules.setdefault("zksnark", zksnark)

    yield

    sys.modules.pop("bulletproofs", None)
    sys.modules.pop("zksnark", None)


@pytest.fixture()
def privacy_module():
    """Load the privacy module without triggering heavy package imports."""

    module_name = "qi.privacy.zero_knowledge_system"
    module_path = Path(__file__).resolve().parents[3] / "qi" / "privacy" / "zero_knowledge_system.py"

    qi_pkg = types.ModuleType("qi")
    qi_pkg.__path__ = []  # type: ignore[attr-defined]
    sys.modules.setdefault("qi", qi_pkg)

    privacy_pkg = types.ModuleType("qi.privacy")
    privacy_pkg.__path__ = []  # type: ignore[attr-defined]
    sys.modules.setdefault("qi.privacy", privacy_pkg)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    yield module

    sys.modules.pop(module_name, None)
    sys.modules.pop("qi.privacy", None)
    sys.modules.pop("qi", None)


def test_privacy_statement_adaptive_threshold(privacy_module):
    PrivacyStatement = privacy_module.PrivacyStatement

    statement = PrivacyStatement(
        statement_id="stmt-001",
        requires_non_interactive=True,
        circuit_size=512,
        public_input={"user_id": "anon"},
    )

    assert statement.is_suitable_for_adaptive_mode() is True
    assert statement.is_suitable_for_adaptive_mode(threshold=256) is False


def test_privacy_statement_describe_returns_copy(privacy_module):
    PrivacyStatement = privacy_module.PrivacyStatement

    statement = PrivacyStatement(
        statement_id="stmt-002",
        requires_non_interactive=False,
        circuit_size=12000,
        public_input=[1, 2, 3],
        metadata={"purpose": "audit"},
    )

    description = statement.describe()

    assert description["statement_id"] == "stmt-002"
    assert description["metadata"] == {"purpose": "audit"}

    statement.metadata["purpose"] = "updated"

    assert description["metadata"] == {"purpose": "audit"}
