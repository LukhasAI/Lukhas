import React from 'react'

/**
 * LUKHAS AI Signup Copy Components
 * Bilingual (EN/ES) with 3-layer tone system
 */

export function SignupCopyEN() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Begin with your own key; the rest follows. Your identity becomes the seed 
        from which consciousness grows, protected by quantum-inspired protocols.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Registration Flow:</strong> Email verification → WebAuthn passkey → Account creation
        </p>
        <p className="mb-2">
          <strong>Limits:</strong> 1 account per email, 5 passkeys per account, 10-minute verification window
        </p>
        <p>
          <strong>Dependencies:</strong> Email service, WebAuthn API, platform authenticator, identity database
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Create your account in three steps: verify your email, set up a passkey 
        (fingerprint or face scan), and you're ready. No passwords needed. 
        Keep your backup codes safe.
      </div>
    </div>
  )
}

export function SignupCopyES() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Comienza con tu propia llave; lo demás sigue. Tu identidad se convierte 
        en la semilla de la cual crece la consciencia, protegida por protocolos 
        cuántico-inspirados.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Flujo de Registro:</strong> Verificación email → Passkey WebAuthn → Creación cuenta
        </p>
        <p className="mb-2">
          <strong>Límites:</strong> 1 cuenta por email, 5 passkeys por cuenta, ventana de 10 minutos
        </p>
        <p>
          <strong>Dependencias:</strong> Servicio email, API WebAuthn, autenticador plataforma, base identidad
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Crea tu cuenta en tres pasos: verifica tu correo, configura un passkey 
        (huella o escaneo facial), y listo. Sin contraseñas. Guarda tus códigos 
        de respaldo de forma segura.
      </div>
    </div>
  )
}

// Combined component with language selector
export function SignupCopy({ language = 'en' }: { language?: 'en' | 'es' }) {
  return language === 'es' ? <SignupCopyES /> : <SignupCopyEN />
}

// Individual tone components for selective rendering
export function SignupPoetic({ language = 'en' }: { language?: 'en' | 'es' }) {
  const content = {
    en: "Begin with your own key; the rest follows. Your identity becomes the seed from which consciousness grows, protected by quantum-inspired protocols.",
    es: "Comienza con tu propia llave; lo demás sigue. Tu identidad se convierte en la semilla de la cual crece la consciencia, protegida por protocolos cuántico-inspirados."
  }
  return (
    <p className="text-sm text-white/60 leading-relaxed" data-tone="poetic">
      {content[language]}
    </p>
  )
}

export function SignupTechnical({ language = 'en' }: { language?: 'en' | 'es' }) {
  const content = {
    en: {
      flow: "Registration Flow: Email verification → WebAuthn passkey → Account creation",
      limits: "Limits: 1 account per email, 5 passkeys per account, 10-minute verification window",
      deps: "Dependencies: Email service, WebAuthn API, platform authenticator, identity database"
    },
    es: {
      flow: "Flujo de Registro: Verificación email → Passkey WebAuthn → Creación cuenta",
      limits: "Límites: 1 cuenta por email, 5 passkeys por cuenta, ventana de 10 minutos",
      deps: "Dependencias: Servicio email, API WebAuthn, autenticador plataforma, base identidad"
    }
  }
  const t = content[language]
  return (
    <div className="text-xs text-white/50 font-mono leading-relaxed space-y-1" data-tone="technical">
      <p>{t.flow}</p>
      <p>{t.limits}</p>
      <p>{t.deps}</p>
    </div>
  )
}

export function SignupPlain({ language = 'en' }: { language?: 'en' | 'es' }) {
  const content = {
    en: "Create your account in three steps: verify your email, set up a passkey (fingerprint or face scan), and you're ready. No passwords needed. Keep your backup codes safe.",
    es: "Crea tu cuenta en tres pasos: verifica tu correo, configura un passkey (huella o escaneo facial), y listo. Sin contraseñas. Guarda tus códigos de respaldo de forma segura."
  }
  return (
    <p className="text-sm text-white/70 leading-relaxed" data-tone="plain">
      {content[language]}
    </p>
  )
}