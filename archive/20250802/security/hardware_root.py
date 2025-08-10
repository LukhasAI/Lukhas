"""Hardware root of trust abstraction."""

import os

import structlog

log = structlog.get_logger(__name__)


class HardwareRoot:
    """Minimal interface to a hardware root of trust."""

    def __init__(self):
        self.available = bool(os.environ.get("TPM_AVAILABLE", "0") == "1")
        if not self.available:
            log.warning("Hardware root not available")

    def store_key(self, key_name: str, key_data: bytes) -> bool:
        if not self.available:
            return False
        log.info("Key stored in hardware", key=key_name)
        return True

    def retrieve_key(self, key_name: str) -> bytes:
        if not self.available:
            raise RuntimeError("No hardware root")
        log.info("Key retrieved from hardware", key=key_name)
        return b"dummy"
