/**
 * Challenge Orchestrator for Adaptive MFA
 * Risk-based selection of emoji/word challenges (grid/swipe/sequence)
 */

import { getRedisClient } from '../middleware/rate-limit-redis'

export type ChallengeType = 'grid' | 'swipe' | 'sequence'
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export interface UserPreferences {
  preferredChallenge?: ChallengeType
  accessibility?: {
    highContrast: boolean
    keyboardNav: boolean
    screenReader: boolean
  }
}

export interface RiskFactors {
  deviceTrust: number      // 0-100: known device score
  geoNovelty: number       // 0-100: location anomaly score
  velocity: number         // 0-100: action frequency score
  recentResets: number     // Count of recent password/auth resets
  stepUpHistory: number    // Count of recent step-ups
}

export interface Challenge {
  id: string
  type: ChallengeType
  data: any
  ttl: number
  maxAttempts: number
  createdAt: number
}

export interface GridChallenge {
  type: 'grid'
  grid: string[][]      // 3x3 or 4x4 grid of emojis
  target: string[]      // Emojis to select in order
  accessibility: {
    labels: Record<string, string>  // Emoji -> description mapping
  }
}

export interface SwipeChallenge {
  type: 'swipe'
  sequence: string[]    // Emojis to swipe through
  directions: ('up' | 'down' | 'left' | 'right')[]
  accessibility: {
    labels: Record<string, string>
    keyboardMapping: Record<string, string>  // Key -> direction
  }
}

export interface SequenceChallenge {
  type: 'sequence'
  words: string[]       // Word pool
  correctSequence: number[]  // Indices of correct order
  accessibility: {
    pronunciation: Record<string, string>  // Phonetic hints
  }
}

// Risk score bands determine challenge requirements
export const RISK_BANDS = {
  LOW: { min: 0, max: 29, challenges: 0 },      // Passkey only
  MEDIUM: { min: 30, max: 59, challenges: 1 },   // Add one challenge
  HIGH: { min: 60, max: 79, challenges: 1, oob: true },  // Challenge + OOB
  CRITICAL: { min: 80, max: 100, passkeyOnly: true }     // Passkey required
} as const

/**
 * Calculate risk score from various factors
 */
export function calculateRiskScore(factors: RiskFactors): number {
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
export function getRiskLevel(score: number): RiskLevel {
  if (score <= RISK_BANDS.LOW.max) return 'low'
  if (score <= RISK_BANDS.MEDIUM.max) return 'medium'
  if (score <= RISK_BANDS.HIGH.max) return 'high'
  return 'critical'
}

/**
 * Pick appropriate challenge based on risk and preferences
 */
export async function pickChallenge(
  riskScore: number,
  preferences: UserPreferences
): Promise<Challenge | null> {
  const level = getRiskLevel(riskScore)

  // Low risk - no additional challenge needed
  if (level === 'low') {
    return null
  }

  // Critical risk - passkey only, no emoji challenges
  if (level === 'critical') {
    return null
  }

  // Select challenge type based on preferences and accessibility
  let challengeType: ChallengeType = preferences.preferredChallenge || 'grid'

  // Adjust for accessibility needs
  if (preferences.accessibility?.screenReader) {
    // Sequence works best with screen readers
    challengeType = 'sequence'
  } else if (preferences.accessibility?.keyboardNav) {
    // Grid or sequence for keyboard navigation
    challengeType = challengeType === 'swipe' ? 'grid' : challengeType
  }

  // Generate the challenge
  const challenge = await generateChallenge(challengeType, preferences)

  // Store in Redis with TTL
  const redis = await getRedisClient()
  const challengeKey = `challenge:${challenge.id}`
  await redis.setex(challengeKey, challenge.ttl, JSON.stringify(challenge))

  return challenge
}

/**
 * Generate a specific type of challenge
 */
async function generateChallenge(
  type: ChallengeType,
  preferences: UserPreferences
): Promise<Challenge> {
  const challengeId = crypto.randomUUID()
  const baseChallenge = {
    id: challengeId,
    type,
    ttl: 120,  // 2 minutes
    maxAttempts: 3,
    createdAt: Date.now()
  }

  switch (type) {
    case 'grid':
      return {
        ...baseChallenge,
        data: generateGridChallenge(preferences)
      }

    case 'swipe':
      return {
        ...baseChallenge,
        data: generateSwipeChallenge(preferences)
      }

    case 'sequence':
      return {
        ...baseChallenge,
        data: generateSequenceChallenge(preferences)
      }
  }
}

/**
 * Generate grid challenge with emojis
 */
function generateGridChallenge(preferences: UserPreferences): GridChallenge {
  // Emoji pool - chosen for clarity and distinctiveness
  const emojiPool = [
    '🌟', '🎨', '🚀', '🌈', '🎭', '🎪', '🎯', '🎲',
    '🌺', '🌸', '🌼', '🌻', '🌷', '🌹', '🏵️', '🌵',
    '🦋', '🐢', '🦜', '🦚', '🐠', '🦈', '🐙', '🦀',
    '🍎', '🍊', '🍋', '🍇', '🍓', '🍑', '🥝', '🍉'
  ]

  // High contrast mode uses more distinct emojis
  if (preferences.accessibility?.highContrast) {
    emojiPool.splice(0, emojiPool.length,
      '⭐', '🔴', '🔵', '🟢', '🟡', '🟣', '⚫', '⚪',
      '▲', '■', '●', '♦', '✦', '✚', '◉', '◐'
    )
  }

  // Create 3x3 grid
  const gridSize = 3
  const grid: string[][] = []
  const used = new Set<string>()

  for (let i = 0; i < gridSize; i++) {
    const row: string[] = []
    for (let j = 0; j < gridSize; j++) {
      let emoji: string
      do {
        emoji = emojiPool[Math.floor(Math.random() * emojiPool.length)]
      } while (used.has(emoji))
      used.add(emoji)
      row.push(emoji)
    }
    grid.push(row)
  }

  // Select 3-4 target emojis
  const targetCount = 3 + Math.floor(Math.random() * 2)
  const flatGrid = grid.flat()
  const target: string[] = []

  for (let i = 0; i < targetCount; i++) {
    target.push(flatGrid[Math.floor(Math.random() * flatGrid.length)])
  }

  // Generate accessibility labels
  const labels: Record<string, string> = {
    '🌟': 'star',
    '🎨': 'art palette',
    '🚀': 'rocket',
    '🌈': 'rainbow',
    '⭐': 'star shape',
    '🔴': 'red circle',
    '▲': 'triangle',
    '■': 'square',
    // ... add all emoji descriptions
  }

  return {
    type: 'grid',
    grid,
    target,
    accessibility: { labels }
  }
}

/**
 * Generate swipe challenge
 */
function generateSwipeChallenge(preferences: UserPreferences): SwipeChallenge {
  const emojiPool = ['🎯', '🎲', '🎨', '🚀', '🌟', '🌈']
  const sequence = []
  const directions: ('up' | 'down' | 'left' | 'right')[] = []

  // Generate 4-6 swipes
  const swipeCount = 4 + Math.floor(Math.random() * 3)

  for (let i = 0; i < swipeCount; i++) {
    sequence.push(emojiPool[Math.floor(Math.random() * emojiPool.length)])
    const dirs: ('up' | 'down' | 'left' | 'right')[] = ['up', 'down', 'left', 'right']
    directions.push(dirs[Math.floor(Math.random() * 4)])
  }

  return {
    type: 'swipe',
    sequence,
    directions,
    accessibility: {
      labels: {
        '🎯': 'target',
        '🎲': 'dice',
        '🎨': 'palette',
        '🚀': 'rocket',
        '🌟': 'star',
        '🌈': 'rainbow'
      },
      keyboardMapping: {
        'ArrowUp': 'up',
        'ArrowDown': 'down',
        'ArrowLeft': 'left',
        'ArrowRight': 'right',
        'w': 'up',
        's': 'down',
        'a': 'left',
        'd': 'right'
      }
    }
  }
}

/**
 * Generate word sequence challenge
 */
function generateSequenceChallenge(preferences: UserPreferences): SequenceChallenge {
  // Word pools by category
  const wordPools = {
    nature: ['river', 'mountain', 'forest', 'ocean', 'desert', 'valley'],
    colors: ['crimson', 'azure', 'emerald', 'golden', 'violet', 'silver'],
    actions: ['explore', 'discover', 'create', 'imagine', 'inspire', 'achieve']
  }

  // Pick a random category
  const categories = Object.keys(wordPools) as (keyof typeof wordPools)[]
  const category = categories[Math.floor(Math.random() * categories.length)]
  const pool = wordPools[category]

  // Select 4-5 words
  const wordCount = 4 + Math.floor(Math.random() * 2)
  const words: string[] = []
  const indices: number[] = []

  for (let i = 0; i < wordCount; i++) {
    let idx: number
    do {
      idx = Math.floor(Math.random() * pool.length)
    } while (indices.includes(idx))
    indices.push(idx)
    words.push(pool[idx])
  }

  // Shuffle for display
  const shuffled = [...words].sort(() => Math.random() - 0.5)
  const correctSequence = shuffled.map(w => words.indexOf(w))

  return {
    type: 'sequence',
    words: shuffled,
    correctSequence,
    accessibility: {
      pronunciation: {
        'azure': 'AZH-er',
        'crimson': 'KRIM-zuhn',
        'emerald': 'EM-er-uhld',
        // ... add pronunciations
      }
    }
  }
}

/**
 * Verify challenge response
 */
export async function verifyChallenge(
  challengeId: string,
  response: any
): Promise<{ verified: boolean; attemptsRemaining?: number }> {
  const redis = await getRedisClient()
  const challengeKey = `challenge:${challengeId}`
  const attemptKey = `challenge-attempts:${challengeId}`

  try {
    // Get challenge from Redis
    const challengeData = await redis.get(challengeKey)
    if (!challengeData) {
      return { verified: false }
    }

    const challenge: Challenge = JSON.parse(challengeData)

    // Check attempts
    const attempts = await redis.incr(attemptKey)
    await redis.expire(attemptKey, 120)  // Same TTL as challenge

    if (attempts > challenge.maxAttempts) {
      // Too many attempts - delete challenge
      await redis.del(challengeKey)
      return { verified: false, attemptsRemaining: 0 }
    }

    // Verify based on challenge type
    let verified = false

    switch (challenge.type) {
      case 'grid':
        verified = verifyGridResponse(challenge.data, response)
        break
      case 'swipe':
        verified = verifySwipeResponse(challenge.data, response)
        break
      case 'sequence':
        verified = verifySequenceResponse(challenge.data, response)
        break
    }

    if (verified) {
      // Clean up on success
      await redis.del(challengeKey)
      await redis.del(attemptKey)
      return { verified: true }
    }

    return {
      verified: false,
      attemptsRemaining: challenge.maxAttempts - attempts
    }
  } catch (error) {
    console.error('Challenge verification error:', error)
    return { verified: false }
  }
}

function verifyGridResponse(challenge: GridChallenge, response: string[]): boolean {
  return JSON.stringify(challenge.target) === JSON.stringify(response)
}

function verifySwipeResponse(challenge: SwipeChallenge, response: string[]): boolean {
  return JSON.stringify(challenge.directions) === JSON.stringify(response)
}

function verifySequenceResponse(challenge: SequenceChallenge, response: number[]): boolean {
  return JSON.stringify(challenge.correctSequence) === JSON.stringify(response)
}
