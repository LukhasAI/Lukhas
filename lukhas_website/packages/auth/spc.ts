/**
 * Secure Payment Confirmation (SPC) implementation
 * WebAuthn-based payment authentication with transaction binding
 */

export interface SPCTransactionData {
  amount: string
  currency: string
  payee: string
  paymentMethodId?: string
  orderId?: string
}

export interface SPCOptions {
  rpId: string
  challenge: string
  instrument: {
    displayName: string
    icon: string
    iconMustBeShown?: boolean
  }
  payeeOrigin?: string
  timeout?: number
}

/**
 * Check if SPC is supported in the current browser
 */
export function isSPCSupported(): boolean {
  return !!(
    window.PaymentRequest &&
    window.PublicKeyCredential &&
    'secure-payment-confirmation' in window
  )
}

/**
 * Initialize SPC for a payment transaction
 */
export async function initiateSPC(
  transaction: SPCTransactionData,
  credentialId: string
): Promise<PaymentResponse | null> {
  try {
    // Check if SPC is enabled via feature flag
    const featureFlag = process.env.NEXT_PUBLIC_FEATURE_SPC === 'true'
    if (!featureFlag || !isSPCSupported()) {
      console.log('SPC not supported or disabled, falling back to standard WebAuthn')
      return null
    }

    // Generate challenge for this transaction
    const challenge = await generateTransactionChallenge(transaction)

    // Build SPC data
    const spcData: SPCOptions = {
      rpId: process.env.NEXT_PUBLIC_RP_ID || 'lukhas.ai',
      challenge,
      instrument: {
        displayName: 'LUKHAS AI Payment',
        icon: '/icons/lukhas-payment.png',
        iconMustBeShown: true
      },
      payeeOrigin: process.env.NEXT_PUBLIC_APP_URL || 'https://lukhas.ai',
      timeout: 60000
    }

    // Build payment method data
    const methodData: PaymentMethodData[] = [{
      supportedMethods: 'secure-payment-confirmation',
      data: {
        ...spcData,
        credentialIds: [base64UrlToArrayBuffer(credentialId)],
        challenge: base64UrlToArrayBuffer(challenge)
      }
    }]

    // Build payment details
    const details: PaymentDetailsInit = {
      total: {
        label: `Payment to ${transaction.payee}`,
        amount: {
          currency: transaction.currency,
          value: transaction.amount
        }
      },
      displayItems: [{
        label: 'LUKHAS AI Service',
        amount: {
          currency: transaction.currency,
          value: transaction.amount
        }
      }]
    }

    // Create payment request
    const request = new PaymentRequest(methodData, details)

    // Check if payment can be made
    const canMake = await request.canMakePayment()
    if (!canMake) {
      console.log('SPC payment cannot be made, falling back')
      return null
    }

    // Show payment UI and get response
    const response = await request.show()

    // The response contains the WebAuthn assertion bound to the transaction
    return response
  } catch (error) {
    console.error('SPC failed:', error)
    return null
  }
}

/**
 * Verify SPC payment response on the server
 */
export async function verifySPCPayment(
  response: any,
  transaction: SPCTransactionData
): Promise<{ verified: boolean; transactionId?: string }> {
  try {
    // Extract WebAuthn assertion from payment response
    const assertion = response.details

    // Verify the assertion is bound to the correct transaction
    const clientData = JSON.parse(
      new TextDecoder().decode(
        base64UrlToArrayBuffer(assertion.clientDataJSON)
      )
    )

    // Check payment extension data
    if (clientData.payment) {
      const { amount, currency, payee } = clientData.payment

      // Verify transaction details match
      if (
        amount !== transaction.amount ||
        currency !== transaction.currency ||
        (payee && payee !== transaction.payee)
      ) {
        console.error('Transaction details mismatch')
        return { verified: false }
      }
    }

    // Verify WebAuthn signature (simplified - use proper verification in production)
    const verified = await verifyWebAuthnAssertion(assertion)

    if (verified) {
      // Generate transaction ID
      const transactionId = generateTransactionId()

      // Log successful SPC verification
      console.log('payment.spc.verified', {
        transactionId,
        amount: transaction.amount,
        currency: transaction.currency,
        timestamp: new Date().toISOString()
      })

      return { verified: true, transactionId }
    }

    return { verified: false }
  } catch (error) {
    console.error('SPC verification failed:', error)
    return { verified: false }
  }
}

/**
 * Fallback to standard WebAuthn step-up for payments
 */
export async function fallbackToWebAuthnPayment(
  transaction: SPCTransactionData
): Promise<boolean> {
  try {
    // Use the step-up authentication flow
    const { triggerStepUp } = await import('./stepup')

    // Trigger step-up with billing purpose
    const stepUpToken = await triggerStepUp('billing')

    if (!stepUpToken) {
      return false
    }

    // Verify payment with step-up token
    const response = await fetch('/api/payments/confirm', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-stepup-token': stepUpToken
      },
      body: JSON.stringify(transaction)
    })

    return response.ok
  } catch (error) {
    console.error('WebAuthn payment fallback failed:', error)
    return false
  }
}

/**
 * Main payment confirmation flow with SPC and fallback
 */
export async function confirmPayment(
  transaction: SPCTransactionData,
  credentialId?: string
): Promise<{ success: boolean; transactionId?: string; method: 'spc' | 'webauthn' }> {
  // Try SPC first if credential is available
  if (credentialId && isSPCSupported()) {
    const spcResponse = await initiateSPC(transaction, credentialId)

    if (spcResponse) {
      // Complete the payment
      await spcResponse.complete('success')

      // Verify on server
      const verification = await verifySPCPayment(spcResponse, transaction)

      if (verification.verified) {
        return {
          success: true,
          transactionId: verification.transactionId,
          method: 'spc'
        }
      }
    }
  }

  // Fallback to standard WebAuthn step-up
  console.log('Falling back to WebAuthn step-up for payment')
  const fallbackSuccess = await fallbackToWebAuthnPayment(transaction)

  return {
    success: fallbackSuccess,
    transactionId: fallbackSuccess ? generateTransactionId() : undefined,
    method: 'webauthn'
  }
}

/**
 * Generate challenge specific to transaction
 */
async function generateTransactionChallenge(transaction: SPCTransactionData): string {
  const encoder = new TextEncoder()
  const data = encoder.encode(
    `${transaction.amount}${transaction.currency}${transaction.payee}${Date.now()}`
  )
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  return arrayBufferToBase64Url(hashBuffer)
}

/**
 * Verify WebAuthn assertion (simplified)
 */
async function verifyWebAuthnAssertion(assertion: any): Promise<boolean> {
  // This is a placeholder - implement proper WebAuthn verification
  // using @simplewebauthn/server or similar library
  return true
}

/**
 * Generate unique transaction ID
 */
function generateTransactionId(): string {
  return `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Helper functions
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
