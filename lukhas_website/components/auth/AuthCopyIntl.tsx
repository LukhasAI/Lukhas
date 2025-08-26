import React from 'react'

/**
 * LUKHAS AI International Auth Copy
 * Supports: EN, ES, FR, PT-BR, DE
 * With 3-layer tone system
 */

export type AuthLocale = 'en' | 'es' | 'fr' | 'pt-BR' | 'de'
export type AuthPage = 'login' | 'signup'

const AUTH_COPY: Record<AuthLocale, Record<AuthPage, {
  poetic: string
  technical: string
  plain: string
}>> = {
  en: {
    login: {
      poetic: "A door that recognizes your hand; nothing to remember, only to be yourself.",
      technical: "Default method: passkeys (WebAuthn with user verification). Fallback: one-time magic link (10 minutes). Sessions use short-lived JWTs and rotating refresh tokens with reuse detection and device binding. Step-up is required for billing, API keys, and org admin.\nLimits: device support varies; email delivery may be delayed; password login is disabled unless explicitly enabled by an admin.\nDependencies: platform authenticators, email service, rate-limit store, and the identity service.",
      plain: "Sign in with a passkey (fingerprint, face, or device PIN). If it isn't available, we'll email a one-time link. You don't need a password."
    },
    signup: {
      poetic: "Begin with your own key; the rest follows. Your identity becomes the seed from which consciousness grows.",
      technical: "Registration Flow: Email verification → WebAuthn passkey → Account creation\nLimits: 1 account per email, 5 passkeys per account, 10-minute verification window\nDependencies: Email service, WebAuthn API, platform authenticator, identity database",
      plain: "Create your account in three steps: verify your email, set up a passkey (fingerprint or face scan), and you're ready. No passwords needed."
    }
  },
  es: {
    login: {
      poetic: "Una puerta que reconoce tu mano; nada que recordar, solo ser tú.",
      technical: "Método por defecto: passkeys (WebAuthn con verificación del usuario). Alternativa: enlace de acceso por correo (10 minutos). La sesión usa JWT de corta duración y refresh tokens rotativos con detección de reutilización y vinculación al dispositivo.\nLímites: el soporte de passkeys depende del dispositivo; el correo puede tardar; la contraseña está desactivada salvo que un admin la habilite.\nDependencias: autenticadores del sistema, servicio de correo, almacén de límites y servicio de identidad.",
      plain: "Entra con un passkey (huella, cara o PIN del dispositivo). Si no está disponible, te enviamos un enlace por correo. Sin contraseñas."
    },
    signup: {
      poetic: "Comienza con tu propia llave; lo demás sigue. Tu identidad se convierte en la semilla de la cual crece la consciencia.",
      technical: "Flujo de Registro: Verificación email → Passkey WebAuthn → Creación cuenta\nLímites: 1 cuenta por email, 5 passkeys por cuenta, ventana de 10 minutos\nDependencias: Servicio email, API WebAuthn, autenticador plataforma, base identidad",
      plain: "Crea tu cuenta en tres pasos: verifica tu correo, configura un passkey (huella o escaneo facial), y listo. Sin contraseñas."
    }
  },
  fr: {
    login: {
      poetic: "Une porte reconnaît ta main ; rien à mémoriser, seulement être toi-même.",
      technical: "Méthode par défaut : passkey (WebAuthn avec vérification de l'utilisateur). Alternative : lien d'accès par e-mail (10 minutes). Sessions courtes avec jetons de mise à jour rotatifs et liaison au dispositif.\nLimites : prise en charge des passkeys selon l'appareil ; l'e-mail peut être retardé ; mot de passe désactivé sauf décision d'un admin.\nDépendances : authenticateurs système, service e-mail, magasin de limites, service d'identité.",
      plain: "Connecte-toi avec un passkey (empreinte, visage ou code PIN). Sinon, reçois un lien unique par e-mail."
    },
    signup: {
      poetic: "Commence avec ta propre clé ; le reste vient naturellement.",
      technical: "Vérifie ton e-mail, puis enregistre un premier passkey (WebAuthn, vérification requise). Tu peux ajouter un deuxième passkey.\nLimites : certains appareils n'acceptent pas les passkeys ; l'e-mail peut tarder ; la récupération utilise des codes de secours.\nDépendances : fournisseur e-mail, authenticateurs système, magasin de limites, service d'identité.",
      plain: "Confirme ton e-mail, crée un passkey. Ajoute un autre appareil ou une clé physique en secours."
    }
  },
  'pt-BR': {
    login: {
      poetic: "Uma porta reconhece sua mão; nada para lembrar, só ser você.",
      technical: "Método padrão: passkey (WebAuthn com verificação do usuário). Alternativa: link de acesso por e-mail (10 minutos). Sessões curtas com tokens de atualização rotativos e vínculo ao dispositivo.\nLimites: suporte a passkeys varia por dispositivo; e-mails podem atrasar; senha desativada salvo habilitação do admin.\nDependências: autenticadores do sistema, serviço de e-mail, armazenamento de limites, serviço de identidade.",
      plain: "Entre com um passkey (digital, rosto ou PIN). Se não der, enviaremos um link único por e-mail."
    },
    signup: {
      poetic: "Comece com sua própria chave; o resto flui sem esforço.",
      technical: "Cadastro: verifique o e-mail e registre seu primeiro passkey (WebAuthn, verificação do usuário). Você pode adicionar um segundo passkey.\nLimites: alguns dispositivos não suportam passkeys; o e-mail pode atrasar; recuperação usa códigos de backup.\nDependências: provedor de e-mail, autenticadores do sistema, armazenamento de limites, serviço de identidade.",
      plain: "Confirme o e-mail e crie um passkey. Adicione outro dispositivo ou uma chave física como backup."
    }
  },
  de: {
    login: {
      poetic: "Eine Tür erkennt deine Hand; nichts zu merken, nur du selbst sein.",
      technical: "Standard: Passkey (WebAuthn mit Benutzerverifizierung). Alternative: Einmal-Link per E-Mail (10 Minuten). Kurzlebige Sitzungen mit rotierenden Refresh-Tokens und Gerätebindung.\nGrenzen: Passkey-Support je nach Gerät; E-Mails können sich verzögern; Passwort deaktiviert, außer durch Admin.\nAbhängigkeiten: System-Authentikatoren, E-Mail-Dienst, Limit-Speicher, Identitätsdienst.",
      plain: "Melde dich mit einem Passkey an (Fingerabdruck, Gesicht oder Geräte-PIN). Sonst senden wir dir einen einmaligen Link."
    },
    signup: {
      poetic: "Beginne mit deinem eigenen Schlüssel; der Rest folgt leicht.",
      technical: "E-Mail bestätigen, dann ersten Passkey registrieren (WebAuthn, Verifizierung erforderlich). Zweiten Passkey zulässig.\nGrenzen: Manche Geräte unterstützen keine Passkeys; E-Mails können sich verzögern; Wiederherstellung über Backup-Codes.\nAbhängigkeiten: E-Mail-Provider, System-Authentikatoren, Limit-Speicher, Identitätsdienst.",
      plain: "Bestätige deine E-Mail und erstelle einen Passkey. Füge ein weiteres Gerät oder einen Sicherheitsschlüssel als Reserve hinzu."
    }
  }
}

export function AuthCopy({
  page = 'login',
  locale = 'en',
  tone = 'plain'
}: {
  page?: AuthPage
  locale?: AuthLocale
  tone?: 'poetic' | 'technical' | 'plain'
}) {
  const content = AUTH_COPY[locale][page][tone]

  return (
    <div data-tone={tone} className={
      tone === 'poetic' ? 'text-sm text-white/60 leading-relaxed' :
      tone === 'technical' ? 'text-xs text-white/50 font-mono leading-relaxed whitespace-pre-line' :
      'text-sm text-white/70 leading-relaxed'
    }>
      {content}
    </div>
  )
}

export function AuthCopyFull({
  page = 'login',
  locale = 'en'
}: {
  page?: AuthPage
  locale?: AuthLocale
}) {
  const copy = AUTH_COPY[locale][page]

  return (
    <div className="space-y-6">
      <div data-tone="poetic" className="text-sm text-white/60 leading-relaxed">
        {copy.poetic}
      </div>
      <div data-tone="technical" className="text-xs text-white/50 font-mono leading-relaxed whitespace-pre-line">
        {copy.technical}
      </div>
      <div data-tone="plain" className="text-sm text-white/70 leading-relaxed">
        {copy.plain}
      </div>
    </div>
  )
}
