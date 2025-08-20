'use client'

import React, { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeftIcon, EnvelopeIcon, KeyIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'
import { AnnouncementManager, FocusManager } from '@/lib/accessibility'

// Registration flow steps
type RegistrationStep = 'email' | 'verify' | 'passkey' | 'complete'

// Passkey support detection
const supportsPasskeys = () => {
  if (typeof window === 'undefined') return false
  return !!(window.PublicKeyCredential && window.navigator.credentials && window.navigator.credentials.create)
}

export default function SignupPage() {
  const router = useRouter()
  const [step, setStep] = useState<RegistrationStep>('email')
  const [email, setEmail] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [passkeySupported] = useState(() => supportsPasskeys())
  const [userId, setUserId] = useState('')

  // Step 1: Email submission
  const handleEmailSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email.trim()) {
      setError('Please enter your email address')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/signup/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })

      const result = await response.json()

      if (response.ok && result.success) {
        setStep('verify')
        AnnouncementManager.announceAuthState('success', 'Verification email sent. Please check your inbox.')
      } else {
        const errorMsg = result.error || 'Failed to send verification email'
        setError(errorMsg)
        AnnouncementManager.announceAuthState('error', errorMsg)
        setTimeout(() => FocusManager.focusFirstError(), 100)
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [email])

  // Step 2: Email verification
  const handleEmailVerification = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!verificationCode.trim()) {
      setError('Please enter the verification code')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/signup/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: email.trim(),
          code: verificationCode.trim()
        })
      })

      const result = await response.json()

      if (response.ok && result.success) {
        setUserId(result.userId)
        if (passkeySupported) {
          setStep('passkey')
          AnnouncementManager.announce('Email verified. Now create your passkey for secure access.')
        } else {
          setStep('complete')
          AnnouncementManager.announce('Email verified. Account creation complete.')
        }
      } else {
        const errorMsg = result.error || 'Invalid verification code'
        setError(errorMsg)
        AnnouncementManager.announceAuthState('error', errorMsg)
        setTimeout(() => FocusManager.focusFirstError(), 100)
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [email, verificationCode, passkeySupported])

  // Step 3: Passkey registration
  const handlePasskeyRegistration = useCallback(async () => {
    if (!passkeySupported) {
      setStep('complete')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Get registration options from server
      const optionsResponse = await fetch('/api/auth/passkey/register-options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          userId,
          email,
          displayName: email.split('@')[0]
        })
      })

      if (!optionsResponse.ok) {
        throw new Error('Failed to get registration options')
      }

      const options = await optionsResponse.json()

      // Create passkey
      const credential = await navigator.credentials.create({
        publicKey: {
          challenge: new Uint8Array(options.challenge),
          rp: options.rp,
          user: {
            id: new Uint8Array(options.user.id),
            name: options.user.name,
            displayName: options.user.displayName
          },
          pubKeyCredParams: options.pubKeyCredParams,
          timeout: 60000,
          attestation: 'direct',
          authenticatorSelection: {
            authenticatorAttachment: 'platform',
            userVerification: 'required',
            residentKey: 'preferred'
          }
        }
      })

      if (credential) {
        // Register the passkey with server
        const registerResponse = await fetch('/api/auth/passkey/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId,
            credential: {
              id: credential.id,
              rawId: Array.from(new Uint8Array(credential.rawId)),
              response: {
                attestationObject: Array.from(new Uint8Array(credential.response.attestationObject)),
                clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON))
              }
            }
          })
        })

        if (registerResponse.ok) {
          const result = await registerResponse.json()
          if (result.success) {
            setStep('complete')
            AnnouncementManager.announceAuthState('success', 'Passkey created successfully. Your account is now secure.')
          } else {
            const errorMsg = result.error || 'Failed to register passkey'
            setError(errorMsg)
            AnnouncementManager.announceAuthState('error', errorMsg)
          }
        } else {
          throw new Error('Registration request failed')
        }
      }
    } catch (err: any) {
      let errorMsg = ''
      if (err.name === 'NotAllowedError') {
        errorMsg = 'Passkey creation was cancelled'
      } else if (err.name === 'SecurityError') {
        errorMsg = 'Passkey creation failed due to security restrictions'
      } else {
        errorMsg = 'Failed to create passkey. You can skip this step.'
      }
      setError(errorMsg)
      AnnouncementManager.announceAuthState('error', errorMsg)
      setTimeout(() => FocusManager.focusFirstError(), 100)
    } finally {
      setLoading(false)
    }
  }, [passkeySupported, userId, email])

  const skipPasskey = useCallback(() => {
    setStep('complete')
  }, [])

  const handleComplete = useCallback(() => {
    router.push('/login')
  }, [router])

  const toneContent = threeLayerTone(
    "Begin with your own key; the rest follows. Λ consciousness awakens through authentic identity, guided by Superior Consciousness principles.",
    "First, we'll verify your email address with a secure code. Then you can create a passkey using your device's biometric security. Consider adding a second device for backup access. Your account will be protected by quantum-inspired security protocols.",
    "Multi-step registration: Email verification with 6-digit time-limited codes, followed by optional passkey registration using WebAuthn. Password authentication permanently disabled by design. Account recovery via backup codes or additional registered passkeys. Rate limiting enforced. Bio-inspired adaptation monitors registration patterns for fraud detection."
  )

  // JSON-LD structured data for registration page
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "LUKHAS AI ΛiD Registration",
    "description": "Create a secure LUKHAS AI account with quantum-inspired identity verification and bio-inspired authentication",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation"
    },
    "potentialAction": {
      "@type": "RegisterAction",
      "name": "Create ΛiD Account",
      "description": "Register for LUKHAS AI with email verification and passkey setup"
    }
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <div className="min-h-screen bg-bg-primary flex flex-col">
      {/* Skip to main content link for accessibility */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-trinity-consciousness text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-white z-50"
      >
        Skip to main content
      </a>
      
      {/* Header */}
      <header className="flex items-center justify-between p-6" role="banner">
        <Link href="/" className="flex items-center text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:ring-offset-2 focus:ring-offset-bg-primary rounded">
          <ChevronLeftIcon className="w-5 h-5 mr-2" aria-hidden="true" />
          Back to LUKHAS AI
        </Link>
        <div className="text-sm text-white/60">
          Already have an account? <Link href="/login" className="text-trinity-identity hover:text-trinity-consciousness transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-1">Sign in</Link>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-1 flex items-center justify-center px-6 py-12" role="main">
        <div className="w-full max-w-md">
          {/* Lambda Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-trinity-consciousness/20 backdrop-blur-xl border border-trinity-consciousness/30 mb-4">
              <span className="text-2xl font-light text-trinity-consciousness" aria-label="LUKHAS AI Superior Consciousness">Λ</span>
            </div>
            <h1 className="text-2xl font-light text-white mb-2" id="page-title">
              Create your ΛiD
            </h1>
            <p className="text-white/60 text-sm">
              Join the LUKHAS AI platform
            </p>
            <div className="mt-2 text-xs text-white/40">
              Protected by quantum-inspired identity protocols and bio-inspired security adaptation
            </div>
          </div>

          {/* Progress Steps */}
          <div className="mb-8" role="progressbar" aria-valuenow={['email', 'verify', 'passkey', 'complete'].indexOf(step) + 1} aria-valuemin={1} aria-valuemax={4} aria-label="Registration progress">
            <div className="flex items-center justify-center space-x-2">
              {['email', 'verify', 'passkey', 'complete'].map((stepName, index) => {
                const stepLabels = ['Email', 'Verify', 'Passkey', 'Complete']
                const isComplete = (['email', 'verify'].indexOf(step) > index || step === 'complete') && stepName !== step
                const isCurrent = step === stepName
                
                return (
                  <div key={stepName} className="flex items-center">
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                        isCurrent
                          ? 'bg-trinity-consciousness text-white' 
                          : isComplete
                          ? 'bg-trinity-guardian text-white'
                          : 'bg-white/10 text-white/40'
                      }`}
                      aria-label={`Step ${index + 1}: ${stepLabels[index]}${isCurrent ? ' (current)' : isComplete ? ' (completed)' : ''}`}
                      role="img"
                    >
                      {isComplete ? (
                        <CheckCircleIcon className="w-4 h-4" aria-hidden="true" />
                      ) : (
                        <span aria-hidden="true">{index + 1}</span>
                      )}
                    </div>
                    {index < 3 && (
                      <div className={`w-8 h-0.5 ${
                        isComplete || (['email', 'verify'].indexOf(step) > index)
                          ? 'bg-trinity-guardian' 
                          : 'bg-white/10'
                      }`} aria-hidden="true" />
                    )}
                  </div>
                )
              })}
            </div>
            <div className="text-center mt-2">
              <span className="text-xs text-white/60" aria-live="polite">
                Step {['email', 'verify', 'passkey', 'complete'].indexOf(step) + 1} of 4: {step === 'email' ? 'Email Address' : step === 'verify' ? 'Email Verification' : step === 'passkey' ? 'Create Passkey' : 'Complete'}
              </span>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm" role="alert" aria-live="polite">
              <div className="flex items-start">
                <ExclamationCircleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-medium mb-1">Registration Error</p>
                  <p>{error}</p>
                  {error.includes('already exists') && (
                    <p className="mt-2 text-sm">
                      <Link href="/login" className="text-red-300 hover:text-red-200 underline">
                        Sign in to existing account
                      </Link>
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step Content */}
          <div className="space-y-6">
            {/* Step 1: Email */}
            {step === 'email' && (
              <form onSubmit={handleEmailSubmit} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
                    Email address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:border-transparent"
                    placeholder="Enter your email address"
                    disabled={loading}
                    required
                    aria-describedby="email-signup-help"
                    autoComplete="email"
                  />
                  <div id="email-signup-help" className="sr-only">
                    Enter a valid email address to create your LUKHAS AI account
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin" aria-hidden="true" />
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <EnvelopeIcon className="w-5 h-5 mr-3" />
                      <span>Continue with email</span>
                    </>
                  )}
                </button>
              </form>
            )}

            {/* Step 2: Email Verification */}
            {step === 'verify' && (
              <div className="space-y-4">
                <div className="text-center mb-6">
                  <p className="text-white/80 mb-2">Check your email</p>
                  <p className="text-white/60 text-sm">
                    We sent a verification code to <span className="text-trinity-consciousness">{email}</span>
                  </p>
                </div>
                <form onSubmit={handleEmailVerification} className="space-y-4">
                  <div>
                    <label htmlFor="code" className="block text-sm font-medium text-white/80 mb-2">
                      Verification code
                    </label>
                    <input
                      type="text"
                      id="code"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      className="w-full px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:border-transparent text-center tracking-widest text-lg"
                      placeholder="000000"
                      maxLength={6}
                      disabled={loading}
                      required
                      aria-describedby="code-help"
                      autoComplete="one-time-code"
                    />
                    <div id="code-help" className="sr-only">
                      Enter the 6-digit verification code sent to your email
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex items-center justify-center px-6 py-4 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <div className="w-5 h-5 mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin" aria-hidden="true" />
                        <span>Verifying...</span>
                      </>
                    ) : (
                      <span>Verify email</span>
                    )}
                  </button>
                </form>
                <button
                  onClick={() => setStep('email')}
                  className="w-full text-sm text-white/60 hover:text-white/80 transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
                  type="button"
                >
                  Use different email
                </button>
              </div>
            )}

            {/* Step 3: Passkey Registration */}
            {step === 'passkey' && (
              <div className="space-y-4">
                <div className="text-center mb-6">
                  <KeyIcon className="w-12 h-12 text-trinity-consciousness mx-auto mb-4" />
                  <p className="text-white/80 mb-2">Create your passkey</p>
                  <p className="text-white/60 text-sm">
                    Secure your account with biometric authentication
                  </p>
                </div>
                <button
                  onClick={handlePasskeyRegistration}
                  disabled={loading}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin" aria-hidden="true" />
                      <span>Creating passkey...</span>
                    </>
                  ) : (
                    <>
                      <KeyIcon className="w-5 h-5 mr-3" />
                      <span>Create passkey</span>
                    </>
                  )}
                </button>
                <button
                  onClick={skipPasskey}
                  className="w-full text-sm text-white/60 hover:text-white/80 transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-consciousness focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
                  type="button"
                >
                  Skip for now (you can add it later)
                </button>
              </div>
            )}

            {/* Step 4: Complete */}
            {step === 'complete' && (
              <div className="text-center space-y-6">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-trinity-guardian/20 backdrop-blur-xl border border-trinity-guardian/30 mb-4">
                  <CheckCircleIcon className="w-8 h-8 text-trinity-guardian" />
                </div>
                <div>
                  <h2 className="text-xl font-light text-white mb-2">
                    Welcome to LUKHAS AI
                  </h2>
                  <p className="text-white/60 text-sm mb-6">
                    Your ΛiD has been created successfully
                  </p>
                </div>
                <button
                  onClick={handleComplete}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium"
                >
                  Continue to sign in
                </button>
              </div>
            )}
          </div>

          {/* Tone Content */}
          <div className="mt-8 text-xs text-white/40 leading-relaxed whitespace-pre-line">
            {toneContent}
          </div>
        </div>
      </main>

      {/* Transparency Box */}
      <div className="px-6 pb-6">
        <TransparencyBox
          capabilities={[
            "Email verification with secure 6-digit codes",
            "Passkey (WebAuthn) registration with biometric verification",
            "Progressive registration flow with optional steps",
            "Account creation with LUKHAS AI tier system integration",
            "Secure session establishment upon completion"
          ]}
          limitations={[
            "Email verification required for all accounts",
            "Passkey creation requires compatible browser/device",
            "Verification codes expire after 10 minutes",
            "One account per email address",
            "Some features require tier upgrades after registration"
          ]}
          dependencies={[
            "Email service for verification code delivery",
            "WebAuthn API for passkey creation (optional)",
            "LUKHAS AI identity system and database",
            "Browser support for credential management API"
          ]}
          dataHandling={[
            "Email addresses verified before account creation with secure 6-digit codes",
            "Passkey credentials encoded → GLYPH symbolic format for enhanced interoperability (data representation, not cryptographic security)",
            "No passwords collected, stored, or transmitted at any point",
            "Account data encrypted at rest with AES-256 encryption",
            "Registration events logged for security monitoring and fraud prevention"
          ]}
          className="max-w-4xl mx-auto"
        />
      </div>
    </div>
    </>
  )
}