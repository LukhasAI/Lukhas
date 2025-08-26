/**
 * Emoji/Word Secret Management
 * Handles user's emoji and word secrets for adaptive MFA
 */

import { hash, verify } from 'argon2'
import { randomBytes } from 'crypto'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export interface EmojiSecretConfig {
  userId: string
  emojis?: string[]  // Selected emojis
  words?: string[]   // Selected words
  pattern?: string   // Optional pattern (e.g., "swipe-up-down-left")
}

/**
 * Create or update emoji/word secret for a user
 */
export async function setEmojiSecret(config: EmojiSecretConfig): Promise<boolean> {
  try {
    const { userId, emojis, words, pattern } = config

    // Combine all secret elements
    const secretElements: string[] = []
    if (emojis) secretElements.push(...emojis)
    if (words) secretElements.push(...words)
    if (pattern) secretElements.push(pattern)

    if (secretElements.length === 0) {
      throw new Error('No secret elements provided')
    }

    // Create secret string
    const secretString = secretElements.join(':')

    // Generate salt
    const salt = randomBytes(32)

    // Hash with Argon2id (OWASP recommended)
    const secretHash = await hashSecret(secretString, salt)

    // Check if user already has a secret
    const existing = await prisma.emojiSecret.findUnique({
      where: { userId }
    })

    if (existing) {
      // Update existing
      await prisma.emojiSecret.update({
        where: { userId },
        data: {
          secretHash,
          salt,
          rotatedAt: new Date()
        }
      })
    } else {
      // Create new
      await prisma.emojiSecret.create({
        data: {
          userId,
          secretHash,
          salt,
          enabled: true
        }
      })
    }

    // Log security event (no secret data)
    await prisma.securityEvent.create({
      data: {
        userId,
        kind: 'emoji.secret.set',
        meta: {
          hasEmojis: !!emojis,
          hasWords: !!words,
          hasPattern: !!pattern,
          timestamp: new Date().toISOString()
        }
      }
    })

    return true
  } catch (error) {
    console.error('Failed to set emoji secret:', error)
    return false
  }
}

/**
 * Verify emoji/word secret
 */
export async function verifyEmojiSecret(
  userId: string,
  attempt: EmojiSecretConfig
): Promise<boolean> {
  try {
    // Get user's secret
    const emojiSecret = await prisma.emojiSecret.findUnique({
      where: { userId }
    })

    if (!emojiSecret || !emojiSecret.enabled) {
      return false
    }

    // Build attempt string
    const attemptElements: string[] = []
    if (attempt.emojis) attemptElements.push(...attempt.emojis)
    if (attempt.words) attemptElements.push(...attempt.words)
    if (attempt.pattern) attemptElements.push(attempt.pattern)

    const attemptString = attemptElements.join(':')

    // Verify with constant-time comparison
    const isValid = await verifySecret(
      attemptString,
      emojiSecret.secretHash,
      emojiSecret.salt
    )

    // Log attempt
    await prisma.securityEvent.create({
      data: {
        userId,
        kind: isValid ? 'emoji.verify.success' : 'emoji.verify.fail',
        meta: {
          timestamp: new Date().toISOString()
        }
      }
    })

    return isValid
  } catch (error) {
    console.error('Failed to verify emoji secret:', error)
    return false
  }
}

/**
 * Hash secret with Argon2id
 */
async function hashSecret(secret: string, salt: Buffer): Promise<string> {
  const pepper = process.env.SECRET_PEPPER || ''
  const combined = secret + pepper

  return hash(combined, {
    type: 2, // Argon2id
    salt,
    memoryCost: 65536, // 64 MB
    timeCost: 3,
    parallelism: 4,
    hashLength: 32
  })
}

/**
 * Verify secret with constant-time comparison
 */
async function verifySecret(
  attempt: string,
  hash: string,
  salt: Buffer
): Promise<boolean> {
  const pepper = process.env.SECRET_PEPPER || ''
  const combined = attempt + pepper

  try {
    return verify(hash, combined, {
      type: 2,
      salt,
      memoryCost: 65536,
      timeCost: 3,
      parallelism: 4,
      hashLength: 32
    })
  } catch {
    return false
  }
}

/**
 * Disable emoji secret (for account recovery)
 */
export async function disableEmojiSecret(userId: string): Promise<void> {
  await prisma.emojiSecret.updateMany({
    where: { userId },
    data: { enabled: false }
  })

  await prisma.securityEvent.create({
    data: {
      userId,
      kind: 'emoji.secret.disabled',
      meta: {
        timestamp: new Date().toISOString()
      }
    }
  })
}

/**
 * Check if user has emoji secret enabled
 */
export async function hasEmojiSecret(userId: string): Promise<boolean> {
  const secret = await prisma.emojiSecret.findUnique({
    where: { userId },
    select: { enabled: true }
  })

  return secret?.enabled || false
}
