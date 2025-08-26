/**
 * Database Interface for ΛiD Authentication System
 *
 * TypeScript interfaces and types that correspond to the PostgreSQL schema.
 * Provides type safety for database operations and ORM integration.
 */

import { TierLevel } from './scopes';

// Enum types matching PostgreSQL enums
export type UserTier = TierLevel;
export type UserStatus = 'pending' | 'active' | 'suspended' | 'deleted';
export type DeviceType = 'platform' | 'cross-platform' | 'mobile' | 'desktop' | 'unknown';
export type SessionStatus = 'active' | 'expired' | 'revoked';
export type SecurityEventType =
  | 'login_attempt' | 'login_success' | 'login_failure'
  | 'logout' | 'password_change' | 'email_change'
  | 'mfa_enabled' | 'mfa_disabled' | 'passkey_added' | 'passkey_removed'
  | 'session_created' | 'session_expired' | 'session_revoked'
  | 'suspicious_activity' | 'account_locked' | 'account_unlocked'
  | 'magic_link_sent' | 'magic_link_used' | 'rate_limit_hit'
  | 'token_refresh' | 'token_revocation' | 'data_export'
  | 'privacy_setting_change' | 'security_alert';

// Base interface for all database entities
export interface BaseEntity {
  id: string;
  created_at: Date;
  updated_at?: Date;
  deleted_at?: Date;
}

// 1. Users table interface
export interface User extends BaseEntity {
  email: string;
  email_verified: boolean;
  email_verified_at?: Date;

  // User tier and status
  tier: UserTier;
  status: UserStatus;

  // Profile information
  display_name?: string;
  given_name?: string;
  family_name?: string;
  picture_url?: string;
  locale?: string;
  timezone?: string;

  // Password-related
  password_hash?: string;
  password_changed_at?: Date;
  password_reset_required: boolean;

  // Organization membership
  organization_id?: string;
  organization_role?: string;

  // Preferences and settings
  preferences: Record<string, any>;
  feature_flags: Record<string, any>;

  // Audit fields
  last_login_at?: Date;
  login_count: number;
}

// User creation input
export interface CreateUserInput {
  email: string;
  tier?: UserTier;
  display_name?: string;
  given_name?: string;
  family_name?: string;
  picture_url?: string;
  locale?: string;
  timezone?: string;
  organization_id?: string;
  organization_role?: string;
  preferences?: Record<string, any>;
}

// User update input
export interface UpdateUserInput {
  email?: string;
  email_verified?: boolean;
  tier?: UserTier;
  status?: UserStatus;
  display_name?: string;
  given_name?: string;
  family_name?: string;
  picture_url?: string;
  locale?: string;
  timezone?: string;
  password_hash?: string;
  organization_id?: string;
  organization_role?: string;
  preferences?: Record<string, any>;
  feature_flags?: Record<string, any>;
}

// 2. Sessions table interface
export interface Session extends BaseEntity {
  user_id: string;
  device_handle_id?: string;

  // Session identification
  session_token: string;
  session_token_hash: string;

  // Session metadata
  status: SessionStatus;
  ip_address: string;
  user_agent?: string;

  // Geolocation
  country_code?: string;
  city?: string;

  // Session lifetime
  expires_at: Date;
  last_activity_at: Date;

  // Session data
  scopes: string[];
  roles: string[];
  metadata: Record<string, any>;

  // Revocation tracking
  revoked_at?: Date;
  revocation_reason?: string;
}

export interface CreateSessionInput {
  user_id: string;
  device_handle_id?: string;
  session_token: string;
  session_token_hash: string;
  ip_address: string;
  user_agent?: string;
  expires_at: Date;
  scopes?: string[];
  roles?: string[];
  metadata?: Record<string, any>;
}

// 3. Passkeys table interface
export interface Passkey extends BaseEntity {
  user_id: string;

  // WebAuthn credential data
  credential_id: Uint8Array;
  credential_id_b64: string;
  public_key: Uint8Array;
  algorithm: number;

  // User handle for discoverable credentials
  user_handle: string;

  // Authenticator information
  aaguid?: string;
  device_type: DeviceType;
  device_label: string;

  // WebAuthn flags and counters
  sign_count: number;
  uv_required: boolean;
  rk: boolean;

  // Transport methods
  transports: string[];

  // Attestation data
  attestation_type?: string;
  attestation_data?: Uint8Array;

  // Backup eligibility and state
  backup_eligible: boolean;
  backup_state: boolean;

  // Usage tracking
  last_used_at?: Date;
  use_count: number;
}

export interface CreatePasskeyInput {
  user_id: string;
  credential_id: Uint8Array;
  credential_id_b64: string;
  public_key: Uint8Array;
  algorithm: number;
  user_handle: string;
  aaguid?: string;
  device_type: DeviceType;
  device_label: string;
  uv_required?: boolean;
  rk?: boolean;
  transports?: string[];
  attestation_type?: string;
  attestation_data?: Uint8Array;
  backup_eligible?: boolean;
  backup_state?: boolean;
}

// 4. Refresh tokens table interface
export interface RefreshToken extends BaseEntity {
  user_id: string;
  device_handle_id?: string;

  // Refresh token family tracking
  family_id: string;
  token_hash: string;

  // Token metadata
  sequence_number: number;
  parent_token_id?: string;

  // Lifetime and usage
  expires_at: Date;
  used_at?: Date;

  // Security tracking
  ip_address: string;
  user_agent?: string;

  // Revocation
  revoked_at?: Date;
  revocation_reason?: string;

  // Metadata
  scopes: string[];
  metadata: Record<string, any>;
}

export interface CreateRefreshTokenInput {
  user_id: string;
  device_handle_id?: string;
  family_id: string;
  token_hash: string;
  sequence_number?: number;
  parent_token_id?: string;
  expires_at: Date;
  ip_address: string;
  user_agent?: string;
  scopes?: string[];
  metadata?: Record<string, any>;
}

// 5. Device handles table interface
export interface DeviceHandle extends BaseEntity {
  user_id: string;

  // Device identification
  device_id: string;
  device_fingerprint?: string;

  // Device metadata
  device_type: DeviceType;
  device_name?: string;
  platform?: string;
  browser?: string;
  os?: string;

  // Network information
  ip_address?: string;
  country_code?: string;
  city?: string;

  // Trust level
  trusted: boolean;
  trust_score: number;

  // Usage tracking
  last_used_at: Date;
  last_seen_ip?: string;
  use_count: number;

  // Additional metadata
  metadata: Record<string, any>;
}

export interface CreateDeviceHandleInput {
  user_id: string;
  device_id: string;
  device_fingerprint?: string;
  device_type: DeviceType;
  device_name?: string;
  platform?: string;
  browser?: string;
  os?: string;
  ip_address?: string;
  country_code?: string;
  city?: string;
  trusted?: boolean;
  trust_score?: number;
  metadata?: Record<string, any>;
}

// 6. Backup codes table interface
export interface BackupCode extends BaseEntity {
  user_id: string;

  // Code data
  code_hash: string;
  code_partial: string;

  // Usage tracking
  used_at?: Date;

  // Context when used
  used_ip_address?: string;
  used_user_agent?: string;
}

export interface CreateBackupCodeInput {
  user_id: string;
  code_hash: string;
  code_partial: string;
}

// 7. Security events table interface
export interface SecurityEvent extends BaseEntity {
  user_id?: string;
  session_id?: string;

  // Event classification
  event_type: SecurityEventType;
  event_category?: string;
  severity: 'info' | 'warning' | 'error' | 'critical';

  // Event details
  description?: string;
  result?: 'success' | 'failure' | 'blocked';
  error_code?: string;

  // Context information
  ip_address?: string;
  user_agent?: string;
  country_code?: string;
  city?: string;

  // Request details
  endpoint?: string;
  method?: string;
  status_code?: number;

  // Device and session context
  device_handle_id?: string;
  device_fingerprint?: string;

  // Risk assessment
  risk_score?: number;
  risk_factors?: string[];

  // Timing
  event_timestamp: Date;

  // Additional data
  metadata: Record<string, any>;

  // Data retention
  expires_at?: Date;
}

export interface CreateSecurityEventInput {
  user_id?: string;
  session_id?: string;
  event_type: SecurityEventType;
  event_category?: string;
  severity?: 'info' | 'warning' | 'error' | 'critical';
  description?: string;
  result?: 'success' | 'failure' | 'blocked';
  error_code?: string;
  ip_address?: string;
  user_agent?: string;
  country_code?: string;
  city?: string;
  endpoint?: string;
  method?: string;
  status_code?: number;
  device_handle_id?: string;
  device_fingerprint?: string;
  risk_score?: number;
  risk_factors?: string[];
  event_timestamp?: Date;
  metadata?: Record<string, any>;
  expires_at?: Date;
}

// Additional tables

// Email verification tokens interface
export interface EmailVerificationToken extends BaseEntity {
  user_id: string;
  email: string;
  token_hash: string;
  expires_at: Date;
  used_at?: Date;
}

export interface CreateEmailVerificationTokenInput {
  user_id: string;
  email: string;
  token_hash: string;
  expires_at: Date;
}

// Rate limit entries interface
export interface RateLimitEntry extends BaseEntity {
  key_hash: string;
  user_id?: string;

  // Rate limit counters
  count: number;
  daily_count: number;

  // Reset times
  reset_time: Date;
  daily_reset_time: Date;

  // Block status
  blocked: boolean;
  block_expires_at?: Date;

  // Metadata
  tier?: UserTier;
  endpoint?: string;
  ip_address?: string;
}

export interface CreateRateLimitEntryInput {
  key_hash: string;
  user_id?: string;
  count?: number;
  daily_count?: number;
  reset_time: Date;
  daily_reset_time: Date;
  blocked?: boolean;
  block_expires_at?: Date;
  tier?: UserTier;
  endpoint?: string;
  ip_address?: string;
}

// View interfaces for common queries

export interface ActiveSession extends Session {
  email: string;
  tier: UserTier;
  display_name?: string;
  device_name?: string;
  trusted?: boolean;
}

export interface UserSecuritySummary {
  id: string;
  email: string;
  tier: UserTier;
  status: UserStatus;
  active_sessions: number;
  passkey_count: number;
  device_count: number;
  unused_backup_codes: number;
  last_login_at?: Date;
  login_count: number;
}

// Database query interfaces

export interface UserFilters {
  tier?: UserTier;
  status?: UserStatus;
  organization_id?: string;
  email_verified?: boolean;
  created_after?: Date;
  created_before?: Date;
  last_login_after?: Date;
  last_login_before?: Date;
}

export interface SessionFilters {
  user_id?: string;
  status?: SessionStatus;
  device_handle_id?: string;
  ip_address?: string;
  expires_after?: Date;
  expires_before?: Date;
  created_after?: Date;
  created_before?: Date;
}

export interface SecurityEventFilters {
  user_id?: string;
  event_type?: SecurityEventType;
  event_category?: string;
  severity?: 'info' | 'warning' | 'error' | 'critical';
  result?: 'success' | 'failure' | 'blocked';
  ip_address?: string;
  risk_score_min?: number;
  risk_score_max?: number;
  event_after?: Date;
  event_before?: Date;
}

// Pagination interface
export interface PaginationOptions {
  limit?: number;
  offset?: number;
  order_by?: string;
  order_direction?: 'ASC' | 'DESC';
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// Database operation result types
export interface DatabaseResult<T> {
  success: boolean;
  data?: T;
  error?: string;
  affected_rows?: number;
}

// Connection configuration
export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl?: boolean;
  pool_size?: number;
  connection_timeout?: number;
  idle_timeout?: number;
  max_lifetime?: number;
}

// Transaction context
export interface TransactionContext {
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  execute<T>(query: string, params?: any[]): Promise<T>;
}

// Database interface abstract class (to be implemented by specific ORM/driver)
export abstract class DatabaseInterface {
  abstract connect(config: DatabaseConfig): Promise<void>;
  abstract disconnect(): Promise<void>;
  abstract transaction<T>(fn: (tx: TransactionContext) => Promise<T>): Promise<T>;

  // User operations
  abstract createUser(input: CreateUserInput): Promise<DatabaseResult<User>>;
  abstract getUserById(id: string): Promise<DatabaseResult<User>>;
  abstract getUserByEmail(email: string): Promise<DatabaseResult<User>>;
  abstract updateUser(id: string, input: UpdateUserInput): Promise<DatabaseResult<User>>;
  abstract deleteUser(id: string): Promise<DatabaseResult<void>>;
  abstract listUsers(filters?: UserFilters, pagination?: PaginationOptions): Promise<DatabaseResult<PaginatedResult<User>>>;

  // Session operations
  abstract createSession(input: CreateSessionInput): Promise<DatabaseResult<Session>>;
  abstract getSessionByToken(tokenHash: string): Promise<DatabaseResult<Session>>;
  abstract updateSession(id: string, updates: Partial<Session>): Promise<DatabaseResult<Session>>;
  abstract revokeSession(id: string, reason?: string): Promise<DatabaseResult<void>>;
  abstract listUserSessions(userId: string): Promise<DatabaseResult<Session[]>>;
  abstract cleanupExpiredSessions(): Promise<DatabaseResult<number>>;

  // Passkey operations
  abstract createPasskey(input: CreatePasskeyInput): Promise<DatabaseResult<Passkey>>;
  abstract getPasskeyByCredentialId(credentialId: string): Promise<DatabaseResult<Passkey>>;
  abstract listUserPasskeys(userId: string): Promise<DatabaseResult<Passkey[]>>;
  abstract updatePasskey(id: string, updates: Partial<Passkey>): Promise<DatabaseResult<Passkey>>;
  abstract deletePasskey(id: string): Promise<DatabaseResult<void>>;

  // Refresh token operations
  abstract createRefreshToken(input: CreateRefreshTokenInput): Promise<DatabaseResult<RefreshToken>>;
  abstract getRefreshTokenByHash(tokenHash: string): Promise<DatabaseResult<RefreshToken>>;
  abstract revokeRefreshTokenFamily(familyId: string, reason?: string): Promise<DatabaseResult<number>>;
  abstract cleanupExpiredRefreshTokens(): Promise<DatabaseResult<number>>;

  // Device handle operations
  abstract createDeviceHandle(input: CreateDeviceHandleInput): Promise<DatabaseResult<DeviceHandle>>;
  abstract getDeviceHandleByDeviceId(deviceId: string): Promise<DatabaseResult<DeviceHandle>>;
  abstract listUserDeviceHandles(userId: string): Promise<DatabaseResult<DeviceHandle[]>>;
  abstract updateDeviceHandle(id: string, updates: Partial<DeviceHandle>): Promise<DatabaseResult<DeviceHandle>>;
  abstract deleteDeviceHandle(id: string): Promise<DatabaseResult<void>>;

  // Backup code operations
  abstract createBackupCodes(userId: string, codes: CreateBackupCodeInput[]): Promise<DatabaseResult<BackupCode[]>>;
  abstract getBackupCodeByHash(codeHash: string): Promise<DatabaseResult<BackupCode>>;
  abstract markBackupCodeUsed(id: string, ipAddress?: string, userAgent?: string): Promise<DatabaseResult<void>>;
  abstract listUserBackupCodes(userId: string, unusedOnly?: boolean): Promise<DatabaseResult<BackupCode[]>>;

  // Security event operations
  abstract createSecurityEvent(input: CreateSecurityEventInput): Promise<DatabaseResult<SecurityEvent>>;
  abstract listSecurityEvents(filters?: SecurityEventFilters, pagination?: PaginationOptions): Promise<DatabaseResult<PaginatedResult<SecurityEvent>>>;
  abstract cleanupExpiredSecurityEvents(): Promise<DatabaseResult<number>>;

  // Email verification token operations
  abstract createEmailVerificationToken(input: CreateEmailVerificationTokenInput): Promise<DatabaseResult<EmailVerificationToken>>;
  abstract getEmailVerificationTokenByHash(tokenHash: string): Promise<DatabaseResult<EmailVerificationToken>>;
  abstract markEmailVerificationTokenUsed(id: string): Promise<DatabaseResult<void>>;

  // Rate limiting operations
  abstract getRateLimitEntry(keyHash: string): Promise<DatabaseResult<RateLimitEntry>>;
  abstract updateRateLimitEntry(keyHash: string, updates: Partial<RateLimitEntry>): Promise<DatabaseResult<RateLimitEntry>>;
  abstract cleanupExpiredRateLimitEntries(): Promise<DatabaseResult<number>>;

  // View operations
  abstract getActiveSessionsForUser(userId: string): Promise<DatabaseResult<ActiveSession[]>>;
  abstract getUserSecuritySummary(userId: string): Promise<DatabaseResult<UserSecuritySummary>>;

  // Utility operations
  abstract healthCheck(): Promise<DatabaseResult<{ status: string; timestamp: Date }>>;
  abstract runCleanupTasks(): Promise<DatabaseResult<{ cleaned: number }>>;
}

export default DatabaseInterface;
