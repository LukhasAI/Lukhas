import { createHash, createSign, generateKeyPairSync } from 'crypto';

import {
  __resetPasskeyStorage,
  finishAuthentication,
  finishRegistration,
  startAuthentication,
  startRegistration
} from '@/packages/auth/passkeys';

const DEFAULT_ORIGIN = process.env.NEXT_PUBLIC_WEBAUTHN_ORIGIN || process.env.NEXT_PUBLIC_ORIGIN || 'https://lukhas.ai';
const DEFAULT_RP_ID = process.env.NEXT_PUBLIC_RPID || 'localhost';

function bufferToArray(buffer: Buffer): number[] {
  return Array.from(buffer);
}

describe('passkeys authentication flow', () => {
  const userId = 'user-123';

  beforeEach(() => {
    __resetPasskeyStorage();
  });

  it('validates authentication assertions before returning success', async () => {
    const { privateKey, publicKey } = generateKeyPairSync('ec', { namedCurve: 'P-256' });
    const publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' }).toString();

    const registrationOptions = await startRegistration({
      userId,
      username: 'user@example.com',
      displayName: 'Example User'
    });

    const registrationChallenge = Buffer.from(registrationOptions.challenge).toString('base64url');

    const registrationResponse = {
      id: Buffer.from('credential-1').toString('base64url'),
      rawId: bufferToArray(Buffer.from('credential-1')),
      response: {
        clientDataJSON: bufferToArray(
          Buffer.from(
            JSON.stringify({
              type: 'webauthn.create',
              challenge: registrationChallenge,
              origin: DEFAULT_ORIGIN
            })
          )
        ),
        attestationObject: bufferToArray(Buffer.from('attestation')),
        publicKey: publicKeyPem,
        algorithm: 'ES256'
      },
      transports: ['internal']
    };

    const registrationResult = await finishRegistration({ userId, response: registrationResponse });
    expect(registrationResult.success).toBe(true);
    expect(registrationResult.credentialId).toBeDefined();

    const authenticationOptions = await startAuthentication({ userId });
    const authenticationChallenge = Buffer.from(authenticationOptions.challenge).toString('base64url');

    const rpIdHash = createHash('sha256').update(DEFAULT_RP_ID).digest();
    const flags = Buffer.from([0x05]);
    const signCount = Buffer.alloc(4);
    signCount.writeUInt32BE(1);
    const authenticatorData = Buffer.concat([rpIdHash, flags, signCount]);
    const clientDataJSON = Buffer.from(
      JSON.stringify({
        type: 'webauthn.get',
        challenge: authenticationChallenge,
        origin: DEFAULT_ORIGIN
      })
    );
    const signatureBase = Buffer.concat([
      authenticatorData,
      createHash('sha256').update(clientDataJSON).digest()
    ]);
    const signature = createSign('SHA256').update(signatureBase).sign(privateKey);

    const authenticationResponse = {
      id: registrationResult.credentialId,
      rawId: bufferToArray(Buffer.from(registrationResult.credentialId!, 'base64url')),
      response: {
        clientDataJSON: bufferToArray(clientDataJSON),
        authenticatorData: bufferToArray(authenticatorData),
        signature: bufferToArray(signature),
        userHandle: bufferToArray(Buffer.from(userId))
      }
    };

    const result = await finishAuthentication({ userId, response: authenticationResponse });
    expect(result).toMatchObject({
      ok: true,
      userId,
      credentialId: registrationResult.credentialId,
      signCount: 1
    });
  });

  it('rejects authentication with invalid signature', async () => {
    const { privateKey, publicKey } = generateKeyPairSync('ec', { namedCurve: 'P-256' });
    const publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' }).toString();

    const registrationOptions = await startRegistration({
      userId,
      username: 'user@example.com',
      displayName: 'Example User'
    });

    const registrationChallenge = Buffer.from(registrationOptions.challenge).toString('base64url');

    const registrationResponse = {
      id: Buffer.from('credential-2').toString('base64url'),
      rawId: bufferToArray(Buffer.from('credential-2')),
      response: {
        clientDataJSON: bufferToArray(
          Buffer.from(
            JSON.stringify({
              type: 'webauthn.create',
              challenge: registrationChallenge,
              origin: DEFAULT_ORIGIN
            })
          )
        ),
        attestationObject: bufferToArray(Buffer.from('attestation')),
        publicKey: publicKeyPem,
        algorithm: 'ES256'
      },
      transports: ['internal']
    };

    const registrationResult = await finishRegistration({ userId, response: registrationResponse });
    expect(registrationResult.success).toBe(true);

    const authenticationOptions = await startAuthentication({ userId });
    const authenticationChallenge = Buffer.from(authenticationOptions.challenge).toString('base64url');

    const rpIdHash = createHash('sha256').update(DEFAULT_RP_ID).digest();
    const flags = Buffer.from([0x05]);
    const signCount = Buffer.alloc(4);
    signCount.writeUInt32BE(2);
    const authenticatorData = Buffer.concat([rpIdHash, flags, signCount]);

    const clientDataJSON = Buffer.from(
      JSON.stringify({
        type: 'webauthn.get',
        challenge: authenticationChallenge,
        origin: DEFAULT_ORIGIN
      })
    );

    const signatureBase = Buffer.concat([
      authenticatorData,
      createHash('sha256').update(clientDataJSON).digest()
    ]);

    // Tamper with signature payload to force verification failure
    const forgedSignaturePayload = Buffer.concat([signatureBase, Buffer.from('tamper')]);
    const invalidSignature = createSign('SHA256').update(forgedSignaturePayload).sign(privateKey);

    const authenticationResponse = {
      id: registrationResult.credentialId,
      rawId: bufferToArray(Buffer.from(registrationResult.credentialId!, 'base64url')),
      response: {
        clientDataJSON: bufferToArray(clientDataJSON),
        authenticatorData: bufferToArray(authenticatorData),
        signature: bufferToArray(invalidSignature),
        userHandle: bufferToArray(Buffer.from(userId))
      }
    };

    const result = await finishAuthentication({ userId, response: authenticationResponse });
    expect(result.ok).toBe(false);
    expect(result.error).toMatch(/signature/i);
  });

  it('rejects authentication for unknown credentials', async () => {
    const authenticationOptions = await startAuthentication({ userId });
    const authenticationChallenge = Buffer.from(authenticationOptions.challenge).toString('base64url');

    const rpIdHash = createHash('sha256').update(DEFAULT_RP_ID).digest();
    const flags = Buffer.from([0x05]);
    const signCount = Buffer.alloc(4);
    signCount.writeUInt32BE(1);
    const authenticatorData = Buffer.concat([rpIdHash, flags, signCount]);

    const fakeCredentialId = Buffer.from('missing-credential').toString('base64url');

    const authenticationResponse = {
      id: fakeCredentialId,
      rawId: bufferToArray(Buffer.from(fakeCredentialId, 'base64url')),
      response: {
        clientDataJSON: bufferToArray(
          Buffer.from(
            JSON.stringify({
              type: 'webauthn.get',
              challenge: authenticationChallenge,
              origin: DEFAULT_ORIGIN
            })
          )
        ),
        authenticatorData: bufferToArray(authenticatorData),
        signature: bufferToArray(Buffer.from('signature')),
        userHandle: bufferToArray(Buffer.from(userId))
      }
    };

    const result = await finishAuthentication({ userId, response: authenticationResponse });
    expect(result.ok).toBe(false);
    expect(result.error).toMatch(/credential/i);
  });
});
