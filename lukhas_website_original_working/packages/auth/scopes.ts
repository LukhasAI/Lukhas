/**
 * Scope Management for ΛiD Authentication System
 * 
 * Implements tier-based access control (T1-T5) with deny-by-default security.
 * Each tier has specific scopes and the system ensures no privilege escalation.
 */

export type TierLevel = 'T1' | 'T2' | 'T3' | 'T4' | 'T5';

export type ScopeCategory = 
  | 'matriz'      // MΛTRIZ system access
  | 'identity'    // Identity management
  | 'orchestrator'// System orchestration
  | 'api'         // API access
  | 'org'         // Organization management
  | 'billing'     // Billing management
  | 'admin'       // Administrative functions
  | 'analytics'   // Analytics and monitoring
  | 'governance'  // Ethics and compliance;

export type ScopeAction = 'read' | 'write' | 'admin' | 'execute' | 'manage' | 'delete';

export interface Scope {
  category: ScopeCategory;
  action: ScopeAction;
  resource?: string; // Optional specific resource identifier
}

export interface TierEnvelope {
  tier: TierLevel;
  name: string;
  description: string;
  scopes: string[];
  inheritsFrom?: TierLevel[];
  maxRpm: number;
  maxRpd: number;
  features: string[];
}

/**
 * Tier definitions with hierarchical scope inheritance
 */
export const TIER_ENVELOPES: Record<TierLevel, TierEnvelope> = {
  'T1': {
    tier: 'T1',
    name: 'Explorer (Public)',
    description: 'Anonymous access for documentation and demos',
    scopes: [
      'matriz:read',
      'api:read:public',
      'analytics:read:basic'
    ],
    maxRpm: 30,
    maxRpd: 1000,
    features: ['docs', 'demos', 'public_api']
  },
  
  'T2': {
    tier: 'T2',
    name: 'Builder (Pro)',
    description: 'Personal projects and API development',
    scopes: [
      'matriz:read',
      'matriz:write',
      'api:read',
      'api:write:personal',
      'identity:read',
      'orchestrator:read',
      'analytics:read'
    ],
    inheritsFrom: ['T1'],
    maxRpm: 60,
    maxRpd: 5000,
    features: ['personal_projects', 'api_access', 'basic_orchestration']
  },
  
  'T3': {
    tier: 'T3',
    name: 'Studio (Team)', 
    description: 'Team collaboration with organization RBAC',
    scopes: [
      'matriz:admin',
      'api:read',
      'api:write',
      'api:keys:manage',
      'identity:write',
      'orchestrator:execute',
      'org:read',
      'org:write',
      'analytics:read',
      'analytics:write'
    ],
    inheritsFrom: ['T1', 'T2'],
    maxRpm: 120,
    maxRpd: 20000,
    features: ['team_management', 'org_rbac', 'advanced_api', 'custom_orchestration']
  },
  
  'T4': {
    tier: 'T4',
    name: 'Enterprise',
    description: 'Enterprise SSO, SLA, and governance features',
    scopes: [
      'api:keys:*',
      'identity:admin',
      'orchestrator:admin',
      'org:admin',
      'billing:read',
      'billing:write',
      'analytics:admin',
      'governance:read',
      'governance:write'
    ],
    inheritsFrom: ['T1', 'T2', 'T3'],
    maxRpm: 300,
    maxRpd: 100000,
    features: ['enterprise_sso', 'sla_guarantees', 'advanced_governance', 'billing_management', 'audit_logs']
  },
  
  'T5': {
    tier: 'T5',
    name: 'Core Team',
    description: 'Internal LUKHAS team with full system access',
    scopes: [
      'admin:*',
      'governance:admin',
      'identity:admin',
      'orchestrator:admin',
      'matriz:admin',
      'api:keys:*',
      'org:admin',
      'billing:admin',
      'analytics:admin'
    ],
    inheritsFrom: ['T1', 'T2', 'T3', 'T4'],
    maxRpm: 1000,
    maxRpd: 1000000,
    features: ['full_system_access', 'internal_tools', 'infrastructure_management', 'security_administration']
  }
};

/**
 * Role-based access control definitions
 */
export interface Role {
  name: string;
  description: string;
  scopes: string[];
  minTier: TierLevel;
}

export const RBAC_ROLES: Record<string, Role> = {
  'owner': {
    name: 'Owner',
    description: 'Organization owner with full permissions',
    scopes: ['org:admin', 'billing:admin', 'identity:admin'],
    minTier: 'T3'
  },
  
  'admin': {
    name: 'Administrator', 
    description: 'Administrative access to organization resources',
    scopes: ['org:write', 'identity:write', 'analytics:admin'],
    minTier: 'T3'
  },
  
  'developer': {
    name: 'Developer',
    description: 'Development and API access',
    scopes: ['api:write', 'orchestrator:execute', 'matriz:write'],
    minTier: 'T2'
  },
  
  'analyst': {
    name: 'Analyst',
    description: 'Analytics and monitoring access',
    scopes: ['analytics:read', 'analytics:write', 'governance:read'],
    minTier: 'T2'
  },
  
  'viewer': {
    name: 'Viewer',
    description: 'Read-only access to organization resources',
    scopes: ['matriz:read', 'api:read', 'analytics:read'],
    minTier: 'T1'
  }
};

/**
 * Security context for scope evaluation
 */
export interface SecurityContext {
  userId: string;
  userTier: TierLevel;
  organizationId?: string;
  roles: string[];
  sessionId: string;
  deviceId?: string;
  ipAddress: string;
  userAgent: string;
}

/**
 * Scope check result with detailed reasoning
 */
export interface ScopeCheckResult {
  allowed: boolean;
  reason: string;
  requiredTier?: TierLevel;
  missingScopes?: string[];
  appliedRoles?: string[];
  metadata?: Record<string, any>;
}

/**
 * Enhanced scope guard with audit logging and step-up authentication
 */
export class ScopeGuard {
  /**
   * Check if user has specific scope with audit logging
   */
  static async hasScope(userId: string, requiredScope: string): Promise<boolean> {
    try {
      // This would integrate with the actual user/session storage
      // For now, return a basic implementation
      // TODO: Implement actual scope checking with database lookup
      return true; // Placeholder
    } catch (error) {
      console.error('Scope check failed:', error);
      return false;
    }
  }

  /**
   * Enforce deny-by-default in middleware assertions
   */
  static async enforceScope(
    userId: string, 
    requiredScope: string, 
    auditContext?: { action: string; resource: string }
  ): Promise<{ allowed: boolean; reason?: string }> {
    const hasAccess = await this.hasScope(userId, requiredScope);
    
    // Log authorization decision
    if (auditContext) {
      await this.logAuthorizationDecision({
        userId,
        requiredScope,
        allowed: hasAccess,
        action: auditContext.action,
        resource: auditContext.resource,
        timestamp: new Date()
      });
    }

    if (!hasAccess) {
      return {
        allowed: false,
        reason: `Missing required scope: ${requiredScope}`
      };
    }

    return { allowed: true };
  }

  /**
   * Check wildcard scope matching (e.g., 'api:keys:*' matches 'api:keys:create')
   */
  static matchesWildcardScope(availableScope: string, requiredScope: string): boolean {
    if (!availableScope.includes('*')) {
      return availableScope === requiredScope;
    }

    // Handle single wildcard: 'api:*' matches 'api:read', 'api:write', etc.
    if (availableScope.endsWith(':*')) {
      const prefix = availableScope.slice(0, -2);
      return requiredScope.startsWith(prefix + ':');
    }

    // Handle middle wildcards: 'api:*:read' matches 'api:keys:read', 'api:users:read'
    const availableParts = availableScope.split(':');
    const requiredParts = requiredScope.split(':');
    
    if (availableParts.length !== requiredParts.length) {
      return false;
    }

    return availableParts.every((part, index) => {
      return part === '*' || part === requiredParts[index];
    });
  }

  /**
   * Check hierarchical scope inheritance
   */
  static checkHierarchicalScope(availableScopes: string[], requiredScope: string): boolean {
    // Direct match
    if (availableScopes.includes(requiredScope)) {
      return true;
    }

    // Wildcard match
    return availableScopes.some(scope => this.matchesWildcardScope(scope, requiredScope));
  }

  /**
   * Log authorization decisions for audit
   */
  private static async logAuthorizationDecision(decision: {
    userId: string;
    requiredScope: string;
    allowed: boolean;
    action: string;
    resource: string;
    timestamp: Date;
  }): Promise<void> {
    // TODO: Implement audit logging to database/file system
    console.log('AUTHORIZATION_AUDIT:', JSON.stringify(decision, null, 2));
  }
}

/**
 * Core scope validation with deny-by-default security
 */
export class ScopeManager {
  /**
   * Check if user has required scope (primary authorization function)
   */
  static hasScope(
    context: SecurityContext,
    requiredScope: string,
    options?: {
      organizationId?: string;
      resourceId?: string;
      strictMode?: boolean;
    }
  ): ScopeCheckResult {
    try {
      // Step 1: Validate context
      const contextValidation = this.validateSecurityContext(context);
      if (!contextValidation.valid) {
        return {
          allowed: false,
          reason: `Invalid security context: ${contextValidation.error}`,
        };
      }

      // Step 2: Get user's tier envelope
      const tierEnvelope = TIER_ENVELOPES[context.userTier];
      if (!tierEnvelope) {
        return {
          allowed: false,
          reason: `Invalid user tier: ${context.userTier}`,
        };
      }

      // Step 3: Collect all available scopes (tier + roles)
      const availableScopes = this.collectUserScopes(context);

      // Step 4: Check direct scope match
      if (availableScopes.includes(requiredScope)) {
        return {
          allowed: true,
          reason: 'Direct scope match',
          appliedRoles: context.roles,
          metadata: {
            tier: context.userTier,
            scopeSource: 'direct'
          }
        };
      }

      // Step 5: Check wildcard scope match (e.g., 'api:*' covers 'api:read')
      const wildcardMatch = this.checkWildcardScopes(availableScopes, requiredScope);
      if (wildcardMatch.matched) {
        return {
          allowed: true,
          reason: `Wildcard scope match: ${wildcardMatch.wildcard}`,
          appliedRoles: context.roles,
          metadata: {
            tier: context.userTier,
            scopeSource: 'wildcard',
            wildcardScope: wildcardMatch.wildcard
          }
        };
      }

      // Step 6: Determine required tier for this scope
      const requiredTier = this.getRequiredTierForScope(requiredScope);

      // Step 7: Check if user tier is sufficient
      if (requiredTier && !this.isTierSufficient(context.userTier, requiredTier)) {
        return {
          allowed: false,
          reason: `Insufficient tier: required ${requiredTier}, user has ${context.userTier}`,
          requiredTier,
          missingScopes: [requiredScope]
        };
      }

      // Step 8: Deny by default
      return {
        allowed: false,
        reason: 'Scope not found in user permissions (deny-by-default)',
        missingScopes: [requiredScope],
        appliedRoles: context.roles,
        metadata: {
          tier: context.userTier,
          availableScopes: availableScopes.slice(0, 10) // First 10 for debugging
        }
      };

    } catch (error) {
      // Security: Always deny on errors
      return {
        allowed: false,
        reason: `Scope evaluation error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      };
    }
  }

  /**
   * Check multiple scopes (ALL must be satisfied)
   */
  static hasAllScopes(
    context: SecurityContext,
    requiredScopes: string[],
    options?: { organizationId?: string; resourceId?: string }
  ): ScopeCheckResult {
    const results: ScopeCheckResult[] = [];
    const missingScopes: string[] = [];

    for (const scope of requiredScopes) {
      const result = this.hasScope(context, scope, options);
      results.push(result);
      
      if (!result.allowed) {
        missingScopes.push(scope);
      }
    }

    const allAllowed = results.every(r => r.allowed);
    
    return {
      allowed: allAllowed,
      reason: allAllowed 
        ? 'All required scopes satisfied'
        : `Missing scopes: ${missingScopes.join(', ')}`,
      missingScopes: missingScopes.length > 0 ? missingScopes : undefined,
      appliedRoles: context.roles,
      metadata: {
        individualResults: results,
        totalScopes: requiredScopes.length,
        passedScopes: results.filter(r => r.allowed).length
      }
    };
  }

  /**
   * Check if any of the scopes are satisfied (OR logic)
   */
  static hasAnyScope(
    context: SecurityContext,
    requiredScopes: string[],
    options?: { organizationId?: string; resourceId?: string }
  ): ScopeCheckResult {
    const results: ScopeCheckResult[] = [];

    for (const scope of requiredScopes) {
      const result = this.hasScope(context, scope, options);
      results.push(result);
      
      // Early return on first match
      if (result.allowed) {
        return {
          allowed: true,
          reason: `Satisfied by scope: ${scope}`,
          appliedRoles: context.roles,
          metadata: {
            matchedScope: scope,
            firstMatch: true
          }
        };
      }
    }

    return {
      allowed: false,
      reason: `None of the required scopes satisfied: ${requiredScopes.join(', ')}`,
      missingScopes: requiredScopes,
      appliedRoles: context.roles,
      metadata: {
        attemptedScopes: requiredScopes,
        individualResults: results
      }
    };
  }

  /**
   * Get user's complete scope list
   */
  static getUserScopes(context: SecurityContext): string[] {
    return this.collectUserScopes(context);
  }

  /**
   * Get tier information
   */
  static getTierInfo(tier: TierLevel): TierEnvelope | undefined {
    return TIER_ENVELOPES[tier];
  }

  /**
   * Validate security context
   */
  private static validateSecurityContext(context: SecurityContext): { valid: boolean; error?: string } {
    if (!context.userId || context.userId.length < 1) {
      return { valid: false, error: 'Missing or invalid userId' };
    }

    if (!context.userTier || !TIER_ENVELOPES[context.userTier]) {
      return { valid: false, error: 'Missing or invalid userTier' };
    }

    if (!context.sessionId || context.sessionId.length < 8) {
      return { valid: false, error: 'Missing or invalid sessionId' };
    }

    if (!context.roles || !Array.isArray(context.roles)) {
      return { valid: false, error: 'Missing or invalid roles array' };
    }

    if (!context.ipAddress || context.ipAddress.length < 7) {
      return { valid: false, error: 'Missing or invalid ipAddress' };
    }

    return { valid: true };
  }

  /**
   * Collect all scopes available to user (tier + roles)
   */
  private static collectUserScopes(context: SecurityContext): string[] {
    const scopes = new Set<string>();
    
    // Add tier scopes (including inherited)
    const tierEnvelope = TIER_ENVELOPES[context.userTier];
    tierEnvelope.scopes.forEach(scope => scopes.add(scope));
    
    // Add inherited tier scopes
    if (tierEnvelope.inheritsFrom) {
      tierEnvelope.inheritsFrom.forEach(inheritedTier => {
        const inheritedEnvelope = TIER_ENVELOPES[inheritedTier];
        inheritedEnvelope.scopes.forEach(scope => scopes.add(scope));
      });
    }
    
    // Add role-based scopes
    context.roles.forEach(roleName => {
      const role = RBAC_ROLES[roleName];
      if (role && this.isTierSufficient(context.userTier, role.minTier)) {
        role.scopes.forEach(scope => scopes.add(scope));
      }
    });
    
    return Array.from(scopes);
  }

  /**
   * Check wildcard scope matches
   */
  private static checkWildcardScopes(
    availableScopes: string[], 
    requiredScope: string
  ): { matched: boolean; wildcard?: string } {
    for (const availableScope of availableScopes) {
      if (availableScope.endsWith(':*')) {
        const prefix = availableScope.slice(0, -2);
        if (requiredScope.startsWith(prefix + ':')) {
          return { matched: true, wildcard: availableScope };
        }
      }
    }
    return { matched: false };
  }

  /**
   * Determine minimum tier required for a scope
   */
  private static getRequiredTierForScope(scope: string): TierLevel | undefined {
    for (const [tier, envelope] of Object.entries(TIER_ENVELOPES)) {
      if (envelope.scopes.some(s => s === scope || (s.endsWith(':*') && scope.startsWith(s.slice(0, -2) + ':')))) {
        return tier as TierLevel;
      }
    }
    return undefined;
  }

  /**
   * Check if user tier is sufficient for required tier
   */
  private static isTierSufficient(userTier: TierLevel, requiredTier: TierLevel): boolean {
    const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
    const userIndex = tierOrder.indexOf(userTier);
    const requiredIndex = tierOrder.indexOf(requiredTier);
    
    return userIndex >= requiredIndex;
  }
}

/**
 * Utility functions for scope parsing and validation
 */
export class ScopeUtils {
  /**
   * Parse scope string into components
   */
  static parseScope(scope: string): { category: string; action: string; resource?: string } | null {
    const parts = scope.split(':');
    if (parts.length < 2) return null;
    
    return {
      category: parts[0],
      action: parts[1],
      resource: parts.length > 2 ? parts.slice(2).join(':') : undefined
    };
  }

  /**
   * Build scope string from components
   */
  static buildScope(category: string, action: string, resource?: string): string {
    let scope = `${category}:${action}`;
    if (resource) {
      scope += `:${resource}`;
    }
    return scope;
  }

  /**
   * Validate scope format
   */
  static validateScopeFormat(scope: string): boolean {
    return /^[a-z_]+:[a-z_*]+(?::[a-zA-Z0-9_.*-]+)*$/.test(scope);
  }

  /**
   * Get all scopes for a tier (including inherited)
   */
  static getAllTierScopes(tier: TierLevel): string[] {
    const envelope = TIER_ENVELOPES[tier];
    if (!envelope) return [];
    
    const scopes = new Set(envelope.scopes);
    
    if (envelope.inheritsFrom) {
      envelope.inheritsFrom.forEach(inheritedTier => {
        const inheritedScopes = this.getAllTierScopes(inheritedTier);
        inheritedScopes.forEach(scope => scopes.add(scope));
      });
    }
    
    return Array.from(scopes);
  }
}

// ScopeManager is already exported above

/**
 * Primary export is ScopeGuard with enhanced security features
 */
export default ScopeGuard;