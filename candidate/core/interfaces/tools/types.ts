/**
 * Type definitions for Lukhas Cognitive AI System Tools
 */

// Tool execution results
export interface ToolExecutionResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

// Base tool configuration
export interface ToolConfig {
  name: string;
  path: string;
  timeout?: number;
  env?: Record<string, string>;
}

// CLI Tool Types
export interface CliToolOptions {
  verbose?: boolean;
  format?: 'json' | 'text';
  debug?: boolean;
}

export interface CommandRegistryOptions extends CliToolOptions {
  list?: boolean;
  register?: string;
  remove?: string;
  category?: string;
}

export interface DreamCliOptions extends CliToolOptions {
  analyze?: boolean;
  export?: string;
  dateRange?: [Date, Date];
  filter?: string[];
}

// DAO Tool Types
export interface DaoProposalOptions {
  title: string;
  description: string;
  type: 'feature' | 'enhancement' | 'fix';
  priority: 'low' | 'medium' | 'high';
  deadline?: Date;
}

export interface DaoVoteOptions {
  proposalId: string;
  vote: 'yes' | 'no' | 'abstain';
  weight?: number;
  comment?: string;
}

// Research Tool Types
export interface DashboardConfig {
  metrics: string[];
  refreshRate: number;
  alertThresholds?: Record<string, number>;
  export?: {
    format: 'csv' | 'json';
    path: string;
  };
}

// Security Tool Types
export interface SessionLogEntry {
  timestamp: Date;
  userId: string;
  action: string;
  resource: string;
  result: 'success' | 'failure';
  metadata?: Record<string, any>;
}

export interface SecurityPolicyRule {
  resource: string;
  action: string[];
  effect: 'allow' | 'deny';
  conditions?: Record<string, any>;
}

// Tool Runner Types
export interface ToolRunner<T = any> {
  run: (args?: string[], options?: T) => Promise<ToolExecutionResult>;
  validate: (options: T) => boolean;
  getHelp: () => string;
}
