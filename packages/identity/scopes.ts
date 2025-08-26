/**
 * Identity Module Scopes - Extended Authorization System
 *
 * Comprehensive scope definitions for LUKHAS identity module including
 * ABAS, DAST, NIAS, Guardian, and Health monitoring systems.
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import type { UserTier } from '../auth/types/auth.types';

// =============================================================================
// EXTENDED SCOPE DEFINITIONS
// =============================================================================

/**
 * Extended authentication scopes for all LUKHAS modules
 */
export type ExtendedAuthScope =
  // Core Platform Scopes
  | 'docs:read'
  | 'app:read'
  | 'app:write'
  | 'api:read'
  | 'api:write'

  // MATRIZ Core Access
  | 'matriz:demo:read'
  | 'matriz:read'
  | 'matriz:write'
  | 'matriz:export'
  | 'matriz:admin'

  // NIAS (Neural Intelligence Amplification System)
  | 'nias:validate'
  | 'nias:replay'
  | 'nias:models:read'
  | 'nias:models:write'
  | 'nias:models:train'
  | 'nias:models:deploy'
  | 'nias:inference:run'
  | 'nias:inference:batch'
  | 'nias:datasets:read'
  | 'nias:datasets:write'
  | 'nias:experiments:run'
  | 'nias:experiments:design'
  | 'nias:symbolic:reasoning'
  | 'nias:symbolic:validation'
  | 'nias:consciousness:bridge'
  | 'nias:dreams:synthesize'
  | 'nias:dreams:replay'
  | 'nias:research:experimental'

  // ABAS (Adaptive Behavior Analysis System)
  | 'abas:profiles:read'
  | 'abas:profiles:write'
  | 'abas:analytics:read'
  | 'abas:analytics:export'
  | 'abas:patterns:discover'
  | 'abas:patterns:train'
  | 'abas:insights:read'
  | 'abas:insights:share'
  | 'abas:experiments:run'
  | 'abas:experiments:manage'
  | 'abas:alerts:read'
  | 'abas:alerts:configure'
  | 'abas:privacy:configure'

  // DAST (Dynamic Application Service Topology)
  | 'dast:route'
  | 'dast:routes:read'
  | 'dast:routes:write'
  | 'dast:topology:discover'
  | 'dast:topology:visualize'
  | 'dast:load_balancing:read'
  | 'dast:load_balancing:write'
  | 'dast:health_checks:read'
  | 'dast:health_checks:write'
  | 'dast:scaling:read'
  | 'dast:scaling:configure'
  | 'dast:deployment:trigger'
  | 'dast:rollback:execute'
  | 'dast:analytics:advanced'

  // Orchestrator & AI
  | 'orchestrator:run'
  | 'orchestrator:debug'
  | 'orchestrator:admin'

  // API Management
  | 'api:keys:create'
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

  // Guardian & Ethics
  | 'guardian:read'
  | 'guardian:configure'
  | 'guardian:policies:read'
  | 'guardian:policies:write'
  | 'guardian:policies:approve'
  | 'guardian:policy:read'
  | 'guardian:ethics:evaluate'
  | 'guardian:compliance:check'
  | 'guardian:compliance:report'
  | 'guardian:violations:detect'
  | 'guardian:violations:resolve'
  | 'guardian:override'

  // Health & Monitoring
  | 'health:metrics:read'
  | 'health:metrics:export'
  | 'health:alerts:read'
  | 'health:alerts:configure'
  | 'health:dashboards:read'
  | 'health:dashboards:write'
  | 'health:logs:read'
  | 'health:performance:profile'
  | 'health:anomaly:detect'
  | 'health:remediation:auto'
  | 'health:sla:monitor'
  | 'health:observability:setup'

  // Identity & Authentication
  | 'identity:read'
  | 'identity:write'
  | 'identity:admin'
  | 'identity:impersonate'

  // System Administration
  | 'system:monitor'
  | 'system:admin'
  | 'system:emergency';

/**
 * Authentication tiers with extended access levels
 */
export enum IdentityTier {
  T1_EXPLORER = 'T1',      // Anonymous, docs, demos
  T2_BUILDER = 'T2',       // Personal projects, API read
  T3_STUDIO = 'T3',        // Teams, org RBAC, advanced features
  T4_ENTERPRISE = 'T4',    // SSO/SLA, governance, export
  T5_CORE_TEAM = 'T5'      // Internal, full admin access
}

/**
 * Extended tier envelope configurations with module-specific scopes
 */
export const EXTENDED_TIER_ENVELOPES: Record<IdentityTier, ExtendedAuthScope[]> = {
  [IdentityTier.T1_EXPLORER]: [
    // Basic read access
    'docs:read',
    'matriz:demo:read',
    'health:metrics:read',
    'guardian:read'
  ],

  [IdentityTier.T2_BUILDER]: [
    // T1 permissions plus basic operations
    'docs:read',
    'app:read',
    'api:read',
    'matriz:demo:read',
    'matriz:read',
    'nias:validate',
    'abas:profiles:read',
    'dast:routes:read',
    'health:metrics:read',
    'health:alerts:read',
    'guardian:read',
    'identity:read'
  ],

  [IdentityTier.T3_STUDIO]: [
    // T2 permissions plus advanced features
    'docs:read',
    'app:read',
    'app:write',
    'api:read',
    'api:keys:create',
    'matriz:read',
    'matriz:write',
    'nias:validate',
    'nias:replay',
    'nias:models:read',
    'nias:inference:run',
    'abas:profiles:read',
    'abas:profiles:write',
    'abas:analytics:read',
    'abas:patterns:discover',
    'abas:insights:read',
    'dast:route',
    'dast:routes:read',
    'dast:routes:write',
    'dast:topology:discover',
    'dast:topology:visualize',
    'orchestrator:run',
    'org:read',
    'health:metrics:read',
    'health:metrics:export',
    'health:alerts:read',
    'health:alerts:configure',
    'health:dashboards:read',
    'guardian:read',
    'guardian:configure',
    'guardian:policies:read',
    'identity:read',
    'identity:write'
  ],

  [IdentityTier.T4_ENTERPRISE]: [
    // T3 permissions plus enterprise features
    'docs:read',
    'app:read',
    'app:write',
    'api:read',
    'api:write',
    'api:keys:create',
    'api:keys:read',
    'api:keys:write',
    'matriz:read',
    'matriz:write',
    'matriz:export',
    'nias:validate',
    'nias:replay',
    'nias:models:read',
    'nias:models:write',
    'nias:models:train',
    'nias:inference:run',
    'nias:inference:batch',
    'nias:datasets:read',
    'nias:experiments:run',
    'abas:profiles:read',
    'abas:profiles:write',
    'abas:analytics:read',
    'abas:analytics:export',
    'abas:patterns:discover',
    'abas:patterns:train',
    'abas:insights:read',
    'abas:insights:share',
    'abas:experiments:run',
    'abas:alerts:read',
    'abas:alerts:configure',
    'dast:route',
    'dast:routes:read',
    'dast:routes:write',
    'dast:topology:discover',
    'dast:topology:visualize',
    'dast:load_balancing:read',
    'dast:load_balancing:write',
    'dast:health_checks:read',
    'dast:health_checks:write',
    'dast:scaling:read',
    'dast:scaling:configure',
    'orchestrator:run',
    'orchestrator:debug',
    'org:read',
    'org:settings',
    'billing:read',
    'billing:manage',
    'health:metrics:read',
    'health:metrics:export',
    'health:alerts:read',
    'health:alerts:configure',
    'health:dashboards:read',
    'health:dashboards:write',
    'health:logs:read',
    'health:performance:profile',
    'guardian:read',
    'guardian:configure',
    'guardian:policies:read',
    'guardian:policies:write',
    'guardian:policy:read',
    'guardian:compliance:check',
    'guardian:compliance:report',
    'identity:read',
    'identity:write',
    'identity:admin'
  ],

  [IdentityTier.T5_CORE_TEAM]: [
    // All scopes available for core team
    'docs:read',
    'app:read',
    'app:write',
    'api:read',
    'api:write',
    'api:keys:create',
    'api:keys:read',
    'api:keys:write',
    'api:keys:delete',
    'api:keys:admin',
    'matriz:demo:read',
    'matriz:read',
    'matriz:write',
    'matriz:export',
    'matriz:admin',
    'nias:validate',
    'nias:replay',
    'nias:models:read',
    'nias:models:write',
    'nias:models:train',
    'nias:models:deploy',
    'nias:inference:run',
    'nias:inference:batch',
    'nias:datasets:read',
    'nias:datasets:write',
    'nias:experiments:run',
    'nias:experiments:design',
    'nias:symbolic:reasoning',
    'nias:symbolic:validation',
    'nias:consciousness:bridge',
    'nias:dreams:synthesize',
    'nias:dreams:replay',
    'nias:research:experimental',
    'abas:profiles:read',
    'abas:profiles:write',
    'abas:analytics:read',
    'abas:analytics:export',
    'abas:patterns:discover',
    'abas:patterns:train',
    'abas:insights:read',
    'abas:insights:share',
    'abas:experiments:run',
    'abas:experiments:manage',
    'abas:alerts:read',
    'abas:alerts:configure',
    'abas:privacy:configure',
    'dast:route',
    'dast:routes:read',
    'dast:routes:write',
    'dast:topology:discover',
    'dast:topology:visualize',
    'dast:load_balancing:read',
    'dast:load_balancing:write',
    'dast:health_checks:read',
    'dast:health_checks:write',
    'dast:scaling:read',
    'dast:scaling:configure',
    'dast:deployment:trigger',
    'dast:rollback:execute',
    'dast:analytics:advanced',
    'orchestrator:run',
    'orchestrator:debug',
    'orchestrator:admin',
    'org:read',
    'org:settings',
    'org:members',
    'org:admin',
    'billing:read',
    'billing:manage',
    'billing:admin',
    'health:metrics:read',
    'health:metrics:export',
    'health:alerts:read',
    'health:alerts:configure',
    'health:dashboards:read',
    'health:dashboards:write',
    'health:logs:read',
    'health:performance:profile',
    'health:anomaly:detect',
    'health:remediation:auto',
    'health:sla:monitor',
    'health:observability:setup',
    'guardian:read',
    'guardian:configure',
    'guardian:policies:read',
    'guardian:policies:write',
    'guardian:policies:approve',
    'guardian:policy:read',
    'guardian:ethics:evaluate',
    'guardian:compliance:check',
    'guardian:compliance:report',
    'guardian:violations:detect',
    'guardian:violations:resolve',
    'guardian:override',
    'identity:read',
    'identity:write',
    'identity:admin',
    'identity:impersonate',
    'system:monitor',
    'system:admin',
    'system:emergency'
  ]
};

/**
 * Module-specific scope groupings for easier management
 */
export const MODULE_SCOPES = {
  CORE: [
    'docs:read',
    'app:read',
    'app:write',
    'api:read',
    'api:write'
  ] as ExtendedAuthScope[],

  MATRIZ: [
    'matriz:demo:read',
    'matriz:read',
    'matriz:write',
    'matriz:export',
    'matriz:admin'
  ] as ExtendedAuthScope[],

  NIAS: [
    'nias:validate',
    'nias:replay',
    'nias:models:read',
    'nias:models:write',
    'nias:models:train',
    'nias:models:deploy',
    'nias:inference:run',
    'nias:inference:batch',
    'nias:datasets:read',
    'nias:datasets:write',
    'nias:experiments:run',
    'nias:experiments:design',
    'nias:symbolic:reasoning',
    'nias:symbolic:validation',
    'nias:consciousness:bridge',
    'nias:dreams:synthesize',
    'nias:dreams:replay',
    'nias:research:experimental'
  ] as ExtendedAuthScope[],

  ABAS: [
    'abas:profiles:read',
    'abas:profiles:write',
    'abas:analytics:read',
    'abas:analytics:export',
    'abas:patterns:discover',
    'abas:patterns:train',
    'abas:insights:read',
    'abas:insights:share',
    'abas:experiments:run',
    'abas:experiments:manage',
    'abas:alerts:read',
    'abas:alerts:configure',
    'abas:privacy:configure'
  ] as ExtendedAuthScope[],

  DAST: [
    'dast:route',
    'dast:routes:read',
    'dast:routes:write',
    'dast:topology:discover',
    'dast:topology:visualize',
    'dast:load_balancing:read',
    'dast:load_balancing:write',
    'dast:health_checks:read',
    'dast:health_checks:write',
    'dast:scaling:read',
    'dast:scaling:configure',
    'dast:deployment:trigger',
    'dast:rollback:execute',
    'dast:analytics:advanced'
  ] as ExtendedAuthScope[],

  GUARDIAN: [
    'guardian:read',
    'guardian:configure',
    'guardian:policies:read',
    'guardian:policies:write',
    'guardian:policies:approve',
    'guardian:policy:read',
    'guardian:ethics:evaluate',
    'guardian:compliance:check',
    'guardian:compliance:report',
    'guardian:violations:detect',
    'guardian:violations:resolve',
    'guardian:override'
  ] as ExtendedAuthScope[],

  HEALTH: [
    'health:metrics:read',
    'health:metrics:export',
    'health:alerts:read',
    'health:alerts:configure',
    'health:dashboards:read',
    'health:dashboards:write',
    'health:logs:read',
    'health:performance:profile',
    'health:anomaly:detect',
    'health:remediation:auto',
    'health:sla:monitor',
    'health:observability:setup'
  ] as ExtendedAuthScope[]
};

/**
 * Scope hierarchy for inheritance resolution
 */
export const EXTENDED_SCOPE_HIERARCHY: Record<ExtendedAuthScope, ExtendedAuthScope[]> = {
  // Core API hierarchy
  'api:write': ['api:read'],
  'api:keys:admin': ['api:keys:delete', 'api:keys:write', 'api:keys:read'],
  'api:keys:delete': ['api:keys:write', 'api:keys:read'],
  'api:keys:write': ['api:keys:read'],
  'app:write': ['app:read'],

  // MATRIZ hierarchy
  'matriz:admin': ['matriz:export', 'matriz:write', 'matriz:read', 'matriz:demo:read'],
  'matriz:export': ['matriz:write', 'matriz:read', 'matriz:demo:read'],
  'matriz:write': ['matriz:read', 'matriz:demo:read'],
  'matriz:read': ['matriz:demo:read'],

  // NIAS hierarchy
  'nias:research:experimental': ['nias:dreams:replay', 'nias:dreams:synthesize', 'nias:consciousness:bridge', 'nias:symbolic:validation', 'nias:symbolic:reasoning'],
  'nias:models:deploy': ['nias:models:train', 'nias:models:write', 'nias:models:read'],
  'nias:models:train': ['nias:models:write', 'nias:models:read'],
  'nias:models:write': ['nias:models:read'],
  'nias:inference:batch': ['nias:inference:run'],
  'nias:datasets:write': ['nias:datasets:read'],
  'nias:experiments:design': ['nias:experiments:run'],
  'nias:dreams:replay': ['nias:dreams:synthesize'],
  'nias:symbolic:validation': ['nias:symbolic:reasoning'],
  'nias:consciousness:bridge': ['nias:symbolic:reasoning', 'nias:symbolic:validation'],

  // ABAS hierarchy
  'abas:experiments:manage': ['abas:experiments:run'],
  'abas:analytics:export': ['abas:analytics:read'],
  'abas:patterns:train': ['abas:patterns:discover'],
  'abas:insights:share': ['abas:insights:read'],
  'abas:profiles:write': ['abas:profiles:read'],
  'abas:alerts:configure': ['abas:alerts:read'],

  // DAST hierarchy
  'dast:analytics:advanced': ['dast:topology:visualize', 'dast:topology:discover'],
  'dast:rollback:execute': ['dast:deployment:trigger'],
  'dast:scaling:configure': ['dast:scaling:read'],
  'dast:load_balancing:write': ['dast:load_balancing:read'],
  'dast:health_checks:write': ['dast:health_checks:read'],
  'dast:routes:write': ['dast:routes:read'],
  'dast:topology:visualize': ['dast:topology:discover'],
  'dast:route': ['dast:routes:read'],

  // Guardian hierarchy
  'guardian:override': ['guardian:policies:approve', 'guardian:configure', 'guardian:read'],
  'guardian:policies:approve': ['guardian:policies:write', 'guardian:policies:read', 'guardian:read'],
  'guardian:policies:write': ['guardian:policies:read', 'guardian:read'],
  'guardian:policy:read': ['guardian:read'],
  'guardian:ethics:evaluate': ['guardian:read'],
  'guardian:compliance:report': ['guardian:compliance:check', 'guardian:read'],
  'guardian:compliance:check': ['guardian:read'],
  'guardian:violations:resolve': ['guardian:violations:detect', 'guardian:read'],
  'guardian:violations:detect': ['guardian:read'],
  'guardian:configure': ['guardian:read'],

  // Health hierarchy
  'health:observability:setup': ['health:dashboards:write', 'health:alerts:configure', 'health:metrics:export'],
  'health:remediation:auto': ['health:anomaly:detect', 'health:metrics:read'],
  'health:sla:monitor': ['health:metrics:read', 'health:alerts:read'],
  'health:anomaly:detect': ['health:performance:profile', 'health:metrics:read'],
  'health:performance:profile': ['health:logs:read', 'health:metrics:read'],
  'health:dashboards:write': ['health:dashboards:read', 'health:metrics:read'],
  'health:dashboards:read': ['health:metrics:read'],
  'health:alerts:configure': ['health:alerts:read'],
  'health:metrics:export': ['health:metrics:read'],
  'health:logs:read': ['health:metrics:read'],

  // Identity hierarchy
  'identity:admin': ['identity:write', 'identity:read'],
  'identity:write': ['identity:read'],
  'identity:impersonate': ['identity:admin'],

  // Organization hierarchy
  'org:admin': ['org:members', 'org:settings', 'org:read'],
  'org:members': ['org:read'],
  'org:settings': ['org:read'],

  // Billing hierarchy
  'billing:admin': ['billing:manage', 'billing:read'],
  'billing:manage': ['billing:read'],

  // Orchestrator hierarchy
  'orchestrator:admin': ['orchestrator:debug', 'orchestrator:run'],
  'orchestrator:debug': ['orchestrator:run'],

  // System hierarchy
  'system:emergency': ['system:admin', 'system:monitor'],
  'system:admin': ['system:monitor'],

  // Base scopes (no inheritance)
  'docs:read': [],
  'nias:validate': [],
  'nias:replay': [],
  'api:keys:create': []
};

/**
 * Permission context for granular access control
 */
export interface ExtendedPermissionContext {
  resource?: string;
  action?: string;
  module?: 'nias' | 'abas' | 'dast' | 'guardian' | 'health' | 'matriz';
  conditions?: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * Enhanced authorization result with module context
 */
export interface ExtendedAuthorizationResult {
  allowed: boolean;
  reason?: string;
  requiredScope?: ExtendedAuthScope;
  missingPermissions?: ExtendedAuthScope[];
  module?: string;
  metadata?: Record<string, any>;
}

/**
 * Enhanced scope validation with module-aware logic
 *
 * @param userTier - User's current tier level
 * @param userScopes - Explicitly granted scopes
 * @param requiredScope - Scope required for the operation
 * @param context - Additional permission context including module
 * @returns Authorization decision with detailed reasoning
 */
export function hasExtendedScope(
  userTier: UserTier,
  userScopes: ExtendedAuthScope[],
  requiredScope: ExtendedAuthScope,
  context?: ExtendedPermissionContext
): ExtendedAuthorizationResult {
  // Deny by default
  let result: ExtendedAuthorizationResult = {
    allowed: false,
    reason: 'Access denied by default policy',
    requiredScope,
    module: context?.module
  };

  try {
    // 1. Check if scope exists in tier envelope
    const tierScopes = EXTENDED_TIER_ENVELOPES[userTier as IdentityTier];
    if (!tierScopes.includes(requiredScope)) {
      return {
        ...result,
        reason: `Scope '${requiredScope}' not available in tier ${userTier}`
      };
    }

    // 2. Check explicit user scopes
    if (!userScopes.includes(requiredScope)) {
      // Check scope hierarchy for inherited permissions
      const inheritedScopes = getExtendedInheritedScopes(userScopes);
      if (!inheritedScopes.includes(requiredScope)) {
        return {
          ...result,
          reason: `User does not have scope '${requiredScope}' or inherited permissions`
        };
      }
    }

    // 3. Apply module-specific conditions
    if (context?.module) {
      const moduleCheck = validateModuleAccess(context.module, requiredScope, context);
      if (!moduleCheck.allowed) {
        return {
          ...result,
          reason: `Module access denied: ${moduleCheck.reason}`
        };
      }
    }

    // 4. Apply contextual conditions if present
    if (context?.conditions) {
      const conditionResult = evaluateExtendedConditions(context.conditions, {
        userTier,
        userScopes,
        requiredScope,
        module: context.module
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
      module: context?.module,
      metadata: {
        tier: userTier,
        grantedVia: userScopes.includes(requiredScope) ? 'explicit' : 'inherited',
        timestamp: new Date().toISOString(),
        module: context?.module
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
 * Get all inherited scopes based on extended hierarchy
 */
export function getExtendedInheritedScopes(explicitScopes: ExtendedAuthScope[]): ExtendedAuthScope[] {
  const inherited = new Set<ExtendedAuthScope>(explicitScopes);

  for (const scope of explicitScopes) {
    const childScopes = EXTENDED_SCOPE_HIERARCHY[scope] || [];
    childScopes.forEach(child => inherited.add(child));
  }

  return Array.from(inherited);
}

/**
 * Validate module-specific access requirements
 */
function validateModuleAccess(
  module: string,
  scope: ExtendedAuthScope,
  context: ExtendedPermissionContext
): { allowed: boolean; reason?: string } {

  // Module-specific validation rules
  switch (module) {
    case 'nias':
      // NIAS requires consciousness integration checks
      if (scope.startsWith('nias:consciousness:') && !context.conditions?.consciousness_active) {
        return { allowed: false, reason: 'Consciousness system not active' };
      }
      if (scope.startsWith('nias:models:train') && !context.conditions?.compute_quota) {
        return { allowed: false, reason: 'Insufficient compute quota' };
      }
      break;

    case 'guardian':
      // Guardian operations require ethical validation
      if (scope.startsWith('guardian:override') && !context.conditions?.ethics_override_approved) {
        return { allowed: false, reason: 'Ethics override not approved' };
      }
      break;

    case 'dast':
      // DAST operations may require infrastructure access
      if (scope.startsWith('dast:deployment:') && !context.conditions?.infrastructure_access) {
        return { allowed: false, reason: 'Infrastructure access required' };
      }
      break;

    case 'health':
      // Health monitoring may require system-level access
      if (scope.startsWith('health:remediation:') && !context.conditions?.system_write_access) {
        return { allowed: false, reason: 'System write access required for remediation' };
      }
      break;
  }

  return { allowed: true };
}

/**
 * Enhanced condition evaluation with module context
 */
function evaluateExtendedConditions(
  conditions: Record<string, any>,
  context: {
    userTier: UserTier;
    userScopes: ExtendedAuthScope[];
    requiredScope: ExtendedAuthScope;
    module?: string;
  }
): { allowed: boolean; reason?: string } {

  // Module-specific conditions
  if (context.module === 'nias' && conditions.compute_intensive) {
    // Check for compute quota
    if (!conditions.compute_quota_available) {
      return { allowed: false, reason: 'Compute quota exhausted' };
    }
  }

  if (context.module === 'guardian' && conditions.ethical_review_required) {
    // Ensure ethical review is completed
    if (!conditions.ethical_review_completed) {
      return { allowed: false, reason: 'Ethical review pending' };
    }
  }

  // Time-based conditions for sensitive operations
  if (conditions.sensitive_operation && conditions.business_hours_only) {
    const now = new Date();
    const hour = now.getUTCHours();
    if (hour < 9 || hour > 17) {
      return { allowed: false, reason: 'Sensitive operations restricted to business hours' };
    }
  }

  // Rate limiting conditions
  if (conditions.rate_limited && conditions.rate_limit_exceeded) {
    return { allowed: false, reason: 'Rate limit exceeded' };
  }

  return { allowed: true };
}

/**
 * Get available scopes for a specific tier
 */
export function getExtendedAvailableScopes(tier: UserTier): ExtendedAuthScope[] {
  return EXTENDED_TIER_ENVELOPES[tier as IdentityTier] || [];
}

/**
 * Get scopes for a specific module
 */
export function getModuleScopes(module: keyof typeof MODULE_SCOPES): ExtendedAuthScope[] {
  return MODULE_SCOPES[module] || [];
}

/**
 * Check if a scope belongs to a specific module
 */
export function isScopeInModule(scope: ExtendedAuthScope, module: keyof typeof MODULE_SCOPES): boolean {
  return MODULE_SCOPES[module].includes(scope);
}

/**
 * Validate scope format for extended scopes
 */
export function isValidExtendedScope(scope: string): scope is ExtendedAuthScope {
  return Object.values(EXTENDED_TIER_ENVELOPES)
    .flat()
    .includes(scope as ExtendedAuthScope);
}

/**
 * Get tier requirement for a specific scope
 */
export function getScopeMinimumTier(scope: ExtendedAuthScope): IdentityTier | null {
  for (const [tier, scopes] of Object.entries(EXTENDED_TIER_ENVELOPES)) {
    if (scopes.includes(scope)) {
      return tier as IdentityTier;
    }
  }
  return null;
}

/**
 * Export types for external use
 */
export type { ExtendedAuthScope, ExtendedPermissionContext, ExtendedAuthorizationResult };
export { IdentityTier };
