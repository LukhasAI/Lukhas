/**
 * LUKHAS Publisher SDK - Production-Grade TypeScript Implementation  
 * 0.001% Engineering: WordPress/Shopify integration, real-time optimization, audience insights
 */

import crypto from 'crypto';

// Publisher SDK Configuration
export interface PublisherSDKConfig {
  apiKey: string;
  publisherId: string;
  baseURL?: string;
  environment?: 'production' | 'staging' | 'development';
  maxRetries?: number;
  timeoutMs?: number;
  enableTelemetry?: boolean;
  rateLimitRpm?: number;
  cacheEnabled?: boolean;
  cacheTtlSeconds?: number;
}

// Content and audience interfaces
export interface ContentContext {
  contentType: 'article' | 'product_review' | 'comparison' | 'tutorial' | 'news' | 'video' | 'podcast';
  title: string;
  description?: string;
  category: string;
  tags: string[];
  language?: string;
  publishedAt?: string;
  author?: {
    id: string;
    name: string;
    expertise_areas: string[];
  };
  seo: {
    keywords: string[];
    meta_description?: string;
    readability_score?: number;
  };
  engagement_data?: {
    page_views: number;
    time_on_page_seconds: number;
    bounce_rate: number;
    social_shares: number;
  };
}

export interface AudienceProfile {
  demographics: {
    age_ranges: Record<string, number>; // e.g., "25-34": 0.3
    gender_distribution: Record<string, number>;
    income_ranges: Record<string, number>;
    geographic_distribution: Record<string, number>; // country codes
  };
  interests: {
    categories: Record<string, number>; // interest category -> score
    brands: Record<string, number>; // brand affinity scores
    price_sensitivity: 'low' | 'medium' | 'high';
    purchase_intent_score: number; // 0-1
  };
  behavior: {
    device_preferences: Record<string, number>; // mobile/desktop/tablet
    shopping_frequency: 'daily' | 'weekly' | 'monthly' | 'occasional';
    content_engagement_patterns: Record<string, number>;
    conversion_likelihood: number; // 0-1
  };
  size_estimate: number; // estimated audience size
  quality_score: number; // 0-1, based on engagement and conversion history
}

export interface OpportunityRequest {
  content_context: ContentContext;
  audience_profile?: Partial<AudienceProfile>;
  placement: {
    position: 'header' | 'sidebar' | 'in_content' | 'footer' | 'overlay' | 'native';
    format: 'banner' | 'card' | 'text_link' | 'product_widget' | 'comparison_table';
    max_count: number;
    size_constraints?: {
      max_width: number;
      max_height: number;
      responsive: boolean;
    };
  };
  targeting: {
    geo_targets?: string[];
    exclude_competitors?: boolean;
    price_range?: { min: number; max: number; currency: string };
    categories?: string[];
    brands?: string[];
  };
  optimization: {
    objective: 'revenue' | 'clicks' | 'conversions' | 'engagement';
    personalization_level: 'none' | 'basic' | 'advanced';
    a_b_test_variants?: number;
    frequency_cap?: number;
  };
}

export interface Opportunity {
  id: string;
  title: string;
  description: string;
  merchant: {
    id: string;
    name: string;
    trust_score: number;
    logo_url?: string;
  };
  product: {
    price: number;
    currency: string;
    image_url: string;
    rating?: number;
    review_count?: number;
    availability: 'in_stock' | 'limited' | 'out_of_stock';
    category: string;
    brand?: string;
  };
  economics: {
    commission_rate: number; // 0-1
    estimated_earnings: number;
    payout_terms: string;
    currency: string;
  };
  targeting: {
    alignment_score: number; // 0-1, how well this matches the request
    audience_match: number; // 0-1, how well this matches the audience
    content_relevance: number; // 0-1, how relevant to the content
    conversion_probability: number; // 0-1, likelihood of conversion
  };
  creative: {
    primary_cta: string;
    secondary_cta?: string;
    visual_assets: {
      banner_urls: Record<string, string>; // size -> url
      product_images: string[];
      logo_url?: string;
    };
    copy_variants: {
      headline: string[];
      description: string[];
      cta_text: string[];
    };
  };
  tracking: {
    impression_url: string;
    click_url: string;
    conversion_tracking: {
      pixel_url?: string;
      postback_url?: string;
      attribution_window_hours: number;
    };
  };
  metadata: {
    campaign_id: string;
    expires_at: string;
    priority: number;
    abas_approved: boolean;
    fraud_score: number; // 0-1, lower is better
  };
}

export interface OpportunityResponse {
  request_id: string;
  opportunities: Opportunity[];
  audience_insights: {
    detected_segments: string[];
    engagement_predictions: Record<string, number>;
    optimization_suggestions: string[];
    competitive_landscape: {
      similar_content: Array<{
        url: string;
        performance_estimate: number;
      }>;
    };
  };
  performance_predictions: {
    estimated_ctr: number;
    estimated_conversion_rate: number;
    estimated_revenue_per_view: number;
    confidence_interval: { min: number; max: number };
  };
  next_optimization_check: string; // ISO timestamp
}

export interface PerformanceReport {
  publisher_id: string;
  period: {
    start_date: string;
    end_date: string;
  };
  summary: {
    total_impressions: number;
    total_clicks: number;
    total_conversions: number;
    total_revenue: number;
    ctr: number;
    conversion_rate: number;
    rpm: number; // Revenue per mille (thousand impressions)
    average_commission_rate: number;
  };
  top_performing: {
    opportunities: Array<{
      opportunity_id: string;
      title: string;
      impressions: number;
      revenue: number;
      ctr: number;
    }>;
    content_types: Array<{
      content_type: string;
      revenue: number;
      conversion_rate: number;
    }>;
    merchants: Array<{
      merchant_id: string;
      merchant_name: string;
      revenue: number;
      avg_commission_rate: number;
    }>;
  };
  audience_insights: {
    most_engaged_segments: string[];
    conversion_drivers: string[];
    optimization_opportunities: string[];
  };
  trends: {
    revenue_trend: Array<{ date: string; revenue: number }>;
    performance_changes: {
      ctr_change: number;
      conversion_rate_change: number;
      revenue_change: number;
    };
  };
}

export interface PublisherProfile {
  publisher_id: string;
  website: {
    domain: string;
    category: string;
    monthly_visitors: number;
    page_views_per_month: number;
    average_session_duration: number;
    bounce_rate: number;
  };
  content: {
    primary_topics: string[];
    content_quality_score: number; // 0-1
    update_frequency: 'daily' | 'weekly' | 'monthly';
    content_depth_score: number; // 0-1
  };
  audience: AudienceProfile;
  performance: {
    historical_ctr: number;
    historical_conversion_rate: number;
    revenue_per_visitor: number;
    trust_score: number; // 0-1
    fraud_risk_score: number; // 0-1, lower is better
  };
  monetization: {
    current_partners: string[];
    preferred_categories: string[];
    min_commission_rate: number;
    payment_preferences: string[];
  };
}

// Publisher SDK Error Classes
export class PublisherSDKError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public retryable: boolean = false,
    public context?: Record<string, any>
  ) {
    super(message);
    this.name = 'PublisherSDKError';
  }
}

export class ContentValidationError extends PublisherSDKError {
  constructor(message: string, public field: string, public value: any) {
    super(message, 'CONTENT_VALIDATION_ERROR', 400, false, { field, value });
  }
}

export class AudienceInsightsError extends PublisherSDKError {
  constructor(message: string, public insights: any) {
    super(message, 'AUDIENCE_INSIGHTS_ERROR', 422, false, { insights });
  }
}

// In-memory cache for optimization
class OptimizationCache {
  private cache = new Map<string, { data: any; expires: number }>();
  
  constructor(private defaultTtlSeconds = 300) {} // 5 minutes default
  
  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry || Date.now() > entry.expires) {
      this.cache.delete(key);
      return null;
    }
    return entry.data;
  }
  
  set(key: string, data: any, ttlSeconds?: number): void {
    this.cache.set(key, {
      data,
      expires: Date.now() + (ttlSeconds || this.defaultTtlSeconds) * 1000
    });
  }
  
  clear(): void {
    this.cache.clear();
  }
}

export class LukhasPublisherSDK {
  private readonly config: Required<PublisherSDKConfig>;
  private lastRequestTime = 0;
  private cache: OptimizationCache;
  private telemetryData: Array<{
    operation: string;
    duration_ms: number;
    success: boolean;
    cache_hit?: boolean;
    timestamp: number;
  }> = [];

  constructor(config: PublisherSDKConfig) {
    // Validate required configuration
    if (!config.apiKey || !config.publisherId) {
      throw new ContentValidationError('apiKey and publisherId are required', 'config', config);
    }

    if (!config.apiKey.match(/^sk_publisher_[a-zA-Z0-9_]+$/)) {
      throw new ContentValidationError('Invalid API key format', 'apiKey', config.apiKey);
    }

    // Set defaults
    this.config = {
      ...config,
      baseURL: config.baseURL || 'https://api.lukhas.ai/v1',
      environment: config.environment || 'production',
      maxRetries: Math.max(1, Math.min(5, config.maxRetries || 3)),
      timeoutMs: Math.max(1000, Math.min(30000, config.timeoutMs || 8000)),
      enableTelemetry: config.enableTelemetry !== false,
      rateLimitRpm: Math.max(100, Math.min(5000, config.rateLimitRpm || 2000)),
      cacheEnabled: config.cacheEnabled !== false,
      cacheTtlSeconds: Math.max(30, Math.min(3600, config.cacheTtlSeconds || 300))
    };

    this.cache = new OptimizationCache(this.config.cacheTtlSeconds);

    console.log(`📰 LUKHAS Publisher SDK initialized for ${this.config.publisherId} (${this.config.environment})`);
  }

  /**
   * Request contextual opportunities with advanced targeting
   */
  async requestOpportunities(request: OpportunityRequest): Promise<OpportunityResponse> {
    const startTime = Date.now();
    let cacheHit = false;

    try {
      // Validate request
      this.validateOpportunityRequest(request);

      // Check cache if enabled
      const cacheKey = this.generateCacheKey('opportunities', request);
      if (this.config.cacheEnabled) {
        const cached = this.cache.get(cacheKey);
        if (cached) {
          cacheHit = true;
          this.recordTelemetry('requestOpportunities', Date.now() - startTime, true, true);
          return cached;
        }
      }

      const enrichedRequest = await this.enrichRequest(request);
      
      const response = await this.makeRequest<OpportunityResponse>(
        'POST',
        '/opportunities/request',
        {
          publisher_id: this.config.publisherId,
          ...enrichedRequest,
          metadata: {
            sdk_version: '2.0.0',
            request_timestamp: new Date().toISOString(),
            cache_enabled: this.config.cacheEnabled
          }
        }
      );

      // Cache successful response
      if (this.config.cacheEnabled && response.opportunities.length > 0) {
        this.cache.set(cacheKey, response);
      }

      this.recordTelemetry('requestOpportunities', Date.now() - startTime, true, cacheHit);
      return response;

    } catch (error) {
      this.recordTelemetry('requestOpportunities', Date.now() - startTime, false, cacheHit);
      throw this.wrapError(error, 'requestOpportunities');
    }
  }

  /**
   * Track opportunity impression for analytics
   */
  async trackImpression(
    opportunityId: string,
    context: {
      position: string;
      viewport_size: { width: number; height: number };
      user_agent?: string;
      referrer?: string;
      session_id?: string;
    }
  ): Promise<{ tracked: boolean; next_optimization_trigger?: number }> {
    const startTime = Date.now();

    try {
      if (!opportunityId.match(/^opp_[a-zA-Z0-9_]+$/)) {
        throw new ContentValidationError('Invalid opportunity ID format', 'opportunityId', opportunityId);
      }

      const response = await this.makeRequest<{ tracked: boolean; next_optimization_trigger?: number }>(
        'POST',
        '/events/impression',
        {
          publisher_id: this.config.publisherId,
          opportunity_id: opportunityId,
          context: {
            ...context,
            timestamp: new Date().toISOString(),
            sdk_version: '2.0.0'
          }
        }
      );

      this.recordTelemetry('trackImpression', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('trackImpression', Date.now() - startTime, false);
      throw this.wrapError(error, 'trackImpression');
    }
  }

  /**
   * Track opportunity click for attribution
   */
  async trackClick(
    opportunityId: string,
    context: {
      click_position: { x: number; y: number };
      element_type: string;
      user_agent?: string;
      session_id?: string;
    }
  ): Promise<{ 
    tracked: boolean; 
    redirect_url: string; 
    attribution_id: string 
  }> {
    const startTime = Date.now();

    try {
      if (!opportunityId.match(/^opp_[a-zA-Z0-9_]+$/)) {
        throw new ContentValidationError('Invalid opportunity ID format', 'opportunityId', opportunityId);
      }

      const response = await this.makeRequest<{
        tracked: boolean;
        redirect_url: string;
        attribution_id: string;
      }>(
        'POST',
        '/events/click',
        {
          publisher_id: this.config.publisherId,
          opportunity_id: opportunityId,
          context: {
            ...context,
            timestamp: new Date().toISOString(),
            sdk_version: '2.0.0'
          }
        }
      );

      this.recordTelemetry('trackClick', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('trackClick', Date.now() - startTime, false);
      throw this.wrapError(error, 'trackClick');
    }
  }

  /**
   * Get comprehensive performance report
   */
  async getPerformanceReport(options: {
    period?: 'last_24h' | 'last_7d' | 'last_30d' | 'last_90d' | 'custom';
    startDate?: string;
    endDate?: string;
    breakdown?: ('daily' | 'weekly' | 'monthly')[];
    includeForecasting?: boolean;
    includeCompetitiveAnalysis?: boolean;
  } = {}): Promise<PerformanceReport> {
    const startTime = Date.now();

    try {
      const params = new URLSearchParams({
        publisher_id: this.config.publisherId,
        period: options.period || 'last_7d',
        breakdown: (options.breakdown || ['daily']).join(','),
        include_forecasting: options.includeForecasting ? 'true' : 'false',
        include_competitive: options.includeCompetitiveAnalysis ? 'true' : 'false'
      });

      if (options.startDate) params.append('start_date', options.startDate);
      if (options.endDate) params.append('end_date', options.endDate);

      const response = await this.makeRequest<PerformanceReport>(
        'GET',
        `/publishers/${this.config.publisherId}/performance?${params}`
      );

      this.recordTelemetry('getPerformanceReport', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('getPerformanceReport', Date.now() - startTime, false);
      throw this.wrapError(error, 'getPerformanceReport');
    }
  }

  /**
   * Get and update publisher profile
   */
  async getPublisherProfile(): Promise<PublisherProfile> {
    const startTime = Date.now();

    try {
      const response = await this.makeRequest<PublisherProfile>(
        'GET',
        `/publishers/${this.config.publisherId}/profile`
      );

      this.recordTelemetry('getPublisherProfile', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('getPublisherProfile', Date.now() - startTime, false);
      throw this.wrapError(error, 'getPublisherProfile');
    }
  }

  /**
   * Update publisher profile with new data
   */
  async updatePublisherProfile(updates: Partial<PublisherProfile>): Promise<PublisherProfile> {
    const startTime = Date.now();

    try {
      // Validate and sanitize updates
      const allowedFields = [
        'website', 'content', 'monetization'
      ];
      
      const sanitizedUpdates = this.sanitizeUpdates(updates, allowedFields);
      sanitizedUpdates.updated_at = new Date().toISOString();

      const response = await this.makeRequest<PublisherProfile>(
        'PATCH',
        `/publishers/${this.config.publisherId}/profile`,
        sanitizedUpdates
      );

      this.recordTelemetry('updatePublisherProfile', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('updatePublisherProfile', Date.now() - startTime, false);
      throw this.wrapError(error, 'updatePublisherProfile');
    }
  }

  /**
   * Get real-time audience insights
   */
  async getAudienceInsights(contentContext: ContentContext): Promise<{
    audience_segments: Array<{
      segment_id: string;
      name: string;
      size_estimate: number;
      engagement_score: number;
      conversion_likelihood: number;
      recommended_opportunities: string[];
    }>;
    content_optimization: {
      keyword_suggestions: string[];
      content_gaps: string[];
      trending_topics: string[];
      seo_recommendations: string[];
    };
    monetization_potential: {
      estimated_rpm: number;
      optimal_ad_positions: string[];
      recommended_formats: string[];
      seasonal_trends: Record<string, number>;
    };
  }> {
    const startTime = Date.now();

    try {
      this.validateContentContext(contentContext);

      const response = await this.makeRequest<any>(
        'POST',
        `/publishers/${this.config.publisherId}/insights`,
        {
          content_context: contentContext,
          analysis_type: 'comprehensive',
          include_predictions: true
        }
      );

      this.recordTelemetry('getAudienceInsights', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('getAudienceInsights', Date.now() - startTime, false);
      throw this.wrapError(error, 'getAudienceInsights');
    }
  }

  /**
   * A/B test different opportunity presentations
   */
  async createABTest(testConfig: {
    name: string;
    variants: Array<{
      variant_id: string;
      opportunity_request: OpportunityRequest;
      traffic_allocation: number; // 0-1
    }>;
    success_metric: 'ctr' | 'conversion_rate' | 'revenue_per_impression';
    duration_days: number;
    minimum_sample_size?: number;
  }): Promise<{
    test_id: string;
    status: 'created' | 'running' | 'completed';
    estimated_completion_date: string;
    traffic_split: Record<string, number>;
  }> {
    const startTime = Date.now();

    try {
      // Validate test configuration
      if (testConfig.variants.length < 2 || testConfig.variants.length > 5) {
        throw new ContentValidationError('Test must have 2-5 variants', 'variants', testConfig.variants);
      }

      const totalAllocation = testConfig.variants.reduce((sum, v) => sum + v.traffic_allocation, 0);
      if (Math.abs(totalAllocation - 1.0) > 0.01) {
        throw new ContentValidationError('Traffic allocation must sum to 1.0', 'traffic_allocation', totalAllocation);
      }

      const response = await this.makeRequest<any>(
        'POST',
        `/publishers/${this.config.publisherId}/ab-tests`,
        {
          ...testConfig,
          created_at: new Date().toISOString(),
          sdk_version: '2.0.0'
        }
      );

      this.recordTelemetry('createABTest', Date.now() - startTime, true);
      return response;

    } catch (error) {
      this.recordTelemetry('createABTest', Date.now() - startTime, false);
      throw this.wrapError(error, 'createABTest');
    }
  }

  /**
   * WordPress integration helper
   */
  generateWordPressShortcode(
    opportunityRequest: OpportunityRequest,
    options: {
      shortcode_name?: string;
      cache_duration?: number;
      lazy_load?: boolean;
    } = {}
  ): string {
    const shortcodeName = options.shortcode_name || 'lukhas_opportunities';
    const encodedRequest = Buffer.from(JSON.stringify(opportunityRequest)).toString('base64');
    
    const attributes = [
      `request="${encodedRequest}"`,
      `publisher_id="${this.config.publisherId}"`,
      `cache_duration="${options.cache_duration || 300}"`,
      `lazy_load="${options.lazy_load !== false ? 'true' : 'false'}"`
    ];

    return `[${shortcodeName} ${attributes.join(' ')}]`;
  }

  /**
   * Shopify integration helper
   */
  generateShopifySnippet(
    opportunityRequest: OpportunityRequest,
    containerId: string
  ): string {
    const config = {
      publisherId: this.config.publisherId,
      apiKey: this.config.apiKey,
      baseURL: this.config.baseURL,
      request: opportunityRequest,
      containerId
    };

    return `
<div id="${containerId}"></div>
<script>
  (function() {
    var config = ${JSON.stringify(config, null, 2)};
    var script = document.createElement('script');
    script.src = '${this.config.baseURL}/sdk/shopify.js';
    script.async = true;
    script.onload = function() {
      new LukhasShopifyWidget(config);
    };
    document.head.appendChild(script);
  })();
</script>
    `.trim();
  }

  /**
   * Get SDK telemetry data
   */
  getTelemetryData(): {
    summary: {
      total_operations: number;
      success_rate: number;
      cache_hit_rate: number;
      avg_latency_ms: number;
    };
    operations: Record<string, {
      count: number;
      success_rate: number;
      avg_latency_ms: number;
      cache_hit_rate?: number;
    }>;
  } {
    const now = Date.now();
    const recentData = this.telemetryData.filter(t => now - t.timestamp < 3600000); // Last hour

    const successfulOps = recentData.filter(t => t.success);
    const cacheHits = recentData.filter(t => t.cache_hit);

    const operationStats = recentData.reduce((stats, op) => {
      if (!stats[op.operation]) {
        stats[op.operation] = { count: 0, successes: 0, total_latency: 0, cache_hits: 0 };
      }
      stats[op.operation].count++;
      if (op.success) stats[op.operation].successes++;
      if (op.cache_hit) stats[op.operation].cache_hits++;
      stats[op.operation].total_latency += op.duration_ms;
      return stats;
    }, {} as Record<string, any>);

    const operations = Object.entries(operationStats).reduce((result, [op, stats]) => {
      result[op] = {
        count: stats.count,
        success_rate: stats.count > 0 ? stats.successes / stats.count : 0,
        avg_latency_ms: stats.count > 0 ? stats.total_latency / stats.count : 0,
        cache_hit_rate: stats.count > 0 ? stats.cache_hits / stats.count : undefined
      };
      return result;
    }, {} as Record<string, any>);

    return {
      summary: {
        total_operations: recentData.length,
        success_rate: recentData.length > 0 ? successfulOps.length / recentData.length : 0,
        cache_hit_rate: recentData.length > 0 ? cacheHits.length / recentData.length : 0,
        avg_latency_ms: recentData.length > 0 ? 
          recentData.reduce((sum, t) => sum + t.duration_ms, 0) / recentData.length : 0
      },
      operations
    };
  }

  // Private helper methods

  private async makeRequest<T>(method: string, endpoint: string, data?: any): Promise<T> {
    await this.enforceRateLimit();

    const url = `${this.config.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${this.config.apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': `LukhasPublisherSDK/2.0.0 (${this.config.environment})`,
      'X-Publisher-ID': this.config.publisherId,
      'X-SDK-Version': '2.0.0',
      'X-Request-ID': crypto.randomUUID()
    };

    const options: RequestInit = {
      method,
      headers,
      signal: AbortSignal.timeout(this.config.timeoutMs)
    };

    if (data && ['POST', 'PATCH', 'PUT'].includes(method)) {
      options.body = JSON.stringify(data);
    }

    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        const response = await fetch(url, options);
        
        if (response.status === 429) {
          const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
          await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
          continue;
        }

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new PublisherSDKError(
            errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            errorData.code || 'HTTP_ERROR',
            response.status,
            response.status >= 500,
            errorData
          );
        }

        return await response.json() as T;

      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        
        if (error instanceof PublisherSDKError && !error.retryable) {
          throw error;
        }

        if (attempt < this.config.maxRetries) {
          const backoffMs = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
          await new Promise(resolve => setTimeout(resolve, backoffMs));
        }
      }
    }

    throw lastError;
  }

  private async enforceRateLimit(): Promise<void> {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    const minInterval = 60000 / this.config.rateLimitRpm;

    if (timeSinceLastRequest < minInterval) {
      const waitTime = minInterval - timeSinceLastRequest;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    this.lastRequestTime = Date.now();
  }

  private validateOpportunityRequest(request: OpportunityRequest): void {
    this.validateContentContext(request.content_context);

    if (!request.placement || !request.placement.position || !request.placement.format) {
      throw new ContentValidationError('Placement configuration is required', 'placement', request.placement);
    }

    if (!request.optimization || !request.optimization.objective) {
      throw new ContentValidationError('Optimization configuration is required', 'optimization', request.optimization);
    }

    if (request.placement.max_count < 1 || request.placement.max_count > 20) {
      throw new ContentValidationError('Max count must be 1-20', 'placement.max_count', request.placement.max_count);
    }
  }

  private validateContentContext(context: ContentContext): void {
    if (!context.contentType || !context.title || !context.category) {
      throw new ContentValidationError(
        'Content type, title, and category are required',
        'content_context',
        context
      );
    }

    if (context.title.length < 5 || context.title.length > 200) {
      throw new ContentValidationError(
        'Content title must be 5-200 characters',
        'title',
        context.title
      );
    }

    if (!Array.isArray(context.tags) || context.tags.length === 0) {
      throw new ContentValidationError('At least one content tag is required', 'tags', context.tags);
    }
  }

  private async enrichRequest(request: OpportunityRequest): Promise<OpportunityRequest> {
    // In a real implementation, this would call various enrichment services
    // For now, we'll add some intelligent defaults
    
    const enriched = { ...request };
    
    // Add audience profile if not provided
    if (!enriched.audience_profile && this.config.environment === 'production') {
      try {
        const profile = await this.getPublisherProfile();
        enriched.audience_profile = profile.audience;
      } catch {
        // Continue without audience profile if fetch fails
      }
    }

    // Enhance targeting based on content
    if (!enriched.targeting.categories) {
      enriched.targeting.categories = this.suggestCategories(request.content_context);
    }

    return enriched;
  }

  private suggestCategories(content: ContentContext): string[] {
    // Simple category suggestion based on content type and tags
    const categoryMap: Record<string, string[]> = {
      'product_review': ['electronics', 'home_garden', 'fashion', 'beauty'],
      'tutorial': ['software', 'diy', 'education', 'tools'],
      'comparison': ['electronics', 'software', 'services', 'finance'],
      'news': ['current_events', 'technology', 'business', 'lifestyle']
    };

    const suggested = categoryMap[content.contentType] || ['general'];
    
    // Add categories based on tags
    content.tags.forEach(tag => {
      const tagLower = tag.toLowerCase();
      if (tagLower.includes('tech')) suggested.push('technology');
      if (tagLower.includes('food')) suggested.push('food_beverage');
      if (tagLower.includes('travel')) suggested.push('travel');
    });

    return [...new Set(suggested)]; // Remove duplicates
  }

  private generateCacheKey(operation: string, data: any): string {
    const hash = crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex');
    return `${this.config.publisherId}:${operation}:${hash.slice(0, 16)}`;
  }

  private sanitizeUpdates(updates: any, allowedFields: string[]): any {
    const sanitized: any = {};
    allowedFields.forEach(field => {
      if (updates[field] !== undefined) {
        sanitized[field] = updates[field];
      }
    });
    return sanitized;
  }

  private recordTelemetry(
    operation: string, 
    duration_ms: number, 
    success: boolean, 
    cache_hit: boolean = false
  ): void {
    if (!this.config.enableTelemetry) return;

    this.telemetryData.push({
      operation,
      duration_ms,
      success,
      cache_hit,
      timestamp: Date.now()
    });

    // Keep only last 1000 entries
    if (this.telemetryData.length > 1000) {
      this.telemetryData = this.telemetryData.slice(-1000);
    }
  }

  private wrapError(error: unknown, operation: string): PublisherSDKError {
    if (error instanceof PublisherSDKError) {
      return error;
    }

    if (error instanceof Error) {
      return new PublisherSDKError(
        `${operation} failed: ${error.message}`,
        'SDK_ERROR',
        undefined,
        false,
        { operation, originalError: error.message }
      );
    }

    return new PublisherSDKError(
      `${operation} failed with unknown error`,
      'UNKNOWN_ERROR',
      undefined,
      false,
      { operation }
    );
  }
}

/**
 * Usage examples:
 * 
 * // Initialize SDK
 * const sdk = new LukhasPublisherSDK({
 *   apiKey: process.env.LUKHAS_PUBLISHER_API_KEY!,
 *   publisherId: 'publisher_123',
 *   environment: 'production',
 *   cacheEnabled: true
 * });
 * 
 * // Request opportunities
 * const opportunities = await sdk.requestOpportunities({
 *   content_context: {
 *     contentType: 'product_review',
 *     title: 'Best Wireless Headphones 2024',
 *     category: 'electronics',
 *     tags: ['headphones', 'audio', 'reviews']
 *   },
 *   placement: {
 *     position: 'in_content',
 *     format: 'product_widget',
 *     max_count: 3
 *   },
 *   targeting: {
 *     categories: ['electronics', 'audio'],
 *     price_range: { min: 50, max: 500, currency: 'USD' }
 *   },
 *   optimization: {
 *     objective: 'revenue',
 *     personalization_level: 'advanced'
 *   }
 * });
 * 
 * // Generate WordPress shortcode
 * const shortcode = sdk.generateWordPressShortcode({
 *   content_context: { ... },
 *   placement: { ... }
 * });
 */

export default LukhasPublisherSDK;