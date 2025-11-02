// WebAuthn Frontend Example (TypeScript)

import { CredentialCreationOptions, CredentialRequestOptions } from './webauthn_types';

// --- Registration ---

async function register(options: CredentialCreationOptions): Promise<void> {
  try {
    const credential = await navigator.credentials.create({ publicKey: options });
    console.log("Registration successful!", credential);

    // Send the credential to the backend for verification
    // await sendToServer('/register/finish', credential);
  } catch (err) {
    console.error("Registration failed:", err);
  }
}

// --- Authentication ---

async function authenticate(options: CredentialRequestOptions): Promise<void> {
  try {
    const assertion = await navigator.credentials.get({ publicKey: options });
    console.log("Authentication successful!", assertion);

    // Send the assertion to the backend for verification
    // await sendToServer('/authenticate/finish', assertion);
  } catch (err) {
    console.error("Authentication failed:", err);
  }
}

// --- Example Usage ---

// In a real application, you would fetch these options from your backend.

// Example registration options
const registrationOptions: CredentialCreationOptions = {
  challenge: "...".toString(), // Replace with a real challenge from the server
  rp: {
    name: "LUKHAS Demo",
    id: "localhost",
  },
  user: {
    id: "...".toString(), // Replace with a real user ID
    name: "testuser",
    displayName: "Test User",
  },
  pubKeyCredParams: [{ alg: -7, type: "public-key" }],
  timeout: 60000,
  attestation: "direct",
};

// Example authentication options
const authenticationOptions: CredentialRequestOptions = {
  challenge: "...".toString(), // Replace with a real challenge from the server
  allowCredentials: [
    {
      type: "public-key",
      id: "...".toString(), // Replace with a real credential ID
    },
  ],
  timeout: 60000,
};

// You would call these functions based on user actions.
// For example, when a user clicks a "Register" or "Login" button.

// register(registrationOptions);
// authenticate(authenticationOptions);
