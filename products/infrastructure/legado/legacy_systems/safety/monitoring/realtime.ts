import { EventEmitter } from 'events';

class SafetyMonitor extends EventEmitter {
  private static instance: SafetyMonitor;
  private metrics: Map<string, number>;

  private constructor() {
    super();
    this.metrics = new Map();
  }

  static getInstance(): SafetyMonitor {
    if (!SafetyMonitor.instance) {
      SafetyMonitor.instance = new SafetyMonitor();
    }
    return SafetyMonitor.instance;
  }

  monitor(metric: string, value: number): void {
    this.metrics.set(metric, value);
    this.emit('metricUpdate', { metric, value });
  }

  getMetric(metric: string): number | undefined {
    return this.metrics.get(metric);
  }

  validateSafety(): boolean {
    // Add safety validation logic here
    return true;
  }
}

export const safetyMonitor = SafetyMonitor.getInstance();
