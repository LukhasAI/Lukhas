import React from 'react'

/**
 * LUKHAS AI Login Copy Components
 * Bilingual (EN/ES) with 3-layer tone system
 */

export function LoginCopyEN() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        A door that recognizes your hand; nothing to remember, only to be yourself.
        Your consciousness awaits, secured by quantum-inspired identity.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Auth Methods:</strong> WebAuthn passkey (primary) → Magic link fallback (10-min TTL)
        </p>
        <p className="mb-2">
          <strong>Limits:</strong> 5 attempts/hour, device binding required, step-up for sensitive ops
        </p>
        <p>
          <strong>Dependencies:</strong> Platform authenticator, email service, rate-limit store, identity service
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Sign in with a passkey (fingerprint, face, or device PIN). If unavailable,
        we'll email a one-time link. No passwords. Add multiple devices for backup access.
      </div>
    </div>
  )
}

export function LoginCopyES() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Una puerta que reconoce tu mano; nada que recordar, solo ser tú.
        Tu consciencia espera, asegurada por identidad cuántica-inspirada.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Métodos Auth:</strong> Passkey WebAuthn (principal) → Enlace mágico respaldo (TTL 10-min)
        </p>
        <p className="mb-2">
          <strong>Límites:</strong> 5 intentos/hora, vinculación dispositivo, verificación extra ops sensibles
        </p>
        <p>
          <strong>Dependencias:</strong> Autenticador plataforma, servicio email, almacén límites, servicio identidad
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Entra con un passkey (huella, cara o PIN del dispositivo). Si no está disponible,
        te enviamos un enlace por correo. Sin contraseñas. Añade varios dispositivos para respaldo.
      </div>
    </div>
  )
}

// Combined component with language selector
export function LoginCopy({ language = 'en' }: { language?: 'en' | 'es' }) {
  return language === 'es' ? <LoginCopyES /> : <LoginCopyEN />
}

// Individual tone components for selective rendering
export function LoginPoetic({ language = 'en' }: { language?: 'en' | 'es' }) {
  const content = {
    en: "A door that recognizes your hand; nothing to remember, only to be yourself. Your consciousness awaits, secured by quantum-inspired identity.",
    es: "Una puerta que reconoce tu mano; nada que recordar, solo ser tú. Tu consciencia espera, asegurada por identidad cuántica-inspirada."
  }
  return (
    <p className="text-sm text-white/60 leading-relaxed" data-tone="poetic">
      {content[language]}
    </p>
  )
}

export function LoginTechnical({ language = 'en' }: { language?: 'en' | 'es' }) {
  const content = {
    en: {
      methods: "Auth Methods: WebAuthn passkey (primary) → Magic link fallback (10-min TTL)",
      limits: "Limits: 5 attempts/hour, device binding required, step-up for sensitive ops",
      deps: "Dependencies: Platform authenticator, email service, rate-limit store, identity service"
    },
    es: {
      methods: "Métodos Auth: Passkey WebAuthn (principal) → Enlace mágico respaldo (TTL 10-min)",
      limits: "Límites: 5 intentos/hora, vinculación dispositivo, verificación extra ops sensibles",
      deps: "Dependencias: Autenticador plataforma, servicio email, almacén límites, servicio identidad"
    }
  }
  const t = content[language]
  return (
    <div className="text-xs text-white/50 font-mono leading-relaxed space-y-1" data-tone="technical">
      <p>{t.methods}</p>
      <p>{t.limits}</p>
      <p>{t.deps}</p>
    </div>
  )
}

export function LoginPlain({ language = 'en' }: { language?: 'en' | 'es' }) {
  const content = {
    en: "Sign in with a passkey (fingerprint, face, or device PIN). If unavailable, we'll email a one-time link. No passwords. Add multiple devices for backup access.",
    es: "Entra con un passkey (huella, cara o PIN del dispositivo). Si no está disponible, te enviamos un enlace por correo. Sin contraseñas. Añade varios dispositivos para respaldo."
  }
  return (
    <p className="text-sm text-white/70 leading-relaxed" data-tone="plain">
      {content[language]}
    </p>
  )
}
