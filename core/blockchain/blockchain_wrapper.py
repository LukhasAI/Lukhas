"""Minimal blockchain wrapper for immutable Healix audit events."""
from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger("blockchain_wrapper")


@dataclass
class BlockchainTransaction:
    """Representation of a blockchain transaction."""

    reference_id: str
    payload: Mapping[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    previous_hash: str = ""
    collapseHash: str = ""


class BlockchainWrapper:
    """In-memory blockchain helper for dashboard integrations."""

    def __init__(self) -> None:
        self._chain: list[BlockchainTransaction] = []
        # ΛTAG: collapseHash - ensures sequential immutability for audit entries
        logger.debug("BlockchainWrapper initialized", extra={"length": 0})

    def record_transaction(self, reference_id: str, payload: Mapping[str, Any]) -> BlockchainTransaction:
        """Record a transaction and append it to the chain."""

        previous_hash = self._chain[-1].collapseHash if self._chain else ""
        collapse_hash = self._compute_hash(reference_id, payload, previous_hash)
        transaction = BlockchainTransaction(
            reference_id=reference_id,
            payload=dict(payload),
            previous_hash=previous_hash,
            collapseHash=collapse_hash,
        )
        self._chain.append(transaction)
        logger.info(
            "Blockchain transaction recorded",
            extra={"reference_id": reference_id, "collapseHash": collapse_hash},
        )
        return transaction

    def get_transactions(self) -> list[BlockchainTransaction]:
        """Return a copy of the blockchain transactions."""

        return list(self._chain)

    def verify_integrity(self) -> bool:
        """Verify that the chain has not been tampered with."""

        for index, transaction in enumerate(self._chain):
            expected_hash = self._compute_hash(
                transaction.reference_id,
                transaction.payload,
                transaction.previous_hash,
            )
            if transaction.collapseHash != expected_hash:
                logger.error(
                    "Blockchain integrity failure",
                    extra={"index": index, "expected": expected_hash, "actual": transaction.collapseHash},
                )
                return False
        logger.debug("Blockchain integrity verified", extra={"length": len(self._chain)})
        return True

    def _compute_hash(
        self,
        reference_id: str,
        payload: Mapping[str, Any],
        previous_hash: str,
    ) -> str:
        serialized_payload = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256()
        digest.update(reference_id.encode("utf-8"))
        digest.update(previous_hash.encode("utf-8"))
        digest.update(serialized_payload.encode("utf-8"))
        collapse_hash = digest.hexdigest()
        logger.debug(
            "Blockchain hash computed",
            extra={"reference_id": reference_id, "collapseHash": collapse_hash},
        )
        return collapse_hash

    # ✅ TODO: connect to persistent ledger backend when available
