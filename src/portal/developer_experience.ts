/**
 * LUKHAS AI Developer Portal & Documentation System
 * 
 * Enterprise-grade developer experience with interactive API documentation,
 * sandbox environments, and comprehensive integration guides.
 * Built to enable rapid partner integration and reduce time-to-production.
 */

import { EventEmitter } from 'events';
import { createHash, randomBytes } from 'crypto';
import * as jwt from 'jsonwebtoken';

// Core Developer Portal Configuration
interface DeveloperPortalConfig {
  sandbox: {
    enabled: boolean;
    rateLimit: number;
    dataRetention: string;
    mockDataEnabled: boolean;
  };
  documentation: {
    interactiveExamples: boolean;
    codeGeneration: boolean;
    liveValidation: boolean;
  };
  authentication: {
    apiKeyValidation: boolean;
    oauthSupport: boolean;
    sandboxTokens: boolean;
  };
  analytics: {
    usageTracking: boolean;
    errorAnalytics: boolean;
    performanceMonitoring: boolean;
  };
}

// API Documentation Schema
interface APIEndpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  summary: string;
  description: string;
  parameters: APIParameter[];
  requestBody?: APIRequestBody;
  responses: APIResponse[];
  examples: APIExample[];
  sdkCode: SDKCodeExample[];
  authentication: string[];
  rateLimit?: RateLimit;
}

interface APIParameter {
  name: string;
  in: 'query' | 'path' | 'header' | 'cookie';
  required: boolean;
  schema: JSONSchema;
  description: string;
  example: any;
}

interface APIRequestBody {
  required: boolean;
  content: Record<string, MediaType>;
  description: string;
}

interface APIResponse {
  statusCode: number;
  description: string;
  schema: JSONSchema;
  examples: Record<string, any>;
}

interface APIExample {
  name: string;
  summary: string;
  request: {
    url: string;
    method: string;
    headers: Record<string, string>;
    body?: any;
  };
  response: {
    status: number;
    headers: Record<string, string>;
    body: any;
  };
}

interface SDKCodeExample {
  language: 'typescript' | 'javascript' | 'python' | 'curl';
  code: string;
  description: string;
}

interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchema>;
  required?: string[];
  items?: JSONSchema;
  enum?: any[];
  description?: string;
  example?: any;
}

interface MediaType {
  schema: JSONSchema;
  examples?: Record<string, any>;
}

interface RateLimit {
  requests: number;
  window: string;
  scope: 'user' | 'api_key' | 'ip';
}

// Sandbox Environment
interface SandboxSession {
  sessionId: string;
  developerId: string;
  createdAt: Date;
  expiresAt: Date;
  apiKey: string;
  rateLimit: {
    remaining: number;
    resetTime: Date;
  };
  usage: {
    requests: number;
    errors: number;
    lastActivity: Date;
  };
}

// Developer Analytics
interface DeveloperMetrics {
  developerId: string;
  period: {
    start: Date;
    end: Date;
  };
  apiUsage: {
    totalRequests: number;
    uniqueEndpoints: number;
    errorRate: number;
    avgResponseTime: number;
  };
  integration: {
    timeToFirstCall: number;
    timeToProduction: number;
    documentsViewed: string[];
    examplesRun: number;
  };
  feedback: {
    rating: number;
    comments: string[];
  };
}

/**
 * Developer Portal Core Engine
 */
export class DeveloperPortal extends EventEmitter {
  private config: DeveloperPortalConfig;
  private sandboxSessions: Map<string, SandboxSession> = new Map();
  private developerMetrics: Map<string, DeveloperMetrics> = new Map();
  private apiDocumentation: APIEndpoint[] = [];

  constructor(config: DeveloperPortalConfig) {
    super();
    this.config = config;
    this.initializeAPIDocumentation();
    this.startSessionCleanup();
  }

  /**
   * Interactive API Documentation Generator
   */
  async generateInteractiveDoc(endpoint: APIEndpoint): Promise<InteractiveDocumentation> {
    const doc: InteractiveDocumentation = {
      endpoint,
      interactiveForm: await this.generateInteractiveForm(endpoint),
      codeExamples: await this.generateCodeExamples(endpoint),
      tryItLive: {
        enabled: this.config.sandbox.enabled,
        sandboxUrl: await this.generateSandboxURL(endpoint),
        authentication: await this.generateSandboxAuth(endpoint)
      },
      validation: {
        realTimeValidation: this.config.documentation.liveValidation,
        schemaValidator: this.createSchemaValidator(endpoint),
        errorPreviews: await this.generateErrorPreviews(endpoint)
      }
    };

    this.emit('documentation:generated', {
      endpoint: endpoint.path,
      timestamp: new Date()
    });

    return doc;
  }

  /**
   * Sandbox Environment Management
   */
  async createSandboxSession(developerId: string): Promise<SandboxSession> {
    const sessionId = this.generateSessionId();
    const apiKey = this.generateSandboxApiKey(sessionId);
    
    const session: SandboxSession = {
      sessionId,
      developerId,
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
      apiKey,
      rateLimit: {
        remaining: this.config.sandbox.rateLimit,
        resetTime: new Date(Date.now() + 60 * 60 * 1000) // 1 hour
      },
      usage: {
        requests: 0,
        errors: 0,
        lastActivity: new Date()
      }
    };

    this.sandboxSessions.set(sessionId, session);

    this.emit('sandbox:session_created', {
      sessionId,
      developerId,
      timestamp: new Date()
    });

    return session;
  }

  /**
   * Code Generation Engine
   */
  async generateSDKCode(endpoint: APIEndpoint, language: string): Promise<string> {
    const generators = {
      typescript: () => this.generateTypeScriptCode(endpoint),
      javascript: () => this.generateJavaScriptCode(endpoint),
      python: () => this.generatePythonCode(endpoint),
      curl: () => this.generateCurlCode(endpoint)
    };

    if (!generators[language]) {
      throw new Error(`Unsupported language: ${language}`);
    }

    const code = await generators[language]();

    this.emit('code:generated', {
      endpoint: endpoint.path,
      language,
      timestamp: new Date()
    });

    return code;
  }

  /**
   * Developer Analytics & Insights
   */
  async trackDeveloperActivity(developerId: string, activity: DeveloperActivity): Promise<void> {
    if (!this.config.analytics.usageTracking) return;

    let metrics = this.developerMetrics.get(developerId);
    if (!metrics) {
      metrics = this.initializeDeveloperMetrics(developerId);
      this.developerMetrics.set(developerId, metrics);
    }

    switch (activity.type) {
      case 'api_call':
        metrics.apiUsage.totalRequests++;
        if (activity.error) {
          metrics.apiUsage.errorRate = 
            (metrics.apiUsage.errorRate * (metrics.apiUsage.totalRequests - 1) + 1) / metrics.apiUsage.totalRequests;
        }
        break;
      
      case 'documentation_view':
        if (!metrics.integration.documentsViewed.includes(activity.resource)) {
          metrics.integration.documentsViewed.push(activity.resource);
        }
        break;
      
      case 'example_run':
        metrics.integration.examplesRun++;
        break;
    }

    this.emit('analytics:activity_tracked', {
      developerId,
      activity,
      timestamp: new Date()
    });
  }

  /**
   * Integration Guides Generator
   */
  async generateIntegrationGuide(platform: string, useCase: string): Promise<IntegrationGuide> {
    const guide: IntegrationGuide = {
      platform,
      useCase,
      steps: await this.generateIntegrationSteps(platform, useCase),
      codeExamples: await this.generatePlatformSpecificCode(platform),
      troubleshooting: await this.generateTroubleshootingGuide(platform),
      testingChecklist: await this.generateTestingChecklist(useCase),
      goLiveChecklist: await this.generateGoLiveChecklist(platform)
    };

    this.emit('guide:generated', {
      platform,
      useCase,
      timestamp: new Date()
    });

    return guide;
  }

  /**
   * Real-time API Explorer
   */
  async createAPIExplorer(developerId: string): Promise<APIExplorer> {
    const session = await this.createSandboxSession(developerId);
    
    return {
      sessionId: session.sessionId,
      baseUrl: process.env.SANDBOX_BASE_URL || 'https://sandbox-api.lukhas.ai',
      authentication: {
        type: 'bearer',
        token: session.apiKey
      },
      endpoints: this.apiDocumentation.map(endpoint => ({
        ...endpoint,
        testable: true,
        mockData: this.config.sandbox.mockDataEnabled
      })),
      realTimeValidation: true,
      responseInspector: true,
      requestHistory: []
    };
  }

  /**
   * Developer Onboarding Flow
   */
  async createOnboardingFlow(developerId: string): Promise<OnboardingFlow> {
    const flow: OnboardingFlow = {
      developerId,
      steps: [
        {
          id: 'welcome',
          title: 'Welcome to LUKHAS AI',
          description: 'Get started with our powerful commerce API',
          action: 'read',
          completed: false
        },
        {
          id: 'api_key',
          title: 'Get Your API Keys',
          description: 'Generate production and sandbox API keys',
          action: 'generate_keys',
          completed: false
        },
        {
          id: 'first_request',
          title: 'Make Your First Request',
          description: 'Test our API with a simple request',
          action: 'api_call',
          endpoint: '/api/v1/health',
          completed: false
        },
        {
          id: 'sdk_setup',
          title: 'Install SDK',
          description: 'Set up our TypeScript SDK',
          action: 'install_sdk',
          completed: false
        },
        {
          id: 'integration_guide',
          title: 'Choose Integration Path',
          description: 'Select your platform and use case',
          action: 'select_guide',
          completed: false
        }
      ],
      currentStep: 0,
      completionRate: 0,
      estimatedTimeToComplete: 15 // minutes
    };

    this.emit('onboarding:started', {
      developerId,
      timestamp: new Date()
    });

    return flow;
  }

  // Private helper methods
  private initializeAPIDocumentation(): void {
    this.apiDocumentation = [
      {
        path: '/api/v1/opportunities',
        method: 'POST',
        summary: 'Submit Merchant Opportunity',
        description: 'Submit a new merchant opportunity for AI-powered matching',
        parameters: [
          {
            name: 'Authorization',
            in: 'header',
            required: true,
            schema: { type: 'string', example: 'Bearer your-api-key' },
            description: 'API authentication token'
          }
        ],
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                properties: {
                  title: { type: 'string', description: 'Opportunity title' },
                  description: { type: 'string', description: 'Detailed description' },
                  budget: { type: 'number', description: 'Budget in USD' },
                  category: { type: 'string', enum: ['technology', 'marketing', 'sales'] }
                },
                required: ['title', 'description', 'budget', 'category']
              }
            }
          },
          description: 'Opportunity details'
        },
        responses: [
          {
            statusCode: 201,
            description: 'Opportunity created successfully',
            schema: {
              type: 'object',
              properties: {
                id: { type: 'string' },
                status: { type: 'string' },
                matchingScore: { type: 'number' }
              }
            },
            examples: {
              success: {
                id: 'opp_123456789',
                status: 'active',
                matchingScore: 0.95
              }
            }
          }
        ],
        examples: [
          {
            name: 'Basic Opportunity',
            summary: 'Submit a technology opportunity',
            request: {
              url: '/api/v1/opportunities',
              method: 'POST',
              headers: {
                'Authorization': 'Bearer your-api-key',
                'Content-Type': 'application/json'
              },
              body: {
                title: 'AI Integration Project',
                description: 'Looking for AI expertise to enhance our platform',
                budget: 50000,
                category: 'technology'
              }
            },
            response: {
              status: 201,
              headers: { 'Content-Type': 'application/json' },
              body: {
                id: 'opp_123456789',
                status: 'active',
                matchingScore: 0.95,
                estimatedMatches: 12
              }
            }
          }
        ],
        sdkCode: [
          {
            language: 'typescript',
            code: `
import { LukhasClient } from '@lukhas/sdk';

const client = new LukhasClient('your-api-key');

const opportunity = await client.opportunities.create({
  title: 'AI Integration Project',
  description: 'Looking for AI expertise to enhance our platform',
  budget: 50000,
  category: 'technology'
});

console.log('Opportunity created:', opportunity.id);`,
            description: 'TypeScript SDK example'
          }
        ],
        authentication: ['api_key'],
        rateLimit: {
          requests: 100,
          window: '1h',
          scope: 'api_key'
        }
      }
    ];
  }

  private generateSessionId(): string {
    return `session_${randomBytes(16).toString('hex')}`;
  }

  private generateSandboxApiKey(sessionId: string): string {
    const payload = {
      sessionId,
      type: 'sandbox',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
    };
    return jwt.sign(payload, process.env.SANDBOX_JWT_SECRET || 'sandbox-secret');
  }

  private async generateInteractiveForm(endpoint: APIEndpoint): Promise<InteractiveForm> {
    return {
      method: endpoint.method,
      url: endpoint.path,
      parameters: endpoint.parameters.map(param => ({
        ...param,
        value: param.example,
        validation: this.createParameterValidator(param)
      })),
      requestBody: endpoint.requestBody ? {
        schema: endpoint.requestBody.content['application/json']?.schema,
        editor: 'json',
        defaultValue: this.generateDefaultRequestBody(endpoint.requestBody)
      } : undefined,
      submitHandler: 'sandbox_request'
    };
  }

  private async generateCodeExamples(endpoint: APIEndpoint): Promise<SDKCodeExample[]> {
    return [
      await this.generateTypeScriptExample(endpoint),
      await this.generateJavaScriptExample(endpoint),
      await this.generatePythonExample(endpoint),
      await this.generateCurlExample(endpoint)
    ];
  }

  private async generateTypeScriptCode(endpoint: APIEndpoint): Promise<string> {
    const clientMethod = endpoint.path.split('/').pop()?.toLowerCase() || 'request';
    const hasBody = endpoint.requestBody !== undefined;
    
    return `
import { LukhasClient } from '@lukhas/sdk';

const client = new LukhasClient(process.env.LUKHAS_API_KEY);

try {
  const result = await client.${clientMethod}(${hasBody ? 'requestData' : ''});
  console.log('Success:', result);
} catch (error) {
  console.error('Error:', error.message);
}`;
  }

  private async generateTypeScriptExample(endpoint: APIEndpoint): Promise<SDKCodeExample> {
    return {
      language: 'typescript',
      code: await this.generateTypeScriptCode(endpoint),
      description: 'TypeScript SDK implementation'
    };
  }

  private async generateJavaScriptExample(endpoint: APIEndpoint): Promise<SDKCodeExample> {
    return {
      language: 'javascript',
      code: await this.generateJavaScriptCode(endpoint),
      description: 'JavaScript SDK implementation'
    };
  }

  private async generateJavaScriptCode(endpoint: APIEndpoint): Promise<string> {
    return `
const { LukhasClient } = require('@lukhas/sdk');

const client = new LukhasClient(process.env.LUKHAS_API_KEY);

client.${endpoint.path.split('/').pop()?.toLowerCase() || 'request'}()
  .then(result => {
    console.log('Success:', result);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });`;
  }

  private async generatePythonExample(endpoint: APIEndpoint): Promise<SDKCodeExample> {
    return {
      language: 'python',
      code: await this.generatePythonCode(endpoint),
      description: 'Python SDK implementation'
    };
  }

  private async generatePythonCode(endpoint: APIEndpoint): Promise<string> {
    return `
import os
from lukhas import LukhasClient

client = LukhasClient(api_key=os.getenv('LUKHAS_API_KEY'))

try:
    result = client.${endpoint.path.split('/').pop()?.toLowerCase() || 'request'}()
    print(f"Success: {result}")
except Exception as error:
    print(f"Error: {error}")`;
  }

  private async generateCurlExample(endpoint: APIEndpoint): Promise<SDKCodeExample> {
    return {
      language: 'curl',
      code: await this.generateCurlCode(endpoint),
      description: 'cURL command example'
    };
  }

  private async generateCurlCode(endpoint: APIEndpoint): Promise<string> {
    const hasBody = endpoint.requestBody !== undefined;
    const bodyExample = hasBody ? '\n  -d \'{"example": "data"}\' \\' : '';
    
    return `
curl -X ${endpoint.method} \\
  https://api.lukhas.ai${endpoint.path} \\
  -H 'Authorization: Bearer your-api-key' \\
  -H 'Content-Type: application/json'${bodyExample}`;
  }

  private startSessionCleanup(): void {
    setInterval(() => {
      const now = new Date();
      for (const [sessionId, session] of this.sandboxSessions.entries()) {
        if (session.expiresAt < now) {
          this.sandboxSessions.delete(sessionId);
          this.emit('sandbox:session_expired', { sessionId });
        }
      }
    }, 60 * 1000); // Check every minute
  }

  private initializeDeveloperMetrics(developerId: string): DeveloperMetrics {
    return {
      developerId,
      period: {
        start: new Date(),
        end: new Date()
      },
      apiUsage: {
        totalRequests: 0,
        uniqueEndpoints: 0,
        errorRate: 0,
        avgResponseTime: 0
      },
      integration: {
        timeToFirstCall: 0,
        timeToProduction: 0,
        documentsViewed: [],
        examplesRun: 0
      },
      feedback: {
        rating: 0,
        comments: []
      }
    };
  }

  private createSchemaValidator(endpoint: APIEndpoint): Function {
    return (data: any) => {
      // Implementation would use a JSON Schema validator like Ajv
      return { valid: true, errors: [] };
    };
  }

  private createParameterValidator(param: APIParameter): Function {
    return (value: any) => {
      // Parameter-specific validation logic
      return { valid: true, message: '' };
    };
  }

  private generateDefaultRequestBody(requestBody: APIRequestBody): any {
    // Generate example request body based on schema
    return {};
  }

  private async generateSandboxURL(endpoint: APIEndpoint): Promise<string> {
    return `${process.env.SANDBOX_BASE_URL || 'https://sandbox-api.lukhas.ai'}${endpoint.path}`;
  }

  private async generateSandboxAuth(endpoint: APIEndpoint): Promise<any> {
    return {
      type: 'bearer',
      instructions: 'Use your sandbox API key from the session'
    };
  }

  private async generateErrorPreviews(endpoint: APIEndpoint): Promise<ErrorPreview[]> {
    return [
      {
        statusCode: 400,
        title: 'Bad Request',
        description: 'Invalid request parameters',
        example: { error: 'Missing required field: title' }
      },
      {
        statusCode: 401,
        title: 'Unauthorized',
        description: 'Invalid API key',
        example: { error: 'Invalid authentication credentials' }
      }
    ];
  }

  private async generateIntegrationSteps(platform: string, useCase: string): Promise<IntegrationStep[]> {
    return [
      {
        step: 1,
        title: 'Install SDK',
        description: `Install the LUKHAS ${platform} SDK`,
        code: `npm install @lukhas/sdk`,
        validation: 'Check that SDK is installed correctly'
      }
    ];
  }

  private async generatePlatformSpecificCode(platform: string): Promise<PlatformCodeExample[]> {
    return [
      {
        platform,
        scenario: 'Basic Setup',
        code: `// Platform-specific setup code`,
        description: 'Initial configuration'
      }
    ];
  }

  private async generateTroubleshootingGuide(platform: string): Promise<TroubleshootingItem[]> {
    return [
      {
        issue: 'Authentication Error',
        solution: 'Verify your API key is correct',
        code: 'client.authenticate(apiKey)'
      }
    ];
  }

  private async generateTestingChecklist(useCase: string): Promise<ChecklistItem[]> {
    return [
      { task: 'Test API connectivity', completed: false },
      { task: 'Validate request/response format', completed: false }
    ];
  }

  private async generateGoLiveChecklist(platform: string): Promise<ChecklistItem[]> {
    return [
      { task: 'Switch to production API keys', completed: false },
      { task: 'Configure error handling', completed: false }
    ];
  }
}

// Additional interfaces
interface InteractiveDocumentation {
  endpoint: APIEndpoint;
  interactiveForm: InteractiveForm;
  codeExamples: SDKCodeExample[];
  tryItLive: {
    enabled: boolean;
    sandboxUrl: string;
    authentication: any;
  };
  validation: {
    realTimeValidation: boolean;
    schemaValidator: Function;
    errorPreviews: ErrorPreview[];
  };
}

interface InteractiveForm {
  method: string;
  url: string;
  parameters: any[];
  requestBody?: {
    schema: JSONSchema;
    editor: string;
    defaultValue: any;
  };
  submitHandler: string;
}

interface ErrorPreview {
  statusCode: number;
  title: string;
  description: string;
  example: any;
}

interface DeveloperActivity {
  type: 'api_call' | 'documentation_view' | 'example_run';
  resource: string;
  error?: boolean;
  metadata?: Record<string, any>;
}

interface IntegrationGuide {
  platform: string;
  useCase: string;
  steps: IntegrationStep[];
  codeExamples: PlatformCodeExample[];
  troubleshooting: TroubleshootingItem[];
  testingChecklist: ChecklistItem[];
  goLiveChecklist: ChecklistItem[];
}

interface IntegrationStep {
  step: number;
  title: string;
  description: string;
  code?: string;
  validation: string;
}

interface PlatformCodeExample {
  platform: string;
  scenario: string;
  code: string;
  description: string;
}

interface TroubleshootingItem {
  issue: string;
  solution: string;
  code?: string;
}

interface ChecklistItem {
  task: string;
  completed: boolean;
}

interface APIExplorer {
  sessionId: string;
  baseUrl: string;
  authentication: {
    type: string;
    token: string;
  };
  endpoints: any[];
  realTimeValidation: boolean;
  responseInspector: boolean;
  requestHistory: any[];
}

interface OnboardingFlow {
  developerId: string;
  steps: OnboardingStep[];
  currentStep: number;
  completionRate: number;
  estimatedTimeToComplete: number;
}

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  action: string;
  endpoint?: string;
  completed: boolean;
}

// Export for use in other modules
export { DeveloperPortalConfig, APIEndpoint, SandboxSession, DeveloperMetrics };