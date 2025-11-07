from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha3_256
from types import SimpleNamespace
from typing import Any

import pytest
from qi.states import safe_blockchain


class DummyMerkleTree:
    """Deterministic Merkle tree used for testing."""

    def __init__(self) -> None:
        self.leaf_hashes: list[str] = []
        self.root: str | None = None

    def add_leaf(self, data: Any) -> None:
        payload = json.dumps(data, sort_keys=True, default=str).encode()
        leaf_hash = sha3_256(payload).hexdigest()
        self.leaf_hashes.append(leaf_hash)
        combined = "".join(self.leaf_hashes).encode()
        self.root = sha3_256(combined).hexdigest() if self.leaf_hashes else None


class DummySigner:
    async def sign(self, payload: bytes, include_timestamp: bool = True) -> str:
        return f"signature:{len(payload)}"


@dataclass
class DummyTransaction:
    data: dict[str, Any]
    transaction_type: str = "ai_decision_audit"

    @property
    def type(self) -> str:
        return self.transaction_type

    @property
    def hash(self) -> str:
        payload = json.dumps(self.data, sort_keys=True, default=str).encode()
        return sha3_256(payload).hexdigest()


@dataclass
class DummyBlock:
    number: int
    transactions: list[DummyTransaction]


class DummyBlockchain(safe_blockchain.QISafeAuditBlockchain):
    def __init__(self, blocks: list[DummyBlock]) -> None:
        # Bypass parent initialisation that depends on unresolved TODOs
        self.chain = []
        self.pending_transactions = []
        self.pqc_signer = DummySigner()
        self.config = SimpleNamespace(block_size=1)
        self._blocks = blocks

    def _get_blocks_in_range(self, time_range: Any):
        return list(self._blocks)

    async def _generate_compliance_proof(self, decision_tree: DummyMerkleTree, framework: str):
        return {
            "framework": framework,
            "leaf_count": len(decision_tree.leaf_hashes),
            "root": decision_tree.root,
        }

    async def _sign_report(self, merkle_root: str | None) -> str | None:
        if not merkle_root:
            return None
        return f"attestation:{merkle_root}"


@pytest.mark.asyncio
async def test_generate_compliance_report_summarises_decisions(monkeypatch):
    monkeypatch.setattr(safe_blockchain, "MerkleTree", DummyMerkleTree, raising=False)

    blocks = [
        DummyBlock(
            number=1,
            transactions=[
                DummyTransaction({"model_version": "alpha", "user_consent_proof": "zk-1"}),
                DummyTransaction({"model_version": "beta", "user_consent_proof": "zk-2"}),
            ],
        ),
        DummyBlock(
            number=2,
            transactions=[
                DummyTransaction({"model_version": "beta"}),
                DummyTransaction({"model_version": "gamma"}, transaction_type="system_event"),
            ],
        ),
    ]

    blockchain = DummyBlockchain(blocks)

    report = await blockchain.generate_compliance_report(SimpleNamespace(), "gdpr")

    assert isinstance(report, safe_blockchain.ComplianceReport)
    assert report.total_blocks == 2
    assert report.total_decisions == 3
    assert report.block_range == (1, 2)
    assert set(report.model_breakdown) == {"alpha", "beta"}
    assert report.model_breakdown["beta"] == 2
    assert report.consent_summary == {"with_consent": 2, "without_consent": 1}
    assert report.compliance_proof == {
        "framework": "gdpr",
        "leaf_count": 3,
        "root": report.merkle_root,
    }
    assert report.cryptographic_attestation == f"attestation:{report.merkle_root}"

    report_dict = report.to_dict()
    assert report_dict["total_decisions"] == 3
    assert report_dict["model_breakdown"]["beta"] == 2
    assert report_dict["framework"] == "gdpr"
    assert report_dict["generated_at"].endswith("Z") is False  # naive isoformat


@pytest.mark.asyncio
async def test_generate_compliance_report_handles_empty_ranges(monkeypatch):
    monkeypatch.setattr(safe_blockchain, "MerkleTree", DummyMerkleTree, raising=False)

    blockchain = DummyBlockchain([])
    report = await blockchain.generate_compliance_report(SimpleNamespace(), "ccpa")

    assert report.total_blocks == 0
    assert report.total_decisions == 0
    assert report.block_range is None
    assert report.merkle_root is None
    assert report.compliance_proof is None
    assert report.cryptographic_attestation is None
    assert report.consent_summary == {"with_consent": 0, "without_consent": 0}
    assert report.to_dict()["compliance_proof"] is None
