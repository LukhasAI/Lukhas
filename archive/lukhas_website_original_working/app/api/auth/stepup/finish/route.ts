import { NextRequest, NextResponse } from 'next/server'
import { verifyJWT } from '@/packages/auth/jwt'
import { getRedisClient } from '@/packages/middleware/rate-limit-redis'
import { verifyAuthentication } from '@simplewebauthn/server'

export async function POST(request: NextRequest) {
  try {
    // Verify user is authenticated
    const token = request.cookies.get('auth-token')?.value
    if (!token) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
    }

    const payload = await verifyJWT(token)
    if (!payload) {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 })
    }

    const credential = await request.json()
    
    // Get the challenge from Redis
    const redis = await getRedisClient()
    const keys = await redis.keys(`stepup:${payload.sub}:*`)
    
    if (!keys || keys.length === 0) {
      return NextResponse.json(
        { error: 'No active step-up session' },
        { status: 400 }
      )
    }

    const latestKey = keys[keys.length - 1]
    const challengeData = await redis.get(latestKey)
    
    if (!challengeData) {
      return NextResponse.json(
        { error: 'Step-up session expired' },
        { status: 400 }
      )
    }

    const challenge = latestKey.split(':')[2]
    const { purpose } = JSON.parse(challengeData)

    // Verify the WebAuthn assertion
    const verification = await verifyAuthentication({
      response: credential,
      expectedChallenge: challenge,
      expectedOrigin: process.env.NEXT_PUBLIC_APP_URL || 'https://lukhas.ai',
      expectedRPID: process.env.NEXT_PUBLIC_RP_ID || 'lukhas.ai',
      requireUserVerification: true, // Ensure UV flag is set
      authenticator: {
        credentialID: credential.id,
        credentialPublicKey: Buffer.from(credential.response.publicKey || '', 'base64'),
        counter: 0
      }
    })

    if (!verification.verified) {
      // Log failed attempt
      console.log('auth.webauthn.stepup.fail', {
        userId: payload.sub,
        purpose,
        timestamp: new Date().toISOString()
      })
      
      return NextResponse.json(
        { error: 'Step-up authentication failed' },
        { status: 401 }
      )
    }

    // Check userVerification flag
    if (!verification.authenticationInfo?.userVerified) {
      return NextResponse.json(
        { error: 'User verification required but not provided' },
        { status: 401 }
      )
    }

    // Clean up Redis
    await redis.del(latestKey)

    // Generate step-up token with short TTL (5 minutes)
    const stepUpToken = await generateStepUpToken(payload.sub, purpose)

    // Log successful step-up
    console.log('auth.webauthn.stepup.ok', {
      userId: payload.sub,
      purpose,
      userVerified: true,
      timestamp: new Date().toISOString()
    })

    return NextResponse.json({
      success: true,
      stepUpToken,
      expiresIn: 300, // 5 minutes
      purpose,
      message: 'Step-up authentication successful'
    })
  } catch (error) {
    console.error('Step-up finish error:', error)
    return NextResponse.json(
      { error: 'Failed to complete step-up authentication' },
      { status: 500 }
    )
  }
}

// Generate a short-lived token for the specific sensitive action
async function generateStepUpToken(userId: string, purpose: string) {
  const redis = await getRedisClient()
  const token = Buffer.from(crypto.randomUUID()).toString('base64url')
  const stepUpTokenKey = `stepup-token:${token}`
  
  await redis.setex(stepUpTokenKey, 300, JSON.stringify({
    userId,
    purpose,
    timestamp: Date.now(),
    used: false
  }))
  
  return token
}