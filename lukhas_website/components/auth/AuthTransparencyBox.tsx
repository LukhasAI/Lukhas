/**
 * Auth-specific TransparencyBox with biometric and adaptive MFA disclosures
 * As per GPT5 recommendations - clearly states no biometric data leaves device
 */

import React from 'react'
import { TransparencyBox, Locale } from '../TransparencyBox'

interface AuthTransparencyBoxProps {
  locale?: Locale
  showBiometrics?: boolean
  showAdaptiveMFA?: boolean
  showSPC?: boolean
  className?: string
}

export function AuthTransparencyBox({
  locale = 'en',
  showBiometrics = true,
  showAdaptiveMFA = true,
  showSPC = false,
  className = ''
}: AuthTransparencyBoxProps) {
  // Build capabilities based on features
  const capabilities = locale === 'en' ? [
    ...(showBiometrics ? [
      "Device biometrics via your OS (Face ID, Touch ID, Windows Hello)",
      "WebAuthn passkeys with platform authenticators",
      "Cryptographic proof without biometric data transmission"
    ] : []),
    ...(showAdaptiveMFA ? [
      "Risk-adaptive multi-factor authentication",
      "Challenge types vary with context to protect you",
      "Accessible emoji and word-based challenges"
    ] : []),
    ...(showSPC ? [
      "Secure Payment Confirmation for high-value transactions",
      "Transaction-bound cryptographic approval"
    ] : [])
  ] : [
    ...(showBiometrics ? [
      "Biometría del dispositivo a través de tu SO (Face ID, Touch ID, Windows Hello)",
      "Passkeys WebAuthn con autenticadores de plataforma",
      "Prueba criptográfica sin transmisión de datos biométricos"
    ] : []),
    ...(showAdaptiveMFA ? [
      "Autenticación multifactor adaptativa al riesgo",
      "Los tipos de desafío varían según el contexto para protegerte",
      "Desafíos accesibles basados en emojis y palabras"
    ] : []),
    ...(showSPC ? [
      "Confirmación de Pago Seguro para transacciones de alto valor",
      "Aprobación criptográfica vinculada a la transacción"
    ] : [])
  ]

  const limitations = locale === 'en' ? [
    "Biometric authentication requires device support",
    "Some features require modern browsers (Chrome 109+, Safari 16+)",
    "Adaptive challenges add friction for high-risk scenarios",
    ...(showSPC ? ["SPC currently supported in Chrome/Edge, fallback for others"] : [])
  ] : [
    "La autenticación biométrica requiere soporte del dispositivo",
    "Algunas funciones requieren navegadores modernos (Chrome 109+, Safari 16+)",
    "Los desafíos adaptativos agregan fricción en escenarios de alto riesgo",
    ...(showSPC ? ["SPC actualmente compatible con Chrome/Edge, alternativa para otros"] : [])
  ]

  const dependencies = locale === 'en' ? [
    "Platform biometric APIs (never direct biometric access)",
    "WebAuthn/FIDO2 standards",
    "Redis for challenge state management",
    "Device secure element for key storage"
  ] : [
    "APIs biométricas de la plataforma (nunca acceso biométrico directo)",
    "Estándares WebAuthn/FIDO2",
    "Redis para gestión del estado de desafíos",
    "Elemento seguro del dispositivo para almacenamiento de claves"
  ]

  const dataHandling = locale === 'en' ? [
    "We never receive your biometric data—only a cryptographic proof",
    "Authentication events logged without personal identifiers",
    "Challenge responses validated server-side then immediately deleted",
    "Step-up tokens expire after 5 minutes of single use"
  ] : [
    "Nunca recibimos tus datos biométricos—solo una prueba criptográfica",
    "Eventos de autenticación registrados sin identificadores personales",
    "Respuestas de desafío validadas en el servidor y eliminadas inmediatamente",
    "Los tokens de verificación adicional expiran después de 5 minutos de uso único"
  ]

  // Special biometric disclosure box
  const BiometricDisclosure = () => (
    <div className="mt-4 p-3 bg-trinity-identity/10 border border-trinity-identity/20 rounded-lg">
      <div className="flex items-start gap-2">
        <svg className="w-5 h-5 text-trinity-identity mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <div className="text-sm text-white/80">
          <strong className="text-white/90">
            {locale === 'en' ? 'Biometric Privacy:' : 'Privacidad Biométrica:'}
          </strong>
          <span className="ml-1">
            {locale === 'en'
              ? "This site uses device biometrics via your OS (Face ID, Touch ID, Windows Hello). We never receive your biometric data—only a cryptographic proof."
              : "Este sitio utiliza biometría del dispositivo a través de tu SO (Face ID, Touch ID, Windows Hello). Nunca recibimos tus datos biométricos—solo una prueba criptográfica."}
          </span>
        </div>
      </div>
    </div>
  )

  return (
    <>
      <TransparencyBox
        title={locale === 'en' ? 'Authentication Transparency' : 'Transparencia de Autenticación'}
        capabilities={capabilities}
        limitations={limitations}
        dependencies={dependencies}
        dataHandling={dataHandling}
        locale={locale}
        className={className}
      />
      {showBiometrics && <BiometricDisclosure />}
    </>
  )
}

export default AuthTransparencyBox
