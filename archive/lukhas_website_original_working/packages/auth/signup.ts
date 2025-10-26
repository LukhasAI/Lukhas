// Signup flow implementation
import { randomInt } from 'crypto';
import { createHash } from 'crypto';

const verificationCodes = new Map<string, { code: string; expires: number }>();

export async function sendSignupEmail({ email }: { email: string }) {
  const code = randomInt(100000, 999999).toString();
  const expires = Date.now() + 10 * 60 * 1000; // 10 minutes
  
  const hashedEmail = createHash('sha256').update(email.toLowerCase()).digest('hex');
  verificationCodes.set(hashedEmail, { code, expires });
  
  // TODO: Send email with code
  console.log(`Verification code for ${email}: ${code}`);
  
  return { ok: true };
}

export async function verifySignupEmail({ email, code }: { email: string; code: string }) {
  const hashedEmail = createHash('sha256').update(email.toLowerCase()).digest('hex');
  const entry = verificationCodes.get(hashedEmail);
  
  if (!entry) return { success: false, error: 'Invalid code' };
  
  if (Date.now() > entry.expires) {
    verificationCodes.delete(hashedEmail);
    return { success: false, error: 'Code expired' };
  }
  
  if (entry.code !== code) {
    return { success: false, error: 'Invalid code' };
  }
  
  verificationCodes.delete(hashedEmail);
  
  // TODO: Create user account
  const userId = 'user_' + Date.now();
  
  return { success: true, userId };
}
