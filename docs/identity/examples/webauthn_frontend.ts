/**
 * WebAuthn Frontend Implementation (TypeScript)
 *
 * Complete client-side implementation of WebAuthn registration and
 * authentication flows. This demonstrates:
 * 1. Requesting registration options from backend
 * 2. Calling navigator.credentials.create() for registration
 * 3. Sending credential to backend for verification
 * 4. Requesting authentication options from backend
 * 5. Calling navigator.credentials.get() for authentication
 * 6. Sending assertion to backend for verification
 *
 * Prerequisites:
 * - TypeScript 4.0+
 * - Browser with WebAuthn support (Chrome 67+, Firefox 60+, Safari 13+)
 * - Backend API endpoints matching webauthn_registration.py / webauthn_authentication.py
 *
 * Usage:
 * - Import into React, Vue, Angular, or vanilla JavaScript
 * - Call handleRegistration() to start registration
 * - Call handleAuthentication() to start authentication
 *
 * Constellation Framework: Identity ⚛️ pillar
 * W3C WebAuthn Level 2 Specification: https://www.w3.org/TR/webauthn-2/
 */

// ============================================================================
// TypeScript Type Definitions
// ============================================================================

interface PublicKeyCredentialRpEntity {
    name: string;
    id: string;
}

interface PublicKeyCredentialUserEntity {
    id: string;
    name: string;
    displayName: string;
}

interface PublicKeyCredentialParameters {
    type: "public-key";
    alg: number;
}

interface PublicKeyCredentialDescriptor {
    type: "public-key";
    id: string;
    transports?: ("usb" | "nfc" | "ble" | "internal" | "hybrid")[];
}

interface AuthenticatorSelectionCriteria {
    authenticatorAttachment?: "platform" | "cross-platform";
    residentKey?: "discouraged" | "preferred" | "required";
    userVerification?: "required" | "preferred" | "discouraged";
}

interface CredentialCreationOptions {
    challenge: string | ArrayBuffer;
    rp: PublicKeyCredentialRpEntity;
    user: PublicKeyCredentialUserEntity;
    pubKeyCredParams: PublicKeyCredentialParameters[];
    timeout?: number;
    excludeCredentials?: PublicKeyCredentialDescriptor[];
    authenticatorSelection?: AuthenticatorSelectionCriteria;
    attestation?: "none" | "indirect" | "direct" | "enterprise";
    extensions?: Record<string, any>;
}

interface CredentialRequestOptions {
    challenge: string | ArrayBuffer;
    timeout?: number;
    rpId?: string;
    allowCredentials?: PublicKeyCredentialDescriptor[];
    userVerification?: "required" | "preferred" | "discouraged";
    extensions?: Record<string, any>;
}

interface AuthenticatorAttestationResponse extends AuthenticatorResponse {
    clientDataJSON: ArrayBuffer;
    attestationObject: ArrayBuffer;
    transports?: string[];
    publicKey?: ArrayBuffer;
    publicKeyAlgorithm?: number;
}

interface AuthenticatorAssertionResponse extends AuthenticatorResponse {
    clientDataJSON: ArrayBuffer;
    authenticatorData: ArrayBuffer;
    signature: ArrayBuffer;
    userHandle?: ArrayBuffer;
}

interface PublicKeyCredentialCreation {
    id: string;
    rawId: string;
    type: string;
    response: {
        clientDataJSON: string;
        attestationObject: string;
        transports?: string[];
    };
    authenticatorAttachment?: "platform" | "cross-platform";
    clientExtensionResults?: Record<string, any>;
}

interface PublicKeyCredentialAssertion {
    id: string;
    rawId: string;
    type: string;
    response: {
        clientDataJSON: string;
        authenticatorData: string;
        signature: string;
        userHandle?: string;
    };
    authenticatorAttachment?: "platform" | "cross-platform";
    clientExtensionResults?: Record<string, any>;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Convert base64url string to ArrayBuffer
 *
 * Base64url uses:
 * - '-' instead of '+'
 * - '_' instead of '/'
 * - No padding ('=' characters)
 *
 * @param base64url Base64url-encoded string
 * @returns ArrayBuffer
 */
function base64urlToBuffer(base64url: string): ArrayBuffer {
    // Add padding if needed
    const base64 = base64url
        .replace(/-/g, '+')
        .replace(/_/g, '/');
    const padded = base64 + '='.repeat((4 - base64.length % 4) % 4);

    // Decode to binary string
    const binary = atob(padded);

    // Convert to Uint8Array
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }

    return bytes.buffer;
}

/**
 * Convert ArrayBuffer to base64url string
 *
 * @param buffer ArrayBuffer to encode
 * @returns Base64url-encoded string
 */
function bufferToBase64url(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);

    // Convert bytes to binary string
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }

    // Encode as base64 and convert to base64url
    return btoa(binary)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

/**
 * Check browser WebAuthn support
 *
 * @returns true if WebAuthn is supported
 */
function isWebAuthnSupported(): boolean {
    return !!(
        navigator.credentials &&
        navigator.credentials.create &&
        navigator.credentials.get &&
        window.PublicKeyCredential
    );
}

/**
 * Check if platform authenticator (biometric) is available
 *
 * @returns true if platform authenticator is available
 */
async function isPlatformAuthenticatorAvailable(): Promise<boolean> {
    if (!isWebAuthnSupported()) {
        return false;
    }

    // Check if platform authenticator is available
    const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    return available;
}

// ============================================================================
// Registration Functions
// ============================================================================

/**
 * Request registration options from backend
 *
 * @param userId User identifier
 * @param username Email or username
 * @param displayName User's display name
 * @returns Registration options from backend
 */
async function requestRegistrationOptions(
    userId: string,
    username: string,
    displayName: string
): Promise<CredentialCreationOptions> {
    const response = await fetch('/api/auth/webauthn/register/begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            username: username,
            display_name: displayName
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Failed to get registration options: ${error.detail}`);
    }

    return response.json();
}

/**
 * Create credential using navigator.credentials.create()
 *
 * This calls the browser's WebAuthn API to prompt the user to create a new
 * credential on their authenticator (security key, Face ID, Touch ID, etc).
 *
 * @param options Registration options from backend
 * @returns Credential created on authenticator
 *
 * @throws NotAllowedError if user cancels or authenticator rejects
 * @throws InvalidStateError if credential already exists on authenticator
 * @throws SecurityError if HTTPS is not used (except localhost)
 */
async function createCredential(
    options: CredentialCreationOptions
): Promise<PublicKeyCredentialCreation> {
    // Convert challenge from base64url to ArrayBuffer
    const challengeBuffer = base64urlToBuffer(options.challenge as string);

    // Convert user ID from base64url to ArrayBuffer
    const userIdBuffer = base64urlToBuffer(options.user.id);

    // Build WebAuthn creation options
    const credentialOptions: CredentialCreationOptions = {
        ...options,
        challenge: challengeBuffer,
        user: {
            ...options.user,
            id: userIdBuffer
        }
    };

    // Convert exclude credentials to use ArrayBuffer
    if (credentialOptions.excludeCredentials) {
        credentialOptions.excludeCredentials = credentialOptions.excludeCredentials.map(cred => ({
            type: cred.type,
            id: base64urlToBuffer(cred.id),
            transports: cred.transports
        }));
    }

    try {
        // Call browser's WebAuthn API
        const credential = await navigator.credentials.create({
            publicKey: credentialOptions
        }) as PublicKeyCredential | null;

        if (!credential) {
            throw new Error('Failed to create credential - null result');
        }

        // Cast response to AttestationResponse
        const attestationResponse = credential.response as AuthenticatorAttestationResponse;

        // Convert response to send to backend
        return {
            id: credential.id,
            rawId: bufferToBase64url(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: bufferToBase64url(attestationResponse.clientDataJSON),
                attestationObject: bufferToBase64url(attestationResponse.attestationObject),
                transports: attestationResponse.transports || []
            },
            authenticatorAttachment: credential.authenticatorAttachment as any,
            clientExtensionResults: credential.getClientExtensionResults()
        };

    } catch (error: any) {
        // Provide user-friendly error messages
        if (error.name === 'NotAllowedError') {
            throw new Error(
                'Registration cancelled by user. Please try again.'
            );
        } else if (error.name === 'InvalidStateError') {
            throw new Error(
                'This authenticator already has a credential registered. ' +
                'Please use a different security key or re-register.'
            );
        } else if (error.name === 'SecurityError') {
            throw new Error(
                'HTTPS is required for WebAuthn (except on localhost). ' +
                'Please use a secure connection.'
            );
        } else if (error.name === 'TimeoutError') {
            throw new Error(
                'Registration timed out. Please check your authenticator and try again.'
            );
        } else if (error.name === 'NetworkError') {
            throw new Error(
                'Network error occurred. Please check your connection.'
            );
        }

        throw error;
    }
}

/**
 * Send credential to backend for verification and storage
 *
 * @param credential Credential from navigator.credentials.create()
 * @param userId User identifier
 * @param deviceName User-friendly device name
 */
async function sendCredentialToBackend(
    credential: PublicKeyCredentialCreation,
    userId: string,
    deviceName: string
): Promise<void> {
    const response = await fetch('/api/auth/webauthn/register/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            credential: credential,
            device_name: deviceName
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Registration failed: ${error.detail}`);
    }

    return response.json();
}

/**
 * Handle complete registration flow
 *
 * Steps:
 * 1. Get registration options from backend
 * 2. Call navigator.credentials.create()
 * 3. Send credential to backend
 *
 * @param userId User identifier
 * @param username Email or username
 * @param displayName User's display name
 * @param deviceName Device/key name (e.g., "Security Key", "Face ID")
 */
async function handleRegistration(
    userId: string,
    username: string,
    displayName: string,
    deviceName: string = "My Device"
): Promise<void> {
    // Check browser support
    if (!isWebAuthnSupported()) {
        throw new Error('WebAuthn is not supported in this browser');
    }

    console.log('Starting WebAuthn registration...');

    try {
        // Step 1: Get registration options from backend
        console.log('Requesting registration options from server...');
        const options = await requestRegistrationOptions(userId, username, displayName);
        console.log('Registration options received');

        // Step 2: Create credential on authenticator
        console.log('Prompting user to create credential on authenticator...');
        const credential = await createCredential(options);
        console.log('Credential created successfully');

        // Step 3: Send credential to backend for verification
        console.log('Sending credential to backend for verification...');
        await sendCredentialToBackend(credential, userId, deviceName);
        console.log('Registration complete!');

        // Show success message to user
        alert(`Security key "${deviceName}" registered successfully!`);

    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
}

// ============================================================================
// Authentication Functions
// ============================================================================

/**
 * Request authentication options from backend
 *
 * @param username Email or username to authenticate
 * @returns Authentication options from backend
 */
async function requestAuthenticationOptions(
    username: string
): Promise<CredentialRequestOptions> {
    const response = await fetch('/api/auth/webauthn/authenticate/begin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Failed to get authentication options: ${error.detail}`);
    }

    return response.json();
}

/**
 * Get assertion using navigator.credentials.get()
 *
 * This calls the browser's WebAuthn API to prompt the user to sign in with
 * their registered authenticator.
 *
 * @param options Authentication options from backend
 * @returns Assertion from authenticator
 */
async function getAssertion(
    options: CredentialRequestOptions
): Promise<PublicKeyCredentialAssertion> {
    // Convert challenge from base64url to ArrayBuffer
    const challengeBuffer = base64urlToBuffer(options.challenge as string);

    // Convert allow credentials to use ArrayBuffer
    const allowCredentials = options.allowCredentials?.map((cred: PublicKeyCredentialDescriptor) => ({
        type: cred.type,
        id: base64urlToBuffer(cred.id),
        transports: cred.transports
    })) || [];

    // Build WebAuthn get options
    const getOptions: CredentialRequestOptions = {
        challenge: challengeBuffer,
        rpId: options.rpId,
        allowCredentials: allowCredentials as any,
        userVerification: options.userVerification,
        timeout: options.timeout
    };

    try {
        // Call browser's WebAuthn API
        const assertion = await navigator.credentials.get({
            publicKey: getOptions as any
        }) as PublicKeyCredential | null;

        if (!assertion) {
            throw new Error('Failed to get assertion - null result');
        }

        // Cast response to AssertionResponse
        const assertionResponse = assertion.response as AuthenticatorAssertionResponse;

        // Convert response to send to backend
        return {
            id: assertion.id,
            rawId: bufferToBase64url(assertion.rawId),
            type: assertion.type,
            response: {
                clientDataJSON: bufferToBase64url(assertionResponse.clientDataJSON),
                authenticatorData: bufferToBase64url(assertionResponse.authenticatorData),
                signature: bufferToBase64url(assertionResponse.signature),
                userHandle: assertionResponse.userHandle ?
                    bufferToBase64url(assertionResponse.userHandle) : undefined
            },
            authenticatorAttachment: assertion.authenticatorAttachment as any,
            clientExtensionResults: assertion.getClientExtensionResults()
        };

    } catch (error: any) {
        // Provide user-friendly error messages
        if (error.name === 'NotAllowedError') {
            throw new Error(
                'Authentication cancelled by user. Please try again.'
            );
        } else if (error.name === 'TimeoutError') {
            throw new Error(
                'Authentication timed out. Please check your authenticator and try again.'
            );
        } else if (error.name === 'SecurityError') {
            throw new Error(
                'HTTPS is required for WebAuthn (except on localhost). ' +
                'Please use a secure connection.'
            );
        } else if (error.name === 'NetworkError') {
            throw new Error(
                'Network error occurred. Please check your connection.'
            );
        }

        throw error;
    }
}

/**
 * Send assertion to backend for verification
 *
 * @param assertion Assertion from navigator.credentials.get()
 * @param username Username being authenticated
 * @returns Session token or authentication response
 */
async function sendAssertionToBackend(
    assertion: PublicKeyCredentialAssertion,
    username: string
): Promise<any> {
    const response = await fetch('/api/auth/webauthn/authenticate/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: username,
            credential: assertion
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Authentication failed: ${error.detail}`);
    }

    return response.json();
}

/**
 * Handle complete authentication flow
 *
 * Steps:
 * 1. Get authentication options from backend
 * 2. Call navigator.credentials.get()
 * 3. Send assertion to backend
 *
 * @param username Email or username to authenticate
 * @returns Authentication result (session token, etc)
 */
async function handleAuthentication(username: string): Promise<any> {
    // Check browser support
    if (!isWebAuthnSupported()) {
        throw new Error('WebAuthn is not supported in this browser');
    }

    console.log('Starting WebAuthn authentication...');

    try {
        // Step 1: Get authentication options from backend
        console.log('Requesting authentication options from server...');
        const options = await requestAuthenticationOptions(username);
        console.log('Authentication options received');

        // Step 2: Get assertion from authenticator
        console.log('Prompting user to authenticate with security key...');
        const assertion = await getAssertion(options);
        console.log('Assertion created successfully');

        // Step 3: Send assertion to backend for verification
        console.log('Sending assertion to backend for verification...');
        const result = await sendAssertionToBackend(assertion, username);
        console.log('Authentication successful!');

        // Store session token if provided
        if (result.session_token) {
            localStorage.setItem('auth_token', result.session_token);
        }

        return result;

    } catch (error) {
        console.error('Authentication failed:', error);
        throw error;
    }
}

// ============================================================================
// Credential Management Functions
// ============================================================================

/**
 * List user's registered WebAuthn credentials
 *
 * @param userId User identifier
 * @returns List of registered credentials
 */
async function listCredentials(userId: string): Promise<any[]> {
    const response = await fetch(`/api/auth/webauthn/credentials?user_id=${userId}`);

    if (!response.ok) {
        throw new Error('Failed to load credentials');
    }

    const data = await response.json();
    return data.credentials;
}

/**
 * Delete a registered credential
 *
 * @param credentialId Credential ID to delete
 * @param userId User identifier
 */
async function deleteCredential(credentialId: string, userId: string): Promise<void> {
    const response = await fetch(
        `/api/auth/webauthn/credentials/${credentialId}?user_id=${userId}`,
        { method: 'DELETE' }
    );

    if (!response.ok) {
        throw new Error('Failed to delete credential');
    }
}

/**
 * Update credential metadata (device name, etc)
 *
 * @param credentialId Credential ID to update
 * @param userId User identifier
 * @param deviceName New device name
 */
async function updateCredentialName(
    credentialId: string,
    userId: string,
    deviceName: string
): Promise<void> {
    const response = await fetch(
        `/api/auth/webauthn/credentials/${credentialId}?user_id=${userId}`,
        {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_name: deviceName })
        }
    );

    if (!response.ok) {
        throw new Error('Failed to update credential');
    }
}

// ============================================================================
// React Component Example
// ============================================================================

/**
 * Example React component for WebAuthn registration
 *
 * Usage:
 * <WebAuthnRegistrationButton userId="123" username="user@example.com" />
 */
export const WebAuthnRegistrationButton: React.FC<{
    userId: string;
    username: string;
}> = ({ userId, username }) => {
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [success, setSuccess] = React.useState(false);

    const handleClick = async () => {
        setLoading(true);
        setError(null);

        try {
            await handleRegistration(
                userId,
                username,
                username.split('@')[0],
                `Security Key`
            );
            setSuccess(true);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return <div className="alert-success">Registration complete!</div>;
    }

    return (
        <div>
            <button onClick={handleClick} disabled={loading}>
                {loading ? 'Registering...' : 'Register Security Key'}
            </button>
            {error && <div className="alert-error">{error}</div>}
        </div>
    );
};

/**
 * Example React component for WebAuthn authentication
 *
 * Usage:
 * <WebAuthnAuthenticationButton username="user@example.com" onSuccess={handleAuth} />
 */
export const WebAuthnAuthenticationButton: React.FC<{
    username: string;
    onSuccess?: (result: any) => void;
}> = ({ username, onSuccess }) => {
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const handleClick = async () => {
        setLoading(true);
        setError(null);

        try {
            const result = await handleAuthentication(username);
            onSuccess?.(result);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <button onClick={handleClick} disabled={loading}>
                {loading ? 'Authenticating...' : 'Sign in with Security Key'}
            </button>
            {error && <div className="alert-error">{error}</div>}
        </div>
    );
};

// ============================================================================
// Exports
// ============================================================================

export {
    // Main flows
    handleRegistration,
    handleAuthentication,

    // Individual functions
    requestRegistrationOptions,
    createCredential,
    sendCredentialToBackend,
    requestAuthenticationOptions,
    getAssertion,
    sendAssertionToBackend,

    // Credential management
    listCredentials,
    deleteCredential,
    updateCredentialName,

    // Utilities
    base64urlToBuffer,
    bufferToBase64url,
    isWebAuthnSupported,
    isPlatformAuthenticatorAvailable,

    // Types
    PublicKeyCredentialCreation,
    PublicKeyCredentialAssertion,
    CredentialCreationOptions,
    CredentialRequestOptions
};
