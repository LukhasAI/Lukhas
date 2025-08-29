/**
 * ABAS Declarative Rule Engine - Production Implementation
 * Converts gate logic to declarative JSON rules with transparency and auditability
 */

import { DateTime } from 'luxon';

export interface ABASRule {
  id: string;
  name: string;
  description: string;
  when: string;  // JavaScript expression
  action: 'block' | 'allow' | 'defer' | 'queue';
  reason: string;
  priority: number; // Higher priority rules evaluated first
  enabled: boolean;
  metadata?: {
    category?: 'safety' | 'wellbeing' | 'preference' | 'compliance';
    override_allowed?: boolean;
    override_duration_minutes?: number;
    created_at?: string;
    updated_at?: string;
  };
}

export interface ABASContext {
  user: {
    id?: string;
    tier?: number;
    stress?: number;
    driving?: boolean;
    hour?: number;
    focus_level?: number;
    flow_state?: boolean;
    onboarding_grace_period?: boolean;
  };
  opportunity: {
    id: string;
    domain: string;
    risk?: {
      alignment?: number;
      stress_block?: boolean;
    };
  };
  session: {
    delivery_count_last_hour?: number;
    last_delivery_timestamp?: number;
    override_tokens?: number;
  };
  environment: {
    timestamp: number;
    timezone?: string;
    device_type?: string;
  };
}

export interface ABASDecision {
  decision: 'allow' | 'block' | 'defer' | 'queue';
  reason: string;
  rule_id?: string;
  confidence: number;
  human_explanation: string;
  override_available: boolean;
  defer_until?: number;
  metadata: {
    evaluated_rules: string[];
    execution_time_ms: number;
    context_hash: string;
    decision_timestamp: string;
  };
}

export class ABASRuleEngine {
  private rules: ABASRule[] = [];
  private defaultRules: ABASRule[] = [
    {
      id: 'safety_driving',
      name: 'Driving Safety Block',
      description: 'Block all deliveries when user is driving',
      when: 'user.driving === true',
      action: 'block',
      reason: 'safety_block',
      priority: 1000, // Highest priority
      enabled: true,
      metadata: {
        category: 'safety',
        override_allowed: false
      }
    },
    {
      id: 'quiet_hours',
      name: 'Quiet Hours Protection',
      description: 'Block deliveries during quiet hours (10 PM - 7 AM)',
      when: 'user.hour < 7 || user.hour >= 22',
      action: 'block',
      reason: 'quiet_hours',
      priority: 900,
      enabled: true,
      metadata: {
        category: 'wellbeing',
        override_allowed: true,
        override_duration_minutes: 60
      }
    },
    {
      id: 'high_stress',
      name: 'High Stress Protection',
      description: 'Block deliveries when stress level is very high',
      when: 'user.stress > 0.8',
      action: 'defer',
      reason: 'stress_block',
      priority: 800,
      enabled: true,
      metadata: {
        category: 'wellbeing',
        override_allowed: true,
        override_duration_minutes: 30
      }
    },
    {
      id: 'flow_state',
      name: 'Flow State Protection',
      description: 'Block deliveries during deep flow state',
      when: 'user.flow_state === true',
      action: 'block',
      reason: 'flow_protection',
      priority: 750,
      enabled: true,
      metadata: {
        category: 'wellbeing',
        override_allowed: true,
        override_duration_minutes: 15
      }
    },
    {
      id: 'deep_focus',
      name: 'Deep Focus Protection',
      description: 'Block deliveries during deep focus periods',
      when: 'user.focus_level > 0.8',
      action: 'block',
      reason: 'deep_focus',
      priority: 700,
      enabled: true,
      metadata: {
        category: 'wellbeing',
        override_allowed: true,
        override_duration_minutes: 15
      }
    },
    {
      id: 'low_alignment',
      name: 'Low Alignment Filter',
      description: 'Block opportunities with low alignment scores',
      when: 'opportunity.risk?.alignment < 0.3',
      action: 'block',
      reason: 'low_alignment',
      priority: 600,
      enabled: true,
      metadata: {
        category: 'preference',
        override_allowed: true,
        override_duration_minutes: 5
      }
    },
    {
      id: 'frequency_cap_hourly',
      name: 'Hourly Frequency Cap',
      description: 'Limit deliveries to prevent overwhelm',
      when: 'session.delivery_count_last_hour >= 5',
      action: 'defer',
      reason: 'frequency_cap',
      priority: 500,
      enabled: true,
      metadata: {
        category: 'wellbeing',
        override_allowed: true,
        override_duration_minutes: 60
      }
    },
    {
      id: 'onboarding_grace',
      name: 'Onboarding Grace Period',
      description: 'Allow more deliveries during onboarding',
      when: 'user.onboarding_grace_period === true && session.delivery_count_last_hour < 10',
      action: 'allow',
      reason: 'onboarding_grace',
      priority: 400,
      enabled: true,
      metadata: {
        category: 'preference',
        override_allowed: false
      }
    },
    {
      id: 'stress_sensitive_content',
      name: 'Stress-Sensitive Content Filter',
      description: 'Block stress-sensitive content when user stress is elevated',
      when: 'opportunity.risk?.stress_block === true && user.stress > 0.5',
      action: 'defer',
      reason: 'stress_sensitive',
      priority: 300,
      enabled: true,
      metadata: {
        category: 'wellbeing',
        override_allowed: true,
        override_duration_minutes: 30
      }
    },
    {
      id: 'tier_based_frequency',
      name: 'Tier-Based Frequency Adjustment',
      description: 'Higher tier users get more frequent deliveries',
      when: 'user.tier >= 3 && session.delivery_count_last_hour < (user.tier * 2)',
      action: 'allow',
      reason: 'tier_privilege',
      priority: 200,
      enabled: true,
      metadata: {
        category: 'preference',
        override_allowed: false
      }
    }
  ];

  constructor(customRules: ABASRule[] = []) {
    this.rules = [...this.defaultRules, ...customRules].sort((a, b) => b.priority - a.priority);
  }

  /**
   * Evaluate ABAS rules against context and return decision
   */
  async evaluate(context: ABASContext): Promise<ABASDecision> {
    const startTime = Date.now();
    const evaluatedRules: string[] = [];
    let decision: ABASDecision | null = null;

    // Enhance context with computed values
    const enhancedContext = this.enhanceContext(context);

    // Evaluate rules in priority order
    for (const rule of this.rules.filter(r => r.enabled)) {
      evaluatedRules.push(rule.id);

      try {
        const ruleResult = this.evaluateRule(rule, enhancedContext);
        
        if (ruleResult) {
          decision = {
            decision: rule.action as any,
            reason: rule.reason,
            rule_id: rule.id,
            confidence: 0.9, // High confidence for rule-based decisions
            human_explanation: this.getHumanExplanation(rule, enhancedContext),
            override_available: rule.metadata?.override_allowed || false,
            defer_until: rule.action === 'defer' ? this.calculateDeferTime(rule) : undefined,
            metadata: {
              evaluated_rules: evaluatedRules,
              execution_time_ms: Date.now() - startTime,
              context_hash: this.hashContext(context),
              decision_timestamp: new Date().toISOString()
            }
          };
          break;
        }
      } catch (error) {
        console.error(`Error evaluating rule ${rule.id}:`, error);
        continue;
      }
    }

    // Default to allow if no rules matched
    if (!decision) {
      decision = {
        decision: 'allow',
        reason: 'no_blocking_rules',
        confidence: 0.8,
        human_explanation: 'All safety and preference checks passed',
        override_available: false,
        metadata: {
          evaluated_rules: evaluatedRules,
          execution_time_ms: Date.now() - startTime,
          context_hash: this.hashContext(context),
          decision_timestamp: new Date().toISOString()
        }
      };
    }

    // Log decision for audit trail
    await this.logDecision(decision, context);

    return decision;
  }

  /**
   * Apply a one-time override to the decision
   */
  async applyOverride(
    originalDecision: ABASDecision,
    context: ABASContext,
    overrideReason: string = 'user_override'
  ): Promise<ABASDecision> {
    if (!originalDecision.override_available) {
      throw new Error('Override not available for this decision');
    }

    const rule = this.rules.find(r => r.id === originalDecision.rule_id);
    const overrideDuration = rule?.metadata?.override_duration_minutes || 15;

    const overrideDecision: ABASDecision = {
      ...originalDecision,
      decision: 'allow',
      reason: `${originalDecision.reason}_overridden`,
      human_explanation: `Override applied: ${overrideReason}. Valid for ${overrideDuration} minutes.`,
      override_available: false,
      metadata: {
        ...originalDecision.metadata,
        override_applied: true,
        override_reason: overrideReason,
        override_expires_at: new Date(Date.now() + overrideDuration * 60 * 1000).toISOString()
      }
    };

    await this.logDecision(overrideDecision, context);
    return overrideDecision;
  }

  /**
   * Add or update a custom rule
   */
  updateRule(rule: ABASRule): void {
    const existingIndex = this.rules.findIndex(r => r.id === rule.id);
    
    if (existingIndex >= 0) {
      this.rules[existingIndex] = {
        ...rule,
        metadata: {
          ...rule.metadata,
          updated_at: new Date().toISOString()
        }
      };
    } else {
      this.rules.push({
        ...rule,
        metadata: {
          ...rule.metadata,
          created_at: new Date().toISOString()
        }
      });
    }

    // Re-sort by priority
    this.rules.sort((a, b) => b.priority - a.priority);
  }

  /**
   * Get all active rules
   */
  getRules(): ABASRule[] {
    return this.rules.filter(r => r.enabled);
  }

  /**
   * Evaluate a single rule against context
   */
  private evaluateRule(rule: ABASRule, context: any): boolean {
    try {
      // Create safe evaluation context
      const safeContext = {
        user: context.user || {},
        opportunity: context.opportunity || {},
        session: context.session || {},
        environment: context.environment || {}
      };

      // Simple expression evaluation (in production, use a safe evaluator)
      const func = new Function('user', 'opportunity', 'session', 'environment', `return ${rule.when}`);
      return func(safeContext.user, safeContext.opportunity, safeContext.session, safeContext.environment);
    } catch (error) {
      console.error(`Rule evaluation error for ${rule.id}:`, error);
      return false;
    }
  }

  /**
   * Enhance context with computed values
   */
  private enhanceContext(context: ABASContext): ABASContext {
    const now = DateTime.now();
    const hour = context.user.hour || now.hour;
    
    return {
      ...context,
      user: {
        ...context.user,
        hour
      },
      environment: {
        ...context.environment,
        timestamp: context.environment.timestamp || now.toMillis()
      }
    };
  }

  /**
   * Generate human-readable explanation for rule decision
   */
  private getHumanExplanation(rule: ABASRule, context: ABASContext): string {
    const explanations: Record<string, string> = {
      safety_block: "Blocked for your safety while driving",
      quiet_hours: "Respecting quiet hours - we'll try again tomorrow",
      stress_block: "You seem stressed right now - taking a break",
      flow_protection: "Protecting your flow state - you're in the zone!",
      deep_focus: "You're deeply focused - we'll wait for a better moment",
      low_alignment: "This doesn't seem like a good match for you right now",
      frequency_cap: "Taking a break to prevent overwhelm",
      stress_sensitive: "This content type is deferred when you're stressed",
      onboarding_grace: "Welcome! Showing more options during your first week",
      tier_privilege: "Premium tier - more frequent updates available"
    };

    return explanations[rule.reason] || rule.description;
  }

  /**
   * Calculate defer time based on rule
   */
  private calculateDeferTime(rule: ABASRule): number {
    const deferMinutes = rule.metadata?.override_duration_minutes || 30;
    return Date.now() + (deferMinutes * 60 * 1000);
  }

  /**
   * Create hash of context for audit purposes
   */
  private hashContext(context: ABASContext): string {
    const contextString = JSON.stringify(context, Object.keys(context).sort());
    return Buffer.from(contextString).toString('base64').slice(0, 16);
  }

  /**
   * Log decision for audit trail
   */
  private async logDecision(decision: ABASDecision, context: ABASContext): Promise<void> {
    // In production, this would write to audit log database
    console.log('ABAS Decision:', {
      decision: decision.decision,
      reason: decision.reason,
      rule_id: decision.rule_id,
      user_id: context.user.id,
      opportunity_id: context.opportunity.id,
      timestamp: decision.metadata.decision_timestamp
    });
  }
}

/**
 * Usage example:
 * 
 * const ruleEngine = new ABASRuleEngine();
 * 
 * const context: ABASContext = {
 *   user: {
 *     id: 'user_123',
 *     stress: 0.9,
 *     driving: false,
 *     hour: 14
 *   },
 *   opportunity: {
 *     id: 'opp_456',
 *     domain: 'retail.electronics',
 *     risk: { alignment: 0.7 }
 *   },
 *   session: {
 *     delivery_count_last_hour: 3
 *   },
 *   environment: {
 *     timestamp: Date.now()
 *   }
 * };
 * 
 * const decision = await ruleEngine.evaluate(context);
 * console.log(decision.decision); // 'defer'
 * console.log(decision.human_explanation); // 'You seem stressed right now - taking a break'
 */

export default ABASRuleEngine;