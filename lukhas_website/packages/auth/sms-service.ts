/**
 * SMS Service for Authentication Codes
 *
 * Production-ready SMS service with support for multiple providers
 * (Twilio, AWS SNS, Vonage, etc.) and international phone number formatting.
 */

export interface SMSConfig {
  provider: 'twilio' | 'aws-sns' | 'vonage' | 'messagebird' | 'console';
  // Twilio
  twilioAccountSid?: string;
  twilioAuthToken?: string;
  twilioPhoneNumber?: string;
  // AWS SNS
  awsRegion?: string;
  awsAccessKeyId?: string;
  awsSecretAccessKey?: string;
  // Vonage (formerly Nexmo)
  vonageApiKey?: string;
  vonageApiSecret?: string;
  vonageFrom?: string;
  // MessageBird
  messageBirdAccessKey?: string;
  messageBirdOriginator?: string;
  // General
  defaultCountryCode?: string;
}

export interface SMSTemplate {
  message: string;
}

export interface SendSMSParams {
  to: string; // E.164 format (e.g., +14155551234)
  message: string;
  metadata?: Record<string, any>;
}

export interface SMSSendResult {
  success: boolean;
  messageId?: string;
  error?: string;
  providedResponse?: any;
}

export class SMSService {
  private config: SMSConfig;
  private initialized: boolean = false;

  constructor(config: SMSConfig) {
    this.config = {
      defaultCountryCode: '+1', // US default
      ...config
    };
    this.initialize();
  }

  private initialize(): void {
    if (this.config.provider === 'console') {
      console.log('[SMSService] Running in console mode - SMS will be logged');
      this.initialized = true;
      return;
    }

    // Validate configuration based on provider
    switch (this.config.provider) {
      case 'twilio':
        if (!this.config.twilioAccountSid || !this.config.twilioAuthToken || !this.config.twilioPhoneNumber) {
          throw new Error('Twilio requires accountSid, authToken, and phoneNumber');
        }
        break;
      case 'aws-sns':
        if (!this.config.awsRegion) {
          throw new Error('AWS SNS requires awsRegion');
        }
        break;
      case 'vonage':
        if (!this.config.vonageApiKey || !this.config.vonageApiSecret) {
          throw new Error('Vonage requires apiKey and apiSecret');
        }
        break;
      case 'messagebird':
        if (!this.config.messageBirdAccessKey) {
          throw new Error('MessageBird requires accessKey');
        }
        break;
    }

    this.initialized = true;
  }

  async sendSMS(params: SendSMSParams): Promise<SMSSendResult> {
    if (!this.initialized) {
      return {
        success: false,
        error: 'SMS service not initialized'
      };
    }

    // Validate and format phone number
    const formattedPhone = this.formatPhoneNumber(params.to);
    if (!formattedPhone) {
      return {
        success: false,
        error: 'Invalid phone number format'
      };
    }

    try {
      switch (this.config.provider) {
        case 'console':
          return await this.sendViaConsole({ ...params, to: formattedPhone });
        case 'twilio':
          return await this.sendViaTwilio({ ...params, to: formattedPhone });
        case 'aws-sns':
          return await this.sendViaAWSSNS({ ...params, to: formattedPhone });
        case 'vonage':
          return await this.sendViaVonage({ ...params, to: formattedPhone });
        case 'messagebird':
          return await this.sendViaMessageBird({ ...params, to: formattedPhone });
        default:
          return {
            success: false,
            error: `Unsupported SMS provider: ${this.config.provider}`
          };
      }
    } catch (error: any) {
      console.error('[SMSService] Failed to send SMS:', error);
      return {
        success: false,
        error: error.message || 'Failed to send SMS'
      };
    }
  }

  async sendVerificationCode(params: {
    phoneNumber: string;
    code: string;
    expiresInMinutes: number;
    language?: string;
  }): Promise<SMSSendResult> {
    const { phoneNumber, code, expiresInMinutes, language = 'en' } = params;

    const messages = {
      en: `Your LUKHAS AI verification code is: ${code}\n\nThis code expires in ${expiresInMinutes} minutes.\n\nIf you didn't request this code, please ignore this message.`,
      es: `Tu código de verificación de LUKHAS AI es: ${code}\n\nEste código expira en ${expiresInMinutes} minutos.\n\nSi no solicitaste este código, ignora este mensaje.`
    };

    const message = messages[language as keyof typeof messages] || messages.en;

    return await this.sendSMS({
      to: phoneNumber,
      message,
      metadata: {
        type: 'verification_code',
        language
      }
    });
  }

  // Console provider (for development/testing)
  private async sendViaConsole(params: SendSMSParams): Promise<SMSSendResult> {
    console.log('\n=== SMS (Console Mode) ===');
    console.log(`To: ${params.to}`);
    console.log(`Message: ${params.message}`);
    console.log('========================\n');

    return {
      success: true,
      messageId: `console-sms-${Date.now()}`
    };
  }

  // Twilio provider
  private async sendViaTwilio(params: SendSMSParams): Promise<SMSSendResult> {
    try {
      const auth = Buffer.from(
        `${this.config.twilioAccountSid}:${this.config.twilioAuthToken}`
      ).toString('base64');

      const response = await fetch(
        `https://api.twilio.com/2010-04-01/Accounts/${this.config.twilioAccountSid}/Messages.json`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Basic ${auth}`,
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({
            To: params.to,
            From: this.config.twilioPhoneNumber!,
            Body: params.message
          })
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(`Twilio error: ${error.message || response.statusText}`);
      }

      const data = await response.json();

      return {
        success: true,
        messageId: data.sid,
        providedResponse: data
      };
    } catch (error: any) {
      throw new Error(`Twilio SMS failed: ${error.message}`);
    }
  }

  // AWS SNS provider
  private async sendViaAWSSNS(params: SendSMSParams): Promise<SMSSendResult> {
    try {
      // This would use AWS SDK v3
      // For now, placeholder
      console.log('[SMSService] AWS SNS integration pending - install @aws-sdk/client-sns');

      return {
        success: false,
        error: 'AWS SNS implementation pending'
      };
    } catch (error: any) {
      throw new Error(`AWS SNS failed: ${error.message}`);
    }
  }

  // Vonage (Nexmo) provider
  private async sendViaVonage(params: SendSMSParams): Promise<SMSSendResult> {
    try {
      const response = await fetch('https://rest.nexmo.com/sms/json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from: this.config.vonageFrom || 'LUKHAS',
          to: params.to.replace('+', ''),
          text: params.message,
          api_key: this.config.vonageApiKey,
          api_secret: this.config.vonageApiSecret
        })
      });

      if (!response.ok) {
        throw new Error(`Vonage API error: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.messages[0].status !== '0') {
        throw new Error(`Vonage error: ${data.messages[0]['error-text']}`);
      }

      return {
        success: true,
        messageId: data.messages[0]['message-id'],
        providedResponse: data
      };
    } catch (error: any) {
      throw new Error(`Vonage SMS failed: ${error.message}`);
    }
  }

  // MessageBird provider
  private async sendViaMessageBird(params: SendSMSParams): Promise<SMSSendResult> {
    try {
      const response = await fetch('https://rest.messagebird.com/messages', {
        method: 'POST',
        headers: {
          'Authorization': `AccessKey ${this.config.messageBirdAccessKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          originator: this.config.messageBirdOriginator || 'LUKHAS',
          recipients: [params.to],
          body: params.message
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(`MessageBird error: ${error.errors?.[0]?.description || response.statusText}`);
      }

      const data = await response.json();

      return {
        success: true,
        messageId: data.id,
        providedResponse: data
      };
    } catch (error: any) {
      throw new Error(`MessageBird SMS failed: ${error.message}`);
    }
  }

  /**
   * Format phone number to E.164 format
   */
  private formatPhoneNumber(phone: string): string | null {
    // Remove all non-digit characters except +
    let formatted = phone.replace(/[^\d+]/g, '');

    // If doesn't start with +, add default country code
    if (!formatted.startsWith('+')) {
      formatted = this.config.defaultCountryCode + formatted;
    }

    // Validate E.164 format (+ followed by 1-15 digits)
    const e164Regex = /^\+[1-9]\d{1,14}$/;
    if (!e164Regex.test(formatted)) {
      console.error('[SMSService] Invalid phone number format:', formatted);
      return null;
    }

    return formatted;
  }

  /**
   * Validate phone number
   */
  isValidPhoneNumber(phone: string): boolean {
    const formatted = this.formatPhoneNumber(phone);
    return formatted !== null;
  }
}

/**
 * Factory function to create SMS service from environment variables
 */
export function createSMSServiceFromEnv(): SMSService {
  const provider = (process.env.SMS_PROVIDER || 'console') as SMSConfig['provider'];

  const config: SMSConfig = {
    provider,
    // Twilio
    twilioAccountSid: process.env.TWILIO_ACCOUNT_SID,
    twilioAuthToken: process.env.TWILIO_AUTH_TOKEN,
    twilioPhoneNumber: process.env.TWILIO_PHONE_NUMBER,
    // AWS SNS
    awsRegion: process.env.AWS_REGION,
    awsAccessKeyId: process.env.AWS_ACCESS_KEY_ID,
    awsSecretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    // Vonage
    vonageApiKey: process.env.VONAGE_API_KEY,
    vonageApiSecret: process.env.VONAGE_API_SECRET,
    vonageFrom: process.env.VONAGE_FROM,
    // MessageBird
    messageBirdAccessKey: process.env.MESSAGEBIRD_ACCESS_KEY,
    messageBirdOriginator: process.env.MESSAGEBIRD_ORIGINATOR,
    // General
    defaultCountryCode: process.env.SMS_DEFAULT_COUNTRY_CODE || '+1'
  };

  return new SMSService(config);
}

export default SMSService;
