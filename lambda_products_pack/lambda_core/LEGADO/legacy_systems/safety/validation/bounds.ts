export interface SafetyBounds {
  maxRecursionDepth: number;
  maxResponseTime: number;
  maxMemoryUsage: number;
  maxCPUUsage: number;
}

export class SafetyValidator {
  private static instance: SafetyValidator;
  private bounds: SafetyBounds;

  private constructor() {
    this.bounds = {
      maxRecursionDepth: 10,
      maxResponseTime: 100, // ms
      maxMemoryUsage: 1024 * 1024 * 1024, // 1GB
      maxCPUUsage: 80 // percentage
    };
  }

  static getInstance(): SafetyValidator {
    if (!SafetyValidator.instance) {
      SafetyValidator.instance = new SafetyValidator();
    }
    return SafetyValidator.instance;
  }

  validateOperation(metrics: Partial<SafetyBounds>): boolean {
    // Validate each provided metric against bounds
    for (const [key, value] of Object.entries(metrics)) {
      if (key in this.bounds && value > this.bounds[key as keyof SafetyBounds]) {
        return false;
      }
    }
    return true;
  }

  updateBounds(newBounds: Partial<SafetyBounds>): void {
    this.bounds = { ...this.bounds, ...newBounds };
  }
}

export const safetyValidator = SafetyValidator.getInstance();
