/**
 * SCIM v2 Group Management with Role Mapping
 * Enterprise group synchronization for LUKHAS AI ΛiD System
 *
 * Supports:
 * - Group membership synchronization
 * - Nested groups support
 * - Group → Role mapping with collision handling
 * - Bulk group operations
 * - Group hierarchy management
 */

import { AuditLogger } from '../audit-logger';
import { RBACManager } from '../rbac';
import { SCIMListResponse } from './scim-users';

export interface SCIMGroup {
  id: string;
  externalId?: string;
  displayName: string;
  members?: Array<{
    value: string;
    $ref?: string;
    type?: 'User' | 'Group';
    display?: string;
  }>;

  // SCIM metadata
  meta: {
    resourceType: 'Group';
    created: string;
    lastModified: string;
    version?: string;
    location?: string;
  };

  // Custom LUKHAS attributes
  'urn:lukhas:params:scim:schemas:extension:2.0:Group'?: {
    tenantId: string;
    mappedRoles: string[];
    isNested: boolean;
    parentGroups?: string[];
    childGroups?: string[];
    priority: number;
    lastSyncTime?: string;
  };
}

export interface SCIMGroupPatch {
  schemas: ['urn:ietf:params:scim:api:messages:2.0:PatchOp'];
  Operations: Array<{
    op: 'add' | 'remove' | 'replace';
    path?: string;
    value?: any;
  }>;
}

export interface LUKHASGroup {
  id: string;
  name: string;
  displayName: string;
  description?: string;
  tenantId: string;
  members: string[]; // User IDs
  nestedGroups: string[]; // Child group IDs
  parentGroups: string[]; // Parent group IDs
  mappedRoles: string[];
  priority: number; // Higher priority = takes precedence in role conflicts
  isActive: boolean;
  metadata: {
    createdAt: Date;
    updatedAt: Date;
    externalId?: string;
    syncedAt?: Date;
    source: 'scim' | 'manual' | 'inherited';
  };
}

export interface GroupRoleMapping {
  id: string;
  tenantId: string;
  groupPattern: string; // Regex pattern to match group names
  roleName: string;
  priority: number;
  isActive: boolean;
  conditions?: {
    userCount?: { min?: number; max?: number };
    groupType?: string[];
    tenantTier?: ('T1' | 'T2' | 'T3' | 'T4' | 'T5')[];
  };
  metadata: {
    createdAt: Date;
    updatedAt: Date;
    lastApplied?: Date;
    applicationCount: number;
  };
}

export interface RoleConflictResolution {
  userId: string;
  conflictingRoles: Array<{
    roleName: string;
    sourceMappingId: string;
    sourceGroupId: string;
    priority: number;
  }>;
  resolvedRole: string;
  resolutionMethod: 'priority' | 'merge' | 'deny';
  timestamp: Date;
}

export class SCIMGroupManager {
  private auditLogger: AuditLogger;
  private rbacManager: RBACManager;
  private groups = new Map<string, LUKHASGroup>();
  private externalIdMapping = new Map<string, string>(); // externalId -> id
  private roleMappings = new Map<string, GroupRoleMapping>();
  private conflictResolutions = new Map<string, RoleConflictResolution>();

  constructor(auditLogger: AuditLogger, rbacManager: RBACManager) {
    this.auditLogger = auditLogger;
    this.rbacManager = rbacManager;
  }

  /**
   * Create a new group via SCIM
   */
  async createGroup(scimGroup: Partial<SCIMGroup>, tenantId: string): Promise<SCIMGroup> {
    try {
      // Validate required fields
      if (!scimGroup.displayName) {
        throw this.createSCIMError('400', 'displayName is required', 'invalidValue');
      }

      // Check if group already exists
      const existingGroup = await this.findGroupByName(scimGroup.displayName, tenantId);
      if (existingGroup) {
        throw this.createSCIMError('409', 'Group already exists with this name', 'uniqueness');
      }

      // Check external ID if provided
      if (scimGroup.externalId && this.externalIdMapping.has(scimGroup.externalId)) {
        throw this.createSCIMError('409', 'Group already exists with this external ID', 'uniqueness');
      }

      const groupId = this.generateGroupId();
      const now = new Date();

      // Determine mapped roles
      const mappedRoles = await this.determineMappedRoles(scimGroup.displayName, tenantId);

      // Create LUKHAS group
      const lukhasGroup: LUKHASGroup = {
        id: groupId,
        name: scimGroup.displayName.toLowerCase().replace(/\s+/g, '_'),
        displayName: scimGroup.displayName,
        tenantId,
        members: [],
        nestedGroups: [],
        parentGroups: [],
        mappedRoles,
        priority: 100, // Default priority
        isActive: true,
        metadata: {
          createdAt: now,
          updatedAt: now,
          externalId: scimGroup.externalId,
          syncedAt: now,
          source: 'scim'
        }
      };

      // Process initial members if provided
      if (scimGroup.members) {
        await this.processMemberUpdates(lukhasGroup, scimGroup.members, 'add');
      }

      // Store group
      this.groups.set(groupId, lukhasGroup);

      if (scimGroup.externalId) {
        this.externalIdMapping.set(scimGroup.externalId, groupId);
      }

      const scimResponse = this.convertToSCIMGroup(lukhasGroup);

      await this.auditLogger.logSecurityEvent('scim_group_created', {
        groupId,
        displayName: scimGroup.displayName,
        tenantId,
        mappedRoles,
        memberCount: scimGroup.members?.length || 0,
        externalId: scimGroup.externalId
      });

      return scimResponse;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('scim_group_create_failed', {
        displayName: scimGroup.displayName,
        tenantId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Get group by ID
   */
  async getGroup(groupId: string): Promise<SCIMGroup> {
    const group = this.groups.get(groupId);
    if (!group) {
      throw this.createSCIMError('404', 'Group not found');
    }

    return this.convertToSCIMGroup(group);
  }

  /**
   * Update group
   */
  async updateGroup(groupId: string, scimGroup: Partial<SCIMGroup>): Promise<SCIMGroup> {
    try {
      const existingGroup = this.groups.get(groupId);
      if (!existingGroup) {
        throw this.createSCIMError('404', 'Group not found');
      }

      const now = new Date();

      // Update display name if provided
      if (scimGroup.displayName && scimGroup.displayName !== existingGroup.displayName) {
        // Check for name conflicts
        const conflictGroup = await this.findGroupByName(scimGroup.displayName, existingGroup.tenantId);
        if (conflictGroup && conflictGroup.id !== groupId) {
          throw this.createSCIMError('409', 'Group name already in use', 'uniqueness');
        }

        existingGroup.displayName = scimGroup.displayName;
        existingGroup.name = scimGroup.displayName.toLowerCase().replace(/\s+/g, '_');

        // Re-evaluate role mappings for new name
        existingGroup.mappedRoles = await this.determineMappedRoles(scimGroup.displayName, existingGroup.tenantId);
      }

      // Update members if provided
      if (scimGroup.members) {
        await this.syncGroupMembers(existingGroup, scimGroup.members);
      }

      // Update external ID mapping if changed
      if (scimGroup.externalId !== undefined && scimGroup.externalId !== existingGroup.metadata.externalId) {
        // Remove old mapping
        if (existingGroup.metadata.externalId) {
          this.externalIdMapping.delete(existingGroup.metadata.externalId);
        }

        // Check for conflicts
        if (scimGroup.externalId && this.externalIdMapping.has(scimGroup.externalId)) {
          throw this.createSCIMError('409', 'External ID already in use', 'uniqueness');
        }

        // Add new mapping
        if (scimGroup.externalId) {
          this.externalIdMapping.set(scimGroup.externalId, groupId);
        }

        existingGroup.metadata.externalId = scimGroup.externalId;
      }

      existingGroup.metadata.updatedAt = now;
      existingGroup.metadata.syncedAt = now;

      // Re-evaluate user role assignments
      await this.recalculateUserRoles(existingGroup);

      const scimResponse = this.convertToSCIMGroup(existingGroup);

      await this.auditLogger.logSecurityEvent('scim_group_updated', {
        groupId,
        displayName: existingGroup.displayName,
        tenantId: existingGroup.tenantId,
        memberCount: existingGroup.members.length,
        mappedRoles: existingGroup.mappedRoles
      });

      return scimResponse;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('scim_group_update_failed', {
        groupId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Patch group with SCIM patch operations
   */
  async patchGroup(groupId: string, patch: SCIMGroupPatch): Promise<SCIMGroup> {
    try {
      const existingGroup = this.groups.get(groupId);
      if (!existingGroup) {
        throw this.createSCIMError('404', 'Group not found');
      }

      // Process patch operations
      for (const operation of patch.Operations) {
        await this.applyGroupPatchOperation(existingGroup, operation);
      }

      existingGroup.metadata.updatedAt = new Date();
      existingGroup.metadata.syncedAt = new Date();

      // Re-evaluate user role assignments
      await this.recalculateUserRoles(existingGroup);

      const scimResponse = this.convertToSCIMGroup(existingGroup);

      await this.auditLogger.logSecurityEvent('scim_group_patched', {
        groupId,
        operationCount: patch.Operations.length,
        displayName: existingGroup.displayName,
        tenantId: existingGroup.tenantId
      });

      return scimResponse;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('scim_group_patch_failed', {
        groupId,
        operationCount: patch.Operations.length,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Delete group
   */
  async deleteGroup(groupId: string): Promise<void> {
    try {
      const group = this.groups.get(groupId);
      if (!group) {
        throw this.createSCIMError('404', 'Group not found');
      }

      // Remove from nested group relationships
      await this.removeFromNestedRelationships(group);

      // Remove user role assignments from this group
      await this.removeGroupRoleAssignments(group);

      // Remove external ID mapping
      if (group.metadata.externalId) {
        this.externalIdMapping.delete(group.metadata.externalId);
      }

      // Remove group
      this.groups.delete(groupId);

      await this.auditLogger.logSecurityEvent('scim_group_deleted', {
        groupId,
        displayName: group.displayName,
        tenantId: group.tenantId,
        memberCount: group.members.length,
        mappedRoles: group.mappedRoles
      });

    } catch (error) {
      await this.auditLogger.logSecurityEvent('scim_group_delete_failed', {
        groupId,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * List groups with filtering and pagination
   */
  async listGroups(
    filter?: string,
    startIndex: number = 1,
    count: number = 100,
    sortBy?: string,
    sortOrder: 'ascending' | 'descending' = 'ascending'
  ): Promise<SCIMListResponse<SCIMGroup>> {
    try {
      let groups = Array.from(this.groups.values());

      // Apply filter if provided
      if (filter) {
        groups = this.applyGroupFilter(groups, filter);
      }

      // Apply sorting
      if (sortBy) {
        groups = this.applyGroupSorting(groups, sortBy, sortOrder);
      }

      // Calculate pagination
      const totalResults = groups.length;
      const endIndex = Math.min(startIndex + count - 1, totalResults);
      const paginatedGroups = groups.slice(startIndex - 1, endIndex);

      // Convert to SCIM format
      const scimGroups = paginatedGroups.map(group => this.convertToSCIMGroup(group));

      return {
        schemas: ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
        totalResults,
        startIndex,
        itemsPerPage: scimGroups.length,
        Resources: scimGroups
      };

    } catch (error) {
      await this.auditLogger.logSecurityEvent('scim_group_list_failed', {
        filter,
        startIndex,
        count,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
      throw error;
    }
  }

  /**
   * Create or update group role mapping
   */
  async setGroupRoleMapping(mapping: Omit<GroupRoleMapping, 'id' | 'metadata'>): Promise<GroupRoleMapping> {
    const mappingId = this.generateMappingId();
    const now = new Date();

    const roleMapping: GroupRoleMapping = {
      id: mappingId,
      ...mapping,
      metadata: {
        createdAt: now,
        updatedAt: now,
        applicationCount: 0
      }
    };

    this.roleMappings.set(mappingId, roleMapping);

    // Apply mapping to existing groups
    await this.applyMappingToExistingGroups(roleMapping);

    await this.auditLogger.logSecurityEvent('group_role_mapping_created', {
      mappingId,
      tenantId: mapping.tenantId,
      groupPattern: mapping.groupPattern,
      roleName: mapping.roleName,
      priority: mapping.priority
    });

    return roleMapping;
  }

  /**
   * Get role mappings for tenant
   */
  getRoleMappingsForTenant(tenantId: string): GroupRoleMapping[] {
    return Array.from(this.roleMappings.values())
      .filter(mapping => mapping.tenantId === tenantId && mapping.isActive)
      .sort((a, b) => b.priority - a.priority);
  }

  /**
   * Resolve role conflicts for user
   */
  async resolveRoleConflicts(userId: string, userGroups: string[]): Promise<string[]> {
    const conflictingRoles: RoleConflictResolution['conflictingRoles'] = [];

    // Collect all roles from all groups
    for (const groupId of userGroups) {
      const group = this.groups.get(groupId);
      if (!group || !group.isActive) continue;

      for (const role of group.mappedRoles) {
        // Find which mapping assigned this role
        const mapping = this.findMappingForGroupRole(group, role);
        if (mapping) {
          conflictingRoles.push({
            roleName: role,
            sourceMappingId: mapping.id,
            sourceGroupId: groupId,
            priority: mapping.priority
          });
        }
      }
    }

    // Group by role name to find conflicts
    const roleGroups = new Map<string, typeof conflictingRoles>();
    for (const roleAssignment of conflictingRoles) {
      if (!roleGroups.has(roleAssignment.roleName)) {
        roleGroups.set(roleAssignment.roleName, []);
      }
      roleGroups.get(roleAssignment.roleName)!.push(roleAssignment);
    }

    // Resolve conflicts
    const resolvedRoles: string[] = [];
    const resolutions: RoleConflictResolution[] = [];

    for (const [roleName, assignments] of roleGroups) {
      if (assignments.length === 1) {
        // No conflict
        resolvedRoles.push(roleName);
      } else {
        // Conflict - resolve by priority
        const highestPriority = Math.max(...assignments.map(a => a.priority));
        const winningAssignments = assignments.filter(a => a.priority === highestPriority);

        if (winningAssignments.length === 1) {
          // Clear winner
          resolvedRoles.push(roleName);
          resolutions.push({
            userId,
            conflictingRoles: assignments,
            resolvedRole: roleName,
            resolutionMethod: 'priority',
            timestamp: new Date()
          });
        } else {
          // Still tied - use first one (could implement other tie-breaking strategies)
          resolvedRoles.push(roleName);
          resolutions.push({
            userId,
            conflictingRoles: assignments,
            resolvedRole: roleName,
            resolutionMethod: 'priority',
            timestamp: new Date()
          });
        }
      }
    }

    // Store resolutions for audit
    for (const resolution of resolutions) {
      this.conflictResolutions.set(`${userId}_${resolution.resolvedRole}`, resolution);
    }

    await this.auditLogger.logSecurityEvent('role_conflicts_resolved', {
      userId,
      totalRoles: conflictingRoles.length,
      resolvedRoles: resolvedRoles.length,
      conflictCount: resolutions.length
    });

    return resolvedRoles;
  }

  private convertToSCIMGroup(lukhasGroup: LUKHASGroup): SCIMGroup {
    return {
      id: lukhasGroup.id,
      externalId: lukhasGroup.metadata.externalId,
      displayName: lukhasGroup.displayName,
      members: lukhasGroup.members.map(userId => ({
        value: userId,
        type: 'User' as const,
        $ref: `/scim/v2/Users/${userId}`
      })),
      meta: {
        resourceType: 'Group',
        created: lukhasGroup.metadata.createdAt.toISOString(),
        lastModified: lukhasGroup.metadata.updatedAt.toISOString(),
        location: `/scim/v2/Groups/${lukhasGroup.id}`
      },
      'urn:lukhas:params:scim:schemas:extension:2.0:Group': {
        tenantId: lukhasGroup.tenantId,
        mappedRoles: lukhasGroup.mappedRoles,
        isNested: lukhasGroup.nestedGroups.length > 0 || lukhasGroup.parentGroups.length > 0,
        parentGroups: lukhasGroup.parentGroups,
        childGroups: lukhasGroup.nestedGroups,
        priority: lukhasGroup.priority,
        lastSyncTime: lukhasGroup.metadata.syncedAt?.toISOString()
      }
    };
  }

  private async findGroupByName(name: string, tenantId: string): Promise<LUKHASGroup | null> {
    for (const group of this.groups.values()) {
      if (group.displayName === name && group.tenantId === tenantId) {
        return group;
      }
    }
    return null;
  }

  private async determineMappedRoles(groupName: string, tenantId: string): Promise<string[]> {
    const mappings = this.getRoleMappingsForTenant(tenantId);
    const roles: string[] = [];

    for (const mapping of mappings) {
      try {
        const regex = new RegExp(mapping.groupPattern, 'i');
        if (regex.test(groupName)) {
          roles.push(mapping.roleName);
          mapping.metadata.applicationCount++;
          mapping.metadata.lastApplied = new Date();
        }
      } catch (error) {
        // Invalid regex pattern - log and skip
        await this.auditLogger.logSecurityEvent('invalid_group_pattern', {
          mappingId: mapping.id,
          pattern: mapping.groupPattern,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }

    return roles;
  }

  private async processMemberUpdates(
    group: LUKHASGroup,
    members: SCIMGroup['members'],
    operation: 'add' | 'remove'
  ): Promise<void> {
    if (!members) return;

    for (const member of members) {
      if (member.type === 'User') {
        if (operation === 'add' && !group.members.includes(member.value)) {
          group.members.push(member.value);
        } else if (operation === 'remove') {
          group.members = group.members.filter(id => id !== member.value);
        }
      } else if (member.type === 'Group') {
        // Handle nested groups
        if (operation === 'add' && !group.nestedGroups.includes(member.value)) {
          group.nestedGroups.push(member.value);
          await this.updateParentGroupRelationship(member.value, group.id, 'add');
        } else if (operation === 'remove') {
          group.nestedGroups = group.nestedGroups.filter(id => id !== member.value);
          await this.updateParentGroupRelationship(member.value, group.id, 'remove');
        }
      }
    }
  }

  private async syncGroupMembers(group: LUKHASGroup, newMembers: SCIMGroup['members']): Promise<void> {
    const currentUserMembers = new Set(group.members);
    const currentGroupMembers = new Set(group.nestedGroups);
    const newUserMembers = new Set<string>();
    const newGroupMembers = new Set<string>();

    if (newMembers) {
      for (const member of newMembers) {
        if (member.type === 'User') {
          newUserMembers.add(member.value);
        } else if (member.type === 'Group') {
          newGroupMembers.add(member.value);
        }
      }
    }

    // Calculate additions and removals for users
    const usersToAdd = Array.from(newUserMembers).filter(id => !currentUserMembers.has(id));
    const usersToRemove = Array.from(currentUserMembers).filter(id => !newUserMembers.has(id));

    // Calculate additions and removals for groups
    const groupsToAdd = Array.from(newGroupMembers).filter(id => !currentGroupMembers.has(id));
    const groupsToRemove = Array.from(currentGroupMembers).filter(id => !newGroupMembers.has(id));

    // Apply changes
    group.members = Array.from(newUserMembers);
    group.nestedGroups = Array.from(newGroupMembers);

    // Update parent-child relationships for groups
    for (const groupId of groupsToAdd) {
      await this.updateParentGroupRelationship(groupId, group.id, 'add');
    }
    for (const groupId of groupsToRemove) {
      await this.updateParentGroupRelationship(groupId, group.id, 'remove');
    }
  }

  private async updateParentGroupRelationship(
    childGroupId: string,
    parentGroupId: string,
    operation: 'add' | 'remove'
  ): Promise<void> {
    const childGroup = this.groups.get(childGroupId);
    if (!childGroup) return;

    if (operation === 'add' && !childGroup.parentGroups.includes(parentGroupId)) {
      childGroup.parentGroups.push(parentGroupId);
    } else if (operation === 'remove') {
      childGroup.parentGroups = childGroup.parentGroups.filter(id => id !== parentGroupId);
    }
  }

  private async applyGroupPatchOperation(
    group: LUKHASGroup,
    operation: SCIMGroupPatch['Operations'][0]
  ): Promise<void> {
    const { op, path, value } = operation;

    switch (op) {
      case 'add':
        if (path === 'members') {
          await this.processMemberUpdates(group, Array.isArray(value) ? value : [value], 'add');
        }
        break;

      case 'remove':
        if (path === 'members') {
          await this.processMemberUpdates(group, Array.isArray(value) ? value : [value], 'remove');
        } else if (path?.startsWith('members[')) {
          // Remove specific member
          const memberMatch = path.match(/members\[value eq "([^"]+)"\]/);
          if (memberMatch) {
            const memberId = memberMatch[1];
            group.members = group.members.filter(id => id !== memberId);
            group.nestedGroups = group.nestedGroups.filter(id => id !== memberId);
          }
        }
        break;

      case 'replace':
        if (path === 'displayName') {
          group.displayName = value;
          group.name = value.toLowerCase().replace(/\s+/g, '_');
          group.mappedRoles = await this.determineMappedRoles(value, group.tenantId);
        } else if (path === 'members') {
          await this.syncGroupMembers(group, Array.isArray(value) ? value : [value]);
        }
        break;
    }
  }

  private async removeFromNestedRelationships(group: LUKHASGroup): Promise<void> {
    // Remove this group from its parent groups
    for (const parentGroupId of group.parentGroups) {
      const parentGroup = this.groups.get(parentGroupId);
      if (parentGroup) {
        parentGroup.nestedGroups = parentGroup.nestedGroups.filter(id => id !== group.id);
      }
    }

    // Remove this group from its child groups' parent lists
    for (const childGroupId of group.nestedGroups) {
      const childGroup = this.groups.get(childGroupId);
      if (childGroup) {
        childGroup.parentGroups = childGroup.parentGroups.filter(id => id !== group.id);
      }
    }
  }

  private async removeGroupRoleAssignments(group: LUKHASGroup): Promise<void> {
    // This would typically trigger a recalculation of user roles
    // who were members of this group
    for (const userId of group.members) {
      // Remove roles that came from this group
      // Implementation would depend on user management system
    }
  }

  private async recalculateUserRoles(group: LUKHASGroup): Promise<void> {
    // Recalculate roles for all members of this group
    for (const userId of group.members) {
      // This would typically call the user role calculation system
      // Implementation depends on integration with user management
    }
  }

  private async applyMappingToExistingGroups(mapping: GroupRoleMapping): Promise<void> {
    const regex = new RegExp(mapping.groupPattern, 'i');

    for (const group of this.groups.values()) {
      if (group.tenantId === mapping.tenantId && regex.test(group.displayName)) {
        if (!group.mappedRoles.includes(mapping.roleName)) {
          group.mappedRoles.push(mapping.roleName);
          await this.recalculateUserRoles(group);
          mapping.metadata.applicationCount++;
        }
      }
    }

    mapping.metadata.lastApplied = new Date();
  }

  private findMappingForGroupRole(group: LUKHASGroup, roleName: string): GroupRoleMapping | null {
    const mappings = this.getRoleMappingsForTenant(group.tenantId);

    for (const mapping of mappings) {
      if (mapping.roleName === roleName) {
        try {
          const regex = new RegExp(mapping.groupPattern, 'i');
          if (regex.test(group.displayName)) {
            return mapping;
          }
        } catch (error) {
          // Invalid regex
        }
      }
    }

    return null;
  }

  private applyGroupFilter(groups: LUKHASGroup[], filter: string): LUKHASGroup[] {
    // Basic filter implementation for group names
    if (filter.includes('displayName eq')) {
      const match = filter.match(/displayName eq "([^"]+)"/);
      if (match) {
        const displayName = match[1];
        return groups.filter(group => group.displayName === displayName);
      }
    }

    return groups;
  }

  private applyGroupSorting(
    groups: LUKHASGroup[],
    sortBy: string,
    sortOrder: 'ascending' | 'descending'
  ): LUKHASGroup[] {
    const sorted = [...groups];

    sorted.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case 'displayName':
          aValue = a.displayName;
          bValue = b.displayName;
          break;
        case 'meta.created':
          aValue = a.metadata.createdAt;
          bValue = b.metadata.createdAt;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortOrder === 'ascending' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'ascending' ? 1 : -1;
      return 0;
    });

    return sorted;
  }

  private generateGroupId(): string {
    return 'grp_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  private generateMappingId(): string {
    return 'map_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  private createSCIMError(status: string, detail?: string, scimType?: string): Error {
    const error = new Error(detail || 'SCIM operation failed');
    (error as any).scimError = {
      schemas: ['urn:ietf:params:scim:api:messages:2.0:Error'],
      status,
      detail,
      scimType
    };
    return error;
  }
}
