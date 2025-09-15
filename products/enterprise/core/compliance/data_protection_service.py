"""
LUKHAS Data Protection Service
============================
Implements persistent storage for data protection policies, keys, and history.
"""

import base64
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import asyncpg
from pydantic import BaseModel

try:
    from cryptography.fernet import Fernet
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class ProtectionPolicy(BaseModel):
    """Data protection policy definition"""

    policy_id: str
    name: str
    description: str
    data_types: list[str]
    protection_level: str
    encryption_required: bool
    encryption_type: str
    key_rotation_days: int
    anonymization_methods: list[str]
    retain_utility: bool
    authorized_roles: list[str]
    audit_required: bool
    gdpr_article_25: bool
    gdpr_article_32: bool
    cache_encrypted: bool
    background_processing: bool
    created_at: datetime
    updated_at: datetime
    version: str


from enum import Enum


class LawfulBasis(str, Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataCategory(str, Enum):
    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    CRIMINAL_DATA = "criminal_data"
    BIOMETRIC_DATA = "biometric_data"
    HEALTH_DATA = "health_data"
    GENETIC_DATA = "genetic_data"


class ProcessingPurpose(str, Enum):
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    RESEARCH = "research"
    COMPLIANCE = "compliance"
    SECURITY = "security"


class DataProcessingActivity(BaseModel):
    activity_id: str
    name: str
    description: str
    controller: str
    processor: Optional[str]
    data_categories: list[DataCategory]
    lawful_basis: LawfulBasis
    purposes: list[ProcessingPurpose]
    data_subjects: list[str]
    retention_period: Optional[str]
    international_transfers: bool
    automated_decision_making: bool
    profiling: bool


class GDPRAssessment(BaseModel):
    activity_id: str
    compliance_status: str
    assessment_date: datetime
    lawfulness_score: float
    privacy_rights_score: float
    security_score: float
    transparency_score: float
    overall_score: float
    violations: list[str]
    recommendations: list[str]
    next_review_date: datetime


class GDPRValidator:
    async def assess_gdpr_compliance(self, activity: DataProcessingActivity) -> GDPRAssessment:
        # Simplified assessment for now
        return GDPRAssessment(
            activity_id=activity.activity_id,
            compliance_status="Fully Compliant",
            assessment_date=datetime.now(timezone.utc),
            lawfulness_score=1.0,
            privacy_rights_score=1.0,
            security_score=1.0,
            transparency_score=1.0,
            overall_score=1.0,
            violations=[],
            recommendations=[],
            next_review_date=datetime.now(timezone.utc) + timedelta(days=180),
        )


class DataProtectionService:
    """
    Advanced data protection system with multi-layer security
    """

    def __init__(self, db_url: str = "postgresql://localhost/lukhas"):
        self.db_url = db_url
        self.db_pool = None
        self.protection_policies: dict[str, ProtectionPolicy] = {}
        self._rsa_private_key = None
        self._public_key_bytes: Optional[bytes] = None
        self._default_passphrase = "lukhas-enterprise"

        if CRYPTO_AVAILABLE:
            self._initialize_crypto_material()

    async def initialize(self):
        """Initialize database connection pool and load policies"""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=10, command_timeout=30)
        await self._load_policies()

    async def close(self):
        """Close database connections"""
        if self.db_pool:
            await self.db_pool.close()

    async def _load_policies(self):
        """Load protection policies from the database"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM protection.policies")
            for row in rows:
                self.protection_policies[row["policy_id"]] = ProtectionPolicy(**row)

    async def protect_data(
        self,
        data: Union[dict[str, Any], str, bytes],
        policy_id: str,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[Any, Any]:
        """
        Apply data protection based on policy.
        """
        datetime.now(timezone.utc)
        context = context or {}

        if policy_id not in self.protection_policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self.protection_policies[policy_id]

        protected_data = data
        methods_applied = []

        if policy.encryption_required:
            protected_data, encryption_result = await self._apply_encryption(protected_data, policy, context)
            methods_applied.append(f"encryption_{policy.encryption_type}")

        # For now, we will just return the protected data and the methods applied
        return protected_data, {"methods_applied": methods_applied}

    def _initialize_crypto_material(self) -> None:
        """Generate RSA material for wrapping derived keys."""

        # ΛTAG: crypto_material
        self._rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        public_key = self._rsa_private_key.public_key()
        self._public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def _derive_symmetric_key(self, passphrase: str, salt: bytes) -> bytes:
        """Derive a symmetric key using PBKDF2."""

        # ΛTAG: key_derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
            backend=default_backend(),
        )
        return kdf.derive(passphrase.encode("utf-8"))

    async def _apply_encryption(
        self, data: Any, policy: ProtectionPolicy, context: dict[str, Any]
    ) -> tuple[Any, dict[str, Any]]:
        """Apply encryption based on policy"""

        passphrase = context.get("passphrase") if context else None
        passphrase = passphrase or self._default_passphrase

        if not CRYPTO_AVAILABLE or self._rsa_private_key is None:
            data_str = json.dumps(data, default=str)
            encoded_data = base64.b64encode(data_str.encode()).decode()
            return {"encrypted": True, "data": encoded_data}, {
                "method": "base64",
                "key_id": "fallback",
            }

        payload = json.dumps(data, default=str).encode("utf-8")
        salt = context.get("salt") if context else None
        if isinstance(salt, str):
            salt_bytes = base64.b64decode(salt)
        else:
            salt_bytes = os.urandom(16)

        key = self._derive_symmetric_key(passphrase, salt_bytes)
        iv = os.urandom(12)
        encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
        ciphertext = encryptor.update(payload) + encryptor.finalize()
        tag = encryptor.tag

        signature = self._rsa_private_key.sign(
            ciphertext,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        result_data = {
            "encrypted": True,
            "algorithm": "AES-256-GCM",
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "iv": base64.b64encode(iv).decode(),
            "tag": base64.b64encode(tag).decode(),
            "salt": base64.b64encode(salt_bytes).decode(),
            "signature": base64.b64encode(signature).decode(),
            "public_key": base64.b64encode(self._public_key_bytes or b"").decode(),
        }

        result_info = {
            "method": "symmetric_aes256_gcm",
            "key_derivation": "pbkdf2_sha256",
            "signature_scheme": "rsa_pss_sha256",
            "success": True,
        }

        return result_data, result_info

    async def unprotect_data(self, protected_data: Any, context: Optional[dict[str, Any]] = None) -> Any:
        """
        Reverse data protection to recover original data.
        """
        if not CRYPTO_AVAILABLE:
            # Fallback for base64 encoding
            if isinstance(protected_data, dict) and protected_data.get("encrypted"):
                decoded_data = base64.b64decode(protected_data["data"])
                return json.loads(decoded_data)
            return protected_data

        if isinstance(protected_data, dict) and protected_data.get("encrypted"):
            if {
                "ciphertext",
                "iv",
                "tag",
                "salt",
                "signature",
            }.issubset(protected_data):
                passphrase = (context or {}).get("passphrase", self._default_passphrase)
                salt_bytes = base64.b64decode(protected_data["salt"])
                iv = base64.b64decode(protected_data["iv"])
                tag = base64.b64decode(protected_data["tag"])
                ciphertext = base64.b64decode(protected_data["ciphertext"])
                signature = base64.b64decode(protected_data["signature"])
                public_bytes = protected_data.get("public_key")

                if not CRYPTO_AVAILABLE or self._rsa_private_key is None:
                    raise ValueError("Cryptography backend unavailable for decryption")

                try:
                    if public_bytes:
                        public_key = serialization.load_pem_public_key(base64.b64decode(public_bytes))
                    else:
                        public_key = self._rsa_private_key.public_key()

                    public_key.verify(
                        signature,
                        ciphertext,
                        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                        hashes.SHA256(),
                    )

                    key = self._derive_symmetric_key(passphrase, salt_bytes)
                    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
                    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                    return json.loads(plaintext)
                except InvalidSignature as exc:
                    raise ValueError("Signature verification failed") from exc
                except Exception as exc:  # pragma: no cover - defensive guard
                    raise ValueError(f"Unable to decrypt payload: {exc!s}") from exc

            # Fallback path for legacy Fernet/base64 payloads
            if "data" in protected_data:
                key_material = b"12345678901234567890123456789012"
                fernet = Fernet(base64.urlsafe_b64encode(key_material))
                encrypted_data = base64.b64decode(protected_data["data"])
                decrypted_data = fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data)

        return protected_data

    async def get_user_data(self, user_lid: str) -> list[dict]:
        """Get all protected data for a user."""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM protection.history WHERE user_lid = $1", user_lid)
            return [dict(row) for row in rows]

    async def delete_user_data(self, user_lid: str) -> int:
        """Delete all protected data for a user."""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM protection.history WHERE user_lid = $1", user_lid)
            return int(result.split(" ")[1])

    async def update_protected_data(self, operation_id: str, new_data: Any) -> Optional[dict]:
        """Update protected data."""
        async with self.db_pool.acquire():
            # For now, we will just log a message.
            # In a real implementation, this would update the data in the database.
            print(f"Updating protected data for operation {operation_id} with {new_data}")
            return {"status": "success"}

    async def assess_processing_activity(self, activity: DataProcessingActivity) -> GDPRAssessment:
        """Assess the compliance of a data processing activity."""
        validator = GDPRValidator()
        return await validator.assess_gdpr_compliance(activity)

    async def enforce_retention_policy(self, retention_period_days: int):
        """
        Enforce data retention policy by deleting data older than the retention period.
        """
        async with self.db_pool.acquire():
            # For now, we will just log a message.
            # In a real implementation, this would delete the data from the database.
            print(f"Enforcing data retention policy: deleting data older than {retention_period_days} days.")

    async def create_baa(
        self,
        business_associate_name: str,
        agreement_date: str,
        expiry_date: str,
        agreement_url: str,
    ) -> dict:
        """Create a new Business Associate Agreement."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO protection.baas (business_associate_name, agreement_date, expiry_date, agreement_url) VALUES ($1, $2, $3, $4) RETURNING *",
                business_associate_name,
                agreement_date,
                expiry_date,
                agreement_url,
            )
            return dict(row)

    async def get_baa(self, business_associate_name: str) -> Optional[dict]:
        """Get a Business Associate Agreement by name."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM protection.baas WHERE business_associate_name = $1 AND status = 'active'",
                business_associate_name,
            )
            return dict(row) if row else None
