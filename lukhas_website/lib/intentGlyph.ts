// lib/intentGlyph.ts
// Intent detection and glyph mapping for smart particle morphing

import { seedFromString } from './prng'
import { generateShapeDNA, type ShapeDNA } from './shape-dna'

export interface Intent {
  type: 'shape' | 'emotion' | 'action' | 'concept'
  confidence: number // 0-1
  keywords: string[]
  glyphText?: string // extracted quotable text
  shapeDNA?: ShapeDNA
}

export interface GlyphEvent {
  text: string
  intent: Intent
  duration: number // ms to hold glyph
  priority: 'low' | 'medium' | 'high'
  timestamp: number
}

// Intent detection patterns
const INTENT_PATTERNS = {
  shape: [
    { pattern: /\b(sphere|ball|circle|round)\b/i, confidence: 0.9, shape: 'sphere' },
    { pattern: /\b(cube|box|square|block)\b/i, confidence: 0.9, shape: 'cube' },
    { pattern: /\b(torus|donut|ring)\b/i, confidence: 0.9, shape: 'torus' },
    { pattern: /\b(helix|spiral|twist|dna)\b/i, confidence: 0.9, shape: 'helix' },
    { pattern: /\b(triangle|pyramid)\b/i, confidence: 0.8, shape: 'cube' }, // fallback
    { pattern: /\b(star|sparkle)\b/i, confidence: 0.7, shape: 'sphere' }
  ],

  emotion: [
    { pattern: /\b(happy|joy|excited|energetic|bright)\b/i, confidence: 0.8, shape: 'sphere' },
    { pattern: /\b(sad|melancholy|down|heavy)\b/i, confidence: 0.8, shape: 'cube' },
    { pattern: /\b(angry|frustrated|intense|sharp)\b/i, confidence: 0.8, shape: 'helix' },
    { pattern: /\b(calm|peaceful|serene|flowing)\b/i, confidence: 0.8, shape: 'torus' },
    { pattern: /\b(chaotic|random|wild|crazy)\b/i, confidence: 0.7, shape: 'helix' }
  ],

  action: [
    { pattern: /\b(spin|rotate|turn|whirl)\b/i, confidence: 0.9, shape: 'torus' },
    { pattern: /\b(expand|grow|inflate|swell)\b/i, confidence: 0.8, shape: 'sphere' },
    { pattern: /\b(contract|shrink|collapse)\b/i, confidence: 0.8, shape: 'cube' },
    { pattern: /\b(twist|spiral|coil)\b/i, confidence: 0.9, shape: 'helix' },
    { pattern: /\b(pulse|beat|throb|oscillate)\b/i, confidence: 0.8, shape: 'sphere' }
  ],

  concept: [
    { pattern: /\b(consciousness|awareness|mind|thought)\b/i, confidence: 0.9, shape: 'sphere' },
    { pattern: /\b(memory|remember|recall|past)\b/i, confidence: 0.8, shape: 'helix' },
    { pattern: /\b(identity|self|who|am)\b/i, confidence: 0.8, shape: 'torus' },
    { pattern: /\b(structure|system|framework|architecture)\b/i, confidence: 0.7, shape: 'cube' },
    { pattern: /\b(flow|stream|current|wave)\b/i, confidence: 0.8, shape: 'helix' }
  ]
}

// Quote extraction patterns
const QUOTE_PATTERNS = [
  /"([^"]+)"/g,           // Double quotes
  /'([^']+)'/g,           // Single quotes
  /«([^»]+)»/g,           // French quotes
  /„([^"]+)"/g,           // German quotes
  /「([^」]+)」/g,         // Japanese quotes
  /\*([^*]+)\*/g,         // Emphasis asterisks
  /\b([A-Z][A-Z\s]{2,15})\b/g // ALL CAPS short phrases
]

/**
 * Analyze text for intent and extract glyph opportunities
 */
export function analyzeIntent(text: string): Intent[] {
  const intents: Intent[] = []
  const lowerText = text.toLowerCase()

  // Check each intent category
  for (const [category, patterns] of Object.entries(INTENT_PATTERNS)) {
    for (const { pattern, confidence, shape } of patterns) {
      const matches = lowerText.match(pattern)
      if (matches) {
        const intent: Intent = {
          type: category as Intent['type'],
          confidence,
          keywords: matches,
          shapeDNA: shape ? generateShapeDNA(`${category}-${shape}-${text.slice(0, 20)}`) : undefined
        }

        intents.push(intent)
      }
    }
  }

  // Extract potential glyph text
  const quotes = extractQuotes(text)
  if (quotes.length > 0) {
    // Find the most significant quote
    const bestQuote = quotes.reduce((best, current) =>
      current.length > best.length ? current : best
    )

    if (bestQuote.length >= 3 && bestQuote.length <= 50) {
      intents.push({
        type: 'concept',
        confidence: 0.9,
        keywords: [bestQuote],
        glyphText: bestQuote,
        shapeDNA: generateShapeDNA(bestQuote)
      })
    }
  }

  // Sort by confidence
  return intents.sort((a, b) => b.confidence - a.confidence)
}

/**
 * Extract quotable text from message
 */
export function extractQuotes(text: string): string[] {
  const quotes: string[] = []

  for (const pattern of QUOTE_PATTERNS) {
    let match
    while ((match = pattern.exec(text)) !== null) {
      const quote = match[1]?.trim()
      if (quote && quote.length >= 2 && quote.length <= 100) {
        quotes.push(quote)
      }
    }
  }

  // Remove duplicates and sort by length (longer = more significant)
  return Array.from(new Set(quotes)).sort((a, b) => b.length - a.length)
}

/**
 * Generate glyph event from chat message
 */
export function createGlyphEvent(
  message: string,
  role: 'user' | 'assistant' = 'user'
): GlyphEvent | null {
  const intents = analyzeIntent(message)

  if (intents.length === 0) return null

  const primaryIntent = intents[0]

  // Determine text to visualize
  let glyphText = primaryIntent.glyphText
  if (!glyphText) {
    // Use first significant word if no quotes found
    const significantWords = message.split(/\s+/).filter(word =>
      word.length >= 4 && !/^(the|and|but|for|are|you|all|can|had|her|was|one|our|out|day|get|has|him|his|how|its|may|new|now|old|see|two|way|who|boy|did|she|use|man|can|her|now|old|see|way|who)$/i.test(word)
    )
    glyphText = significantWords[0] || message.split(' ')[0] || 'IDEA'
  }

  // Determine priority and duration
  let priority: GlyphEvent['priority'] = 'medium'
  let duration = 2000 // default 2 seconds

  if (role === 'assistant') {
    priority = 'high'
    duration = 3000 // AI responses held longer
  } else if (primaryIntent.confidence > 0.8) {
    priority = 'high'
    duration = 2500
  } else if (primaryIntent.confidence < 0.5) {
    priority = 'low'
    duration = 1500
  }

  return {
    text: glyphText.toUpperCase().slice(0, 20), // Limit length and capitalize
    intent: primaryIntent,
    duration,
    priority,
    timestamp: Date.now()
  }
}

/**
 * Process glyph queue and determine what to render
 */
export class GlyphQueue {
  private queue: GlyphEvent[] = []
  private currentEvent: GlyphEvent | null = null
  private timeoutId: number | null = null

  /**
   * Add glyph event to queue
   */
  addEvent(event: GlyphEvent): void {
    // Remove lower priority events if queue is full
    if (this.queue.length >= 3) {
      this.queue = this.queue.filter(e => e.priority !== 'low')
    }

    // Insert by priority
    const insertIndex = this.queue.findIndex(e => e.priority < event.priority)
    if (insertIndex === -1) {
      this.queue.push(event)
    } else {
      this.queue.splice(insertIndex, 0, event)
    }

    // Start processing if not already active
    if (!this.currentEvent) {
      this.processNext()
    }
  }

  /**
   * Process next event in queue
   */
  private processNext(): void {
    if (this.queue.length === 0) {
      this.currentEvent = null
      return
    }

    this.currentEvent = this.queue.shift()!

    // Emit glyph render event
    window.dispatchEvent(new CustomEvent('lukhas-render-glyph', {
      detail: {
        text: this.currentEvent.text,
        intent: this.currentEvent.intent,
        duration: this.currentEvent.duration
      }
    }))

    // Schedule next event
    this.timeoutId = window.setTimeout(() => {
      this.processNext()
    }, this.currentEvent.duration)
  }

  /**
   * Clear queue and current event
   */
  clear(): void {
    this.queue = []
    this.currentEvent = null

    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }
  }

  /**
   * Get current glyph text being displayed
   */
  getCurrentText(): string | null {
    return this.currentEvent?.text || null
  }

  /**
   * Get queue status
   */
  getStatus(): { current: string | null; queued: number; priority: string | null } {
    return {
      current: this.currentEvent?.text || null,
      queued: this.queue.length,
      priority: this.currentEvent?.priority || null
    }
  }
}

// Global glyph queue instance
export const globalGlyphQueue = new GlyphQueue()

/**
 * Helper to process chat message and queue glyph
 */
export function processMessageForGlyph(
  message: string,
  role: 'user' | 'assistant' = 'user'
): void {
  const event = createGlyphEvent(message, role)
  if (event) {
    globalGlyphQueue.addEvent(event)
  }
}
