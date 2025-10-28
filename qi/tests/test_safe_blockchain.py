from __future__ import annotations

"""Tests for the QISafeAuditBlockchain compliance reporting."""

import sys
import types
from types import SimpleNamespace

import pytest

rlp_stub = types.ModuleType("rlp")
rlp_stub.encode = lambda data: data  # type: ignore[assignment]
sys.modules.setdefault("rlp", rlp_stub)

from qi.states import safe_blockchain


class _DummyMerkleTree:
    """Simple Merkle tree stub for testing."""

    def __init__(self) -> None:
        self.leaves: list[dict] = []
        self.root: str | None = None

    def add_leaf(self, data: dict) -> None:
        self.leaves.append(data)
        self.root = f"root-{len(self.leaves)}"


@pytest.mark.asyncio
async def test_generate_compliance_report_builds_structured_report(monkeypatch):
    """Ensure the compliance report contains structured metadata."""

    monkeypatch.setattr(safe_blockchain, "MerkleTree", _DummyMerkleTree, raising=False)

    audit_blockchain = safe_blockchain.QISafeAuditBlockchain.__new__(safe_blockchain.QISafeAuditBlockchain)

    audit_blockchain._get_blocks_in_range = lambda _: [  # type: ignore[attr-defined]
        SimpleNamespace(
            number=1,
            transactions=[
                SimpleNamespace(type="ai_decision_audit", data={"decision_id": "a1"})
            ],
        ),
        SimpleNamespace(number=2, transactions=[SimpleNamespace(type="other", data={})]),
    ]

    async def _fake_generate_proof(tree, framework):  # type: ignore[no-untyped-def]
        return {"framework": framework, "leaf_count": len(tree.leaves)}

    async def _fake_sign(root):  # type: ignore[no-untyped-def]
        return f"signature:{root}"

    audit_blockchain._generate_compliance_proof = _fake_generate_proof  # type: ignore[attr-defined]
    audit_blockchain._sign_report = _fake_sign  # type: ignore[attr-defined]

    time_range = SimpleNamespace(start="2025-01-01", end="2025-01-31")
    report = await audit_blockchain.generate_compliance_report(time_range, "GDPR")

    assert isinstance(report, safe_blockchain.ComplianceReport)
    assert report.framework == "GDPR"
    assert report.time_range is time_range
    assert report.block_range == (1, 2)
    assert report.merkle_root == "root-1"
    assert report.total_transactions == 1
    assert report.compliance_proof == {"framework": "GDPR", "leaf_count": 1}
    assert report.cryptographic_attestation == "signature:root-1"
    assert report.report_id.startswith("compliance_gdpr_")
    assert report.generated_at.tzinfo is not None
