import React from 'react'

/**
 * LUKHAS AI Login Copy - French (FR)
 * With 3-layer tone system
 */

export function LoginCopyFR() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Une porte reconnaît ta main ; rien à mémoriser, seulement être toi-même.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Méthode par défaut :</strong> passkey (WebAuthn avec vérification de l'utilisateur).
        </p>
        <p className="mb-2">
          <strong>Alternative :</strong> lien d'accès par e-mail (10 minutes). Sessions courtes avec jetons de mise à jour rotatifs et liaison au dispositif. Vérification renforcée requise pour facturation, clés API et administration.
        </p>
        <p className="mb-2">
          <strong>Limites :</strong> prise en charge des passkeys selon l'appareil ; l'e-mail peut être retardé ; mot de passe désactivé sauf décision d'un admin.
        </p>
        <p>
          <strong>Dépendances :</strong> authenticateurs système, service e-mail, magasin de limites, service d'identité.
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Connecte-toi avec un passkey (empreinte, visage ou code PIN). Sinon, reçois un lien unique par e-mail.
      </div>
    </div>
  )
}

export function LoginCopyPTBR() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Uma porta reconhece sua mão; nada para lembrar, só ser você.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Método padrão:</strong> passkey (WebAuthn com verificação do usuário).
        </p>
        <p className="mb-2">
          <strong>Alternativa:</strong> link de acesso por e-mail (10 minutos). Sessões curtas com tokens de atualização rotativos e vínculo ao dispositivo. Verificação extra exigida para cobrança, chaves de API e administração.
        </p>
        <p className="mb-2">
          <strong>Limites:</strong> suporte a passkeys varia por dispositivo; e-mails podem atrasar; senha desativada salvo habilitação do admin.
        </p>
        <p>
          <strong>Dependências:</strong> autenticadores do sistema, serviço de e-mail, armazenamento de limites, serviço de identidade.
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Entre com um passkey (digital, rosto ou PIN). Se não der, enviaremos um link único por e-mail.
      </div>
    </div>
  )
}

export function LoginCopyDE() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Eine Tür erkennt deine Hand; nichts zu merken, nur du selbst sein.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Standard:</strong> Passkey (WebAuthn mit Benutzerverifizierung).
        </p>
        <p className="mb-2">
          <strong>Alternative:</strong> Einmal-Link per E-Mail (10 Minuten). Kurzlebige Sitzungen mit rotierenden Refresh-Tokens und Gerätebindung. Stärkere Verifizierung für Abrechnung, API-Schlüssel und Admin-Aktionen.
        </p>
        <p className="mb-2">
          <strong>Grenzen:</strong> Passkey-Support je nach Gerät; E-Mails können sich verzögern; Passwort deaktiviert, außer durch Admin.
        </p>
        <p>
          <strong>Abhängigkeiten:</strong> System-Authentikatoren, E-Mail-Dienst, Limit-Speicher, Identitätsdienst.
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Melde dich mit einem Passkey an (Fingerabdruck, Gesicht oder Geräte-PIN). Sonst senden wir dir einen einmaligen Link.
      </div>
    </div>
  )
}

// Combined multi-language component
export function LoginCopyIntl({ language = 'fr' }: { language?: 'fr' | 'pt-BR' | 'de' }) {
  switch (language) {
    case 'pt-BR':
      return <LoginCopyPTBR />
    case 'de':
      return <LoginCopyDE />
    default:
      return <LoginCopyFR />
  }
}