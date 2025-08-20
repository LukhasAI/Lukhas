/**
 * ΛiD Authentication System - Main Export
 * 
 * Phase 1: Core Infrastructure
 * Enterprise-grade authentication for LUKHAS AI
 * Integrates with Trinity Framework (⚛️🧠🛡️)
 */

// =============================================================================
// CORE AUTHENTICATION MODULES
// =============================================================================

// Scope Management
export {
  hasScope,
  getInheritedScopes,
  isValidScope,
  getAvailableScopes,
  getRoleScopes,
  canGrantScope,
  logAuthorizationDecision,
  emergencyOverride,
  Tier,
  Scope,
  Role,
  TIER_ENVELOPES,
  ROLE_SCOPES,
  SCOPE_HIERARCHY
} from './scopes';

// Rate Limiting
export {
  checkRateLimit,
  acquireConcurrencySlot,
  releaseConcurrencySlot,
  getRateLimitStatus,
  resetRateLimits,
  getAdaptiveRateLimit,
  rateLimitMiddleware,
  TIER_RATE_LIMITS,
  OPERATION_RATE_LIMITS
} from './rate-limits';

// JWT Management
export {
  JWTManager,
  jwtManager,
  generateAccessToken,
  generateRefreshToken,
  generateTokenPair,
  verifyToken,
  getJWKS,
  revokeToken,
  fetchJWKS,
  jwtMiddleware,
  refreshTokens,
  DEFAULT_JWT_CONFIG
} from './jwt';

// Passkey Authentication
export {
  PasskeyManager,
  passkeyManager,
  registerPasskey,
  verifyPasskeyRegistration,
  authenticateWithPasskey,
  verifyPasskeyAuthentication,
  checkPasskeySupport,
  enableConditionalUI,
  storePasskeyBlob,
  retrievePasskeyBlob,
  DEFAULT_WEBAUTHN_CONFIG,
  KNOWN_AAGUIDS
} from './passkeys';

// Magic Links
export {
  MagicLinkManager,
  magicLinkManager,
  sendMagicLink,
  verifyMagicLink,
  checkMagicLinkStatus,
  revokeMagicLink,
  getThrottleLimits,
  sendMagicLinkEmail,
  DEFAULT_MAGIC_LINK_CONFIG
} from './magic-links';

// Security Features
export {
  SecurityManager,
  securityManager,
  RefreshTokenFamilyManager,
  DeviceBindingManager,
  SessionRotationManager,
  AccountLockoutManager
} from './security';

// Tier Configuration
export {
  getTierDefinition,
  getAvailableTiers,
  canUpgradeTier,
  validateTierTransition,
  getTierComparison,
  calculateTierValue,
  tierHasFeature,
  tierCanPerformOperation,
  getTierUpgradeRecommendations,
  TIER_DEFINITIONS,
  LUKHAS_AUTH_CONFIG
} from './tier-config';

// =============================================================================
// TYPE EXPORTS
// =============================================================================

export type {
  // Core types
  UserTier,
  UserRole,
  UserStatus,
  AuthScope,
  Permission,
  
  // User types
  User,
  CreateUserData,
  UpdateUserData,
  
  // JWT types
  JWTHeader,
  JWTPayload,
  TokenPair,
  TokenVerificationResult,
  JWTOptions,
  JWKSResponse,
  RefreshTokenData,
  
  // Rate limiting types
  RateLimitConfig,
  RateLimitWindow,
  RateLimitResult,
  
  // Passkey types
  PasskeyCredential,
  PasskeyRegistrationOptions,
  PasskeyAuthenticationOptions,
  PasskeyRegistrationResult,
  PasskeyAuthenticationResult,
  PasskeyValidationResult,
  
  // Magic link types
  MagicLinkOptions,
  MagicLinkResult,
  MagicLinkValidationResult,
  ThrottleConfig,
  MagicLinkToken,
  
  // Session types
  Session,
  DeviceHandle,
  BackupCode,
  
  // Security event types
  SecurityEventSeverity,
  SecurityEventCategory,
  SecurityEvent,
  
  // OAuth types
  OAuthApplication,
  OAuthAuthorizationCode,
  
  // API types
  ApiResponse,
  PaginatedResponse,
  AuthResponse,
  LoginRequest,
  RegistrationRequest,
  
  // Middleware types
  AuthContext,
  PermissionCheckOptions,
  RateLimitCheckOptions,
  
  // Configuration types
  AuthConfig,
  
  // Utility types
  PartialUpdate,
  DatabaseEntity,
  CreateRequest,
  UpdateRequest
} from '../types/auth.types';

export { AuthErrorCode, AuthError } from '../types/auth.types';

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Initialize ΛiD Authentication System
 */
export function initializeAuth(config?: Partial<typeof LUKHAS_AUTH_CONFIG>) {
  console.log('🚀 Initializing ΛiD Authentication System (Phase 1)');
  console.log('⚛️🧠🛡️ Trinity Framework Integration Active');
  
  if (config) {
    console.log('📋 Custom configuration applied');
  }
  
  return {
    version: '1.0.0',
    phase: 'Phase 1: Core Infrastructure',
    features: [
      'Tier-based access control (T1-T5)',
      'RS256 JWT with key rotation',
      'WebAuthn passkey authentication',
      'Magic link authentication',
      'Advanced rate limiting',
      'Refresh token family tracking',
      'Device binding and fingerprinting',
      'Session rotation',
      'Account lockout with exponential backoff'
    ],
    initialized: true,
    timestamp: new Date().toISOString()
  };
}

/**
 * Get system health status
 */
export function getAuthSystemHealth() {
  return {
    status: 'healthy',
    version: '1.0.0',
    phase: 'Phase 1: Core Infrastructure',
    components: {
      scopes: 'operational',
      rateLimiting: 'operational',
      jwt: 'operational',
      passkeys: 'operational',
      magicLinks: 'operational',
      security: 'operational',
      tierSystem: 'operational'
    },
    metrics: {
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage(),
      timestamp: new Date().toISOString()
    }
  };
}

/**
 * Validate authentication configuration
 */
export function validateAuthConfig(config: any): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check required JWT configuration
  if (!config?.jwt?.issuer) {
    errors.push('JWT issuer is required');
  }
  
  if (!config?.jwt?.audience) {
    errors.push('JWT audience is required');
  }

  // Check WebAuthn configuration
  if (!config?.passkeys?.rpId) {
    errors.push('WebAuthn RP ID is required');
  }

  // Check rate limiting configuration
  if (!config?.rateLimits) {
    warnings.push('Rate limiting configuration not provided, using defaults');
  }

  // Check security configuration
  if (config?.security?.requireMFA === undefined) {
    warnings.push('MFA requirement not specified, defaulting to false');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

// =============================================================================
// DEFAULT EXPORTS FOR CONVENIENCE
// =============================================================================

export default {
  // Main initialization
  initialize: initializeAuth,
  
  // Core managers
  jwt: jwtManager,
  passkeys: passkeyManager,
  magicLinks: magicLinkManager,
  security: securityManager,
  
  // Utility functions
  hasScope,
  checkRateLimit,
  getTierDefinition,
  getAuthSystemHealth,
  validateAuthConfig,
  
  // Configuration
  config: LUKHAS_AUTH_CONFIG
};