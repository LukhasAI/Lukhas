# core/qrg/model.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class QRGSignature:
    algo: str
    pubkey_pem: str
    sig_b64: str
    ts: str
    payload_hash: str
    consent_hash: Optional[str] = None

    def to_dict(self):
        return {
            "algo": self.algo,
            "pubkey_pem": self.pubkey_pem,
            "sig_b64": self.sig_b64,
            "ts": self.ts,
            "payload_hash": self.payload_hash,
            "consent_hash": self.consent_hash,
        }
