#!/usr/bin/env python3
"""
WebAuthn Type Definitions - W3C WebAuthn API TypedDict structures

This module provides TypedDict definitions for WebAuthn data structures
following the W3C WebAuthn Level 2 specification. These types enable
proper type checking for WebAuthn credential creation and authentication
flows.

Constellation Framework: Identity ⚛️ pillar
Specification: https://www.w3.org/TR/webauthn-2/

Part of Task #591 - Define WebAuthn Types (PREREQUISITE for #581, #589, #597, #599)
"""
from __future__ import annotations

from typing import Any, Literal, Union

from typing_extensions import NotRequired, TypedDict

# Base WebAuthn Types

class PublicKeyCredentialRpEntity(TypedDict):
    """Relying Party entity descriptor.

    Describes the organization responsible for the registration and
    authentication ceremony.
    """
    name: str
    id: NotRequired[str]


class PublicKeyCredentialUserEntity(TypedDict):
    """User entity descriptor.

    Describes the user account for which the credential is generated.
    """
    id: str  # Base64url-encoded user handle
    name: str
    displayName: str


class PublicKeyCredentialParameters(TypedDict):
    """Cryptographic parameters for credential generation.

    Specifies the public key algorithm and credential type.
    """
    type: Literal["public-key"]
    alg: int  # COSE algorithm identifier (e.g., -7 for ES256, -257 for RS256)


class PublicKeyCredentialDescriptor(TypedDict):
    """Descriptor for a public key credential.

    Used to identify existing credentials or specify allowed credentials.
    """
    type: Literal["public-key"]
    id: str  # Base64url-encoded credential ID
    transports: NotRequired[list[Literal["usb", "nfc", "ble", "internal", "hybrid"]]]


class AuthenticatorSelectionCriteria(TypedDict):
    """Criteria for selecting authenticators during registration.

    Specifies requirements for the authenticator to be used.
    """
    authenticatorAttachment: NotRequired[Literal["platform", "cross-platform"]]
    residentKey: NotRequired[Literal["discouraged", "preferred", "required"]]
    requireResidentKey: NotRequired[bool]
    userVerification: NotRequired[Literal["required", "preferred", "discouraged"]]


# Credential Creation (Registration) Types

class CredentialCreationOptions(TypedDict):
    """Options for creating a new public key credential (registration).

    Passed to navigator.credentials.create() in the browser.
    """
    challenge: str  # Base64url-encoded challenge
    rp: PublicKeyCredentialRpEntity
    user: PublicKeyCredentialUserEntity
    pubKeyCredParams: list[PublicKeyCredentialParameters]
    timeout: NotRequired[int]  # Milliseconds
    excludeCredentials: NotRequired[list[PublicKeyCredentialDescriptor]]
    authenticatorSelection: NotRequired[AuthenticatorSelectionCriteria]
    attestation: NotRequired[Literal["none", "indirect", "direct", "enterprise"]]
    extensions: NotRequired[dict[str, Any]]


class AuthenticatorAttestationResponse(TypedDict):
    """Response from authenticator during registration.

    Contains the attestation object and client data JSON.
    """
    clientDataJSON: str  # Base64url-encoded client data
    attestationObject: str  # Base64url-encoded attestation object
    transports: NotRequired[list[Literal["usb", "nfc", "ble", "internal", "hybrid"]]]
    authenticatorData: NotRequired[str]  # Base64url-encoded authenticator data
    publicKey: NotRequired[str]  # Base64url-encoded public key (DER SubjectPublicKeyInfo)
    publicKeyAlgorithm: NotRequired[int]  # COSE algorithm identifier


class PublicKeyCredentialCreation(TypedDict):
    """Public key credential from registration ceremony.

    The complete credential object returned from navigator.credentials.create().
    """
    id: str  # Base64url-encoded credential ID
    rawId: str  # Base64url-encoded credential ID
    type: Literal["public-key"]
    response: AuthenticatorAttestationResponse
    authenticatorAttachment: NotRequired[Literal["platform", "cross-platform"]]
    clientExtensionResults: NotRequired[dict[str, Any]]


# Credential Request (Authentication) Types

class CredentialRequestOptions(TypedDict):
    """Options for requesting credential authentication.

    Passed to navigator.credentials.get() in the browser.
    """
    challenge: str  # Base64url-encoded challenge
    timeout: NotRequired[int]  # Milliseconds
    rpId: NotRequired[str]
    allowCredentials: NotRequired[list[PublicKeyCredentialDescriptor]]
    userVerification: NotRequired[Literal["required", "preferred", "discouraged"]]
    extensions: NotRequired[dict[str, Any]]


class AuthenticatorAssertionResponse(TypedDict):
    """Response from authenticator during authentication.

    Contains the assertion signature and related data.
    """
    clientDataJSON: str  # Base64url-encoded client data
    authenticatorData: str  # Base64url-encoded authenticator data
    signature: str  # Base64url-encoded signature
    userHandle: NotRequired[str]  # Base64url-encoded user handle


class PublicKeyCredentialAssertion(TypedDict):
    """Public key credential from authentication ceremony.

    The complete credential object returned from navigator.credentials.get().
    """
    id: str  # Base64url-encoded credential ID
    rawId: str  # Base64url-encoded credential ID
    type: Literal["public-key"]
    response: AuthenticatorAssertionResponse
    authenticatorAttachment: NotRequired[Literal["platform", "cross-platform"]]
    clientExtensionResults: NotRequired[dict[str, Any]]


# Convenience Type Aliases

# Generic credential type that can be either registration or authentication
PublicKeyCredential = Union[PublicKeyCredentialCreation, PublicKeyCredentialAssertion]


# Server-side verification structures (internal use)

class VerifiedRegistration(TypedDict):
    """Result of server-side registration verification.

    Internal type for webauthn library verification results.
    """
    verified: bool
    credential_id: bytes
    credential_public_key: bytes
    sign_count: int
    aaguid: NotRequired[bytes]
    attestation_object: NotRequired[dict[str, Any]]
    backup_eligible: NotRequired[bool]
    backup_state: NotRequired[bool]
    user_verified: NotRequired[bool]


class VerifiedAuthentication(TypedDict):
    """Result of server-side authentication verification.

    Internal type for webauthn library verification results.
    """
    verified: bool
    new_sign_count: int
    backup_eligible: NotRequired[bool]
    backup_state: NotRequired[bool]
    user_verified: NotRequired[bool]


__all__ = [
    # Relying Party and User entities
    "PublicKeyCredentialRpEntity",
    "PublicKeyCredentialUserEntity",

    # Credential parameters and descriptors
    "PublicKeyCredentialParameters",
    "PublicKeyCredentialDescriptor",
    "AuthenticatorSelectionCriteria",

    # Registration (creation) types
    "CredentialCreationOptions",
    "AuthenticatorAttestationResponse",
    "PublicKeyCredentialCreation",

    # Authentication (assertion) types
    "CredentialRequestOptions",
    "AuthenticatorAssertionResponse",
    "PublicKeyCredentialAssertion",

    # Generic types
    "PublicKeyCredential",

    # Verification results (server-side)
    "VerifiedRegistration",
    "VerifiedAuthentication",
]
