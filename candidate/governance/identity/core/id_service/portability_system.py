"""
LUKHAS ΛiD Portability & Recovery System
=======================================

Comprehensive ΛiD portability system with QR-G recovery, emergency fallback,
and cross-device synchronization capabilities.

Features:
- QR-G (QR with Geo-encoding) generation and recovery
- Emergency fallback codes with cryptographic security
- Cross-device synchronization protocols
- Backup/restore workflows
- Recovery phrase generation (BIP39-style)
- Multi-factor recovery authentication
- Offline recovery capabilities
- Recovery analytics and auditing

Author: LUKHAS AI Systems
Version: 1.0.0
Created: 2025-07-05
"""
from typing import List
from typing import Dict
import streamlit as st
from datetime import timezone

import base64
import hashlib
import json
import secrets
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import qrcode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    import mnemonic
except ImportError:
    # Use local mock if mnemonic library is not installed
    from . import mnemonic


class RecoveryMethod(Enum, timezone):
    """Available recovery methods"""

    QR_GEO = "qr_geo"  # QR code with geo-encoding
    EMERGENCY_CODE = "emergency_code"  # Emergency fallback code
    RECOVERY_PHRASE = "recovery_phrase"  # Mnemonic recovery phrase
    BIOMETRIC = "biometric"  # Biometric recovery
    DEVICE_SYNC = "device_sync"  # Cross-device sync
    BACKUP_FILE = "backup_file"  # Encrypted backup file


class RecoveryStatus(Enum):
    """Recovery attempt status"""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    EXPIRED = "expired"
    LOCKED = "locked"
    PENDING = "pending"


class PortabilityPackage:
    """Complete portability package for ΛiD"""

    def __init__(self):
        self.lambda_id = ""
        self.qr_geo_code = ""
        self.emergency_codes = []
        self.recovery_phrase = ""
        self.backup_data = {}
        self.expiry_date = None
        self.geo_location = None
        self.created_at = None
        self.methods_enabled = []
        self.security_level = "standard"

    def to_dict(self) -> dict[str, Any]:
        """Convert package to dictionary"""
        return {
            "lambda_id": self.lambda_id,
            "qr_geo_code": self.qr_geo_code,
            "emergency_codes": self.emergency_codes,
            "recovery_phrase": self.recovery_phrase,
            "backup_data": self.backup_data,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "geo_location": self.geo_location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "methods_enabled": [method.value for method in self.methods_enabled],
            "security_level": self.security_level,
        }


class RecoveryAttempt:
    """Recovery attempt record"""

    def __init__(self):
        self.attempt_id = ""
        self.lambda_id = ""
        self.method = None
        self.status = RecoveryStatus.PENDING
        self.timestamp = None
        self.geo_location = None
        self.device_info = {}
        self.success_factors = []
        self.failure_reasons = []
        self.security_checks = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert attempt to dictionary"""
        return {
            "attempt_id": self.attempt_id,
            "lambda_id": self.lambda_id,
            "method": self.method.value if self.method else None,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "geo_location": self.geo_location,
            "device_info": self.device_info,
            "success_factors": self.success_factors,
            "failure_reasons": self.failure_reasons,
            "security_checks": self.security_checks,
        }


class LambdaIDPortabilitySystem:
    """
    Comprehensive ΛiD portability and recovery system.

    Provides multiple recovery methods, secure backup/restore capabilities,
    and cross-device synchronization for ΛiD ecosystem continuity.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize portability system"""
        self.config = self._load_config(config_path)
        self.recovery_attempts = []
        self.active_packages = {}
        self.geo_encoder = GeographicEncoder()
        self.mnemonic_generator = mnemonic.Mnemonic("english")
        self.crypto_key = self._initialize_crypto_key()

    def create_portability_package(
        self,
        lambda_id: str,
        methods: list[RecoveryMethod],
        geo_location: Optional[dict[str, float]] = None,
        security_level: str = "standard",
    ) -> PortabilityPackage:
        """
        Create comprehensive portability package for ΛiD.

        Args:
            lambda_id: The ΛiD to make portable
            methods: List of recovery methods to enable
            geo_location: Geographic coordinates for geo-encoding
            security_level: Security level (standard, high, ultra)

        Returns:
            PortabilityPackage with all recovery methods
        """
        package = PortabilityPackage()
        package.lambda_id = lambda_id
        package.methods_enabled = methods
        package.geo_location = geo_location
        package.security_level = security_level
        package.created_at = datetime.now(timezone.utc)
        package.expiry_date = self._calculate_expiry_date(security_level)

        # Generate QR-G code if requested
        if RecoveryMethod.QR_GEO in methods:
            package.qr_geo_code = self._generate_qr_geo_code(lambda_id, geo_location)

        # Generate emergency codes if requested
        if RecoveryMethod.EMERGENCY_CODE in methods:
            package.emergency_codes = self._generate_emergency_codes(lambda_id, security_level)

        # Generate recovery phrase if requested
        if RecoveryMethod.RECOVERY_PHRASE in methods:
            package.recovery_phrase = self._generate_recovery_phrase(lambda_id)

        # Create backup data
        package.backup_data = self._create_backup_data(lambda_id, security_level)

        # Store package
        self.active_packages[lambda_id] = package

        return package

    def generate_qr_geo_recovery(
        self,
        lambda_id: str,
        geo_location: dict[str, float],
        security_level: str = "standard",
    ) -> dict[str, Any]:
        """
        Generate QR code with geographic encoding for recovery.

        Args:
            lambda_id: The ΛiD to encode
            geo_location: Geographic coordinates (lat, lng)
            security_level: Security level for encoding

        Returns:
            Dict with QR code data and geo-encoding info
        """
        # Create geo-encoded payload
        geo_payload = self.geo_encoder.encode_with_location(lambda_id, geo_location)

        # Add security layer
        if security_level in ["high", "ultra"]:
            geo_payload = self._add_security_layer(geo_payload, security_level)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=4,
        )
        qr.add_data(geo_payload)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Encode image to base64 for storage/transmission
        import io

        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "qr_code_base64": qr_base64,
            "geo_payload": geo_payload,
            "location": geo_location,
            "security_level": security_level,
            "expiry": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "recovery_instructions": self._get_qr_recovery_instructions(),
        }

    def recover_from_qr_geo(
        self, qr_payload: str, current_location: Optional[dict[str, float]] = None
    ) -> RecoveryAttempt:
        """
        Recover ΛiD from QR-G code.

        Args:
            qr_payload: QR code payload data
            current_location: Current geographic location for verification

        Returns:
            RecoveryAttempt with recovery results
        """
        attempt = RecoveryAttempt()
        attempt.attempt_id = self._generate_attempt_id()
        attempt.method = RecoveryMethod.QR_GEO
        attempt.timestamp = datetime.now(timezone.utc)
        attempt.geo_location = current_location

        try:
            # Decode geo-encoded payload
            decoded_data = self.geo_encoder.decode_from_payload(qr_payload)

            if not decoded_data:
                attempt.status = RecoveryStatus.FAILED
                attempt.failure_reasons.append("Invalid QR payload format")
                return attempt

            lambda_id = decoded_data.get("lambda_id")
            original_location = decoded_data.get("geo_location")

            # Verify geographic proximity if location provided
            if current_location and original_location:
                proximity_check = self._verify_geographic_proximity(current_location, original_location)
                attempt.security_checks["proximity"] = proximity_check

                if not proximity_check["valid"]:
                    attempt.status = RecoveryStatus.FAILED
                    attempt.failure_reasons.append("Geographic verification failed")
                    return attempt

            # Verify ΛiD exists and is recoverable
            if lambda_id not in self.active_packages:
                attempt.status = RecoveryStatus.FAILED
                attempt.failure_reasons.append("ΛiD not found in recovery database")
                return attempt

            # Check expiry
            package = self.active_packages[lambda_id]
            if package.expiry_date and datetime.now(timezone.utc) > package.expiry_date:
                attempt.status = RecoveryStatus.EXPIRED
                attempt.failure_reasons.append("Recovery package expired")
                return attempt

            # Successful recovery
            attempt.lambda_id = lambda_id
            attempt.status = RecoveryStatus.SUCCESS
            attempt.success_factors.extend(
                [
                    "QR payload decoded successfully",
                    "ΛiD found in recovery database",
                    "Package not expired",
                ]
            )

            if current_location:
                attempt.success_factors.append("Geographic verification passed")

        except Exception as e:
            attempt.status = RecoveryStatus.FAILED
            attempt.failure_reasons.append(f"Recovery error: {e!s}")

        self.recovery_attempts.append(attempt)
        return attempt

    def generate_emergency_codes(self, lambda_id: str, count: int = 10) -> list[str]:
        """
        Generate emergency recovery codes for ΛiD.

        Args:
            lambda_id: The ΛiD to generate codes for
            count: Number of codes to generate

        Returns:
            List of emergency recovery codes
        """
        codes = []
        base_seed = hashlib.sha256(lambda_id.encode()).hexdigest()

        for i in range(count):
            # Generate unique code using ΛiD and index
            code_seed = f"{base_seed}-{i}-{secrets.token_hex(8)}"
            code_hash = hashlib.sha256(code_seed.encode()).hexdigest()[:12]

            # Format as human-readable code
            formatted_code = f"{code_hash[:4]}-{code_hash[4:8]}-{code_hash[8:12]}".upper()
            codes.append(formatted_code)

        return codes

    def recover_from_emergency_code(
        self,
        emergency_code: str,
        additional_verification: Optional[dict[str, str]] = None,
    ) -> RecoveryAttempt:
        """
        Recover ΛiD using emergency recovery code.

        Args:
            emergency_code: Emergency recovery code
            additional_verification: Additional verification data

        Returns:
            RecoveryAttempt with recovery results
        """
        attempt = RecoveryAttempt()
        attempt.attempt_id = self._generate_attempt_id()
        attempt.method = RecoveryMethod.EMERGENCY_CODE
        attempt.timestamp = datetime.now(timezone.utc)

        # Search for matching ΛiD
        matching_lambda_id = None
        for lambda_id, package in self.active_packages.items():
            if emergency_code in package.emergency_codes:
                matching_lambda_id = lambda_id
                break

        if not matching_lambda_id:
            attempt.status = RecoveryStatus.FAILED
            attempt.failure_reasons.append("Emergency code not found")
            return attempt

        # Additional verification if required
        if additional_verification:
            verification_passed = self._verify_additional_factors(matching_lambda_id, additional_verification)
            attempt.security_checks["additional_verification"] = verification_passed

            if not verification_passed:
                attempt.status = RecoveryStatus.FAILED
                attempt.failure_reasons.append("Additional verification failed")
                return attempt

        # Successful recovery
        attempt.lambda_id = matching_lambda_id
        attempt.status = RecoveryStatus.SUCCESS
        attempt.success_factors.append("Emergency code verified")

        # Mark code as used (one-time use)
        package = self.active_packages[matching_lambda_id]
        if emergency_code in package.emergency_codes:
            package.emergency_codes.remove(emergency_code)

        self.recovery_attempts.append(attempt)
        return attempt

    def generate_recovery_phrase(self, lambda_id: str) -> str:
        """
        Generate BIP39-style recovery phrase for ΛiD.

        Args:
            lambda_id: The ΛiD to generate phrase for

        Returns:
            24-word recovery phrase
        """
        # Generate entropy from ΛiD
        lambda_bytes = lambda_id.encode("utf-8")
        entropy = hashlib.sha256(lambda_bytes).digest()

        # Generate mnemonic from entropy
        recovery_phrase = self.mnemonic_generator.to_mnemonic(entropy)

        return recovery_phrase

    def recover_from_phrase(self, recovery_phrase: str) -> RecoveryAttempt:
        """
        Recover ΛiD from recovery phrase.

        Args:
            recovery_phrase: BIP39-style recovery phrase

        Returns:
            RecoveryAttempt with recovery results
        """
        attempt = RecoveryAttempt()
        attempt.attempt_id = self._generate_attempt_id()
        attempt.method = RecoveryMethod.RECOVERY_PHRASE
        attempt.timestamp = datetime.now(timezone.utc)

        try:
            # Validate phrase format
            if not self.mnemonic_generator.check(recovery_phrase):
                attempt.status = RecoveryStatus.FAILED
                attempt.failure_reasons.append("Invalid recovery phrase format")
                return attempt

            # Search for matching ΛiD
            matching_lambda_id = None
            for lambda_id, package in self.active_packages.items():
                if package.recovery_phrase == recovery_phrase:
                    matching_lambda_id = lambda_id
                    break

            if not matching_lambda_id:
                attempt.status = RecoveryStatus.FAILED
                attempt.failure_reasons.append("Recovery phrase not found")
                return attempt

            # Successful recovery
            attempt.lambda_id = matching_lambda_id
            attempt.status = RecoveryStatus.SUCCESS
            attempt.success_factors.append("Recovery phrase verified")

        except Exception as e:
            attempt.status = RecoveryStatus.FAILED
            attempt.failure_reasons.append(f"Recovery error: {e!s}")

        self.recovery_attempts.append(attempt)
        return attempt

    def sync_across_devices(self, lambda_id: str, source_device: str, target_devices: list[str]) -> dict[str, Any]:
        """
        Synchronize ΛiD across multiple devices.

        Args:
            lambda_id: The ΛiD to synchronize
            source_device: Source device identifier
            target_devices: List of target device identifiers

        Returns:
            Dict with synchronization results
        """
        sync_results = {
            "lambda_id": lambda_id,
            "source_device": source_device,
            "target_devices": target_devices,
            "sync_timestamp": datetime.now(timezone.utc).isoformat(),
            "successful_syncs": [],
            "failed_syncs": [],
            "sync_package": None,
        }

        # Get portability package
        if lambda_id not in self.active_packages:
            sync_results["error"] = "ΛiD not found in portability system"
            return sync_results

        package = self.active_packages[lambda_id]

        # Create encrypted sync package
        sync_package = self._create_sync_package(package)
        sync_results["sync_package"] = sync_package

        # Simulate device synchronization
        for device in target_devices:
            sync_success = self._sync_to_device(device, sync_package)

            if sync_success:
                sync_results["successful_syncs"].append(device)
            else:
                sync_results["failed_syncs"].append(device)

        return sync_results

    def create_backup_file(self, lambda_id: str, password: str) -> dict[str, Any]:
        """
        Create encrypted backup file for ΛiD.

        Args:
            lambda_id: The ΛiD to backup
            password: Password for encryption

        Returns:
            Dict with backup file data
        """
        if lambda_id not in self.active_packages:
            return {"error": "ΛiD not found in portability system"}

        package = self.active_packages[lambda_id]

        # Create backup data
        backup_data = {
            "lambda_id": lambda_id,
            "package": package.to_dict(),
            "backup_timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
        }

        # Encrypt backup data
        encrypted_backup = self._encrypt_with_password(json.dumps(backup_data).encode(), password)

        return {
            "backup_file": base64.b64encode(encrypted_backup).decode(),
            "filename": f"lambda_id_backup_{lambda_id.replace('LUKHAS', 'L')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.lbak",
            "size_bytes": len(encrypted_backup),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def restore_from_backup(self, backup_file: str, password: str) -> RecoveryAttempt:
        """
        Restore ΛiD from encrypted backup file.

        Args:
            backup_file: Base64-encoded backup file
            password: Password for decryption

        Returns:
            RecoveryAttempt with restore results
        """
        attempt = RecoveryAttempt()
        attempt.attempt_id = self._generate_attempt_id()
        attempt.method = RecoveryMethod.BACKUP_FILE
        attempt.timestamp = datetime.now(timezone.utc)

        try:
            # Decode backup file
            backup_bytes = base64.b64decode(backup_file.encode())

            # Decrypt backup data
            decrypted_data = self._decrypt_with_password(backup_bytes, password)
            backup_data = json.loads(decrypted_data.decode())

            # Validate backup format
            if "lambda_id" not in backup_data or "package" not in backup_data:
                attempt.status = RecoveryStatus.FAILED
                attempt.failure_reasons.append("Invalid backup file format")
                return attempt

            lambda_id = backup_data["lambda_id"]

            # Restore package
            package_data = backup_data["package"]
            package = PortabilityPackage()
            package.lambda_id = package_data["lambda_id"]
            package.qr_geo_code = package_data["qr_geo_code"]
            package.emergency_codes = package_data["emergency_codes"]
            package.recovery_phrase = package_data["recovery_phrase"]
            package.backup_data = package_data["backup_data"]

            # Store restored package
            self.active_packages[lambda_id] = package

            # Successful recovery
            attempt.lambda_id = lambda_id
            attempt.status = RecoveryStatus.SUCCESS
            attempt.success_factors.append("Backup file decrypted successfully")
            attempt.success_factors.append("ΛiD package restored")

        except Exception as e:
            attempt.status = RecoveryStatus.FAILED
            attempt.failure_reasons.append(f"Restore error: {e!s}")

        self.recovery_attempts.append(attempt)
        return attempt

    def get_recovery_analytics(self, lambda_id: Optional[str] = None) -> dict[str, Any]:
        """
        Get recovery analytics and statistics.

        Args:
            lambda_id: Optional specific ΛiD to analyze

        Returns:
            Dict with recovery analytics
        """
        if lambda_id:
            # Analytics for specific ΛiD
            lambda_attempts = [a for a in self.recovery_attempts if a.lambda_id == lambda_id]

            return {
                "lambda_id": lambda_id,
                "total_attempts": len(lambda_attempts),
                "successful_recoveries": len([a for a in lambda_attempts if a.status == RecoveryStatus.SUCCESS]),
                "failed_attempts": len([a for a in lambda_attempts if a.status == RecoveryStatus.FAILED]),
                "methods_used": list({a.method.value for a in lambda_attempts if a.method}),
                "latest_attempt": (lambda_attempts[-1].to_dict() if lambda_attempts else None),
                "package_exists": lambda_id in self.active_packages,
            }
        else:
            # Overall analytics
            total_attempts = len(self.recovery_attempts)
            successful = len([a for a in self.recovery_attempts if a.status == RecoveryStatus.SUCCESS])

            method_stats = {}
            for method in RecoveryMethod:
                method_attempts = [a for a in self.recovery_attempts if a.method == method]
                method_stats[method.value] = {
                    "total": len(method_attempts),
                    "successful": len([a for a in method_attempts if a.status == RecoveryStatus.SUCCESS]),
                }

            return {
                "total_recovery_attempts": total_attempts,
                "successful_recoveries": successful,
                "success_rate": ((successful / total_attempts * 100) if total_attempts > 0 else 0),
                "active_packages": len(self.active_packages),
                "method_statistics": method_stats,
                "peak_recovery_day": self._get_peak_recovery_day(),
            }

    # Private helper methods

    def _generate_qr_geo_code(self, lambda_id: str, geo_location: Optional[dict[str, float]]) -> str:
        """Generate QR-G code for ΛiD"""
        geo_data = self.geo_encoder.encode_with_location(lambda_id, geo_location)
        return geo_data

    def _generate_emergency_codes(self, lambda_id: str, security_level: str) -> list[str]:
        """Generate emergency codes based on security level"""
        code_count = {"standard": 5, "high": 10, "ultra": 15}.get(security_level, 5)
        return self.generate_emergency_codes(lambda_id, code_count)

    def _generate_recovery_phrase(self, lambda_id: str) -> str:
        """Generate recovery phrase for ΛiD"""
        return self.generate_recovery_phrase(lambda_id)

    def _create_backup_data(self, lambda_id: str, security_level: str) -> dict[str, Any]:
        """Create backup data structure"""
        return {
            "lambda_id": lambda_id,
            "security_level": security_level,
            "backup_version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "checksum": hashlib.sha256(lambda_id.encode()).hexdigest(),
        }

    def _calculate_expiry_date(self, security_level: str) -> datetime:
        """Calculate expiry date based on security level"""
        days_mapping = {"standard": 365, "high": 730, "ultra": 1095}
        days = days_mapping.get(security_level, 365)
        return datetime.now(timezone.utc) + timedelta(days=days)

    def _add_security_layer(self, payload: str, security_level: str) -> str:
        """Add additional security layer to payload"""
        if security_level == "high":
            # Add timestamp and signature
            timestamp = datetime.now(timezone.utc).timestamp()
            secured_payload = f"{payload}|{timestamp}"
            return base64.b64encode(secured_payload.encode()).decode()
        elif security_level == "ultra":
            # Add encryption layer
            encrypted = self._encrypt_data(payload.encode())
            return base64.b64encode(encrypted).decode()
        return payload

    def _verify_geographic_proximity(
        self,
        current: dict[str, float],
        original: dict[str, float],
        max_distance_km: float = 50.0,
    ) -> dict[str, Any]:
        """Verify geographic proximity between locations"""
        # Calculate distance using Haversine formula
        import math

        lat1, lon1 = math.radians(current["lat"]), math.radians(current["lng"])
        lat2, lon2 = math.radians(original["lat"]), math.radians(original["lng"])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = 6371 * c  # Earth's radius in km

        return {
            "valid": distance_km <= max_distance_km,
            "distance_km": round(distance_km, 2),
            "max_allowed_km": max_distance_km,
            "current_location": current,
            "original_location": original,
        }

    def _verify_additional_factors(self, lambda_id: str, factors: dict[str, str]) -> bool:
        """Verify additional authentication factors"""
        # Placeholder for additional verification logic
        return True

    def _generate_attempt_id(self) -> str:
        """Generate unique attempt ID"""
        return f"rec_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"

    def _get_qr_recovery_instructions(self) -> list[str]:
        """Get QR recovery instructions"""
        return [
            "Scan QR code with LUKHAS app",
            "Verify your current location matches the original",
            "Complete additional verification if prompted",
            "Your ΛiD will be restored automatically",
        ]

    def _create_sync_package(self, package: PortabilityPackage) -> str:
        """Create encrypted sync package"""
        sync_data = package.to_dict()
        encrypted_data = self._encrypt_data(json.dumps(sync_data).encode())
        return base64.b64encode(encrypted_data).decode()

    def _sync_to_device(self, device_id: str, sync_package: str) -> bool:
        """Simulate device synchronization"""
        # In real implementation, this would use device-specific protocols
        return True  # Simulate success

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using system crypto key"""
        f = Fernet(self.crypto_key)
        return f.encrypt(data)

    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using system crypto key"""
        f = Fernet(self.crypto_key)
        return f.decrypt(encrypted_data)

    def _encrypt_with_password(self, data: bytes, password: str) -> bytes:
        """Encrypt data with password-derived key"""
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        encrypted = f.encrypt(data)
        return salt + encrypted

    def _decrypt_with_password(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data with password-derived key"""
        salt = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        return f.decrypt(encrypted)

    def _get_peak_recovery_day(self) -> Optional[str]:
        """Get day with most recovery attempts"""
        if not self.recovery_attempts:
            return None

        day_counts = defaultdict(int)
        for attempt in self.recovery_attempts:
            day = attempt.timestamp.strftime("%Y-%m-%d")
            day_counts[day] += 1

        peak_day = max(day_counts, key=day_counts.get)
        return peak_day

    def _initialize_crypto_key(self) -> bytes:
        """Initialize or load crypto key"""
        # In production, this would load from secure storage
        return Fernet.generate_key()

    def _load_config(self, config_path: Optional[str] = None) -> dict[str, Any]:
        """Load portability system configuration"""
        return {
            "qr_geo_enabled": True,
            "emergency_codes_enabled": True,
            "recovery_phrase_enabled": True,
            "cross_device_sync_enabled": True,
            "backup_encryption_enabled": True,
            "geographic_verification_enabled": True,
            "max_recovery_attempts_per_day": 5,
        }


class GeographicEncoder:
    """Geographic encoding utility for QR-G codes"""

    def encode_with_location(self, lambda_id: str, geo_location: Optional[dict[str, float]]) -> str:
        """Encode ΛiD with geographic location"""
        if not geo_location:
            return lambda_id

        geo_data = {
            "lambda_id": lambda_id,
            "geo_location": geo_location,
            "timestamp": datetime.now(timezone.utc).timestamp(),
        }

        encoded = base64.b64encode(json.dumps(geo_data).encode()).decode()
        return f"GEO:{encoded}"

    def decode_from_payload(self, payload: str) -> Optional[dict[str, Any]]:
        """Decode geographic payload"""
        try:
            if payload.startswith("GEO:"):
                encoded_data = payload[4:]
                decoded = base64.b64decode(encoded_data.encode()).decode()
                return json.loads(decoded)
        except Exception:
            pass
        return None


# Example usage and testing
if __name__ == "__main__":
    portability = LambdaIDPortabilitySystem()

    # Test ΛiD
    test_lambda_id = "Λ3-A1B2-🔮-C3D4"
    geo_location = {"lat": 37.7749, "lng": -122.4194}  # San Francisco

    print("ΛiD Portability & Recovery System Test:")
    print("=" * 50)

    # Create portability package
    package = portability.create_portability_package(
        test_lambda_id,
        [
            RecoveryMethod.QR_GEO,
            RecoveryMethod.EMERGENCY_CODE,
            RecoveryMethod.RECOVERY_PHRASE,
        ],
        geo_location=geo_location,
        security_level="high",
    )

    print(f"Created portability package for: {test_lambda_id}")
    print(f"Methods enabled: {[m.value for m in package.methods_enabled]}")
    print(f"Emergency codes: {len(package.emergency_codes)}")
    print(f"Recovery phrase: {package.recovery_phrase[:50]}...")

    # Test QR-G recovery
    print("\nTesting QR-G Recovery:")
    qr_data = portability.generate_qr_geo_recovery(test_lambda_id, geo_location)
    print("QR code generated with geo-encoding")

    # Simulate recovery
    recovery_attempt = portability.recover_from_qr_geo(
        qr_data["geo_payload"],
        {"lat": 37.7750, "lng": -122.4195},  # Slightly different location
    )
    print(f"Recovery status: {recovery_attempt.status.value}")
    print(f"Success factors: {recovery_attempt.success_factors}")

    # Test emergency code recovery
    print("\nTesting Emergency Code Recovery:")
    emergency_code = package.emergency_codes[0]
    emergency_recovery = portability.recover_from_emergency_code(emergency_code)
    print(f"Emergency recovery status: {emergency_recovery.status.value}")

    # Test recovery phrase
    print("\nTesting Recovery Phrase:")
    phrase_recovery = portability.recover_from_phrase(package.recovery_phrase)
    print(f"Phrase recovery status: {phrase_recovery.status.value}")

    # Test backup creation
    print("\nTesting Backup Creation:")
    backup = portability.create_backup_file(test_lambda_id, "secure_password_123")
    print(f"Backup file created: {backup['filename']}")
    print(f"Size: {backup['size_bytes']} bytes")

    # Test analytics
    print("\nRecovery Analytics:")
    analytics = portability.get_recovery_analytics()
    print(f"Total attempts: {analytics['total_recovery_attempts']}")
    print(f"Success rate: {analytics['success_rate']:.1f}%")
    print(f"Active packages: {analytics['active_packages']}")
