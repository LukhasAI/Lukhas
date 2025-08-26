/**
 * Comprehensive Audit Logging System for ΛiD Authentication
 *
 * Implements secure, immutable audit trails for all authorization decisions,
 * security events, and administrative actions in LUKHAS AI.
 */

import { TierLevel } from './tier-system';
import { Role, Permission } from './rbac';

export type AuditEventType =
  // Authentication events
  | 'auth_login_success'
  | 'auth_login_failure'
  | 'auth_logout'
  | 'auth_session_created'
  | 'auth_session_rotated'
  | 'auth_session_expired'
  | 'auth_step_up_required'
  | 'auth_step_up_success'
  | 'auth_step_up_failure'
  | 'auth_mfa_enabled'
  | 'auth_mfa_disabled'
  | 'auth_passkey_added'
  | 'auth_passkey_removed'

  // Authorization events
  | 'authz_permission_granted'
  | 'authz_permission_denied'
  | 'authz_scope_granted'
  | 'authz_scope_denied'
  | 'authz_role_assigned'
  | 'authz_role_removed'
  | 'authz_tier_upgraded'
  | 'authz_tier_downgraded'

  // Resource access events
  | 'resource_create'
  | 'resource_read'
  | 'resource_update'
  | 'resource_delete'
  | 'resource_export'
  | 'resource_share'

  // Security events
  | 'security_suspicious_activity'
  | 'security_rate_limit_exceeded'
  | 'security_ip_blocked'
  | 'security_device_blocked'
  | 'security_anomaly_detected'
  | 'security_breach_attempt'

  // Administrative events
  | 'admin_user_created'
  | 'admin_user_updated'
  | 'admin_user_deleted'
  | 'admin_user_impersonated'
  | 'admin_organization_created'
  | 'admin_organization_updated'
  | 'admin_organization_deleted'
  | 'admin_tier_modified'
  | 'admin_policy_updated'
  | 'admin_system_configuration'

  // Billing events
  | 'billing_subscription_created'
  | 'billing_subscription_updated'
  | 'billing_subscription_cancelled'
  | 'billing_payment_success'
  | 'billing_payment_failure'
  | 'billing_invoice_generated'
  | 'billing_usage_limit_exceeded'

  // Compliance events
  | 'compliance_data_exported'
  | 'compliance_data_deleted'
  | 'compliance_retention_expired'
  | 'compliance_consent_granted'
  | 'compliance_consent_revoked'
  | 'compliance_audit_started'
  | 'compliance_audit_completed';

export type AuditSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface AuditContext {
  // Request context
  requestId?: string;
  sessionId?: string;
  traceId?: string;

  // User context
  userId?: string;
  impersonatorId?: string; // If admin is impersonating
  tier?: TierLevel;
  role?: Role;
  organizationId?: string;

  // Network context
  ipAddress: string;
  userAgent: string;
  country?: string;
  asn?: string; // Autonomous System Number

  // Device context
  deviceId?: string;
  deviceFingerprint?: string;
  deviceTrusted?: boolean;

  // Security context
  authMethods?: string[];
  stepUpAuthenticated?: boolean;
  riskScore?: number;

  // Business context
  featureFlags?: Record<string, boolean>;
  experimentId?: string;
  businessUnit?: string;
}

export interface AuditEntry {
  // Core identification
  id: string;
  timestamp: Date;
  eventType: AuditEventType;
  severity: AuditSeverity;

  // Event details
  action: string;
  resource: string;
  resourceId?: string;
  outcome: 'success' | 'failure' | 'denied' | 'error';

  // Authorization details
  permission?: Permission;
  scope?: string;
  requiredTier?: TierLevel;
  actualTier?: TierLevel;

  // Context
  context: AuditContext;

  // Detailed information
  description: string;
  reasons?: string[];
  metadata?: Record<string, any>;

  // Compliance and retention
  retentionPeriod: number; // Days
  sensitive: boolean;
  piiPresent: boolean;

  // Verification
  checksum: string;
  signature?: string; // Digital signature for high-value events
}

export interface AuditQuery {
  // Time range
  startTime?: Date;
  endTime?: Date;

  // Filtering
  eventTypes?: AuditEventType[];
  userIds?: string[];
  organizationIds?: string[];
  severity?: AuditSeverity[];
  outcomes?: ('success' | 'failure' | 'denied' | 'error')[];

  // Search
  searchTerm?: string;
  resource?: string;
  action?: string;

  // Context filters
  ipAddress?: string;
  deviceId?: string;
  tier?: TierLevel;
  role?: Role;

  // Pagination
  limit?: number;
  offset?: number;
  sortBy?: 'timestamp' | 'severity' | 'eventType';
  sortOrder?: 'asc' | 'desc';
}

export interface AuditStats {
  totalEvents: number;
  eventsByType: Record<AuditEventType, number>;
  eventsBySeverity: Record<AuditSeverity, number>;
  uniqueUsers: number;
  suspiciousEvents: number;
  failureRate: number;
  topResources: Array<{ resource: string; count: number }>;
  timeRange: { start: Date; end: Date };
}

/**
 * Secure audit logging with immutable trails
 */
export class AuditLogger {
  private static entries: AuditEntry[] = [];
  private static readonly MAX_MEMORY_ENTRIES = 10000;

  // In production, this would be a secure database or SIEM system
  private static storage: 'memory' | 'database' | 'siem' = 'memory';

  /**
   * Log an audit event
   */
  static async log(params: {
    eventType: AuditEventType;
    action: string;
    resource: string;
    resourceId?: string;
    outcome: 'success' | 'failure' | 'denied' | 'error';
    context: AuditContext;
    description: string;
    reasons?: string[];
    metadata?: Record<string, any>;
    permission?: Permission;
    scope?: string;
    requiredTier?: TierLevel;
    sensitive?: boolean;
    piiPresent?: boolean;
  }): Promise<string> {

    const id = await this.generateAuditId();
    const timestamp = new Date();
    const severity = this.determineSeverity(params.eventType, params.outcome);

    const entry: AuditEntry = {
      id,
      timestamp,
      eventType: params.eventType,
      severity,
      action: params.action,
      resource: params.resource,
      resourceId: params.resourceId,
      outcome: params.outcome,
      permission: params.permission,
      scope: params.scope,
      requiredTier: params.requiredTier,
      actualTier: params.context.tier,
      context: { ...params.context },
      description: params.description,
      reasons: params.reasons ? [...params.reasons] : undefined,
      metadata: params.metadata ? { ...params.metadata } : undefined,
      retentionPeriod: this.calculateRetentionPeriod(params.eventType, severity, params.sensitive),
      sensitive: params.sensitive || false,
      piiPresent: params.piiPresent || false,
      checksum: '', // Will be calculated
      signature: undefined
    };

    // Calculate checksum for integrity
    entry.checksum = await this.calculateChecksum(entry);

    // Sign critical events
    if (severity === 'critical' || params.sensitive) {
      entry.signature = await this.signEntry(entry);
    }

    // Store the entry
    await this.storeEntry(entry);

    // Send to external systems if configured
    await this.forwardToExternalSystems(entry);

    // Trigger alerts for critical events
    if (severity === 'critical' || params.eventType.startsWith('security_')) {
      await this.triggerSecurityAlert(entry);
    }

    return id;
  }

  /**
   * Log authorization decision
   */
  static async logAuthorizationDecision(params: {
    action: string;
    resource: string;
    resourceId?: string;
    permission?: Permission;
    scope?: string;
    requiredTier?: TierLevel;
    allowed: boolean;
    reasons?: string[];
    context: AuditContext;
    metadata?: Record<string, any>;
  }): Promise<string> {

    return this.log({
      eventType: params.allowed ? 'authz_permission_granted' : 'authz_permission_denied',
      action: params.action,
      resource: params.resource,
      resourceId: params.resourceId,
      outcome: params.allowed ? 'success' : 'denied',
      context: params.context,
      description: params.allowed
        ? `Access granted to ${params.resource}${params.resourceId ? ` (${params.resourceId})` : ''}`
        : `Access denied to ${params.resource}${params.resourceId ? ` (${params.resourceId})` : ''}`,
      reasons: params.reasons,
      permission: params.permission,
      scope: params.scope,
      requiredTier: params.requiredTier,
      metadata: params.metadata
    });
  }

  /**
   * Log authentication event
   */
  static async logAuthentication(params: {
    eventType: Extract<AuditEventType, 'auth_login_success' | 'auth_login_failure' | 'auth_logout' | 'auth_session_created'>;
    userId?: string;
    method: string;
    success: boolean;
    context: AuditContext;
    failureReason?: string;
    sessionId?: string;
    metadata?: Record<string, any>;
  }): Promise<string> {

    return this.log({
      eventType: params.eventType,
      action: 'authenticate',
      resource: 'user_session',
      resourceId: params.sessionId || params.userId,
      outcome: params.success ? 'success' : 'failure',
      context: {
        ...params.context,
        userId: params.userId,
        sessionId: params.sessionId,
        authMethods: [params.method]
      },
      description: params.success
        ? `User authentication successful via ${params.method}`
        : `User authentication failed via ${params.method}${params.failureReason ? `: ${params.failureReason}` : ''}`,
      reasons: params.failureReason ? [params.failureReason] : undefined,
      metadata: params.metadata,
      sensitive: true // Authentication events are always sensitive
    });
  }

  /**
   * Log security event
   */
  static async logSecurityEvent(params: {
    eventType: Extract<AuditEventType, 'security_suspicious_activity' | 'security_rate_limit_exceeded' | 'security_ip_blocked' | 'security_device_blocked' | 'security_anomaly_detected' | 'security_breach_attempt'>;
    description: string;
    context: AuditContext;
    riskScore?: number;
    actionTaken: string;
    metadata?: Record<string, any>;
  }): Promise<string> {

    return this.log({
      eventType: params.eventType,
      action: 'security_monitor',
      resource: 'system_security',
      outcome: 'success', // Detection is success, breach would be failure
      context: {
        ...params.context,
        riskScore: params.riskScore
      },
      description: params.description,
      reasons: [params.actionTaken],
      metadata: {
        ...params.metadata,
        actionTaken: params.actionTaken,
        riskScore: params.riskScore
      },
      sensitive: true
    });
  }

  /**
   * Log administrative action
   */
  static async logAdminAction(params: {
    eventType: Extract<AuditEventType, 'admin_user_created' | 'admin_user_updated' | 'admin_user_deleted' | 'admin_user_impersonated' | 'admin_organization_created' | 'admin_organization_updated' | 'admin_organization_deleted' | 'admin_tier_modified' | 'admin_policy_updated' | 'admin_system_configuration'>;
    adminUserId: string;
    targetUserId?: string;
    targetOrganizationId?: string;
    action: string;
    changes?: Record<string, { from: any; to: any }>;
    context: AuditContext;
    metadata?: Record<string, any>;
  }): Promise<string> {

    return this.log({
      eventType: params.eventType,
      action: params.action,
      resource: params.targetUserId ? 'user' : params.targetOrganizationId ? 'organization' : 'system',
      resourceId: params.targetUserId || params.targetOrganizationId,
      outcome: 'success',
      context: {
        ...params.context,
        userId: params.adminUserId
      },
      description: `Admin action: ${params.action}${params.targetUserId ? ` on user ${params.targetUserId}` : ''}${params.targetOrganizationId ? ` on organization ${params.targetOrganizationId}` : ''}`,
      metadata: {
        ...params.metadata,
        adminUserId: params.adminUserId,
        changes: params.changes
      },
      sensitive: true,
      piiPresent: Boolean(params.targetUserId || params.changes)
    });
  }

  /**
   * Query audit logs
   */
  static async query(query: AuditQuery): Promise<{
    entries: AuditEntry[];
    total: number;
    hasMore: boolean;
  }> {

    let filteredEntries = [...this.entries];

    // Apply filters
    if (query.startTime) {
      filteredEntries = filteredEntries.filter(e => e.timestamp >= query.startTime!);
    }

    if (query.endTime) {
      filteredEntries = filteredEntries.filter(e => e.timestamp <= query.endTime!);
    }

    if (query.eventTypes?.length) {
      filteredEntries = filteredEntries.filter(e => query.eventTypes!.includes(e.eventType));
    }

    if (query.userIds?.length) {
      filteredEntries = filteredEntries.filter(e =>
        e.context.userId && query.userIds!.includes(e.context.userId)
      );
    }

    if (query.organizationIds?.length) {
      filteredEntries = filteredEntries.filter(e =>
        e.context.organizationId && query.organizationIds!.includes(e.context.organizationId)
      );
    }

    if (query.severity?.length) {
      filteredEntries = filteredEntries.filter(e => query.severity!.includes(e.severity));
    }

    if (query.outcomes?.length) {
      filteredEntries = filteredEntries.filter(e => query.outcomes!.includes(e.outcome));
    }

    if (query.searchTerm) {
      const term = query.searchTerm.toLowerCase();
      filteredEntries = filteredEntries.filter(e =>
        e.description.toLowerCase().includes(term) ||
        e.action.toLowerCase().includes(term) ||
        e.resource.toLowerCase().includes(term)
      );
    }

    if (query.resource) {
      filteredEntries = filteredEntries.filter(e => e.resource === query.resource);
    }

    if (query.action) {
      filteredEntries = filteredEntries.filter(e => e.action === query.action);
    }

    if (query.ipAddress) {
      filteredEntries = filteredEntries.filter(e => e.context.ipAddress === query.ipAddress);
    }

    if (query.deviceId) {
      filteredEntries = filteredEntries.filter(e => e.context.deviceId === query.deviceId);
    }

    if (query.tier) {
      filteredEntries = filteredEntries.filter(e => e.context.tier === query.tier);
    }

    if (query.role) {
      filteredEntries = filteredEntries.filter(e => e.context.role === query.role);
    }

    // Sort
    const sortBy = query.sortBy || 'timestamp';
    const sortOrder = query.sortOrder || 'desc';

    filteredEntries.sort((a, b) => {
      let aVal: any, bVal: any;

      switch (sortBy) {
        case 'timestamp':
          aVal = a.timestamp.getTime();
          bVal = b.timestamp.getTime();
          break;
        case 'severity':
          const severityOrder = { low: 1, medium: 2, high: 3, critical: 4 };
          aVal = severityOrder[a.severity];
          bVal = severityOrder[b.severity];
          break;
        case 'eventType':
          aVal = a.eventType;
          bVal = b.eventType;
          break;
        default:
          aVal = a.timestamp.getTime();
          bVal = b.timestamp.getTime();
      }

      if (sortOrder === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
      }
    });

    // Paginate
    const total = filteredEntries.length;
    const offset = query.offset || 0;
    const limit = query.limit || 100;

    const paginatedEntries = filteredEntries.slice(offset, offset + limit);
    const hasMore = offset + limit < total;

    return {
      entries: paginatedEntries,
      total,
      hasMore
    };
  }

  /**
   * Get audit statistics
   */
  static async getStats(query?: Partial<AuditQuery>): Promise<AuditStats> {
    const queryResult = await this.query({
      ...query,
      limit: undefined,
      offset: undefined
    });

    const entries = queryResult.entries;

    const eventsByType: Record<string, number> = {};
    const eventsBySeverity: Record<string, number> = {};
    const resources: Record<string, number> = {};
    const uniqueUserIds = new Set<string>();

    let suspiciousEvents = 0;
    let failureCount = 0;

    for (const entry of entries) {
      eventsByType[entry.eventType] = (eventsByType[entry.eventType] || 0) + 1;
      eventsBySeverity[entry.severity] = (eventsBySeverity[entry.severity] || 0) + 1;
      resources[entry.resource] = (resources[entry.resource] || 0) + 1;

      if (entry.context.userId) {
        uniqueUserIds.add(entry.context.userId);
      }

      if (entry.eventType.startsWith('security_') || entry.severity === 'critical') {
        suspiciousEvents++;
      }

      if (entry.outcome === 'failure' || entry.outcome === 'denied') {
        failureCount++;
      }
    }

    const topResources = Object.entries(resources)
      .map(([resource, count]) => ({ resource, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    const timestamps = entries.map(e => e.timestamp.getTime());
    const timeRange = {
      start: new Date(Math.min(...timestamps)),
      end: new Date(Math.max(...timestamps))
    };

    return {
      totalEvents: entries.length,
      eventsByType: eventsByType as Record<AuditEventType, number>,
      eventsBySeverity: eventsBySeverity as Record<AuditSeverity, number>,
      uniqueUsers: uniqueUserIds.size,
      suspiciousEvents,
      failureRate: entries.length > 0 ? failureCount / entries.length : 0,
      topResources,
      timeRange
    };
  }

  /**
   * Verify audit trail integrity
   */
  static async verifyIntegrity(entryIds?: string[]): Promise<{
    verified: boolean;
    corruptedEntries: string[];
    totalChecked: number;
  }> {

    const entriesToCheck = entryIds
      ? this.entries.filter(e => entryIds.includes(e.id))
      : this.entries;

    const corruptedEntries: string[] = [];

    for (const entry of entriesToCheck) {
      const expectedChecksum = await this.calculateChecksum({
        ...entry,
        checksum: '', // Exclude current checksum from calculation
        signature: undefined // Exclude signature from checksum
      });

      if (entry.checksum !== expectedChecksum) {
        corruptedEntries.push(entry.id);
      }
    }

    return {
      verified: corruptedEntries.length === 0,
      corruptedEntries,
      totalChecked: entriesToCheck.length
    };
  }

  /**
   * Export audit logs for compliance
   */
  static async exportForCompliance(query: AuditQuery, format: 'json' | 'csv' | 'xml' = 'json'): Promise<string> {
    const result = await this.query(query);

    switch (format) {
      case 'json':
        return JSON.stringify(result.entries, null, 2);

      case 'csv':
        const headers = ['id', 'timestamp', 'eventType', 'severity', 'action', 'resource', 'outcome', 'userId', 'description'];
        const rows = result.entries.map(entry => [
          entry.id,
          entry.timestamp.toISOString(),
          entry.eventType,
          entry.severity,
          entry.action,
          entry.resource,
          entry.outcome,
          entry.context.userId || '',
          entry.description.replace(/"/g, '""') // Escape quotes
        ]);

        return [headers, ...rows]
          .map(row => row.map(cell => `"${cell}"`).join(','))
          .join('\n');

      case 'xml':
        const xmlEntries = result.entries.map(entry => `
          <entry>
            <id>${entry.id}</id>
            <timestamp>${entry.timestamp.toISOString()}</timestamp>
            <eventType>${entry.eventType}</eventType>
            <severity>${entry.severity}</severity>
            <action>${entry.action}</action>
            <resource>${entry.resource}</resource>
            <outcome>${entry.outcome}</outcome>
            <userId>${entry.context.userId || ''}</userId>
            <description><![CDATA[${entry.description}]]></description>
          </entry>
        `).join('');

        return `<?xml version="1.0" encoding="UTF-8"?><auditLog>${xmlEntries}</auditLog>`;

      default:
        return JSON.stringify(result.entries, null, 2);
    }
  }

  /**
   * Clean up expired entries based on retention policy
   */
  static async cleanupExpiredEntries(): Promise<number> {
    const now = Date.now();
    const initialCount = this.entries.length;

    this.entries = this.entries.filter(entry => {
      const retentionMs = entry.retentionPeriod * 24 * 60 * 60 * 1000;
      const expiryTime = entry.timestamp.getTime() + retentionMs;
      return now < expiryTime;
    });

    const cleanedCount = initialCount - this.entries.length;

    if (cleanedCount > 0) {
      await this.log({
        eventType: 'compliance_retention_expired',
        action: 'cleanup_expired_entries',
        resource: 'audit_log',
        outcome: 'success',
        context: {
          ipAddress: 'system',
          userAgent: 'audit_cleanup_service'
        },
        description: `Cleaned up ${cleanedCount} expired audit entries`,
        metadata: {
          cleanedCount,
          remainingCount: this.entries.length
        }
      });
    }

    return cleanedCount;
  }

  // Private helper methods

  private static async generateAuditId(): Promise<string> {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2);
    const extraEntropy = crypto.getRandomValues(new Uint8Array(8))
      .reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');

    return `audit_${timestamp}_${randomPart}_${extraEntropy}`;
  }

  private static determineSeverity(eventType: AuditEventType, outcome: string): AuditSeverity {
    // Critical events
    if (eventType.startsWith('security_breach') ||
        eventType.startsWith('admin_') && eventType.includes('deleted') ||
        eventType === 'compliance_data_deleted') {
      return 'critical';
    }

    // High severity events
    if (eventType.startsWith('security_') ||
        eventType.startsWith('admin_') ||
        outcome === 'failure' && eventType.startsWith('auth_')) {
      return 'high';
    }

    // Medium severity events
    if (eventType.startsWith('authz_') && outcome === 'denied' ||
        eventType.startsWith('billing_') ||
        eventType.includes('tier_')) {
      return 'medium';
    }

    // Default to low
    return 'low';
  }

  private static calculateRetentionPeriod(eventType: AuditEventType, severity: AuditSeverity, sensitive?: boolean): number {
    // Legal and compliance requirements
    if (eventType.startsWith('compliance_') || eventType.startsWith('billing_')) {
      return 2555; // 7 years
    }

    // Security events - long retention
    if (eventType.startsWith('security_') || severity === 'critical') {
      return 1095; // 3 years
    }

    // Administrative actions
    if (eventType.startsWith('admin_') || sensitive) {
      return 730; // 2 years
    }

    // Authentication events
    if (eventType.startsWith('auth_')) {
      return 365; // 1 year
    }

    // Default retention
    return 90; // 3 months
  }

  private static async calculateChecksum(entry: Omit<AuditEntry, 'checksum' | 'signature'>): Promise<string> {
    const data = JSON.stringify(entry, Object.keys(entry).sort());
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private static async signEntry(entry: AuditEntry): Promise<string> {
    // In production, this would use a proper digital signature
    // For now, return a simple signature based on checksum
    return `sig_${entry.checksum.substring(0, 16)}`;
  }

  private static async storeEntry(entry: AuditEntry): Promise<void> {
    this.entries.push(entry);

    // Keep memory usage reasonable
    if (this.entries.length > this.MAX_MEMORY_ENTRIES) {
      this.entries = this.entries.slice(-this.MAX_MEMORY_ENTRIES);
    }

    // In production, also store in persistent storage
    console.log('AUDIT_ENTRY:', JSON.stringify(entry, null, 2));
  }

  private static async forwardToExternalSystems(entry: AuditEntry): Promise<void> {
    // Forward to SIEM, log aggregation, etc.
    // Implementation depends on external systems
    if (entry.severity === 'critical' || entry.eventType.startsWith('security_')) {
      console.log('FORWARD_TO_SIEM:', entry.id);
    }
  }

  private static async triggerSecurityAlert(entry: AuditEntry): Promise<void> {
    // Trigger security alerts for critical events
    console.log('SECURITY_ALERT:', {
      entryId: entry.id,
      eventType: entry.eventType,
      severity: entry.severity,
      description: entry.description
    });

    // In production, this would:
    // - Send to security team
    // - Trigger incident response
    // - Update security dashboards
    // - Send to external monitoring
  }
}

export default AuditLogger;
