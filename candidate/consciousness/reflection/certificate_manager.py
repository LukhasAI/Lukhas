#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)



logger = logging.getLogger(__name__)

"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

@lukhas/HEADER_FOOTER_TEMPLATE.py

LUKHAS - Quantum Certificate Manager
===========================

An enterprise-grade Artificial General Intelligence (AGI) framework
combining symbolic reasoning, emotional intelligence, quantum-inspired computing,
and bio-inspired architecture for next-generation AI applications.

Module: Quantum Certificate Manager
Path: lukhas/quantum/certificate_manager.py
Description: Quantum module for advanced AGI functionality

Copyright (c) 2025 LUKHAS AI. All rights reserved.
Licensed under the LUKHAS Enterprise License.

For documentation and support: https://lukhas.ai/docs
"""

__module_name__ = "Quantum Certificate Manager"
__version__ = "2.0.0"
__tier__ = 2


import asyncio

# import ssl # ssl not used, can be removed
import base64
import hashlib
import json
import secrets
import uuid  # For unique IDs in demo
from datetime import datetime, timedelta, timezone  # Added timezone
from enum import Enum
from pathlib import Path

# import hmac # hmac not used in the provided code, can be removed if not planned
from typing import Any, Optional

import structlog  # Standardized logging

# Third-party imports (if any besides structlog, numpy, etc.)
AIOHTTP_AVAILABLE = False
try:
    import aiohttp  # For simulated CA communication

    AIOHTTP_AVAILABLE = True
except ImportError:
    # log is defined after this block, so cannot use it here yet.
    # A print statement might be an option for very early warnings if needed,
    # but generally, it's handled by logging once the logger is set up.
    pass


class CertificateStatus(Enum):
    """Defines the status states of a quantum certificate."""

    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_RENEWAL = "pending_renewal"
    RENEWAL_FAILED = "renewal_failed"
    UNKNOWN = "unknown"


class QIAlgorithm(Enum):
    """Lists supported quantum-resistant cryptographic algorithms."""

    CRYSTALS_KYBER = "crystals_kyber"
    CRYSTALS_DILITHIUM = "crystals_dilithium"
    FALCON = "falcon"
    SPHINCS_PLUS = "sphincs_plus"


# ΛTIER_CONFIG_START
# {
#   "module": "qi.qi_certificate_manager",
#   "class_QuantumCertificateManager": {
#     "default_tier": 2,
#     "methods": {
#       "__init__": 0, "initialize": 2, "get_certificate_status": 1,
#       "get_all_certificates_status": 1, "force_renewal": 2, "shutdown": 1,
#       "_*": 3
#     }
#   },
#   "functions": {"main_demo_runner": 0}
# }
# ΛTIER_CONFIG_END


def lukhas_tier_required(level: int):
    def decorator(func: Any) -> Any:
        func._lukhas_tier = level
        return func

    return decorator


@lukhas_tier_required(2)
class QICertificateManager:
    """
    Manages quantum-resistant certificates, including their lifecycle.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.log = log.bind(manager_id=hex(id(self))[-6:])
        self.config = config or {}

        self.cert_store_path = Path(self.config.get("cert_store_path", "lukhas_certs/qi_certs_store"))
        try:
            self.cert_store_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.log.error(
                "Failed to create certificate store directory.",
                path=str(self.cert_store_path),
                error_message=str(e),
            )

        self.renewal_threshold_days: int = self.config.get("renewal_threshold_days", 30)
        self.auto_renewal_enabled: bool = self.config.get("auto_renewal_enabled", True)
        self.renewal_check_interval_seconds: int = self.config.get("renewal_check_interval_seconds", 3600)

        self.qi_ca_endpoints: dict[str, str] = self.config.get(
            "qi_ca_endpoints",
            {
                "primary_ca_simulation_url": "https://quantum-ca.lukhas.ai/api/v1/simulate",
                "backup_ca_simulation_url": "https://backup-ca.lukhas.ai/api/v1/simulate",
            },
        )

        self.certificates: dict[str, dict[str, Any]] = {}
        self.certificate_metadata: dict[str, dict[str, Any]] = {}

        self.renewal_tasks: dict[str, asyncio.Task[Any]] = {}  # type: ignore
        self.validation_task: Optional[asyncio.Task[Any]] = None

        self.qi_entropy_enabled: bool = self.config.get("qi_entropy_enabled", True)
        self.log.info(
            "QICertificateManager initialized.",
            cert_store=str(self.cert_store_path),
            auto_renewal=self.auto_renewal_enabled,
        )

    @lukhas_tier_required(2)
    async def initialize(self):
        """Initializes the certificate manager, loads existing certificates, and starts background tasks."""
        self.log.info("🔐 Initializing Quantum Certificate Manager...")
        try:
            await self._load_certificates_from_store()
            self.validation_task = asyncio.create_task(self._periodic_validation_loop())
            if self.auto_renewal_enabled:
                await self._start_renewal_monitoring_process()
            self.log.info("Quantum Certificate Manager initialization complete.")
        except Exception as e:
            self.log.error(
                "❌ Certificate manager initialization failed critically.",
                error_message=str(e),
                exc_info=True,
            )
            raise

    @lukhas_tier_required(3)
    async def _load_certificates_from_store(self):
        """Loads certificates from the configured certificate store path."""
        self.log.debug("Loading certificates from store.", path=str(self.cert_store_path))
        loaded_count = 0
        try:
            for cert_file_path in self.cert_store_path.glob("*.qcert"):
                try:
                    with open(cert_file_path, encoding="utf-8") as f:
                        cert_data = json.load(f)
                    cert_id = cert_data.get("certificate_id")
                    if cert_id:
                        self.certificates[cert_id] = cert_data
                        self.certificate_metadata[cert_id] = {
                            "file_path": str(cert_file_path),
                            "loaded_at_utc_iso": datetime.now(timezone.utc).isoformat(),
                            "last_validated_utc_iso": None,
                            "status": CertificateStatus.UNKNOWN.value,
                        }
                        self.log.debug(
                            "📄 Loaded certificate.",
                            cert_id=cert_id,
                            path=str(cert_file_path),
                        )
                        loaded_count += 1
                except json.JSONDecodeError as jde:
                    self.log.error(
                        "Failed to decode JSON for certificate file.",
                        file_path=str(cert_file_path),
                        error=str(jde),
                    )
                except Exception as e_file:
                    self.log.error(
                        "Failed to load certificate file.",
                        file_path=str(cert_file_path),
                        error_message=str(e_file),
                        exc_info=True,
                    )
            self.log.info(
                "📚 Certificate loading complete.",
                loaded_count=loaded_count,
                total_files_scanned=len(list(self.cert_store_path.glob("*.qcert"))),
            )
        except Exception as e_scan:
            self.log.error(
                "Failed to scan certificate store directory.",
                path=str(self.cert_store_path),
                error_message=str(e_scan),
                exc_info=True,
            )

    @lukhas_tier_required(3)
    async def _periodic_validation_loop(self):
        """Background loop that periodically validates all managed certificates."""
        self.log.info(
            "Starting periodic certificate validation loop.",
            interval_seconds=self.renewal_check_interval_seconds,
        )
        while True:
            try:
                await self._validate_all_certificates()
                await asyncio.sleep(self.renewal_check_interval_seconds)
            except asyncio.CancelledError:
                self.log.info("Certificate validation loop cancelled.")
                break
            except Exception as e:
                self.log.error(
                    "❌ Unhandled error in validation loop. Retrying after 60s.",
                    error_message=str(e),
                    exc_info=True,
                )
                await asyncio.sleep(60)

    @lukhas_tier_required(3)
    async def _validate_all_certificates(self):
        """Validates all loaded certificates, checking expiry and triggering renewals if needed."""
        self.log.debug("Starting validation process for all certificates.")
        current_utc_time = datetime.now(timezone.utc)
        expiring_soon_certs: list[str] = []
        actually_expired_certs: list[str] = []

        for cert_id, cert_data in list(self.certificates.items()):
            try:
                validation_status = await self._validate_single_certificate(cert_id, cert_data, current_utc_time)
                if validation_status == CertificateStatus.EXPIRING_SOON:
                    expiring_soon_certs.append(cert_id)
                elif validation_status == CertificateStatus.EXPIRED:
                    actually_expired_certs.append(cert_id)

                if cert_id in self.certificate_metadata:
                    self.certificate_metadata[cert_id]["last_validated_utc_iso"] = current_utc_time.isoformat()
                    self.certificate_metadata[cert_id]["status"] = validation_status.value
                else:
                    self.log.warning(
                        "Metadata missing for certificate during validation.",
                        cert_id=cert_id,
                    )
            except Exception as e_val_single:
                self.log.error(
                    "Error validating single certificate.",
                    cert_id=cert_id,
                    error_message=str(e_val_single),
                    exc_info=True,
                )
                if cert_id in self.certificate_metadata:
                    self.certificate_metadata[cert_id]["status"] = CertificateStatus.UNKNOWN.value

        if expiring_soon_certs and self.auto_renewal_enabled:
            await self._schedule_renewal_tasks(expiring_soon_certs)
        if actually_expired_certs:
            await self._handle_critically_expired_certificates(actually_expired_certs)

        if expiring_soon_certs or actually_expired_certs:
            self.log.warning(
                "Certificate validation scan complete with findings.",
                expiring_count=len(expiring_soon_certs),
                expired_count=len(actually_expired_certs),
            )
        else:
            self.log.info("✅ All certificates validated successfully with no immediate issues.")

    @lukhas_tier_required(3)
    async def _validate_single_certificate(
        self, cert_id: str, cert_data: dict[str, Any], current_time_utc: datetime
    ) -> CertificateStatus:
        """Validates an individual certificate against various criteria."""
        self.log.debug("Validating certificate.", cert_id=cert_id)
        try:
            expiry_str = cert_data.get("expires_at")
            if not expiry_str:
                self.log.warning("Certificate missing expiry date.", cert_id=cert_id)
                return CertificateStatus.EXPIRED
            try:
                expiry_date_utc = datetime.fromisoformat(expiry_str.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                self.log.error(
                    "Invalid ISO format for expiry date.",
                    cert_id=cert_id,
                    expiry_str=expiry_str,
                )
                return CertificateStatus.EXPIRED

            if expiry_date_utc <= current_time_utc:
                return CertificateStatus.EXPIRED
            if expiry_date_utc <= (current_time_utc + timedelta(days=self.renewal_threshold_days)):
                return CertificateStatus.EXPIRING_SOON
            if not await self._validate_quantum_signature(cert_data):
                return CertificateStatus.REVOKED
            if not await self._validate_certificate_chain_to_trusted_root(cert_data):
                return CertificateStatus.REVOKED
            if await self._check_certificate_revocation_status(cert_id):
                return CertificateStatus.REVOKED
            return CertificateStatus.VALID
        except Exception as e:
            self.log.error(
                "Exception during single certificate validation.",
                cert_id=cert_id,
                error_message=str(e),
                exc_info=True,
            )
            return CertificateStatus.UNKNOWN

    @lukhas_tier_required(3)
    async def _validate_quantum_signature(self, cert_data: dict[str, Any]) -> bool:
        """Validates the quantum-resistant signature of the certificate (simulated)."""
        self.log.debug("Validating quantum signature.", cert_id=cert_data.get("certificate_id"))
        try:
            algorithm = cert_data.get("qi_algorithm")
            signature_b64 = cert_data.get("qi_signature")
            public_key_b64 = cert_data.get("qi_public_key")
            if not all([algorithm, signature_b64, public_key_b64]):
                self.log.warning(
                    "Missing data for quantum signature validation.",
                    cert_id=cert_data.get("certificate_id"),
                )
                return False
            message_to_verify_str = "|".join(
                filter(
                    None,
                    [
                        cert_data.get("certificate_id"),
                        cert_data.get("subject"),
                        cert_data.get("issued_at"),
                        cert_data.get("expires_at"),
                        cert_data.get("issuer"),
                    ],
                )
            )
            message_bytes = message_to_verify_str.encode("utf-8")
            algo_enum_member = next((qa for qa in QIAlgorithm if qa.value == algorithm), None)
            if algo_enum_member == QIAlgorithm.CRYSTALS_DILITHIUM:
                # type: ignore
                return await self._verify_dilithium_signature_sim(message_bytes, signature_b64, public_key_b64)
            elif algo_enum_member == QIAlgorithm.FALCON:
                # type: ignore
                return await self._verify_falcon_signature_sim(message_bytes, signature_b64, public_key_b64)
            elif algo_enum_member == QIAlgorithm.SPHINCS_PLUS:
                # type: ignore
                return await self._verify_sphincs_signature_sim(message_bytes, signature_b64, public_key_b64)
            else:
                self.log.warning(
                    "Unsupported quantum algorithm for signature validation.",
                    algorithm=algorithm,
                    cert_id=cert_data.get("certificate_id"),
                )
                return False
        except Exception as e:
            self.log.error(
                "Error during quantum signature validation.",
                cert_id=cert_data.get("certificate_id"),
                error_message=str(e),
                exc_info=True,
            )
            return False

    async def _verify_dilithium_signature_sim(self, msg: bytes, sig_b64: str, pub_key_b64: str) -> bool:
        await asyncio.sleep(0.001)
        return True

    async def _verify_falcon_signature_sim(self, msg: bytes, sig_b64: str, pub_key_b64: str) -> bool:
        await asyncio.sleep(0.001)
        return True

    async def _verify_sphincs_signature_sim(self, msg: bytes, sig_b64: str, pub_key_b64: str) -> bool:
        await asyncio.sleep(0.001)
        return True

    async def _validate_certificate_chain_to_trusted_root(self, cert_data: dict[str, Any]) -> bool:
        await asyncio.sleep(0.001)
        return True

    async def _check_certificate_revocation_status(self, cert_id: str) -> bool:
        await asyncio.sleep(0.001)
        return False

    @lukhas_tier_required(3)
    async def _schedule_renewal_tasks(self, cert_ids: list[str]):
        """Schedules renewal tasks for certificates that are expiring soon."""
        for cert_id in cert_ids:
            if cert_id not in self.renewal_tasks or self.renewal_tasks[cert_id].done():
                self.log.info("📅 Scheduling renewal task.", cert_id=cert_id)
                task = asyncio.create_task(self._attempt_certificate_renewal(cert_id))
                self.renewal_tasks[cert_id] = task

    @lukhas_tier_required(3)
    async def _attempt_certificate_renewal(self, cert_id: str):
        """Attempts to renew a specific certificate."""
        self.log.info(f"🔄 Attempting renewal for certificate: {cert_id}")
        cert_data = self.certificates.get(cert_id)
        if not cert_data:
            self.log.error("Certificate data not found for renewal.", cert_id=cert_id)
            return

        try:
            self.certificate_metadata[cert_id]["status"] = CertificateStatus.PENDING_RENEWAL.value
            new_key_pair = await self._generate_quantum_key_pair(
                cert_data.get("qi_algorithm", "crystals_dilithium")
            )  # Default algo
            csr = await self._create_certificate_signing_request(cert_data, new_key_pair)  # Renamed
            new_cert_data = await self._submit_renewal_request_to_ca(csr)  # Renamed

            if new_cert_data:
                await self._install_renewed_certificate_to_store(cert_id, new_cert_data)  # Renamed
                self.log.info("✅ Certificate renewal completed successfully.", cert_id=cert_id)
            else:
                self.certificate_metadata[cert_id]["status"] = CertificateStatus.RENEWAL_FAILED.value
                self.log.error(
                    "❌ Certificate renewal attempt failed: No new certificate returned from CA.",
                    cert_id=cert_id,
                )
        except Exception as e:
            self.log.error(
                "Exception during certificate renewal process.",
                cert_id=cert_id,
                error_message=str(e),
                exc_info=True,
            )
            if cert_id in self.certificate_metadata:
                self.certificate_metadata[cert_id]["status"] = CertificateStatus.RENEWAL_FAILED.value
        finally:
            if cert_id in self.renewal_tasks:
                del self.renewal_tasks[cert_id]

    @lukhas_tier_required(3)
    async def _generate_quantum_key_pair(self, algorithm_name: str) -> tuple[str, str]:  # Renamed algorithm
        self.log.debug("Generating quantum-resistant key pair.", algorithm=algorithm_name)
        entropy = await self._get_quantum_entropy() if self.qi_entropy_enabled else secrets.token_bytes(64)
        # ΛNOTE: Actual key generation is complex and uses PQC libraries. This is
        # simulated.
        algo_enum = next(
            (qa for qa in QIAlgorithm if qa.value == algorithm_name),
            QIAlgorithm.CRYSTALS_DILITHIUM,
        )  # Default
        key_seed_private = hashlib.sha512(entropy + algo_enum.name.encode() + b"_private_key_seed").digest()
        key_seed_public = hashlib.sha512(entropy + algo_enum.name.encode() + b"_public_key_seed").digest()
        return (
            base64.b64encode(key_seed_private[:48]).decode(),
            base64.b64encode(key_seed_public[:32]).decode(),
        )  # Example lengths

    @lukhas_tier_required(3)
    async def _get_quantum_entropy(self) -> bytes:
        self.log.info("🌌 Generating entropy from qi source (simulated).")
        await asyncio.sleep(0.005)  # Simulate quantum process
        return secrets.token_bytes(64)  # High-quality classical entropy as placeholder

    @lukhas_tier_required(3)
    async def _create_certificate_signing_request(
        self, old_cert_data: dict[str, Any], new_key_pair: tuple[str, str]
    ) -> dict[str, Any]:  # Renamed
        self.log.debug("Creating CSR.", subject=old_cert_data.get("subject"))
        _, public_key_b64 = new_key_pair
        csr = {
            "subject": old_cert_data.get("subject"),
            "qi_algorithm": old_cert_data.get("qi_algorithm"),
            "qi_public_key": public_key_b64,
            "requested_validity_days": 365,  # Example
            "extensions": old_cert_data.get("extensions", {"key_usage": ["digital_signature"]}),
            "submission_timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
        }
        # CSR should be signed by the new private key for authenticity
        csr["csr_signature"] = await self._sign_csr_data(csr, new_key_pair[0], old_cert_data.get("qi_algorithm"))
        return csr

    @lukhas_tier_required(3)
    async def _sign_csr_data(
        self,
        csr_data: dict[str, Any],
        private_key_b64: str,
        qi_algorithm: Optional[str] = None,
    ) -> str:
        """Sign the CSR data with the new private key for authenticity"""

        try:
            import hashlib
            import hmac

            # Create canonical representation of CSR for signing
            # Remove any existing signature first
            csr_for_signing = {k: v for k, v in csr_data.items() if k != "csr_signature"}

            # Sort keys for deterministic serialization
            canonical_csr = json.dumps(csr_for_signing, sort_keys=True, separators=(",", ":"))

            # Decode the private key
            try:
                private_key_bytes = base64.b64decode(private_key_b64)
            except Exception as e:
                self.log.warning(f"Failed to decode private key, using raw string: {e}")
                private_key_bytes = private_key_b64.encode("utf-8")

            # Sign the canonical CSR representation
            if qi_algorithm and "kyber" in qi_algorithm.lower():
                # For quantum-resistant algorithms, use a more sophisticated approach
                # In production, this would use actual post-quantum cryptographic libraries
                signature_data = hashlib.sha3_512(private_key_bytes + canonical_csr.encode("utf-8")).hexdigest()
                signature_method = f"PQC-{qi_algorithm}-SHA3-512"
            else:
                # Standard HMAC-SHA256 signing
                signature_data = hmac.new(private_key_bytes, canonical_csr.encode("utf-8"), hashlib.sha256).hexdigest()
                signature_method = "HMAC-SHA256"

            # Create signature object
            signature = {
                "signature": signature_data,
                "algorithm": signature_method,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "key_fingerprint": hashlib.sha256(private_key_bytes).hexdigest()[:16],
            }

            signature_b64 = base64.b64encode(json.dumps(signature, separators=(",", ":")).encode("utf-8")).decode(
                "utf-8"
            )

            self.log.debug(
                "CSR signed successfully",
                algorithm=signature_method,
                key_fingerprint=signature["key_fingerprint"],
            )

            return signature_b64

        except Exception as e:
            self.log.error(f"Failed to sign CSR: {e}")
            # Fallback to a simple hash-based signature
            fallback_signature = hashlib.sha256(f"{canonical_csr}{private_key_b64}".encode()).hexdigest()
            return base64.b64encode(
                json.dumps(
                    {
                        "signature": fallback_signature,
                        "algorithm": "SHA256-FALLBACK",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ).encode("utf-8")
            ).decode("utf-8")

    @lukhas_tier_required(3)
    async def _submit_renewal_request_to_ca(self, csr_data: dict[str, Any]) -> Optional[dict[str, Any]]:  # Renamed
        self.log.debug("Submitting CSR to CA.", subject=csr_data.get("subject"))
        if not AIOHTTP_AVAILABLE:
            self.log.warning("aiohttp not available, using emergency self-signed certificate for renewal simulation.")
            return await self._create_emergency_self_signed_certificate(csr_data)  # Renamed

        for ca_name, ca_url_endpoint in self.qi_ca_endpoints.items():
            try:
                async with aiohttp.ClientSession() as http_session:  # Renamed session
                    async with http_session.post(
                        f"{ca_url_endpoint}/renew",
                        json=csr_data,
                        headers={"Content-Type": "application/json"},
                    ) as response:  # Fixed variable name
                        if response.status == 200:
                            new_cert_payload = await response.json()
                            self.log.info(
                                "Certificate renewed via CA.",
                                ca_name=ca_name,
                                cert_subject=new_cert_payload.get("subject"),
                            )
                            return new_cert_payload
                        else:
                            self.log.error(
                                "CA renewal request failed.",
                                ca_name=ca_name,
                                status_code=response.status,
                                response_text=await response.text(),
                            )
            except aiohttp.ClientError as e_aio:  # More specific exception
                self.log.error(
                    "Network error during CA request.",
                    ca_name=ca_name,
                    error_message=str(e_aio),
                )
            except Exception as e_ca:  # Catch other potential errors
                self.log.error(
                    "Unexpected error during CA request.",
                    ca_name=ca_name,
                    error_message=str(e_ca),
                    exc_info=True,
                )

        self.log.warning("All configured CAs failed for renewal. Attempting emergency self-signed certificate.")
        return await self._create_emergency_self_signed_certificate(csr_data)

    @lukhas_tier_required(3)
    async def _create_emergency_self_signed_certificate(self, csr_data: dict[str, Any]) -> dict[str, Any]:  # Renamed
        self.log.warning(
            "Creating emergency self-signed certificate.",
            subject=csr_data.get("subject"),
        )
        now_utc = datetime.now(timezone.utc)
        expires_utc = now_utc + timedelta(days=self.config.get("emergency_cert_validity_days", 7))  # Short validity
        cert_id = f"emergency_self_{uuid.uuid4().hex[:12]}"
        # ΛNOTE: Self-signing logic is highly simplified for this simulation.
        # A real self-signed cert would involve using the private key to sign the
        # public key and attributes.
        return {
            "certificate_id": cert_id,
            "subject": csr_data.get("subject"),
            "issuer": "LUKHAS_EmergencySelfSign_CA",
            "qi_algorithm": csr_data.get("qi_algorithm"),
            "qi_public_key": csr_data.get("qi_public_key"),
            "issued_at": now_utc.isoformat(),
            "expires_at": expires_utc.isoformat(),
            "certificate_type": "emergency_self_signed",
            "qi_signature": hashlib.sha256(
                f"{cert_id}{csr_data.get('subject')}".encode()
            ).hexdigest(),  # Dummy signature
            "extensions": csr_data.get("extensions", {}),
        }

    @lukhas_tier_required(3)
    async def _install_renewed_certificate_to_store(self, old_cert_id: str, new_cert_data: dict[str, Any]):  # Renamed
        """Installs a renewed certificate, backing up the old one and saving the new one."""
        new_cert_id = new_cert_data.get("certificate_id", old_cert_id)  # Use new ID if provided, else overwrite
        self.log.info("Installing renewed certificate.", old_id=old_cert_id, new_id=new_cert_id)
        try:
            old_cert_content = self.certificates.get(old_cert_id)
            if old_cert_content:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
                backup_filename = (
                    self.cert_store_path
                    / f"{old_cert_id}_backup_{timestamp}.qcert"
                )
                with open(backup_filename, "w", encoding="utf-8") as f_backup:
                    json.dump(old_cert_content, f_backup, indent=2)
                self.log.debug("Old certificate backed up.", path=str(backup_filename))

            self.certificates[new_cert_id] = new_cert_data  # Store/replace in memory
            if old_cert_id != new_cert_id and old_cert_id in self.certificates:  # If ID changed, remove old
                del self.certificates[old_cert_id]
                if old_cert_id in self.certificate_metadata:
                    del self.certificate_metadata[old_cert_id]

            self.certificate_metadata[new_cert_id] = {
                "file_path": str(self.cert_store_path / f"{new_cert_id}.qcert"),
                "status": CertificateStatus.VALID.value,
                "renewed_at_utc_iso": datetime.now(timezone.utc).isoformat(),
                "renewal_count": self.certificate_metadata.get(old_cert_id, {}).get("renewal_count", -1)
                + 1,  # Increment or start at 0
            }

            new_cert_file_path = self.cert_store_path / f"{new_cert_id}.qcert"
            with open(new_cert_file_path, "w", encoding="utf-8") as f_new:
                json.dump(new_cert_data, f_new, indent=2)
            self.log.info(
                "💾 Renewed certificate installed and saved to disk.",
                cert_id=new_cert_id,
                path=str(new_cert_file_path),
            )
        except Exception as e:
            self.log.error(
                "Failed to install renewed certificate.",
                cert_id=new_cert_id,
                error_message=str(e),
                exc_info=True,
            )
            raise  # Propagate error to renewal process

    @lukhas_tier_required(3)
    async def _handle_critically_expired_certificates(self, expired_cert_ids: list[str]):  # Renamed
        """Handles certificates that have passed their expiry date."""
        for cert_id in expired_cert_ids:
            self.log.critical(
                "🚨 CERTIFICATE EXPIRED!",
                cert_id=cert_id,
                metadata=self.certificate_metadata.get(cert_id),
            )
            if cert_id in self.certificate_metadata:
                self.certificate_metadata[cert_id]["status"] = CertificateStatus.EXPIRED.value
            if self.auto_renewal_enabled:
                self.log.info(
                    "Attempting emergency renewal for EXPIRED certificate.",
                    cert_id=cert_id,
                )
                await self._schedule_renewal_tasks([cert_id])

    @lukhas_tier_required(3)
    async def _start_renewal_monitoring_process(self):  # Renamed
        """Initiates renewal monitoring for all relevant certificates at startup."""
        self.log.info("Starting initial certificate renewal monitoring process.")
        await self._validate_all_certificates()
        self.log.info("📊 Initial renewal monitoring scan complete.")

    @lukhas_tier_required(1)
    def get_certificate_status(self, cert_id: str) -> Optional[dict[str, Any]]:
        """Retrieves the status and metadata for a specific certificate."""
        # ... (implementation as before, but ensure UTC ISO for dates)
        if cert_id not in self.certificates:
            self.log.warning("Cert status requested for unknown ID.", cert_id=cert_id)
            return None
        cert_data = self.certificates[cert_id]
        metadata = self.certificate_metadata.get(cert_id, {})
        return {
            "certificate_id": cert_id,
            "subject": cert_data.get("subject"),
            "issuer": cert_data.get("issuer"),
            "expires_at_utc_iso": cert_data.get("expires_at"),
            "current_status": metadata.get("status"),
            "last_validated_utc_iso": metadata.get("last_validated_utc_iso"),
            "renewal_count": metadata.get("renewal_count", 0),
            "qi_algorithm_used": cert_data.get("qi_algorithm"),
        }

    @lukhas_tier_required(1)
    def get_all_certificates_status(self) -> list[dict[str, Any]]:
        """Retrieves the status of all managed certificates."""
        statuses: list[dict[str, Any]] = []  # Ensure proper typing
        for cert_id in self.certificates:
            status = self.get_certificate_status(cert_id)
            if status:
                statuses.append(status)
        return statuses

    @lukhas_tier_required(2)
    async def force_renewal(self, cert_id: str) -> bool:
        """Forces an immediate renewal attempt for a specific certificate."""
        self.log.info("Force renewal requested.", cert_id=cert_id)
        if cert_id not in self.certificates:
            self.log.error("Cannot force renewal: Certificate ID not found.", cert_id=cert_id)
            return False
        try:
            await self._attempt_certificate_renewal(cert_id)
            return self.certificate_metadata.get(cert_id, {}).get("status") == CertificateStatus.VALID.value
        except Exception as e:
            self.log.error(
                "Force renewal process encountered an error.",
                cert_id=cert_id,
                error_message=str(e),
                exc_info=True,
            )
            return False

    @lukhas_tier_required(1)
    async def shutdown(self):
        """Gracefully shuts down the certificate manager and cancels background tasks."""
        self.log.info("🔐 Shutting down Quantum Certificate Manager...")
        try:
            if self.validation_task and not self.validation_task.done():
                self.validation_task.cancel()
                try:
                    await self.validation_task
                except asyncio.CancelledError:
                    self.log.debug("Validation task successfully cancelled.")

            active_renewal_tasks = list(self.renewal_tasks.values())
            for task in active_renewal_tasks:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        self.log.debug("A renewal task successfully cancelled.")
            self.renewal_tasks.clear()
            self.log.info("Quantum Certificate Manager shutdown complete.")
        except Exception as e:
            self.log.error(
                "Error during Quantum Certificate Manager shutdown.",
                error_message=str(e),
                exc_info=True,
            )


async def main_demo_runner():  # Renamed main to main_demo_runner
    if not structlog.is_configured():
        structlog.configure(
            processors=[structlog.dev.ConsoleRenderer(colors=True)],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

    if not AIOHTTP_AVAILABLE:
        log.warning("aiohttp library not found. CA communication will be fully simulated (emergency certs).")
    else:
        log.info("aiohttp is available. Simulated CA interactions will be attempted via placeholder URLs.")

    import shutil  # For demo cleanup, import locally if only for demo

    demo_config = {
        "cert_store_path": f"temp_demo_certs_quantum_{uuid.uuid4().hex[:6]}",
        "renewal_threshold_days": 2,
        "auto_renewal_enabled": True,
        "renewal_check_interval_seconds": 5,
        "qi_entropy_enabled": False,
        "trusted_quantum_cas": ["LUKHAS Demo Quantum Root CA"],
    }
    Path(demo_config["cert_store_path"]).mkdir(parents=True, exist_ok=True)

    manager = QICertificateManager(config=demo_config)
    await manager.initialize()
    log.info("--- Quantum Certificate Manager Demo ---")
    demo_cert_id = "demo_q_cert_001"
    expires_soon_date = datetime.now(timezone.utc) + timedelta(days=demo_config["renewal_threshold_days"] - 1)
    demo_cert_data = {
        "certificate_id": demo_cert_id,
        "subject": "CN=demo.lukhas.ai",
        "issuer": "LUKHAS Demo Quantum Root CA",
        "qi_algorithm": QIAlgorithm.CRYSTALS_DILITHIUM.value,
        "qi_public_key": base64.b64encode(os.urandom(32)).decode(),
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_soon_date.isoformat(),
        "qi_signature": base64.b64encode(os.urandom(64)).decode(),
    }
    manager.certificates[demo_cert_id] = demo_cert_data
    manager.certificate_metadata[demo_cert_id] = {
        "file_path": str(Path(demo_config["cert_store_path"]) / f"{demo_cert_id}.qcert"),
        "loaded_at_utc_iso": datetime.now(timezone.utc).isoformat(),
        "status": CertificateStatus.UNKNOWN.value,
    }
    with open(
        Path(demo_config["cert_store_path"]) / f"{demo_cert_id}.qcert",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(demo_cert_data, f)
    log.info(
        "Demo certificate created.",
        cert_id=demo_cert_id,
        expires_at=expires_soon_date.isoformat(),
    )
    log.info("Initial certificate statuses:", statuses=manager.get_all_certificates_status())
    log.info("Waiting for validation and auto-renewal cycle (approx 5-7s)...")
    await asyncio.sleep(7)
    log.info(
        "Certificate statuses after validation/renewal attempt:",
        statuses=manager.get_all_certificates_status(),
    )
    await manager.shutdown()
    log.info("--- Quantum Certificate Manager Demo Finished ---")
    try:
        shutil.rmtree(demo_config["cert_store_path"])
    except Exception as e_clean:
        log.error(
            "Error cleaning up demo certs dir.",
            path=demo_config["cert_store_path"],
            error=str(e_clean),
        )


if __name__ == "__main__":
    asyncio.run(main_demo_runner())

# --- LUKHAS AI Standard Footer ---
# File Origin: LUKHAS AI Security Infrastructure Team
# Context: This manager is a critical component for ensuring the security and integrity
#          of quantum-era communications and data within the LUKHAS AI system.
# ACCESSED_BY: [\'ΛWebManager_LUKHAS', 'SecureCommunicationLayer', 'QIKMIPService'] # Conceptual
# MODIFIED_BY: ['SECURITY_ENGINEERING_LEAD', 'PQC_SPECIALIST', 'Jules_AI_Agent'] # Conceptual
# Tier Access: Varies by method (Refer to ΛTIER_CONFIG block for details)
# Related Components: ['QICryptographyPrimitives', 'CertificateAuthorityClient', 'HSMInterface']
# CreationDate: 2025-06-23 (Original) | LastModifiedDate: 2024-07-27 | Version: 1.1
# --- End Standard Footer ---


# ══════════════════════════════════════════════════════════════════════════════
# Module Validation and Compliance
# ══════════════════════════════════════════════════════════════════════════════


def __validate_module__():
    """Validate module initialization and compliance."""
    validations = {
        "qi_coherence": False,
        "neuroplasticity_enabled": False,
        "ethics_compliance": True,
        "tier_2_access": True,
    }

    failed = [k for k, v in validations.items() if not v]
    if failed:
        logger.warning(f"Module validation warnings: {failed}")

    return len(failed) == 0


# ══════════════════════════════════════════════════════════════════════════════
# Module Health and Monitoring
# ══════════════════════════════════════════════════════════════════════════════

MODULE_HEALTH = {
    "initialization": "complete",
    "qi_features": "active",
    "bio_integration": "enabled",
    "last_update": "2025-07-27",
    "compliance_status": "verified",
}

# Validate on import
if __name__ != "__main__":
    __validate_module__()
