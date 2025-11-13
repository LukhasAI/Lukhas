// Magic link implementation
import { randomBytes } from 'crypto';
import { createHash } from 'crypto';
import { createEmailServiceFromEnv } from './email-service';

const tokens = new Map<string, { email: string; expires: number }>();

// Initialize email service
let emailService: ReturnType<typeof createEmailServiceFromEnv> | null = null;

function getEmailService() {
  if (!emailService) {
    emailService = createEmailServiceFromEnv();
  }
  return emailService;
}

export async function createMagicLink({ email, ip }: { email: string; ip?: string }) {
  const token = randomBytes(32).toString('base64url');
  const expires = Date.now() + 10 * 60 * 1000; // 10 minutes

  // Enumeration-safe: always succeeds
  const hashedEmail = createHash('sha256').update(email.toLowerCase()).digest('hex');
  tokens.set(token, { email: hashedEmail, expires });

  // Construct magic link URL
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || process.env.VERCEL_URL || 'http://localhost:3000';
  const magicLink = `${baseUrl}/api/auth/magic-link?token=${token}`;

  // Send email with link
  try {
    const service = getEmailService();
    const result = await service.sendMagicLink({
      email,
      magicLink,
      expiresInMinutes: 10,
      language: 'en' // TODO: Get from user preferences or Accept-Language header
    });

    if (!result.success) {
      console.error(`[MagicLink] Failed to send email to ${email}:`, result.error);
    } else {
      console.log(`[MagicLink] Sent magic link to ${email} (Message ID: ${result.messageId})`);
    }
  } catch (error) {
    console.error(`[MagicLink] Error sending email:`, error);
  }

  // Always return success for enumeration safety
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

  // Session creation handled by caller (typically in API route)
  // Returns email hash for user lookup and session creation
  return { ok: true, emailHash: entry.email };
}
