// WebAuthn passkey implementation
import { randomBytes } from 'crypto';
import { verifyRegistrationResponse } from '@simplewebauthn/server';
import type { RegistrationResponseJSON } from '@simplewebauthn/types';
import { Prisma } from '@prisma/client';
import { prisma } from '@/lib/prisma';

type PendingRegistration = {
  challenge: string;
  expiresAt: number;
};

const REGISTRATION_TTL_MS = 5 * 60 * 1000; // 5 minutes
const pendingRegistrations = new Map<string, PendingRegistration>();

const DEFAULT_RPID = process.env.NEXT_PUBLIC_RPID || 'localhost';
const DEFAULT_ORIGIN = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

function cleanupExpiredChallenges(now = Date.now()) {
  for (const [key, pending] of pendingRegistrations) {
    if (pending.expiresAt <= now) {
      pendingRegistrations.delete(key);
    }
  }
}

function toBase64Url(value: unknown): string {
  if (typeof value === 'string') {
    return value;
  }
  if (value instanceof ArrayBuffer) {
    return Buffer.from(value).toString('base64url');
  }
  if (ArrayBuffer.isView(value)) {
    const view = value as ArrayBufferView;
    return Buffer.from(view.buffer, view.byteOffset, view.byteLength).toString('base64url');
  }
  if (Array.isArray(value)) {
    return Buffer.from(value).toString('base64url');
  }
  throw new Error('Unsupported binary format');
}

function normalizeRegistrationResponse(raw: any): RegistrationResponseJSON {
  if (!raw?.id || !raw?.response) {
    throw new Error('Invalid credential response');
  }

  return {
    id: raw.id,
    rawId: toBase64Url(raw.rawId ?? raw.id),
    type: raw.type || 'public-key',
    authenticatorAttachment: raw.authenticatorAttachment,
    clientExtensionResults: raw.clientExtensionResults ?? {},
    response: {
      attestationObject: toBase64Url(raw.response.attestationObject),
      clientDataJSON: toBase64Url(raw.response.clientDataJSON),
      transports: raw.response.transports,
    },
  };
}

export function generateChallenge(length = 32): string {
  return randomBytes(length).toString('base64url');
}

export async function startRegistration({ userId, username, displayName }: {
  userId: string;
  username: string;
  displayName: string;
}) {
  cleanupExpiredChallenges();

  const challengeBuffer = randomBytes(32);
  const challenge = challengeBuffer.toString('base64url');
  pendingRegistrations.set(userId, {
    challenge,
    expiresAt: Date.now() + REGISTRATION_TTL_MS,
  });

  return {
    challenge: Array.from(challengeBuffer),
    rp: {
      name: 'LUKHAS AI',
      id: DEFAULT_RPID,
    },
    user: {
      id: Array.from(Buffer.from(userId)),
      name: username,
      displayName,
    },
    pubKeyCredParams: [
      { alg: -7, type: 'public-key' }, // ES256
      { alg: -257, type: 'public-key' }, // RS256
    ],
    timeout: 60000,
    attestation: 'direct',
    authenticatorSelection: {
      authenticatorAttachment: 'platform',
      userVerification: 'required',
      residentKey: 'preferred',
    },
  };
}

export async function finishRegistration({ userId, response }: {
  userId: string;
  response: any;
}) {
  const pending = pendingRegistrations.get(userId);
  if (!pending) {
    return { success: false, error: 'No pending registration challenge' };
  }

  if (pending.expiresAt <= Date.now()) {
    pendingRegistrations.delete(userId);
    return { success: false, error: 'Registration challenge expired' };
  }

  const credential = response?.credential ?? response;

  let normalized: RegistrationResponseJSON;
  try {
    normalized = normalizeRegistrationResponse(credential);
  } catch (error) {
    pendingRegistrations.delete(userId);
    return { success: false, error: error instanceof Error ? error.message : 'Invalid credential response' };
  }

  try {
    const verification = await verifyRegistrationResponse({
      response: normalized,
      expectedChallenge: pending.challenge,
      expectedOrigin: DEFAULT_ORIGIN,
      expectedRPID: DEFAULT_RPID,
      requireUserVerification: true,
    });

    if (!verification.verified || !verification.registrationInfo) {
      return {
        success: false,
        error: verification.error || 'Passkey attestation could not be verified',
      };
    }

    const { credentialID, credentialPublicKey, counter, aaguid } = verification.registrationInfo;
    const transports = normalized.response.transports;

    const stored = await prisma.passkeyCredential.create({
      data: {
        userId,
        credentialId: Buffer.from(credentialID),
        publicKey: Buffer.from(credentialPublicKey),
        aaguid: aaguid ?? null,
        transports: Array.isArray(transports) && transports.length > 0 ? transports.join(',') : null,
        signCount: typeof counter === 'number' ? counter : 0,
        lastUsedAt: new Date(),
      },
    });

    return {
      success: true,
      credentialId: normalized.id,
      passkey: {
        id: stored.id,
        aaguid: stored.aaguid,
        signCount: stored.signCount,
        createdAt: stored.createdAt.toISOString(),
        lastUsedAt: stored.lastUsedAt ? stored.lastUsedAt.toISOString() : null,
      },
    };
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2002') {
      return { success: false, error: 'Passkey already registered' };
    }

    console.error('finishRegistration error:', error);
    return { success: false, error: 'Failed to complete passkey registration' };
  } finally {
    pendingRegistrations.delete(userId);
  }
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
