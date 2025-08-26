/**
 * Risk Scoring Engine for Adaptive MFA
 * Calculates risk based on various factors and determines authentication requirements
 */

import { PrismaClient } from '@prisma/client'
import { createHash } from 'crypto'

const prisma = new PrismaClient()

export interface RiskFactors {
  deviceTrust: number      // 0-100: known device score
  geoNovelty: number       // 0-100: location anomaly score
  velocity: number         // 0-100: action frequency score
  recentResets: number     // Count of recent password/auth resets
  stepUpHistory: number    // Count of recent step-ups
}

export interface RiskContext {
  userId: string
  ipAddress: string
  userAgent: string
  deviceId?: string
  action: string
}

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

// Risk score bands
export const RISK_BANDS = {
  LOW: { min: 0, max: 29 },
  MEDIUM: { min: 30, max: 59 },
  HIGH: { min: 60, max: 79 },
  CRITICAL: { min: 80, max: 100 }
} as const

/**
 * Calculate comprehensive risk score
 */
export async function calculateRisk(context: RiskContext): Promise<{
  score: number
  level: RiskLevel
  factors: RiskFactors
  recommendations: string[]
}> {
  const factors = await gatherRiskFactors(context)
  const score = computeRiskScore(factors)
  const level = getRiskLevel(score)
  const recommendations = getRecommendations(level, factors)

  // Log risk assessment
  await prisma.securityEvent.create({
    data: {
      userId: context.userId,
      kind: 'risk.assessment',
      meta: {
        score,
        level,
        factors,
        action: context.action,
        timestamp: new Date().toISOString()
      }
    }
  })

  return { score, level, factors, recommendations }
}

/**
 * Gather risk factors from various sources
 */
async function gatherRiskFactors(context: RiskContext): Promise<RiskFactors> {
  const { userId, ipAddress, userAgent, deviceId } = context

  // Device trust score
  const deviceTrust = await calculateDeviceTrust(userId, deviceId, userAgent)

  // Geographic novelty
  const geoNovelty = await calculateGeoNovelty(userId, ipAddress)

  // Action velocity
  const velocity = await calculateVelocity(userId)

  // Recent resets
  const recentResets = await countRecentResets(userId)

  // Step-up history
  const stepUpHistory = await countRecentStepUps(userId)

  return {
    deviceTrust,
    geoNovelty,
    velocity,
    recentResets,
    stepUpHistory
  }
}

/**
 * Calculate device trust score
 */
async function calculateDeviceTrust(
  userId: string,
  deviceId?: string,
  userAgent?: string
): Promise<number> {
  if (!deviceId) return 0

  // Check if device has been seen before
  const deviceHash = hashDevice(deviceId, userAgent || '')

  // Look for recent successful authentications from this device
  const recentAuths = await prisma.securityEvent.count({
    where: {
      userId,
      kind: { in: ['auth.success', 'auth.stepup.ok'] },
      meta: {
        path: ['deviceHash'],
        equals: deviceHash
      },
      createdAt: {
        gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) // Last 30 days
      }
    }
  })

  // More recent auths = higher trust
  const trustScore = Math.min(100, recentAuths * 10)
  return trustScore
}

/**
 * Calculate geographic novelty score
 */
async function calculateGeoNovelty(
  userId: string,
  ipAddress: string
): Promise<number> {
  // Get IP geolocation (simplified - use MaxMind or similar in production)
  const geoHash = hashIP(ipAddress)

  // Check if this geo has been seen before
  const knownGeos = await prisma.securityEvent.count({
    where: {
      userId,
      kind: { in: ['auth.success'] },
      meta: {
        path: ['geoHash'],
        equals: geoHash
      },
      createdAt: {
        gte: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) // Last 90 days
      }
    }
  })

  // New location = higher novelty score
  if (knownGeos === 0) return 80
  if (knownGeos < 5) return 40
  return 10
}

/**
 * Calculate action velocity score
 */
async function calculateVelocity(userId: string): Promise<number> {
  // Count recent sensitive actions
  const recentActions = await prisma.securityEvent.count({
    where: {
      userId,
      kind: {
        in: [
          'auth.stepup.ok',
          'api.key.create',
          'api.key.rotate',
          'billing.update',
          'org.role.change'
        ]
      },
      createdAt: {
        gte: new Date(Date.now() - 60 * 60 * 1000) // Last hour
      }
    }
  })

  // High velocity = higher risk
  if (recentActions >= 10) return 90
  if (recentActions >= 5) return 60
  if (recentActions >= 3) return 30
  return 10
}

/**
 * Count recent password/auth resets
 */
async function countRecentResets(userId: string): Promise<number> {
  return prisma.securityEvent.count({
    where: {
      userId,
      kind: { in: ['password.reset', 'recovery.complete', 'passkey.reset'] },
      createdAt: {
        gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // Last 7 days
      }
    }
  })
}

/**
 * Count recent step-up authentications
 */
async function countRecentStepUps(userId: string): Promise<number> {
  return prisma.securityEvent.count({
    where: {
      userId,
      kind: 'auth.stepup.ok',
      createdAt: {
        gte: new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
      }
    }
  })
}

/**
 * Compute final risk score from factors
 */
function computeRiskScore(factors: RiskFactors): number {
  const weights = {
    deviceTrust: -0.3,    // Negative weight (trust reduces risk)
    geoNovelty: 0.25,
    velocity: 0.2,
    recentResets: 0.15,
    stepUpHistory: 0.1
  }

  let score = 50  // Base score

  // Apply weighted factors
  score += factors.deviceTrust * weights.deviceTrust
  score += factors.geoNovelty * weights.geoNovelty
  score += factors.velocity * weights.velocity
  score += factors.recentResets * weights.recentResets * 10  // Scale up
  score += factors.stepUpHistory * weights.stepUpHistory * 5

  // Clamp to 0-100
  return Math.max(0, Math.min(100, Math.round(score)))
}

/**
 * Determine risk level from score
 */
function getRiskLevel(score: number): RiskLevel {
  if (score <= RISK_BANDS.LOW.max) return 'low'
  if (score <= RISK_BANDS.MEDIUM.max) return 'medium'
  if (score <= RISK_BANDS.HIGH.max) return 'high'
  return 'critical'
}

/**
 * Get security recommendations based on risk
 */
function getRecommendations(level: RiskLevel, factors: RiskFactors): string[] {
  const recommendations: string[] = []

  switch (level) {
    case 'low':
      // Passkey only
      recommendations.push('Standard authentication sufficient')
      break

    case 'medium':
      // Add one challenge
      recommendations.push('Require additional verification')
      recommendations.push('Use emoji/word challenge')
      break

    case 'high':
      // Challenge + OOB
      recommendations.push('Require multi-factor authentication')
      recommendations.push('Send out-of-band confirmation')
      recommendations.push('Notify user of high-risk activity')
      break

    case 'critical':
      // Passkey required, no alternatives
      recommendations.push('Require passkey authentication only')
      recommendations.push('Disable alternative authentication methods')
      recommendations.push('Enforce cooldown period')
      recommendations.push('Alert security team')
      break
  }

  // Specific recommendations based on factors
  if (factors.deviceTrust < 30) {
    recommendations.push('Unknown device - require additional verification')
  }

  if (factors.geoNovelty > 70) {
    recommendations.push('New location detected - verify identity')
  }

  if (factors.velocity > 50) {
    recommendations.push('High activity rate - possible automation')
  }

  if (factors.recentResets > 0) {
    recommendations.push('Recent security changes - heightened monitoring')
  }

  return recommendations
}

// Helper functions
function hashDevice(deviceId: string, userAgent: string): string {
  return createHash('sha256')
    .update(`${deviceId}:${userAgent}`)
    .digest('hex')
    .substring(0, 16)
}

function hashIP(ip: string): string {
  // Hash IP to /24 subnet for privacy
  const subnet = ip.split('.').slice(0, 3).join('.')
  return createHash('sha256')
    .update(subnet)
    .digest('hex')
    .substring(0, 16)
}
