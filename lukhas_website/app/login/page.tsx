'use client'

import React, { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeftIcon, KeyIcon, EnvelopeIcon, ExclamationCircleIcon, CheckCircleIcon, LanguageIcon } from '@heroicons/react/24/outline'
import TransparencyBox from '@/components/TransparencyBox'
import { AnnouncementManager, FocusManager } from '@/lib/accessibility'

// Passkey detection and browser support
const supportsPasskeys = () => {
  if (typeof window === 'undefined') return false
  return !!(window.PublicKeyCredential && window.navigator.credentials && window.navigator.credentials.create)
}

// Bilingual auth copy with 3-layer tone
const AUTH_COPY = {
  en: {
    poetic: "A door that recognizes your hand; nothing to remember, only to be yourself.",
    technical: "Default method: passkeys (WebAuthn with user verification). Fallback: one-time magic link (10 minutes). Sessions use short-lived JWTs and rotating refresh tokens with reuse detection and device binding. Step-up is required for billing, API keys, and org admin.\nLimits: device support varies; email delivery may be delayed; password login is disabled unless explicitly enabled by an admin.\nDependencies: platform authenticators, email service, rate-limit store, and the identity service.",
    plain: "Sign in with a passkey (fingerprint, face, or device PIN). If it isn't available, we'll email a one-time link. You don't need a password. Keep your backup codes safe, and you can add more than one device."
  },
  es: {
    poetic: "Una puerta que reconoce tu mano; nada que recordar, solo ser tú.",
    technical: "Método por defecto: passkeys (WebAuthn con verificación del usuario). Alternativa: enlace de acceso por correo (10 minutos). La sesión usa JWT de corta duración y refresh tokens rotativos con detección de reutilización y vinculación al dispositivo. Se exige verificación adicional para pagos, claves de API y administración.\nLímites: el soporte de passkeys depende del dispositivo; el correo puede tardar; la contraseña está desactivada salvo que un admin la habilite.\nDependencias: autenticadores del sistema, servicio de correo, almacén de límites y servicio de identidad.",
    plain: "Entra con un passkey (huella, cara o PIN del dispositivo). Si no está disponible, te enviaremos un enlace de acceso por correo. No necesitas contraseña. Guarda tus códigos de respaldo y añade más de un dispositivo."
  }
}

// UI text translations
const UI_TEXT = {
  en: {
    backToLukhas: 'Back to LUKHAS AI',
    newToLukhas: 'New to LUKHAS AI?',
    createAccount: 'Create account',
    welcomeBack: 'Welcome back',
    signInToYourAccount: 'Sign in to your ΛiD account',
    securedBy: 'Secured by LUKHAS AI quantum-inspired identity verification',
    authError: 'Authentication Error',
    createAccountInstead: 'Create an account instead',
    checkEmail: 'Check your email',
    emailSentTo: 'If an account exists for',
    linkSent: "we've sent you a secure sign-in link.",
    linkExpires: 'The link expires in 10 minutes for security.',
    loginWithLid: 'Log in with ΛiD',
    authenticating: 'Authenticating...',
    emailAddress: 'Email address',
    enterEmail: 'Enter your email address',
    sendMagicLink: 'Send magic link',
    sending: 'Sending...',
    usePasskeyInstead: 'Use passkey instead',
    useEmailInstead: 'Use email instead',
    lostAccess: 'Lost access? Use backup codes',
    createNewAccount: 'Create new account',
    cancelledAuth: 'Authentication was cancelled or not allowed',
    noPasskeysFound: 'No registered passkeys found. Please create an account first.',
    passkeyFailed: 'Passkey authentication failed. Please try a magic link instead.',
    pleaseEnterEmail: 'Please enter your email address',
    authFailed: 'Authentication failed'
  },
  es: {
    backToLukhas: 'Volver a LUKHAS AI',
    newToLukhas: '¿Nuevo en LUKHAS AI?',
    createAccount: 'Crear cuenta',
    welcomeBack: 'Bienvenido de nuevo',
    signInToYourAccount: 'Inicia sesión en tu cuenta ΛiD',
    securedBy: 'Protegido por verificación de identidad cuántica-inspirada de LUKHAS AI',
    authError: 'Error de autenticación',
    createAccountInstead: 'Crear una cuenta en su lugar',
    checkEmail: 'Revisa tu correo',
    emailSentTo: 'Si existe una cuenta para',
    linkSent: 'te hemos enviado un enlace seguro de acceso.',
    linkExpires: 'El enlace expira en 10 minutos por seguridad.',
    loginWithLid: 'Entrar con ΛiD',
    authenticating: 'Autenticando...',
    emailAddress: 'Correo electrónico',
    enterEmail: 'Ingresa tu correo electrónico',
    sendMagicLink: 'Enviar enlace mágico',
    sending: 'Enviando...',
    usePasskeyInstead: 'Usar passkey en su lugar',
    useEmailInstead: 'Usar correo en su lugar',
    lostAccess: '¿Perdiste acceso? Usa códigos de respaldo',
    createNewAccount: 'Crear nueva cuenta',
    cancelledAuth: 'La autenticación fue cancelada o no permitida',
    noPasskeysFound: 'No se encontraron passkeys registrados. Por favor crea una cuenta primero.',
    passkeyFailed: 'La autenticación con passkey falló. Por favor intenta con un enlace mágico.',
    pleaseEnterEmail: 'Por favor ingresa tu correo electrónico',
    authFailed: 'Autenticación fallida'
  }
}

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMagicLink, setShowMagicLink] = useState(false)
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const [passkeySupported] = useState(() => supportsPasskeys())
  const [locale, setLocale] = useState<'en' | 'es'>('en')
  const [selectedTone, setSelectedTone] = useState<'poetic' | 'technical' | 'plain'>('plain')

  const t = UI_TEXT[locale]
  const copyContent = AUTH_COPY[locale]

  // Handle passkey authentication
  const handlePasskeyAuth = useCallback(async () => {
    AnnouncementManager.announceAuthState('loading', t.authenticating)
    if (!passkeySupported) {
      setError(t.passkeyFailed)
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
            const errorMsg = result.error || t.authFailed
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
        errorMsg = t.cancelledAuth
      } else if (err.name === 'InvalidStateError') {
        errorMsg = t.noPasskeysFound
        setTimeout(() => router.push('/signup'), 2000)
      } else {
        errorMsg = t.passkeyFailed
        setShowMagicLink(true)
      }
      setError(errorMsg)
      AnnouncementManager.announceAuthState('error', errorMsg)
      
      // Focus the error message for screen readers
      setTimeout(() => FocusManager.focusFirstError(), 100)
    } finally {
      setLoading(false)
    }
  }, [passkeySupported, router, t])

  // Handle magic link request
  const handleMagicLink = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    AnnouncementManager.announceAuthState('loading', t.sending)
    
    if (!email.trim()) {
      setError(t.pleaseEnterEmail)
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
      AnnouncementManager.announceAuthState('success', t.checkEmail)
    } catch (err) {
      // Still show success message for enumeration protection
      setMagicLinkSent(true)
      AnnouncementManager.announceAuthState('success', t.checkEmail)
    } finally {
      setLoading(false)
    }
  }, [email, t])

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
          {t.backToLukhas}
        </Link>
        <div className="flex items-center gap-4">
          {/* Language selector */}
          <button
            onClick={() => setLocale(locale === 'en' ? 'es' : 'en')}
            className="flex items-center text-white/60 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
            aria-label={locale === 'en' ? 'Cambiar a español' : 'Switch to English'}
          >
            <LanguageIcon className="w-4 h-4 mr-1" />
            {locale === 'en' ? 'ES' : 'EN'}
          </button>
          <div className="text-sm text-white/60">
            {t.newToLukhas} <Link href="/signup" className="text-trinity-identity hover:text-trinity-consciousness transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-1">{t.createAccount}</Link>
          </div>
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
              {t.welcomeBack}
            </h1>
            <p className="text-white/60 text-sm">
              {t.signInToYourAccount}
            </p>
            <div className="mt-2 text-xs text-white/40">
              {t.securedBy}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm" role="alert" aria-live="polite">
              <div className="flex items-start">
                <ExclamationCircleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-medium mb-1">{t.authError}</p>
                  <p>{error}</p>
                  {error.includes(t.noPasskeysFound) && (
                    <p className="mt-2 text-sm">
                      <Link href="/signup" className="text-red-300 hover:text-red-200 underline">
                        {t.createAccountInstead}
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
                  <p className="font-medium mb-1">{t.checkEmail}</p>
                  <p>{t.emailSentTo} <span className="font-mono">{email}</span>, {t.linkSent}</p>
                  <p className="mt-2 text-xs text-green-300">{t.linkExpires}</p>
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
                aria-label="Log in with Lukhas ID"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 mr-3 border-2 border-white/30 border-t-white rounded-full animate-spin" aria-hidden="true" />
                    <span>{t.authenticating}</span>
                  </>
                ) : (
                  <>
                    <KeyIcon className="w-5 h-5 mr-3" />
                    <span>{t.loginWithLid}</span>
                  </>
                )}
              </button>
            )}

            {/* Fallback to Magic Link */}
            {(!passkeySupported || showMagicLink) && !magicLinkSent && (
              <form onSubmit={handleMagicLink} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-white/80 mb-2">
                    {t.emailAddress}
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:border-transparent"
                    placeholder={t.enterEmail}
                    disabled={loading}
                    required
                    aria-describedby="email-help"
                    autoComplete="email"
                  />
                  <div id="email-help" className="sr-only">
                    {t.enterEmail}
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
                      <span>{t.sending}</span>
                    </>
                  ) : (
                    <>
                      <EnvelopeIcon className="w-5 h-5 mr-3" />
                      <span>{t.sendMagicLink}</span>
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
                  {showMagicLink ? t.usePasskeyInstead : t.useEmailInstead}
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
              {t.lostAccess}
            </Link>
            <Link 
              href="/signup" 
              className="block text-sm text-trinity-identity hover:text-trinity-consciousness transition-colors focus:outline-none focus:ring-2 focus:ring-trinity-identity focus:ring-offset-2 focus:ring-offset-bg-primary rounded px-2 py-1"
            >
              {t.createNewAccount}
            </Link>
          </div>

          {/* 3-Layer Tone Content */}
          <div className="mt-8 p-4 rounded-lg bg-black/20 backdrop-blur-xl border border-white/10">
            {/* Tone Selector */}
            <div className="flex justify-center gap-2 mb-4">
              {(['poetic', 'technical', 'plain'] as const).map((tone) => (
                <button
                  key={tone}
                  onClick={() => setSelectedTone(tone)}
                  className={`px-3 py-1 text-xs rounded transition-colors ${
                    selectedTone === tone
                      ? 'bg-trinity-identity text-white'
                      : 'bg-white/10 text-white/60 hover:bg-white/20'
                  }`}
                  aria-label={`Show ${tone} explanation`}
                >
                  {tone.charAt(0).toUpperCase() + tone.slice(1)}
                </button>
              ))}
            </div>
            
            {/* Content */}
            <div className="text-xs text-white/60 leading-relaxed" data-tone={selectedTone}>
              {copyContent[selectedTone]}
            </div>
          </div>
        </div>
      </main>

      {/* Transparency Box */}
      <div className="px-6 pb-6">
        <TransparencyBox
          locale={locale}
          capabilities={[
            locale === 'en'
              ? "Passkey (WebAuthn) authentication with UV requirement"
              : "Autenticación con passkey (WebAuthn) con requisito UV",
            locale === 'en'
              ? "Magic link email fallback with enumeration protection"
              : "Enlace mágico por correo con protección de enumeración",
            locale === 'en'
              ? "Device binding and session management"
              : "Vinculación de dispositivo y gestión de sesiones",
            locale === 'en'
              ? "Rate limiting and abuse protection"
              : "Límites de tasa y protección contra abuso",
            locale === 'en'
              ? "Step-up authentication for sensitive operations"
              : "Autenticación adicional para operaciones sensibles"
          ]}
          limitations={[
            locale === 'en'
              ? "Passkeys require compatible browser/device (95%+ coverage)"
              : "Los passkeys requieren navegador/dispositivo compatible (95%+ cobertura)",
            locale === 'en'
              ? "Magic links expire after 10 minutes"
              : "Los enlaces mágicos expiran después de 10 minutos",
            locale === 'en'
              ? "Rate limits apply: 5 attempts per hour per IP"
              : "Límites de tasa: 5 intentos por hora por IP",
            locale === 'en'
              ? "Session expires after 24 hours of inactivity"
              : "La sesión expira después de 24 horas de inactividad",
            locale === 'en'
              ? "Some features require higher tier access"
              : "Algunas funciones requieren acceso de nivel superior"
          ]}
          dependencies={[
            locale === 'en'
              ? "WebAuthn API for passkey authentication"
              : "API WebAuthn para autenticación con passkey",
            locale === 'en'
              ? "Email service for magic link delivery"
              : "Servicio de correo para entrega de enlaces mágicos",
            locale === 'en'
              ? "LUKHAS AI identity and session infrastructure"
              : "Infraestructura de identidad y sesión LUKHAS AI",
            locale === 'en'
              ? "Browser local storage for session persistence"
              : "Almacenamiento local del navegador para persistencia de sesión"
          ]}
          dataHandling={[
            locale === 'en'
              ? "Credentials stored securely with AES-256 encoding → GLYPH symbolic processing (for enhanced interoperability, not cryptographic security)"
              : "Credenciales almacenadas de forma segura con codificación AES-256 → procesamiento simbólico GLYPH (para interoperabilidad mejorada, no seguridad criptográfica)",
            locale === 'en'
              ? "Session data encrypted and signed with rotating keys"
              : "Datos de sesión cifrados y firmados con claves rotativas",
            locale === 'en'
              ? "Email addresses hashed for enumeration protection"
              : "Direcciones de correo hasheadas para protección de enumeración",
            locale === 'en'
              ? "Authentication events logged for security monitoring"
              : "Eventos de autenticación registrados para monitoreo de seguridad",
            locale === 'en'
              ? "No passwords stored or transmitted ever"
              : "No se almacenan ni transmiten contraseñas nunca"
          ]}
          className="max-w-4xl mx-auto"
        />
      </div>
    </div>
    </>
  )
}