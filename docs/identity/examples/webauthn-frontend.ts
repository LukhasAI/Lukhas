/**
 * WebAuthn Frontend Example (TypeScript)
 *
 * This script provides a conceptual example of how a frontend application
 * would use the `navigator.credentials` API to handle WebAuthn registration
 * and authentication ceremonies.
 *
 * NOTE: This is a conceptual, browser-focused example. It is not a complete
 * frontend component (e.g., React, Vue, Angular) but demonstrates the core logic.
 */

// --- Type Definitions (from lukhas_website/lukhas/identity/webauthn_types.py) ---
// These would typically be generated or defined in a shared types file.

interface CredentialCreationOptions {
  challenge: string;
  rp: { name: string; id?: string };
  user: { id: string; name: string; displayName: string };
  pubKeyCredParams: { type: "public-key"; alg: number }[];
  // ... and other optional fields
}

interface CredentialRequestOptions {
  challenge: string;
  allowCredentials?: { type: "public-key"; id: string }[];
  // ... and other optional fields
}

// Helper function to convert Base64URL strings to ArrayBuffers
// (The browser API requires ArrayBuffers for many fields)
function base64urlToBuffer(base64urlString: string): ArrayBuffer {
  const padding = "=".repeat((4 - (base64urlString.length % 4)) % 4);
  const base64 = (base64urlString + padding).replace(/\-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray.buffer;
}

/**
 * Handles the WebAuthn registration process on the frontend.
 */
async function handleRegistration() {
  try {
    // 1. Fetch registration options from the server
    const response = await fetch("/api/webauthn/generate-registration-options");
    const options: CredentialCreationOptions = await response.json();

    // The server sends the challenge as a Base64URL string, but the API needs an ArrayBuffer
    options.challenge = base64urlToBuffer(options.challenge);
    // The user ID must also be an ArrayBuffer
    options.user.id = base64urlToBuffer(options.user.id);

    console.log("Registration Options from Server:", options);

    // 2. Call navigator.credentials.create() to prompt the user
    const credential = await navigator.credentials.create({ publicKey: options });

    console.log("Credential created:", credential);

    // 3. Send the resulting credential to the server for verification
    // The frontend does not need to understand the contents of the response object.
    // It just sends it back to the server to be verified and stored.
    await fetch("/api/webauthn/verify-registration", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credential),
    });

    alert("Registration successful!");
  } catch (error) {
    console.error("Registration failed:", error);
    alert(`Registration failed: ${error}`);
  }
}

/**
 * Handles the WebAuthn authentication process on the frontend.
 */
async function handleAuthentication() {
  try {
    // 1. Fetch authentication options from the server
    const response = await fetch("/api/webauthn/generate-authentication-options");
    const options: CredentialRequestOptions = await response.json();

    // Convert challenge and any credential IDs from Base64URL to ArrayBuffer
    options.challenge = base64urlToBuffer(options.challenge);
    if (options.allowCredentials) {
      for (const cred of options.allowCredentials) {
        cred.id = base64urlToBuffer(cred.id);
      }
    }

    console.log("Authentication Options from Server:", options);

    // 2. Call navigator.credentials.get() to prompt the user
    const assertion = await navigator.credentials.get({ publicKey: options });

    console.log("Assertion created:", assertion);

    // 3. Send the assertion to the server for verification
    await fetch("/api/webauthn/verify-authentication", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(assertion),
    });

    alert("Authentication successful!");
  } catch (error) {
    console.error("Authentication failed:", error);
    alert(`Authentication failed: ${error}`);
  }
}

// Example of how you might trigger these functions
// document.getElementById('register-button').addEventListener('click', handleRegistration);
// document.getElementById('login-button').addEventListener('click', handleAuthentication);
