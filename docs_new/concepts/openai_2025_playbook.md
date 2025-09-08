---
title: Openai 2025 Playbook
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["api", "testing", "monitoring", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic"]
  audience: ["dev"]
---

# OpenAI Integration Playbook 2025

## Overview

Complete integration guide for OpenAI APIs within LUKHAS AI's NIAS delivery engine. Covers 2025 API alignments, new models, safety policies, and cost optimization strategies for production deployment.

## API Strategy

### Model Selection Matrix

| Use Case | Model | Cost/1M Tokens | Response Time | Notes |
|----------|-------|----------------|---------------|--------|
| Creative Copy | `gpt-4o-mini` | $0.15 | ~200ms | Cost-optimized for short copy |
| Image Generation | `dall-e-3` | $0.080/image | ~10s | HD quality, 1024x1024 default |
| Content Moderation | `text-moderation-007` | Free | ~100ms | Always required for UGC |
| Complex Planning | `gpt-4o` | $5.00 | ~1s | Use for complex DAST queries |
| Function Calling | `gpt-4o` | $5.00 | ~800ms | JSON mode, tool use |

### 2025 API Updates

**Responses API (Beta)**
```javascript
// New structured response format for reliability
const response = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: prompt }],
  response_format: {
    type: "json_schema",
    json_schema: {
      name: "opportunity_response",
      strict: true,
      schema: opportunitySchema
    }
  }
});
```

**Vision Improvements**
- Enhanced image understanding for product analysis
- Better context retention across image/text sequences
- Support for multiple images per message

**Function Calling v3**
- Parallel function execution
- Better error handling and recovery
- Streaming function calls

## NIAS-Specific Implementation

### Creative Generation Pipeline

```javascript
import OpenAI from 'openai';
import { z } from 'zod';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID
});

// Zod schema for validation
const CreativeSchema = z.object({
  copy: z.string().max(90),
  image_prompt: z.string().min(20),
  tone: z.enum(['professional', 'casual', 'urgent']),
  compliance_flags: z.array(z.string()).optional()
});

class NIASCreativeEngine {
  constructor(options = {}) {
    this.model = options.model || 'gpt-4o-mini';
    this.temperature = options.temperature || 0.7;
    this.maxTokens = options.maxTokens || 300;
    this.cache = new Map(); // Simple cache for cost optimization
  }

  async generateCreative(opportunity, context) {
    const cacheKey = this.getCacheKey(opportunity, context);
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const systemPrompt = this.buildSystemPrompt();
    const userPrompt = JSON.stringify({ opportunity, context });

    try {
      const response = await client.chat.completions.create({
        model: this.model,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
        response_format: { 
          type: "json_schema",
          json_schema: {
            name: "creative_output",
            strict: true,
            schema: this.getCreativeSchema()
          }
        },
        temperature: this.temperature,
        max_tokens: this.maxTokens
      });

      const creative = JSON.parse(response.choices[0].message.content);
      
      // Validate with Zod
      const validated = CreativeSchema.parse(creative);
      
      // Moderate content
      const moderated = await this.moderateContent(validated);
      
      // Cache for 1 hour
      this.cache.set(cacheKey, moderated);
      setTimeout(() => this.cache.delete(cacheKey), 3600000);
      
      return moderated;
      
    } catch (error) {
      console.error('Creative generation failed:', error);
      return this.getFallbackCreative(opportunity);
    }
  }

  buildSystemPrompt() {
    return `You are the NIAS Creative Planner. Generate marketing copy and image prompts for product opportunities.

Rules:
- Copy must be ≤90 characters, non-manipulative, consent-respectful
- Avoid urgency ("last chance", "hurry") unless context.urgency=true
- Image prompts must be brand-safe, concrete scenes without logos
- Focus on utility and value, not emotional manipulation
- Maintain LUKHAS tone: helpful, transparent, user-first

Output only JSON: {"copy": "...", "image_prompt": "...", "tone": "...", "compliance_flags": [...]}`;
  }

  getCreativeSchema() {
    return {
      type: "object",
      properties: {
        copy: { type: "string", maxLength: 90 },
        image_prompt: { type: "string", minLength: 20 },
        tone: { type: "string", enum: ["professional", "casual", "urgent"] },
        compliance_flags: { 
          type: "array", 
          items: { type: "string" },
          description: "Potential compliance concerns"
        }
      },
      required: ["copy", "image_prompt", "tone"],
      additionalProperties: false
    };
  }

  async moderateContent(creative) {
    try {
      const moderation = await client.moderations.create({
        input: creative.copy,
        model: "text-moderation-007"
      });

      if (moderation.results[0].flagged) {
        const categories = Object.keys(moderation.results[0].categories)
          .filter(key => moderation.results[0].categories[key]);
        
        creative.compliance_flags = [...(creative.compliance_flags || []), ...categories];
        creative.copy = "Found this for you"; // Safe fallback
      }

      return creative;
    } catch (error) {
      console.error('Moderation failed:', error);
      return creative;
    }
  }

  getFallbackCreative(opportunity) {
    return {
      copy: "Found this for you",
      image_prompt: "Product in clean, minimal setting with soft natural lighting",
      tone: "professional",
      compliance_flags: ["fallback_used"]
    };
  }

  getCacheKey(opportunity, context) {
    return `${opportunity.id}_${context.season}_${context.style}_${context.urgency}`;
  }
}
```

### DAST Provider Integration

```javascript
class OpenAIDastProvider {
  constructor() {
    this.model = 'gpt-4o';
    this.temperature = 0.3; // Lower for more consistent structured output
  }

  async generateOpportunities(intent, context, consent) {
    const systemPrompt = `Role: DAST Provider
Goal: Given (intent, context, consent), return Opportunity[] matching schema.

Constraints:
- Only use sources in consent.scopes
- Fill risk.alignment in [0,1] based on user value match
- Populate provenance.sources with auditable strings
- Ensure economics splits ≤10000 basis points total
- All opportunities need valid window (start/end timestamps)

Output: JSON array of Opportunity objects only. No explanations.`;

    const userInput = JSON.stringify({ intent, context, consent });

    try {
      const response = await client.chat.completions.create({
        model: this.model,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userInput }
        ],
        response_format: { 
          type: "json_schema",
          json_schema: {
            name: "opportunities_response",
            strict: true,
            schema: this.getOpportunityArraySchema()
          }
        },
        temperature: this.temperature,
        max_tokens: 2000
      });

      const opportunities = JSON.parse(response.choices[0].message.content);
      return this.validateOpportunities(opportunities, consent);
      
    } catch (error) {
      console.error('DAST generation failed:', error);
      return [];
    }
  }

  getOpportunityArraySchema() {
    return {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          domain: { type: "string", pattern: "^\\w+\\.\\w+$" },
          title: { type: "string", maxLength: 90 },
          description: { type: "string", maxLength: 300 },
          price_current: { type: "number", minimum: 0 },
          price_alt: { type: "number", minimum: 0 },
          window: {
            type: "object",
            properties: {
              start: { type: "integer" },
              end: { type: "integer" }
            },
            required: ["start", "end"]
          },
          risk: {
            type: "object",
            properties: {
              alignment: { type: "number", minimum: -1, maximum: 1 },
              stress_block: { type: "boolean" },
              notes: { type: "string" }
            },
            required: ["alignment"]
          },
          economics: {
            type: "object",
            properties: {
              split_user_bps: { type: "integer", minimum: 0, maximum: 10000 },
              split_platform_bps: { type: "integer", minimum: 0, maximum: 10000 },
              tier: { type: "string", enum: ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"] }
            }
          },
          media: {
            type: "object",
            properties: {
              kind: { type: "string", enum: ["image", "video"] },
              cdn_url: { type: "string", format: "uri" },
              alt: { type: "string" },
              thumbnail_url: { type: "string", format: "uri" }
            },
            required: ["kind", "cdn_url", "alt"]
          },
          provenance: {
            type: "object",
            properties: {
              sources: { type: "array", items: { type: "string" } },
              version: { type: "string" },
              hash: { type: "string" }
            },
            required: ["sources", "version", "hash"]
          }
        },
        required: ["id", "domain", "title", "window", "risk", "media", "provenance"]
      }
    };
  }

  validateOpportunities(opportunities, consent) {
    return opportunities.filter(opp => {
      // Validate consent scope coverage
      const requiredSources = opp.provenance?.sources || [];
      const allowedScopes = consent.scopes || [];
      
      const hasValidSources = requiredSources.every(source => 
        allowedScopes.some(scope => source.includes(scope.split('.')[0]))
      );
      
      // Validate economics splits
      const userBps = opp.economics?.split_user_bps || 0;
      const platformBps = opp.economics?.split_platform_bps || 0;
      const validSplits = (userBps + platformBps) <= 10000;
      
      // Validate time window
      const validWindow = opp.window?.start < opp.window?.end;
      
      return hasValidSources && validSplits && validWindow;
    });
  }
}
```

## Safety & Compliance

### Content Moderation Pipeline

```javascript
class NIASModerationEngine {
  constructor() {
    this.client = new OpenAI();
    this.forbiddenPhrases = [
      "urgent", "last chance", "hurry", "act fast", "limited time",
      "don't miss", "you need", "must have", "exclusive offer"
    ];
  }

  async moderateContent(content) {
    const results = await Promise.all([
      this.openaiModeration(content),
      this.toneValidation(content),
      this.lengthValidation(content),
      this.complianceCheck(content)
    ]);

    return {
      approved: results.every(r => r.approved),
      flags: results.flatMap(r => r.flags || []),
      sanitized_content: results.find(r => r.sanitized)?.content || content
    };
  }

  async openaiModeration(content) {
    try {
      const response = await this.client.moderations.create({
        input: content,
        model: "text-moderation-007"
      });

      const result = response.results[0];
      if (result.flagged) {
        const categories = Object.keys(result.categories)
          .filter(key => result.categories[key]);
        
        return {
          approved: false,
          flags: categories,
          reason: "OpenAI moderation flagged content"
        };
      }

      return { approved: true };
    } catch (error) {
      console.error('OpenAI moderation failed:', error);
      return { approved: false, flags: ["moderation_error"] };
    }
  }

  toneValidation(content) {
    const lowerContent = content.toLowerCase();
    const flaggedPhrases = this.forbiddenPhrases.filter(phrase => 
      lowerContent.includes(phrase)
    );

    if (flaggedPhrases.length > 0) {
      return {
        approved: false,
        flags: flaggedPhrases.map(phrase => `forbidden_phrase:${phrase}`),
        sanitized: "Found this for you"
      };
    }

    return { approved: true };
  }

  lengthValidation(content) {
    if (content.length > 90) {
      return {
        approved: false,
        flags: ["excessive_length"],
        sanitized: content.substring(0, 87) + "..."
      };
    }

    return { approved: true };
  }

  complianceCheck(content) {
    const gdprTriggers = ["personal data", "track", "cookies", "profile"];
    const flags = gdprTriggers.filter(trigger => 
      content.toLowerCase().includes(trigger)
    );

    return {
      approved: flags.length === 0,
      flags: flags.map(flag => `gdpr_concern:${flag}`)
    };
  }
}
```

## Cost Optimization

### Token Management Strategy

```javascript
class TokenOptimizer {
  constructor() {
    this.tokenCosts = {
      'gpt-4o': { input: 0.005, output: 0.015 },
      'gpt-4o-mini': { input: 0.00015, output: 0.0006 },
      'dall-e-3': { image: 0.080 }
    };
  }

  async optimizeRequest(prompt, requirements) {
    // Choose model based on complexity
    const model = this.selectOptimalModel(prompt, requirements);
    
    // Compress prompt if possible
    const optimizedPrompt = this.compressPrompt(prompt);
    
    // Estimate cost
    const estimatedCost = this.estimateCost(optimizedPrompt, model);
    
    return {
      model,
      prompt: optimizedPrompt,
      estimated_cost: estimatedCost,
      max_tokens: this.calculateMaxTokens(requirements)
    };
  }

  selectOptimalModel(prompt, requirements) {
    const complexity = this.assessComplexity(prompt, requirements);
    
    if (complexity.score < 0.3) {
      return 'gpt-4o-mini'; // Simple copy generation
    } else if (complexity.score < 0.7) {
      return 'gpt-4o-mini'; // Most NIAS tasks
    } else {
      return 'gpt-4o'; // Complex planning/reasoning
    }
  }

  assessComplexity(prompt, requirements) {
    let score = 0;
    
    // JSON schema complexity
    if (requirements.schema) {
      score += Object.keys(requirements.schema.properties || {}).length * 0.1;
    }
    
    // Prompt length
    score += Math.min(prompt.length / 1000, 0.5);
    
    // Function calling
    if (requirements.functions) {
      score += 0.3;
    }
    
    // Reasoning requirements
    const reasoningKeywords = ['analyze', 'compare', 'evaluate', 'synthesize'];
    if (reasoningKeywords.some(kw => prompt.toLowerCase().includes(kw))) {
      score += 0.4;
    }
    
    return { score: Math.min(score, 1.0) };
  }

  compressPrompt(prompt) {
    return prompt
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/\n\s*\n/g, '\n') // Remove empty lines
      .trim();
  }

  estimateCost(prompt, model) {
    const inputTokens = Math.ceil(prompt.length / 4); // Rough estimate
    const outputTokens = 200; // Average for NIAS responses
    
    const costs = this.tokenCosts[model];
    return (inputTokens * costs.input / 1000) + (outputTokens * costs.output / 1000);
  }

  calculateMaxTokens(requirements) {
    if (requirements.type === 'creative') return 300;
    if (requirements.type === 'opportunities') return 2000;
    if (requirements.type === 'simple') return 150;
    return 500;
  }
}
```

## Monitoring & Analytics

### Usage Tracking

```javascript
class OpenAIUsageTracker {
  constructor() {
    this.metrics = {
      requests: 0,
      tokens_used: 0,
      cost_total: 0,
      errors: 0,
      cache_hits: 0
    };
  }

  async trackRequest(model, inputTokens, outputTokens, cached = false) {
    this.metrics.requests++;
    
    if (cached) {
      this.metrics.cache_hits++;
    } else {
      this.metrics.tokens_used += inputTokens + outputTokens;
      this.metrics.cost_total += this.calculateCost(model, inputTokens, outputTokens);
    }
    
    // Log to monitoring system
    await this.logMetrics();
  }

  calculateCost(model, inputTokens, outputTokens) {
    const costs = {
      'gpt-4o': { input: 0.005, output: 0.015 },
      'gpt-4o-mini': { input: 0.00015, output: 0.0006 }
    };
    
    const modelCosts = costs[model] || costs['gpt-4o-mini'];
    return (inputTokens * modelCosts.input / 1000) + (outputTokens * modelCosts.output / 1000);
  }

  async logMetrics() {
    // Send to monitoring system (e.g., DataDog, New Relic)
    console.log('OpenAI Usage:', this.metrics);
  }

  getCostEfficiency() {
    return {
      cost_per_request: this.metrics.cost_total / this.metrics.requests,
      cache_hit_rate: this.metrics.cache_hits / this.metrics.requests,
      tokens_per_request: this.metrics.tokens_used / this.metrics.requests
    };
  }
}
```

## Error Handling & Resilience

### Retry Strategy with Exponential Backoff

```javascript
class ResilientOpenAIClient {
  constructor() {
    this.client = new OpenAI();
    this.maxRetries = 3;
    this.baseDelay = 1000; // 1 second
  }

  async makeRequest(requestConfig, retryCount = 0) {
    try {
      const response = await this.client.chat.completions.create(requestConfig);
      return response;
    } catch (error) {
      if (retryCount >= this.maxRetries) {
        throw new Error(`OpenAI request failed after ${this.maxRetries} retries: ${error.message}`);
      }

      const shouldRetry = this.shouldRetry(error);
      if (!shouldRetry) {
        throw error;
      }

      const delay = this.calculateDelay(retryCount);
      await this.sleep(delay);

      return this.makeRequest(requestConfig, retryCount + 1);
    }
  }

  shouldRetry(error) {
    // Retry on rate limits, server errors, timeouts
    const retryableErrors = [429, 500, 502, 503, 504];
    return retryableErrors.includes(error.status) || 
           error.code === 'ECONNRESET' ||
           error.code === 'ETIMEDOUT';
  }

  calculateDelay(retryCount) {
    return this.baseDelay * Math.pow(2, retryCount) + Math.random() * 1000; // Jitter
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## Environment Configuration

### Production Setup

```bash
# Environment Variables
OPENAI_API_KEY=sk-proj-...
OPENAI_ORG_ID=org-...
OPENAI_PROJECT_ID=proj_...

# Rate Limiting
OPENAI_MAX_REQUESTS_PER_MINUTE=3000
OPENAI_MAX_TOKENS_PER_MINUTE=150000

# Model Selection
NIAS_CREATIVE_MODEL=gpt-4o-mini
DAST_PROVIDER_MODEL=gpt-4o
MODERATION_MODEL=text-moderation-007

# Caching
CREATIVE_CACHE_TTL=3600
OPPORTUNITY_CACHE_TTL=1800
```

### Development vs Production

```javascript
const config = {
  development: {
    model: 'gpt-4o-mini',
    temperature: 0.8,
    max_tokens: 500,
    cache_enabled: false,
    verbose_logging: true
  },
  production: {
    model: 'gpt-4o-mini',
    temperature: 0.7,
    max_tokens: 300,
    cache_enabled: true,
    verbose_logging: false,
    rate_limiting: true,
    retry_enabled: true
  }
};
```

## Testing Strategy

### Unit Tests for OpenAI Integration

```javascript
import { jest } from '@jest/globals';
import { NIASCreativeEngine } from '../src/nias-creative-engine.js';

describe('NIASCreativeEngine', () => {
  let engine;
  
  beforeEach(() => {
    engine = new NIASCreativeEngine({
      model: 'gpt-4o-mini',
      temperature: 0.5
    });
    
    // Mock OpenAI client
    jest.mock('openai');
  });

  test('should generate valid creative within length limits', async () => {
    const opportunity = {
      id: 'test-opp-123',
      domain: 'retail.pet_food',
      title: 'Acme Dog Food 10kg'
    };
    
    const context = {
      season: 'autumn',
      style: 'minimal',
      urgency: false
    };

    const result = await engine.generateCreative(opportunity, context);
    
    expect(result.copy).toBeDefined();
    expect(result.copy.length).toBeLessThanOrEqual(90);
    expect(result.image_prompt).toBeDefined();
    expect(result.tone).toMatch(/^(professional|casual|urgent)$/);
  });

  test('should handle rate limiting gracefully', async () => {
    // Mock rate limit error
    const rateLimitError = new Error('Rate limit exceeded');
    rateLimitError.status = 429;
    
    jest.spyOn(engine.client, 'chat.completions.create')
        .mockRejectedValueOnce(rateLimitError)
        .mockResolvedValueOnce({
          choices: [{ message: { content: '{"copy":"Fallback copy","image_prompt":"Fallback image"}' }}]
        });

    const result = await engine.generateCreative(opportunity, context);
    expect(result.copy).toBeDefined();
  });

  test('should cache results properly', async () => {
    const opportunity = { id: 'cache-test' };
    const context = { season: 'winter' };
    
    // First call
    const result1 = await engine.generateCreative(opportunity, context);
    
    // Second call should be cached
    const result2 = await engine.generateCreative(opportunity, context);
    
    expect(result1).toEqual(result2);
    expect(engine.cache.size).toBe(1);
  });
});
```

## Deployment Checklist

- [ ] OpenAI API key configured with appropriate permissions
- [ ] Rate limiting configured for production traffic
- [ ] Content moderation pipeline tested
- [ ] Cost monitoring dashboard set up
- [ ] Error logging and alerting configured
- [ ] Cache strategy implemented and tested
- [ ] Fallback responses defined for all failure modes
- [ ] Load testing completed for expected traffic
- [ ] Compliance review for generated content
- [ ] A/B testing framework for creative optimization

## Performance Targets

| Metric | Target | Measurement |
|--------|---------|-------------|
| Response Time | <500ms p95 | API latency |
| Cost per Creative | <$0.01 | Token usage tracking |
| Cache Hit Rate | >60% | Redis metrics |
| Error Rate | <1% | Error monitoring |
| Content Safety | 100% | Moderation pipeline |

## Next Steps

1. Implement SDK templates for easy merchant integration
2. Create TEQ compliance bundle with GDPR alignment
3. Set up attribution fallback ladder with S2S postback
4. Define auto-escalator split policy for profit sharing
5. Build comprehensive monitoring dashboard
6. Establish A/B testing for creative optimization