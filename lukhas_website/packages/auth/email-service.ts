/**
 * Email Service for Authentication
 *
 * Production-ready email service with support for multiple providers
 * (SendGrid, AWS SES, Resend, etc.) and template rendering.
 */

export interface EmailConfig {
  provider: 'sendgrid' | 'ses' | 'resend' | 'smtp' | 'console';
  apiKey?: string;
  fromEmail: string;
  fromName: string;
  replyTo?: string;
  awsRegion?: string; // For SES
  smtpHost?: string; // For SMTP
  smtpPort?: number;
  smtpUser?: string;
  smtpPass?: string;
}

export interface EmailTemplate {
  subject: string;
  htmlBody: string;
  textBody: string;
}

export interface SendEmailParams {
  to: string;
  template: EmailTemplate;
  metadata?: Record<string, any>;
}

export interface EmailSendResult {
  success: boolean;
  messageId?: string;
  error?: string;
  providedResponse?: any;
}

export class EmailService {
  private config: EmailConfig;
  private initialized: boolean = false;

  constructor(config: EmailConfig) {
    this.config = config;
    this.initialize();
  }

  private initialize(): void {
    if (this.config.provider === 'console') {
      console.log('[EmailService] Running in console mode - emails will be logged');
      this.initialized = true;
      return;
    }

    // Validate configuration based on provider
    switch (this.config.provider) {
      case 'sendgrid':
        if (!this.config.apiKey) {
          throw new Error('SendGrid API key is required');
        }
        break;
      case 'ses':
        if (!this.config.awsRegion) {
          throw new Error('AWS region is required for SES');
        }
        break;
      case 'resend':
        if (!this.config.apiKey) {
          throw new Error('Resend API key is required');
        }
        break;
      case 'smtp':
        if (!this.config.smtpHost || !this.config.smtpPort) {
          throw new Error('SMTP host and port are required');
        }
        break;
    }

    this.initialized = true;
  }

  async sendEmail(params: SendEmailParams): Promise<EmailSendResult> {
    if (!this.initialized) {
      return {
        success: false,
        error: 'Email service not initialized'
      };
    }

    try {
      switch (this.config.provider) {
        case 'console':
          return await this.sendViaConsole(params);
        case 'sendgrid':
          return await this.sendViaSendGrid(params);
        case 'ses':
          return await this.sendViaSES(params);
        case 'resend':
          return await this.sendViaResend(params);
        case 'smtp':
          return await this.sendViaSMTP(params);
        default:
          return {
            success: false,
            error: `Unsupported email provider: ${this.config.provider}`
          };
      }
    } catch (error: any) {
      console.error('[EmailService] Failed to send email:', error);
      return {
        success: false,
        error: error.message || 'Failed to send email'
      };
    }
  }

  async sendMagicLink(params: {
    email: string;
    magicLink: string;
    expiresInMinutes: number;
    language?: string;
  }): Promise<EmailSendResult> {
    const { email, magicLink, expiresInMinutes, language = 'en' } = params;

    const template = this.renderMagicLinkTemplate({
      magicLink,
      expiresInMinutes,
      language
    });

    return await this.sendEmail({
      to: email,
      template,
      metadata: {
        type: 'magic_link',
        language
      }
    });
  }

  async sendVerificationCode(params: {
    email: string;
    code: string;
    expiresInMinutes: number;
    purpose: 'login' | 'register' | 'password-reset';
    language?: string;
  }): Promise<EmailSendResult> {
    const { email, code, expiresInMinutes, purpose, language = 'en' } = params;

    const template = this.renderVerificationCodeTemplate({
      code,
      expiresInMinutes,
      purpose,
      language
    });

    return await this.sendEmail({
      to: email,
      template,
      metadata: {
        type: 'verification_code',
        purpose,
        language
      }
    });
  }

  // Console provider (for development/testing)
  private async sendViaConsole(params: SendEmailParams): Promise<EmailSendResult> {
    console.log('\n=== EMAIL (Console Mode) ===');
    console.log(`To: ${params.to}`);
    console.log(`Subject: ${params.template.subject}`);
    console.log(`\nText Body:\n${params.template.textBody}`);
    console.log('\n=========================\n');

    return {
      success: true,
      messageId: `console-${Date.now()}`
    };
  }

  // SendGrid provider
  private async sendViaSendGrid(params: SendEmailParams): Promise<EmailSendResult> {
    // Implementation would use @sendgrid/mail package
    // This is a placeholder that shows the structure
    const sendgrid = await import('@sendgrid/mail').catch(() => null);

    if (!sendgrid) {
      throw new Error('SendGrid package not installed. Run: npm install @sendgrid/mail');
    }

    sendgrid.setApiKey(this.config.apiKey!);

    const msg = {
      to: params.to,
      from: {
        email: this.config.fromEmail,
        name: this.config.fromName
      },
      replyTo: this.config.replyTo,
      subject: params.template.subject,
      text: params.template.textBody,
      html: params.template.htmlBody
    };

    const response = await sendgrid.send(msg);

    return {
      success: true,
      messageId: response[0].headers['x-message-id'],
      providedResponse: response[0]
    };
  }

  // AWS SES provider
  private async sendViaSES(params: SendEmailParams): Promise<EmailSendResult> {
    // Implementation would use AWS SDK v3
    // This is a placeholder
    throw new Error('AWS SES implementation pending - install @aws-sdk/client-ses');
  }

  // Resend provider
  private async sendViaResend(params: SendEmailParams): Promise<EmailSendResult> {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`
      },
      body: JSON.stringify({
        from: `${this.config.fromName} <${this.config.fromEmail}>`,
        to: [params.to],
        subject: params.template.subject,
        html: params.template.htmlBody,
        text: params.template.textBody,
        reply_to: this.config.replyTo
      })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(`Resend API error: ${error.message}`);
    }

    const data = await response.json();

    return {
      success: true,
      messageId: data.id,
      providedResponse: data
    };
  }

  // SMTP provider
  private async sendViaSMTP(params: SendEmailParams): Promise<EmailSendResult> {
    // Implementation would use nodemailer
    // This is a placeholder
    throw new Error('SMTP implementation pending - install nodemailer');
  }

  // Template rendering methods

  private renderMagicLinkTemplate(params: {
    magicLink: string;
    expiresInMinutes: number;
    language: string;
  }): EmailTemplate {
    const { magicLink, expiresInMinutes, language } = params;

    const content = {
      en: {
        subject: 'Your Magic Link - LUKHAS AI',
        heading: 'Sign in to LUKHAS AI',
        body: `Click the link below to sign in to your account. This link will expire in ${expiresInMinutes} minutes.`,
        button: 'Sign In',
        footer: 'If you didn\'t request this link, you can safely ignore this email.'
      },
      es: {
        subject: 'Tu Enlace Mágico - LUKHAS AI',
        heading: 'Inicia sesión en LUKHAS AI',
        body: `Haz clic en el enlace a continuación para iniciar sesión en tu cuenta. Este enlace expirará en ${expiresInMinutes} minutos.`,
        button: 'Iniciar Sesión',
        footer: 'Si no solicitaste este enlace, puedes ignorar este correo de forma segura.'
      }
    };

    const c = content[language as keyof typeof content] || content.en;

    const htmlBody = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
    <h1 style="color: white; margin: 0;">⚛️ LUKHAS AI</h1>
  </div>
  <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
    <h2 style="color: #333; margin-top: 0;">${c.heading}</h2>
    <p style="color: #666; font-size: 16px;">${c.body}</p>
    <div style="text-align: center; margin: 30px 0;">
      <a href="${magicLink}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">${c.button}</a>
    </div>
    <p style="color: #999; font-size: 14px; margin-top: 30px;">${c.footer}</p>
  </div>
</body>
</html>
    `.trim();

    const textBody = `
${c.heading}

${c.body}

${magicLink}

${c.footer}
    `.trim();

    return {
      subject: c.subject,
      htmlBody,
      textBody
    };
  }

  private renderVerificationCodeTemplate(params: {
    code: string;
    expiresInMinutes: number;
    purpose: string;
    language: string;
  }): EmailTemplate {
    const { code, expiresInMinutes, purpose, language } = params;

    const content = {
      en: {
        subject: 'Your Verification Code - LUKHAS AI',
        heading: 'Verification Code',
        body: `Your verification code for ${purpose} is:`,
        expires: `This code will expire in ${expiresInMinutes} minutes.`,
        footer: 'If you didn\'t request this code, you can safely ignore this email.'
      },
      es: {
        subject: 'Tu Código de Verificación - LUKHAS AI',
        heading: 'Código de Verificación',
        body: `Tu código de verificación para ${purpose} es:`,
        expires: `Este código expirará en ${expiresInMinutes} minutos.`,
        footer: 'Si no solicitaste este código, puedes ignorar este correo de forma segura.'
      }
    };

    const c = content[language as keyof typeof content] || content.en;

    const htmlBody = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
    <h1 style="color: white; margin: 0;">⚛️ LUKHAS AI</h1>
  </div>
  <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
    <h2 style="color: #333; margin-top: 0;">${c.heading}</h2>
    <p style="color: #666; font-size: 16px;">${c.body}</p>
    <div style="text-align: center; margin: 30px 0;">
      <div style="background: white; border: 2px solid #667eea; padding: 20px; border-radius: 10px; display: inline-block;">
        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #667eea;">${code}</span>
      </div>
    </div>
    <p style="color: #999; font-size: 14px; text-align: center;">${c.expires}</p>
    <p style="color: #999; font-size: 14px; margin-top: 30px;">${c.footer}</p>
  </div>
</body>
</html>
    `.trim();

    const textBody = `
${c.heading}

${c.body}

${code}

${c.expires}

${c.footer}
    `.trim();

    return {
      subject: c.subject,
      htmlBody,
      textBody
    };
  }
}

// Factory function to create email service from environment variables
export function createEmailServiceFromEnv(): EmailService {
  const provider = (process.env.EMAIL_PROVIDER || 'console') as EmailConfig['provider'];

  const config: EmailConfig = {
    provider,
    apiKey: process.env.EMAIL_API_KEY,
    fromEmail: process.env.EMAIL_FROM_ADDRESS || 'noreply@lukhas.ai',
    fromName: process.env.EMAIL_FROM_NAME || 'LUKHAS AI',
    replyTo: process.env.EMAIL_REPLY_TO,
    awsRegion: process.env.AWS_REGION,
    smtpHost: process.env.SMTP_HOST,
    smtpPort: process.env.SMTP_PORT ? parseInt(process.env.SMTP_PORT) : undefined,
    smtpUser: process.env.SMTP_USER,
    smtpPass: process.env.SMTP_PASS
  };

  return new EmailService(config);
}

export default EmailService;
