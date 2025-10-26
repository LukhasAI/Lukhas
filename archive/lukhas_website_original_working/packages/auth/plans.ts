/**
 * LUKHAS AI Plan System - OpenAI-Style Access Levels
 * 
 * Aligns with industry-standard naming conventions while maintaining
 * LUKHAS AI's unique Trinity Framework and consciousness features.
 */

export type Plan = 'free' | 'plus' | 'team' | 'enterprise' | 'core';

/**
 * Plan feature configuration matrix
 * Defines what each plan tier can access
 */
export const PLAN_FEATURES: Record<Plan, {
  sso: 'none' | 'team' | 'enterprise';
  scim: boolean;
  rbac: 'basic' | 'custom';
  credits: 'none' | 'per-seat' | 'pooled';
  adminApi: boolean;
  analytics: 'none' | 'workspace';
  // LUKHAS-specific features
  matrizAccess: boolean;
  consciousnessEngine: boolean;
  dreamStates: boolean;
  quantumInspired: boolean;
  bioInspired: boolean;
  guardianSystem: boolean;
}> = {
  free: { 
    sso: 'none',       
    scim: false, 
    rbac: 'basic',  
    credits: 'none',     
    adminApi: false, 
    analytics: 'none',
    // LUKHAS features
    matrizAccess: true,
    consciousnessEngine: false,
    dreamStates: false,
    quantumInspired: false,
    bioInspired: false,
    guardianSystem: true  // Basic ethics always enabled
  },
  
  plus: { 
    sso: 'none',       
    scim: false, 
    rbac: 'basic',  
    credits: 'none',     
    adminApi: false, 
    analytics: 'none',
    // LUKHAS features
    matrizAccess: true,
    consciousnessEngine: true,
    dreamStates: true,
    quantumInspired: true,
    bioInspired: true,
    guardianSystem: true
  },
  
  team: { 
    sso: 'team',       
    scim: false, 
    rbac: 'basic',  
    credits: 'per-seat', 
    adminApi: false, 
    analytics: 'workspace',
    // LUKHAS features
    matrizAccess: true,
    consciousnessEngine: true,
    dreamStates: true,
    quantumInspired: true,
    bioInspired: true,
    guardianSystem: true
  },
  
  enterprise: { 
    sso: 'enterprise', 
    scim: true,  
    rbac: 'custom', 
    credits: 'pooled',   
    adminApi: true,  
    analytics: 'workspace',
    // LUKHAS features
    matrizAccess: true,
    consciousnessEngine: true,
    dreamStates: true,
    quantumInspired: true,
    bioInspired: true,
    guardianSystem: true
  },
  
  core: { 
    sso: 'enterprise', 
    scim: true,  
    rbac: 'custom', 
    credits: 'pooled',   
    adminApi: true,  
    analytics: 'workspace',
    // LUKHAS features (all enabled for internal team)
    matrizAccess: true,
    consciousnessEngine: true,
    dreamStates: true,
    quantumInspired: true,
    bioInspired: true,
    guardianSystem: true
  }
};

/**
 * Rate limiting envelopes per plan
 * RPM = Requests Per Minute
 * RPD = Requests Per Day
 */
export const RATE_ENVELOPES = {
  free:       { rpm: 30,   rpd: 1_000,     burst: 15,    concurrent: 2 },
  plus:       { rpm: 60,   rpd: 5_000,     burst: 45,    concurrent: 5 },
  team:       { rpm: 120,  rpd: 20_000,    burst: 120,   concurrent: 20 },
  enterprise: { rpm: 300,  rpd: 100_000,   burst: 450,   concurrent: 100 },
  core:       { rpm: 1000, rpd: 1_000_000, burst: 2000,  concurrent: 1000 },
} as const;

/**
 * Pricing configuration per plan
 */
export const PLAN_PRICING = {
  free: {
    monthly: 0,
    yearly: 0,
    currency: 'USD',
    trial: false,
    trialDays: 0
  },
  plus: {
    monthly: 29,
    yearly: 290, // 2 months free
    currency: 'USD',
    trial: true,
    trialDays: 14
  },
  team: {
    monthly: 99,
    yearly: 990, // 2 months free
    currency: 'USD',
    trial: true,
    trialDays: 30
  },
  enterprise: {
    monthly: 499,
    yearly: 4990, // 2 months free
    currency: 'USD',
    trial: true,
    trialDays: 30,
    customPricing: true
  },
  core: {
    monthly: 0, // Internal use
    yearly: 0,
    currency: 'USD',
    trial: false,
    trialDays: 0
  }
} as const;

/**
 * Legacy tier mapping for backwards compatibility
 * Maps old T1-T5 naming to new OpenAI-style naming
 */
export const LEGACY_TIER_MAPPING = {
  'T1': 'free',
  'T2': 'plus',
  'T3': 'team',
  'T4': 'enterprise',
  'T5': 'core'
} as const;

/**
 * Reverse mapping for when we need to convert back
 */
export const PLAN_TO_TIER_MAPPING = {
  'free': 'T1',
  'plus': 'T2',
  'team': 'T3',
  'enterprise': 'T4',
  'core': 'T5'
} as const;

/**
 * Authentication methods allowed per plan
 */
export const PLAN_AUTH_METHODS: Record<Plan, {
  password: boolean;
  magicLink: boolean;
  passkey: boolean;
  sso: boolean;
  totp: boolean;
  backupCodes: boolean;
}> = {
  free: {
    password: false,  // Passwordless by default
    magicLink: true,
    passkey: true,
    sso: false,
    totp: false,
    backupCodes: false
  },
  plus: {
    password: false,
    magicLink: true,
    passkey: true,
    sso: false,
    totp: true,
    backupCodes: true
  },
  team: {
    password: false,
    magicLink: true,
    passkey: true,
    sso: true,  // Team SSO enabled
    totp: true,
    backupCodes: true
  },
  enterprise: {
    password: false,
    magicLink: true,
    passkey: true,
    sso: true,  // Enterprise SSO required
    totp: true,
    backupCodes: true
  },
  core: {
    password: false,
    magicLink: true,
    passkey: true,
    sso: true,  // Core team SSO required
    totp: true,
    backupCodes: true
  }
};

/**
 * Plan management utilities
 */
export class PlanManager {
  /**
   * Check if a feature is enabled for a plan
   */
  static isFeatureEnabled(plan: Plan, feature: keyof typeof PLAN_FEATURES[Plan]): boolean {
    const features = PLAN_FEATURES[plan];
    const value = features[feature];
    
    // Handle different value types
    if (typeof value === 'boolean') {
      return value;
    }
    if (typeof value === 'string') {
      return value !== 'none';
    }
    return false;
  }

  /**
   * Get rate limits for a plan
   */
  static getRateLimits(plan: Plan) {
    return RATE_ENVELOPES[plan];
  }

  /**
   * Check if SSO is required for a plan
   */
  static isSSORequired(plan: Plan): boolean {
    // Enterprise and Core require SSO when configured
    return plan === 'enterprise' || plan === 'core';
  }

  /**
   * Check if SCIM is available for a plan
   */
  static isSCIMAvailable(plan: Plan): boolean {
    return PLAN_FEATURES[plan].scim;
  }

  /**
   * Check if a plan can be upgraded to another
   */
  static canUpgradeTo(currentPlan: Plan, targetPlan: Plan): boolean {
    const planOrder: Plan[] = ['free', 'plus', 'team', 'enterprise', 'core'];
    const currentIndex = planOrder.indexOf(currentPlan);
    const targetIndex = planOrder.indexOf(targetPlan);
    
    // Core is internal only, cannot upgrade to it normally
    if (targetPlan === 'core') {
      return false;
    }
    
    return targetIndex > currentIndex;
  }

  /**
   * Get the next available upgrade plan
   */
  static getNextPlan(currentPlan: Plan): Plan | null {
    const planOrder: Plan[] = ['free', 'plus', 'team', 'enterprise'];
    const currentIndex = planOrder.indexOf(currentPlan);
    
    if (currentIndex < planOrder.length - 1) {
      return planOrder[currentIndex + 1];
    }
    
    return null;
  }

  /**
   * Convert legacy tier to new plan
   */
  static fromLegacyTier(tier: keyof typeof LEGACY_TIER_MAPPING): Plan {
    return LEGACY_TIER_MAPPING[tier] as Plan;
  }

  /**
   * Convert plan to legacy tier (for backwards compatibility)
   */
  static toLegacyTier(plan: Plan): string {
    return PLAN_TO_TIER_MAPPING[plan];
  }

  /**
   * Check if plan requires step-up authentication for an action
   */
  static requiresStepUp(plan: Plan, action: 'billing' | 'api-keys' | 'org-admin' | 'security'): boolean {
    // All plans require step-up for sensitive operations
    const sensitiveActions = ['billing', 'api-keys', 'org-admin', 'security'];
    return sensitiveActions.includes(action);
  }

  /**
   * Get plan comparison for upgrade flow
   */
  static comparePlans(currentPlan: Plan, targetPlan: Plan): {
    upgrades: string[];
    pricing: { difference: number; savings?: number };
  } {
    const currentFeatures = PLAN_FEATURES[currentPlan];
    const targetFeatures = PLAN_FEATURES[targetPlan];
    const upgrades: string[] = [];
    
    // Check SSO upgrade
    if (targetFeatures.sso !== 'none' && currentFeatures.sso === 'none') {
      upgrades.push('Single Sign-On (SSO) support');
    }
    
    // Check SCIM upgrade
    if (targetFeatures.scim && !currentFeatures.scim) {
      upgrades.push('SCIM user provisioning');
    }
    
    // Check RBAC upgrade
    if (targetFeatures.rbac === 'custom' && currentFeatures.rbac === 'basic') {
      upgrades.push('Custom role-based access control');
    }
    
    // Check analytics upgrade
    if (targetFeatures.analytics === 'workspace' && currentFeatures.analytics === 'none') {
      upgrades.push('Workspace analytics and insights');
    }
    
    // Check admin API
    if (targetFeatures.adminApi && !currentFeatures.adminApi) {
      upgrades.push('Admin API access');
    }
    
    // Check rate limits
    const currentLimits = RATE_ENVELOPES[currentPlan];
    const targetLimits = RATE_ENVELOPES[targetPlan];
    if (targetLimits.rpm > currentLimits.rpm) {
      upgrades.push(`Rate limit: ${currentLimits.rpm} → ${targetLimits.rpm} RPM`);
    }
    
    // Calculate pricing difference
    const currentPricing = PLAN_PRICING[currentPlan];
    const targetPricing = PLAN_PRICING[targetPlan];
    const monthlyDifference = targetPricing.monthly - currentPricing.monthly;
    const yearlyDifference = targetPricing.yearly - currentPricing.yearly;
    const yearlySavings = (targetPricing.monthly * 12) - targetPricing.yearly;
    
    return {
      upgrades,
      pricing: {
        difference: monthlyDifference,
        savings: yearlySavings > 0 ? yearlySavings : undefined
      }
    };
  }
}

export default PlanManager;