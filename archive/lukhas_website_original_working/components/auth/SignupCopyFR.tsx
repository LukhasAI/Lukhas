import React from 'react'

/**
 * LUKHAS AI Signup Copy - French/Portuguese/German
 * With 3-layer tone system
 */

export function SignupCopyFR() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Commence avec ta propre clé ; le reste vient naturellement.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Processus :</strong> Vérifie ton e-mail, puis enregistre un premier passkey (WebAuthn, vérification requise). Tu peux ajouter un deuxième passkey (autre appareil ou clé de sécurité). Mot de passe masqué par défaut.
        </p>
        <p className="mb-2">
          <strong>Limites :</strong> certains appareils n'acceptent pas les passkeys ; l'e-mail peut tarder ; la récupération utilise des codes de secours ou d'autres passkeys.
        </p>
        <p>
          <strong>Dépendances :</strong> fournisseur e-mail, authenticateurs système, magasin de limites, service d'identité.
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Confirme ton e-mail, crée un passkey. Ajoute un autre appareil ou une clé physique en secours.
      </div>
    </div>
  )
}

export function SignupCopyPTBR() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Comece com sua própria chave; o resto flui sem esforço.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Cadastro:</strong> verifique o e-mail e registre seu primeiro passkey (WebAuthn, verificação do usuário). Você pode adicionar um segundo passkey (outro dispositivo ou chave física). Senha oculta por padrão.
        </p>
        <p className="mb-2">
          <strong>Limites:</strong> alguns dispositivos não suportam passkeys; o e-mail pode atrasar; recuperação usa códigos de backup ou passkeys extras.
        </p>
        <p>
          <strong>Dependências:</strong> provedor de e-mail, autenticadores do sistema, armazenamento de limites, serviço de identidade.
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Confirme o e-mail e crie um passkey. Adicione outro dispositivo ou uma chave física como backup.
      </div>
    </div>
  )
}

export function SignupCopyDE() {
  return (
    <div className="space-y-6">
      {/* Poetic Layer */}
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        Beginne mit deinem eigenen Schlüssel; der Rest folgt leicht.
      </div>

      {/* Technical Layer */}
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed">
        <p className="mb-2">
          <strong>Ablauf:</strong> E-Mail bestätigen, dann ersten Passkey registrieren (WebAuthn, Verifizierung erforderlich). Zweiten Passkey zulässig (weiteres Gerät oder Sicherheitsschlüssel). Passwort standardmäßig verborgen.
        </p>
        <p className="mb-2">
          <strong>Grenzen:</strong> Manche Geräte unterstützen keine Passkeys; E-Mails können sich verzögern; Wiederherstellung über Backup-Codes oder zusätzliche Passkeys.
        </p>
        <p>
          <strong>Abhängigkeiten:</strong> E-Mail-Provider, System-Authentikatoren, Limit-Speicher, Identitätsdienst.
        </p>
      </div>

      {/* Plain Layer */}
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        Bestätige deine E-Mail und erstelle einen Passkey. Füge ein weiteres Gerät oder einen Sicherheitsschlüssel als Reserve hinzu.
      </div>
    </div>
  )
}

// Combined multi-language component
export function SignupCopyIntl({ language = 'fr' }: { language?: 'fr' | 'pt-BR' | 'de' }) {
  switch (language) {
    case 'pt-BR':
      return <SignupCopyPTBR />
    case 'de':
      return <SignupCopyDE />
    default:
      return <SignupCopyFR />
  }
}