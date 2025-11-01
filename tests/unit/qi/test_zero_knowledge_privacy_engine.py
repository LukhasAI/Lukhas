import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "qi" / "privacy" / "zero_knowledge_system.py"

QI_PACKAGE_PATH = str(REPO_ROOT / "qi")
qi_module = sys.modules.get("qi")
if qi_module is None:
    qi_module = types.ModuleType("qi")
    qi_module.__path__ = [QI_PACKAGE_PATH]
    sys.modules["qi"] = qi_module
elif hasattr(qi_module, "__path__") and QI_PACKAGE_PATH not in qi_module.__path__:
    qi_module.__path__.append(QI_PACKAGE_PATH)

spec = importlib.util.spec_from_file_location(
    "qi.privacy.zero_knowledge_system",
    MODULE_PATH,
    submodule_search_locations=[str(MODULE_PATH.parent)],
)
assert spec is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
assert spec.loader is not None
spec.loader.exec_module(module)

PrivacyStatement = module.PrivacyStatement
PrivateWitness = module.PrivateWitness
ZeroKnowledgePrivacyEngine = module.ZeroKnowledgePrivacyEngine


def test_privacy_statement_generates_identifier() -> None:
    """Default identifiers should be generated from the statement fingerprint."""

    statement = PrivacyStatement(
        public_input={"balance": "100"},
        requires_non_interactive=True,
        circuit_size=512,
        description="Balance disclosure without revealing account details",
    )

    assert statement.metadata == {}
    assert statement.statement_id.startswith("stmt-")
    assert len(statement.statement_id) == len("stmt-") + 12


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

    witness = PrivateWitness(values={"secret": 42})

    result = await engine.create_privacy_preserving_proof(
        statement=statement,
        witness=witness,
        proof_type="adaptive",
    )

    assert result == "snark-proof"
    engine._create_zksnark_proof.assert_awaited_once_with(statement, witness)
    engine._create_bulletproof.assert_not_called()


@pytest.mark.asyncio
async def test_proof_metadata_includes_statement_details() -> None:
    """Generated proofs should embed statement metadata for provenance."""

    engine = ZeroKnowledgePrivacyEngine()
    statement = PrivacyStatement(
        statement_id="stmt-xyz",
        public_input={"balance": 7},
        requires_non_interactive=False,
        circuit_size=8192,
        metadata={"origin": "unit-test"},
    )
    witness = PrivateWitness(values={"range": (0, 10)})

    proof = await engine._create_bulletproof(statement, witness)

    assert proof.metadata["statement_id"] == "stmt-xyz"
    assert proof.metadata["origin"] == "unit-test"
    assert proof.public_input == {"balance": 7}
