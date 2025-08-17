/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: dream.ts
 * MODULE: frontend.src.types
 * DESCRIPTION: TypeScript type definitions for Oneiric Core dream analysis
 *              system. Defines interfaces for dreams, symbols, user profiles,
 *              and related data structures used throughout the frontend.
 * DEPENDENCIES: TypeScript, React component interfaces
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */

export interface Dream {
  sceneId: string;
  narrativeText: string;
  renderedImageUrl: string;
  narrativeAudioUrl?: string;
  symbolicStructure: {
    visualAnchor: string;
    directive_used: string;
    driftAnalysis?: {
      driftScore: number;
      symbolic_entropy?: number;
      emotional_charge?: number;
      narrative_coherence?: number;
    };
  };
  createdAt?: string;
  userId?: string;
}

export interface Symbol {
  symbol: string;
  frequency: number;
  emotional_charge: number;
  recent_dreams: string[];
}

export interface UserProfile {
  total_dreams: number;
  avg_drift: number;
  avg_entropy: number;
  avg_emotional: number;
  avg_coherence: number;
  drift_history: DriftEntry[];
}

export interface DriftEntry {
  drift_score: number;
  entropy_drift: number;
  emotional_drift: number;
  coherence_drift: number;
  timestamp: string;
  is_significant: boolean;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: dream.ts
 * VERSION: 1.0.0
 * TIER SYSTEM: Type definitions (Foundation for all user tiers)
 * ΛTRACE INTEGRATION: ENABLED
 * CAPABILITIES: Type safety, interface definitions, data structure modeling,
 *               dream analysis types, symbolic structure definitions, user profiling
 * FUNCTIONS: None directly defined (type definitions only)
 * CLASSES: None directly defined (interface definitions)
 * DECORATORS: None
 * DEPENDENCIES: TypeScript compiler, React type system
 * INTERFACES: Dream, Symbol, UserProfile, DreamRequest, DreamHistory
 * ERROR HANDLING: TypeScript compile-time type checking
 * LOGGING: ΛTRACE_ENABLED for type usage tracking
 * AUTHENTICATION: Not applicable (Type definitions)
 * HOW TO USE:
 *   import { Dream, Symbol, UserProfile } from '../types/dream';
 *   const dream: Dream = { sceneId: '...', narrativeText: '...' };
 *   Used throughout frontend for type safety and IntelliSense
 * INTEGRATION NOTES: Core type definitions for Oneiric Core frontend.
 *   Ensures type safety across all components and API interactions.
 *   Provides structure for dream analysis and symbolic interpretation data.
 * MAINTENANCE: Update types as API evolves, maintain compatibility with backend,
 *   add new interfaces as features develop, document breaking changes.
 * CONTACT: LUKHAS DEVELOPMENT TEAM
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */
