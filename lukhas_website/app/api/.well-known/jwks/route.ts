/**
 * JWKS (JSON Web Key Set) API Endpoint
 *
 * Provides public keys for JWT verification at /.well-known/jwks.json
 * Implements proper caching and security headers.
 */

import { NextRequest, NextResponse } from 'next/server';
import { JWKSManager } from '../../../../packages/auth/jwks';

// Initialize JWKS manager with environment configuration
let jwksManager: JWKSManager | null = null;

async function initJWKSManager(): Promise<JWKSManager> {
  if (jwksManager) return jwksManager;

  const config = {
    privateKey: process.env.JWT_PRIVATE_KEY || '',
    publicKey: process.env.JWT_PUBLIC_KEY || '',
    keyId: process.env.JWT_KEY_ID || 'lukhas-auth-default',
    rotationDays: parseInt(process.env.JWKS_ROTATION_DAYS || '90')
  };

  // Validate configuration
  JWKSManager.validateConfig(config);

  jwksManager = new JWKSManager(config);
  await jwksManager.initialize();

  return jwksManager;
}

export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    // Security headers
    const headers = new Headers({
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=86400, must-revalidate', // 24 hours
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Access-Control-Allow-Origin': '*', // JWKS endpoints are public
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Max-Age': '86400'
    });

    // Initialize JWKS manager
    const manager = await initJWKSManager();

    // Generate JWKS response
    const jwks = manager.getJWKS();

    // Add metadata for monitoring
    const response = {
      ...jwks,
      _metadata: {
        issuer: 'https://lukhas.ai',
        generated_at: new Date().toISOString(),
        algorithm: 'RS256',
        key_count: jwks.keys.length
      }
    };

    return new NextResponse(JSON.stringify(response, null, 2), {
      status: 200,
      headers
    });

  } catch (error) {
    console.error('❌ JWKS endpoint error:', error);

    // Return generic error response (don't leak implementation details)
    return new NextResponse(
      JSON.stringify({
        error: 'service_unavailable',
        message: 'JWKS service is temporarily unavailable'
      }),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Retry-After': '300' // 5 minutes
        }
      }
    );
  }
}

// Disable other HTTP methods
export async function POST(): Promise<NextResponse> {
  return new NextResponse('Method Not Allowed', { status: 405 });
}

export async function PUT(): Promise<NextResponse> {
  return new NextResponse('Method Not Allowed', { status: 405 });
}

export async function DELETE(): Promise<NextResponse> {
  return new NextResponse('Method Not Allowed', { status: 405 });
}

export async function PATCH(): Promise<NextResponse> {
  return new NextResponse('Method Not Allowed', { status: 405 });
}
