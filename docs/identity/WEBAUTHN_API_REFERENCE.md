# WebAuthn API Reference

This document provides a detailed reference for the WebAuthn `TypedDict` definitions used in LUKHAS.

## Base WebAuthn Types

### `PublicKeyCredentialRpEntity`
Relying Party entity descriptor. Describes the organization responsible for the registration and authentication ceremony.

| Field | Type | Description |
|---|---|---|
| `name` | `str` | The name of the Relying Party. |
| `id` | `NotRequired[str]` | The ID of the Relying Party. |

### `PublicKeyCredentialUserEntity`
User entity descriptor. Describes the user account for which the credential is generated.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Base64url-encoded user handle. |
| `name` | `str` | The user's name. |
| `displayName` | `str` | The user's display name. |

### `PublicKeyCredentialParameters`
Cryptographic parameters for credential generation. Specifies the public key algorithm and credential type.

| Field | Type | Description |
|---|---|---|
| `type` | `Literal["public-key"]` | The type of the credential. |
| `alg` | `int` | The COSE algorithm identifier. |

### `PublicKeyCredentialDescriptor`
Descriptor for a public key credential. Used to identify existing credentials or specify allowed credentials.

| Field | Type | Description |
|---|---|---|
| `type` | `Literal["public-key"]` | The type of the credential. |
| `id` | `str` | Base64url-encoded credential ID. |
| `transports` | `NotRequired[list[Literal["usb", "nfc", "ble", "internal", "hybrid"]]]` | A list of transports that can be used with the credential. |

### `AuthenticatorSelectionCriteria`
Criteria for selecting authenticators during registration. Specifies requirements for the authenticator to be used.

| Field | Type | Description |
|---|---|---|
| `authenticatorAttachment` | `NotRequired[Literal["platform", "cross-platform"]]` | The authenticator attachment. |
| `residentKey` | `NotRequired[Literal["discouraged", "preferred", "required"]]` | The resident key requirement. |
| `requireResidentKey` | `NotRequired[bool]` | Whether a resident key is required. |
| `userVerification` | `NotRequired[Literal["required", "preferred", "discouraged"]]` | The user verification requirement. |

## Credential Creation (Registration) Types

### `CredentialCreationOptions`
Options for creating a new public key credential (registration). Passed to `navigator.credentials.create()` in the browser.

| Field | Type | Description |
|---|---|---|
| `challenge` | `str` | Base64url-encoded challenge. |
| `rp` | `PublicKeyCredentialRpEntity` | The Relying Party entity. |
| `user` | `PublicKeyCredentialUserEntity` | The user entity. |
| `pubKeyCredParams` | `list[PublicKeyCredentialParameters]` | A list of public key credential parameters. |
| `timeout` | `NotRequired[int]` | The timeout in milliseconds. |
| `excludeCredentials` | `NotRequired[list[PublicKeyCredentialDescriptor]]` | A list of credentials to exclude. |
| `authenticatorSelection` | `NotRequired[AuthenticatorSelectionCriteria]` | The authenticator selection criteria. |
| `attestation` | `NotRequired[Literal["none", "indirect", "direct", "enterprise"]]` | The attestation type. |
| `extensions` | `NotRequired[dict[str, Any]]` | A dictionary of extensions. |

### `AuthenticatorAttestationResponse`
Response from authenticator during registration. Contains the attestation object and client data JSON.

| Field | Type | Description |
|---|---|---|
| `clientDataJSON` | `str` | Base64url-encoded client data. |
| `attestationObject` | `str` | Base64url-encoded attestation object. |
| `transports` | `NotRequired[list[Literal["usb", "nfc", "ble", "internal", "hybrid"]]]` | A list of transports. |
| `authenticatorData` | `NotRequired[str]` | Base64url-encoded authenticator data. |
| `publicKey` | `NotRequired[str]` | Base64url-encoded public key. |
| `publicKeyAlgorithm` | `NotRequired[int]` | The COSE algorithm identifier. |

### `PublicKeyCredentialCreation`
Public key credential from registration ceremony. The complete credential object returned from `navigator.credentials.create()`.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Base64url-encoded credential ID. |
| `rawId` | `str` | Base64url-encoded credential ID. |
| `type` | `Literal["public-key"]` | The type of the credential. |
| `response` | `AuthenticatorAttestationResponse` | The authenticator attestation response. |
| `authenticatorAttachment` | `NotRequired[Literal["platform", "cross-platform"]]` | The authenticator attachment. |
| `clientExtensionResults` | `NotRequired[dict[str, Any]]` | A dictionary of client extension results. |

## Credential Request (Authentication) Types

### `CredentialRequestOptions`
Options for requesting credential authentication. Passed to `navigator.credentials.get()` in the browser.

| Field | Type | Description |
|---|---|---|
| `challenge` | `str` | Base64url-encoded challenge. |
| `timeout` | `NotRequired[int]` | The timeout in milliseconds. |
| `rpId` | `NotRequired[str]` | The Relying Party ID. |
| `allowCredentials` | `NotRequired[list[PublicKeyCredentialDescriptor]]` | A list of allowed credentials. |
| `userVerification` | `NotRequired[Literal["required", "preferred", "discouraged"]]` | The user verification requirement. |
| `extensions` | `NotRequired[dict[str, Any]]` | A dictionary of extensions. |

### `AuthenticatorAssertionResponse`
Response from authenticator during authentication. Contains the assertion signature and related data.

| Field | Type | Description |
|---|---|---|
| `clientDataJSON` | `str` | Base64url-encoded client data. |
| `authenticatorData` | `str` | Base64url-encoded authenticator data. |
| `signature` | `str` | Base64url-encoded signature. |
| `userHandle` | `NotRequired[str]` | Base64url-encoded user handle. |

### `PublicKeyCredentialAssertion`
Public key credential from authentication ceremony. The complete credential object returned from `navigator.credentials.get()`.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Base64url-encoded credential ID. |
| `rawId` | `str` | Base64url-encoded credential ID. |
| `type` | `Literal["public-key"]` | The type of the credential. |
| `response` | `AuthenticatorAssertionResponse` | The authenticator assertion response. |
| `authenticatorAttachment` | `NotRequired[Literal["platform", "cross-platform"]]` | The authenticator attachment. |
| `clientExtensionResults` | `NotRequired[dict[str, Any]]` | A dictionary of client extension results. |

## Server-side verification structures

### `VerifiedRegistration`
Result of server-side registration verification. Internal type for webauthn library verification results.

| Field | Type | Description |
|---|---|---|
| `verified` | `bool` | Whether the registration was verified. |
| `credential_id` | `bytes` | The credential ID. |
| `credential_public_key` | `bytes` | The credential public key. |
| `sign_count` | `int` | The signature count. |
| `aaguid` | `NotRequired[bytes]` | The AAGUID. |
| `attestation_object` | `NotRequired[dict[str, Any]]` | The attestation object. |
| `backup_eligible` | `NotRequired[bool]` | Whether the credential is backup eligible. |
| `backup_state` | `NotRequired[bool]` | The backup state. |
| `user_verified` | `NotRequired[bool]` | Whether the user was verified. |

### `VerifiedAuthentication`
Result of server-side authentication verification. Internal type for webauthn library verification results.

| Field | Type | Description |
|---|---|---|
| `verified` | `bool` | Whether the authentication was verified. |
| `new_sign_count` | `int` | The new signature count. |
| `backup_eligible` | `NotRequired[bool]` | Whether the credential is backup eligible. |
| `backup_state` | `NotRequired[bool]` | The backup state. |
| `user_verified` | `NotRequired[bool]` | Whether the user was verified. |
