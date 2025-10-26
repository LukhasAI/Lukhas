"""High priority coverage for QRSManager audit trail behaviour."""

import asyncio
import time

from labs.bridge.api.api import QRSManager, QRSStatus


def _payload() -> dict:
    return {
        "request_id": "req-123",
        "response_payload": {"result": "ok"},
        "timestamp": int(time.time()),
        "service": "lukhas.bridge",
    }


def test_qrs_manager_records_audit_events():
    manager = QRSManager(secret_key="secret-key")

    qrs = asyncio.run(manager.create_qrs(_payload()))
    verification = asyncio.run(manager.verify_qrs(qrs.to_dict()))

    assert verification.valid
    trail = manager.get_audit_trail()
    assert any(entry["event"] == "qrs_created" for entry in trail)
    assert any(entry["event"] == "qrs_verified" and entry["valid"] for entry in trail)


def test_qrs_manager_detects_tampering_and_logs():
    manager = QRSManager(secret_key="secret-key")

    qrs = asyncio.run(manager.create_qrs(_payload()))
    tampered = qrs.to_dict()
    tampered["signature"] = "0xdeadbeef"

    result = asyncio.run(manager.verify_qrs(tampered))

    assert not result.valid
    assert result.status == QRSStatus.TAMPERED

    trail = manager.get_audit_trail()
    assert any(entry["event"] == "qrs_verified" and not entry["valid"] for entry in trail)


def test_qrs_manager_batch_verify_reports_expired():
    manager = QRSManager(secret_key="secret-key")

    qrs_valid = asyncio.run(manager.create_qrs(_payload()))
    expired = qrs_valid.to_dict()
    expired.setdefault("metadata", {})["expires_at"] = int(time.time()) - 1

    results = asyncio.run(manager.batch_verify([qrs_valid.to_dict(), expired]))

    assert any(result.valid for result in results)
    assert any(result.status == QRSStatus.EXPIRED for result in results)
