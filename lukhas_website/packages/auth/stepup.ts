/**
 * Step-up authentication for sensitive operations
 * Requires WebAuthn with userVerification for Face ID / Touch ID / Windows Hello
 */

import { NextRequest } from 'next/server'
import { getRedisClient } from '../middleware/rate-limit-redis'

export interface StepUpConfig {
  billing: boolean
  apiKeys: boolean
  orgRoles: boolean
  exports: boolean
}

// Default configuration for step-up requirements
export const STEP_UP_CONFIG: StepUpConfig = {
  billing: true,    // Payment confirms
  apiKeys: true,    // Create/rotate API keys
  orgRoles: true,   // Organization role changes
  exports: true     // Data exports from MΛTRIZ
}

// Sensitive operations that require step-up
export const STEP_UP_OPERATIONS = {
  BILLING_PAYMENT: 'billing.payment',
  BILLING_UPDATE: 'billing.update',
  API_KEY_CREATE: 'api.key.create',
  API_KEY_ROTATE: 'api.key.rotate',
  API_KEY_DELETE: 'api.key.delete',
  ORG_ROLE_CHANGE: 'org.role.change',
  ORG_MEMBER_REMOVE: 'org.member.remove',
  MATRIZ_EXPORT: 'matriz.export',
  ACCOUNT_DELETE: 'account.delete',
  SECURITY_SETTINGS: 'security.settings'
} as const

export type StepUpOperation = typeof STEP_UP_OPERATIONS[keyof typeof STEP_UP_OPERATIONS]

/**
 * Check if a step-up token is valid for the given operation
 */
export async function validateStepUpToken(
  token: string | undefined,
  operation: StepUpOperation,
  userId: string
): Promise<boolean> {
  if (!token) return false

  try {
    const redis = await getRedisClient()
    const key = `stepup-token:${token}`
    const data = await redis.get(key)

    if (!data) return false

    const tokenData = JSON.parse(data)

    // Validate token belongs to user and hasn't been used
    if (tokenData.userId !== userId || tokenData.used) {
      return false
    }

    // Check if token purpose matches the operation
    if (!isOperationAllowed(tokenData.purpose, operation)) {
      return false
    }

    // Mark token as used (single-use)
    await redis.set(key, JSON.stringify({ ...tokenData, used: true }), 'EX', 60)

    return true
  } catch (error) {
    console.error('Step-up token validation error:', error)
    return false
  }
}

/**
 * Check if an operation is allowed for a given purpose
 */
function isOperationAllowed(purpose: string, operation: StepUpOperation): boolean {
  // Map purposes to allowed operations
  const purposeMap: Record<string, StepUpOperation[]> = {
    'billing': [
      STEP_UP_OPERATIONS.BILLING_PAYMENT,
      STEP_UP_OPERATIONS.BILLING_UPDATE
    ],
    'api-keys': [
      STEP_UP_OPERATIONS.API_KEY_CREATE,
      STEP_UP_OPERATIONS.API_KEY_ROTATE,
      STEP_UP_OPERATIONS.API_KEY_DELETE
    ],
    'org-management': [
      STEP_UP_OPERATIONS.ORG_ROLE_CHANGE,
      STEP_UP_OPERATIONS.ORG_MEMBER_REMOVE
    ],
    'data-export': [
      STEP_UP_OPERATIONS.MATRIZ_EXPORT
    ],
    'account': [
      STEP_UP_OPERATIONS.ACCOUNT_DELETE,
      STEP_UP_OPERATIONS.SECURITY_SETTINGS
    ],
    'sensitive-action': Object.values(STEP_UP_OPERATIONS) // Generic purpose allows all
  }

  const allowedOps = purposeMap[purpose] || []
  return allowedOps.includes(operation)
}

/**
 * Middleware to require step-up for sensitive operations
 */
export async function requireStepUp(
  request: NextRequest,
  operation: StepUpOperation,
  userId: string
): Promise<{ allowed: boolean; error?: string }> {
  // Get step-up token from header or cookie
  const stepUpToken =
    request.headers.get('x-stepup-token') ||
    request.cookies.get('stepup-token')?.value

  if (!stepUpToken) {
    return {
      allowed: false,
      error: 'Step-up authentication required for this operation'
    }
  }

  const isValid = await validateStepUpToken(stepUpToken, operation, userId)

  if (!isValid) {
    return {
      allowed: false,
      error: 'Invalid or expired step-up token'
    }
  }

  return { allowed: true }
}

/**
 * Client-side helper to trigger step-up flow
 */
export async function triggerStepUp(purpose: string = 'sensitive-action'): Promise<string | null> {
  try {
    // Start step-up
    const startRes = await fetch('/api/auth/stepup/start', {
      method: 'POST',
      headers: { 'x-stepup-purpose': purpose }
    })

    if (!startRes.ok) throw new Error('Failed to start step-up')

    // Get WebAuthn options
    const optionsRes = await fetch('/api/auth/stepup/options')
    if (!optionsRes.ok) throw new Error('Failed to get options')

    const options = await optionsRes.json()

    // Convert challenge to ArrayBuffer
    options.challenge = base64UrlToArrayBuffer(options.challenge)

    // Request platform authenticator with UV
    options.userVerification = 'required'

    // Get credential from browser
    const credential = await navigator.credentials.get({
      publicKey: options
    }) as PublicKeyCredential

    if (!credential) throw new Error('No credential received')

    // Finish step-up
    const finishRes = await fetch('/api/auth/stepup/finish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: credential.id,
        rawId: arrayBufferToBase64Url(credential.rawId),
        response: {
          authenticatorData: arrayBufferToBase64Url(
            (credential.response as AuthenticatorAssertionResponse).authenticatorData
          ),
          clientDataJSON: arrayBufferToBase64Url(
            credential.response.clientDataJSON
          ),
          signature: arrayBufferToBase64Url(
            (credential.response as AuthenticatorAssertionResponse).signature
          ),
          userHandle: arrayBufferToBase64Url(
            (credential.response as AuthenticatorAssertionResponse).userHandle!
          )
        },
        type: credential.type
      })
    })

    if (!finishRes.ok) throw new Error('Step-up verification failed')

    const result = await finishRes.json()
    return result.stepUpToken
  } catch (error) {
    console.error('Step-up authentication failed:', error)
    return null
  }
}

// Helper functions for WebAuthn data conversion
function base64UrlToArrayBuffer(base64url: string): ArrayBuffer {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=')
  const binary = atob(padded)
  const buffer = new ArrayBuffer(binary.length)
  const bytes = new Uint8Array(buffer)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return buffer
}

function arrayBufferToBase64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  const base64 = btoa(binary)
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}
