const verifyRegistrationResponse = jest.fn();
const prismaCreate = jest.fn();

jest.mock('@simplewebauthn/server', () => ({
  verifyRegistrationResponse,
}));

jest.mock('@/lib/prisma', () => ({
  prisma: {
    passkeyCredential: {
      create: prismaCreate,
    },
  },
}));

describe('passkey registration', () => {
  let startRegistration: typeof import('@/packages/auth/passkeys').startRegistration;
  let finishRegistration: typeof import('@/packages/auth/passkeys').finishRegistration;

  beforeEach(async () => {
    jest.resetModules();
    verifyRegistrationResponse.mockReset();
    prismaCreate.mockReset();

    process.env.NEXT_PUBLIC_APP_URL = 'https://lukhas.ai';
    process.env.NEXT_PUBLIC_RPID = 'lukhas.ai';

    ({ startRegistration, finishRegistration } = await import('@/packages/auth/passkeys'));
  });

  it('returns failure when no pending challenge exists', async () => {
    const result = await finishRegistration({ userId: 'user-123', response: {} });

    expect(result.success).toBe(false);
    expect(result.error).toMatch(/challenge/i);
    expect(verifyRegistrationResponse).not.toHaveBeenCalled();
  });

  it('stores credential when attestation verifies', async () => {
    const registrationOptions = await startRegistration({
      userId: 'user-123',
      username: 'user@example.com',
      displayName: 'User Example',
    });

    expect(Array.isArray(registrationOptions.challenge)).toBe(true);

    const credentialResponse = {
      id: 'cred-id',
      rawId: [1, 2, 3],
      response: {
        attestationObject: [4, 5, 6],
        clientDataJSON: [7, 8, 9],
      },
    };

    const createdAt = new Date('2024-01-01T00:00:00.000Z');
    const lastUsedAt = new Date('2024-01-01T00:01:00.000Z');

    verifyRegistrationResponse.mockResolvedValue({
      verified: true,
      registrationInfo: {
        credentialID: new Uint8Array([10, 11, 12]),
        credentialPublicKey: new Uint8Array([13, 14, 15]),
        counter: 42,
        aaguid: 'aaguid-test',
      },
    });

    prismaCreate.mockResolvedValue({
      id: 'pk-1',
      userId: 'user-123',
      credentialId: Buffer.from([10, 11, 12]),
      publicKey: Buffer.from([13, 14, 15]),
      aaguid: 'aaguid-test',
      transports: null,
      signCount: 42,
      deviceBinding: null,
      createdAt,
      lastUsedAt,
    });

    const result = await finishRegistration({ userId: 'user-123', response: credentialResponse });

    expect(verifyRegistrationResponse).toHaveBeenCalledTimes(1);
    const verifyArgs = verifyRegistrationResponse.mock.calls[0][0];
    expect(verifyArgs.expectedChallenge).toMatch(/^[A-Za-z0-9_-]+$/);
    expect(verifyArgs.expectedOrigin).toBe('https://lukhas.ai');
    expect(verifyArgs.expectedRPID).toBe('lukhas.ai');

    expect(prismaCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({
          userId: 'user-123',
          signCount: 42,
        }),
      }),
    );

    expect(result.success).toBe(true);
    expect(result.passkey).toEqual({
      id: 'pk-1',
      aaguid: 'aaguid-test',
      signCount: 42,
      createdAt: createdAt.toISOString(),
      lastUsedAt: lastUsedAt.toISOString(),
    });

    const secondAttempt = await finishRegistration({ userId: 'user-123', response: credentialResponse });
    expect(secondAttempt.success).toBe(false);
  });

  it('returns failure when attestation is not verified', async () => {
    await startRegistration({
      userId: 'user-456',
      username: 'user@example.com',
      displayName: 'User Example',
    });

    verifyRegistrationResponse.mockResolvedValue({
      verified: false,
      error: 'not verified',
    });

    const credentialResponse = {
      id: 'cred-id',
      rawId: [1, 2, 3],
      response: {
        attestationObject: [4, 5, 6],
        clientDataJSON: [7, 8, 9],
      },
    };

    const result = await finishRegistration({ userId: 'user-456', response: credentialResponse });

    expect(result.success).toBe(false);
    expect(result.error).toMatch(/verified/i);
    expect(prismaCreate).not.toHaveBeenCalled();
  });
});
