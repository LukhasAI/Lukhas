/**
 * LID Alias System
 * Generates PII-free public aliases in format: ΛiD#REALM/ZONE/TOKEN
 * Token is HMAC-derived, non-reversible, with check digit
 */

import { createHmac } from 'crypto'

export interface AliasConfig {
  realm: string  // e.g., "LUKHAS", "MATRIX", user-chosen
  zone: string   // e.g., "US", "EU", "AS"
  identifier: string  // The verified identifier (email/phone)
  idType: 'email' | 'phone' | 'other'
}

export interface AliasResult {
  aliasKey: string      // Normalized for lookups
  aliasDisplay: string  // Display format with ΛiD#
  realm: string
  zone: string
  token: string
}

/**
 * Build a public alias from verified identifier
 */
export async function buildAlias(config: AliasConfig): Promise<AliasResult> {
  const { realm, zone, identifier, idType } = config

  // Generate token from identifier
  const token = generateToken(identifier, idType)

  // Format for display
  const aliasDisplay = `ΛiD#${realm}/${zone}/${token}`

  // Normalized key for DB lookups (no special chars)
  const aliasKey = `${realm}${zone}${token}`.toUpperCase().replace(/[^A-Z0-9]/g, '')

  return {
    aliasKey,
    aliasDisplay,
    realm,
    zone,
    token
  }
}

/**
 * Generate HMAC token from identifier
 * Format: H-XXXX-XXXX-C (H prefix, 8 chars, check digit)
 */
function generateToken(identifier: string, idType: string): string {
  const secret = process.env.LID_ALIAS_SECRET || 'default-secret'

  // Create HMAC
  const hmac = createHmac('sha256', secret)
  hmac.update(`${idType}:${identifier.toLowerCase()}`)
  const hash = hmac.digest('hex')

  // Convert to Base32-like encoding (A-Z, 2-7)
  const encoded = hashToBase32(hash)

  // Take first 8 chars and add check digit
  const core = encoded.substring(0, 8)
  const checkDigit = calculateCheckDigit(core)

  // Format as H-XXXX-XXXX-C
  return `H-${core.substring(0, 4)}-${core.substring(4, 8)}-${checkDigit}`
}

/**
 * Convert hex hash to Base32-like encoding
 */
function hashToBase32(hash: string): string {
  const charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ234567' // Base32 without confusing chars
  let result = ''

  // Convert hex to base32
  for (let i = 0; i < hash.length; i += 2) {
    const byte = parseInt(hash.substr(i, 2), 16)
    result += charset[byte % 32]
    if (result.length >= 16) break // We only need 8-16 chars
  }

  return result
}

/**
 * Calculate Luhn-like check digit
 */
function calculateCheckDigit(input: string): string {
  const charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ234567'
  let sum = 0

  for (let i = 0; i < input.length; i++) {
    const charIndex = charset.indexOf(input[i])
    const weight = (i % 2 === 0) ? 2 : 1
    sum += (charIndex * weight) % 32
  }

  return charset[sum % charset.length]
}

/**
 * Validate alias format
 */
export function isValidAlias(alias: string): boolean {
  // Match ΛiD#REALM/ZONE/H-XXXX-XXXX-C format
  const pattern = /^ΛiD#[A-Z0-9-]{2,12}\/[A-Z]{2,3}\/H-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]$/
  return pattern.test(alias)
}

/**
 * Parse alias components
 */
export function parseAlias(alias: string): AliasResult | null {
  if (!isValidAlias(alias)) return null

  // Remove ΛiD# prefix
  const parts = alias.substring(4).split('/')
  if (parts.length !== 3) return null

  const [realm, zone, token] = parts
  const aliasKey = `${realm}${zone}${token}`.toUpperCase().replace(/[^A-Z0-9]/g, '')

  return {
    aliasKey,
    aliasDisplay: alias,
    realm,
    zone,
    token
  }
}

/**
 * Rotate alias token (for compromised aliases)
 */
export async function rotateAlias(
  currentAlias: string,
  newIdentifier?: string
): Promise<AliasResult> {
  const parsed = parseAlias(currentAlias)
  if (!parsed) throw new Error('Invalid alias format')

  // Add rotation salt to generate new token
  const rotationSalt = Date.now().toString()
  const identifierWithSalt = (newIdentifier || '') + rotationSalt

  return buildAlias({
    realm: parsed.realm,
    zone: parsed.zone,
    identifier: identifierWithSalt,
    idType: 'other' // Rotated aliases use 'other' type
  })
}
