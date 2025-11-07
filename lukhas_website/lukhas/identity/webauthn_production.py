#!/usr/bin/env python3
"""
LUKHAS I.4 WebAuthn/Passkeys - Production Implementation
Production Schema v1.0.0

Complete WebAuthn/FIDO2 production implementation with biometric support,
device attestation, and enterprise-grade security features.

Constellation Framework: Identity ⚛️ pillar with T4-T5 authentication tiers
"""

from __future__ import annotations

import base64
import binascii
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Tuple

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics
webauthn_registrations_total = Counter(
    'lukhas_webauthn_registrations_total',
    'Total WebAuthn registrations',
    ['authenticator_type', 'status']
)

webauthn_authentications_total = Counter(
    'lukhas_webauthn_authentications_total',
    'Total WebAuthn authentications',
    ['authenticator_type', 'status', 'tier']
)

webauthn_latency_seconds = Histogram(
    'lukhas_webauthn_latency_seconds',
    'WebAuthn operation latency',
    ['operation', 'authenticator_type'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

webauthn_active_credentials = Gauge(
    'lukhas_webauthn_active_credentials',
    'Active WebAuthn credentials count',
    ['user_tier', 'authenticator_type']
)

try:
    from webauthn import (
        generate_authentication_options,
        generate_registration_options,
        verify_authentication_response,
        verify_registration_response,
    )
    from webauthn.helpers import (
        parse_authentication_credential_json,
        parse_registration_credential_json,
    )
    from webauthn.helpers.structs import (
        AttestationConveyancePreference,
        AuthenticatorAttachment,
        AuthenticatorSelectionCriteria,
        PublicKeyCredentialDescriptor,
        RegistrationCredential,
        ResidentKeyRequirement,
        UserVerificationRequirement,
    )
    WEBAUTHN_AVAILABLE = True
except ImportError:
    logger.warning("WebAuthn library not available - using mock implementation")
    WEBAUTHN_AVAILABLE = False
    RegistrationCredential = Any  # type: ignore[misc,assignment]

# Import LUKHAS WebAuthn type definitions (TypedDict for type checking)
# Resolves: #591, #592, #593, #594, #595, #596


def _decode_credential_id(credential_id: str) -> bytes | None:
    """Decode a credential ID stored as URL-safe base64."""
    padding = "=" * (-len(credential_id) % 4)
    try:
        return base64.b64decode(
            f"{credential_id}{padding}",
            altchars=b"-_",
            validate=True
        )
    except (ValueError, binascii.Error) as exc:
        logger.warning("Invalid credential_id encoding for WebAuthn descriptor: %s", exc)
        return None


class AuthenticatorType(Enum):
    """Types of WebAuthn authenticators"""
    PLATFORM = "platform"  # Built-in (Touch ID, Windows Hello, etc.)
    ROAMING = "roaming"    # External (YubiKey, etc.)
    HYBRID = "hybrid"      # Cross-device authentication


class AuthenticatorTier(Enum):
    """Authentication tier requirements"""
    T3_MFA = "T3"      # Basic 2FA
    T4_STRONG = "T4"   # Strong authentication
    T5_BIOMETRIC = "T5"  # Biometric attestation


class CredentialStatus(Enum):
    """WebAuthn credential status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class WebAuthnCredential:
    """WebAuthn credential with enhanced metadata"""
    credential_id: str
    public_key: str
    user_id: str
    sign_count: int = 0
    authenticator_type: AuthenticatorType = AuthenticatorType.PLATFORM
    tier: AuthenticatorTier = AuthenticatorTier.T4_STRONG
    status: CredentialStatus = CredentialStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime | None = None
    device_name: str | None = None
    aaguid: str | None = None  # Authenticator Attestation GUID
    attestation_data: dict[str, Any] = field(default_factory=dict)
    biometric_enrolled: bool = False
    backup_eligible: bool = False
    backup_state: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert credential to dictionary"""
        return {
            "credential_id": self.credential_id,
            "public_key": self.public_key,
            "user_id": self.user_id,
            "sign_count": self.sign_count,
            "authenticator_type": self.authenticator_type.value,
            "tier": self.tier.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "device_name": self.device_name,
            "aaguid": self.aaguid,
            "attestation_data": self.attestation_data,
            "biometric_enrolled": self.biometric_enrolled,
            "backup_eligible": self.backup_eligible,
            "backup_state": self.backup_state,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebAuthnCredential:
        """Create credential from dictionary"""
        credential = cls(
            credential_id=data["credential_id"],
            public_key=data["public_key"],
            user_id=data["user_id"],
            sign_count=data.get("sign_count", 0),
            authenticator_type=AuthenticatorType(data.get("authenticator_type", "platform")),
            tier=AuthenticatorTier(data.get("tier", "T4")),
            status=CredentialStatus(data.get("status", "active")),
            created_at=datetime.fromisoformat(data["created_at"]),
            device_name=data.get("device_name"),
            aaguid=data.get("aaguid"),
            attestation_data=data.get("attestation_data", {}),
            biometric_enrolled=data.get("biometric_enrolled", False),
            backup_eligible=data.get("backup_eligible", False),
            backup_state=data.get("backup_state", False),
            metadata=data.get("metadata", {})
        )

        if data.get("last_used"):
            credential.last_used = datetime.fromisoformat(data["last_used"])

        return credential


@dataclass
class WebAuthnChallenge:
    """WebAuthn challenge session"""
    challenge_id: str
    challenge: str
    user_id: str
    operation: str  # "registration" or "authentication"
    expires_at: datetime
    tier_required: AuthenticatorTier = AuthenticatorTier.T4_STRONG
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if challenge is expired"""
        return datetime.now(timezone.utc) > self.expires_at


class WebAuthnCredentialStore:
    """Credential storage interface"""

    def __init__(self):
        self._credentials: dict[str, list[WebAuthnCredential]] = {}
        self._challenges: dict[str, WebAuthnChallenge] = {}

    async def store_credential(self, credential: WebAuthnCredential) -> None:
        """Store a WebAuthn credential"""
        if credential.user_id not in self._credentials:
            self._credentials[credential.user_id] = []

        self._credentials[credential.user_id].append(credential)

        # Update metrics
        webauthn_active_credentials.labels(
            user_tier=credential.tier.value,
            authenticator_type=credential.authenticator_type.value
        ).inc()

    async def get_credentials(self, user_id: str) -> list[WebAuthnCredential]:
        """Get all credentials for a user"""
        return self._credentials.get(user_id, [])

    async def get_credential(self, credential_id: str) -> WebAuthnCredential | None:
        """Get specific credential by ID"""
        for credentials in self._credentials.values():
            for credential in credentials:
                if credential.credential_id == credential_id:
                    return credential
        return None

    async def update_credential(self, credential: WebAuthnCredential) -> None:
        """Update an existing credential"""
        for credentials in self._credentials.values():
            for i, cred in enumerate(credentials):
                if cred.credential_id == credential.credential_id:
                    credentials[i] = credential
                    return

    async def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential"""
        for _user_id, credentials in self._credentials.items():
            for i, credential in enumerate(credentials):
                if credential.credential_id == credential_id:
                    removed = credentials.pop(i)

                    # Update metrics
                    webauthn_active_credentials.labels(
                        user_tier=removed.tier.value,
                        authenticator_type=removed.authenticator_type.value
                    ).dec()

                    return True
        return False

    async def store_challenge(self, challenge: WebAuthnChallenge) -> None:
        """Store a WebAuthn challenge"""
        self._challenges[challenge.challenge_id] = challenge

    async def get_challenge(self, challenge_id: str) -> WebAuthnChallenge | None:
        """Get a challenge by ID"""
        challenge = self._challenges.get(challenge_id)
        if challenge and challenge.is_expired():
            del self._challenges[challenge_id]
            return None
        return challenge

    async def delete_challenge(self, challenge_id: str) -> None:
        """Delete a challenge"""
        if challenge_id in self._challenges:
            del self._challenges[challenge_id]


class WebAuthnManager:
    """Production WebAuthn/Passkeys manager"""

    def __init__(self,
                 rp_id: str,
                 rp_name: str,
                 origin: str,
                 credential_store: WebAuthnCredentialStore | None = None):
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.origin = origin
        self.credential_store = credential_store or WebAuthnCredentialStore()

        # Initialize authenticator metadata
        self._load_authenticator_metadata()

    def _load_authenticator_metadata(self) -> None:
        """Load authenticator metadata for device recognition"""
        # In production, this would load from FIDO Alliance MDS
        self.authenticator_metadata = {
            # Apple Touch ID
            "08987058-cadc-4b81-b6e1-30de50dcbe96": {
                "name": "Touch ID",
                "icon": "🔐",
                "biometric": True,
                "tier": "T5"
            },
            # Windows Hello
            "6028b017-b1d4-4c02-b4b3-afcdafc96bb2": {
                "name": "Windows Hello",
                "icon": "🔑",
                "biometric": True,
                "tier": "T5"
            },
            # YubiKey 5 Series
            "cb69481e-8ff7-4039-93ec-0a2729a154a8": {
                "name": "YubiKey 5",
                "icon": "🔧",
                "biometric": False,
                "tier": "T4"
            }
        }

    async def begin_registration(self,
                               user_id: str,
                               username: str,
                               display_name: str,
                               tier: AuthenticatorTier = AuthenticatorTier.T4_STRONG,
                               authenticator_attachment: str | None = None,
                               resident_key: bool = True) -> dict[str, Any]:
        """Begin WebAuthn credential registration"""

        with tracer.start_span("webauthn.begin_registration") as span:
            span.set_attribute("user_id", user_id)
            span.set_attribute("tier", tier.value)
            span.set_attribute("authenticator_attachment", authenticator_attachment or "any")

            start_time = time.time()

            try:
                # Get existing credentials for excludeCredentials
                existing_credentials = await self.credential_store.get_credentials(user_id)
                active_credentials = [
                    cred for cred in existing_credentials
                    if cred.status == CredentialStatus.ACTIVE
                ]

                if not WEBAUTHN_AVAILABLE:
                    exclude_credentials = [
                        {"id": cred.credential_id, "type": "public-key"}
                        for cred in active_credentials
                    ]
                    # Mock implementation for testing
                    challenge_id = secrets.token_urlsafe(32)
                    challenge = secrets.token_urlsafe(64)

                    # Store challenge
                    await self.credential_store.store_challenge(WebAuthnChallenge(
                        challenge_id=challenge_id,
                        challenge=challenge,
                        user_id=user_id,
                        operation="registration",
                        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                        tier_required=tier
                    ))

                    return {
                        "challenge": challenge,
                        "rp": {"id": self.rp_id, "name": self.rp_name},
                        "user": {
                            "id": base64.urlsafe_b64encode(user_id.encode()).decode().rstrip("="),
                            "name": username,
                            "displayName": display_name
                        },
                        "pubKeyCredParams": [
                            {"alg": -7, "type": "public-key"},  # ES256
                            {"alg": -257, "type": "public-key"}  # RS256
                        ],
                        "timeout": 300000,  # 5 minutes
                        "excludeCredentials": exclude_credentials,
                        "authenticatorSelection": {
                            "authenticatorAttachment": authenticator_attachment,
                            "residentKey": "required" if resident_key else "discouraged",
                            "userVerification": "required" if tier == AuthenticatorTier.T5_BIOMETRIC else "preferred"
                        },
                        "attestation": "direct" if tier == AuthenticatorTier.T5_BIOMETRIC else "none",
                        "_challenge_id": challenge_id
                    }

                exclude_credentials = self._build_credential_descriptors(active_credentials)

                # Production WebAuthn implementation
                user_verification = (
                    UserVerificationRequirement.REQUIRED
                    if tier == AuthenticatorTier.T5_BIOMETRIC
                    else UserVerificationRequirement.PREFERRED
                )

                authenticator_selection = AuthenticatorSelectionCriteria(
                    authenticator_attachment=AuthenticatorAttachment(authenticator_attachment) if authenticator_attachment else None,
                    resident_key=ResidentKeyRequirement.REQUIRED if resident_key else ResidentKeyRequirement.DISCOURAGED,
                    user_verification=user_verification
                )

                attestation = (
                    AttestationConveyancePreference.DIRECT
                    if tier == AuthenticatorTier.T5_BIOMETRIC
                    else AttestationConveyancePreference.NONE
                )

                registration_options = generate_registration_options(
                    rp_id=self.rp_id,
                    rp_name=self.rp_name,
                    user_id=user_id.encode(),
                    user_name=username,
                    user_display_name=display_name,
                    exclude_credentials=exclude_credentials,
                    authenticator_selection=authenticator_selection,
                    attestation=attestation,
                    timeout=300000  # 5 minutes
                )

                # Store challenge for verification
                challenge_id = secrets.token_urlsafe(32)
                await self.credential_store.store_challenge(WebAuthnChallenge(
                    challenge_id=challenge_id,
                    challenge=registration_options.challenge,
                    user_id=user_id,
                    operation="registration",
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                    tier_required=tier
                ))

                # Record metrics
                latency = time.time() - start_time
                webauthn_latency_seconds.labels(
                    operation="begin_registration",
                    authenticator_type=authenticator_attachment or "any"
                ).observe(latency)

                span.set_attribute("challenge_id", challenge_id)
                span.set_attribute("latency", latency)

                options_dict = registration_options.model_dump(mode="json")
                options_dict["_challenge_id"] = challenge_id
                return options_dict

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                webauthn_registrations_total.labels(
                    authenticator_type=authenticator_attachment or "any",
                    status="error"
                ).inc()

                logger.error(f"WebAuthn registration initiation failed: {e}")
                raise

    async def finish_registration(self,
                                challenge_id: str,
                                credential_data: dict[str, Any],
                                device_name: str | None = None) -> WebAuthnCredential:
        """Complete WebAuthn credential registration"""

        with tracer.start_span("webauthn.finish_registration") as span:
            span.set_attribute("challenge_id", challenge_id)

            start_time = time.time()

            try:
                # Retrieve and validate challenge
                challenge = await self.credential_store.get_challenge(challenge_id)
                if not challenge or challenge.operation != "registration":
                    raise ValueError("Invalid or expired registration challenge")

                if not WEBAUTHN_AVAILABLE:
                    # Mock implementation for testing
                    credential_id = secrets.token_urlsafe(32)
                    public_key = secrets.token_urlsafe(64)

                    credential = WebAuthnCredential(
                        credential_id=credential_id,
                        public_key=public_key,
                        user_id=challenge.user_id,
                        tier=challenge.tier_required,
                        authenticator_type=AuthenticatorType.PLATFORM,
                        device_name=device_name or "Mock Authenticator",
                        biometric_enrolled=challenge.tier_required == AuthenticatorTier.T5_BIOMETRIC
                    )

                    await self.credential_store.store_credential(credential)
                    await self.credential_store.delete_challenge(challenge_id)

                    # Record metrics
                    latency = time.time() - start_time
                    webauthn_latency_seconds.labels(
                        operation="finish_registration",
                        authenticator_type="platform"
                    ).observe(latency)

                    webauthn_registrations_total.labels(
                        authenticator_type="platform",
                        status="success"
                    ).inc()

                    return credential

                # Production WebAuthn implementation
                credential: RegistrationCredential = parse_registration_credential_json(
                    json.dumps(credential_data)
                )

                verification = verify_registration_response(
                    credential=credential,
                    expected_challenge=challenge.challenge.encode(),
                    expected_origin=self.origin,
                    expected_rp_id=self.rp_id
                )

                if not verification.verified:
                    raise ValueError("WebAuthn registration verification failed")

                # Extract credential information
                credential_id = base64.urlsafe_b64encode(verification.credential_id).decode().rstrip("=")
                public_key = base64.urlsafe_b64encode(verification.credential_public_key).decode().rstrip("=")

                # Determine authenticator type and capabilities
                authenticator_type = self._determine_authenticator_type(verification)
                biometric_enrolled = self._check_biometric_enrollment(verification)

                # Create credential record
                webauthn_credential = WebAuthnCredential(
                    credential_id=credential_id,
                    public_key=public_key,
                    user_id=challenge.user_id,
                    sign_count=verification.sign_count,
                    tier=challenge.tier_required,
                    authenticator_type=authenticator_type,
                    device_name=device_name or self._get_device_name(verification),
                    aaguid=verification.aaguid.hex() if verification.aaguid else None,
                    attestation_data=verification.attestation_object if hasattr(verification, 'attestation_object') else {},
                    biometric_enrolled=biometric_enrolled,
                    backup_eligible=getattr(verification, 'backup_eligible', False),
                    backup_state=getattr(verification, 'backup_state', False)
                )

                # Store credential
                await self.credential_store.store_credential(webauthn_credential)
                await self.credential_store.delete_challenge(challenge_id)

                # Record metrics
                latency = time.time() - start_time
                webauthn_latency_seconds.labels(
                    operation="finish_registration",
                    authenticator_type=authenticator_type.value
                ).observe(latency)

                webauthn_registrations_total.labels(
                    authenticator_type=authenticator_type.value,
                    status="success"
                ).inc()

                span.set_attribute("credential_id", credential_id)
                span.set_attribute("authenticator_type", authenticator_type.value)
                span.set_attribute("biometric_enrolled", biometric_enrolled)
                span.set_attribute("latency", latency)

                return webauthn_credential

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                webauthn_registrations_total.labels(
                    authenticator_type="unknown",
                    status="error"
                ).inc()

                logger.error(f"WebAuthn registration completion failed: {e}")
                raise

    async def begin_authentication(self,
                                 user_id: str | None = None,
                                 tier: AuthenticatorTier = AuthenticatorTier.T4_STRONG,
                                 timeout: int = 300000) -> dict[str, Any]:
        """Begin WebAuthn authentication"""

        with tracer.start_span("webauthn.begin_authentication") as span:
            span.set_attribute("user_id", user_id or "usernameless")
            span.set_attribute("tier", tier.value)

            start_time = time.time()

            try:
                # Get allowed credentials
                active_credentials: list[WebAuthnCredential] = []
                if user_id:
                    credentials = await self.credential_store.get_credentials(user_id)
                    active_credentials = [
                        cred
                        for cred in credentials
                        if cred.status == CredentialStatus.ACTIVE and cred.tier.value >= tier.value
                    ]

                    if not WEBAUTHN_AVAILABLE:
                        allowed_credentials = [
                            {"id": cred.credential_id, "type": "public-key"}
                            for cred in active_credentials
                        ]
                    else:
                        allowed_credentials = self._build_credential_descriptors(active_credentials)

                if not WEBAUTHN_AVAILABLE:
                    # Mock implementation for testing
                    challenge_id = secrets.token_urlsafe(32)
                    challenge = secrets.token_urlsafe(64)

                    allowed_credentials = [
                        {"id": cred.credential_id, "type": "public-key"}
                        for cred in active_credentials
                    ]

                    # Store challenge
                    await self.credential_store.store_challenge(WebAuthnChallenge(
                        challenge_id=challenge_id,
                        challenge=challenge,
                        user_id=user_id or "",
                        operation="authentication",
                        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                        tier_required=tier
                    ))

                    span.set_attribute("allowed_credentials", len(allowed_credentials))

                    return {
                        "challenge": challenge,
                        "timeout": timeout,
                        "rpId": self.rp_id,
                        "allowCredentials": allowed_credentials,
                        "userVerification": "required" if tier == AuthenticatorTier.T5_BIOMETRIC else "preferred",
                        "_challenge_id": challenge_id
                    }

                # Production WebAuthn implementation
                user_verification = (
                    UserVerificationRequirement.REQUIRED
                    if tier == AuthenticatorTier.T5_BIOMETRIC
                    else UserVerificationRequirement.PREFERRED
                )

                allowed_credentials = []
                for cred in active_credentials:
                    descriptor_bytes = _decode_credential_id(cred.credential_id)
                    if descriptor_bytes is None:
                        continue
                    allowed_credentials.append(
                        PublicKeyCredentialDescriptor(
                            id=descriptor_bytes,
                            type="public-key"
                        )
                    )

                authentication_options = generate_authentication_options(
                    rp_id=self.rp_id,
                    allow_credentials=allowed_credentials,
                    user_verification=user_verification,
                    timeout=timeout
                )

                # Store challenge for verification
                challenge_id = secrets.token_urlsafe(32)
                await self.credential_store.store_challenge(WebAuthnChallenge(
                    challenge_id=challenge_id,
                    challenge=authentication_options.challenge,
                    user_id=user_id or "",
                    operation="authentication",
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                    tier_required=tier
                ))

                # Record metrics
                latency = time.time() - start_time
                webauthn_latency_seconds.labels(
                    operation="begin_authentication",
                    authenticator_type="any"
                ).observe(latency)

                span.set_attribute("challenge_id", challenge_id)
                span.set_attribute("allowed_credentials", len(allowed_credentials))
                span.set_attribute("latency", latency)

                options_dict = authentication_options.model_dump(mode="json")
                options_dict["_challenge_id"] = challenge_id
                return options_dict

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                logger.error(f"WebAuthn authentication initiation failed: {e}")
                raise

    async def finish_authentication(self,
                                  challenge_id: str,
                                  credential_data: dict[str, Any]) -> tuple[WebAuthnCredential, dict[str, Any]]:
        """Complete WebAuthn authentication"""

        with tracer.start_span("webauthn.finish_authentication") as span:
            span.set_attribute("challenge_id", challenge_id)

            start_time = time.time()

            try:
                # Retrieve and validate challenge
                challenge = await self.credential_store.get_challenge(challenge_id)
                if not challenge or challenge.operation != "authentication":
                    raise ValueError("Invalid or expired authentication challenge")

                if not WEBAUTHN_AVAILABLE:
                    # Mock implementation for testing
                    credential_id = credential_data.get("id", "mock_credential")
                    credential = await self.credential_store.get_credential(credential_id)

                    if not credential:
                        raise ValueError("Credential not found")

                    if credential.status != CredentialStatus.ACTIVE:
                        raise ValueError("Credential is not active")

                    # Update credential
                    credential.last_used = datetime.now(timezone.utc)
                    credential.sign_count += 1
                    await self.credential_store.update_credential(credential)
                    await self.credential_store.delete_challenge(challenge_id)

                    # Record metrics
                    latency = time.time() - start_time
                    webauthn_latency_seconds.labels(
                        operation="finish_authentication",
                        authenticator_type=credential.authenticator_type.value
                    ).observe(latency)

                    webauthn_authentications_total.labels(
                        authenticator_type=credential.authenticator_type.value,
                        status="success",
                        tier=credential.tier.value
                    ).inc()

                    return credential, {"verified": True, "sign_count": credential.sign_count}

                # Production WebAuthn implementation
                credential_json = parse_authentication_credential_json(json.dumps(credential_data))

                # Get stored credential
                credential_id = credential_data.get("id")
                stored_credential = await self.credential_store.get_credential(credential_id)

                if not stored_credential:
                    raise ValueError("Credential not found")

                if stored_credential.status != CredentialStatus.ACTIVE:
                    raise ValueError("Credential is not active")

                # Verify authentication response
                verification = verify_authentication_response(
                    credential=credential_json,
                    expected_challenge=challenge.challenge.encode(),
                    expected_origin=self.origin,
                    expected_rp_id=self.rp_id,
                    credential_public_key=base64.urlsafe_b64decode(stored_credential.public_key + "==="),
                    credential_current_sign_count=stored_credential.sign_count
                )

                if not verification.verified:
                    webauthn_authentications_total.labels(
                        authenticator_type=stored_credential.authenticator_type.value,
                        status="failed",
                        tier=stored_credential.tier.value
                    ).inc()
                    raise ValueError("WebAuthn authentication verification failed")

                # Update credential
                stored_credential.last_used = datetime.now(timezone.utc)
                stored_credential.sign_count = verification.new_sign_count
                await self.credential_store.update_credential(stored_credential)
                await self.credential_store.delete_challenge(challenge_id)

                # Record metrics
                latency = time.time() - start_time
                webauthn_latency_seconds.labels(
                    operation="finish_authentication",
                    authenticator_type=stored_credential.authenticator_type.value
                ).observe(latency)

                webauthn_authentications_total.labels(
                    authenticator_type=stored_credential.authenticator_type.value,
                    status="success",
                    tier=stored_credential.tier.value
                ).inc()

                span.set_attribute("credential_id", credential_id)
                span.set_attribute("authenticator_type", stored_credential.authenticator_type.value)
                span.set_attribute("tier", stored_credential.tier.value)
                span.set_attribute("latency", latency)

                verification_result = {
                    "verified": verification.verified,
                    "sign_count": verification.new_sign_count,
                    "backup_eligible": getattr(verification, 'backup_eligible', False),
                    "backup_state": getattr(verification, 'backup_state', False)
                }

                return stored_credential, verification_result

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

                webauthn_authentications_total.labels(
                    authenticator_type="unknown",
                    status="error",
                    tier="unknown"
                ).inc()

                logger.error(f"WebAuthn authentication completion failed: {e}")
                raise

    def _determine_authenticator_type(self, verification) -> AuthenticatorType:
        """Determine authenticator type from verification data"""
        # This would analyze the attestation data to determine type
        # For now, default to platform authenticator
        return AuthenticatorType.PLATFORM

    def _check_biometric_enrollment(self, verification) -> bool:
        """Check if biometric authentication is enrolled"""
        # This would analyze the attestation data for biometric capabilities
        # For now, assume biometric if user verification is performed
        return getattr(verification, 'user_verified', False)

    def _get_device_name(self, verification) -> str:
        """Get device name from verification data"""
        # This would use the AAGUID to look up device information
        aaguid = verification.aaguid.hex() if verification.aaguid else None
        if aaguid and aaguid in self.authenticator_metadata:
            return self.authenticator_metadata[aaguid]["name"]
        return "Unknown Device"

    def _decode_credential_id(self, credential_id: Any) -> bytes:
        """Decode credential ID into bytes for PublicKeyCredentialDescriptor."""
        if isinstance(credential_id, bytes):
            return credential_id

        if isinstance(credential_id, str):
            padding = "=" * (-len(credential_id) % 4)
            try:
                return base64.urlsafe_b64decode(credential_id + padding)
            except (ValueError, binascii.Error):
                return credential_id.encode()

        raise TypeError("Unsupported credential_id type")

    def _build_credential_descriptors(self, credentials: list[WebAuthnCredential]):
        """Create PublicKeyCredentialDescriptor entries for provided credentials."""
        if not WEBAUTHN_AVAILABLE:
            raise RuntimeError("PublicKeyCredentialDescriptor is unavailable")

        descriptors = []
        for credential in credentials:
            credential_id_bytes = self._decode_credential_id(credential.credential_id)
            descriptors.append(PublicKeyCredentialDescriptor(id=credential_id_bytes))
        return descriptors

    async def list_user_credentials(self, user_id: str) -> list[dict[str, Any]]:
        """List all credentials for a user"""
        credentials = await self.credential_store.get_credentials(user_id)
        return [
            {
                "id": cred.credential_id,
                "device_name": cred.device_name,
                "authenticator_type": cred.authenticator_type.value,
                "tier": cred.tier.value,
                "status": cred.status.value,
                "created_at": cred.created_at.isoformat(),
                "last_used": cred.last_used.isoformat() if cred.last_used else None,
                "biometric_enrolled": cred.biometric_enrolled,
                "backup_eligible": cred.backup_eligible
            }
            for cred in credentials
        ]

    async def revoke_credential(self, credential_id: str) -> bool:
        """Revoke a WebAuthn credential"""
        credential = await self.credential_store.get_credential(credential_id)
        if not credential:
            return False

        credential.status = CredentialStatus.REVOKED
        await self.credential_store.update_credential(credential)

        # Update metrics
        webauthn_active_credentials.labels(
            user_tier=credential.tier.value,
            authenticator_type=credential.authenticator_type.value
        ).dec()

        return True


# Global WebAuthn manager instance
_global_webauthn_manager: WebAuthnManager | None = None

def get_webauthn_manager(rp_id: str = "ai",
                        rp_name: str = "LUKHAS AI",
                        origin: str = "https://ai") -> WebAuthnManager:
    """Get global WebAuthn manager instance"""
    global _global_webauthn_manager
    if _global_webauthn_manager is None:
        _global_webauthn_manager = WebAuthnManager(rp_id, rp_name, origin)
    return _global_webauthn_manager
