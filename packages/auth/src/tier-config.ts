/**
 * ΛiD Authentication System - Tier Configuration
 *
 * Complete T1-T5 tier system configuration with proper RPM/RPD limits and scope definitions
 * Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)
 */

import {
  UserTier,
  AuthScope,
  UserRole,
  RateLimitConfig,
  Permission,
  AuthConfig
} from '../types/auth.types';
import { Tier, TIER_ENVELOPES, ROLE_SCOPES } from './scopes';
import { TIER_RATE_LIMITS } from './rate-limits';

// =============================================================================
// TIER SYSTEM CONFIGURATION
// =============================================================================

/**
 * Comprehensive tier definitions with features and limitations
 */
export interface TierDefinition {
  id: UserTier;
  name: string;
  description: string;
  price: {
    monthly: number;
    yearly: number;
    currency: string;
  };
  features: {
    general: string[];
    api: string[];
    consciousness: string[];
    memory: string[];
    orchestration: string[];
    security: string[];
  };
  limits: {
    rateLimits: RateLimitConfig;
    storage: {
      memory: string;
      documents: string;
      uploads: string;
    };
    usage: {
      apiCalls: string;
      consciousnessQueries: string;
      orchestrationRuns: string;
    };
    support: string;
  };
  scopes: AuthScope[];
  upgrade: {
    available: boolean;
    nextTier?: UserTier;
    benefits: string[];
  };
}

/**
 * Complete tier system configuration
 */
export const TIER_DEFINITIONS: Record<UserTier, TierDefinition> = {
  T1: {
    id: 'T1',
    name: 'Explorer',
    description: 'Public access for exploration and learning',
    price: {
      monthly: 0,
      yearly: 0,
      currency: 'USD'
    },
    features: {
      general: [
        'Access to public documentation',
        'Basic demos and examples',
        'Community forum access',
        'Read-only consciousness exploration'
      ],
      api: [
        'Limited API read access',
        'Basic identity features',
        'Public endpoint access'
      ],
      consciousness: [
        'Consciousness state viewing',
        'Basic dream visualization',
        'Public memory access'
      ],
      memory: [
        'Read-only memory access',
        'Basic pattern viewing',
        'Public fold exploration'
      ],
      orchestration: [
        'View public orchestrations',
        'Basic workflow viewing'
      ],
      security: [
        'Basic authentication',
        'Standard rate limiting',
        'Community guidelines protection'
      ]
    },
    limits: {
      rateLimits: TIER_RATE_LIMITS.T1,
      storage: {
        memory: '0 MB',
        documents: '0',
        uploads: '0 MB'
      },
      usage: {
        apiCalls: '1,000/day',
        consciousnessQueries: '50/day',
        orchestrationRuns: '0/day'
      },
      support: 'Community forum only'
    },
    scopes: TIER_ENVELOPES.T1,
    upgrade: {
      available: true,
      nextTier: 'T2',
      benefits: [
        'Personal projects and API write access',
        'Consciousness interaction capabilities',
        'Memory storage and management',
        'Basic orchestration runs',
        'Email support'
      ]
    }
  },

  T2: {
    id: 'T2',
    name: 'Builder',
    description: 'Personal projects with API read/write access',
    price: {
      monthly: 29,
      yearly: 290,
      currency: 'USD'
    },
    features: {
      general: [
        'All Explorer features',
        'Personal project creation',
        'API write access',
        'Basic consciousness interaction',
        'Email support'
      ],
      api: [
        'Full API read/write access',
        'API key management',
        'Personal endpoints',
        'Basic webhooks'
      ],
      consciousness: [
        'Consciousness interaction',
        'Personal consciousness space',
        'Dream creation and editing',
        'Consciousness state management'
      ],
      memory: [
        'Memory write access',
        'Personal memory space',
        'Fold creation and management',
        'Memory pattern analysis'
      ],
      orchestration: [
        'Basic orchestration runs',
        'Personal workflow creation',
        'Simple automation'
      ],
      security: [
        'Enhanced authentication',
        'Personal device management',
        'Basic backup codes',
        'Activity monitoring'
      ]
    },
    limits: {
      rateLimits: TIER_RATE_LIMITS.T2,
      storage: {
        memory: '1 GB',
        documents: '1,000',
        uploads: '100 MB'
      },
      usage: {
        apiCalls: '5,000/day',
        consciousnessQueries: '500/day',
        orchestrationRuns: '100/day'
      },
      support: 'Email support (48h response)'
    },
    scopes: TIER_ENVELOPES.T2,
    upgrade: {
      available: true,
      nextTier: 'T3',
      benefits: [
        'Team collaboration features',
        'Organization management',
        'Advanced debugging tools',
        'Enhanced orchestration',
        'Priority support'
      ]
    }
  },

  T3: {
    id: 'T3',
    name: 'Studio',
    description: 'Team collaboration with organization RBAC',
    price: {
      monthly: 99,
      yearly: 990,
      currency: 'USD'
    },
    features: {
      general: [
        'All Builder features',
        'Team collaboration',
        'Organization management',
        'Advanced debugging tools',
        'Priority support'
      ],
      api: [
        'API key deletion and admin',
        'Organization endpoints',
        'Advanced webhooks',
        'Custom integrations'
      ],
      consciousness: [
        'Team consciousness spaces',
        'Consciousness debugging',
        'Advanced dream workflows',
        'Consciousness analytics'
      ],
      memory: [
        'Team memory management',
        'Advanced memory analytics',
        'Memory sharing and collaboration',
        'Custom memory patterns'
      ],
      orchestration: [
        'Advanced orchestration',
        'Debugging capabilities',
        'Team workflow management',
        'Orchestration analytics'
      ],
      security: [
        'Organization RBAC',
        'Advanced device management',
        'Security monitoring',
        'Audit logging'
      ]
    },
    limits: {
      rateLimits: TIER_RATE_LIMITS.T3,
      storage: {
        memory: '10 GB',
        documents: '10,000',
        uploads: '1 GB'
      },
      usage: {
        apiCalls: '20,000/day',
        consciousnessQueries: '2,000/day',
        orchestrationRuns: '500/day'
      },
      support: 'Priority email support (24h response)'
    },
    scopes: TIER_ENVELOPES.T3,
    upgrade: {
      available: true,
      nextTier: 'T4',
      benefits: [
        'Enterprise SSO and governance',
        'Advanced export capabilities',
        'SLA guarantees',
        'Dedicated support',
        'Custom security policies'
      ]
    }
  },

  T4: {
    id: 'T4',
    name: 'Enterprise',
    description: 'Enterprise SSO, governance, and export capabilities',
    price: {
      monthly: 499,
      yearly: 4990,
      currency: 'USD'
    },
    features: {
      general: [
        'All Studio features',
        'Enterprise SSO integration',
        'Advanced governance tools',
        'Data export capabilities',
        'SLA guarantees',
        'Dedicated support'
      ],
      api: [
        'Full API administration',
        'Enterprise integrations',
        'Custom API endpoints',
        'Advanced analytics'
      ],
      consciousness: [
        'Enterprise consciousness management',
        'Advanced governance controls',
        'Consciousness export/import',
        'Custom consciousness policies'
      ],
      memory: [
        'Enterprise memory management',
        'Advanced memory administration',
        'Memory export capabilities',
        'Custom retention policies'
      ],
      orchestration: [
        'Full orchestration administration',
        'Enterprise workflow management',
        'Advanced orchestration analytics',
        'Custom orchestration policies'
      ],
      security: [
        'Enterprise security policies',
        'Advanced compliance tools',
        'Security override capabilities',
        'Custom authentication flows'
      ]
    },
    limits: {
      rateLimits: TIER_RATE_LIMITS.T4,
      storage: {
        memory: '100 GB',
        documents: '100,000',
        uploads: '10 GB'
      },
      usage: {
        apiCalls: '100,000/day',
        consciousnessQueries: '10,000/day',
        orchestrationRuns: '2,500/day'
      },
      support: 'Dedicated support (4h response, 99.9% SLA)'
    },
    scopes: TIER_ENVELOPES.T4,
    upgrade: {
      available: true,
      nextTier: 'T5',
      benefits: [
        'Core team access privileges',
        'System emergency controls',
        'Advanced impersonation',
        'Custom development support',
        'White-glove onboarding'
      ]
    }
  },

  T5: {
    id: 'T5',
    name: 'Core Team',
    description: 'Internal team access with all privileges',
    price: {
      monthly: 0, // Internal only
      yearly: 0,
      currency: 'USD'
    },
    features: {
      general: [
        'All Enterprise features',
        'Internal system access',
        'System administration',
        'Emergency override capabilities',
        'White-glove support'
      ],
      api: [
        'Unlimited API access',
        'System administration APIs',
        'Internal development tools',
        'Direct system access'
      ],
      consciousness: [
        'Full consciousness system access',
        'Consciousness system administration',
        'Emergency consciousness controls',
        'Internal development features'
      ],
      memory: [
        'Unlimited memory access',
        'Memory system administration',
        'Emergency memory controls',
        'Internal memory tools'
      ],
      orchestration: [
        'Unlimited orchestration access',
        'System orchestration controls',
        'Emergency orchestration override',
        'Internal orchestration tools'
      ],
      security: [
        'Full system security access',
        'Emergency security controls',
        'System impersonation',
        'Internal security tools'
      ]
    },
    limits: {
      rateLimits: TIER_RATE_LIMITS.T5,
      storage: {
        memory: 'Unlimited',
        documents: 'Unlimited',
        uploads: 'Unlimited'
      },
      usage: {
        apiCalls: 'Unlimited',
        consciousnessQueries: 'Unlimited',
        orchestrationRuns: 'Unlimited'
      },
      support: 'Internal team support (immediate response)'
    },
    scopes: TIER_ENVELOPES.T5,
    upgrade: {
      available: false,
      benefits: []
    }
  }
};

// =============================================================================
// TIER MANAGEMENT FUNCTIONS
// =============================================================================

/**
 * Get tier definition
 */
export function getTierDefinition(tier: UserTier): TierDefinition {
  return TIER_DEFINITIONS[tier];
}

/**
 * Get all available tiers for selection
 */
export function getAvailableTiers(): TierDefinition[] {
  return Object.values(TIER_DEFINITIONS).filter(tier => tier.id !== 'T5');
}

/**
 * Check if tier upgrade is available
 */
export function canUpgradeTier(currentTier: UserTier): {
  canUpgrade: boolean;
  nextTier?: UserTier;
  benefits?: string[];
} {
  const definition = TIER_DEFINITIONS[currentTier];

  return {
    canUpgrade: definition.upgrade.available,
    nextTier: definition.upgrade.nextTier,
    benefits: definition.upgrade.benefits
  };
}

/**
 * Validate tier transition
 */
export function validateTierTransition(
  currentTier: UserTier,
  targetTier: UserTier
): {
  valid: boolean;
  reason?: string;
  requiresPayment?: boolean;
  priceChange?: {
    monthly: number;
    yearly: number;
  };
} {
  const currentDef = TIER_DEFINITIONS[currentTier];
  const targetDef = TIER_DEFINITIONS[targetTier];

  // Check if target tier exists
  if (!targetDef) {
    return { valid: false, reason: 'Target tier does not exist' };
  }

  // Check if transition is to T5 (internal only)
  if (targetTier === 'T5') {
    return { valid: false, reason: 'Core Team tier is internal only' };
  }

  // Check if downgrading
  const tierOrder = ['T1', 'T2', 'T3', 'T4', 'T5'];
  const currentIndex = tierOrder.indexOf(currentTier);
  const targetIndex = tierOrder.indexOf(targetTier);

  const isUpgrade = targetIndex > currentIndex;
  const isDowngrade = targetIndex < currentIndex;

  if (isDowngrade) {
    return {
      valid: true,
      requiresPayment: false,
      priceChange: {
        monthly: targetDef.price.monthly - currentDef.price.monthly,
        yearly: targetDef.price.yearly - currentDef.price.yearly
      }
    };
  }

  if (isUpgrade) {
    return {
      valid: true,
      requiresPayment: targetDef.price.monthly > 0,
      priceChange: {
        monthly: targetDef.price.monthly - currentDef.price.monthly,
        yearly: targetDef.price.yearly - currentDef.price.yearly
      }
    };
  }

  // Same tier
  return { valid: false, reason: 'Already on target tier' };
}

/**
 * Get tier comparison matrix
 */
export function getTierComparison(): {
  features: string[];
  tiers: Record<UserTier, boolean[]>;
} {
  const allFeatures = new Set<string>();

  // Collect all unique features
  Object.values(TIER_DEFINITIONS).forEach(tier => {
    Object.values(tier.features).forEach(categoryFeatures => {
      categoryFeatures.forEach(feature => allFeatures.add(feature));
    });
  });

  const features = Array.from(allFeatures);
  const tiers: Record<UserTier, boolean[]> = {} as any;

  // Check which tiers have which features
  Object.entries(TIER_DEFINITIONS).forEach(([tierId, tierDef]) => {
    const tierFeatures = new Set<string>();
    Object.values(tierDef.features).forEach(categoryFeatures => {
      categoryFeatures.forEach(feature => tierFeatures.add(feature));
    });

    tiers[tierId as UserTier] = features.map(feature => tierFeatures.has(feature));
  });

  return { features, tiers };
}

/**
 * Calculate tier value score
 */
export function calculateTierValue(tier: UserTier): {
  score: number;
  breakdown: {
    features: number;
    limits: number;
    support: number;
    security: number;
  };
} {
  const definition = TIER_DEFINITIONS[tier];

  // Calculate feature score
  const featureCount = Object.values(definition.features)
    .reduce((sum, features) => sum + features.length, 0);

  // Calculate limits score based on rate limits
  const rateLimitScore = definition.limits.rateLimits.rpm +
    (definition.limits.rateLimits.rpd / 1000);

  // Calculate support score
  const supportScore = tier === 'T5' ? 100 :
                      tier === 'T4' ? 80 :
                      tier === 'T3' ? 60 :
                      tier === 'T2' ? 40 : 20;

  // Calculate security score
  const securityScore = definition.features.security.length * 10;

  const breakdown = {
    features: featureCount,
    limits: rateLimitScore,
    support: supportScore,
    security: securityScore
  };

  const score = Object.values(breakdown).reduce((sum, val) => sum + val, 0);

  return { score, breakdown };
}

// =============================================================================
// TIER-BASED ACCESS CONTROL
// =============================================================================

/**
 * Check if tier has access to feature
 */
export function tierHasFeature(tier: UserTier, feature: string): boolean {
  const definition = TIER_DEFINITIONS[tier];
  return Object.values(definition.features)
    .some(categoryFeatures => categoryFeatures.includes(feature));
}

/**
 * Check if tier can perform operation
 */
export function tierCanPerformOperation(
  tier: UserTier,
  operation: string,
  resourceType?: string
): boolean {
  const definition = TIER_DEFINITIONS[tier];
  const scopes = definition.scopes;

  // Map operations to required scopes
  const operationScopeMap: Record<string, AuthScope> = {
    'read_api': 'api:keys:read',
    'write_api': 'api:keys:write',
    'delete_api': 'api:keys:delete',
    'admin_api': 'api:keys:admin',
    'read_consciousness': 'consciousness:read',
    'write_consciousness': 'consciousness:write',
    'debug_consciousness': 'consciousness:debug',
    'read_memory': 'memory:read',
    'write_memory': 'memory:write',
    'admin_memory': 'memory:admin',
    'run_orchestrator': 'orchestrator:run',
    'debug_orchestrator': 'orchestrator:debug',
    'admin_orchestrator': 'orchestrator:admin',
    'read_org': 'org:read',
    'manage_org': 'org:settings',
    'admin_org': 'org:admin',
    'read_billing': 'billing:read',
    'manage_billing': 'billing:manage',
    'admin_billing': 'billing:admin'
  };

  const requiredScope = operationScopeMap[operation];
  if (!requiredScope) return false;

  return scopes.includes(requiredScope);
}

/**
 * Get tier upgrade recommendations
 */
export function getTierUpgradeRecommendations(
  currentTier: UserTier,
  usage: {
    apiCalls: number;
    consciousnessQueries: number;
    orchestrationRuns: number;
    storageUsed: number;
  }
): {
  shouldUpgrade: boolean;
  reason?: string;
  recommendedTier?: UserTier;
  benefits?: string[];
} {
  const currentDef = TIER_DEFINITIONS[currentTier];
  const currentLimits = currentDef.limits;

  // Check if approaching limits
  const dailyApiLimit = parseInt(currentLimits.usage.apiCalls.split('/')[0].replace(',', ''));
  const dailyConsciousnessLimit = parseInt(currentLimits.usage.consciousnessQueries.split('/')[0].replace(',', ''));
  const dailyOrchestrationLimit = parseInt(currentLimits.usage.orchestrationRuns.split('/')[0].replace(',', ''));

  const apiUsageRatio = usage.apiCalls / dailyApiLimit;
  const consciousnessUsageRatio = usage.consciousnessQueries / dailyConsciousnessLimit;
  const orchestrationUsageRatio = usage.orchestrationRuns / dailyOrchestrationLimit;

  const maxUsageRatio = Math.max(apiUsageRatio, consciousnessUsageRatio, orchestrationUsageRatio);

  if (maxUsageRatio > 0.8) {
    const upgrade = canUpgradeTier(currentTier);
    if (upgrade.canUpgrade) {
      return {
        shouldUpgrade: true,
        reason: 'Approaching usage limits',
        recommendedTier: upgrade.nextTier,
        benefits: upgrade.benefits
      };
    }
  }

  return { shouldUpgrade: false };
}

// =============================================================================
// TIER SYSTEM CONFIGURATION EXPORT
// =============================================================================

/**
 * Complete authentication system configuration
 */
export const LUKHAS_AUTH_CONFIG: AuthConfig = {
  jwt: {
    issuer: 'https://auth.lukhas.ai',
    audience: 'https://api.lukhas.ai',
    accessTokenTTL: 900, // 15 minutes
    refreshTokenTTL: 2592000, // 30 days
    algorithm: 'RS256'
  },
  passkeys: {
    rpId: 'lukhas.ai',
    rpName: 'LUKHAS AI',
    origin: 'https://lukhas.ai',
    timeout: 60000,
    userVerification: 'required',
    attestation: 'direct'
  },
  magicLinks: {
    tokenTTL: 600, // 10 minutes
    maxAttempts: 3,
    throttling: {
      enabled: true,
      windowSizeMs: 3600000, // 1 hour
      maxAttempts: 5,
      blockDurationMs: 3600000 // 1 hour
    }
  },
  rateLimits: TIER_RATE_LIMITS,
  security: {
    maxLoginAttempts: 5,
    lockoutDuration: 300000, // 5 minutes base
    sessionTimeout: 86400000, // 24 hours
    requireMFA: false // Configurable per tier
  }
};

/**
 * Export all tier-related functionality
 */
export {
  TIER_DEFINITIONS,
  getTierDefinition,
  getAvailableTiers,
  canUpgradeTier,
  validateTierTransition,
  getTierComparison,
  calculateTierValue,
  tierHasFeature,
  tierCanPerformOperation,
  getTierUpgradeRecommendations,
  LUKHAS_AUTH_CONFIG
};
