"""QR-G code generation and validation utilities."""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from datetime import datetime, timezone
from typing import Any


class QRGGenerator:
    """Generate and validate QR-G codes for device pairing."""

    def __init__(self, config):
        self.config = {
            **{"code_length": 16, "code_ttl": 300, "max_generation_attempts": 5},
            **(config or {}),
        }
        self.active_codes: dict[str, dict[str, Any]] = {}

    def generate_pairing_code(self, user_id, device_info):
        """Generate a time-limited QR-G code for device pairing."""

        self.cleanup_expired_codes()
        fingerprint = self._fingerprint_device(device_info)

        code_length = int(self.config.get("code_length", 16))
        attempts = int(self.config.get("max_generation_attempts", 5))
        ttl = float(self.config.get("code_ttl", 300))

        code = None
        for _ in range(max(attempts, 1)):
            candidate = secrets.token_hex(code_length)[:code_length].upper()
            if candidate not in self.active_codes:
                code = candidate
                break
        if code is None:
            raise RuntimeError("Unable to generate unique QR-G code")

        expires_at = self._now() + ttl
        issued_at = self._now()
        # ΛTAG: qrg_generation
        self.active_codes[code] = {
            "user_id": user_id,
            "device_info": device_info,
            "device_signature": fingerprint,
            "expires_at": expires_at,
            "issued_at": issued_at,
            "attempts": 0,
        }

        return {
            "code": code,
            "expires_at": expires_at,
            "issued_at": issued_at,
            "signature": fingerprint,
        }

    def validate_pairing_code(self, qr_code, device_signature):
        """Validate a QR-G code and establish pairing."""

        self.cleanup_expired_codes()
        record = self.active_codes.get(qr_code)
        if record is None:
            return {"valid": False, "reason": "unknown_code"}

        if record["expires_at"] <= self._now():
            self.active_codes.pop(qr_code, None)
            return {"valid": False, "reason": "expired"}

        if device_signature != record["device_signature"]:
            record["attempts"] = record.get("attempts", 0) + 1
            return {"valid": False, "reason": "signature_mismatch"}

        paired_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "valid": True,
            "user_id": record["user_id"],
            "device_info": record["device_info"],
            "paired_at": paired_at,
        }
        # ΛTAG: qrg_validation
        self.active_codes.pop(qr_code, None)
        return payload

    def cleanup_expired_codes(self):
        """Clean up expired QR-G codes."""

        now = self._now()
        expired = [code for code, meta in self.active_codes.items() if meta["expires_at"] <= now]
        for code in expired:
            self.active_codes.pop(code, None)

        # ΛTAG: qrg_cleanup
        return len(expired)

    def _fingerprint_device(self, device_info) -> str:
        """Create a deterministic fingerprint for the device payload."""

        normalized = json.dumps(device_info, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _now(self) -> float:
        """Provide a hookable clock for testing."""

        return float(time.time())
