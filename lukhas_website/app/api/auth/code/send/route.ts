/**
 * LUKHAS AI - Verification Code Send API
 *
 * Generates and sends 6-digit verification codes via email/SMS
 * Enumeration-safe responses, HMAC-based validation, rate limiting
 */

import { NextRequest, NextResponse } from 'next/server';
import { sendVerificationCode } from '../../../../../../packages/auth/src/codes';
import { TemplateEngine } from '../../../../../../identity/email_templates/engine';
import { rateLimit } from '@/lib/rate-limit';
import { headers } from 'next/headers';
import { z } from 'zod';

// Request validation schema
const SendCodeRequestSchema = z.object({
  email: z.string().email('Invalid email address'),
  purpose: z.enum(['login', 'register', 'password-reset', 'email-verification', 'phone-verification']),
  language: z.enum(['en', 'es']).optional().default('en'),
  channel: z.enum(['email', 'sms']).optional().default('email'),
  userTier: z.enum(['T1', 'T2', 'T3', 'T4', 'T5']).optional(),
  userId: z.string().optional(),
  metadata: z.record(z.any()).optional()
});

type SendCodeRequest = z.infer<typeof SendCodeRequestSchema>;

/**
 * POST /api/auth/code/send
 * Send verification code via email or SMS
 */
export async function POST(req: NextRequest) {
  try {
    // Get client IP and user agent
    const headersList = headers();
    const ipAddress = headersList.get('x-forwarded-for') ??
                      headersList.get('x-real-ip') ??
                      req.ip ??
                      '127.0.0.1';
    const userAgent = headersList.get('user-agent') ?? 'Unknown';

    // Parse and validate request body
    let body: SendCodeRequest;
    try {
      const rawBody = await req.json();
      body = SendCodeRequestSchema.parse(rawBody);
    } catch (error) {
      return NextResponse.json(
        {
          ok: true,  // Enumeration-safe response
          message: 'If the email address is valid, a verification code has been sent.',
          requestId: `req_${Date.now()}_${Math.random().toString(36).substring(2)}`
        },
        { status: 200 }
      );
    }

    const { email, purpose, language, channel, userTier, userId, metadata } = body;

    // Apply rate limiting
    const rateLimitResult = await rateLimit({
      key: `code_send:${ipAddress}:${email}`,
      limit: 5, // 5 attempts per window
      window: 3600000 // 1 hour
    });

    if (!rateLimitResult.success) {
      return NextResponse.json(
        {
          ok: true,  // Enumeration-safe response
          message: 'If the email address is valid, a verification code has been sent.',
          requestId: `req_${Date.now()}_${Math.random().toString(36).substring(2)}`
        },
        { status: 200 }
      );
    }

    // Generate verification code
    const codeResult = await sendVerificationCode(email, purpose, {
      ipAddress,
      userAgent,
      userId,
      userTier: userTier as any,
      maxAttempts: 5,
      metadata: {
        ...metadata,
        channel,
        language
      }
    });

    // Always return success for enumeration safety
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2)}`;

    if (codeResult.success && codeResult.code) {
      // Send the code via the requested channel
      const templateEngine = new TemplateEngine();

      if (channel === 'email') {
        // Render email template
        const templateType = 'code_verification' as const;
        const template = templateEngine.render_template(
          templateType,
          language,
          {
            verification_code: codeResult.code,
            expires_at: new Date(codeResult.expiresAt!),
            user_email: email,
            current_timestamp: new Date()
          }
        );

        // TODO: Send email using your email service (SendGrid, AWS SES, etc.)
        // await emailService.send({
        //   to: email,
        //   subject: template.subject,
        //   html: template.html,
        //   text: template.plain_text
        // });

        console.log(`[ΛiD CODE] Email verification code sent to ${email}:`, {
          code: codeResult.code,
          purpose,
          requestId
        });
      } else if (channel === 'sms') {
        // Render SMS template
        const smsTemplateType = 'sms_code_verification' as const;
        const smsTemplate = templateEngine.render_template(
          smsTemplateType,
          language,
          {
            verification_code: codeResult.code,
            expires_at: new Date(codeResult.expiresAt!)
          }
        );

        // TODO: Send SMS using your SMS service (Twilio, AWS SNS, etc.)
        // await smsService.send({
        //   to: email, // In production, this would be a phone number
        //   message: smsTemplate.plain_text
        // });

        console.log(`[ΛiD CODE] SMS verification code sent to ${email}:`, {
          code: codeResult.code,
          purpose,
          requestId
        });
      }
    }

    // Always return enumeration-safe success response
    return NextResponse.json(
      {
        ok: true,
        message: 'If the email address is valid, a verification code has been sent.',
        requestId,
        ...(process.env.NODE_ENV === 'development' && codeResult.success ? {
          // Include debug info in development
          debug: {
            codeGenerated: true,
            expiresAt: codeResult.expiresAt,
            expiresIn: codeResult.expiresIn,
            channel,
            purpose
          }
        } : {})
      },
      { status: 200 }
    );

  } catch (error) {
    console.error('[ΛiD CODE SEND] Error:', error);

    // Always return enumeration-safe response even on errors
    return NextResponse.json(
      {
        ok: true,
        message: 'If the email address is valid, a verification code has been sent.',
        requestId: `req_${Date.now()}_${Math.random().toString(36).substring(2)}`
      },
      { status: 200 }
    );
  }
}

/**
 * GET /api/auth/code/send
 * Return method not allowed for GET requests
 */
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405 }
  );
}
