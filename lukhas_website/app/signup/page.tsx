'use client'

import React, { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeftIcon, EnvelopeIcon, KeyIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

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
      } else {
        setError(result.error || 'Failed to send verification email')
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
        } else {
          setStep('complete')
        }
      } else {
        setError(result.error || 'Invalid verification code')
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
          } else {
            setError(result.error || 'Failed to register passkey')
          }
        } else {
          throw new Error('Registration request failed')
        }
      }
    } catch (err: any) {
      if (err.name === 'NotAllowedError') {
        setError('Passkey creation was cancelled')
      } else if (err.name === 'SecurityError') {
        setError('Passkey creation failed due to security restrictions')
      } else {
        setError('Failed to create passkey. You can skip this step.')
      }
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
    "Begin with your own key; the rest follows.",
    "Confirm your email, then create a passkey. Add a second device for safety.",
    "Email verification, then passkey registration. Password is disabled by default. Recovery via backup codes or additional passkeys."
  )

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between p-6">
        <Link href="/" className="flex items-center text-white/80 hover:text-white transition-colors">
          <ChevronLeftIcon className="w-5 h-5 mr-2" />
          Back to LUKHAS AI
        </Link>
        <div className="text-sm text-white/60">
          Already have an account? <Link href="/login" className="text-trinity-identity hover:text-trinity-consciousness transition-colors">Sign in</Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Lambda Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-trinity-consciousness/20 backdrop-blur-xl border border-trinity-consciousness/30 mb-4">
              <span className="text-2xl font-light text-trinity-consciousness">Λ</span>
            </div>
            <h1 className="text-2xl font-light text-white mb-2">
              Create your ΛiD
            </h1>
            <p className="text-white/60 text-sm">
              Join LUKHAS AI consciousness platform
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-center mb-8 space-x-2">
            {['email', 'verify', 'passkey', 'complete'].map((stepName, index) => (
              <div key={stepName} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                  step === stepName 
                    ? 'bg-trinity-consciousness text-white' 
                    : ['email', 'verify'].indexOf(step) > index || step === 'complete'
                    ? 'bg-trinity-guardian text-white'
                    : 'bg-white/10 text-white/40'
                }`}>
                  {(['email', 'verify'].indexOf(step) > index || step === 'complete') && stepName !== step ? (
                    <CheckCircleIcon className="w-4 h-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                {index < 3 && (
                  <div className={`w-8 h-0.5 ${
                    ['email', 'verify'].indexOf(step) > index || step === 'complete'
                      ? 'bg-trinity-guardian' 
                      : 'bg-white/10'
                  }`} />
                )}
              </div>
            ))}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
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
                    placeholder="Enter your email"
                    disabled={loading}
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <EnvelopeIcon className="w-5 h-5 mr-3" />
                  {loading ? 'Sending...' : 'Continue with email'}
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
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex items-center justify-center px-6 py-4 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Verifying...' : 'Verify email'}
                  </button>
                </form>
                <button
                  onClick={() => setStep('email')}
                  className="w-full text-sm text-white/60 hover:text-white/80 transition-colors"
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
                  <KeyIcon className="w-5 h-5 mr-3" />
                  {loading ? 'Creating passkey...' : 'Create passkey'}
                </button>
                <button
                  onClick={skipPasskey}
                  className="w-full text-sm text-white/60 hover:text-white/80 transition-colors"
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
            "Email addresses verified before account creation",
            "Passkey credentials encoded → GLYPH format for security",
            "No passwords collected, stored, or transmitted",
            "Account data encrypted at rest with AES-256",
            "Registration events logged for security monitoring"
          ]}
          className="max-w-4xl mx-auto"
        />
      </div>
    </div>
  )
}