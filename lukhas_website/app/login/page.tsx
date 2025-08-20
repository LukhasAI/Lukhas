'use client'

import React, { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeftIcon, KeyIcon, EnvelopeIcon, ExclamationCircleIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/transparency-box'
import { threeLayerTone } from '@/lib/toneSystem'
import { AnnouncementManager, FocusManager } from '@/lib/accessibility'

// Passkey detection and browser support
const supportsPasskeys = () => {
  if (typeof window === 'undefined') return false
  return !!(window.PublicKeyCredential && window.navigator.credentials && window.navigator.credentials.create)
}

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMagicLink, setShowMagicLink] = useState(false)
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const [passkeySupported] = useState(() => supportsPasskeys())

  // Handle passkey authentication
  const handlePasskeyAuth = useCallback(async () => {
    AnnouncementManager.announceAuthState('loading', 'Starting passkey authentication...')
    if (!passkeySupported) {
      setError('Passkeys are not supported in your browser. Please use a magic link instead.')
      setShowMagicLink(true)
      return
    }

    setLoading(true)
    setError('')

    try {
      // Request passkey authentication
      const credential = await navigator.credentials.get({
        publicKey: {
          challenge: new Uint8Array(32), // This would come from server
          allowCredentials: [], // Empty to allow any registered credential
          userVerification: 'required',
          timeout: 60000
        }
      })

      if (credential) {
        // Send credential to server for verification
        const response = await fetch('/api/auth/passkey/authenticate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            credential: {
              id: credential.id,
              rawId: Array.from(new Uint8Array(credential.rawId)),
              response: {
                authenticatorData: Array.from(new Uint8Array(credential.response.authenticatorData)),
                clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON)),
                signature: Array.from(new Uint8Array(credential.response.signature)),
                userHandle: credential.response.userHandle ? Array.from(new Uint8Array(credential.response.userHandle)) : null
              }
            }
          })
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            AnnouncementManager.announceAuthState('success', 'Successfully authenticated with passkey')
            router.push('/experience')
          } else {
            const errorMsg = result.error || 'Authentication failed'
            setError(errorMsg)
            AnnouncementManager.announceAuthState('error', errorMsg)
          }
        } else {
          throw new Error('Authentication request failed')
        }
      }
    } catch (err: any) {
      let errorMsg = ''
      if (err.name === 'NotAllowedError') {
        errorMsg = 'Authentication was cancelled or not allowed'
      } else if (err.name === 'InvalidStateError') {
        errorMsg = 'No registered passkeys found. Please create an account first.'
        setTimeout(() => router.push('/signup'), 2000)
      } else {
        errorMsg = 'Passkey authentication failed. Please try a magic link instead.'
        setShowMagicLink(true)
      }
      setError(errorMsg)
      AnnouncementManager.announceAuthState('error', errorMsg)
      
      // Focus the error message for screen readers
      setTimeout(() => FocusManager.focusFirstError(), 100)
    } finally {
      setLoading(false)
    }
  }, [passkeySupported, router])

  // Handle magic link request
  const handleMagicLink = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    AnnouncementManager.announceAuthState('loading', 'Sending secure magic link...')
    
    if (!email.trim()) {
      setError('Please enter your email address')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/magic-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })

      // Always show success message (enumeration protection)
      setMagicLinkSent(true)
      AnnouncementManager.announceAuthState('success', 'Magic link sent. Please check your email.')
    } catch (err) {
      // Still show success message for enumeration protection
      setMagicLinkSent(true)
      AnnouncementManager.announceAuthState('success', 'Magic link sent. Please check your email.')
    } finally {
      setLoading(false)
    }
  }, [email])

  const toneContent = threeLayerTone(
    "The door knows your hand; nothing to remember, only to be. Λ consciousness recognizes your essence through Superior Consciousness authentication.",
    "Use your device to sign in securely with your fingerprint or face. If passkeys don't work, we'll email you a secure one-time link instead. Keep your backup codes safe somewhere only you can access. Your authentication is protected by quantum-inspired security protocols.",
    "Passkeys (WebAuthn UV) primary authentication with magic-link fallback. Short-lived JWTs with rotating refresh tokens and reuse-detection. Device binding required. Step-up authentication enforced for billing operations, API key management, and organization administration. Rate limiting: 5 attempts per hour per IP address. Bio-inspired adaptation monitors authentication patterns for anomaly detection."
  )

  // JSON-LD structured data for authentication page
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "LUKHAS AI ΛiD Login",
    "description": "Secure authentication for LUKHAS AI platform using passkeys and quantum-inspired identity verification",
    "provider": {
      "@type": "Organization",
      "name": "LUKHAS AI",
      "description": "Advanced AI platform with quantum-inspired consciousness and bio-inspired adaptation"
    },
    "potentialAction": {
      "@type": "AuthenticateAction",
      "name": "Login with ΛiD",
      "description": "Authenticate using WebAuthn passkeys or secure magic link"
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
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-trinity-identity text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-white z-50"
      >
        Skip to main content
      </a>
      
      {/* Header */}
      <header className="flex items-center justify-between p-6" role="banner">
        <Link href="/" className="flex items-center text-white/80 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded">
          <ChevronLeftIcon className="w-5 h-5 mr-2" aria-hidden="true" />
          Back to LUKHAS AI
        </Link>
        <div className="text-sm text-white/60">
          New to LUKHAS AI? <Link href="/signup" className="text-trinity-identity hover:text-trinity-consciousness transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-1">Create account</Link>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="flex-1 flex items-center justify-center px-6 py-12" role="main">
        <div className="w-full max-w-md">
          {/* Lambda Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-trinity-identity/20 backdrop-blur-xl border border-trinity-identity/30 mb-4">
              <span className="text-2xl font-light text-trinity-identity" aria-label="LUKHAS AI Identity">Λ</span>
            </div>
            <h1 className="text-2xl font-light text-white mb-2" id="page-title">
              Welcome back
            </h1>
            <p className="text-white/60 text-sm">
              Sign in to your ΛiD account
            </p>
            <div className="mt-2 text-xs text-white/40">
              Secured by LUKHAS AI quantum-inspired identity verification
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm" role="alert" aria-live="polite">
              <div className="flex items-start">
                <ExclamationCircleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-medium mb-1">Authentication Error</p>
                  <p>{error}</p>
                  {error.includes('Not registered') && (
                    <p className="mt-2 text-sm">
                      <Link href="/signup" className="text-red-300 hover:text-red-200 underline">
                        Create an account instead
                      </Link>
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Magic Link Success */}
          {magicLinkSent && (
            <div className="mb-6 p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm" role="alert" aria-live="polite">
              <div className="flex items-start">
                <CheckCircleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-medium mb-1">Check your email</p>
                  <p>If an account exists for <span className="font-mono">{email}</span>, we've sent you a secure sign-in link.</p>
                  <p className="mt-2 text-xs text-green-300">The link expires in 10 minutes for security.</p>
                </div>
              </div>
            </div>
          )}

          {/* Authentication Methods */}
          <div className="space-y-4">
            {/* Passkey Authentication (Primary) */}
            {passkeySupported && !showMagicLink && (
              <button
                onClick={handlePasskeyAuth}
                disabled={loading}
                className="w-full flex items-center justify-center px-6 py-4 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Log in with LUKHAS AI Identity using passkey authentication"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin" aria-hidden="true" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <KeyIcon className="w-5 h-5 mr-3" />
                    <span>Log in with ΛiD</span>
                  </>
                )}
              </button>
            )}

            {/* Fallback to Magic Link */}
            {(!passkeySupported || showMagicLink) && !magicLinkSent && (
              <form onSubmit={handleMagicLink} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
                    Email address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                    placeholder="Enter your email address"
                    disabled={loading}
                    required
                    aria-describedby="email-help"
                    autoComplete="email"
                  />
                  <div id="email-help" className="sr-only">
                    Enter the email address associated with your LUKHAS AI account
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center px-6 py-4 bg-trinity-identity hover:bg-trinity-consciousness transition-colors rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin" aria-hidden="true" />
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <EnvelopeIcon className="w-5 h-5 mr-3" />
                      <span>Send magic link</span>
                    </>
                  )}
                </button>
              </form>
            )}

            {/* Switch between methods */}
            {passkeySupported && !magicLinkSent && (
              <div className="text-center">
                <button
                  onClick={() => setShowMagicLink(!showMagicLink)}
                  className="text-sm text-white/60 hover:text-white/80 transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
                  type="button"
                >
                  {showMagicLink ? 'Use passkey instead' : 'Use email instead'}
                </button>
              </div>
            )}
          </div>

          {/* Recovery Options */}
          <div className="mt-8 text-center space-y-2">
            <Link 
              href="/recover" 
              className="block text-sm text-white/60 hover:text-white/80 transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
            >
              Lost access? Use backup codes
            </Link>
            <Link 
              href="/signup" 
              className="block text-sm text-trinity-identity hover:text-trinity-consciousness transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
            >
              Create new account
            </Link>
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
            "Passkey (WebAuthn) authentication with UV requirement",
            "Magic link email fallback with enumeration protection",
            "Device binding and session management",
            "Rate limiting and abuse protection",
            "Step-up authentication for sensitive operations"
          ]}
          limitations={[
            "Passkeys require compatible browser/device (95%+ coverage)",
            "Magic links expire after 10 minutes",
            "Rate limits apply: 5 attempts per hour per IP",
            "Session expires after 24 hours of inactivity",
            "Some features require higher tier access"
          ]}
          dependencies={[
            "WebAuthn API for passkey authentication",
            "Email service for magic link delivery",
            "LUKHAS AI identity and session infrastructure",
            "Browser local storage for session persistence"
          ]}
          dataHandling={[
            "Credentials stored securely with AES-256 encoding → GLYPH symbolic processing (for enhanced interoperability, not cryptographic security)",
            "Session data encrypted and signed with rotating keys",
            "Email addresses hashed for enumeration protection",
            "Authentication events logged for security monitoring",
            "No passwords stored or transmitted ever"
          ]}
          className="max-w-4xl mx-auto"
        />
      </div>
    </div>
    </>
  )
}