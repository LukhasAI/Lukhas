import { NextRequest, NextResponse } from 'next/server'
import { generateChallenge } from '@/packages/auth/passkeys'
import { verifyJWT } from '@/packages/auth/jwt'
import { getRedisClient } from '@/packages/middleware/rate-limit-redis'

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

    // Generate challenge for step-up
    const challenge = generateChallenge()

    // Store challenge in Redis with 2-minute TTL
    const redis = await getRedisClient()
    const stepUpKey = `stepup:${payload.sub}:${challenge}`
    await redis.setex(stepUpKey, 120, JSON.stringify({
      userId: payload.sub,
      timestamp: Date.now(),
      purpose: request.headers.get('x-stepup-purpose') || 'sensitive-action'
    }))

    // Log step-up initiation
    console.log('auth.webauthn.stepup.start', {
      userId: payload.sub,
      purpose: request.headers.get('x-stepup-purpose'),
      timestamp: new Date().toISOString()
    })

    return NextResponse.json({
      success: true,
      challenge,
      message: 'Step-up authentication required'
    })
  } catch (error) {
    console.error('Step-up start error:', error)
    return NextResponse.json(
      { error: 'Failed to initiate step-up authentication' },
      { status: 500 }
    )
  }
}
