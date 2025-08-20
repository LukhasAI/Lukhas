/**
 * Tier System Configuration for ΛiD Authentication System
 * 
 * Implements the complete T1-T5 tier system with specific RPM/RPD limits,
 * permissions, features, and pricing tiers for LUKHAS AI.
 */

import { TierLevel, TIER_ENVELOPES } from './scopes';

export interface TierConfiguration {
  tier: TierLevel;
  name: string;
  description: string;
  tagline: string;
  
  // Rate limits
  maxRpm: number;           // Requests per minute
  maxRpd: number;           // Requests per day
  burstLimit: number;       // Burst allowance
  concurrentSessions: number; // Max concurrent sessions
  
  // Authentication features
  authMethods: AuthMethod[];
  maxPasskeys: number;
  backupCodesEnabled: boolean;
  sessionDuration: number;  // Max session duration in seconds
  
  // API and system access
  apiAccess: ApiAccessLevel[];
  maxApiKeys: number;
  webhooksEnabled: boolean;
  customIntegrationsEnabled: boolean;
  
  // Collaboration and organization
  maxTeamMembers: number;
  organizationFeaturesEnabled: boolean;
  rbacEnabled: boolean;
  ssoEnabled: boolean;
  scimEnabled: boolean;
  
  // Advanced features
  analyticsLevel: AnalyticsLevel;
  auditLogsRetention: number; // Days
  customModelAccess: boolean;
  prioritySupport: boolean;
  slaGuarantees: boolean;
  
  // Pricing and billing
  pricing: TierPricing;
  
  // Feature flags
  features: TierFeatures;
  
  // Limitations and quotas
  quotas: TierQuotas;
}

export type AuthMethod = 
  | 'password' 
  | 'magic_link' 
  | 'passkey' 
  | 'sso' 
  | 'backup_codes'
  | 'totp'
  | 'sms';

export type ApiAccessLevel = 
  | 'public_readonly'
  | 'personal_readwrite'
  | 'team_readwrite'
  | 'organization_admin'
  | 'enterprise_admin'
  | 'internal_admin';

export type AnalyticsLevel = 
  | 'basic'      // Basic usage metrics
  | 'standard'   // Detailed analytics
  | 'advanced'   // Real-time analytics + insights
  | 'enterprise' // Custom dashboards + AI insights
  | 'internal';  // Full system telemetry

export interface TierPricing {
  monthly: number;          // USD per month
  yearly: number;           // USD per year
  currency: string;
  freeTrial: boolean;
  trialDuration: number;    // Days
  customPricing: boolean;
  enterpriseContact: boolean;
}

export interface TierFeatures {
  // Core LUKHAS features
  matrizAccess: boolean;
  consciousnessEngine: boolean;
  dreamStates: boolean;
  quantumInspiredProcessing: boolean;
  bioInspiredAdaptation: boolean;
  
  // Identity and security
  advancedAuthentication: boolean;
  deviceBinding: boolean;
  sessionManagement: boolean;
  securityAlerts: boolean;
  complianceReports: boolean;
  
  // Collaboration
  teamWorkspaces: boolean;
  projectSharing: boolean;
  roleBasedAccess: boolean;
  guestAccess: boolean;
  
  // Development
  apiAccess: boolean;
  webhooks: boolean;
  customIntegrations: boolean;
  sdkAccess: boolean;
  sandboxEnvironment: boolean;
  
  // Enterprise
  singleSignOn: boolean;
  scimProvisioning: boolean;
  auditLogs: boolean;
  dataExport: boolean;
  customBranding: boolean;
  dedicatedSupport: boolean;
  
  // Advanced AI
  customModels: boolean;
  fineTuning: boolean;
  modelTraining: boolean;
  advancedAnalytics: boolean;
  realTimeInsights: boolean;
}

export interface TierQuotas {
  // Storage and data
  storageLimit: number;     // GB
  monthlyDataTransfer: number; // GB
  
  // Processing
  computeHours: number;     // Hours per month
  modelInferences: number;  // Per month
  
  // API usage
  apiCalls: number;         // Per month
  webhookDeliveries: number; // Per month
  
  // Content and projects
  maxProjects: number;
  maxModels: number;
  maxIntegrations: number;
  
  // Team and organization
  maxUsers: number;
  maxRoles: number;
  maxPolicies: number;
  
  // Support
  supportTickets: number;   // Per month
  responseTime: string;     // SLA
}

/**
 * Complete tier system configuration
 */
export const TIER_SYSTEM: Record<TierLevel, TierConfiguration> = {
  'T1': {
    tier: 'T1',
    name: 'Explorer',
    description: 'Perfect for individuals exploring LUKHAS AI capabilities',
    tagline: 'Discover the future of consciousness-driven AI',
    
    // Rate limits
    maxRpm: 30,
    maxRpd: 1000,
    burstLimit: 15,
    concurrentSessions: 2,
    
    // Authentication
    authMethods: ['password', 'magic_link'],
    maxPasskeys: 1,
    backupCodesEnabled: false,
    sessionDuration: 8 * 60 * 60, // 8 hours
    
    // API access
    apiAccess: ['public_readonly'],
    maxApiKeys: 1,
    webhooksEnabled: false,
    customIntegrationsEnabled: false,
    
    // Collaboration
    maxTeamMembers: 1,
    organizationFeaturesEnabled: false,
    rbacEnabled: false,
    ssoEnabled: false,
    scimEnabled: false,
    
    // Advanced features
    analyticsLevel: 'basic',
    auditLogsRetention: 7,
    customModelAccess: false,
    prioritySupport: false,
    slaGuarantees: false,
    
    // Pricing
    pricing: {
      monthly: 0,
      yearly: 0,
      currency: 'USD',
      freeTrial: false,
      trialDuration: 0,
      customPricing: false,
      enterpriseContact: false
    },
    
    // Features
    features: {
      matrizAccess: true,
      consciousnessEngine: false,
      dreamStates: false,
      quantumInspiredProcessing: false,
      bioInspiredAdaptation: false,
      advancedAuthentication: false,
      deviceBinding: false,
      sessionManagement: true,
      securityAlerts: false,
      complianceReports: false,
      teamWorkspaces: false,
      projectSharing: false,
      roleBasedAccess: false,
      guestAccess: false,
      apiAccess: true,
      webhooks: false,
      customIntegrations: false,
      sdkAccess: false,
      sandboxEnvironment: true,
      singleSignOn: false,
      scimProvisioning: false,
      auditLogs: false,
      dataExport: false,
      customBranding: false,
      dedicatedSupport: false,
      customModels: false,
      fineTuning: false,
      modelTraining: false,
      advancedAnalytics: false,
      realTimeInsights: false
    },
    
    // Quotas
    quotas: {
      storageLimit: 1,
      monthlyDataTransfer: 10,
      computeHours: 5,
      modelInferences: 1000,
      apiCalls: 1000,
      webhookDeliveries: 0,
      maxProjects: 3,
      maxModels: 1,
      maxIntegrations: 0,
      maxUsers: 1,
      maxRoles: 1,
      maxPolicies: 1,
      supportTickets: 2,
      responseTime: '72h'
    }
  },

  'T2': {
    tier: 'T2',
    name: 'Builder',
    description: 'For developers building personal projects with LUKHAS AI',
    tagline: 'Build intelligent applications with consciousness',
    
    // Rate limits
    maxRpm: 60,
    maxRpd: 5000,
    burstLimit: 45,
    concurrentSessions: 5,
    
    // Authentication
    authMethods: ['password', 'magic_link', 'passkey', 'totp'],
    maxPasskeys: 3,
    backupCodesEnabled: true,
    sessionDuration: 12 * 60 * 60, // 12 hours
    
    // API access
    apiAccess: ['public_readonly', 'personal_readwrite'],
    maxApiKeys: 3,
    webhooksEnabled: true,
    customIntegrationsEnabled: false,
    
    // Collaboration
    maxTeamMembers: 1,
    organizationFeaturesEnabled: false,
    rbacEnabled: false,
    ssoEnabled: false,
    scimEnabled: false,
    
    // Advanced features
    analyticsLevel: 'standard',
    auditLogsRetention: 30,
    customModelAccess: false,
    prioritySupport: false,
    slaGuarantees: false,
    
    // Pricing
    pricing: {
      monthly: 29,
      yearly: 290, // 2 months free
      currency: 'USD',
      freeTrial: true,
      trialDuration: 14,
      customPricing: false,
      enterpriseContact: false
    },
    
    // Features
    features: {
      matrizAccess: true,
      consciousnessEngine: true,
      dreamStates: true,
      quantumInspiredProcessing: true,
      bioInspiredAdaptation: true,
      advancedAuthentication: true,
      deviceBinding: true,
      sessionManagement: true,
      securityAlerts: true,
      complianceReports: false,
      teamWorkspaces: false,
      projectSharing: true,
      roleBasedAccess: false,
      guestAccess: false,
      apiAccess: true,
      webhooks: true,
      customIntegrations: false,
      sdkAccess: true,
      sandboxEnvironment: true,
      singleSignOn: false,
      scimProvisioning: false,
      auditLogs: true,
      dataExport: true,
      customBranding: false,
      dedicatedSupport: false,
      customModels: false,
      fineTuning: false,
      modelTraining: false,
      advancedAnalytics: true,
      realTimeInsights: false
    },
    
    // Quotas
    quotas: {
      storageLimit: 10,
      monthlyDataTransfer: 100,
      computeHours: 50,
      modelInferences: 10000,
      apiCalls: 5000,
      webhookDeliveries: 1000,
      maxProjects: 10,
      maxModels: 3,
      maxIntegrations: 3,
      maxUsers: 1,
      maxRoles: 3,
      maxPolicies: 5,
      supportTickets: 5,
      responseTime: '48h'
    }
  },

  'T3': {
    tier: 'T3',
    name: 'Studio',
    description: 'For teams collaborating on AI-powered projects',
    tagline: 'Orchestrate intelligence across your team',
    
    // Rate limits
    maxRpm: 120,
    maxRpd: 20000,
    burstLimit: 120,
    concurrentSessions: 20,
    
    // Authentication
    authMethods: ['password', 'magic_link', 'passkey', 'sso', 'totp', 'backup_codes'],
    maxPasskeys: 5,
    backupCodesEnabled: true,
    sessionDuration: 24 * 60 * 60, // 24 hours
    
    // API access
    apiAccess: ['public_readonly', 'personal_readwrite', 'team_readwrite'],
    maxApiKeys: 10,
    webhooksEnabled: true,
    customIntegrationsEnabled: true,
    
    // Collaboration
    maxTeamMembers: 10,
    organizationFeaturesEnabled: true,
    rbacEnabled: true,
    ssoEnabled: true,
    scimEnabled: false,
    
    // Advanced features
    analyticsLevel: 'advanced',
    auditLogsRetention: 90,
    customModelAccess: true,
    prioritySupport: true,
    slaGuarantees: false,
    
    // Pricing
    pricing: {
      monthly: 99,
      yearly: 990, // 2 months free
      currency: 'USD',
      freeTrial: true,
      trialDuration: 30,
      customPricing: false,
      enterpriseContact: false
    },
    
    // Features
    features: {
      matrizAccess: true,
      consciousnessEngine: true,
      dreamStates: true,
      quantumInspiredProcessing: true,
      bioInspiredAdaptation: true,
      advancedAuthentication: true,
      deviceBinding: true,
      sessionManagement: true,
      securityAlerts: true,
      complianceReports: true,
      teamWorkspaces: true,
      projectSharing: true,
      roleBasedAccess: true,
      guestAccess: true,
      apiAccess: true,
      webhooks: true,
      customIntegrations: true,
      sdkAccess: true,
      sandboxEnvironment: true,
      singleSignOn: true,
      scimProvisioning: false,
      auditLogs: true,
      dataExport: true,
      customBranding: true,
      dedicatedSupport: false,
      customModels: true,
      fineTuning: true,
      modelTraining: false,
      advancedAnalytics: true,
      realTimeInsights: true
    },
    
    // Quotas
    quotas: {
      storageLimit: 100,
      monthlyDataTransfer: 1000,
      computeHours: 200,
      modelInferences: 100000,
      apiCalls: 20000,
      webhookDeliveries: 5000,
      maxProjects: 50,
      maxModels: 10,
      maxIntegrations: 10,
      maxUsers: 10,
      maxRoles: 10,
      maxPolicies: 20,
      supportTickets: 10,
      responseTime: '24h'
    }
  },

  'T4': {
    tier: 'T4',
    name: 'Enterprise',
    description: 'For large organizations with enterprise requirements',
    tagline: 'Scale consciousness across your enterprise',
    
    // Rate limits
    maxRpm: 300,
    maxRpd: 100000,
    burstLimit: 450,
    concurrentSessions: 100,
    
    // Authentication
    authMethods: ['password', 'magic_link', 'passkey', 'sso', 'totp', 'backup_codes', 'sms'],
    maxPasskeys: 10,
    backupCodesEnabled: true,
    sessionDuration: 48 * 60 * 60, // 48 hours
    
    // API access
    apiAccess: ['public_readonly', 'personal_readwrite', 'team_readwrite', 'organization_admin'],
    maxApiKeys: 50,
    webhooksEnabled: true,
    customIntegrationsEnabled: true,
    
    // Collaboration
    maxTeamMembers: 100,
    organizationFeaturesEnabled: true,
    rbacEnabled: true,
    ssoEnabled: true,
    scimEnabled: true,
    
    // Advanced features
    analyticsLevel: 'enterprise',
    auditLogsRetention: 365,
    customModelAccess: true,
    prioritySupport: true,
    slaGuarantees: true,
    
    // Pricing
    pricing: {
      monthly: 499,
      yearly: 4990, // 2 months free
      currency: 'USD',
      freeTrial: true,
      trialDuration: 30,
      customPricing: true,
      enterpriseContact: true
    },
    
    // Features
    features: {
      matrizAccess: true,
      consciousnessEngine: true,
      dreamStates: true,
      quantumInspiredProcessing: true,
      bioInspiredAdaptation: true,
      advancedAuthentication: true,
      deviceBinding: true,
      sessionManagement: true,
      securityAlerts: true,
      complianceReports: true,
      teamWorkspaces: true,
      projectSharing: true,
      roleBasedAccess: true,
      guestAccess: true,
      apiAccess: true,
      webhooks: true,
      customIntegrations: true,
      sdkAccess: true,
      sandboxEnvironment: true,
      singleSignOn: true,
      scimProvisioning: true,
      auditLogs: true,
      dataExport: true,
      customBranding: true,
      dedicatedSupport: true,
      customModels: true,
      fineTuning: true,
      modelTraining: true,
      advancedAnalytics: true,
      realTimeInsights: true
    },
    
    // Quotas
    quotas: {
      storageLimit: 1000,
      monthlyDataTransfer: 10000,
      computeHours: 1000,
      modelInferences: 1000000,
      apiCalls: 100000,
      webhookDeliveries: 50000,
      maxProjects: 500,
      maxModels: 50,
      maxIntegrations: 50,
      maxUsers: 100,
      maxRoles: 50,
      maxPolicies: 100,
      supportTickets: 50,
      responseTime: '4h'
    }
  },

  'T5': {
    tier: 'T5',
    name: 'Core Team',
    description: 'Internal LUKHAS team with full system access',
    tagline: 'Architect the future of consciousness',
    
    // Rate limits
    maxRpm: 1000,
    maxRpd: 1000000,
    burstLimit: 2000,
    concurrentSessions: 1000,
    
    // Authentication
    authMethods: ['password', 'magic_link', 'passkey', 'sso', 'totp', 'backup_codes', 'sms'],
    maxPasskeys: 20,
    backupCodesEnabled: true,
    sessionDuration: 7 * 24 * 60 * 60, // 7 days
    
    // API access
    apiAccess: ['public_readonly', 'personal_readwrite', 'team_readwrite', 'organization_admin', 'enterprise_admin', 'internal_admin'],
    maxApiKeys: 200,
    webhooksEnabled: true,
    customIntegrationsEnabled: true,
    
    // Collaboration
    maxTeamMembers: 1000,
    organizationFeaturesEnabled: true,
    rbacEnabled: true,
    ssoEnabled: true,
    scimEnabled: true,
    
    // Advanced features
    analyticsLevel: 'internal',
    auditLogsRetention: 2555, // 7 years
    customModelAccess: true,
    prioritySupport: true,
    slaGuarantees: true,
    
    // Pricing
    pricing: {
      monthly: 0, // Internal use
      yearly: 0,
      currency: 'USD',
      freeTrial: false,
      trialDuration: 0,
      customPricing: false,
      enterpriseContact: false
    },
    
    // Features (all enabled)
    features: {
      matrizAccess: true,
      consciousnessEngine: true,
      dreamStates: true,
      quantumInspiredProcessing: true,
      bioInspiredAdaptation: true,
      advancedAuthentication: true,
      deviceBinding: true,
      sessionManagement: true,
      securityAlerts: true,
      complianceReports: true,
      teamWorkspaces: true,
      projectSharing: true,
      roleBasedAccess: true,
      guestAccess: true,
      apiAccess: true,
      webhooks: true,
      customIntegrations: true,
      sdkAccess: true,
      sandboxEnvironment: true,
      singleSignOn: true,
      scimProvisioning: true,
      auditLogs: true,
      dataExport: true,
      customBranding: true,
      dedicatedSupport: true,
      customModels: true,
      fineTuning: true,
      modelTraining: true,
      advancedAnalytics: true,
      realTimeInsights: true
    },
    
    // Quotas (unlimited or very high)
    quotas: {
      storageLimit: 10000,
      monthlyDataTransfer: 100000,
      computeHours: 10000,
      modelInferences: 100000000,
      apiCalls: 1000000,
      webhookDeliveries: 1000000,
      maxProjects: 10000,
      maxModels: 1000,
      maxIntegrations: 1000,
      maxUsers: 1000,
      maxRoles: 1000,
      maxPolicies: 10000,
      supportTickets: 1000,
      responseTime: '1h'
    }
  }
};

/**
 * Tier management utilities
 */
export class TierManager {
  /**
   * Get tier configuration
   */
  static getTierConfig(tier: TierLevel): TierConfiguration {
    return TIER_SYSTEM[tier];
  }

  /**
   * Check if feature is enabled for tier
   */
  static isFeatureEnabled(tier: TierLevel, feature: keyof TierFeatures): boolean {
    const config = this.getTierConfig(tier);
    return config.features[feature];
  }

  /**
   * Check if auth method is allowed for tier
   */
  static isAuthMethodAllowed(tier: TierLevel, method: AuthMethod): boolean {
    const config = this.getTierConfig(tier);
    return config.authMethods.includes(method);
  }

  /**
   * Check if API access level is allowed for tier
   */
  static hasApiAccess(tier: TierLevel, accessLevel: ApiAccessLevel): boolean {
    const config = this.getTierConfig(tier);
    return config.apiAccess.includes(accessLevel);
  }

  /**
   * Get rate limits for tier
   */
  static getRateLimits(tier: TierLevel): {
    rpm: number;
    rpd: number;
    burst: number;
    concurrent: number;
  } {
    const config = this.getTierConfig(tier);
    return {
      rpm: config.maxRpm,
      rpd: config.maxRpd,
      burst: config.burstLimit,
      concurrent: config.concurrentSessions
    };
  }

  /**
   * Check if quota limit is exceeded
   */
  static isQuotaExceeded(
    tier: TierLevel,
    quotaType: keyof TierQuotas,
    currentUsage: number
  ): boolean {
    const config = this.getTierConfig(tier);
    const limit = config.quotas[quotaType] as number;
    return currentUsage >= limit;
  }

  /**
   * Get remaining quota
   */
  static getRemainingQuota(
    tier: TierLevel,
    quotaType: keyof TierQuotas,
    currentUsage: number
  ): number {
    const config = this.getTierConfig(tier);
    const limit = config.quotas[quotaType] as number;
    return Math.max(0, limit - currentUsage);
  }

  /**
   * Check if tier can be upgraded
   */
  static canUpgradeTo(currentTier: TierLevel, targetTier: TierLevel): boolean {
    const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
    const currentIndex = tierOrder.indexOf(currentTier);
    const targetIndex = tierOrder.indexOf(targetTier);
    
    return targetIndex > currentIndex;
  }

  /**
   * Get next available tier for upgrade
   */
  static getNextTier(currentTier: TierLevel): TierLevel | null {
    const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
    const currentIndex = tierOrder.indexOf(currentTier);
    
    if (currentIndex < tierOrder.length - 1) {
      return tierOrder[currentIndex + 1];
    }
    
    return null; // Already at highest tier
  }

  /**
   * Calculate tier comparison
   */
  static compareTiers(
    tier1: TierLevel,
    tier2: TierLevel
  ): { 
    upgrades: string[];
    downgrades: string[];
    pricing: { difference: number; savings?: number };
  } {
    const config1 = this.getTierConfig(tier1);
    const config2 = this.getTierConfig(tier2);
    
    const upgrades: string[] = [];
    const downgrades: string[] = [];
    
    // Compare key metrics
    if (config2.maxRpm > config1.maxRpm) {
      upgrades.push(`Rate limit: ${config1.maxRpm} → ${config2.maxRpm} RPM`);
    } else if (config2.maxRpm < config1.maxRpm) {
      downgrades.push(`Rate limit: ${config1.maxRpm} → ${config2.maxRpm} RPM`);
    }
    
    if (config2.maxTeamMembers > config1.maxTeamMembers) {
      upgrades.push(`Team size: ${config1.maxTeamMembers} → ${config2.maxTeamMembers} members`);
    } else if (config2.maxTeamMembers < config1.maxTeamMembers) {
      downgrades.push(`Team size: ${config1.maxTeamMembers} → ${config2.maxTeamMembers} members`);
    }
    
    // Compare features
    for (const [feature, enabled2] of Object.entries(config2.features)) {
      const enabled1 = config1.features[feature as keyof TierFeatures];
      if (enabled2 && !enabled1) {
        upgrades.push(`New feature: ${feature}`);
      } else if (!enabled2 && enabled1) {
        downgrades.push(`Lost feature: ${feature}`);
      }
    }
    
    const priceDifference = config2.pricing.monthly - config1.pricing.monthly;
    const yearlyDifference = config2.pricing.yearly - config1.pricing.yearly;
    const yearlySavings = (config2.pricing.monthly * 12) - config2.pricing.yearly;
    
    return {
      upgrades,
      downgrades,
      pricing: {
        difference: priceDifference,
        savings: yearlySavings > 0 ? yearlySavings : undefined
      }
    };
  }

  /**
   * Get recommended tier based on usage
   */
  static getRecommendedTier(usage: {
    monthlyApiCalls: number;
    teamSize: number;
    storageNeeded: number;
    requiresSSO: boolean;
    requiresCustomModels: boolean;
  }): { 
    recommended: TierLevel;
    reasons: string[];
    alternatives: TierLevel[];
  } {
    const reasons: string[] = [];
    const alternatives: TierLevel[] = [];
    
    // Start with T1 and upgrade based on requirements
    let recommended: TierLevel = 'T1';
    
    // Check API usage
    if (usage.monthlyApiCalls > 1000) {
      recommended = 'T2';
      reasons.push(`API usage (${usage.monthlyApiCalls}/month) exceeds T1 limit`);
      
      if (usage.monthlyApiCalls > 5000) {
        recommended = 'T3';
        reasons.push('High API usage requires T3 or higher');
        
        if (usage.monthlyApiCalls > 20000) {
          recommended = 'T4';
          reasons.push('Enterprise-level API usage');
        }
      }
    }
    
    // Check team size
    if (usage.teamSize > 1) {
      if (recommended === 'T1') recommended = 'T3';
      reasons.push(`Team size (${usage.teamSize}) requires collaboration features`);
      
      if (usage.teamSize > 10) {
        recommended = 'T4';
        reasons.push('Large team requires enterprise features');
      }
    }
    
    // Check storage requirements
    if (usage.storageNeeded > 10) {
      if (recommended === 'T1' || recommended === 'T2') {
        recommended = 'T3';
        reasons.push(`Storage needs (${usage.storageNeeded}GB) require T3 or higher`);
      }
      
      if (usage.storageNeeded > 100) {
        recommended = 'T4';
        reasons.push('High storage requirements need enterprise tier');
      }
    }
    
    // Check enterprise features
    if (usage.requiresSSO) {
      if (recommended === 'T1' || recommended === 'T2') {
        recommended = 'T3';
        reasons.push('SSO requires T3 or higher');
      }
    }
    
    if (usage.requiresCustomModels) {
      if (recommended === 'T1' || recommended === 'T2') {
        recommended = 'T3';
        reasons.push('Custom models require T3 or higher');
      }
    }
    
    // Suggest alternatives
    const tierOrder: TierLevel[] = ['T1', 'T2', 'T3', 'T4', 'T5'];
    const currentIndex = tierOrder.indexOf(recommended);
    
    if (currentIndex > 0) {
      alternatives.push(tierOrder[currentIndex - 1]);
    }
    if (currentIndex < tierOrder.length - 1) {
      alternatives.push(tierOrder[currentIndex + 1]);
    }
    
    return { recommended, reasons, alternatives };
  }
}

export default TierManager;