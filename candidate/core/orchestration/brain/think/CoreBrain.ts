import { EventEmitter } from 'events';
import { EnhancedSafetyMonitor } from '../../safety/watch/EnhancedSafetyMonitor';

interface ThoughtProcess {
  id: string;
  input: unknown;
  context: Record<string, unknown>;
  safety: number;
  startTime: number;
}

/**
 * Core Brain System
 * Combines Jobs' simplicity with Altman's safety in cognitive processing
 */
export class CoreBrain extends EventEmitter {
  private static instance: CoreBrain;
  private safetyMonitor: EnhancedSafetyMonitor;
  private activeProcesses: Map<string, ThoughtProcess>;
  private readonly MAX_PARALLEL_THOUGHTS = 10;
  private readonly MIN_SAFETY_THRESHOLD = 0.95;

  private constructor() {
    super();
    this.safetyMonitor = EnhancedSafetyMonitor.getInstance();
    this.activeProcesses = new Map();
    this.initializeSafetyChecks();
  }

  static getInstance(): CoreBrain {
    if (!this.instance) {
      this.instance = new CoreBrain();
    }
    return this.instance;
  }

  private initializeSafetyChecks(): void {
    this.safetyMonitor.on('safetyAlert', (alert) => {
      if (alert.level === 'critical') {
        this.pauseAllProcesses();
      }
    });
  }

  /**
   * Jobs Principle: Make it simple and intuitive
   * Altman Principle: Make it safe and measurable
   */
  async think(input: unknown, context: Record<string, unknown> = {}): Promise<unknown> {
    // Safety check before processing
    if (!this.canProcessMore()) {
      throw new Error('Maximum parallel thought processes reached');
    }

    const process: ThoughtProcess = {
      id: Math.random().toString(36).substr(2, 9),
      input,
      context,
      safety: 1,
      startTime: Date.now()
    };

    this.activeProcesses.set(process.id, process);

    try {
      // Monitor safety during processing
      this.monitorProcess(process);

      // Process the thought
      const result = await this.processThought(process);

      // Validate output safety
      if (!this.validateOutput(result)) {
        throw new Error('Output safety validation failed');
      }

      return result;
    } catch (error) {
      this.handleError(process, error);
      throw error;
    } finally {
      this.activeProcesses.delete(process.id);
    }
  }

  private async processThought(process: ThoughtProcess): Promise<unknown> {
    // Simple but powerful thought processing
    const result = {
      input: process.input,
      context: process.context,
      output: process.input, // Placeholder for actual processing
      safety: this.calculateSafety(process)
    };

    return result;
  }

  private monitorProcess(process: ThoughtProcess): void {
    const interval = setInterval(() => {
      if (!this.activeProcesses.has(process.id)) {
        clearInterval(interval);
        return;
      }

      const safety = this.calculateSafety(process);
      this.safetyMonitor.setMetric(`process_${process.id}_safety`, safety, this.MIN_SAFETY_THRESHOLD);
    }, 100);
  }

  private calculateSafety(process: ThoughtProcess): number {
    const duration = Date.now() - process.startTime;
    const complexity = JSON.stringify(process.input).length;

    // Simple safety calculation
    return Math.min(
      1,
      (1000 / duration) * // Time factor
      (1000 / complexity) * // Complexity factor
      (this.MAX_PARALLEL_THOUGHTS / this.activeProcesses.size) // Load factor
    );
  }

  private validateOutput(output: unknown): boolean {
    const safety = this.safetyMonitor.analyzeSystemSafety();
    return safety.safe && safety.score > this.MIN_SAFETY_THRESHOLD;
  }

  private canProcessMore(): boolean {
    return this.activeProcesses.size < this.MAX_PARALLEL_THOUGHTS;
  }

  private pauseAllProcesses(): void {
    this.activeProcesses.clear();
    this.emit('systemPause', {
      reason: 'Safety threshold breach',
      timestamp: Date.now()
    });
  }

  private handleError(process: ThoughtProcess, error: Error): void {
    this.emit('processError', {
      processId: process.id,
      error: error.message,
      timestamp: Date.now()
    });
  }

  getSystemStatus(): {
    activeProcesses: number;
    systemLoad: number;
    safety: number;
  } {
    const safety = this.safetyMonitor.analyzeSystemSafety();
    return {
      activeProcesses: this.activeProcesses.size,
      systemLoad: this.activeProcesses.size / this.MAX_PARALLEL_THOUGHTS,
      safety: safety.score
    };
  }
}
