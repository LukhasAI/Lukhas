// Magic link implementation
import { randomBytes } from 'crypto';
import { createHash } from 'crypto';

const tokens = new Map<string, { email: string; expires: number }>();

export async function createMagicLink({ email, ip }: { email: string; ip?: string }) {
  const token = randomBytes(32).toString('base64url');
  const expires = Date.now() + 10 * 60 * 1000; // 10 minutes
  
  // Enumeration-safe: always succeeds
  const hashedEmail = createHash('sha256').update(email.toLowerCase()).digest('hex');
  tokens.set(token, { email: hashedEmail, expires });
  
  // TODO: Send email with link
  console.log(`Magic link for ${email}: /api/auth/magic-link?token=${token}`);
  
  return { ok: true };
}

export async function verifyMagicLink({ token }: { token: string }) {
  const entry = tokens.get(token);
  if (!entry) return { ok: false };
  
  if (Date.now() > entry.expires) {
    tokens.delete(token);
    return { ok: false };
  }
  
  tokens.delete(token);
  // TODO: Create session
  return { ok: true, email: entry.email };
}
