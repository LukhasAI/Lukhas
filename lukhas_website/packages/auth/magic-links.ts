// Magic link implementation
import { randomBytes } from 'crypto';
import { createHash } from 'crypto';

const tokens = new Map<string, { email: string; expires: number }>();

// Initialize email service
let emailService: ReturnType<typeof createEmailServiceFromEnv> | null = null;

function getEmailService() {
  if (!emailService) {
    emailService = createEmailServiceFromEnv();
  }
  return emailService;
}

function stripTrailingSlash(url: string) {
  return url.replace(/\/+$/, '');
}

function resolveMagicLinkBaseUrl() {
  const explicitUrl = process.env.NEXT_PUBLIC_APP_URL;
  if (explicitUrl && explicitUrl.trim().length > 0) {
    return stripTrailingSlash(explicitUrl);
  }

  const vercelUrl = process.env.VERCEL_URL;
  if (vercelUrl && vercelUrl.trim().length > 0) {
    const normalized = vercelUrl.startsWith('http://') || vercelUrl.startsWith('https://')
      ? vercelUrl
      : `https://${vercelUrl}`;
    return stripTrailingSlash(normalized);
  }

  return 'http://localhost:3000';
}

export async function createMagicLink({ email, ip }: { email: string; ip?: string }) {
  const token = randomBytes(32).toString('base64url');
  const expires = Date.now() + 10 * 60 * 1000; // 10 minutes

  // Enumeration-safe: always succeeds
  const hashedEmail = createHash('sha256').update(email.toLowerCase()).digest('hex');
  tokens.set(token, { email: hashedEmail, expires });

  // Construct magic link URL
  const baseUrl = resolveMagicLinkBaseUrl();
  const magicLink = `${baseUrl}/api/auth/magic-link?token=${token}`;

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
