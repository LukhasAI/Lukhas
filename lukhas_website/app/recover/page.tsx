'use client'

import React, { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeftIcon, KeyIcon, ShieldCheckIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'

// Recovery flow steps
type RecoveryStep = 'method' | 'backup' | 'passkey' | 'complete'

// Recovery methods
type RecoveryMethod = 'backup-codes' | 'new-passkey' | 'support'

export default function RecoverPage() {
  const router = useRouter()
  const [step, setStep] = useState<RecoveryStep>('method')
  const [method, setMethod] = useState<RecoveryMethod>('backup-codes')
  const [email, setEmail] = useState('')
  const [backupCodes, setBackupCodes] = useState(['', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [warning, setWarning] = useState('')

  // Method selection
  const handleMethodSelect = useCallback((selectedMethod: RecoveryMethod) => {
    setMethod(selectedMethod)
    setError('')
    setWarning('')

    if (selectedMethod === 'backup-codes') {
      setStep('backup')
    } else if (selectedMethod === 'new-passkey') {
      setStep('passkey')
    } else {
      // Support method - redirect to support
      window.location.href = '/support?type=account-recovery'
    }
  }, [])

  // Backup code validation
  const handleBackupCodeSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    const codes = backupCodes.filter(code => code.trim().length > 0)
    if (codes.length === 0) {
      setError('Please enter at least one backup code')
      return
    }

    if (!email.trim()) {
      setError('Please enter your email address')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/recover/backup-codes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: email.trim(),
          codes: codes.map(code => code.trim())
        })
      })

      const result = await response.json()

      if (response.ok && result.success) {
        // Log in user with recovery session
        if (result.tokens) {
          // Store tokens and redirect
          localStorage.setItem('lukhas_access_token', result.tokens.accessToken)
          localStorage.setItem('lukhas_refresh_token', result.tokens.refreshToken)
          setStep('complete')
        } else {
          setError('Recovery authentication failed')
        }
      } else {
        setError(result.error || 'Invalid backup codes')
        
        // Show warning about remaining codes
        if (result.remainingCodes !== undefined) {
          setWarning(`${result.remainingCodes} backup codes remaining`)
        }
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [email, backupCodes])

  // New passkey registration for recovery
  const handleNewPasskeyRecovery = useCallback(async () => {
    if (!email.trim()) {
      setError('Please enter your email address first')
      return
    }

    setLoading(true)
    setError('')

    try {
      // First, verify user exists and send verification
      const verifyResponse = await fetch('/api/auth/recover/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })

      if (!verifyResponse.ok) {
        throw new Error('Email verification failed')
      }

      // Get passkey registration options
      const optionsResponse = await fetch('/api/auth/recover/passkey-options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })

      if (!optionsResponse.ok) {
        throw new Error('Failed to get registration options')
      }

      const options = await optionsResponse.json()

      // Create new passkey
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
        // Register the recovery passkey
        const registerResponse = await fetch('/api/auth/recover/register-passkey', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email.trim(),
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
            setError(result.error || 'Failed to register recovery passkey')
          }
        } else {
          throw new Error('Recovery registration failed')
        }
      }
    } catch (err: any) {
      if (err.name === 'NotAllowedError') {
        setError('Passkey creation was cancelled')
      } else if (err.name === 'SecurityError') {
        setError('Passkey creation failed due to security restrictions')
      } else {
        setError('Failed to create recovery passkey. Please try backup codes or contact support.')
      }
    } finally {
      setLoading(false)
    }
  }, [email])

  const handleComplete = useCallback(() => {
    router.push('/experience')
  }, [router])

  const toneContent = threeLayerTone(
    "When keys are lost, other doors remain; the path continues.",
    "Use your backup codes or create a new passkey on this device. Contact support if needed.",
    "Backup codes provide one-time access with remaining count tracking. New passkey registration requires email verification. Support escalation available for critical access."
  )

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between p-6">
        <Link href="/login" className="flex items-center text-white/80 hover:text-white transition-colors">
          <ChevronLeftIcon className="w-5 h-5 mr-2" />
          Back to sign in
        </Link>
        <div className="text-sm text-white/60">
          New to LUKHAS AI? <Link href="/signup" className="text-trinity-identity hover:text-trinity-consciousness transition-colors">Create account</Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Lambda Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-trinity-guardian/20 backdrop-blur-xl border border-trinity-guardian/30 mb-4">
              <ShieldCheckIcon className="w-8 h-8 text-trinity-guardian" />
            </div>
            <h1 className="text-2xl font-light text-white mb-2">
              Recover your ΛiD
            </h1>
            <p className="text-white/60 text-sm">
              Regain access to your LUKHAS AI account
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Warning Display */}
          {warning && (
            <div className="mb-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-sm flex items-start">
              <ExclamationTriangleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
              {warning}
            </div>
          )}

          {/* Step Content */}
          <div className="space-y-6">
            {/* Step 1: Recovery Method Selection */}
            {step === 'method' && (
              <div className="space-y-4">
                <div className="mb-6">
                  <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
                    Email address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent"
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-white/80 mb-3">Choose recovery method:</h3>
                  
                  {/* Backup Codes Option */}
                  <button
                    onClick={() => handleMethodSelect('backup-codes')}
                    className="w-full p-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-left hover:border-trinity-guardian/50 transition-colors group"
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-10 h-10 bg-trinity-guardian/20 rounded-lg flex items-center justify-center mr-3">
                        <ShieldCheckIcon className="w-5 h-5 text-trinity-guardian" />
                      </div>
                      <div>
                        <h4 className="text-white font-medium mb-1">Use backup codes</h4>
                        <p className="text-white/60 text-sm">Enter one or more of your saved backup codes</p>
                      </div>
                    </div>
                  </button>

                  {/* New Passkey Option */}
                  <button
                    onClick={() => handleMethodSelect('new-passkey')}
                    className="w-full p-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-left hover:border-trinity-guardian/50 transition-colors group"
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-10 h-10 bg-trinity-consciousness/20 rounded-lg flex items-center justify-center mr-3">
                        <KeyIcon className="w-5 h-5 text-trinity-consciousness" />
                      </div>
                      <div>
                        <h4 className="text-white font-medium mb-1">Create new passkey</h4>
                        <p className="text-white/60 text-sm">Add a passkey on this device (requires email verification)</p>
                      </div>
                    </div>
                  </button>

                  {/* Support Option */}
                  <button
                    onClick={() => handleMethodSelect('support')}
                    className="w-full p-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-left hover:border-trinity-guardian/50 transition-colors group"
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center mr-3">
                        <ExclamationTriangleIcon className="w-5 h-5 text-yellow-400" />
                      </div>
                      <div>
                        <h4 className="text-white font-medium mb-1">Contact support</h4>
                        <p className="text-white/60 text-sm">Get help from our security team</p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Backup Code Entry */}
            {step === 'backup' && (
              <div className="space-y-4">
                <button
                  onClick={() => setStep('method')}
                  className="text-sm text-white/60 hover:text-white/80 transition-colors mb-4"
                >
                  ← Choose different method
                </button>

                <div className="text-center mb-6">
                  <ShieldCheckIcon className="w-12 h-12 text-trinity-guardian mx-auto mb-4" />
                  <p className="text-white/80 mb-2">Enter your backup codes</p>
                  <p className="text-white/60 text-sm">
                    You can enter multiple codes for verification
                  </p>
                </div>

                <form onSubmit={handleBackupCodeSubmit} className="space-y-4">
                  {backupCodes.map((code, index) => (
                    <div key={index}>
                      <label htmlFor={`code-${index}`} className="block text-sm font-medium text-white/80 mb-2">
                        Backup code {index + 1} {index === 0 && <span className="text-red-400">*</span>}
                      </label>
                      <input
                        type="text"
                        id={`code-${index}`}
                        value={code}
                        onChange={(e) => {
                          const newCodes = [...backupCodes]
                          newCodes[index] = e.target.value
                          setBackupCodes(newCodes)
                        }}
                        className="w-full px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-guardian focus:border-transparent text-center tracking-widest font-mono"
                        placeholder="XXXX-XXXX-XXXX"
                        maxLength={14}
                        disabled={loading}
                        required={index === 0}
                      />
                    </div>
                  ))}

                  <button
                    type="submit"
                    disabled={loading || !backupCodes[0].trim()}
                    className="w-full flex items-center justify-center px-6 py-4 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Verifying...' : 'Recover account'}
                  </button>
                </form>
              </div>
            )}

            {/* Step 3: New Passkey Creation */}
            {step === 'passkey' && (
              <div className="space-y-4">
                <button
                  onClick={() => setStep('method')}
                  className="text-sm text-white/60 hover:text-white/80 transition-colors mb-4"
                >
                  ← Choose different method
                </button>

                <div className="text-center mb-6">
                  <KeyIcon className="w-12 h-12 text-trinity-consciousness mx-auto mb-4" />
                  <p className="text-white/80 mb-2">Create recovery passkey</p>
                  <p className="text-white/60 text-sm">
                    This will add a new passkey to your account on this device
                  </p>
                </div>

                <button
                  onClick={handleNewPasskeyRecovery}
                  disabled={loading || !email.trim()}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-consciousness hover:bg-trinity-identity transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <KeyIcon className="w-5 h-5 mr-3" />
                  {loading ? 'Creating passkey...' : 'Create recovery passkey'}
                </button>

                <div className="text-center">
                  <p className="text-xs text-white/50">
                    This will require email verification and biometric authentication
                  </p>
                </div>
              </div>
            )}

            {/* Step 4: Complete */}
            {step === 'complete' && (
              <div className="text-center space-y-6">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-trinity-guardian/20 backdrop-blur-xl border border-trinity-guardian/30 mb-4">
                  <ShieldCheckIcon className="w-8 h-8 text-trinity-guardian" />
                </div>
                <div>
                  <h2 className="text-xl font-light text-white mb-2">
                    Account recovered
                  </h2>
                  <p className="text-white/60 text-sm mb-6">
                    You now have access to your LUKHAS AI account
                  </p>
                </div>
                <button
                  onClick={handleComplete}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-guardian hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium"
                >
                  Continue to experience
                </button>
                <div className="text-center">
                  <Link 
                    href="/settings/security" 
                    className="text-sm text-trinity-consciousness hover:text-trinity-identity transition-colors"
                  >
                    Review security settings
                  </Link>
                </div>
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
            "Backup code verification with rate limiting",
            "New passkey registration for account recovery",
            "Email verification for recovery operations",
            "Support escalation for critical access issues",
            "Secure session establishment after recovery"
          ]}
          limitations={[
            "Backup codes are single-use and have limited quantity",
            "New passkey creation requires browser/device support",
            "Recovery operations are rate-limited for security",
            "Support recovery may take 24-48 hours",
            "Some recovery methods may require additional verification"
          ]}
          dependencies={[
            "Email service for recovery verification",
            "WebAuthn API for new passkey creation",
            "LUKHAS AI security and audit systems",
            "Support ticketing system for escalations"
          ]}
          dataHandling={[
            "Backup codes hashed and securely stored with usage tracking",
            "Recovery operations logged for security auditing",
            "New passkey credentials encoded → GLYPH format",
            "Email communications secured with TLS encryption",
            "Account recovery events monitored for suspicious activity"
          ]}
          className="max-w-4xl mx-auto"
        />
      </div>
    </div>
  )
}