/**
 * ΛiD Authentication System - TypeScript Type Definitions
 *
 * Comprehensive type definitions for LUKHAS authentication system
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

// =============================================================================
// CORE AUTHENTICATION TYPES
// =============================================================================

/**
 * User tier levels for LUKHAS access control
 */
export type UserTier = 'T1' | 'T2' | 'T3' | 'T4' | 'T5';

/**
 * User roles within organizations
 */
export type UserRole = 'owner' | 'admin' | 'developer' | 'analyst' | 'viewer';

/**
 * User account status
 */
export type UserStatus = 'active' | 'suspended' | 'locked' | 'deleted';

/**
 * Authentication scopes for permission management
 */
export type AuthScope =
  // MATRIZ Core Access
  | 'matriz:read'
  | 'matriz:write'
  | 'matriz:admin'

  // Identity Management
  | 'identity:read'
  | 'identity:write'
  | 'identity:admin'
  | 'identity:impersonate'

  // Orchestration & AI
  | 'orchestrator:run'
  | 'orchestrator:debug'
  | 'orchestrator:admin'

  // API Management
  | 'api:keys:read'
  | 'api:keys:write'
  | 'api:keys:delete'
  | 'api:keys:admin'

  // Organization Management
  | 'org:read'
  | 'org:settings'
  | 'org:members'
  | 'org:admin'

  // Billing & Commerce
  | 'billing:read'
  | 'billing:manage'
  | 'billing:admin'

  // Consciousness & Memory Systems
  | 'consciousness:read'
  | 'consciousness:write'
  | 'consciousness:debug'
  | 'memory:read'
  | 'memory:write'
  | 'memory:admin'

  // Guardian & Ethics
  | 'guardian:read'
  | 'guardian:configure'
  | 'guardian:override'

  // System Administration
  | 'system:monitor'
  | 'system:admin'
  | 'system:emergency';

/**
 * Permission object
 */
export interface Permission {
  scope: AuthScope;
  resourceType?: string;
  resourceId?: string;
  conditions?: Record<string, any>;
}

// =============================================================================
// USER TYPES
// =============================================================================

/**
 * User profile information
 */
export interface User {
  id: string;
  email: string;
  emailVerified: boolean;
  emailVerifiedAt?: string;
  tier: UserTier;
  role: UserRole;
  status: UserStatus;
  lockedUntil?: string;
  failedLoginAttempts: number;
  lastFailedLogin?: string;
  displayName?: string;
  avatarUrl?: string;
  timezone: string;
  locale: string;
  metadata: Record<string, any>;
  preferences: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  lastLoginAt?: string;
  lastActivityAt?: string;
}

/**
 * User creation data
 */
export interface CreateUserData {
  email: string;
  tier?: UserTier;
  role?: UserRole;
  displayName?: string;
  timezone?: string;
  locale?: string;
  metadata?: Record<string, any>;
  preferences?: Record<string, any>;
}

/**
 * User update data
 */
export interface UpdateUserData {
  tier?: UserTier;
  role?: UserRole;
  status?: UserStatus;
  displayName?: string;
  avatarUrl?: string;
  timezone?: string;
  locale?: string;
  metadata?: Record<string, any>;
  preferences?: Record<string, any>;
}

// =============================================================================
// JWT TYPES
// =============================================================================

/**
 * JWT header structure
 */
export interface JWTHeader {
  alg: 'RS256';
  typ: 'JWT';
  kid: string;
}

/**
 * JWT payload structure
 */
export interface JWTPayload {
  iss: string;                    // Issuer
  aud: string;                    // Audience
  sub: string;                    // Subject (user ID)
  iat: number;                    // Issued at
  exp: number;                    // Expires at
  jti: string;                    // JWT ID
  scope?: string;                 // Space-separated scopes
  tier: UserTier;                 // User tier
  type: 'access' | 'refresh';     // Token type
  device?: string;                // Device handle (for refresh tokens)
  family?: string;                // Token family ID (for refresh tokens)
  metadata?: Record<string, any>; // Additional metadata
}

/**
 * JWT token pair
 */
export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: 'Bearer';
  expiresIn: number;
  scope: string;
}

/**
 * JWT verification result
 */
export interface TokenVerificationResult {
  valid: boolean;
  reason?: string;
  payload?: JWTPayload;
  header?: JWTHeader;
}

/**
 * JWT options for token generation
 */
export interface JWTOptions {
  ttl?: number;
  metadata?: Record<string, any>;
}

/**
 * JWKS response structure
 */
export interface JWKSResponse {
  keys: Array<{
    kty: 'RSA';
    use: 'sig';
    kid: string;
    alg: 'RS256';
    n: string;
    e: string;
  }>;
}

/**
 * Refresh token data
 */
export interface RefreshTokenData {
  id: string;
  userId: string;
  familyId: string;
  tokenHash: string;
  deviceHandle: string;
  jti: string;
  scopes: AuthScope[];
  tier: UserTier;
  ipAddress?: string;
  userAgent?: string;
  revokedAt?: string;
  revokedReason?: string;
  createdAt: string;
  expiresAt: string;
  usedAt?: string;
  parentTokenId?: string;
  metadata: Record<string, any>;
}

// =============================================================================
// RATE LIMITING TYPES
// =============================================================================

/**
 * Rate limit configuration
 */
export interface RateLimitConfig {
  rpm: number;                    // Requests per minute
  rpd: number;                    // Requests per day
  burst: number;                  // Burst allowance
  concurrency: number;            // Max concurrent requests
  resetWindow: 'minute' | 'hour' | 'day';
}

/**
 * Rate limit window tracking
 */
export interface RateLimitWindow {
  count: number;
  burstUsed: number;
  expiresAt: number;
  createdAt: number;
}

/**
 * Rate limit check result
 */
export interface RateLimitResult {
  allowed: boolean;
  reason?: string;
  remaining?: {
    minute: number;
    day: number;
    burst: number;
  };
  resetTime: number;
  metadata?: Record<string, any>;
}

// =============================================================================
// PASSKEY TYPES
// =============================================================================

/**
 * Passkey credential information
 */
export interface PasskeyCredential {
  id: string;
  publicKey: string;
  algorithm: number;
  aaguid: string;
  authenticatorInfo?: {
    name: string;
    vendor: string;
    type: 'platform' | 'cross-platform';
    trusted: boolean;
    certificationLevel?: 'L1' | 'L2' | 'L3';
  };
  signCount: number;
  uvInitialized: boolean;
  backupEligible: boolean;
  backupState: boolean;
  deviceType: string;
  createdAt: string;
  lastUsedAt: string;
}

/**
 * Passkey registration options
 */
export interface PasskeyRegistrationOptions {
  challenge: string;
  rp: {
    id: string;
    name: string;
  };
  user: {
    id: ArrayBuffer;
    name: string;
    displayName: string;
  };
  pubKeyCredParams: Array<{
    type: 'public-key';
    alg: number;
  }>;
  timeout: number;
  attestation: 'none' | 'indirect' | 'direct' | 'enterprise';
  authenticatorSelection: {
    authenticatorAttachment?: 'platform' | 'cross-platform';
    userVerification: 'required' | 'preferred' | 'discouraged';
    residentKey: 'required' | 'preferred' | 'discouraged';
    requireResidentKey?: boolean;
  };
  excludeCredentials: Array<{
    type: 'public-key';
    id: ArrayBuffer;
    transports: string[];
  }>;
  extensions?: {
    credProps?: boolean;
    largeBlob?: {
      support: 'required' | 'preferred';
    };
  };
}

/**
 * Passkey authentication options
 */
export interface PasskeyAuthenticationOptions {
  challenge: string;
  timeout: number;
  rpId: string;
  userVerification: 'required' | 'preferred' | 'discouraged';
  allowCredentials?: Array<{
    type: 'public-key';
    id: ArrayBuffer;
    transports: string[];
  }>;
  extensions?: {
    largeBlob?: {
      read: boolean;
    };
    getCredBlob?: boolean;
  };
}

/**
 * Passkey registration result
 */
export interface PasskeyRegistrationResult {
  verified: boolean;
  reason?: string;
  credential?: PasskeyCredential;
  attestationObject?: any;
  clientData?: any;
}

/**
 * Passkey authentication result
 */
export interface PasskeyAuthenticationResult {
  verified: boolean;
  reason?: string;
  credential?: PasskeyCredential;
  newSignCount?: number;
  userVerified?: boolean;
  clientData?: any;
}

/**
 * Passkey validation result
 */
export interface PasskeyValidationResult {
  supported: boolean;
  reason?: string;
  capabilities?: {
    platform: boolean;
    conditionalUI: boolean;
    largeBlob: boolean;
    userVerifying: boolean;
  };
}

// =============================================================================
// MAGIC LINK TYPES
// =============================================================================

/**
 * Magic link options
 */
export interface MagicLinkOptions {
  userId?: string;
  userTier?: UserTier;
  ipAddress: string;
  userAgent: string;
  maxAttempts?: number;
  metadata?: Record<string, any>;
}

/**
 * Magic link result
 */
export interface MagicLinkResult {
  success: boolean;
  reason?: string;
  token?: string;
  magicLink?: string;
  expiresAt?: string;
  expiresIn?: number;
  resetTime?: number;
}

/**
 * Magic link validation result
 */
export interface MagicLinkValidationResult {
  valid: boolean;
  reason?: string;
  email?: string;
  userId?: string;
  purpose?: 'login' | 'register' | 'password-reset' | 'email-verification';
  metadata?: Record<string, any>;
}

/**
 * Throttle configuration
 */
export interface ThrottleConfig {
  enabled: boolean;
  windowSizeMs: number;
  maxAttempts: number;
  blockDurationMs: number;
}

/**
 * Magic link token
 */
export interface MagicLinkToken {
  id: string;
  userId?: string;
  tokenHash: string;
  tokenPartial: string;
  email: string;
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification';
  ipAddress?: string;
  userAgent?: string;
  maxAttempts: number;
  attempts: number;
  usedAt?: string;
  usedIpAddress?: string;
  createdAt: string;
  expiresAt: string;
  metadata: Record<string, any>;
}

// =============================================================================
// SESSION TYPES
// =============================================================================

/**
 * Session information
 */
export interface Session {
  id: string;
  userId: string;
  deviceHandle: string;
  accessTokenJti: string;
  refreshTokenJti?: string;
  ipAddress?: string;
  userAgent?: string;
  fingerprintHash?: string;
  scopes: AuthScope[];
  tier: UserTier;
  role: UserRole;
  createdAt: string;
  expiresAt: string;
  lastUsedAt: string;
  metadata: Record<string, any>;
}

/**
 * Device handle information
 */
export interface DeviceHandle {
  id: string;
  userId: string;
  handle: string;
  deviceType?: string;
  fingerprintHash?: string;
  deviceName?: string;
  platform?: string;
  browser?: string;
  browserVersion?: string;
  trusted: boolean;
  trustedAt?: string;
  trustedBy?: string;
  firstSeenAt: string;
  lastSeenAt: string;
  lastIpAddress?: string;
  useCount: number;
  blocked: boolean;
  blockedAt?: string;
  blockedReason?: string;
  metadata: Record<string, any>;
}

/**
 * Backup code information
 */
export interface BackupCode {
  id: string;
  userId: string;
  codeHash: string;
  codePartial: string;
  usedAt?: string;
  usedIpAddress?: string;
  usedUserAgent?: string;
  createdAt: string;
  expiresAt?: string;
  metadata: Record<string, any>;
}

// =============================================================================
// SECURITY EVENT TYPES
// =============================================================================

/**
 * Security event severity levels
 */
export type SecurityEventSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';

/**
 * Security event categories
 */
export type SecurityEventCategory = 'auth' | 'session' | 'device' | 'security' | 'admin';

/**
 * Security event information
 */
export interface SecurityEvent {
  id: string;
  userId?: string;
  eventType: string;
  eventCategory: SecurityEventCategory;
  severity: SecurityEventSeverity;
  ipAddress?: string;
  userAgent?: string;
  deviceHandle?: string;
  sessionId?: string;
  success?: boolean;
  errorCode?: string;
  errorMessage?: string;
  requestId?: string;
  endpoint?: string;
  method?: string;
  countryCode?: string;
  region?: string;
  city?: string;
  riskScore: number;
  riskFactors?: string[];
  createdAt: string;
  metadata: Record<string, any>;
}

// =============================================================================
// OAUTH TYPES
// =============================================================================

/**
 * OAuth application information
 */
export interface OAuthApplication {
  id: string;
  clientId: string;
  name: string;
  description?: string;
  redirectUris: string[];
  allowedScopes: AuthScope[];
  grantTypes: string[];
  responseTypes: string[];
  websiteUrl?: string;
  privacyPolicyUrl?: string;
  termsOfServiceUrl?: string;
  logoUrl?: string;
  trusted: boolean;
  confidential: boolean;
  pkceRequired: boolean;
  ownerId: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;
  metadata: Record<string, any>;
}

/**
 * OAuth authorization code
 */
export interface OAuthAuthorizationCode {
  id: string;
  codeHash: string;
  clientId: string;
  userId: string;
  redirectUri: string;
  scopes: AuthScope[];
  state?: string;
  codeChallenge?: string;
  codeChallengeMethod?: 'S256' | 'plain';
  usedAt?: string;
  createdAt: string;
  expiresAt: string;
  metadata: Record<string, any>;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

/**
 * Standard API response wrapper
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: string;
    requestId: string;
    rateLimit?: {
      remaining: number;
      resetTime: number;
    };
  };
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T = any> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

/**
 * Authentication response
 */
export interface AuthResponse {
  user: User;
  tokens: TokenPair;
  session: Session;
  requiresMFA?: boolean;
  mfaChallenge?: {
    type: 'passkey' | 'backup-code';
    challenge?: string;
    options?: any;
  };
}

/**
 * Login request data
 */
export interface LoginRequest {
  email: string;
  password?: string;
  magicLinkToken?: string;
  passkey?: any;
  backupCode?: string;
  deviceHandle?: string;
  ipAddress?: string;
  userAgent?: string;
  metadata?: Record<string, any>;
}

/**
 * Registration request data
 */
export interface RegistrationRequest {
  email: string;
  displayName?: string;
  tier?: UserTier;
  inviteCode?: string;
  deviceHandle?: string;
  ipAddress?: string;
  userAgent?: string;
  metadata?: Record<string, any>;
}

// =============================================================================
// MIDDLEWARE TYPES
// =============================================================================

/**
 * Authentication middleware context
 */
export interface AuthContext {
  user?: User;
  session?: Session;
  token?: JWTPayload;
  scopes: AuthScope[];
  tier: UserTier;
  role: UserRole;
  deviceHandle?: string;
  ipAddress?: string;
  userAgent?: string;
}

/**
 * Permission check options
 */
export interface PermissionCheckOptions {
  scope: AuthScope;
  resourceType?: string;
  resourceId?: string;
  conditions?: Record<string, any>;
  allowInherited?: boolean;
}

/**
 * Rate limit check options
 */
export interface RateLimitCheckOptions {
  operation?: string;
  identifier?: string;
  customLimits?: Partial<RateLimitConfig>;
}

// =============================================================================
// CONFIGURATION TYPES
// =============================================================================

/**
 * Authentication system configuration
 */
export interface AuthConfig {
  jwt: {
    issuer: string;
    audience: string;
    accessTokenTTL: number;
    refreshTokenTTL: number;
    algorithm: 'RS256';
  };
  passkeys: {
    rpId: string;
    rpName: string;
    origin: string;
    timeout: number;
    userVerification: 'required' | 'preferred' | 'discouraged';
    attestation: 'none' | 'indirect' | 'direct' | 'enterprise';
  };
  magicLinks: {
    tokenTTL: number;
    maxAttempts: number;
    throttling: ThrottleConfig;
  };
  rateLimits: Record<UserTier, RateLimitConfig>;
  security: {
    maxLoginAttempts: number;
    lockoutDuration: number;
    sessionTimeout: number;
    requireMFA: boolean;
  };
}

// =============================================================================
// ERROR TYPES
// =============================================================================

/**
 * Authentication error codes
 */
export enum AuthErrorCode {
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  USER_NOT_FOUND = 'USER_NOT_FOUND',
  USER_LOCKED = 'USER_LOCKED',
  USER_SUSPENDED = 'USER_SUSPENDED',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  TOKEN_INVALID = 'TOKEN_INVALID',
  TOKEN_REVOKED = 'TOKEN_REVOKED',
  INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  MFA_REQUIRED = 'MFA_REQUIRED',
  INVALID_MFA = 'INVALID_MFA',
  DEVICE_NOT_TRUSTED = 'DEVICE_NOT_TRUSTED',
  PASSKEY_NOT_SUPPORTED = 'PASSKEY_NOT_SUPPORTED',
  PASSKEY_VERIFICATION_FAILED = 'PASSKEY_VERIFICATION_FAILED',
  MAGIC_LINK_EXPIRED = 'MAGIC_LINK_EXPIRED',
  MAGIC_LINK_USED = 'MAGIC_LINK_USED',
  MAGIC_LINK_INVALID = 'MAGIC_LINK_INVALID',
  EMAIL_NOT_VERIFIED = 'EMAIL_NOT_VERIFIED',
  INVALID_TIER = 'INVALID_TIER',
  INVALID_SCOPE = 'INVALID_SCOPE',
  SECURITY_VIOLATION = 'SECURITY_VIOLATION'
}

/**
 * Authentication error
 */
export class AuthError extends Error {
  constructor(
    public code: AuthErrorCode,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/**
 * Create type for partial updates
 */
export type PartialUpdate<T> = Partial<Omit<T, 'id' | 'createdAt' | 'updatedAt'>>;

/**
 * Create type for database entities
 */
export type DatabaseEntity<T> = T & {
  id: string;
  createdAt: string;
  updatedAt: string;
};

/**
 * Create type for API create requests
 */
export type CreateRequest<T> = Omit<T, 'id' | 'createdAt' | 'updatedAt'>;

/**
 * Create type for API update requests
 */
export type UpdateRequest<T> = PartialUpdate<T>;

// =============================================================================
// EXPORTS
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

  // Verification code types
  VerificationCodeOptions,
  VerificationCodeResult,
  VerificationCodeValidationResult,
  VerificationCodeEntry,

// =============================================================================
// VERIFICATION CODE TYPES
// =============================================================================

/**
 * Verification code options
 */
export interface VerificationCodeOptions {
  userId?: string;
  userTier?: UserTier;
  ipAddress: string;
  userAgent: string;
  maxAttempts?: number;
  metadata?: Record<string, any>;
}

/**
 * Verification code result
 */
export interface VerificationCodeResult {
  success: boolean;
  reason?: string;
  code?: string;  // Only returned for sending, never stored
  expiresAt?: string;
  expiresIn?: number;
  resetTime?: number;
}

/**
 * Verification code validation result
 */
export interface VerificationCodeValidationResult {
  valid: boolean;
  reason?: string;
  email?: string;
  userId?: string;
  purpose?: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification';
  metadata?: Record<string, any>;
}

/**
 * Verification code entry (no raw codes stored)
 */
export interface VerificationCodeEntry {
  id: string;
  userId?: string;
  codeHash: string;  // HMAC hash, never the actual code
  email: string;
  purpose: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification';
  ipAddress?: string;
  userAgent?: string;
  maxAttempts: number;
  attempts: number;
  verifiedAt?: string;
  verifiedIpAddress?: string;
  createdAt: string;
  expiresAt: string;
  metadata: Record<string, any>;
}

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
};

export { AuthErrorCode, AuthError };
