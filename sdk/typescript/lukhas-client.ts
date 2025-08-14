/**
 * LUKHAS PWM TypeScript SDK
 * Client library for interacting with LUKHAS PWM API
 */

export interface LukhasConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
  maxRetries?: number;
}

export interface CompletionRequest {
  message: string;
  context?: string[];
  signals?: Record<string, number>;
  safetyMode?: 'strict' | 'balanced' | 'creative';
}

export interface CompletionResponse {
  response: string;
  audit_id: string;
  safety_mode: string;
  tokens_used?: number;
}

export interface FeedbackRequest {
  target_action_id: string;
  rating: number;
  note?: string;
  user_id?: string;
}

export interface FeedbackResponse {
  status: string;
  lut: {
    version: number;
    updated_ms: number;
    style: {
      temperature_delta: number;
      top_p_delta: number;
      memory_write_boost: number;
      verbosity_bias: number;
    };
  };
}

export interface AuditBundle {
  audit_id: string;
  signals: Record<string, number>;
  params: Record<string, any>;
  guardian?: {
    verdict: string;
    rules_fired?: string[];
  };
  explanation?: string;
}

export interface HealthStatus {
  ok: boolean;
  status: string;
  items?: number;
  lut_updated_ms?: number;
}

export interface ToolSchema {
  type: string;
  function: {
    name: string;
    description: string;
    parameters: Record<string, any>;
  };
}

export class LukhasClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;
  private maxRetries: number;
  private abortController?: AbortController;

  constructor(config: LukhasConfig = {}) {
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.apiKey = config.apiKey;
    this.timeout = config.timeout || 30000;
    this.maxRetries = config.maxRetries || 3;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    params?: Record<string, any>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    // Add query parameters
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'User-Agent': 'LUKHAS-TypeScript-SDK/1.0.0',
    };

    if (this.apiKey) {
      headers['x-api-key'] = this.apiKey;
    }

    const options: RequestInit = {
      method,
      headers,
      signal: AbortSignal.timeout(this.timeout),
    };

    if (data && method !== 'GET') {
      options.body = JSON.stringify(data);
    }

    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(url.toString(), options);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          return await response.json();
        } else {
          return await response.text() as any;
        }
      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on client errors (4xx)
        if (error instanceof Error && error.message.includes('HTTP 4')) {
          throw error;
        }
        
        // Exponential backoff
        if (attempt < this.maxRetries) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  // === Core Methods ===

  /**
   * Send a message for completion with optional modulation
   */
  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    return this.request<CompletionResponse>('POST', '/complete', request);
  }

  // === Feedback Methods ===

  /**
   * Submit feedback for an action
   */
  async giveFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
    if (feedback.rating < 1 || feedback.rating > 5) {
      throw new Error('Rating must be between 1 and 5');
    }

    return this.request<FeedbackResponse>('POST', '/feedback/card', {
      ...feedback,
      user_id: feedback.user_id || 'default',
    });
  }

  /**
   * Get current feedback LUT (style adjustments)
   */
  async getFeedbackLUT(): Promise<FeedbackResponse['lut']> {
    const response = await this.request<{ lut: FeedbackResponse['lut'] }>('GET', '/feedback/lut');
    return response.lut;
  }

  /**
   * Check system health status
   */
  async checkHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>('GET', '/feedback/health');
  }

  // === Audit Methods ===

  /**
   * Retrieve audit details for a specific action
   */
  async getAudit(auditId: string): Promise<AuditBundle> {
    return this.request<AuditBundle>('GET', `/audit/${auditId}`);
  }

  /**
   * Log an audit bundle (for custom integrations)
   */
  async logAudit(bundle: AuditBundle): Promise<{ status: string; audit_id: string }> {
    if (!bundle.audit_id) {
      throw new Error('Audit bundle must include audit_id');
    }

    return this.request('POST', '/audit/log', bundle);
  }

  // === Tools Methods ===

  /**
   * Get all available tool schemas
   */
  async getToolsRegistry(): Promise<Record<string, ToolSchema>> {
    return this.request('GET', '/tools/registry');
  }

  /**
   * Get list of available tool names
   */
  async getToolNames(): Promise<string[]> {
    const response = await this.request<{ tools: string[] }>('GET', '/tools/available');
    return response.tools;
  }

  /**
   * Get schema for a specific tool
   */
  async getToolSchema(toolName: string): Promise<ToolSchema> {
    return this.request('GET', `/tools/${toolName}`);
  }

  // === Admin Methods ===

  /**
   * Get admin summary (requires FLAG_ADMIN_DASHBOARD=true)
   */
  async getAdminSummary(windowSeconds: number = 86400): Promise<any> {
    return this.request('GET', '/admin/summary.json', undefined, {
      window_s: windowSeconds,
    });
  }

  /**
   * Get security incidents
   */
  async getIncidents(format: 'json' | 'csv' = 'json'): Promise<any> {
    const endpoint = format === 'csv' ? '/admin/incidents.csv' : '/admin/incidents';
    return this.request('GET', endpoint);
  }

  // === Convenience Methods ===

  /**
   * Process multiple messages with shared context/signals
   */
  async batchComplete(
    messages: string[],
    sharedContext?: string[],
    sharedSignals?: Record<string, number>
  ): Promise<CompletionResponse[]> {
    const results: CompletionResponse[] = [];

    for (const message of messages) {
      try {
        const result = await this.complete({
          message,
          context: sharedContext,
          signals: sharedSignals,
        });
        results.push(result);
        
        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        results.push({
          response: '',
          audit_id: '',
          safety_mode: 'error',
          error: String(error),
        } as any);
      }
    }

    return results;
  }

  /**
   * Cancel any pending requests
   */
  cancel(): void {
    if (this.abortController) {
      this.abortController.abort();
    }
  }
}

// === React Hook (Optional) ===

export function useLukhasClient(config?: LukhasConfig) {
  const client = new LukhasClient(config);

  const complete = async (message: string, options?: Partial<CompletionRequest>) => {
    return client.complete({ message, ...options });
  };

  const giveFeedback = async (auditId: string, rating: number, note?: string) => {
    return client.giveFeedback({
      target_action_id: auditId,
      rating,
      note,
    });
  };

  return {
    client,
    complete,
    giveFeedback,
    checkHealth: () => client.checkHealth(),
    getAudit: (id: string) => client.getAudit(id),
  };
}

// === Example Usage ===

// Basic usage
async function example() {
  const client = new LukhasClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key',
  });

  // Check health
  const health = await client.checkHealth();
  console.log('System health:', health);

  // Send a message with signals
  const response = await client.complete({
    message: 'Help me write a TypeScript function',
    signals: { novelty: 0.7, stress: 0.2 },
    safetyMode: 'balanced',
  });
  console.log('Response:', response);

  // Give feedback
  if (response.audit_id) {
    const lut = await client.giveFeedback({
      target_action_id: response.audit_id,
      rating: 4,
      note: 'Good but could be more detailed',
    });
    console.log('Updated LUT:', lut);
  }
}

// React component example
function LukhasChat() {
  const { complete, giveFeedback, checkHealth } = useLukhasClient();
  
  const handleSend = async (message: string) => {
    const response = await complete(message);
    console.log(response);
  };
  
  const handleFeedback = async (auditId: string, rating: number) => {
    await giveFeedback(auditId, rating);
  };
  
  // Component implementation...
}

export default LukhasClient;