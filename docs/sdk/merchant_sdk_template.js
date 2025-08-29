/**
 * LUKHAS Merchant SDK - Production Template
 * Ready-to-ship merchant integration for weekend deployment
 */

class LukhasMerchantSDK {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.merchantId = config.merchantId;
    this.baseURL = config.baseURL || 'https://api.lukhas.ai/v1';
    this.environment = config.environment || 'production';
    
    // Validate required config
    if (!this.apiKey || !this.merchantId) {
      throw new Error('apiKey and merchantId are required');
    }
    
    // Rate limiting
    this.requestQueue = [];
    this.rateLimitRpm = 1000;
    this.lastRequestTime = 0;
  }

  /**
   * Submit product opportunity to LUKHAS marketplace
   * @param {Object} product - Product details
   * @param {Object} campaign - Campaign configuration
   * @returns {Promise<Object>} Submission result
   */
  async submitOpportunity(product, campaign = {}) {
    const opportunity = {
      id: this._generateOpportunityId(),
      merchant_id: this.merchantId,
      domain: product.category || 'general',
      title: product.title,
      description: product.description,
      
      // Media
      media: {
        image_url: product.image_url,
        thumbnail_url: product.thumbnail_url,
        video_url: product.video_url
      },
      
      // Commercial terms
      economics: {
        base_price_usd: product.price,
        commission_bps: campaign.commissionBps || 500, // 5% default
        currency: product.currency || 'USD',
        affiliate_link: product.affiliate_link || this._generateAffiliateLink(product.id)
      },
      
      // Targeting
      window: {
        start_date: campaign.startDate || new Date().toISOString(),
        end_date: campaign.endDate || this._getDefaultEndDate(),
        geo_targets: campaign.geoTargets || ['US', 'CA', 'UK'],
        audience_segments: campaign.audienceSegments || []
      },
      
      // Risk assessment
      risk: {
        alignment: campaign.expectedAlignment || 0.7,
        stress_block: campaign.stressSensitive || false,
        safety_category: this._categorizeProduct(product)
      },
      
      // Tracking
      provenance: {
        source: 'merchant_sdk',
        campaign_id: campaign.campaignId,
        submitted_at: new Date().toISOString(),
        version: '1.0.0'
      }
    };

    return await this._apiCall('POST', '/opportunities', opportunity);
  }

  /**
   * Update existing opportunity
   * @param {string} opportunityId 
   * @param {Object} updates 
   * @returns {Promise<Object>}
   */
  async updateOpportunity(opportunityId, updates) {
    const allowedFields = [
      'title', 'description', 'media', 'economics', 'window', 'risk'
    ];
    
    const sanitizedUpdates = {};
    for (const field of allowedFields) {
      if (updates[field] !== undefined) {
        sanitizedUpdates[field] = updates[field];
      }
    }
    
    sanitizedUpdates.updated_at = new Date().toISOString();
    
    return await this._apiCall(
      'PATCH', 
      `/opportunities/${opportunityId}`, 
      sanitizedUpdates
    );
  }

  /**
   * Get opportunity performance metrics
   * @param {string} opportunityId 
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Performance data
   */
  async getOpportunityMetrics(opportunityId, options = {}) {
    const params = new URLSearchParams({
      start_date: options.startDate || this._getLastWeek(),
      end_date: options.endDate || new Date().toISOString(),
      metrics: options.metrics?.join(',') || 'impressions,clicks,conversions,revenue'
    });

    return await this._apiCall(
      'GET', 
      `/opportunities/${opportunityId}/metrics?${params}`
    );
  }

  /**
   * Bulk upload opportunities from catalog
   * @param {Array} products - Array of product objects
   * @param {Object} defaultCampaign - Default campaign settings
   * @returns {Promise<Object>} Bulk upload results
   */
  async bulkUploadCatalog(products, defaultCampaign = {}) {
    const opportunities = products.map(product => ({
      ...this._productToOpportunity(product, defaultCampaign),
      batch_id: this._generateBatchId()
    }));

    // Split into batches of 100
    const batches = this._chunkArray(opportunities, 100);
    const results = [];

    for (const batch of batches) {
      try {
        const result = await this._apiCall('POST', '/opportunities/bulk', {
          opportunities: batch,
          merchant_id: this.merchantId
        });
        results.push(result);
      } catch (error) {
        results.push({ error: error.message, batch_size: batch.length });
      }
    }

    return {
      total_products: products.length,
      successful_batches: results.filter(r => !r.error).length,
      failed_batches: results.filter(r => r.error).length,
      results
    };
  }

  /**
   * Get merchant dashboard summary
   * @returns {Promise<Object>} Dashboard data
   */
  async getDashboard() {
    return await this._apiCall('GET', `/merchants/${this.merchantId}/dashboard`);
  }

  /**
   * Configure S2S postback webhook
   * @param {Object} webhookConfig 
   * @returns {Promise<Object>}
   */
  async configureWebhook(webhookConfig) {
    const config = {
      url: webhookConfig.url,
      events: webhookConfig.events || ['conversion', 'payout'],
      secret: webhookConfig.secret || this._generateWebhookSecret(),
      retry_policy: {
        max_retries: 3,
        backoff_multiplier: 2,
        timeout_seconds: 30
      }
    };

    return await this._apiCall(
      'POST', 
      `/merchants/${this.merchantId}/webhooks`, 
      config
    );
  }

  // Private helper methods

  async _apiCall(method, endpoint, data = null) {
    await this._rateLimitCheck();

    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': `LukhasMerchantSDK/1.0.0`,
      'X-Merchant-ID': this.merchantId
    };

    const options = {
      method,
      headers
    };

    if (data && (method === 'POST' || method === 'PATCH' || method === 'PUT')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'API error' }));
        throw new Error(`API Error ${response.status}: ${error.message}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(`SDK Error: ${error.message}`);
    }
  }

  async _rateLimitCheck() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    const minInterval = 60000 / this.rateLimitRpm; // Convert RPM to ms interval

    if (timeSinceLastRequest < minInterval) {
      await new Promise(resolve => 
        setTimeout(resolve, minInterval - timeSinceLastRequest)
      );
    }

    this.lastRequestTime = Date.now();
  }

  _generateOpportunityId() {
    return `opp_${this.merchantId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  _generateAffiliateLink(productId) {
    const params = new URLSearchParams({
      merchant: this.merchantId,
      product: productId,
      utm_source: 'lukhas',
      utm_medium: 'affiliate',
      utm_campaign: 'lukhas_marketplace'
    });
    
    return `https://track.lukhas.ai/aff?${params}`;
  }

  _generateBatchId() {
    return `batch_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
  }

  _generateWebhookSecret() {
    return 'whk_' + Array(32).fill(0).map(() => 
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
  }

  _getDefaultEndDate() {
    const date = new Date();
    date.setMonth(date.getMonth() + 3); // 3 months default
    return date.toISOString();
  }

  _getLastWeek() {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString();
  }

  _categorizeProduct(product) {
    const sensitiveCategories = ['health', 'finance', 'insurance', 'legal'];
    const category = product.category?.toLowerCase() || '';
    
    return sensitiveCategories.includes(category) ? 'sensitive' : 'standard';
  }

  _productToOpportunity(product, campaign) {
    // Convert product object to opportunity format
    return {
      id: this._generateOpportunityId(),
      merchant_id: this.merchantId,
      domain: product.category || 'general',
      title: product.title || product.name,
      description: product.description,
      media: {
        image_url: product.image_url || product.image,
        thumbnail_url: product.thumbnail_url
      },
      economics: {
        base_price_usd: product.price,
        commission_bps: campaign.commissionBps || 500,
        currency: product.currency || 'USD',
        affiliate_link: product.affiliate_link || this._generateAffiliateLink(product.id)
      },
      window: {
        start_date: campaign.startDate || new Date().toISOString(),
        end_date: campaign.endDate || this._getDefaultEndDate(),
        geo_targets: campaign.geoTargets || ['US']
      },
      risk: {
        alignment: campaign.expectedAlignment || 0.7,
        safety_category: this._categorizeProduct(product)
      },
      provenance: {
        source: 'bulk_upload',
        submitted_at: new Date().toISOString()
      }
    };
  }

  _chunkArray(array, chunkSize) {
    const chunks = [];
    for (let i = 0; i < array.length; i += chunkSize) {
      chunks.push(array.slice(i, i + chunkSize));
    }
    return chunks;
  }
}

// Usage examples
const examples = {
  
  // Basic initialization
  initialization: () => {
    const sdk = new LukhasMerchantSDK({
      apiKey: 'sk_merchant_live_abc123...',
      merchantId: 'merchant_456',
      environment: 'production'
    });
  },

  // Submit single product
  singleProduct: async (sdk) => {
    const product = {
      id: 'prod_123',
      title: 'Premium Wireless Headphones',
      description: 'Noise-canceling Bluetooth headphones with 30-hour battery',
      price: 299.99,
      category: 'electronics',
      image_url: 'https://example.com/headphones.jpg',
      affiliate_link: 'https://store.example.com/products/headphones?ref=merchant456'
    };

    const campaign = {
      campaignId: 'summer_sale_2024',
      commissionBps: 800, // 8% commission
      geoTargets: ['US', 'CA', 'UK'],
      expectedAlignment: 0.8
    };

    const result = await sdk.submitOpportunity(product, campaign);
    console.log('Opportunity submitted:', result.opportunity_id);
  },

  // Bulk catalog upload
  bulkUpload: async (sdk) => {
    const products = [
      { id: 'prod_1', title: 'Product 1', price: 99.99 },
      { id: 'prod_2', title: 'Product 2', price: 149.99 },
      // ... more products
    ];

    const result = await sdk.bulkUploadCatalog(products, {
      commissionBps: 600,
      geoTargets: ['US', 'CA']
    });

    console.log(`Uploaded ${result.total_products} products in ${result.successful_batches} batches`);
  },

  // Setup webhook for conversion tracking
  webhook: async (sdk) => {
    const webhookConfig = {
      url: 'https://api.mystore.com/lukhas/webhook',
      events: ['conversion', 'payout'],
      secret: 'my_webhook_secret_key'
    };

    const webhook = await sdk.configureWebhook(webhookConfig);
    console.log('Webhook configured:', webhook.webhook_id);
  },

  // Get performance metrics
  metrics: async (sdk) => {
    const opportunityId = 'opp_merchant_456_1234567890_abc123def';
    const metrics = await sdk.getOpportunityMetrics(opportunityId, {
      startDate: '2024-01-01T00:00:00Z',
      endDate: '2024-01-31T23:59:59Z',
      metrics: ['impressions', 'clicks', 'conversions', 'revenue']
    });

    console.log('Performance:', {
      impressions: metrics.impressions,
      ctr: metrics.clicks / metrics.impressions,
      conversion_rate: metrics.conversions / metrics.clicks,
      revenue: metrics.revenue
    });
  }
};

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { LukhasMerchantSDK, examples };
} else if (typeof window !== 'undefined') {
  window.LukhasMerchantSDK = LukhasMerchantSDK;
}

// TypeScript definitions (for reference)
const typeDefinitions = `
interface MerchantSDKConfig {
  apiKey: string;
  merchantId: string;
  baseURL?: string;
  environment?: 'production' | 'staging' | 'development';
}

interface Product {
  id: string;
  title: string;
  description: string;
  price: number;
  category?: string;
  image_url?: string;
  thumbnail_url?: string;
  video_url?: string;
  affiliate_link?: string;
  currency?: string;
}

interface Campaign {
  campaignId?: string;
  commissionBps?: number;
  startDate?: string;
  endDate?: string;
  geoTargets?: string[];
  audienceSegments?: string[];
  expectedAlignment?: number;
  stressSensitive?: boolean;
}

interface OpportunityMetrics {
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  ctr: number;
  conversion_rate: number;
}
`;

export { LukhasMerchantSDK, examples, typeDefinitions };