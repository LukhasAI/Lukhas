/**
 * Group to Role Mapping System with Collision Handling
 * Enterprise-grade role mapping for LUKHAS AI ΛiD System
 * 
 * Supports:
 * - Deterministic mapping from IdP groups to platform roles
 * - Collision resolution strategy with priority-based conflict handling
 * - Custom mapping rules with regex patterns
 * - Audit trail for mapping decisions
 * - Multi-tenant isolation
 */

import { AuditLogger } from '../audit-logger';
import { RBACManager } from '../rbac';

export interface GroupMappingRule {
  id: string;
  tenantId: string;
  name: string;
  description?: string;
  
  // Group matching
  groupPattern: string; // Regex pattern to match group names
  groupPatternFlags?: string; // Regex flags (i, g, m, etc.)
  exactMatch?: boolean; // If true, use exact string match instead of regex
  
  // Role assignment
  roleName: string;
  roleScope?: 'global' | 'tenant' | 'group'; // Scope of the role assignment
  
  // Priority and conditions
  priority: number; // Higher number = higher priority (1-1000)
  isActive: boolean;
  
  // Conditions for applying the rule
  conditions?: {
    userCount?: { min?: number; max?: number }; // Group size requirements
    groupType?: string[]; // Required group types
    tenantTier?: ('T1' | 'T2' | 'T3' | 'T4' | 'T5')[]; // Required tenant tiers
    userAttributes?: Record<string, string | string[]>; // Required user attributes
    timeWindow?: { start: string; end: string }; // Time-based conditions
  };
  
  // Metadata
  metadata: {
    createdAt: Date;
    updatedAt: Date;
    createdBy: string;
    lastApplied?: Date;
    applicationCount: number;
    lastTestResult?: GroupMappingTestResult;
  };
}

export interface GroupMappingTestResult {
  ruleId: string;
  testType: 'syntax' | 'application' | 'full';
  success: boolean;
  testedGroups: string[];
  matchedGroups: string[];
  errors: string[];
  warnings: string[];
  timestamp: Date;
}

export interface MappingConflict {
  conflictId: string;
  userId: string;
  userEmail: string;
  groupName: string;
  
  // Conflicting mappings
  conflictingRules: Array<{
    ruleId: string;
    ruleName: string;
    roleName: string;
    priority: number;
    tenantId: string;
  }>;
  
  // Resolution details
  resolution: {
    strategy: 'priority' | 'merge' | 'first' | 'manual';
    selectedRuleId: string;
    selectedRoleName: string;
    reason: string;
  };
  
  // Metadata
  timestamp: Date;
  resolvedAt?: Date;
  resolvedBy?: string;
}

export interface MappingApplicationResult {
  userId: string;
  userEmail: string;
  groupMemberships: string[];
  appliedMappings: Array<{
    ruleId: string;
    ruleName: string;
    groupName: string;
    roleName: string;
    priority: number;
  }>;
  conflicts: MappingConflict[];
  finalRoles: string[];
  warnings: string[];
}

export interface MappingAuditEntry {
  id: string;
  tenantId: string;
  eventType: 'rule_created' | 'rule_updated' | 'rule_deleted' | 'mapping_applied' | 'conflict_resolved';
  
  details: {
    ruleId?: string;
    userId?: string;
    groupName?: string;
    roleName?: string;
    conflictId?: string;
    changes?: Record<string, { old: any; new: any }>;
  };
  
  actor: {
    userId: string;
    email: string;
    role: string;
  };
  
  timestamp: Date;
  ipAddress?: string;
  userAgent?: string;
}

export class GroupMappingManager {
  private auditLogger: AuditLogger;
  private rbacManager: RBACManager;
  private mappingRules = new Map<string, GroupMappingRule>();
  private tenantRules = new Map<string, string[]>(); // tenantId -> ruleIds
  private conflicts = new Map<string, MappingConflict>();
  private auditTrail: MappingAuditEntry[] = [];

  constructor(auditLogger: AuditLogger, rbacManager: RBACManager) {
    this.auditLogger = auditLogger;
    this.rbacManager = rbacManager;
  }

  /**
   * Create a new group mapping rule
   */
  async createMappingRule(
    rule: Omit<GroupMappingRule, 'id' | 'metadata'>,
    actorInfo: { userId: string; email: string; role: string }
  ): Promise<GroupMappingRule> {
    try {
      // Validate rule
      await this.validateMappingRule(rule);

      const ruleId = this.generateRuleId();
      const now = new Date();

      const mappingRule: GroupMappingRule = {
        id: ruleId,
        ...rule,
        metadata: {
          createdAt: now,
          updatedAt: now,
          createdBy: actorInfo.userId,
          applicationCount: 0
        }
      };

      // Test rule syntax
      const testResult = await this.testMappingRule(mappingRule, ['test-group-name']);
      mappingRule.metadata.lastTestResult = testResult;

      if (!testResult.success) {
        throw new Error(`Invalid mapping rule: ${testResult.errors.join(', ')}`);
      }

      // Store rule
      this.mappingRules.set(ruleId, mappingRule);

      // Update tenant index
      if (!this.tenantRules.has(rule.tenantId)) {
        this.tenantRules.set(rule.tenantId, []);
      }
      this.tenantRules.get(rule.tenantId)!.push(ruleId);

      // Create audit entry
      await this.createAuditEntry({
        tenantId: rule.tenantId,
        eventType: 'rule_created',
        details: {
          ruleId,
          groupName: rule.groupPattern,
          roleName: rule.roleName
        },
        actor: actorInfo
      });

      await this.auditLogger.logSecurityEvent('group_mapping_rule_created', {
        ruleId,
        tenantId: rule.tenantId,
        ruleName: rule.name,
        groupPattern: rule.groupPattern,
        roleName: rule.roleName,
        priority: rule.priority,
        isActive: rule.isActive
      });

      return mappingRule;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('group_mapping_rule_create_failed', {
        tenantId: rule.tenantId,
        groupPattern: rule.groupPattern,
        roleName: rule.roleName,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Update an existing mapping rule
   */
  async updateMappingRule(
    ruleId: string,
    updates: Partial<Omit<GroupMappingRule, 'id' | 'metadata'>>,
    actorInfo: { userId: string; email: string; role: string }
  ): Promise<GroupMappingRule> {
    try {
      const existingRule = this.mappingRules.get(ruleId);
      if (!existingRule) {
        throw new Error(`Mapping rule not found: ${ruleId}`);
      }

      // Validate updates
      const updatedRule = { ...existingRule, ...updates };
      await this.validateMappingRule(updatedRule);

      // Track changes for audit
      const changes: Record<string, { old: any; new: any }> = {};
      for (const [key, newValue] of Object.entries(updates)) {
        const oldValue = (existingRule as any)[key];
        if (oldValue !== newValue) {
          changes[key] = { old: oldValue, new: newValue };
        }
      }

      // Apply updates
      Object.assign(existingRule, updates, {
        metadata: {
          ...existingRule.metadata,
          updatedAt: new Date()
        }
      });

      // Test updated rule
      const testResult = await this.testMappingRule(existingRule, ['test-group-name']);
      existingRule.metadata.lastTestResult = testResult;

      if (!testResult.success) {
        throw new Error(`Updated rule is invalid: ${testResult.errors.join(', ')}`);
      }

      // Create audit entry
      await this.createAuditEntry({
        tenantId: existingRule.tenantId,
        eventType: 'rule_updated',
        details: {
          ruleId,
          changes
        },
        actor: actorInfo
      });

      await this.auditLogger.logSecurityEvent('group_mapping_rule_updated', {
        ruleId,
        tenantId: existingRule.tenantId,
        changedFields: Object.keys(changes),
        isActive: existingRule.isActive
      });

      return existingRule;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('group_mapping_rule_update_failed', {
        ruleId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Delete a mapping rule
   */
  async deleteMappingRule(
    ruleId: string,
    actorInfo: { userId: string; email: string; role: string }
  ): Promise<void> {
    try {
      const rule = this.mappingRules.get(ruleId);
      if (!rule) {
        throw new Error(`Mapping rule not found: ${ruleId}`);
      }

      // Remove from tenant index
      const tenantRules = this.tenantRules.get(rule.tenantId);
      if (tenantRules) {
        const index = tenantRules.indexOf(ruleId);
        if (index >= 0) {
          tenantRules.splice(index, 1);
        }
      }

      // Remove rule
      this.mappingRules.delete(ruleId);

      // Create audit entry
      await this.createAuditEntry({
        tenantId: rule.tenantId,
        eventType: 'rule_deleted',
        details: {
          ruleId,
          groupName: rule.groupPattern,
          roleName: rule.roleName
        },
        actor: actorInfo
      });

      await this.auditLogger.logSecurityEvent('group_mapping_rule_deleted', {
        ruleId,
        tenantId: rule.tenantId,
        ruleName: rule.name,
        applicationCount: rule.metadata.applicationCount
      });

    } catch (error) {
      await this.auditLogger.logSecurityEvent('group_mapping_rule_delete_failed', {
        ruleId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Apply group mappings to a user
   */
  async applyGroupMappings(
    userId: string,
    userEmail: string,
    tenantId: string,
    groupMemberships: string[],
    userAttributes?: Record<string, any>
  ): Promise<MappingApplicationResult> {
    try {
      const appliedMappings: MappingApplicationResult['appliedMappings'] = [];
      const conflicts: MappingConflict[] = [];
      const warnings: string[] = [];
      const roleAssignments = new Map<string, Array<{ ruleId: string; priority: number; ruleName: string }>>();

      // Get rules for tenant
      const tenantRuleIds = this.tenantRules.get(tenantId) || [];
      const tenantRules = tenantRuleIds
        .map(id => this.mappingRules.get(id))
        .filter(rule => rule && rule.isActive)
        .sort((a, b) => b!.priority - a!.priority); // Sort by priority descending

      // Apply each rule
      for (const rule of tenantRules) {
        if (!rule) continue;

        for (const groupName of groupMemberships) {
          const matches = await this.evaluateRule(rule, groupName, userAttributes);
          
          if (matches.isMatch) {
            appliedMappings.push({
              ruleId: rule.id,
              ruleName: rule.name,
              groupName,
              roleName: rule.roleName,
              priority: rule.priority
            });

            // Track role assignments for conflict detection
            if (!roleAssignments.has(rule.roleName)) {
              roleAssignments.set(rule.roleName, []);
            }
            roleAssignments.get(rule.roleName)!.push({
              ruleId: rule.id,
              priority: rule.priority,
              ruleName: rule.name
            });

            // Update rule application count
            rule.metadata.applicationCount++;
            rule.metadata.lastApplied = new Date();
          }

          if (matches.warnings) {
            warnings.push(...matches.warnings);
          }
        }
      }

      // Detect and resolve conflicts
      const finalRoles: string[] = [];
      for (const [roleName, assignments] of roleAssignments) {
        if (assignments.length === 1) {
          // No conflict
          finalRoles.push(roleName);
        } else {
          // Conflict detected - resolve by priority
          const conflict = await this.createConflict(
            userId,
            userEmail,
            groupMemberships[0], // Use first group for context
            assignments.map(a => ({
              ruleId: a.ruleId,
              ruleName: a.ruleName,
              roleName,
              priority: a.priority,
              tenantId
            }))
          );

          conflicts.push(conflict);
          finalRoles.push(conflict.resolution.selectedRoleName);
        }
      }

      const result: MappingApplicationResult = {
        userId,
        userEmail,
        groupMemberships,
        appliedMappings,
        conflicts,
        finalRoles,
        warnings
      };

      // Create audit entry
      await this.createAuditEntry({
        tenantId,
        eventType: 'mapping_applied',
        details: {
          userId,
          groupName: groupMemberships.join(', '),
          roleName: finalRoles.join(', ')
        },
        actor: { userId: 'system', email: 'system@lukhas.ai', role: 'system' }
      });

      await this.auditLogger.logSecurityEvent('group_mappings_applied', {
        userId,
        userEmail,
        tenantId,
        groupCount: groupMemberships.length,
        appliedMappingsCount: appliedMappings.length,
        conflictCount: conflicts.length,
        finalRoleCount: finalRoles.length
      });

      return result;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('group_mapping_application_failed', {
        userId,
        userEmail,
        tenantId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Test a mapping rule against sample groups
   */
  async testMappingRule(
    rule: GroupMappingRule,
    sampleGroups: string[]
  ): Promise<GroupMappingTestResult> {
    const errors: string[] = [];
    const warnings: string[] = [];
    const matchedGroups: string[] = [];

    try {
      // Test regex syntax
      if (!rule.exactMatch) {
        try {
          new RegExp(rule.groupPattern, rule.groupPatternFlags || 'i');
        } catch (regexError) {
          errors.push(`Invalid regex pattern: ${regexError instanceof Error ? regexError.message : 'Unknown error'}`);
        }
      }

      // Test role existence
      if (!await this.rbacManager.roleExists(rule.roleName)) {
        warnings.push(`Role '${rule.roleName}' does not exist and will be created when applied`);
      }

      // Test pattern against sample groups
      if (errors.length === 0) {
        for (const groupName of sampleGroups) {
          const matches = await this.evaluateRule(rule, groupName);
          if (matches.isMatch) {
            matchedGroups.push(groupName);
          }
          if (matches.warnings) {
            warnings.push(...matches.warnings);
          }
        }
      }

      // Validate priority range
      if (rule.priority < 1 || rule.priority > 1000) {
        warnings.push('Priority should be between 1 and 1000 for optimal conflict resolution');
      }

      return {
        ruleId: rule.id,
        testType: 'full',
        success: errors.length === 0,
        testedGroups: sampleGroups,
        matchedGroups,
        errors,
        warnings,
        timestamp: new Date()
      };

    } catch (error) {
      return {
        ruleId: rule.id,
        testType: 'full',
        success: false,
        testedGroups: sampleGroups,
        matchedGroups: [],
        errors: [error instanceof Error ? error.message : 'Unknown test error'],
        warnings,
        timestamp: new Date()
      };
    }
  }

  /**
   * Get mapping rules for tenant
   */
  getMappingRulesForTenant(tenantId: string): GroupMappingRule[] {
    const ruleIds = this.tenantRules.get(tenantId) || [];
    return ruleIds
      .map(id => this.mappingRules.get(id))
      .filter(rule => rule !== undefined) as GroupMappingRule[];
  }

  /**
   * Get mapping conflicts for tenant
   */
  getConflictsForTenant(tenantId: string): MappingConflict[] {
    return Array.from(this.conflicts.values())
      .filter(conflict => conflict.conflictingRules.some(rule => rule.tenantId === tenantId));
  }

  /**
   * Get audit trail for tenant
   */
  getAuditTrailForTenant(tenantId: string, limit: number = 100): MappingAuditEntry[] {
    return this.auditTrail
      .filter(entry => entry.tenantId === tenantId)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  private async validateMappingRule(rule: Omit<GroupMappingRule, 'id' | 'metadata'>): Promise<void> {
    if (!rule.name || rule.name.trim().length === 0) {
      throw new Error('Rule name is required');
    }

    if (!rule.groupPattern || rule.groupPattern.trim().length === 0) {
      throw new Error('Group pattern is required');
    }

    if (!rule.roleName || rule.roleName.trim().length === 0) {
      throw new Error('Role name is required');
    }

    if (!rule.tenantId || rule.tenantId.trim().length === 0) {
      throw new Error('Tenant ID is required');
    }

    if (rule.priority < 1 || rule.priority > 1000) {
      throw new Error('Priority must be between 1 and 1000');
    }

    // Test regex syntax if not exact match
    if (!rule.exactMatch) {
      try {
        new RegExp(rule.groupPattern, rule.groupPatternFlags || 'i');
      } catch (error) {
        throw new Error(`Invalid regex pattern: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  }

  private async evaluateRule(
    rule: GroupMappingRule,
    groupName: string,
    userAttributes?: Record<string, any>
  ): Promise<{ isMatch: boolean; warnings?: string[] }> {
    const warnings: string[] = [];

    try {
      // Check group name match
      let matches = false;
      if (rule.exactMatch) {
        matches = groupName === rule.groupPattern;
      } else {
        const regex = new RegExp(rule.groupPattern, rule.groupPatternFlags || 'i');
        matches = regex.test(groupName);
      }

      if (!matches) {
        return { isMatch: false };
      }

      // Check conditions if specified
      if (rule.conditions) {
        // User attribute conditions
        if (rule.conditions.userAttributes && userAttributes) {
          for (const [attrName, expectedValue] of Object.entries(rule.conditions.userAttributes)) {
            const actualValue = userAttributes[attrName];
            if (Array.isArray(expectedValue)) {
              if (!expectedValue.includes(actualValue)) {
                return { isMatch: false, warnings };
              }
            } else {
              if (actualValue !== expectedValue) {
                return { isMatch: false, warnings };
              }
            }
          }
        }

        // Time window conditions
        if (rule.conditions.timeWindow) {
          const now = new Date();
          const start = new Date(rule.conditions.timeWindow.start);
          const end = new Date(rule.conditions.timeWindow.end);
          
          if (now < start || now > end) {
            return { isMatch: false, warnings };
          }
        }

        // Other conditions would be checked here (group size, tenant tier, etc.)
      }

      return { isMatch: true, warnings: warnings.length > 0 ? warnings : undefined };

    } catch (error) {
      warnings.push(`Error evaluating rule: ${error instanceof Error ? error.message : 'Unknown error'}`);
      return { isMatch: false, warnings };
    }
  }

  private async createConflict(
    userId: string,
    userEmail: string,
    groupName: string,
    conflictingRules: MappingConflict['conflictingRules']
  ): Promise<MappingConflict> {
    const conflictId = this.generateConflictId();
    
    // Resolve by priority (highest priority wins)
    const sortedRules = [...conflictingRules].sort((a, b) => b.priority - a.priority);
    const winner = sortedRules[0];
    
    const conflict: MappingConflict = {
      conflictId,
      userId,
      userEmail,
      groupName,
      conflictingRules,
      resolution: {
        strategy: 'priority',
        selectedRuleId: winner.ruleId,
        selectedRoleName: winner.roleName,
        reason: `Selected rule '${winner.ruleName}' with highest priority (${winner.priority})`
      },
      timestamp: new Date(),
      resolvedAt: new Date(),
      resolvedBy: 'system'
    };

    this.conflicts.set(conflictId, conflict);

    await this.auditLogger.logSecurityEvent('group_mapping_conflict_resolved', {
      conflictId,
      userId,
      userEmail,
      groupName,
      conflictingRuleCount: conflictingRules.length,
      selectedRuleId: winner.ruleId,
      selectedRoleName: winner.roleName,
      resolutionStrategy: 'priority'
    });

    return conflict;
  }

  private async createAuditEntry(
    entry: Omit<MappingAuditEntry, 'id' | 'timestamp' | 'ipAddress' | 'userAgent'>
  ): Promise<void> {
    const auditEntry: MappingAuditEntry = {
      id: this.generateAuditId(),
      ...entry,
      timestamp: new Date()
    };

    this.auditTrail.push(auditEntry);

    // Keep only last 10,000 entries per tenant
    const tenantEntries = this.auditTrail.filter(e => e.tenantId === entry.tenantId);
    if (tenantEntries.length > 10000) {
      // Remove oldest entries for this tenant
      const sortedEntries = tenantEntries.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      const toRemove = sortedEntries.slice(0, sortedEntries.length - 10000);
      this.auditTrail = this.auditTrail.filter(e => !toRemove.includes(e));
    }
  }

  private generateRuleId(): string {
    return 'gmr_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  private generateConflictId(): string {
    return 'gmc_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  private generateAuditId(): string {
    return 'gma_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }
}

/**
 * Collision resolution strategies
 */
export const COLLISION_STRATEGIES = {
  PRIORITY: 'priority',
  MERGE: 'merge',
  FIRST: 'first',
  MANUAL: 'manual'
} as const;

/**
 * Common group patterns for enterprise IdPs
 */
export const COMMON_GROUP_PATTERNS = {
  OKTA: {
    ADMIN: '^.*[Aa]dmin.*$',
    USER: '^.*[Uu]ser.*$',
    DEVELOPER: '^.*[Dd]ev.*$',
    SUPPORT: '^.*[Ss]upport.*$'
  },
  AZURE_AD: {
    ADMIN: '^.*Administrator.*$',
    USER: '^.*Member.*$',
    GUEST: '^.*Guest.*$',
    SECURITY: '^.*Security.*$'
  },
  GOOGLE_WORKSPACE: {
    ADMIN: '^.*admin@.*$',
    GROUP_PREFIX: '^group-.*',
    DEPARTMENT: '^dept-.*'
  }
} as const;

/**
 * Default role mappings for common patterns
 */
export const DEFAULT_ROLE_MAPPINGS = [
  {
    name: 'Admin Users',
    groupPattern: '.*[Aa]dmin.*',
    roleName: 'admin',
    priority: 900
  },
  {
    name: 'Developer Users',
    groupPattern: '.*[Dd]ev.*',
    roleName: 'developer',
    priority: 700
  },
  {
    name: 'Support Users',
    groupPattern: '.*[Ss]upport.*',
    roleName: 'support',
    priority: 600
  },
  {
    name: 'Regular Users',
    groupPattern: '.*[Uu]ser.*',
    roleName: 'user',
    priority: 500
  }
] as const;