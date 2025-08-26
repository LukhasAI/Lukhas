/**
 * Runtime Poetic Guard - Client-side validation for poetic content
 * Clamps poetic text to ≤40 words and ensures safety compliance
 */

interface PoeticPolicy {
  maxWords: number
  noClaims: boolean
}

const DEFAULT_POLICY: PoeticPolicy = {
  maxWords: 40,
  noClaims: true
}

// Common claim words to avoid in poetic content
const CLAIM_WORDS = [
  'guarantee', 'proven', 'certified', 'always', 'never', 'every', 'all', 'none',
  'breakthrough', 'revolutionary', 'seamlessly', 'effortlessly', 'instantly',
  'the future of', 'next generation', 'cutting-edge'
]

// Common metric patterns that should be avoided in poetic content
const METRIC_PATTERNS = [
  /\b\d+%\s*(accurate|reliable|success|improvement)\b/i,
  /\b(proven|validated|tested|verified)\s+(to|by)\b/i,
  /\b(always|never|every|all|none)\s+(works|fails|delivers)\b/i
]

/**
 * Validates and clamps poetic content to policy limits
 */
export function validatePoeticContent(content: string, policy: PoeticPolicy = DEFAULT_POLICY): {
  isValid: boolean
  clampedContent: string
  violations: string[]
  wordCount: number
} {
  const violations: string[] = []

  // Word count validation
  const words = content.trim().split(/\s+/).filter(word => word.length > 0)
  const wordCount = words.length

  let clampedContent = content

  // Clamp to max words if exceeded
  if (wordCount > policy.maxWords) {
    const clampedWords = words.slice(0, policy.maxWords)
    clampedContent = clampedWords.join(' ')
    violations.push(`Exceeded max words (${wordCount}/${policy.maxWords})`)
  }

  // Check for claims if policy requires no claims
  if (policy.noClaims) {
    // Check for claim words
    const lowerContent = content.toLowerCase()
    const foundClaimWords = CLAIM_WORDS.filter(word =>
      lowerContent.includes(word.toLowerCase())
    )
    if (foundClaimWords.length > 0) {
      violations.push(`Contains claim words: ${foundClaimWords.join(', ')}`)
    }

    // Check for metric patterns
    const foundMetrics = METRIC_PATTERNS.filter(pattern =>
      pattern.test(content)
    )
    if (foundMetrics.length > 0) {
      violations.push('Contains metrics or absolute statements')
    }
  }

  return {
    isValid: violations.length === 0,
    clampedContent,
    violations,
    wordCount
  }
}

/**
 * React hook for poetic content validation
 */
export function usePoeticValidation(content: string, policy?: PoeticPolicy) {
  return validatePoeticContent(content, policy)
}

/**
 * Utility to extract word count from text
 */
export function getWordCount(text: string): number {
  return text.trim().split(/\s+/).filter(word => word.length > 0).length
}

/**
 * Check if content appears to be poetic (contains common poetic indicators)
 */
export function isPoeticContent(content: string): boolean {
  const poeticIndicators = [
    /\b(dreams?|light|dance|symphony|harmony|bridge|essence|soul)\b/i,
    /\b(where|flowing|emerges?|whispers?|dances?)\b/i,
    /[,;]\s*\w+ing\b/i, // participial phrases
    /\b\w+\s+(meets?|becomes?)\s+\w+/i // metaphorical connections
  ]

  return poeticIndicators.some(pattern => pattern.test(content))
}

/**
 * Safe poetic content wrapper - ensures content meets policy
 */
export function safePoeticContent(content: string, fallback: string = ''): string {
  const validation = validatePoeticContent(content)

  if (validation.isValid) {
    return content
  }

  // Log violations in development
  if (process.env.NODE_ENV === 'development') {
    console.warn('[PoeticGuard] Poetic content violations:', validation.violations)
  }

  // Return clamped content or fallback
  return validation.clampedContent || fallback
}
