// WebAuthn passkey implementation stubs
import { randomBytes } from 'crypto';

export async function startRegistration({ userId, username, displayName }: {
  userId: string;
  username: string;
  displayName: string;
}) {
  const challenge = randomBytes(32);
  return {
    challenge: Array.from(challenge),
    rp: {
      name: 'LUKHAS AI',
      id: process.env.NEXT_PUBLIC_RPID || 'localhost'
    },
    user: {
      id: Array.from(Buffer.from(userId)),
      name: username,
      displayName
    },
    pubKeyCredParams: [
      { alg: -7, type: 'public-key' },  // ES256
      { alg: -257, type: 'public-key' } // RS256
    ],
    timeout: 60000,
    attestation: 'direct',
    authenticatorSelection: {
      authenticatorAttachment: 'platform',
      userVerification: 'required',
      residentKey: 'preferred'
    }
  };
}

export async function finishRegistration({ userId, response }: {
  userId: string;
  response: any;
}) {
# See: https://github.com/LukhasAI/Lukhas/issues/598
  return { success: true, credentialId: response.id };
}

export async function startAuthentication({ userId }: { userId?: string }) {
  const challenge = randomBytes(32);
  return {
    challenge: Array.from(challenge),
    allowCredentials: [], // Empty to allow any registered credential
    userVerification: 'required',
    timeout: 60000
  };
}

export async function finishAuthentication({ userId, response, deviceId }: {
  userId: string;
  response: any;
  deviceId?: string;
}) {
# See: https://github.com/LukhasAI/Lukhas/issues/599
  return { ok: true, userId };
}
