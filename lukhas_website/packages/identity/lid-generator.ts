/**
 * LID (LUKHAS Identity) Generator
 * Generates canonical user IDs in format: lid_<ULID>
 */

import { ulid } from 'ulid'

/**
 * Generate a new LID (LUKHAS Identity)
 * Format: lid_<ULID>
 * ULID is uppercase, max 26 chars, so total is <= 30 chars
 */
export function generateLidId(): string {
  const ulidValue = ulid().toUpperCase()
  return `lid_${ulidValue}`
}

/**
 * Validate a LID format
 */
export function isValidLid(lid: string): boolean {
  return /^lid_[0-9A-Z]{26}$/.test(lid)
}

/**
 * Extract ULID from LID
 */
export function extractUlid(lid: string): string | null {
  if (!isValidLid(lid)) return null
  return lid.substring(4)
}

/**
 * Get timestamp from LID (via ULID)
 */
export function getLidTimestamp(lid: string): Date | null {
  const ulidPart = extractUlid(lid)
  if (!ulidPart) return null

  try {
    // ULID encodes timestamp in first 10 chars (48 bits)
    const timestampChars = ulidPart.substring(0, 10)
    const timestamp = decodeTime(timestampChars)
    return new Date(timestamp)
  } catch {
    return null
  }
}

// Decode ULID timestamp (simplified - use ulid library in production)
function decodeTime(timestampChars: string): number {
  const ENCODING = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
  let timestamp = 0

  for (const char of timestampChars) {
    const value = ENCODING.indexOf(char)
    if (value === -1) throw new Error('Invalid ULID character')
    timestamp = timestamp * 32 + value
  }

  return timestamp
}
