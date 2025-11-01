// WebAuthn passkey implementation utilities (simplified server-side logic)
import { createHash, randomBytes } from 'crypto';

type PublicKeyCredentialDescriptor = {
  type: 'public-key';
  id: number[];
  transports?: string[];
};

interface RegistrationOptions {
  challenge: number[];
  rp: {
    name: string;
    id: string;
  };
  user: {
    id: number[];
    name: string;
    displayName: string;
  };
  pubKeyCredParams: { alg: number; type: 'public-key' }[];
  timeout: number;
  attestation: 'direct';
  authenticatorSelection: {
    authenticatorAttachment: 'platform';
    userVerification: 'required';
    residentKey: 'preferred';
  };
}

interface RegistrationResult {
  success: boolean;
  credentialId?: string;
  error?: string;
}

interface AuthenticationOptions {
  challenge: number[];
  rpId: string;
  allowCredentials: PublicKeyCredentialDescriptor[];
  userVerification: 'required';
  timeout: number;
}

interface AuthenticationResult {
  ok: boolean;
  userId?: string;
  credentialId?: string;
  signCount?: number;
  error?: string;
}

interface StoredCredential {
  userId: string;
  credentialId: string;
  signCount: number;
  transports: string[];
  createdAt: string;
  updatedAt: string;
  lastUsedAt?: string;
  lastDeviceId?: string;
}

const registrationChallenges = new Map<string, string>();
const authenticationChallenges = new Map<string, string>();
const credentialStore = new Map<string, StoredCredential>();

const ANONYMOUS_CHALLENGE_KEY = '__anon__';

function getRpId(): string {
  return process.env.NEXT_PUBLIC_RPID || 'localhost';
}

function getExpectedOrigin(): string {
  return process.env.NEXT_PUBLIC_WEBAUTHN_ORIGIN || process.env.NEXT_PUBLIC_ORIGIN || 'https://lukhas.ai';
}

function toBase64Url(buffer: Buffer): string {
  return buffer.toString('base64url');
}

function base64UrlToBuffer(value: string): Buffer {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/');
  const pad = (4 - (normalized.length % 4)) % 4;
  const padded = normalized + '='.repeat(pad);
  return Buffer.from(padded, 'base64');
}

function normalizeBase64Url(value: string): string {
  try {
    return toBase64Url(base64UrlToBuffer(value));
  } catch {
    return value;
  }
}

function toBuffer(data: unknown): Buffer {
  if (data == null) {
    return Buffer.alloc(0);
  }

  if (Buffer.isBuffer(data)) {
    return data;
  }

  if (data instanceof ArrayBuffer) {
    return Buffer.from(data);
  }

  if (ArrayBuffer.isView(data)) {
    return Buffer.from(data.buffer, data.byteOffset, data.byteLength);
  }

  if (typeof data === 'string') {
    // Prefer base64 decoding, fall back to UTF-8
    try {
      return Buffer.from(data, 'base64');
    } catch {
      return Buffer.from(data, 'utf8');
    }
  }

  if (Array.isArray(data)) {
    return Buffer.from(data);
  }

  if (typeof data === 'object') {
    const maybeBuffer = data as { type?: string; data?: number[] };
    if (maybeBuffer.type === 'Buffer' && Array.isArray(maybeBuffer.data)) {
      return Buffer.from(maybeBuffer.data);
    }

    if (Array.isArray(maybeBuffer.data)) {
      return Buffer.from(maybeBuffer.data);
    }
  }

  return Buffer.from(String(data), 'utf8');
}

function parseClientDataJSON(data: unknown): Record<string, unknown> | null {
  const buffer = toBuffer(data);
  if (!buffer.length) {
    return null;
  }

  try {
    return JSON.parse(buffer.toString('utf8')) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function normalizeCredentialId(id: unknown): string | null {
  if (id == null) {
    return null;
  }

  try {
    if (typeof id === 'string') {
      return normalizeBase64Url(id);
    }

    const buffer = toBuffer(id);
    if (!buffer.length) {
      return null;
    }

    return toBase64Url(buffer);
  } catch {
    return null;
  }
}

function decodeUserHandle(userHandle: unknown): string | null {
  const buffer = toBuffer(userHandle);
  if (!buffer.length) {
    return null;
  }

  return buffer.toString('utf8');
}

function getAuthenticationChallengeKey(userId?: string): string {
  return userId ?? ANONYMOUS_CHALLENGE_KEY;
}

export async function startRegistration({
  userId,
  username,
  displayName
}: {
  userId: string;
  username: string;
  displayName: string;
}): Promise<RegistrationOptions> {
  const challengeBytes = randomBytes(32);
  const challengeBase64 = toBase64Url(challengeBytes);
  registrationChallenges.set(userId, challengeBase64);

  return {
    challenge: Array.from(challengeBytes),
    rp: {
      name: 'LUKHAS AI',
      id: getRpId()
    },
    user: {
      id: Array.from(Buffer.from(userId)),
      name: username,
      displayName
    },
    pubKeyCredParams: [
      { alg: -7, type: 'public-key' },
      { alg: -257, type: 'public-key' }
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

export async function finishRegistration({
  userId,
  response
}: {
  userId: string;
  response: any;
}): Promise<RegistrationResult> {
  const expectedChallenge = registrationChallenges.get(userId);
  if (!expectedChallenge) {
    return { success: false, error: 'Registration challenge not found' };
  }

  const clientData = parseClientDataJSON(response?.response?.clientDataJSON);
  if (!clientData) {
    return { success: false, error: 'Invalid registration client data' };
  }

  const clientType = typeof clientData.type === 'string' ? clientData.type : undefined;
  if (clientType !== 'webauthn.create') {
    return { success: false, error: 'Unexpected registration client data type' };
  }

  const rawRegistrationChallenge = (clientData as { challenge?: unknown }).challenge;
  const challengeFromClient = typeof rawRegistrationChallenge === 'string'
    ? normalizeBase64Url(rawRegistrationChallenge)
    : toBase64Url(toBuffer(rawRegistrationChallenge));

  if (challengeFromClient !== expectedChallenge) {
    return { success: false, error: 'Registration challenge mismatch' };
  }

  registrationChallenges.delete(userId);

  const credentialId = normalizeCredentialId(response?.id ?? response?.rawId);
  if (!credentialId) {
    return { success: false, error: 'Missing credential identifier' };
  }

  const now = new Date().toISOString();
  const transports = Array.isArray(response?.transports) ? response.transports : [];

  credentialStore.set(credentialId, {
    userId,
    credentialId,
    signCount: 0,
    transports,
    createdAt: now,
    updatedAt: now
  });

  return { success: true, credentialId };
}

export async function startAuthentication({ userId }: { userId?: string }): Promise<AuthenticationOptions> {
  const challengeBytes = randomBytes(32);
  const challengeBase64 = toBase64Url(challengeBytes);

  const challengeKey = getAuthenticationChallengeKey(userId);
  authenticationChallenges.set(challengeKey, challengeBase64);

  const allowCredentials: PublicKeyCredentialDescriptor[] = [];

  if (userId) {
    for (const credential of credentialStore.values()) {
      if (credential.userId !== userId) continue;

      allowCredentials.push({
        type: 'public-key',
        id: Array.from(base64UrlToBuffer(credential.credentialId)),
        transports: credential.transports.length ? credential.transports : undefined
      });
    }
  }

  return {
    challenge: Array.from(challengeBytes),
    rpId: getRpId(),
    allowCredentials,
    userVerification: 'required',
    timeout: 60000
  };
}

export async function finishAuthentication({
  userId,
  response,
  deviceId
}: {
  userId: string;
  response: any;
  deviceId?: string;
}): Promise<AuthenticationResult> {
  const challengeKey = getAuthenticationChallengeKey(userId);
  const expectedChallenge = authenticationChallenges.get(challengeKey);
  if (!expectedChallenge) {
    return { ok: false, error: 'Authentication challenge not found' };
  }

  const credentialId = normalizeCredentialId(response?.id ?? response?.rawId);
  if (!credentialId) {
    return { ok: false, error: 'Missing credential identifier' };
  }

  const storedCredential = credentialStore.get(credentialId);
  if (!storedCredential || storedCredential.userId !== userId) {
    return { ok: false, error: 'Credential not recognized for user' };
  }

  const clientData = parseClientDataJSON(response?.response?.clientDataJSON);
  if (!clientData) {
    return { ok: false, error: 'Invalid authentication client data' };
  }

  const clientType = typeof clientData.type === 'string' ? clientData.type : undefined;
  if (clientType !== 'webauthn.get') {
    return { ok: false, error: 'Unexpected authentication client data type' };
  }

  const rawChallenge = (clientData as { challenge?: unknown }).challenge;
  const challengeFromClient = typeof rawChallenge === 'string'
    ? normalizeBase64Url(rawChallenge)
    : toBase64Url(toBuffer(rawChallenge));

  if (challengeFromClient !== expectedChallenge) {
    return { ok: false, error: 'Authentication challenge mismatch' };
  }

  const expectedOrigin = getExpectedOrigin();
  const origin = typeof clientData.origin === 'string' ? clientData.origin : undefined;
  if (origin && origin !== expectedOrigin) {
    return { ok: false, error: 'Authentication origin mismatch' };
  }

  // Once the challenge is verified it cannot be reused
  authenticationChallenges.delete(challengeKey);

  const authenticatorData = toBuffer(response?.response?.authenticatorData);
  if (authenticatorData.length < 37) {
    return { ok: false, error: 'Authenticator data is incomplete' };
  }

  const rpIdHash = createHash('sha256').update(getRpId()).digest();
  const providedRpHash = authenticatorData.subarray(0, 32);
  if (!providedRpHash.equals(rpIdHash)) {
    return { ok: false, error: 'RP ID hash mismatch' };
  }

  const flags = authenticatorData[32];
  const userPresent = (flags & 0x01) === 0x01;
  const userVerified = (flags & 0x04) === 0x04;

  if (!userPresent) {
    return { ok: false, error: 'User presence not verified' };
  }

  if (!userVerified) {
    return { ok: false, error: 'User verification not satisfied' };
  }

  const signCount = authenticatorData.readUInt32BE(33);
  if (storedCredential.signCount > 0 && signCount <= storedCredential.signCount) {
    return { ok: false, error: 'Sign count replay detected' };
  }

  const userHandle = decodeUserHandle(response?.response?.userHandle);
  if (userHandle && userHandle !== userId) {
    return { ok: false, error: 'User handle mismatch' };
  }

  const updatedAt = new Date().toISOString();
  credentialStore.set(credentialId, {
    ...storedCredential,
    signCount,
    updatedAt,
    lastUsedAt: updatedAt,
    lastDeviceId: deviceId ?? storedCredential.lastDeviceId
  });

  return { ok: true, userId, credentialId, signCount };
}

export function __resetPasskeyStorage() {
  registrationChallenges.clear();
  authenticationChallenges.clear();
  credentialStore.clear();
}
