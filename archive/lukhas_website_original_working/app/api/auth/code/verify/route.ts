/**
 * LUKHAS AI - Verification Code Verify API
 * 
 * Verifies 6-digit verification codes with HMAC validation
 * Enumeration-safe responses, rate limiting, attempt tracking
 */

import { NextRequest, NextResponse } from 'next/server';
import { verifyVerificationCode } from '../../../../../../packages/auth/src/codes';
import { rateLimit } from '@/lib/rate-limit';
import { headers } from 'next/headers';
import { z } from 'zod';

// Request validation schema
const VerifyCodeRequestSchema = z.object({
  email: z.string().email('Invalid email address'),
  code: z.string().regex(/^\d{6}$/, 'Code must be exactly 6 digits'),
  purpose: z.enum(['login', 'register', 'password-reset', 'email-verification', 'phone-verification']),
  metadata: z.record(z.any()).optional()
});

type VerifyCodeRequest = z.infer<typeof VerifyCodeRequestSchema>;

/**
 * POST /api/auth/code/verify
 * Verify a 6-digit verification code
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
    let body: VerifyCodeRequest;
    try {
      const rawBody = await req.json();
      body = VerifyCodeRequestSchema.parse(rawBody);
    } catch (error) {
      // Return enumeration-safe response for invalid requests
      return NextResponse.json(
        { 
          ok: true,  // Enumeration-safe response
          verified: false,
          message: 'Verification completed.',
          requestId: `req_${Date.now()}_${Math.random().toString(36).substring(2)}`
        },
        { status: 200 }
      );
    }

    const { email, code, purpose, metadata } = body;

    // Apply rate limiting (more restrictive for verification attempts)
    const rateLimitResult = await rateLimit({
      key: `code_verify:${ipAddress}:${email}`,
      limit: 10, // 10 verification attempts per window
      window: 3600000 // 1 hour
    });

    if (!rateLimitResult.success) {
      return NextResponse.json(
        { 
          ok: true,  // Enumeration-safe response
          verified: false,
          message: 'Verification completed.',
          requestId: `req_${Date.now()}_${Math.random().toString(36).substring(2)}`
        },
        { status: 200 }
      );
    }

    // Verify the code
    const verificationResult = await verifyVerificationCode(
      email,
      code,
      purpose,
      ipAddress,
      userAgent
    );

    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2)}`;

    if (verificationResult.valid) {
      // Code is valid - return success with additional info
      return NextResponse.json(
        { 
          ok: true,
          verified: true,
          message: 'Verification completed.',
          requestId,
          user: {
            email: verificationResult.email,
            userId: verificationResult.userId,
            purpose: verificationResult.purpose,
            metadata: verificationResult.metadata
          }
        },
        { status: 200 }
      );
    } else {
      // Code is invalid - return enumeration-safe failure
      return NextResponse.json(
        { 
          ok: true,  // Enumeration-safe response
          verified: false,
          message: 'Verification completed.',
          requestId
        },
        { status: 200 }
      );
    }

  } catch (error) {
    console.error('[ΛiD CODE VERIFY] Error:', error);

    // Always return enumeration-safe response even on errors
    return NextResponse.json(
      { 
        ok: true,
        verified: false,
        message: 'Verification completed.',
        requestId: `req_${Date.now()}_${Math.random().toString(36).substring(2)}`
      },
      { status: 200 }
    );
  }
}

/**
 * GET /api/auth/code/verify
 * Return method not allowed for GET requests
 */
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405 }
  );
}

/**
 * OPTIONS /api/auth/code/verify
 * Handle CORS preflight requests
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}