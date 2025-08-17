import { EventEmitter } from 'events';
import { EnhancedSafetyMonitor } from '../../safety/watch/EnhancedSafetyMonitor';
import { CoreBrain } from '../think/CoreBrain';

interface LearningPattern {
  id: string;
  pattern: unknown;
  confidence: number;
  validationScore: number;
  timestamp: number;
}

/**
 * Learning System
 * Implements Jobs' simplicity in learning and Altman's safe adaptation
 */
export class LearningSystem extends EventEmitter {
  private static instance: LearningSystem;
  private safetyMonitor: EnhancedSafetyMonitor;
  private coreBrain: CoreBrain;
  private patterns: Map<string, LearningPattern>;
  private readonly MIN_CONFIDENCE = 0.95;
  private readonly MAX_PATTERNS = 1000;

  private constructor() {
    super();
    this.safetyMonitor = EnhancedSafetyMonitor.getInstance();
    this.coreBrain = CoreBrain.getInstance();
    this.patterns = new Map();
    this.initializeSafeLearning();
  }

  static getInstance(): LearningSystem {
    if (!this.instance) {
      this.instance = new LearningSystem();
    }
    return this.instance;
  }

  private initializeSafeLearning(): void {
    this.safetyMonitor.on('safetyAlert', (alert) => {
      if (alert.level === 'critical') {
        this.pauseLearning();
      }
    });
  }

  /**
   * Jobs Principle: Learn simply and effectively
   * Altman Principle: Learn safely and verifiably
   */
  async learn(input: unknown): Promise<void> {
    const startTime = Date.now();

    try {
      // Validate learning capacity
      if (!this.canLearnMore()) {
        await this.consolidatePatterns();
      }

      // Process through core brain first
      const processed = await this.coreBrain.think(input);
      
      // Extract and validate pattern
      const pattern = await this.extractPattern(processed);
      
      if (pattern.confidence >= this.MIN_CONFIDENCE) {
        this.patterns.set(pattern.id, pattern);
        this.emit('patternLearned', pattern);
      }

      // Monitor learning performance
      this.safetyMonitor.setMetric('learningTime', Date.now() - startTime, 1000);
      this.safetyMonitor.setMetric('patternConfidence', pattern.confidence, this.MIN_CONFIDENCE);
    } catch (error) {
      this.handleLearningError(error);
      throw error;
    }
  }

  private async extractPattern(input: unknown): Promise<LearningPattern> {
    // Simple but effective pattern extraction
    return {
      id: Math.random().toString(36).substr(2, 9),
      pattern: input,
      confidence: this.calculateConfidence(input),
      validationScore: await this.validatePattern(input),
      timestamp: Date.now()
    };
  }

  private calculateConfidence(input: unknown): number {
    // Simple confidence calculation
    const complexity = JSON.stringify(input).length;
    const existingPatterns = this.patterns.size;
    
    return Math.min(
      1,
      (1000 / complexity) * // Complexity factor
      (this.MAX_PATTERNS / (existingPatterns + 1)) // Capacity factor
    );
  }

  private async validatePattern(input: unknown): Promise<number> {
    // Validate pattern safety and effectiveness
    const brainStatus = this.coreBrain.getSystemStatus();
    const safetyAnalysis = this.safetyMonitor.analyzeSystemSafety();
    
    return Math.min(brainStatus.safety, safetyAnalysis.score);
  }

  private async consolidatePatterns(): Promise<void> {
    // Consolidate patterns by merging similar ones
    const patterns = Array.from(this.patterns.values());
    patterns.sort((a, b) => b.confidence - a.confidence);
    
    // Keep only the most confident patterns
    this.patterns.clear();
    patterns.slice(0, this.MAX_PATTERNS / 2).forEach(pattern => {
      this.patterns.set(pattern.id, pattern);
    });
  }

  private canLearnMore(): boolean {
    return this.patterns.size < this.MAX_PATTERNS;
  }

  private pauseLearning(): void {
    this.emit('learningPaused', {
      reason: 'Safety threshold breach',
      timestamp: Date.now()
    });
  }

  private handleLearningError(error: Error): void {
    this.emit('learningError', {
      error: error.message,
      timestamp: Date.now()
    });
  }

  getLearningStatus(): {
    patternsLearned: number;
    averageConfidence: number;
    systemCapacity: number;
  } {
    const patterns = Array.from(this.patterns.values());
    const avgConfidence = patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length;

    return {
      patternsLearned: patterns.length,
      averageConfidence: avgConfidence || 0,
      systemCapacity: this.patterns.size / this.MAX_PATTERNS
    };
  }
}
