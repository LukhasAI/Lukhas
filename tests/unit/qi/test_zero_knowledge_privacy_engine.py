"""Unit tests for the zero-knowledge privacy engine primitives."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

QI_PACKAGE_PATH = str(REPO_ROOT / "qi")
qi_module = sys.modules.get("qi")
if qi_module is None:
    qi_module = types.ModuleType("qi")
    qi_module.__path__ = [QI_PACKAGE_PATH]
    sys.modules["qi"] = qi_module
elif hasattr(qi_module, "__path__") and QI_PACKAGE_PATH not in qi_module.__path__:
    qi_module.__path__.append(QI_PACKAGE_PATH)


def _ensure_stubbed_modules() -> None:
    """Provide lightweight stubs for optional cryptography dependencies."""

    bulletproofs_module = sys.modules.setdefault("bulletproofs", types.ModuleType("bulletproofs"))

    if not hasattr(bulletproofs_module, "BulletproofSystem"):
        class _BulletproofSystemStub:  # pragma: no cover - simple compatibility shim
            async def verify(self, proof, expected_computation):  # noqa: D401 - inherited behaviour not documented
                """Stub verification routine that always succeeds."""

                return True

        bulletproofs_module.BulletproofSystem = _BulletproofSystemStub

    zksnark_module = sys.modules.setdefault("zksnark", types.ModuleType("zksnark"))

    if not hasattr(zksnark_module, "ZkSnark"):
        class _ZkSnarkStub:  # pragma: no cover - simple compatibility shim
            def __init__(self, curve: str = "BN254") -> None:  # noqa: D401 - init mirrors production signature
                self.curve = curve

            async def trusted_setup(self, circuit):
                return types.SimpleNamespace(verification_key="vk", circuit=circuit)

            async def prove(self, circuit, setup_params, public_input, private_witness):
                return {
                    "circuit": circuit,
                    "setup": setup_params,
                    "public": public_input,
                    "witness": private_witness,
                }

            async def verify(self, verification_key, public_input, proof_data):
                return verification_key == "vk" and proof_data["public"] == public_input

        zksnark_module.ZkSnark = _ZkSnarkStub


_ensure_stubbed_modules()

from qi.privacy.zero_knowledge_system import PrivacyStatement, ZeroKnowledgePrivacyEngine


def test_privacy_statement_metadata_defaults() -> None:
    """Metadata defaults to an empty dictionary for repeatable caching behaviour."""

    statement = PrivacyStatement(
        statement_id="stmt-001",
        public_input={"balance": "100"},
        requires_non_interactive=True,
        circuit_size=512,
        description="Balance disclosure without revealing account details",
    )

    assert statement.metadata == {}


@pytest.mark.asyncio
async def test_adaptive_proof_selection_uses_privacy_statement() -> None:
    """The adaptive path should route to zk-SNARKs when the statement requires it."""

    engine = ZeroKnowledgePrivacyEngine()
    engine._create_zksnark_proof = AsyncMock(return_value="snark-proof")
    engine._create_bulletproof = AsyncMock(return_value="bullet-proof")

    statement = PrivacyStatement(
        statement_id="stmt-002",
        public_input={"feature": "value"},
        requires_non_interactive=True,
        circuit_size=2048,
        description="Test statement",
    )

    witness = {"secret": 42}

    result = await engine.create_privacy_preserving_proof(
        statement=statement,
        witness=witness,
        proof_type="adaptive",
    )

    assert result == "snark-proof"
    engine._create_zksnark_proof.assert_awaited_once_with(statement, witness)
    engine._create_bulletproof.assert_not_called()
