// Signup flow implementation
import { randomInt } from 'crypto';
import { createHash } from 'crypto';
import { createEmailServiceFromEnv } from './email-service';
import { createSMSServiceFromEnv } from './sms-service';

const verificationCodes = new Map<string, { code: string; expires: number; method: 'email' | 'sms' }>();

// Initialize services
let emailService: ReturnType<typeof createEmailServiceFromEnv> | null = null;
let smsService: ReturnType<typeof createSMSServiceFromEnv> | null = null;

function getEmailService() {
  if (!emailService) {
    emailService = createEmailServiceFromEnv();
  }
  return emailService;
}

function getSMSService() {
  if (!smsService) {
    smsService = createSMSServiceFromEnv();
  }
  return smsService;
}

export async function sendSignupEmail({ email }: { email: string }) {
  const code = randomInt(100000, 999999).toString();
  const expires = Date.now() + 10 * 60 * 1000; // 10 minutes

  const hashedEmail = createHash('sha256').update(email.toLowerCase()).digest('hex');
  verificationCodes.set(hashedEmail, { code, expires, method: 'email' });

  // Send email with verification code
  try {
    const service = getEmailService();
    const result = await service.sendVerificationCode({
      email,
      code,
      expiresInMinutes: 10,
      purpose: 'register',
      language: 'en' // TODO: Get from user preferences or Accept-Language header
    });

    if (!result.success) {
      console.error(`[Signup] Failed to send verification email to ${email}:`, result.error);
    } else {
      console.log(`[Signup] Sent verification code to ${email} (Message ID: ${result.messageId})`);
    }
  } catch (error) {
    console.error(`[Signup] Error sending email:`, error);
  }

  // Always return success for enumeration safety
  return { ok: true };
}

export async function sendSignupSMS({ phoneNumber }: { phoneNumber: string }) {
  const code = randomInt(100000, 999999).toString();
  const expires = Date.now() + 10 * 60 * 1000; // 10 minutes

  const hashedPhone = createHash('sha256').update(phoneNumber).digest('hex');
  verificationCodes.set(hashedPhone, { code, expires, method: 'sms' });

  // Send SMS with verification code
  try {
    const service = getSMSService();
    const result = await service.sendVerificationCode({
      phoneNumber,
      code,
      expiresInMinutes: 10,
      language: 'en' // TODO: Get from user preferences
    });

    if (!result.success) {
      console.error(`[Signup] Failed to send verification SMS to ${phoneNumber}:`, result.error);
    } else {
      console.log(`[Signup] Sent verification code to ${phoneNumber} (Message ID: ${result.messageId})`);
    }
  } catch (error) {
    console.error(`[Signup] Error sending SMS:`, error);
  }

  // Always return success for enumeration safety
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

  // User account creation handled by caller (typically in API route)
  // This allows for proper database integration and transaction handling
  // Returns success to indicate code verification passed
  return { success: true, email: hashedEmail };
}

export async function verifySignupSMS({ phoneNumber, code }: { phoneNumber: string; code: string }) {
  const hashedPhone = createHash('sha256').update(phoneNumber).digest('hex');
  const entry = verificationCodes.get(hashedPhone);

  if (!entry) return { success: false, error: 'Invalid code' };

  if (Date.now() > entry.expires) {
    verificationCodes.delete(hashedPhone);
    return { success: false, error: 'Code expired' };
  }

  if (entry.code !== code) {
    return { success: false, error: 'Invalid code' };
  }

  verificationCodes.delete(hashedPhone);

  // User account creation handled by caller
  return { success: true, phoneNumber: hashedPhone };
}
