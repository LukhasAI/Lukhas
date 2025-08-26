/**
 * ΛiD Authentication System - Scope Management
 *
 * Tier-based authorization with deny-by-default security
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import { UserTier, AuthScope, Permission, Role } from '../types/auth.types';

/**
 * Authentication tiers aligned with LUKHAS access levels
 */
export enum Tier {
  T1_EXPLORER = 'T1',    // Anonymous, docs, demos
  T2_BUILDER = 'T2',     // Personal projects, API read
  T3_STUDIO = 'T3',      // Teams, org RBAC
  T4_ENTERPRISE = 'T4',  // SSO/SLA, governance, export
  T5_CORE_TEAM = 'T5'    // Internal, SSO+SCIM required
}

/**
 * Comprehensive scope definitions for LUKHAS ecosystem
 */
export enum Scope {
  // MATRIZ Core Access
  'matriz:read' = 'matriz:read',
  'matriz:write' = 'matriz:write',
  'matriz:admin' = 'matriz:admin',

  // Identity Management
  'identity:read' = 'identity:read',
  'identity:write' = 'identity:write',
  'identity:admin' = 'identity:admin',
  'identity:impersonate' = 'identity:impersonate',

  // Orchestration & AI
  'orchestrator:run' = 'orchestrator:run',
  'orchestrator:debug' = 'orchestrator:debug',
  'orchestrator:admin' = 'orchestrator:admin',

  // API Management
  'api:keys:read' = 'api:keys:read',
  'api:keys:write' = 'api:keys:write',
  'api:keys:delete' = 'api:keys:delete',
  'api:keys:admin' = 'api:keys:admin',

  // Organization Management
  'org:read' = 'org:read',
  'org:settings' = 'org:settings',
  'org:members' = 'org:members',
  'org:admin' = 'org:admin',

  // Billing & Commerce
  'billing:read' = 'billing:read',
  'billing:manage' = 'billing:manage',
  'billing:admin' = 'billing:admin',

  // Consciousness & Memory Systems
  'consciousness:read' = 'consciousness:read',
  'consciousness:write' = 'consciousness:write',
  'consciousness:debug' = 'consciousness:debug',
  'memory:read' = 'memory:read',
  'memory:write' = 'memory:write',
  'memory:admin' = 'memory:admin',

  // Guardian & Ethics
  'guardian:read' = 'guardian:read',
  'guardian:configure' = 'guardian:configure',
  'guardian:override' = 'guardian:override',

  // System Administration
  'system:monitor' = 'system:monitor',
  'system:admin' = 'system:admin',
  'system:emergency' = 'system:emergency'
}

/**
 * Role-based access control definitions
 */
export enum Role {
  OWNER = 'owner',
  ADMIN = 'admin',
  DEVELOPER = 'developer',
  ANALYST = 'analyst',
  VIEWER = 'viewer'
}

/**
 * Tier envelope configurations - defines scope boundaries per tier
 */
export const TIER_ENVELOPES: Record<Tier, AuthScope[]> = {
  [Tier.T1_EXPLORER]: [
    Scope['matriz:read'],
    Scope['identity:read'],
    Scope['consciousness:read'],
    Scope['guardian:read']
  ],

  [Tier.T2_BUILDER]: [
    Scope['matriz:read'],
    Scope['matriz:write'],
    Scope['identity:read'],
    Scope['identity:write'],
    Scope['api:keys:read'],
    Scope['api:keys:write'],
    Scope['orchestrator:run'],
    Scope['consciousness:read'],
    Scope['consciousness:write'],
    Scope['memory:read'],
    Scope['memory:write'],
    Scope['guardian:read']
  ],

  [Tier.T3_STUDIO]: [
    Scope['matriz:read'],
    Scope['matriz:write'],
    Scope['identity:read'],
    Scope['identity:write'],
    Scope['api:keys:read'],
    Scope['api:keys:write'],
    Scope['api:keys:delete'],
    Scope['orchestrator:run'],
    Scope['orchestrator:debug'],
    Scope['consciousness:read'],
    Scope['consciousness:write'],
    Scope['consciousness:debug'],
    Scope['memory:read'],
    Scope['memory:write'],
    Scope['org:read'],
    Scope['org:settings'],
    Scope['org:members'],
    Scope['billing:read'],
    Scope['guardian:read'],
    Scope['guardian:configure'],
    Scope['system:monitor']
  ],

  [Tier.T4_ENTERPRISE]: [
    Scope['matriz:read'],
    Scope['matriz:write'],
    Scope['matriz:admin'],
    Scope['identity:read'],
    Scope['identity:write'],
    Scope['identity:admin'],
    Scope['api:keys:read'],
    Scope['api:keys:write'],
    Scope['api:keys:delete'],
    Scope['api:keys:admin'],
    Scope['orchestrator:run'],
    Scope['orchestrator:debug'],
    Scope['orchestrator:admin'],
    Scope['consciousness:read'],
    Scope['consciousness:write'],
    Scope['consciousness:debug'],
    Scope['memory:read'],
    Scope['memory:write'],
    Scope['memory:admin'],
    Scope['org:read'],
    Scope['org:settings'],
    Scope['org:members'],
    Scope['org:admin'],
    Scope['billing:read'],
    Scope['billing:manage'],
    Scope['guardian:read'],
    Scope['guardian:configure'],
    Scope['guardian:override'],
    Scope['system:monitor'],
    Scope['system:admin']
  ],

  [Tier.T5_CORE_TEAM]: [
    ...Object.values(Scope) // All scopes available
  ]
};

/**
 * Role-based scope mappings
 */
export const ROLE_SCOPES: Record<Role, AuthScope[]> = {
  [Role.VIEWER]: [
    Scope['matriz:read'],
    Scope['identity:read'],
    Scope['consciousness:read'],
    Scope['memory:read'],
    Scope['org:read'],
    Scope['billing:read'],
    Scope['guardian:read'],
    Scope['system:monitor']
  ],

  [Role.ANALYST]: [
    ...ROLE_SCOPES[Role.VIEWER],
    Scope['orchestrator:run'],
    Scope['consciousness:debug'],
    Scope['guardian:configure']
  ],

  [Role.DEVELOPER]: [
    ...ROLE_SCOPES[Role.ANALYST],
    Scope['matriz:write'],
    Scope['identity:write'],
    Scope['api:keys:read'],
    Scope['api:keys:write'],
    Scope['consciousness:write'],
    Scope['memory:write'],
    Scope['orchestrator:debug']
  ],

  [Role.ADMIN]: [
    ...ROLE_SCOPES[Role.DEVELOPER],
    Scope['identity:admin'],
    Scope['api:keys:delete'],
    Scope['api:keys:admin'],
    Scope['orchestrator:admin'],
    Scope['memory:admin'],
    Scope['org:settings'],
    Scope['org:members'],
    Scope['billing:manage'],
    Scope['guardian:override'],
    Scope['system:admin']
  ],

  [Role.OWNER]: [
    ...Object.values(Scope) // All scopes for owners
  ]
};

/**
 * Scope hierarchy for inheritance resolution
 */
export const SCOPE_HIERARCHY: Record<AuthScope, AuthScope[]> = {
  // MATRIZ hierarchy
  [Scope['matriz:admin']]: [Scope['matriz:write'], Scope['matriz:read']],
  [Scope['matriz:write']]: [Scope['matriz:read']],

  // Identity hierarchy
  [Scope['identity:admin']]: [Scope['identity:write'], Scope['identity:read']],
  [Scope['identity:write']]: [Scope['identity:read']],

  // API keys hierarchy
  [Scope['api:keys:admin']]: [Scope['api:keys:delete'], Scope['api:keys:write'], Scope['api:keys:read']],
  [Scope['api:keys:delete']]: [Scope['api:keys:write'], Scope['api:keys:read']],
  [Scope['api:keys:write']]: [Scope['api:keys:read']],

  // Organization hierarchy
  [Scope['org:admin']]: [Scope['org:members'], Scope['org:settings'], Scope['org:read']],
  [Scope['org:members']]: [Scope['org:read']],
  [Scope['org:settings']]: [Scope['org:read']],

  // Billing hierarchy
  [Scope['billing:admin']]: [Scope['billing:manage'], Scope['billing:read']],
  [Scope['billing:manage']]: [Scope['billing:read']],

  // Consciousness hierarchy
  [Scope['consciousness:debug']]: [Scope['consciousness:write'], Scope['consciousness:read']],
  [Scope['consciousness:write']]: [Scope['consciousness:read']],

  // Memory hierarchy
  [Scope['memory:admin']]: [Scope['memory:write'], Scope['memory:read']],
  [Scope['memory:write']]: [Scope['memory:read']],

  // Guardian hierarchy
  [Scope['guardian:override']]: [Scope['guardian:configure'], Scope['guardian:read']],
  [Scope['guardian:configure']]: [Scope['guardian:read']],

  // Orchestrator hierarchy
  [Scope['orchestrator:admin']]: [Scope['orchestrator:debug'], Scope['orchestrator:run']],
  [Scope['orchestrator:debug']]: [Scope['orchestrator:run']],

  // System hierarchy
  [Scope['system:emergency']]: [Scope['system:admin'], Scope['system:monitor']],
  [Scope['system:admin']]: [Scope['system:monitor']]
};

/**
 * Permission context for granular access control
 */
export interface PermissionContext {
  resource?: string;
  action?: string;
  conditions?: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * Authorization result with detailed feedback
 */
export interface AuthorizationResult {
  allowed: boolean;
  reason?: string;
  requiredScope?: AuthScope;
  missingPermissions?: Permission[];
  metadata?: Record<string, any>;
}

/**
 * Core authorization function - implements deny-by-default security
 *
 * @param userTier - User's current tier level
 * @param userRole - User's role within organization
 * @param userScopes - Explicitly granted scopes
 * @param requiredScope - Scope required for the operation
 * @param context - Additional permission context
 * @returns Authorization decision with detailed reasoning
 */
export function hasScope(
  userTier: UserTier,
  userRole: Role,
  userScopes: AuthScope[],
  requiredScope: AuthScope,
  context?: PermissionContext
): AuthorizationResult {
  // Deny by default
  let result: AuthorizationResult = {
    allowed: false,
    reason: 'Access denied by default policy',
    requiredScope
  };

  try {
    // 1. Check if scope exists in tier envelope
    const tierScopes = TIER_ENVELOPES[userTier as Tier];
    if (!tierScopes.includes(requiredScope)) {
      return {
        ...result,
        reason: `Scope '${requiredScope}' not available in tier ${userTier}`
      };
    }

    // 2. Check role-based permissions
    const roleScopes = ROLE_SCOPES[userRole];
    if (!roleScopes.includes(requiredScope)) {
      return {
        ...result,
        reason: `Scope '${requiredScope}' not granted to role '${userRole}'`
      };
    }

    // 3. Check explicit user scopes
    if (!userScopes.includes(requiredScope)) {
      // Check scope hierarchy for inherited permissions
      const inheritedScopes = getInheritedScopes(userScopes);
      if (!inheritedScopes.includes(requiredScope)) {
        return {
          ...result,
          reason: `User does not have scope '${requiredScope}' or inherited permissions`
        };
      }
    }

    // 4. Apply contextual conditions if present
    if (context?.conditions) {
      const conditionResult = evaluateConditions(context.conditions, {
        userTier,
        userRole,
        userScopes,
        requiredScope
      });

      if (!conditionResult.allowed) {
        return {
          ...result,
          reason: `Contextual condition failed: ${conditionResult.reason}`
        };
      }
    }

    // 5. Grant access
    return {
      allowed: true,
      metadata: {
        tier: userTier,
        role: userRole,
        grantedVia: userScopes.includes(requiredScope) ? 'explicit' : 'inherited',
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    return {
      ...result,
      reason: `Authorization check failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    };
  }
}

/**
 * Get all inherited scopes based on hierarchy
 */
export function getInheritedScopes(explicitScopes: AuthScope[]): AuthScope[] {
  const inherited = new Set<AuthScope>(explicitScopes);

  for (const scope of explicitScopes) {
    const childScopes = SCOPE_HIERARCHY[scope] || [];
    childScopes.forEach(child => inherited.add(child));
  }

  return Array.from(inherited);
}

/**
 * Evaluate conditional access rules
 */
function evaluateConditions(
  conditions: Record<string, any>,
  context: {
    userTier: UserTier;
    userRole: Role;
    userScopes: AuthScope[];
    requiredScope: AuthScope;
  }
): { allowed: boolean; reason?: string } {
  // Time-based conditions
  if (conditions.timeWindow) {
    const now = new Date();
    const start = new Date(conditions.timeWindow.start);
    const end = new Date(conditions.timeWindow.end);

    if (now < start || now > end) {
      return { allowed: false, reason: 'Outside allowed time window' };
    }
  }

  // IP-based conditions
  if (conditions.allowedIPs && conditions.clientIP) {
    if (!conditions.allowedIPs.includes(conditions.clientIP)) {
      return { allowed: false, reason: 'IP address not in allowed list' };
    }
  }

  // Resource-specific conditions
  if (conditions.resourceOwner && conditions.requestingUser) {
    if (conditions.resourceOwner !== conditions.requestingUser &&
        context.userRole !== Role.ADMIN &&
        context.userRole !== Role.OWNER) {
      return { allowed: false, reason: 'Insufficient permissions for resource' };
    }
  }

  // Rate limiting conditions
  if (conditions.rateLimitExceeded) {
    return { allowed: false, reason: 'Rate limit exceeded' };
  }

  return { allowed: true };
}

/**
 * Validate scope format and existence
 */
export function isValidScope(scope: string): scope is AuthScope {
  return Object.values(Scope).includes(scope as AuthScope);
}

/**
 * Get all available scopes for a tier
 */
export function getAvailableScopes(tier: UserTier): AuthScope[] {
  return TIER_ENVELOPES[tier as Tier] || [];
}

/**
 * Get all scopes for a role
 */
export function getRoleScopes(role: Role): AuthScope[] {
  return ROLE_SCOPES[role] || [];
}

/**
 * Check if user can be granted a scope based on tier and role
 */
export function canGrantScope(
  userTier: UserTier,
  userRole: Role,
  scope: AuthScope
): boolean {
  const tierScopes = getAvailableScopes(userTier);
  const roleScopes = getRoleScopes(userRole);

  return tierScopes.includes(scope) && roleScopes.includes(scope);
}

/**
 * Audit helper to log authorization decisions
 */
export function logAuthorizationDecision(
  userId: string,
  result: AuthorizationResult,
  context?: PermissionContext
): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    userId,
    allowed: result.allowed,
    reason: result.reason,
    requiredScope: result.requiredScope,
    context: context || {},
    metadata: result.metadata || {}
  };

  // In production, this would log to a secure audit system
  console.log('[ΛiD AUTH AUDIT]', JSON.stringify(logEntry));
}

/**
 * Emergency override for critical system operations
 * Requires special authorization and creates audit trail
 */
export function emergencyOverride(
  adminUserId: string,
  targetUserId: string,
  requiredScope: AuthScope,
  justification: string,
  authToken: string
): AuthorizationResult {
  // Validate emergency override token (implementation depends on security setup)
  if (!validateEmergencyToken(authToken)) {
    return {
      allowed: false,
      reason: 'Invalid emergency override token'
    };
  }

  // Create comprehensive audit trail
  const auditEntry = {
    type: 'EMERGENCY_OVERRIDE',
    timestamp: new Date().toISOString(),
    adminUserId,
    targetUserId,
    requiredScope,
    justification,
    tokenHash: hashToken(authToken)
  };

  // Log to high-security audit system
  console.log('[ΛiD EMERGENCY OVERRIDE]', JSON.stringify(auditEntry));

  return {
    allowed: true,
    metadata: {
      overrideType: 'emergency',
      adminUserId,
      justification,
      auditId: generateAuditId()
    }
  };
}

// Helper functions for emergency override
function validateEmergencyToken(token: string): boolean {
  // Implementation would validate against secure token store
  return token.length > 32 && token.includes('EMERGENCY_');
}

function hashToken(token: string): string {
  // Implementation would use proper crypto hashing
  return `hash_${token.substring(0, 8)}...`;
}

function generateAuditId(): string {
  return `audit_${Date.now()}_${Math.random().toString(36).substring(2)}`;
}
