/**
 * TypeScript types for Dream Engine API
 */

export enum TierLevel {
  TIER_1 = 'tier_1',
  TIER_2 = 'tier_2',
  TIER_3 = 'tier_3'
}

export interface EmotionalState {
  valence: number;          // -1.0 to 1.0
  arousal: number;          // 0.0 to 1.0
  dominance: number;        // 0.0 to 1.0
  primary_emotion: string;
  intensity: number;        // 0.0 to 1.0
}

export interface SymbolicAnnotation {
  symbol: string;
  meaning: string;
  context: string;
  confidence: number;
}

export interface DreamRequest {
  content: string;
  symbolic_tags?: string[];
  qi_enhanced?: boolean;
  tier?: TierLevel;
}

export interface DreamResponse {
  dream_id: string;
  processed_content: string;
  quantum_coherence: number;
  emotional_state: EmotionalState;
  symbolic_annotations: SymbolicAnnotation[];
  tier: TierLevel;
  processing_time_ms: number;
  timestamp: string;
}

export interface TierFeatures {
  name: string;
  features: string[];
  price: string;
  processingSpeed: string;
}

export const TIER_COMPARISON: Record<TierLevel, TierFeatures> = {
  [TierLevel.TIER_1]: {
    name: 'Basic',
    features: [
      'Dream text processing',
      'Basic emotional analysis',
      'Standard coherence metrics'
    ],
    price: 'Free',
    processingSpeed: '< 2s'
  },
  [TierLevel.TIER_2]: {
    name: 'Advanced',
    features: [
      'All Tier 1 features',
      'Symbolic pattern recognition',
      'Enhanced quantum coherence',
      'Historical dream correlation'
    ],
    price: '$9/month',
    processingSpeed: '< 1s'
  },
  [TierLevel.TIER_3]: {
    name: 'Professional',
    features: [
      'All Tier 2 features',
      'Real-time consciousness metrics',
      'AI-guided interpretation',
      'Export to multiple formats',
      'API access'
    ],
    price: '$29/month',
    processingSpeed: '< 500ms'
  }
};
