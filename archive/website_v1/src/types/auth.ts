/**
 * LUKHAS ΛiD Authentication Types (Simplified for Website)
 * 
 * Based on the comprehensive LUKHAS authentication system
 * Simplified subset for website frontend integration
 */

export type UserTier = 'T1' | 'T2' | 'T3' | 'T4' | 'T5';
export type UserRole = 'owner' | 'admin' | 'developer' | 'analyst' | 'viewer';
export type UserStatus = 'active' | 'suspended' | 'locked' | 'deleted';

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

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: 'Bearer';
  expiresIn: number;
  scope: string;
}

export interface Session {
  id: string;
  userId: string;
  deviceHandle: string;
  accessTokenJti: string;
  refreshTokenJti?: string;
  ipAddress?: string;
  userAgent?: string;
  fingerprintHash?: string;
  scopes: string[];
  tier: UserTier;
  role: UserRole;
  createdAt: string;
  expiresAt: string;
  lastUsedAt: string;
  metadata: Record<string, any>;
}

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