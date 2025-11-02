# WebAuthn API Reference

This document provides a detailed reference for the Python `TypedDict` data structures used in the LUKHAS WebAuthn implementation. These types are based on the [W3C WebAuthn Level 2 specification](https://www.w3.org/TR/webauthn-2/).

---

## Table of Contents

- [Base Types](#base-types)
- [Registration Types](#registration-types)
- [Authentication Types](#authentication-types)
- [Server-Side Verification Types](#server-side-verification-types)

---

## Base Types

These types are fundamental building blocks used in both registration and authentication ceremonies.

### `PublicKeyCredentialRpEntity`

Describes the Relying Party (the application or service).

```python
class PublicKeyCredentialRpEntity(TypedDict):
    name: str
    id: NotRequired[str]
```

- `name`: A human-readable name for the Relying Party.
- `id`: The domain of the Relying Party. If not provided, it defaults to the current domain.

### `PublicKeyCredentialUserEntity`

Describes the user account.

```python
class PublicKeyCredentialUserEntity(TypedDict):
    id: str
    name: str
    displayName: str
```

- `id`: A unique, non-personally identifiable user handle (should be Base64URL encoded).
- `name`: The user's username (e.g., `user@example.com`).
- `displayName`: A human-readable name for the user (e.g., "Jane Doe").

### `PublicKeyCredentialParameters`

Defines the cryptographic algorithms supported.

```python
class PublicKeyCredentialParameters(TypedDict):
    type: Literal["public-key"]
    alg: int
```

- `type`: Must be `"public-key"`.
- `alg`: A COSE algorithm identifier (e.g., -7 for ES256).

### `PublicKeyCredentialDescriptor`

Identifies an existing credential.

```python
class PublicKeyCredentialDescriptor(TypedDict):
    type: Literal["public-key"]
    id: str
    transports: NotRequired[list[Literal["usb", "nfc", "ble", "internal", "hybrid"]]]
```

- `type`: Must be `"public-key"`.
- `id`: The Base64URL-encoded ID of a previously registered credential.
- `transports`: Hints for how the client might communicate with the authenticator.

### `AuthenticatorSelectionCriteria`

Specifies requirements for the desired authenticator.

```python
class AuthenticatorSelectionCriteria(TypedDict):
    authenticatorAttachment: NotRequired[Literal["platform", "cross-platform"]]
    residentKey: NotRequired[Literal["discouraged", "preferred", "required"]]
    requireResidentKey: NotRequired[bool]
    userVerification: NotRequired[Literal["required", "preferred", "discouraged"]]
```

- `authenticatorAttachment`: `"platform"` (e.g., Touch ID) or `"cross-platform"` (e.g., YubiKey).
- `residentKey`: Whether to create a client-side discoverable credential.
- `userVerification`: Whether the user must be verified (e.g., with a biometric or PIN).

---

## Registration Types

These types are used when creating a new credential.

### `CredentialCreationOptions`

Options sent from the server to the browser to initiate registration.

```python
class CredentialCreationOptions(TypedDict):
    challenge: str
    rp: PublicKeyCredentialRpEntity
    user: PublicKeyCredentialUserEntity
    pubKeyCredParams: list[PublicKeyCredentialParameters]
    timeout: NotRequired[int]
    excludeCredentials: NotRequired[list[PublicKeyCredentialDescriptor]]
    authenticatorSelection: NotRequired[AuthenticatorSelectionCriteria]
    attestation: NotRequired[Literal["none", "indirect", "direct", "enterprise"]]
    extensions: NotRequired[dict[str, Any]]
```

### `AuthenticatorAttestationResponse`

Part of the data returned from the browser after a successful `navigator.credentials.create()` call.

```python
class AuthenticatorAttestationResponse(TypedDict):
    clientDataJSON: str
    attestationObject: str
    transports: NotRequired[list[Literal[...]]]
    authenticatorData: NotRequired[str]
    publicKey: NotRequired[str]
    publicKeyAlgorithm: NotRequired[int]
```

### `PublicKeyCredentialCreation`

The full credential object returned by the browser upon registration.

```python
class PublicKeyCredentialCreation(TypedDict):
    id: str
    rawId: str
    type: Literal["public-key"]
    response: AuthenticatorAttestationResponse
    authenticatorAttachment: NotRequired[Literal[...]]
    clientExtensionResults: NotRequired[dict[str, Any]]
```

---

## Authentication Types

These types are used when authenticating a user with an existing credential.

### `CredentialRequestOptions`

Options sent from the server to the browser to initiate authentication.

```python
class CredentialRequestOptions(TypedDict):
    challenge: str
    timeout: NotRequired[int]
    rpId: NotRequired[str]
    allowCredentials: NotRequired[list[PublicKeyCredentialDescriptor]]
    userVerification: NotRequired[Literal[...]]
    extensions: NotRequired[dict[str, Any]]
```

### `AuthenticatorAssertionResponse`

Part of the data returned from the browser after a successful `navigator.credentials.get()` call.

```python
class AuthenticatorAssertionResponse(TypedDict):
    clientDataJSON: str
    authenticatorData: str
    signature: str
    userHandle: NotRequired[str]
```

### `PublicKeyCredentialAssertion`

The full credential object returned by the browser upon authentication.

```python
class PublicKeyCredentialAssertion(TypedDict):
    id: str
    rawId: str
    type: Literal["public-key"]
    response: AuthenticatorAssertionResponse
    authenticatorAttachment: NotRequired[Literal[...]]
    clientExtensionResults: NotRequired[dict[str, Any]]
```

---

## Server-Side Verification Types

These types are used internally on the server after verifying the data from the browser.

### `VerifiedRegistration`

Represents the result of a successful registration verification.

```python
class VerifiedRegistration(TypedDict):
    verified: bool
    credential_id: bytes
    credential_public_key: bytes
    sign_count: int
    ...
```

### `VerifiedAuthentication`

Represents the result of a successful authentication verification.

```python
class VerifiedAuthentication(TypedDict):
    verified: bool
    new_sign_count: int
    ...
```
