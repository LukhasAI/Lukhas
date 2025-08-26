import { EventEmitter } from 'events';

interface SafetyMetric {
  name: string;
  value: number;
  threshold: number;
  timestamp: number;
  context?: Record<string, unknown>;
}

interface SafetyAlert {
  level: 'info' | 'warning' | 'critical';
  message: string;
  metric: SafetyMetric;
  recommendations: string[];
}

interface TrendAnalysis {
  trend: 'improving' | 'stable' | 'degrading';
  velocity: number;
  prediction: number;
  confidence: number;
}

/**
 * Advanced Safety Monitor
 * Combines Jobs' simplicity with Altman's thorough safety approach
 */
export class AdvancedSafetyMonitor extends EventEmitter {
  private static instance: AdvancedSafetyMonitor;
  private metrics: Map<string, SafetyMetric[]>;
  private readonly MAX_HISTORY = 1000;
  private readonly TREND_WINDOW = 100;

  // Enhanced safety thresholds
  private readonly THRESHOLDS = {
    responseTime: 100,
    memoryUsage: 0.8,
    cpuUsage: 0.7,
    errorRate: 0.01,
    complexity: 0.7,
    stability: 0.95,
    predictability: 0.9,
    transparency: 1.0
  };

  private constructor() {
    super();
    this.metrics = new Map();
    this.initializeMetrics();
  }

  static getInstance(): AdvancedSafetyMonitor {
    if (!this.instance) {
      this.instance = new AdvancedSafetyMonitor();
    }
    return this.instance;
  }

  private initializeMetrics(): void {
    Object.entries(this.THRESHOLDS).forEach(([name, threshold]) => {
      this.metrics.set(name, []);
      this.setMetric(name, 0, threshold);
    });
  }

  /**
   * Jobs Principle: Simple to understand metrics
   * Altman Principle: Comprehensive safety tracking
   */
  setMetric(name: string, value: number, threshold: number, context?: Record<string, unknown>): void {
    const metric: SafetyMetric = {
      name,
      value,
      threshold,
      timestamp: Date.now(),
      context
    };

    const history = this.metrics.get(name) || [];
    history.push(metric);

    // Maintain history limit
    if (history.length > this.MAX_HISTORY) {
      history.shift();
    }

    this.metrics.set(name, history);
    this.analyzeMetric(metric);
  }

  private analyzeMetric(metric: SafetyMetric): void {
    // Analyze current state
    const alert = this.checkThreshold(metric);
    if (alert) {
      this.emit('safetyAlert', alert);
    }

    // Analyze trends
    const trend = this.analyzeTrend(metric.name);
    if (trend.trend === 'degrading' && trend.confidence > 0.8) {
      this.emit('trendAlert', {
        metric: metric.name,
        trend,
        timestamp: Date.now()
      });
    }
  }

  private checkThreshold(metric: SafetyMetric): SafetyAlert | null {
    if (metric.value > metric.threshold) {
      return {
        level: metric.value > metric.threshold * 1.2 ? 'critical' : 'warning',
        message: `Safety threshold exceeded for ${metric.name}`,
        metric,
        recommendations: this.generateRecommendations(metric)
      };
    }
    return null;
  }

  private generateRecommendations(metric: SafetyMetric): string[] {
    const recommendations: string[] = [];

    if (metric.value > metric.threshold * 1.5) {
      recommendations.push('Immediate system pause recommended');
      recommendations.push('Initiate emergency safety protocols');
    } else if (metric.value > metric.threshold * 1.2) {
      recommendations.push('Reduce system load');
      recommendations.push('Increase monitoring frequency');
    } else {
      recommendations.push('Monitor situation closely');
      recommendations.push('Review recent changes');
    }

    return recommendations;
  }

  analyzeTrend(metricName: string): TrendAnalysis {
    const history = this.metrics.get(metricName) || [];
    if (history.length < this.TREND_WINDOW) {
      return {
        trend: 'stable',
        velocity: 0,
        prediction: history[history.length - 1]?.value || 0,
        confidence: 0
      };
    }

    const recent = history.slice(-this.TREND_WINDOW);
    const values = recent.map(m => m.value);

    // Calculate trend
    const velocity = this.calculateVelocity(values);
    const prediction = this.predictNextValue(values);
    const confidence = this.calculateConfidence(values);

    return {
      trend: velocity > 0.01 ? 'degrading' : velocity < -0.01 ? 'improving' : 'stable',
      velocity,
      prediction,
      confidence
    };
  }

  private calculateVelocity(values: number[]): number {
    // Calculate rate of change
    const deltas = values.slice(1).map((v, i) => v - values[i]);
    return deltas.reduce((sum, v) => sum + v, 0) / deltas.length;
  }

  private predictNextValue(values: number[]): number {
    // Simple linear prediction
    const velocity = this.calculateVelocity(values);
    return values[values.length - 1] + velocity;
  }

  private calculateConfidence(values: number[]): number {
    // Calculate prediction confidence based on stability
    const variance = values.reduce((sum, v) => sum + Math.pow(v - values[0], 2), 0) / values.length;
    return Math.max(0, 1 - Math.sqrt(variance));
  }

  /**
   * Jobs Principle: Clear, simple status
   * Altman Principle: Complete safety picture
   */
  getSystemSafetyStatus(): {
    safe: boolean;
    score: number;
    metrics: Record<string, SafetyMetric>;
    trends: Record<string, TrendAnalysis>;
  } {
    const metricEntries = Array.from(this.metrics.entries());
    const currentMetrics = Object.fromEntries(
      metricEntries.map(([name, history]) => [name, history[history.length - 1]])
    );

    const trends = Object.fromEntries(
      metricEntries.map(([name]) => [name, this.analyzeTrend(name)])
    );

    const score = this.calculateOverallSafety(currentMetrics);

    return {
      safe: score > 0.95,
      score,
      metrics: currentMetrics,
      trends
    };
  }

  private calculateOverallSafety(metrics: Record<string, SafetyMetric>): number {
    // Calculate weighted safety score
    const weights = {
      stability: 0.3,
      predictability: 0.2,
      transparency: 0.2,
      errorRate: 0.15,
      complexity: 0.15
    };

    return Object.entries(weights).reduce((score, [name, weight]) => {
      const metric = metrics[name];
      if (!metric) return score;

      const normalizedValue = Math.min(1, metric.threshold / Math.max(metric.value, 0.0001));
      return score + (normalizedValue * weight);
    }, 0);
  }
}
