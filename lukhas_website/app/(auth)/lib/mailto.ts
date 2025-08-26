/**
 * LUKHAS AI - Support Email Generator
 *
 * Mailto utility for prefilled support emails with structured data collection,
 * browser fingerprinting for diagnostics, and proper URL encoding.
 */

// Types for browser information collection
interface BrowserInfo {
  browser: string;
  version: string;
  os: string;
  osVersion: string;
  device: string;
  language: string;
  timezone: string;
  screen: string;
  viewport: string;
  userAgent: string;
  cookiesEnabled: boolean;
  javaEnabled: boolean;
  onlineStatus: boolean;
  connectionType?: string;
  timestamp: string;
}

// Types for support email context
interface SupportContext {
  email: string;
  purpose: string;
  userTier?: string;
  realm?: string;
  zone?: string;
  userAlias?: string;
  senderDomain: string;
  timestamp: string;
  [key: string]: any;
}

// Types for email template data
interface EmailTemplateData {
  subject: string;
  body: string;
  context: SupportContext;
  browserInfo: BrowserInfo;
  locale: string;
}

/**
 * Collect comprehensive browser information for support diagnostics
 */
export function collectBrowserInfo(): BrowserInfo {
  const nav = navigator;
  const screen = window.screen;
  const now = new Date();

  // Parse user agent for browser detection
  const userAgent = nav.userAgent;
  const browserInfo = {
    browser: 'Unknown',
    version: 'Unknown',
    os: 'Unknown',
    osVersion: 'Unknown'
  };

  // Browser detection
  if (userAgent.includes('Chrome')) {
    browserInfo.browser = 'Chrome';
    const match = userAgent.match(/Chrome\/([0-9.]+)/);
    browserInfo.version = match ? match[1] : 'Unknown';
  } else if (userAgent.includes('Firefox')) {
    browserInfo.browser = 'Firefox';
    const match = userAgent.match(/Firefox\/([0-9.]+)/);
    browserInfo.version = match ? match[1] : 'Unknown';
  } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
    browserInfo.browser = 'Safari';
    const match = userAgent.match(/Version\/([0-9.]+)/);
    browserInfo.version = match ? match[1] : 'Unknown';
  } else if (userAgent.includes('Edge')) {
    browserInfo.browser = 'Edge';
    const match = userAgent.match(/Edge\/([0-9.]+)/);
    browserInfo.version = match ? match[1] : 'Unknown';
  }

  // OS detection
  if (userAgent.includes('Windows NT')) {
    browserInfo.os = 'Windows';
    const match = userAgent.match(/Windows NT ([0-9.]+)/);
    browserInfo.osVersion = match ? match[1] : 'Unknown';
  } else if (userAgent.includes('Mac OS X')) {
    browserInfo.os = 'macOS';
    const match = userAgent.match(/Mac OS X ([0-9_]+)/);
    browserInfo.osVersion = match ? match[1].replace(/_/g, '.') : 'Unknown';
  } else if (userAgent.includes('Linux')) {
    browserInfo.os = 'Linux';
  } else if (userAgent.includes('Android')) {
    browserInfo.os = 'Android';
    const match = userAgent.match(/Android ([0-9.]+)/);
    browserInfo.osVersion = match ? match[1] : 'Unknown';
  } else if (userAgent.includes('iOS')) {
    browserInfo.os = 'iOS';
    const match = userAgent.match(/OS ([0-9_]+)/);
    browserInfo.osVersion = match ? match[1].replace(/_/g, '.') : 'Unknown';
  }

  // Device detection
  let device = 'Desktop';
  if (userAgent.includes('Mobile')) {
    device = 'Mobile';
  } else if (userAgent.includes('Tablet') || userAgent.includes('iPad')) {
    device = 'Tablet';
  }

  // Connection type (if supported)
  let connectionType: string | undefined;
  if ('connection' in nav) {
    const connection = (nav as any).connection;
    connectionType = connection?.effectiveType || connection?.type;
  }

  return {
    browser: browserInfo.browser,
    version: browserInfo.version,
    os: browserInfo.os,
    osVersion: browserInfo.osVersion,
    device,
    language: nav.language || 'en-US',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Unknown',
    screen: `${screen.width}x${screen.height}`,
    viewport: `${window.innerWidth}x${window.innerHeight}`,
    userAgent: userAgent,
    cookiesEnabled: nav.cookieEnabled,
    javaEnabled: nav.javaEnabled?.() || false,
    onlineStatus: nav.onLine,
    connectionType,
    timestamp: now.toISOString()
  };
}

/**
 * Generate structured diagnostic information
 */
function generateDiagnosticInfo(context: SupportContext, browserInfo: BrowserInfo): string {
  const sections = [
    '--- AUTHENTICATION CONTEXT ---',
    `Email: ${context.email}`,
    `Purpose: ${context.purpose}`,
    `Tier: ${context.userTier || 'Not specified'}`,
    `Realm: ${context.realm || 'Default'}`,
    `Zone: ${context.zone || 'Default'}`,
    `User Alias: ${context.userAlias || 'Not specified'}`,
    `Sender Domain: ${context.senderDomain}`,
    `Timestamp: ${context.timestamp}`,
    '',
    '--- BROWSER ENVIRONMENT ---',
    `Browser: ${browserInfo.browser} ${browserInfo.version}`,
    `OS: ${browserInfo.os} ${browserInfo.osVersion}`,
    `Device: ${browserInfo.device}`,
    `Language: ${browserInfo.language}`,
    `Timezone: ${browserInfo.timezone}`,
    `Screen: ${browserInfo.screen}`,
    `Viewport: ${browserInfo.viewport}`,
    `Online: ${browserInfo.onlineStatus}`,
    `Cookies: ${browserInfo.cookiesEnabled}`,
    `Java: ${browserInfo.javaEnabled}`,
    browserInfo.connectionType ? `Connection: ${browserInfo.connectionType}` : '',
    '',
    '--- TECHNICAL DETAILS ---',
    `User Agent: ${browserInfo.userAgent}`,
    `Session Timestamp: ${browserInfo.timestamp}`
  ].filter(Boolean);

  return sections.join('\n');
}

/**
 * Generate email body with template and diagnostic information
 */
function generateEmailBody(
  template: string,
  context: SupportContext,
  browserInfo: BrowserInfo,
  locale: string
): string {
  const diagnosticInfo = generateDiagnosticInfo(context, browserInfo);

  // Replace template variables
  let body = template;

  // Basic template variables
  body = body.replace(/{email}/g, context.email);
  body = body.replace(/{purpose}/g, context.purpose);
  body = body.replace(/{userTier}/g, context.userTier || 'Not specified');
  body = body.replace(/{realm}/g, context.realm || 'Default');
  body = body.replace(/{zone}/g, context.zone || 'Default');
  body = body.replace(/{userAlias}/g, context.userAlias || 'Not specified');
  body = body.replace(/{senderDomain}/g, context.senderDomain);
  body = body.replace(/{timestamp}/g, context.timestamp);
  body = body.replace(/{locale}/g, locale);

  // Browser info variables
  body = body.replace(/{browser}/g, `${browserInfo.browser} ${browserInfo.version}`);
  body = body.replace(/{os}/g, `${browserInfo.os} ${browserInfo.osVersion}`);
  body = body.replace(/{device}/g, browserInfo.device);
  body = body.replace(/{timezone}/g, browserInfo.timezone);

  // Add diagnostic information section
  body += '\n\n--- DIAGNOSTIC INFORMATION ---\n';
  body += '(Please include this information to help our support team assist you faster)\n\n';
  body += diagnosticInfo;

  return body;
}

/**
 * Build a properly encoded mailto URL for support emails
 */
export function buildSupportMailto({
  subject,
  body,
  context,
  browserInfo,
  locale,
  supportEmail = 'support@lukhas.ai'
}: {
  subject: string;
  body: string;
  context: SupportContext;
  browserInfo: BrowserInfo;
  locale: string;
  supportEmail?: string;
}): string {
  // Generate the complete email body
  const fullBody = generateEmailBody(body, context, browserInfo, locale);

  // URL encode the components
  const encodedSubject = encodeURIComponent(subject);
  const encodedBody = encodeURIComponent(fullBody);

  // Build the mailto URL
  const mailtoUrl = `mailto:${supportEmail}?subject=${encodedSubject}&body=${encodedBody}`;

  return mailtoUrl;
}

/**
 * Generate support email templates based on purpose and locale
 */
export function getSupportEmailTemplate(purpose: string, locale: string = 'en'): { subject: string; body: string } {
  const templates = {
    en: {
      login: {
        subject: 'Login Authentication Support - {email}',
        body: `Hello LUKHAS Support Team,

I'm having trouble with email verification during login for my account ({email}).

Issue Description:
- I'm trying to log in but haven't received the verification code
- Purpose: {purpose}
- User Tier: {userTier}
- Sender Domain: {senderDomain}

What I've already tried:
[ ] Checked spam/junk folder
[ ] Waited 5+ minutes
[ ] Searched my inbox for "{senderDomain}"
[ ] Verified my email settings

Additional Context:
{realm}.{zone} realm/zone context
Timestamp: {timestamp}
Browser: {browser}
Device: {device}
Timezone: {timezone}

Please help me resolve this authentication issue.

Best regards,
{userAlias}`
      },
      register: {
        subject: 'Registration Support - Email Verification Issue - {email}',
        body: `Hello LUKHAS Support Team,

I'm experiencing issues with email verification during account registration.

Registration Details:
- Email: {email}
- Purpose: {purpose}
- Registration Tier: {userTier}
- Timestamp: {timestamp}

The Problem:
I'm trying to complete my LUKHAS AI account registration but the verification email isn't arriving. I've checked all the usual places (spam folder, promotions tab, etc.) but can't locate the message.

Technical Context:
- Expected sender: {senderDomain}
- Browser: {browser}
- Device: {device}
- Timezone: {timezone}

Could you please help me complete my registration or resend the verification email?

Thank you for your assistance!

Best regards,
{userAlias}`
      },
      'password-reset': {
        subject: 'Password Reset Support - {email}',
        body: `Hello LUKHAS Support Team,

I need assistance with password reset email delivery.

Account Information:
- Email: {email}
- Purpose: {purpose}
- User Tier: {userTier}
- Timestamp: {timestamp}

Issue:
I requested a password reset but haven't received the reset email. I've checked:
- Primary inbox
- Spam/Junk folder
- All email folders
- Waited over 10 minutes

Technical Details:
- Expected from: {senderDomain}
- Browser: {browser}
- OS: {os}
- Device: {device}

Please help me reset my password or troubleshoot the email delivery issue.

Thank you,
{userAlias}`
      },
      default: {
        subject: 'Authentication Support Request - {email}',
        body: `Hello LUKHAS Support Team,

I need assistance with email verification for my LUKHAS AI account.

Account Details:
- Email: {email}
- Authentication Purpose: {purpose}
- User Tier: {userTier}
- Realm/Zone: {realm}.{zone}
- Timestamp: {timestamp}

Issue Description:
I'm not receiving verification emails from {senderDomain}. I've tried the standard troubleshooting steps without success.

Environment:
- Browser: {browser}
- Device: {device}
- Timezone: {timezone}

Please assist me with this authentication issue.

Best regards,
{userAlias}`
      }
    },
    es: {
      login: {
        subject: 'Soporte de Autenticación - Inicio de Sesión - {email}',
        body: `Hola Equipo de Soporte de LUKHAS,

Tengo problemas con la verificación de email durante el inicio de sesión para mi cuenta ({email}).

Descripción del Problema:
- Estoy intentando iniciar sesión pero no he recibido el código de verificación
- Propósito: {purpose}
- Nivel de Usuario: {userTier}
- Dominio Remitente: {senderDomain}

Lo que ya he intentado:
[ ] Revisé la carpeta de spam/correo no deseado
[ ] Esperé más de 5 minutos
[ ] Busqué en mi bandeja de entrada por "{senderDomain}"
[ ] Verifiqué la configuración de mi email

Contexto Adicional:
Contexto de realm/zone {realm}.{zone}
Timestamp: {timestamp}
Navegador: {browser}
Dispositivo: {device}
Zona horaria: {timezone}

Por favor ayúdenme a resolver este problema de autenticación.

Saludos cordiales,
{userAlias}`
      },
      register: {
        subject: 'Soporte de Registro - Problema de Verificación de Email - {email}',
        body: `Hola Equipo de Soporte de LUKHAS,

Estoy experimentando problemas con la verificación de email durante el registro de cuenta.

Detalles del Registro:
- Email: {email}
- Propósito: {purpose}
- Nivel de Registro: {userTier}
- Timestamp: {timestamp}

El Problema:
Estoy intentando completar mi registro de cuenta LUKHAS AI pero el email de verificación no está llegando. He revisado todos los lugares usuales (carpeta de spam, pestaña de promociones, etc.) pero no puedo localizar el mensaje.

Contexto Técnico:
- Remitente esperado: {senderDomain}
- Navegador: {browser}
- Dispositivo: {device}
- Zona horaria: {timezone}

¿Podrían por favor ayudarme a completar mi registro o reenviar el email de verificación?

¡Gracias por su ayuda!

Saludos cordiales,
{userAlias}`
      },
      'password-reset': {
        subject: 'Soporte de Restablecimiento de Contraseña - {email}',
        body: `Hola Equipo de Soporte de LUKHAS,

Necesito ayuda con la entrega del email de restablecimiento de contraseña.

Información de la Cuenta:
- Email: {email}
- Propósito: {purpose}
- Nivel de Usuario: {userTier}
- Timestamp: {timestamp}

Problema:
Solicité un restablecimiento de contraseña pero no he recibido el email de restablecimiento. He revisado:
- Bandeja de entrada principal
- Carpeta de Spam/Correo no deseado
- Todas las carpetas de email
- Esperé más de 10 minutos

Detalles Técnicos:
- Esperado de: {senderDomain}
- Navegador: {browser}
- SO: {os}
- Dispositivo: {device}

Por favor ayúdenme a restablecer mi contraseña o solucionar el problema de entrega de email.

Gracias,
{userAlias}`
      },
      default: {
        subject: 'Solicitud de Soporte de Autenticación - {email}',
        body: `Hola Equipo de Soporte de LUKHAS,

Necesito ayuda con la verificación de email para mi cuenta de LUKHAS AI.

Detalles de la Cuenta:
- Email: {email}
- Propósito de Autenticación: {purpose}
- Nivel de Usuario: {userTier}
- Realm/Zone: {realm}.{zone}
- Timestamp: {timestamp}

Descripción del Problema:
No estoy recibiendo emails de verificación de {senderDomain}. He intentado los pasos de solución de problemas estándar sin éxito.

Entorno:
- Navegador: {browser}
- Dispositivo: {device}
- Zona horaria: {timezone}

Por favor ayúdenme con este problema de autenticación.

Saludos cordiales,
{userAlias}`
      }
    }
  };

  const localeTemplates = templates[locale as keyof typeof templates] || templates.en;
  return localeTemplates[purpose as keyof typeof localeTemplates] || localeTemplates.default;
}

/**
 * Validate email address format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Generate a unique support request ID for tracking
 */
export function generateSupportRequestId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 5);
  return `LUKHAS-${timestamp}-${random}`.toUpperCase();
}

/**
 * Build a comprehensive support URL with query parameters
 */
export function buildSupportUrl({
  baseUrl = '/support',
  context,
  browserInfo,
  requestId
}: {
  baseUrl?: string;
  context: SupportContext;
  browserInfo: BrowserInfo;
  requestId?: string;
}): string {
  const params = new URLSearchParams();

  // Add context parameters
  params.set('email', context.email);
  params.set('purpose', context.purpose);
  if (context.userTier) params.set('tier', context.userTier);
  if (context.realm) params.set('realm', context.realm);
  if (context.zone) params.set('zone', context.zone);
  if (requestId) params.set('requestId', requestId);

  // Add browser info
  params.set('browser', `${browserInfo.browser} ${browserInfo.version}`);
  params.set('os', `${browserInfo.os} ${browserInfo.osVersion}`);
  params.set('device', browserInfo.device);
  params.set('timestamp', browserInfo.timestamp);

  return `${baseUrl}?${params.toString()}`;
}

export default {
  collectBrowserInfo,
  buildSupportMailto,
  getSupportEmailTemplate,
  isValidEmail,
  generateSupportRequestId,
  buildSupportUrl
};
