import { hash, verify } from 'argon2';
import { createHash } from 'crypto';

/**
 * Hash a password or secret using Argon2id
 */
export async function hashSecret(secret: string): Promise<string> {
  return hash(secret, {
    type: 2, // argon2id
    memoryCost: 19456, // ~19 MB
    timeCost: 2,
    parallelism: 1
  });
}

/**
 * Verify a password or secret against an Argon2id hash
 */
export async function verifySecret(secret: string, hashedSecret: string): Promise<boolean> {
  try {
    return await verify(hashedSecret, secret);
  } catch {
    return false;
  }
}

/**
 * Create a SHA256 hash of arbitrary data
 */
export function sha256(data: string | Buffer): string {
  return createHash('sha256').update(data).digest('hex');
}

/**
 * Create a deterministic hash for challenge answers
 */
export function hashAnswer(answer: any): string {
  return sha256(JSON.stringify(answer));
}
