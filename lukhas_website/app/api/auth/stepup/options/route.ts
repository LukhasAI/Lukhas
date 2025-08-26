import { NextRequest, NextResponse } from 'next/server'
import { verifyJWT } from '@/packages/auth/jwt'
import { getRedisClient } from '@/packages/middleware/rate-limit-redis'

export async function GET(request: NextRequest) {
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

    // Get the latest challenge from Redis
    const redis = await getRedisClient()
    const keys = await redis.keys(`stepup:${payload.sub}:*`)

    if (!keys || keys.length === 0) {
      return NextResponse.json(
        { error: 'No active step-up session. Please start step-up first.' },
        { status: 400 }
      )
    }

    // Get the most recent challenge
    const latestKey = keys[keys.length - 1]
    const challengeData = await redis.get(latestKey)

    if (!challengeData) {
      return NextResponse.json(
        { error: 'Step-up session expired' },
        { status: 400 }
      )
    }

    const challenge = latestKey.split(':')[2]

    // Build WebAuthn options with userVerification required
    const options = {
      challenge: Buffer.from(challenge, 'base64url'),
      timeout: 60000,
      userVerification: 'required', // Forces Face ID / Touch ID / Windows Hello
      rpId: process.env.NEXT_PUBLIC_RP_ID || 'lukhas.ai',
      allowCredentials: [] // Will be populated with user's registered credentials
    }

    // Get user's registered credentials from database
    // This is a placeholder - implement based on your credential storage
    const userCredentials = await getUserCredentials(payload.sub)

    if (userCredentials && userCredentials.length > 0) {
      options.allowCredentials = userCredentials.map(cred => ({
        type: 'public-key',
        id: cred.credentialId,
        transports: cred.transports || ['internal', 'hybrid']
      }))
    }

    return NextResponse.json(options)
  } catch (error) {
    console.error('Step-up options error:', error)
    return NextResponse.json(
      { error: 'Failed to get step-up options' },
      { status: 500 }
    )
  }
}

// Placeholder function - implement based on your database schema
async function getUserCredentials(userId: string) {
  // TODO: Fetch from your database
  // For now, return empty array to allow platform authenticator
  return []
}
