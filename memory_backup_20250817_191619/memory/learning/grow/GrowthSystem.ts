import { EventEmitter } from 'events';
import { EnhancedSafetyMonitor } from '../../safety/watch/EnhancedSafetyMonitor';
import { CoreBrain } from '../think/CoreBrain';
import { LearningSystem } from '../learn/LearningSystem';

interface GrowthMetrics {
  efficiency: number;
  stability: number;
  safety: number;
  complexity: number;
}

/**
 * Growth System
 * Combines Jobs' simplicity with Altman's safe self-improvement
 */
export class GrowthSystem extends EventEmitter {
  private static instance: GrowthSystem;
  private safetyMonitor: EnhancedSafetyMonitor;
  private coreBrain: CoreBrain;
  private learningSystem: LearningSystem;
  
  private readonly MIN_GROWTH_SAFETY = 0.98; // Higher than general safety threshold
  private readonly MAX_COMPLEXITY_INCREASE = 0.1; // 10% max complexity increase per iteration
  private growthMetrics: GrowthMetrics;

  private constructor() {
    super();
    this.safetyMonitor = EnhancedSafetyMonitor.getInstance();
    this.coreBrain = CoreBrain.getInstance();
    this.learningSystem = LearningSystem.getInstance();
    this.growthMetrics = this.initializeMetrics();
    this.initializeSafeGrowth();
  }

  static getInstance(): GrowthSystem {
    if (!this.instance) {
      this.instance = new GrowthSystem();
    }
    return this.instance;
  }

  private initializeMetrics(): GrowthMetrics {
    return {
      efficiency: 1,
      stability: 1,
      safety: 1,
      complexity: 0
    };
  }

  private initializeSafeGrowth(): void {
    this.safetyMonitor.on('safetyAlert', (alert) => {
      if (alert.level === 'critical') {
        this.pauseGrowth();
      }
    });
  }

  /**
   * Jobs Principle: Improve simply and naturally
   * Altman Principle: Grow safely and controllably
   */
  async improve(): Promise<boolean> {
    try {
      // Validate current state
      if (!this.canGrow()) {
        return false;
      }

      // Analyze current performance
      const currentMetrics = await this.analyzePerformance();
      
      // Plan improvements
      const improvements = await this.planImprovements(currentMetrics);
      
      // Validate safety of improvements
      if (!this.validateImprovements(improvements)) {
        return false;
      }

      // Apply improvements
      await this.applyImprovements(improvements);
      
      // Verify results
      const newMetrics = await this.analyzePerformance();
      return this.verifyImprovement(currentMetrics, newMetrics);
    } catch (error) {
      this.handleGrowthError(error);
      return false;
    }
  }

  private async analyzePerformance(): Promise<GrowthMetrics> {
    const brainStatus = this.coreBrain.getSystemStatus();
    const learningStatus = this.learningSystem.getLearningStatus();
    const safetyAnalysis = this.safetyMonitor.analyzeSystemSafety();

    return {
      efficiency: brainStatus.systemLoad,
      stability: learningStatus.averageConfidence,
      safety: safetyAnalysis.score,
      complexity: this.calculateComplexity()
    };
  }

  private async planImprovements(current: GrowthMetrics): Promise<Partial<GrowthMetrics>> {
    // Plan improvements while maintaining simplicity
    return {
      efficiency: Math.min(1, current.efficiency * 1.1),
      stability: Math.min(1, current.stability * 1.05),
      safety: Math.max(current.safety, this.MIN_GROWTH_SAFETY),
      complexity: Math.min(1, current.complexity * (1 + this.MAX_COMPLEXITY_INCREASE))
    };
  }

  private validateImprovements(improvements: Partial<GrowthMetrics>): boolean {
    // Ensure safety and simplicity are maintained
    if (improvements.safety < this.MIN_GROWTH_SAFETY) {
      return false;
    }

    if (improvements.complexity > this.growthMetrics.complexity * (1 + this.MAX_COMPLEXITY_INCREASE)) {
      return false;
    }

    return true;
  }

  private async applyImprovements(improvements: Partial<GrowthMetrics>): Promise<void> {
    // Apply improvements gradually
    Object.assign(this.growthMetrics, improvements);
    this.emit('growthProgress', {
      metrics: this.growthMetrics,
      timestamp: Date.now()
    });
  }

  private verifyImprovement(before: GrowthMetrics, after: GrowthMetrics): boolean {
    // Verify that improvements maintain safety and simplicity
    return (
      after.safety >= before.safety &&
      after.efficiency > before.efficiency &&
      after.complexity <= before.complexity * (1 + this.MAX_COMPLEXITY_INCREASE)
    );
  }

  private calculateComplexity(): number {
    // Measure system complexity
    const brainStatus = this.coreBrain.getSystemStatus();
    const learningStatus = this.learningSystem.getLearningStatus();
    
    return (
      (brainStatus.systemLoad + learningStatus.systemCapacity) / 2
    );
  }

  private canGrow(): boolean {
    return (
      this.safetyMonitor.analyzeSystemSafety().safe &&
      this.growthMetrics.safety >= this.MIN_GROWTH_SAFETY
    );
  }

  private pauseGrowth(): void {
    this.emit('growthPaused', {
      reason: 'Safety threshold breach',
      metrics: this.growthMetrics,
      timestamp: Date.now()
    });
  }

  private handleGrowthError(error: Error): void {
    this.emit('growthError', {
      error: error.message,
      metrics: this.growthMetrics,
      timestamp: Date.now()
    });
  }

  getGrowthStatus(): {
    metrics: GrowthMetrics;
    canGrow: boolean;
    safetyStatus: string;
  } {
    const safety = this.safetyMonitor.analyzeSystemSafety();
    
    return {
      metrics: this.growthMetrics,
      canGrow: this.canGrow(),
      safetyStatus: safety.safe ? 'safe' : 'unsafe'
    };
  }
}
