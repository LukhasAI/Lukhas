/**
 * Role-Based Access Control (RBAC) System for ΛiD Authentication
 *
 * Implements hierarchical role management with organization-scoped permissions,
 * role inheritance, and fine-grained access control for LUKHAS AI.
 */

import { TierLevel } from './scopes';
import { TierManager } from './tier-system';

export type Role =
  | 'owner'      // Organization owner (highest authority)
  | 'admin'      // Organization administrator
  | 'developer'  // Developer with creation/modification rights
  | 'analyst'    // Analyst with read access and limited write
  | 'viewer';    // Read-only access

export type Permission =
  // Organization management
  | 'org:create'
  | 'org:read'
  | 'org:update'
  | 'org:delete'
  | 'org:invite'
  | 'org:remove_members'
  | 'org:manage_roles'
  | 'org:manage_billing'
  | 'org:export_data'

  // User management
  | 'user:read'
  | 'user:update'
  | 'user:delete'
  | 'user:impersonate'

  // Project management
  | 'project:create'
  | 'project:read'
  | 'project:update'
  | 'project:delete'
  | 'project:share'
  | 'project:export'

  // API and integration management
  | 'api:keys:create'
  | 'api:keys:read'
  | 'api:keys:update'
  | 'api:keys:delete'
  | 'api:usage:read'
  | 'webhooks:create'
  | 'webhooks:read'
  | 'webhooks:update'
  | 'webhooks:delete'

  // Model and AI management
  | 'models:create'
  | 'models:read'
  | 'models:update'
  | 'models:delete'
  | 'models:train'
  | 'models:deploy'
  | 'models:inference'

  // Analytics and monitoring
  | 'analytics:read'
  | 'analytics:export'
  | 'logs:read'
  | 'logs:export'
  | 'metrics:read'

  // Security and compliance
  | 'security:read'
  | 'security:configure'
  | 'audit:read'
  | 'audit:export'
  | 'compliance:read'
  | 'compliance:configure'

  // Billing and subscription
  | 'billing:read'
  | 'billing:update'
  | 'billing:export'
  | 'subscription:read'
  | 'subscription:update'

  // Administrative functions
  | 'admin:system:read'
  | 'admin:system:configure'
  | 'admin:users:manage'
  | 'admin:organizations:manage'
  | 'admin:tiers:manage'
  | 'admin:support:access'

  // Special permissions
  | 'support:access'
  | 'debug:access'
  | 'impersonate:any';

export interface RoleDefinition {
  role: Role;
  name: string;
  description: string;
  permissions: Permission[];
  inherits?: Role[];
  minTier?: TierLevel;
  requiresVerification?: boolean;
  requiresSSO?: boolean;
}

export interface OrganizationRole {
  userId: string;
  organizationId: string;
  role: Role;
  grantedBy: string;
  grantedAt: Date;
  expiresAt?: Date;
  conditions?: RoleConditions;
}

export interface RoleConditions {
  ipWhitelist?: string[];
  timeRestriction?: {
    startTime: string; // HH:MM format
    endTime: string;   // HH:MM format
    timezone: string;
  };
  mfaRequired?: boolean;
  sessionMaxDuration?: number; // seconds
}

export interface RoleContext {
  userId: string;
  organizationId?: string;
  tier: TierLevel;
  isVerified: boolean;
  isSSOAuthenticated: boolean;
  currentIP?: string;
  sessionCreatedAt: Date;
}

/**
 * Role hierarchy and permission definitions
 */
export const ROLE_DEFINITIONS: Record<Role, RoleDefinition> = {
  viewer: {
    role: 'viewer',
    name: 'Viewer',
    description: 'Read-only access to organization resources',
    permissions: [
      'org:read',
      'user:read',
      'project:read',
      'api:usage:read',
      'models:read',
      'analytics:read',
      'metrics:read'
    ],
    minTier: 'T3'
  },

  analyst: {
    role: 'analyst',
    name: 'Analyst',
    description: 'Analysis and reporting with limited modification rights',
    permissions: [
      'project:create',
      'project:update',
      'models:inference',
      'analytics:export',
      'logs:read'
    ],
    inherits: ['viewer'],
    minTier: 'T3'
  },

  developer: {
    role: 'developer',
    name: 'Developer',
    description: 'Development access with creation and modification rights',
    permissions: [
      'project:delete',
      'project:share',
      'project:export',
      'api:keys:create',
      'api:keys:read',
      'api:keys:update',
      'webhooks:create',
      'webhooks:read',
      'webhooks:update',
      'models:create',
      'models:update',
      'models:train',
      'models:deploy'
    ],
    inherits: ['analyst'],
    minTier: 'T3'
  },

  admin: {
    role: 'admin',
    name: 'Administrator',
    description: 'Administrative access to organization management',
    permissions: [
      'org:update',
      'org:invite',
      'org:remove_members',
      'org:manage_roles',
      'user:update',
      'api:keys:delete',
      'webhooks:delete',
      'models:delete',
      'security:read',
      'security:configure',
      'audit:read',
      'billing:read',
      'subscription:read'
    ],
    inherits: ['developer'],
    minTier: 'T3',
    requiresVerification: true
  },

  owner: {
    role: 'owner',
    name: 'Owner',
    description: 'Full ownership and control of the organization',
    permissions: [
      'org:delete',
      'org:manage_billing',
      'org:export_data',
      'user:delete',
      'user:impersonate',
      'analytics:export',
      'logs:export',
      'audit:export',
      'compliance:read',
      'compliance:configure',
      'billing:update',
      'billing:export',
      'subscription:update'
    ],
    inherits: ['admin'],
    minTier: 'T3',
    requiresVerification: true
  }
};

/**
 * Special internal roles for LUKHAS Core Team (T5)
 */
export const INTERNAL_ROLE_DEFINITIONS: Record<string, RoleDefinition> = {
  support: {
    role: 'admin' as Role,
    name: 'Support Agent',
    description: 'Customer support with limited administrative access',
    permissions: [
      'support:access',
      'org:read',
      'user:read',
      'billing:read',
      'audit:read',
      'analytics:read'
    ],
    minTier: 'T5',
    requiresSSO: true
  },

  engineer: {
    role: 'admin' as Role,
    name: 'Platform Engineer',
    description: 'Engineering access to system administration',
    permissions: [
      'admin:system:read',
      'admin:system:configure',
      'debug:access',
      'logs:export',
      'metrics:read'
    ],
    minTier: 'T5',
    requiresSSO: true
  },

  superadmin: {
    role: 'owner' as Role,
    name: 'Super Administrator',
    description: 'Full system administration access',
    permissions: [
      'admin:users:manage',
      'admin:organizations:manage',
      'admin:tiers:manage',
      'admin:support:access',
      'impersonate:any'
    ],
    minTier: 'T5',
    requiresSSO: true,
    requiresVerification: true
  }
};

/**
 * RBAC Manager class for role and permission management
 */
export class RBACManager {
  /**
   * Get all permissions for a role, including inherited permissions
   */
  static getEffectivePermissions(role: Role): Permission[] {
    const roleDefinition = ROLE_DEFINITIONS[role];
    if (!roleDefinition) return [];

    const permissions = new Set<Permission>(roleDefinition.permissions);

    // Add inherited permissions
    if (roleDefinition.inherits) {
      for (const inheritedRole of roleDefinition.inherits) {
        const inheritedPermissions = this.getEffectivePermissions(inheritedRole);
        inheritedPermissions.forEach(p => permissions.add(p));
      }
    }

    return Array.from(permissions);
  }

  /**
   * Check if a role has a specific permission
   */
  static hasPermission(role: Role, permission: Permission): boolean {
    const effectivePermissions = this.getEffectivePermissions(role);
    return effectivePermissions.includes(permission);
  }

  /**
   * Check if role meets tier and verification requirements
   */
  static canAssignRole(
    role: Role,
    context: RoleContext,
    organizationTier?: TierLevel
  ): { allowed: boolean; reasons: string[] } {
    const roleDefinition = ROLE_DEFINITIONS[role];
    const reasons: string[] = [];

    if (!roleDefinition) {
      return { allowed: false, reasons: ['Invalid role'] };
    }

    // Check minimum tier requirement
    if (roleDefinition.minTier) {
      const userTier = context.tier;
      const requiredTier = roleDefinition.minTier;
      const orgTier = organizationTier || userTier;

      if (!this.meetsTierRequirement(orgTier, requiredTier)) {
        reasons.push(`Role requires ${requiredTier} tier or higher`);
      }
    }

    // Check verification requirement
    if (roleDefinition.requiresVerification && !context.isVerified) {
      reasons.push('Role requires verified account');
    }

    // Check SSO requirement
    if (roleDefinition.requiresSSO && !context.isSSOAuthenticated) {
      reasons.push('Role requires SSO authentication');
    }

    return { allowed: reasons.length === 0, reasons };
  }

  /**
   * Check if tier meets minimum requirement
   */
  private static meetsTierRequirement(currentTier: TierLevel, requiredTier: TierLevel): boolean {
    const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
    const currentIndex = tierOrder.indexOf(currentTier);
    const requiredIndex = tierOrder.indexOf(requiredTier);
    return currentIndex >= requiredIndex;
  }

  /**
   * Validate role conditions (IP restrictions, time limits, etc.)
   */
  static validateRoleConditions(
    conditions: RoleConditions | undefined,
    context: RoleContext
  ): { valid: boolean; reasons: string[] } {
    if (!conditions) return { valid: true, reasons: [] };

    const reasons: string[] = [];

    // Check IP whitelist
    if (conditions.ipWhitelist && context.currentIP) {
      const isIPAllowed = conditions.ipWhitelist.some(allowedIP => {
        // Simple IP matching (extend with CIDR support if needed)
        return context.currentIP === allowedIP || allowedIP === '*';
      });

      if (!isIPAllowed) {
        reasons.push('IP address not in whitelist');
      }
    }

    // Check time restrictions
    if (conditions.timeRestriction) {
      const now = new Date();
      const currentTime = now.toLocaleTimeString('en-US', {
        hour12: false,
        timeZone: conditions.timeRestriction.timezone
      });

      const startTime = conditions.timeRestriction.startTime;
      const endTime = conditions.timeRestriction.endTime;

      if (currentTime < startTime || currentTime > endTime) {
        reasons.push(`Access only allowed between ${startTime} and ${endTime}`);
      }
    }

    // Check session duration
    if (conditions.sessionMaxDuration) {
      const sessionAge = (Date.now() - context.sessionCreatedAt.getTime()) / 1000;
      if (sessionAge > conditions.sessionMaxDuration) {
        reasons.push('Session exceeded maximum duration for this role');
      }
    }

    return { valid: reasons.length === 0, reasons };
  }

  /**
   * Get role hierarchy (roles that can manage other roles)
   */
  static getRoleHierarchy(): Record<Role, Role[]> {
    return {
      owner: ['admin', 'developer', 'analyst', 'viewer'],
      admin: ['developer', 'analyst', 'viewer'],
      developer: ['analyst', 'viewer'],
      analyst: ['viewer'],
      viewer: []
    };
  }

  /**
   * Check if a role can manage another role
   */
  static canManageRole(managerRole: Role, targetRole: Role): boolean {
    const hierarchy = this.getRoleHierarchy();
    return hierarchy[managerRole]?.includes(targetRole) || managerRole === targetRole;
  }

  /**
   * Get available roles for assignment based on current user role
   */
  static getAssignableRoles(currentRole: Role): Role[] {
    const hierarchy = this.getRoleHierarchy();
    return hierarchy[currentRole] || [];
  }

  /**
   * Create a role assignment with validation
   */
  static createRoleAssignment(
    userId: string,
    organizationId: string,
    role: Role,
    grantedBy: string,
    context: RoleContext,
    conditions?: RoleConditions,
    expiresAt?: Date
  ): { success: boolean; assignment?: OrganizationRole; errors: string[] } {
    const errors: string[] = [];

    // Validate role assignment capability
    const { allowed, reasons } = this.canAssignRole(role, context);
    if (!allowed) {
      errors.push(...reasons);
    }

    // Validate conditions
    if (conditions) {
      const { valid, reasons: conditionReasons } = this.validateRoleConditions(conditions, context);
      if (!valid) {
        errors.push(...conditionReasons);
      }
    }

    if (errors.length > 0) {
      return { success: false, errors };
    }

    const assignment: OrganizationRole = {
      userId,
      organizationId,
      role,
      grantedBy,
      grantedAt: new Date(),
      expiresAt,
      conditions
    };

    return { success: true, assignment, errors: [] };
  }

  /**
   * Check comprehensive authorization
   */
  static authorize(
    permission: Permission,
    userRole: Role,
    context: RoleContext,
    conditions?: RoleConditions
  ): { authorized: boolean; reasons: string[] } {
    const reasons: string[] = [];

    // Check if role has permission
    if (!this.hasPermission(userRole, permission)) {
      reasons.push('Insufficient role permissions');
    }

    // Validate role assignment requirements
    const { allowed, reasons: roleReasons } = this.canAssignRole(userRole, context);
    if (!allowed) {
      reasons.push(...roleReasons);
    }

    // Validate conditions
    if (conditions) {
      const { valid, reasons: conditionReasons } = this.validateRoleConditions(conditions, context);
      if (!valid) {
        reasons.push(...conditionReasons);
      }
    }

    return { authorized: reasons.length === 0, reasons };
  }

  /**
   * Get permission documentation
   */
  static getPermissionDescription(permission: Permission): string {
    const descriptions: Record<Permission, string> = {
      // Organization permissions
      'org:create': 'Create new organizations',
      'org:read': 'View organization details',
      'org:update': 'Modify organization settings',
      'org:delete': 'Delete organizations',
      'org:invite': 'Invite users to organization',
      'org:remove_members': 'Remove members from organization',
      'org:manage_roles': 'Assign and modify user roles',
      'org:manage_billing': 'Manage billing and subscription',
      'org:export_data': 'Export all organization data',

      // User permissions
      'user:read': 'View user profiles',
      'user:update': 'Modify user information',
      'user:delete': 'Delete user accounts',
      'user:impersonate': 'Impersonate other users',

      // Project permissions
      'project:create': 'Create new projects',
      'project:read': 'View project details',
      'project:update': 'Modify projects',
      'project:delete': 'Delete projects',
      'project:share': 'Share projects with others',
      'project:export': 'Export project data',

      // API permissions
      'api:keys:create': 'Create API keys',
      'api:keys:read': 'View API keys',
      'api:keys:update': 'Modify API keys',
      'api:keys:delete': 'Delete API keys',
      'api:usage:read': 'View API usage statistics',

      // Webhook permissions
      'webhooks:create': 'Create webhooks',
      'webhooks:read': 'View webhook configurations',
      'webhooks:update': 'Modify webhooks',
      'webhooks:delete': 'Delete webhooks',

      // Model permissions
      'models:create': 'Create AI models',
      'models:read': 'View model details',
      'models:update': 'Modify models',
      'models:delete': 'Delete models',
      'models:train': 'Train AI models',
      'models:deploy': 'Deploy models to production',
      'models:inference': 'Run model inference',

      // Analytics permissions
      'analytics:read': 'View analytics dashboards',
      'analytics:export': 'Export analytics data',
      'logs:read': 'View system logs',
      'logs:export': 'Export log data',
      'metrics:read': 'View system metrics',

      // Security permissions
      'security:read': 'View security settings',
      'security:configure': 'Configure security policies',
      'audit:read': 'View audit logs',
      'audit:export': 'Export audit data',
      'compliance:read': 'View compliance reports',
      'compliance:configure': 'Configure compliance settings',

      // Billing permissions
      'billing:read': 'View billing information',
      'billing:update': 'Modify billing settings',
      'billing:export': 'Export billing data',
      'subscription:read': 'View subscription details',
      'subscription:update': 'Modify subscription',

      // Admin permissions
      'admin:system:read': 'View system administration',
      'admin:system:configure': 'Configure system settings',
      'admin:users:manage': 'Manage all users',
      'admin:organizations:manage': 'Manage all organizations',
      'admin:tiers:manage': 'Manage tier assignments',
      'admin:support:access': 'Access support functions',

      // Special permissions
      'support:access': 'Access customer support tools',
      'debug:access': 'Access debugging tools',
      'impersonate:any': 'Impersonate any user'
    };

    return descriptions[permission] || 'Unknown permission';
  }
}

export default RBACManager;
