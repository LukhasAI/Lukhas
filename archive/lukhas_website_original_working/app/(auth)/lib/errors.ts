/**
 * LUKHAS AI - Authentication Error Mapping Utility
 * 
 * Maps API error responses to user-friendly messages with proper
 * internationalization and tone layer support.
 */

// Import error messages
import rateI18n from '@/locales/auth.rate.json';
import emailHelpI18n from '@/locales/auth.help.email.json';

export type Locale = 'en' | 'es';

export interface ErrorContext {
  /** The locale for error messages */
  locale?: Locale;
  /** The operation that failed */
  operation?: 'send_code' | 'verify_code' | 'magic_link' | 'passkey_register' | 'passkey_authenticate';
  /** Additional context for interpolation */
  context?: Record<string, string | number>;
  /** Whether to include poetic messages */
  includePoetic?: boolean;
}

export interface MappedError {
  /** Error type/category */
  type: 'network' | 'server' | 'validation' | 'rate_limit' | 'authentication' | 'authorization' | 'generic';
  /** User-friendly title */
  title: string;
  /** User-friendly message */
  message: string;
  /** Optional poetic message for detail sections */
  poetic?: string;
  /** Suggested user actions */
  actions?: string[];
  /** Technical details for debugging */
  technical?: string;
  /** Retry information */
  retry?: {
    allowed: boolean;
    after?: number; // milliseconds
    maxAttempts?: number;
  };
}

/**
 * Map HTTP status codes to error types
 */
export function getErrorTypeFromStatus(status: number): MappedError['type'] {
  if (status >= 400 && status < 500) {
    switch (status) {
      case 400:
      case 422:
        return 'validation';
      case 401:
        return 'authentication';
      case 403:
        return 'authorization';
      case 429:
        return 'rate_limit';
      default:
        return 'generic';
    }
  }
  
  if (status >= 500) {
    return 'server';
  }
  
  return 'generic';
}

/**
 * Map network errors to user-friendly messages
 */
export function mapNetworkError(
  error: Error | string,
  context: ErrorContext = {}
): MappedError {
  const { locale = 'en', includePoetic = false } = context;
  const t = rateI18n[locale];
  
  return {
    type: 'network',
    title: t.errors.network.title,
    message: t.errors.network.message,
    poetic: includePoetic ? t.errors.network.poetic : undefined,
    actions: [
      locale === 'es' ? 'Verificar conexión a internet' : 'Check internet connection',
      locale === 'es' ? 'Reintentar en unos segundos' : 'Retry in a few seconds'
    ],
    technical: typeof error === 'string' ? error : error.message,
    retry: {
      allowed: true,
      after: 3000 // 3 seconds
    }
  };
}

/**
 * Map HTTP response errors to user-friendly messages
 */
export function mapHttpError(
  response: Response,
  responseBody?: any,
  context: ErrorContext = {}
): MappedError {
  const { locale = 'en', includePoetic = false, operation } = context;
  const t = rateI18n[locale];
  const status = response.status;
  const errorType = getErrorTypeFromStatus(status);
  
  // Rate limiting
  if (status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    const retryMs = retryAfter ? parseInt(retryAfter, 10) * 1000 : undefined;
    
    return {
      type: 'rate_limit',
      title: t.rateLimit.exceeded.title,
      message: t.rateLimit.exceeded.message.replace('{time}', retryAfter || '1 hour'),
      poetic: includePoetic ? t.errors.server.poetic : undefined,
      actions: [
        locale === 'es' ? 'Esperar antes de reintentar' : 'Wait before retrying',
        locale === 'es' ? 'Usar un email diferente' : 'Try a different email address'
      ],
      technical: `HTTP ${status}: ${response.statusText}`,
      retry: {
        allowed: true,
        after: retryMs,
        maxAttempts: 5
      }
    };
  }
  
  // Validation errors
  if (errorType === 'validation') {
    return {
      type: 'validation',
      title: t.errors.validation.title,
      message: responseBody?.message || t.errors.validation.message,
      poetic: includePoetic ? t.errors.validation.poetic : undefined,
      actions: [
        locale === 'es' ? 'Verificar la información ingresada' : 'Check the entered information',
        locale === 'es' ? 'Corregir errores de formato' : 'Fix formatting errors'
      ],
      technical: `HTTP ${status}: ${responseBody?.details || response.statusText}`,
      retry: {
        allowed: false
      }
    };
  }
  
  // Authentication errors
  if (errorType === 'authentication') {
    return {
      type: 'authentication',
      title: locale === 'es' ? 'Error de Autenticación' : 'Authentication Error',
      message: responseBody?.message || (locale === 'es' 
        ? 'Las credenciales proporcionadas no son válidas' 
        : 'The provided credentials are not valid'),
      actions: [
        locale === 'es' ? 'Verificar credenciales' : 'Check credentials',
        locale === 'es' ? 'Solicitar nuevo código' : 'Request new code'
      ],
      technical: `HTTP ${status}: ${response.statusText}`,
      retry: {
        allowed: true
      }
    };
  }
  
  // Authorization errors
  if (errorType === 'authorization') {
    return {
      type: 'authorization',
      title: locale === 'es' ? 'Acceso Denegado' : 'Access Denied',
      message: responseBody?.message || (locale === 'es'
        ? 'No tienes permisos para realizar esta acción'
        : 'You do not have permission to perform this action'),
      actions: [
        locale === 'es' ? 'Contactar soporte' : 'Contact support',
        locale === 'es' ? 'Verificar permisos de cuenta' : 'Check account permissions'
      ],
      technical: `HTTP ${status}: ${response.statusText}`,
      retry: {
        allowed: false
      }
    };
  }
  
  // Server errors
  if (errorType === 'server') {
    return {
      type: 'server',
      title: t.errors.server.title,
      message: t.errors.server.message,
      poetic: includePoetic ? t.errors.server.poetic : undefined,
      actions: [
        locale === 'es' ? 'Intentar de nuevo en unos minutos' : 'Try again in a few minutes',
        locale === 'es' ? 'Contactar soporte si persiste' : 'Contact support if it persists'
      ],
      technical: `HTTP ${status}: ${response.statusText}`,
      retry: {
        allowed: true,
        after: 60000, // 1 minute
        maxAttempts: 3
      }
    };
  }
  
  // Generic errors
  return {
    type: 'generic',
    title: t.errors.generic.title,
    message: responseBody?.message || t.errors.generic.message,
    poetic: includePoetic ? t.errors.generic.poetic : undefined,
    actions: [
      locale === 'es' ? 'Reintentar' : 'Try again',
      locale === 'es' ? 'Refrescar la página' : 'Refresh the page'
    ],
    technical: `HTTP ${status}: ${response.statusText}`,
    retry: {
      allowed: true,
      after: 5000 // 5 seconds
    }
  };
}

/**
 * Map API operation errors with context
 */
export function mapOperationError(
  error: any,
  operation: ErrorContext['operation'],
  context: ErrorContext = {}
): MappedError {
  const enhancedContext = { ...context, operation };
  
  // Network/fetch errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return mapNetworkError(error, enhancedContext);
  }
  
  // HTTP response errors
  if (error.response) {
    return mapHttpError(error.response, error.data, enhancedContext);
  }
  
  // Generic errors
  return mapNetworkError(error, enhancedContext);
}

/**
 * Get suggested recovery actions based on error type and operation
 */
export function getRecoveryActions(
  errorType: MappedError['type'],
  operation?: ErrorContext['operation'],
  locale: Locale = 'en'
): string[] {
  const baseActions: Record<MappedError['type'], string[]> = {
    network: [
      locale === 'es' ? 'Verificar conexión a internet' : 'Check internet connection',
      locale === 'es' ? 'Reintentar' : 'Try again'
    ],
    server: [
      locale === 'es' ? 'Esperar unos minutos' : 'Wait a few minutes',
      locale === 'es' ? 'Reintentar' : 'Try again',
      locale === 'es' ? 'Contactar soporte' : 'Contact support'
    ],
    validation: [
      locale === 'es' ? 'Verificar información' : 'Check information',
      locale === 'es' ? 'Corregir errores' : 'Fix errors'
    ],
    rate_limit: [
      locale === 'es' ? 'Esperar período de enfriamiento' : 'Wait for cooldown period',
      locale === 'es' ? 'Usar email diferente' : 'Try different email'
    ],
    authentication: [
      locale === 'es' ? 'Verificar credenciales' : 'Check credentials',
      locale === 'es' ? 'Solicitar nuevo código' : 'Request new code'
    ],
    authorization: [
      locale === 'es' ? 'Contactar administrador' : 'Contact administrator',
      locale === 'es' ? 'Verificar permisos' : 'Check permissions'
    ],
    generic: [
      locale === 'es' ? 'Refrescar página' : 'Refresh page',
      locale === 'es' ? 'Reintentar' : 'Try again'
    ]
  };
  
  const actions = baseActions[errorType] || baseActions.generic;
  
  // Add operation-specific actions
  if (operation === 'send_code') {
    actions.push(
      locale === 'es' ? 'Verificar carpeta de spam' : 'Check spam folder',
      locale === 'es' ? 'Usar enlace mágico' : 'Try magic link'
    );
  } else if (operation === 'verify_code') {
    actions.push(
      locale === 'es' ? 'Verificar código ingresado' : 'Check entered code',
      locale === 'es' ? 'Solicitar nuevo código' : 'Request new code'
    );
  }
  
  return actions;
}

/**
 * Create error handler for API calls
 */
export function createErrorHandler(context: ErrorContext = {}) {
  return (error: any): MappedError => {
    return mapOperationError(error, context.operation, context);
  };
}

/**
 * Utility to check if an error is retryable
 */
export function isRetryableError(mappedError: MappedError): boolean {
  return mappedError.retry?.allowed === true;
}

/**
 * Utility to get retry delay
 */
export function getRetryDelay(mappedError: MappedError): number {
  return mappedError.retry?.after || 5000; // Default 5 seconds
}

export default {
  mapNetworkError,
  mapHttpError,
  mapOperationError,
  getRecoveryActions,
  createErrorHandler,
  isRetryableError,
  getRetryDelay,
  getErrorTypeFromStatus
};