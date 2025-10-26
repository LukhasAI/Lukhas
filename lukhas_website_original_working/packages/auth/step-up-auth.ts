/**
 * Step-Up Authentication System for ΛiD Authentication
 * 
 * Implements enhanced security for sensitive operations requiring additional
 * authentication verification beyond initial login for LUKHAS AI.
 */

import { TierLevel } from './tier-system';
import { Role, Permission } from './rbac';
import { AuditLogger } from './audit-logger';
import { SessionManager } from './session';

export type StepUpReason = 
  | 'sensitive_operation'
  | 'high_value_transaction'
  | 'administrative_action'
  | 'data_export'
  | 'security_configuration'
  | 'billing_change'
  | 'role_elevation'
  | 'suspicious_activity'
  | 'compliance_requirement'
  | 'time_based_requirement';

export type StepUpMethod = 
  | 'password'
  | 'passkey'
  | 'totp'
  | 'sms'
  | 'email'
  | 'backup_codes'
  | 'hardware_token'
  | 'biometric'
  | 'admin_approval';

export interface StepUpRequirement {
  // Basic requirement info
  id: string;
  reason: StepUpReason;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  
  // Authentication requirements
  requiredMethods: StepUpMethod[];
  minimumMethods: number; // At least this many methods required
  allowedMethods: StepUpMethod[]; // User can choose from these
  
  // Constraints and policies
  maxAge: number; // Maximum age of step-up in seconds
  requiresFreshAuth: boolean; // Must be recent primary authentication
  requiresSecureContext: boolean; // Must be HTTPS, trusted device, etc.
  
  // Conditional requirements
  minTier?: TierLevel;
  requiredRole?: Role;
  requiredPermission?: Permission;
  
  // Time and location constraints
  businessHoursOnly?: boolean;
  allowedCountries?: string[];
  blockedCountries?: string[];
  trustedDeviceRequired?: boolean;
  
  // Escalation and approval
  requiresApproval?: boolean;
  approverRoles?: Role[];
  escalationTimeoutMs?: number;
  
  // Compliance and audit
  complianceFramework?: string; // SOX, HIPAA, PCI-DSS, etc.
  auditLevel: 'standard' | 'enhanced' | 'forensic';
  retentionPeriod: number; // Days
}

export interface StepUpChallenge {
  // Challenge identification
  challengeId: string;
  sessionId: string;
  userId: string;
  
  // Requirement details
  requirement: StepUpRequirement;
  
  // Challenge state
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'expired';
  createdAt: Date;
  expiresAt: Date;
  completedAt?: Date;
  
  // Authentication attempts
  attempts: StepUpAttempt[];
  maxAttempts: number;
  remainingAttempts: number;
  
  // Methods used
  completedMethods: StepUpMethod[];
  availableMethods: StepUpMethod[];
  
  // Context
  triggeredBy: string; // Action that triggered step-up
  originalRequestId: string;
  ipAddress: string;
  userAgent: string;
  deviceId?: string;
  
  // Risk and security
  riskScore: number;
  securityFlags: string[];
  
  // Approval workflow
  approvalRequired: boolean;
  approvalStatus?: 'pending' | 'approved' | 'rejected';
  approvedBy?: string;
  approvedAt?: Date;
  approvalComments?: string;
}

export interface StepUpAttempt {
  attemptId: string;
  method: StepUpMethod;
  timestamp: Date;
  success: boolean;
  failureReason?: string;
  
  // Method-specific data
  methodData?: {
    // TOTP
    totpCode?: string;
    totpWindow?: number;
    
    // SMS/Email
    verificationCode?: string;
    sentTo?: string;
    
    // Passkey
    passkeyId?: string;
    challenge?: string;
    
    // Hardware token
    tokenSerial?: string;
    
    // Biometric
    biometricType?: 'fingerprint' | 'face' | 'voice';
    confidenceScore?: number;
  };
  
  // Security context
  ipAddress: string;
  userAgent: string;
  deviceFingerprint?: string;
  geolocation?: {
    country: string;
    region: string;
    city: string;
  };
}

export interface StepUpResult {
  success: boolean;
  challengeId?: string;
  token?: string; // Step-up proof token
  expiresAt?: Date;
  completedMethods?: StepUpMethod[];
  nextRequiredMethod?: StepUpMethod;
  remainingAttempts?: number;
  requiresApproval?: boolean;
  error?: string;
  retryAfter?: number; // Seconds
}

/**
 * Step-up authentication requirements configuration
 */
export const STEP_UP_REQUIREMENTS: Record<string, StepUpRequirement> = {
  // API key management
  api_key_create: {
    id: 'api_key_create',
    reason: 'sensitive_operation',
    description: 'Creating new API keys',
    severity: 'high',
    requiredMethods: ['passkey', 'totp'],
    minimumMethods: 1,
    allowedMethods: ['passkey', 'totp', 'sms'],
    maxAge: 15 * 60, // 15 minutes
    requiresFreshAuth: false,
    requiresSecureContext: true,
    auditLevel: 'enhanced',
    retentionPeriod: 365
  },
  
  api_key_delete: {
    id: 'api_key_delete',
    reason: 'sensitive_operation',
    description: 'Deleting API keys',
    severity: 'critical',
    requiredMethods: ['passkey', 'totp'],
    minimumMethods: 2,
    allowedMethods: ['passkey', 'totp', 'backup_codes'],
    maxAge: 5 * 60, // 5 minutes
    requiresFreshAuth: true,
    requiresSecureContext: true,
    auditLevel: 'forensic',
    retentionPeriod: 2555 // 7 years
  },
  
  // Billing and subscription changes
  billing_payment_method: {
    id: 'billing_payment_method',
    reason: 'high_value_transaction',
    description: 'Changing payment method',
    severity: 'high',
    requiredMethods: ['password', 'totp'],
    minimumMethods: 2,
    allowedMethods: ['password', 'passkey', 'totp', 'sms'],
    maxAge: 10 * 60, // 10 minutes
    requiresFreshAuth: false,
    requiresSecureContext: true,
    complianceFramework: 'PCI-DSS',
    auditLevel: 'enhanced',
    retentionPeriod: 2555
  },
  
  billing_subscription_cancel: {
    id: 'billing_subscription_cancel',
    reason: 'high_value_transaction',
    description: 'Cancelling subscription',
    severity: 'critical',
    requiredMethods: ['password', 'totp'],
    minimumMethods: 2,
    allowedMethods: ['password', 'passkey', 'totp', 'email'],
    maxAge: 30 * 60, // 30 minutes
    requiresFreshAuth: false,
    requiresSecureContext: true,
    auditLevel: 'forensic',
    retentionPeriod: 2555
  },
  
  // Organization management
  org_member_remove: {
    id: 'org_member_remove',
    reason: 'administrative_action',
    description: 'Removing organization members',
    severity: 'high',
    requiredMethods: ['passkey', 'totp'],
    minimumMethods: 1,
    allowedMethods: ['passkey', 'totp', 'backup_codes'],
    maxAge: 15 * 60,
    requiresFreshAuth: false,
    requiresSecureContext: true,
    requiredRole: 'admin',
    auditLevel: 'enhanced',
    retentionPeriod: 730
  },
  
  org_role_assign_admin: {
    id: 'org_role_assign_admin',
    reason: 'role_elevation',
    description: 'Assigning admin roles',
    severity: 'critical',
    requiredMethods: ['passkey', 'totp', 'password'],
    minimumMethods: 2,
    allowedMethods: ['passkey', 'totp', 'password', 'backup_codes'],
    maxAge: 5 * 60,
    requiresFreshAuth: true,
    requiresSecureContext: true,
    requiredRole: 'owner',
    requiresApproval: true,
    approverRoles: ['owner'],
    auditLevel: 'forensic',
    retentionPeriod: 2555
  },
  
  // Data export and compliance
  data_export_personal: {
    id: 'data_export_personal',
    reason: 'data_export',
    description: 'Exporting personal data',
    severity: 'medium',
    requiredMethods: ['totp'],
    minimumMethods: 1,
    allowedMethods: ['totp', 'sms', 'email'],
    maxAge: 60 * 60, // 1 hour
    requiresFreshAuth: false,
    requiresSecureContext: true,
    complianceFramework: 'GDPR',
    auditLevel: 'enhanced',
    retentionPeriod: 2555
  },
  
  data_export_organization: {
    id: 'data_export_organization',
    reason: 'data_export',
    description: 'Exporting organization data',
    severity: 'critical',
    requiredMethods: ['passkey', 'totp'],
    minimumMethods: 2,
    allowedMethods: ['passkey', 'totp', 'hardware_token'],
    maxAge: 30 * 60,
    requiresFreshAuth: true,
    requiresSecureContext: true,
    requiredRole: 'admin',
    businessHoursOnly: true,
    requiresApproval: true,
    approverRoles: ['owner'],
    escalationTimeoutMs: 4 * 60 * 60 * 1000, // 4 hours
    complianceFramework: 'SOX',
    auditLevel: 'forensic',
    retentionPeriod: 2555
  },
  
  // Security configuration
  security_mfa_disable: {
    id: 'security_mfa_disable',
    reason: 'security_configuration',
    description: 'Disabling multi-factor authentication',
    severity: 'critical',
    requiredMethods: ['passkey', 'totp', 'backup_codes'],
    minimumMethods: 3,
    allowedMethods: ['passkey', 'totp', 'backup_codes', 'hardware_token'],
    maxAge: 5 * 60,
    requiresFreshAuth: true,
    requiresSecureContext: true,
    trustedDeviceRequired: true,
    auditLevel: 'forensic',
    retentionPeriod: 2555
  },
  
  // Administrative functions (T5 only)
  admin_user_impersonate: {
    id: 'admin_user_impersonate',
    reason: 'administrative_action',
    description: 'Impersonating another user',
    severity: 'critical',
    requiredMethods: ['passkey', 'totp', 'admin_approval'],
    minimumMethods: 3,
    allowedMethods: ['passkey', 'totp', 'hardware_token', 'admin_approval'],
    maxAge: 30 * 60,
    requiresFreshAuth: true,
    requiresSecureContext: true,
    minTier: 'T5',
    requiredRole: 'admin',
    businessHoursOnly: true,
    requiresApproval: true,
    approverRoles: ['admin'],
    escalationTimeoutMs: 2 * 60 * 60 * 1000, // 2 hours
    auditLevel: 'forensic',
    retentionPeriod: 2555
  }
};

/**
 * Step-up authentication manager
 */
export class StepUpAuthManager {
  private static challenges = new Map<string, StepUpChallenge>();
  private static readonly CHALLENGE_CLEANUP_INTERVAL = 5 * 60 * 1000; // 5 minutes

  static {
    // Start cleanup interval
    setInterval(() => {
      this.cleanupExpiredChallenges();
    }, this.CHALLENGE_CLEANUP_INTERVAL);
  }

  /**
   * Check if step-up authentication is required for an operation
   */
  static requiresStepUp(
    operationId: string,
    context: {
      userId: string;
      sessionId: string;
      tier: TierLevel;
      role?: Role;
      lastStepUpAt?: Date;
      isSecureContext: boolean;
      ipAddress: string;
      userAgent: string;
      deviceId?: string;
      riskScore?: number;
    }
  ): { required: boolean; requirement?: StepUpRequirement; reason?: string } {
    
    const requirement = STEP_UP_REQUIREMENTS[operationId];
    if (!requirement) {
      return { required: false, reason: 'No step-up requirement defined' };
    }

    // Check tier requirement
    if (requirement.minTier) {
      const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
      const userTierIndex = tierOrder.indexOf(context.tier);
      const requiredTierIndex = tierOrder.indexOf(requirement.minTier);
      
      if (userTierIndex < requiredTierIndex) {
        return { required: false, reason: `Requires ${requirement.minTier} tier or higher` };
      }
    }

    // Check role requirement
    if (requirement.requiredRole && context.role !== requirement.requiredRole) {
      return { required: false, reason: `Requires ${requirement.requiredRole} role` };
    }

    // Check secure context requirement
    if (requirement.requiresSecureContext && !context.isSecureContext) {
      return { required: true, requirement, reason: 'Secure context required' };
    }

    // Check if recent step-up exists and is still valid
    if (context.lastStepUpAt) {
      const stepUpAge = (Date.now() - context.lastStepUpAt.getTime()) / 1000;
      if (stepUpAge < requirement.maxAge) {
        return { required: false, reason: 'Recent step-up authentication still valid' };
      }
    }

    // Check risk score
    const riskScore = context.riskScore || 0;
    if (riskScore > 0.7 && !requirement.requiredMethods.includes('admin_approval')) {
      // High risk operations require additional security
      const enhancedRequirement = {
        ...requirement,
        minimumMethods: Math.max(requirement.minimumMethods, 2),
        maxAge: Math.min(requirement.maxAge, 5 * 60) // 5 minutes max for high risk
      };
      return { required: true, requirement: enhancedRequirement, reason: 'High risk operation detected' };
    }

    return { required: true, requirement, reason: 'Step-up authentication required' };
  }

  /**
   * Initiate step-up authentication challenge
   */
  static async initiateStepUp(params: {
    operationId: string;
    userId: string;
    sessionId: string;
    triggeredBy: string;
    originalRequestId: string;
    context: {
      tier: TierLevel;
      role?: Role;
      isSecureContext: boolean;
      ipAddress: string;
      userAgent: string;
      deviceId?: string;
      riskScore?: number;
    };
  }): Promise<StepUpResult> {
    
    const requirementCheck = this.requiresStepUp(params.operationId, {
      userId: params.userId,
      sessionId: params.sessionId,
      tier: params.context.tier,
      role: params.context.role,
      isSecureContext: params.context.isSecureContext,
      ipAddress: params.context.ipAddress,
      userAgent: params.context.userAgent,
      deviceId: params.context.deviceId,
      riskScore: params.context.riskScore
    });

    if (!requirementCheck.required || !requirementCheck.requirement) {
      return {
        success: false,
        error: requirementCheck.reason || 'Step-up not required'
      };
    }

    const requirement = requirementCheck.requirement;
    const challengeId = await this.generateChallengeId();
    
    // Calculate available methods based on user's capabilities
    const availableMethods = await this.getAvailableMethodsForUser(params.userId, requirement.allowedMethods);
    
    if (availableMethods.length < requirement.minimumMethods) {
      return {
        success: false,
        error: `Insufficient authentication methods available. Required: ${requirement.minimumMethods}, Available: ${availableMethods.length}`
      };
    }

    const challenge: StepUpChallenge = {
      challengeId,
      sessionId: params.sessionId,
      userId: params.userId,
      requirement,
      status: 'pending',
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + (requirement.maxAge * 1000)),
      attempts: [],
      maxAttempts: this.calculateMaxAttempts(requirement.severity),
      remainingAttempts: this.calculateMaxAttempts(requirement.severity),
      completedMethods: [],
      availableMethods,
      triggeredBy: params.triggeredBy,
      originalRequestId: params.originalRequestId,
      ipAddress: params.context.ipAddress,
      userAgent: params.context.userAgent,
      deviceId: params.context.deviceId,
      riskScore: params.context.riskScore || 0,
      securityFlags: this.calculateSecurityFlags(params.context),
      approvalRequired: requirement.requiresApproval || false
    };

    this.challenges.set(challengeId, challenge);

    // Log the initiation
    await AuditLogger.log({
      eventType: 'auth_step_up_required',
      action: 'initiate_step_up',
      resource: 'step_up_challenge',
      resourceId: challengeId,
      outcome: 'success',
      context: {
        userId: params.userId,
        sessionId: params.sessionId,
        tier: params.context.tier,
        role: params.context.role,
        ipAddress: params.context.ipAddress,
        userAgent: params.context.userAgent,
        deviceId: params.context.deviceId,
        riskScore: params.context.riskScore
      },
      description: `Step-up authentication required for ${params.operationId}`,
      metadata: {
        operationId: params.operationId,
        requirementId: requirement.id,
        availableMethods,
        minimumMethods: requirement.minimumMethods,
        maxAge: requirement.maxAge
      },
      sensitive: true
    });

    return {
      success: true,
      challengeId,
      nextRequiredMethod: this.getNextRequiredMethod(challenge),
      remainingAttempts: challenge.remainingAttempts,
      requiresApproval: challenge.approvalRequired
    };
  }

  /**
   * Submit authentication method for step-up challenge
   */
  static async submitStepUpMethod(
    challengeId: string,
    method: StepUpMethod,
    methodData: any,
    context: {
      ipAddress: string;
      userAgent: string;
      deviceFingerprint?: string;
    }
  ): Promise<StepUpResult> {
    
    const challenge = this.challenges.get(challengeId);
    if (!challenge) {
      return {
        success: false,
        error: 'Challenge not found or expired'
      };
    }

    // Check if challenge is still valid
    if (challenge.status !== 'pending' && challenge.status !== 'in_progress') {
      return {
        success: false,
        error: `Challenge is ${challenge.status}`
      };
    }

    if (new Date() > challenge.expiresAt) {
      challenge.status = 'expired';
      return {
        success: false,
        error: 'Challenge has expired'
      };
    }

    if (challenge.remainingAttempts <= 0) {
      challenge.status = 'failed';
      return {
        success: false,
        error: 'Maximum attempts exceeded'
      };
    }

    // Check if method is allowed
    if (!challenge.availableMethods.includes(method)) {
      return {
        success: false,
        error: `Method ${method} is not allowed for this challenge`
      };
    }

    // Check if method was already completed
    if (challenge.completedMethods.includes(method)) {
      return {
        success: false,
        error: `Method ${method} was already completed`
      };
    }

    challenge.status = 'in_progress';
    
    // Verify the authentication method
    const methodResult = await this.verifyStepUpMethod(method, methodData, challenge);
    
    const attempt: StepUpAttempt = {
      attemptId: await this.generateAttemptId(),
      method,
      timestamp: new Date(),
      success: methodResult.success,
      failureReason: methodResult.error,
      methodData: this.sanitizeMethodData(methodData),
      ipAddress: context.ipAddress,
      userAgent: context.userAgent,
      deviceFingerprint: context.deviceFingerprint
    };

    challenge.attempts.push(attempt);
    challenge.remainingAttempts--;

    if (methodResult.success) {
      challenge.completedMethods.push(method);
      
      // Check if we have enough methods completed
      const hasRequiredMethods = challenge.requirement.requiredMethods.every(
        required => challenge.completedMethods.includes(required)
      );
      
      const hasMinimumMethods = challenge.completedMethods.length >= challenge.requirement.minimumMethods;
      
      if (hasRequiredMethods && hasMinimumMethods) {
        // Check if approval is required
        if (challenge.approvalRequired && challenge.approvalStatus !== 'approved') {
          challenge.status = 'pending';
          
          await this.requestApproval(challenge);
          
          return {
            success: false,
            challengeId,
            requiresApproval: true,
            error: 'Approval required to complete step-up authentication'
          };
        } else {
          // Challenge completed successfully
          challenge.status = 'completed';
          challenge.completedAt = new Date();
          
          // Generate step-up proof token
          const token = await this.generateStepUpToken(challenge);
          
          // Update session with step-up timestamp
          await SessionManager.updateSessionSecurity(challenge.sessionId, {
            lastStepUpAt: new Date()
          });

          // Log successful completion
          await AuditLogger.log({
            eventType: 'auth_step_up_success',
            action: 'complete_step_up',
            resource: 'step_up_challenge',
            resourceId: challengeId,
            outcome: 'success',
            context: {
              userId: challenge.userId,
              sessionId: challenge.sessionId,
              ipAddress: context.ipAddress,
              userAgent: context.userAgent,
              deviceId: challenge.deviceId
            },
            description: `Step-up authentication completed successfully`,
            metadata: {
              operationId: challenge.requirement.id,
              completedMethods: challenge.completedMethods,
              attemptCount: challenge.attempts.length,
              timeToComplete: Date.now() - challenge.createdAt.getTime()
            },
            sensitive: true
          });

          return {
            success: true,
            challengeId,
            token,
            expiresAt: new Date(Date.now() + (challenge.requirement.maxAge * 1000)),
            completedMethods: challenge.completedMethods
          };
        }
      } else {
        // More methods required
        const nextMethod = this.getNextRequiredMethod(challenge);
        return {
          success: false,
          challengeId,
          nextRequiredMethod: nextMethod,
          remainingAttempts: challenge.remainingAttempts,
          error: nextMethod ? `Additional authentication method required: ${nextMethod}` : 'Additional authentication methods required'
        };
      }
    } else {
      // Method verification failed
      if (challenge.remainingAttempts <= 0) {
        challenge.status = 'failed';
        
        // Log failure
        await AuditLogger.log({
          eventType: 'auth_step_up_failure',
          action: 'step_up_failed',
          resource: 'step_up_challenge',
          resourceId: challengeId,
          outcome: 'failure',
          context: {
            userId: challenge.userId,
            sessionId: challenge.sessionId,
            ipAddress: context.ipAddress,
            userAgent: context.userAgent,
            deviceId: challenge.deviceId
          },
          description: `Step-up authentication failed after maximum attempts`,
          reasons: [methodResult.error || 'Unknown error'],
          metadata: {
            operationId: challenge.requirement.id,
            attemptCount: challenge.attempts.length,
            failedMethods: challenge.attempts.filter(a => !a.success).map(a => a.method)
          },
          sensitive: true
        });
      }

      return {
        success: false,
        challengeId,
        remainingAttempts: challenge.remainingAttempts,
        error: methodResult.error || 'Authentication method verification failed',
        retryAfter: challenge.remainingAttempts > 0 ? undefined : 300 // 5 minutes lockout
      };
    }
  }

  /**
   * Get challenge status
   */
  static getChallenge(challengeId: string): StepUpChallenge | null {
    return this.challenges.get(challengeId) || null;
  }

  /**
   * Cancel step-up challenge
   */
  static async cancelChallenge(
    challengeId: string,
    reason: string,
    context: {
      userId: string;
      ipAddress: string;
      userAgent: string;
    }
  ): Promise<boolean> {
    
    const challenge = this.challenges.get(challengeId);
    if (!challenge) {
      return false;
    }

    if (challenge.userId !== context.userId) {
      return false; // User can only cancel their own challenges
    }

    challenge.status = 'failed';

    // Log cancellation
    await AuditLogger.log({
      eventType: 'auth_step_up_failure',
      action: 'cancel_step_up',
      resource: 'step_up_challenge',
      resourceId: challengeId,
      outcome: 'failure',
      context: {
        userId: context.userId,
        sessionId: challenge.sessionId,
        ipAddress: context.ipAddress,
        userAgent: context.userAgent,
        deviceId: challenge.deviceId
      },
      description: `Step-up authentication cancelled by user`,
      reasons: [reason],
      metadata: {
        operationId: challenge.requirement.id,
        attemptCount: challenge.attempts.length,
        cancelReason: reason
      },
      sensitive: true
    });

    return true;
  }

  /**
   * Verify step-up proof token
   */
  static async verifyStepUpToken(
    token: string,
    operationId: string,
    context: {
      userId: string;
      sessionId: string;
    }
  ): Promise<{ valid: boolean; challengeId?: string; error?: string }> {
    
    try {
      // In production, this would verify a JWT token
      // For now, simple format: "stepup_${challengeId}_${timestamp}_${signature}"
      const parts = token.split('_');
      if (parts.length < 4 || parts[0] !== 'stepup') {
        return { valid: false, error: 'Invalid token format' };
      }

      const challengeId = parts[1];
      const timestamp = parseInt(parts[2]);
      
      const challenge = this.challenges.get(challengeId);
      if (!challenge) {
        return { valid: false, error: 'Challenge not found' };
      }

      if (challenge.userId !== context.userId || challenge.sessionId !== context.sessionId) {
        return { valid: false, error: 'Token ownership mismatch' };
      }

      if (challenge.status !== 'completed') {
        return { valid: false, error: 'Challenge not completed' };
      }

      // Check token age
      const tokenAge = Date.now() - timestamp;
      if (tokenAge > (challenge.requirement.maxAge * 1000)) {
        return { valid: false, error: 'Token expired' };
      }

      // Verify the operation matches the challenge requirement
      if (challenge.requirement.id !== operationId) {
        return { valid: false, error: 'Token not valid for this operation' };
      }

      return { valid: true, challengeId };
      
    } catch (error) {
      return { valid: false, error: 'Token verification failed' };
    }
  }

  // Private helper methods

  private static async generateChallengeId(): Promise<string> {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2);
    return `stepup_${timestamp}_${randomPart}`;
  }

  private static async generateAttemptId(): Promise<string> {
    const timestamp = Date.now().toString(36);
    const randomPart = Math.random().toString(36).substring(2);
    return `attempt_${timestamp}_${randomPart}`;
  }

  private static async getAvailableMethodsForUser(userId: string, allowedMethods: StepUpMethod[]): Promise<StepUpMethod[]> {
    // In production, this would check user's configured auth methods
    // For now, return a subset of allowed methods
    const userConfiguredMethods: StepUpMethod[] = ['password', 'passkey', 'totp', 'email'];
    return allowedMethods.filter(method => userConfiguredMethods.includes(method));
  }

  private static calculateMaxAttempts(severity: string): number {
    switch (severity) {
      case 'critical': return 3;
      case 'high': return 5;
      case 'medium': return 7;
      case 'low': return 10;
      default: return 5;
    }
  }

  private static calculateSecurityFlags(context: any): string[] {
    const flags: string[] = [];
    
    if (!context.isSecureContext) flags.push('insecure_context');
    if (context.riskScore > 0.7) flags.push('high_risk');
    if (!context.deviceId) flags.push('unknown_device');
    
    return flags;
  }

  private static getNextRequiredMethod(challenge: StepUpChallenge): StepUpMethod | undefined {
    // Find the next required method that hasn't been completed
    for (const required of challenge.requirement.requiredMethods) {
      if (!challenge.completedMethods.includes(required) && challenge.availableMethods.includes(required)) {
        return required;
      }
    }
    
    // If all required methods are done, check if we need more for minimum
    if (challenge.completedMethods.length < challenge.requirement.minimumMethods) {
      for (const available of challenge.availableMethods) {
        if (!challenge.completedMethods.includes(available)) {
          return available;
        }
      }
    }
    
    return undefined;
  }

  private static async verifyStepUpMethod(
    method: StepUpMethod,
    methodData: any,
    challenge: StepUpChallenge
  ): Promise<{ success: boolean; error?: string }> {
    
    // This would integrate with actual verification systems
    // For now, simulate verification logic
    
    switch (method) {
      case 'password':
        return { success: methodData.password === 'correct_password' };
      
      case 'totp':
        // Simulate TOTP verification with time window
        const validCodes = ['123456', '234567', '345678']; // Time-based codes
        return { 
          success: validCodes.includes(methodData.code),
          error: validCodes.includes(methodData.code) ? undefined : 'Invalid TOTP code'
        };
      
      case 'passkey':
        // Simulate passkey verification
        return { 
          success: methodData.signature === 'valid_signature',
          error: methodData.signature === 'valid_signature' ? undefined : 'Passkey verification failed'
        };
      
      case 'sms':
      case 'email':
        // Simulate code verification
        return { 
          success: methodData.code === '123456',
          error: methodData.code === '123456' ? undefined : 'Invalid verification code'
        };
      
      case 'backup_codes':
        // Simulate backup code verification
        const validBackupCodes = ['backup-123', 'backup-456', 'backup-789'];
        return { 
          success: validBackupCodes.includes(methodData.code),
          error: validBackupCodes.includes(methodData.code) ? undefined : 'Invalid backup code'
        };
      
      default:
        return { success: false, error: `Unsupported method: ${method}` };
    }
  }

  private static sanitizeMethodData(methodData: any): any {
    // Remove sensitive data from method data before storing
    const sanitized = { ...methodData };
    
    // Remove actual passwords, codes, etc.
    if (sanitized.password) sanitized.password = '[REDACTED]';
    if (sanitized.code) sanitized.code = '[REDACTED]';
    if (sanitized.signature) sanitized.signature = '[REDACTED]';
    
    return sanitized;
  }

  private static async generateStepUpToken(challenge: StepUpChallenge): Promise<string> {
    const timestamp = Date.now();
    const signature = await this.signTokenData(challenge.challengeId, timestamp, challenge.userId);
    return `stepup_${challenge.challengeId}_${timestamp}_${signature}`;
  }

  private static async signTokenData(challengeId: string, timestamp: number, userId: string): Promise<string> {
    // In production, use proper cryptographic signing
    const data = `${challengeId}:${timestamp}:${userId}`;
    const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(data));
    return Array.from(new Uint8Array(hash))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')
      .substring(0, 16);
  }

  private static async requestApproval(challenge: StepUpChallenge): Promise<void> {
    // In production, this would:
    // 1. Send notifications to approvers
    // 2. Create approval workflow entries
    // 3. Set up escalation timers
    
    console.log('APPROVAL_REQUEST:', {
      challengeId: challenge.challengeId,
      userId: challenge.userId,
      operation: challenge.requirement.id,
      approverRoles: challenge.requirement.approverRoles
    });
  }

  private static async cleanupExpiredChallenges(): Promise<void> {
    const now = new Date();
    let cleanedCount = 0;
    
    for (const [challengeId, challenge] of this.challenges.entries()) {
      if (now > challenge.expiresAt || 
          (challenge.status === 'completed' && now.getTime() - challenge.completedAt!.getTime() > 24 * 60 * 60 * 1000)) {
        this.challenges.delete(challengeId);
        cleanedCount++;
      }
    }
    
    if (cleanedCount > 0) {
      console.log(`Cleaned up ${cleanedCount} expired step-up challenges`);
    }
  }
}

export default StepUpAuthManager;