/**
 * LUKHAS Merchant SDK Template
 * Weekend-Ready Integration for E-commerce Platforms
 * 
 * Features:
 * - Opportunity submission and management
 * - Real-time attribution tracking
 * - Payout receipt processing
 * - GDPR/CCPA compliance helpers
 * - Plug-and-play for Shopify, WooCommerce, Magento
 */

class LukhasMerchantSDK {
  constructor(config = {}) {
    this.apiKey = config.apiKey || process.env.LUKHAS_MERCHANT_API_KEY;
    this.baseUrl = config.baseUrl || 'https://api.lukhas.ai/v1';
    this.merchantId = config.merchantId;
    this.sandbox = config.sandbox || false;
    
    if (!this.apiKey || !this.merchantId) {
      throw new Error('API key and merchant ID are required');
    }
    
    this.client = this.createHttpClient();
  }

  createHttpClient() {
    return {
      async post(url, data, headers = {}) {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`,
            'X-Merchant-ID': this.merchantId,
            ...headers
          },
          body: JSON.stringify(data)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        return response.json();
      },

      async get(url, headers = {}) {
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'X-Merchant-ID': this.merchantId,
            ...headers
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        return response.json();
      }
    }.bind(this);
  }

  /**
   * Submit product opportunity to LUKHAS delivery engine
   * Called when products go on sale, restock, or have inventory changes
   */
  async submitOpportunity(product, options = {}) {
    const opportunity = {
      id: `opp_${this.merchantId}_${product.id}_${Date.now()}`,
      domain: this.inferDomain(product.category),
      title: this.formatTitle(product.name, options),
      description: this.formatDescription(product, options),
      price_current: product.price,
      price_alt: product.original_price || product.msrp,
      
      affiliate: {
        merchant: this.merchantId,
        url: this.buildAffiliateUrl(product.id, options.campaignId),
        est_commission_bps: options.commissionBps || 500 // 5% default
      },

      window: {
        start: Date.now(),
        end: Date.now() + (options.windowHours || 24) * 60 * 60 * 1000
      },

      risk: {
        alignment: options.alignment || 0.7,
        stress_block: options.stressBlock || false,
        notes: options.riskNotes
      },

      economics: {
        split_user_bps: options.userSplitBps || 4000, // 40% to user
        split_platform_bps: options.platformSplitBps || 6000, // 60% to platform
        tier: options.tier || 'visitor'
      },

      media: {
        kind: 'image',
        cdn_url: product.image_url,
        alt: product.image_alt || `${product.name} product image`,
        thumbnail_url: product.thumbnail_url
      },

      provenance: {
        sources: [`merchant:${this.merchantId}`, 'product_catalog'],
        version: 'merchant_sdk_1.0.0',
        hash: this.generateHash(product)
      }
    };

    try {
      const response = await this.client.post(`${this.baseUrl}/opportunities`, {
        opportunities: [opportunity],
        merchant_id: this.merchantId,
        campaign_id: options.campaignId
      });

      return {
        success: true,
        opportunity_id: opportunity.id,
        delivery_estimate: response.delivery_estimate,
        attribution_link: response.attribution_link
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        retry_after: this.parseRetryAfter(error)
      };
    }
  }

  /**
   * Track conversion when user completes purchase
   * Essential for attribution and profit sharing
   */
  async trackConversion(opportunityId, purchaseData) {
    const conversion = {
      opportunity_id: opportunityId,
      merchant_id: this.merchantId,
      user_id: purchaseData.userId, // LUKHAS user ID from attribution
      
      purchase: {
        order_id: purchaseData.orderId,
        amount: purchaseData.amount,
        currency: purchaseData.currency || 'USD',
        commission: purchaseData.commission,
        items: purchaseData.items
      },

      attribution: {
        click_time: purchaseData.clickTime,
        purchase_time: Date.now(),
        attribution_model: 'last_click', // or 'multi_touch'
        touch_points: purchaseData.touchPoints || []
      },

      compliance: {
        consent_id: purchaseData.consentId, // Required for GDPR
        privacy_policy_version: purchaseData.privacyVersion,
        data_processing_consent: purchaseData.dataConsent
      }
    };

    try {
      const response = await this.client.post(`${this.baseUrl}/conversions`, conversion);
      
      return {
        success: true,
        conversion_id: response.conversion_id,
        payout_receipt_id: response.payout_receipt_id,
        user_earnings: response.user_earnings,
        merchant_cost: response.merchant_cost
      };
    } catch (error) {
      throw new Error(`Conversion tracking failed: ${error.message}`);
    }
  }

  /**
   * Retrieve payout receipts for transparency and accounting
   */
  async getPayoutReceipts(startDate, endDate) {
    const params = new URLSearchParams({
      merchant_id: this.merchantId,
      start_date: startDate,
      end_date: endDate,
      format: 'detailed'
    });

    try {
      const response = await this.client.get(`${this.baseUrl}/receipts/payout?${params}`);
      return response.receipts;
    } catch (error) {
      throw new Error(`Failed to retrieve payout receipts: ${error.message}`);
    }
  }

  /**
   * Validate user consent for GDPR/CCPA compliance
   */
  async validateConsent(userId, requiredScopes) {
    try {
      const response = await this.client.post(`${this.baseUrl}/consent/validate`, {
        user_id: userId,
        merchant_id: this.merchantId,
        required_scopes: requiredScopes,
        purpose: 'product_recommendation'
      });

      return {
        valid: response.consent_valid,
        expires: response.expires_at,
        scopes: response.granted_scopes,
        consent_id: response.consent_id
      };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  }

  // Helper Methods

  inferDomain(category) {
    const domainMap = {
      'electronics': 'tech.consumer_electronics',
      'clothing': 'fashion.apparel',
      'shoes': 'fashion.footwear',
      'home': 'home.decor',
      'books': 'media.books',
      'pet_supplies': 'retail.pet_food',
      'health': 'health.supplements',
      'beauty': 'beauty.skincare',
      'sports': 'sports.equipment',
      'automotive': 'automotive.parts'
    };

    return domainMap[category] || `retail.${category.replace(/\s+/g, '_')}`;
  }

  formatTitle(productName, options) {
    let title = productName;
    
    if (options.salePrice && options.originalPrice) {
      const discount = Math.round((1 - options.salePrice / options.originalPrice) * 100);
      if (discount >= 20) {
        title += ` - ${discount}% off`;
      }
    }
    
    if (options.inventory === 'low') {
      title += ' - Limited stock';
    }
    
    return title.substring(0, 90); // Max length constraint
  }

  formatDescription(product, options) {
    let desc = product.description || '';
    
    if (options.salePrice && options.originalPrice) {
      desc += ` Now $${options.salePrice} (was $${options.originalPrice}).`;
    }
    
    if (product.rating && product.rating > 4) {
      desc += ` Highly rated: ${product.rating}/5 stars.`;
    }
    
    if (options.freeShipping) {
      desc += ' Free shipping included.';
    }
    
    return desc.substring(0, 300); // Max length constraint
  }

  buildAffiliateUrl(productId, campaignId) {
    const params = new URLSearchParams({
      merchant_id: this.merchantId,
      product_id: productId,
      campaign_id: campaignId || 'default',
      utm_source: 'lukhas',
      utm_medium: 'nias',
      utm_campaign: campaignId || 'auto'
    });

    return `https://${this.merchantId}.com/products/${productId}?${params}`;
  }

  generateHash(product) {
    const hashInput = `${product.id}:${product.name}:${product.price}:${Date.now()}`;
    return 'sha256:' + btoa(hashInput).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  }

  parseRetryAfter(error) {
    // Extract retry-after header from rate limit responses
    if (error.message.includes('Rate limit')) {
      return 60; // Default 60 seconds
    }
    return null;
  }
}

// Platform-Specific Integrations

/**
 * Shopify Integration
 */
class ShopifyLukhasIntegration extends LukhasMerchantSDK {
  constructor(config) {
    super(config);
    this.shopifyDomain = config.shopifyDomain;
    this.accessToken = config.shopifyAccessToken;
  }

  async syncProductCatalog() {
    const products = await this.getShopifyProducts();
    const opportunities = [];

    for (const product of products) {
      if (this.shouldCreateOpportunity(product)) {
        const opportunity = await this.submitOpportunity(
          this.convertShopifyProduct(product),
          { campaignId: 'catalog_sync' }
        );
        opportunities.push(opportunity);
      }
    }

    return opportunities;
  }

  async getShopifyProducts() {
    const response = await fetch(
      `https://${this.shopifyDomain}.myshopify.com/admin/api/2023-10/products.json`,
      {
        headers: {
          'X-Shopify-Access-Token': this.accessToken
        }
      }
    );

    const data = await response.json();
    return data.products;
  }

  convertShopifyProduct(shopifyProduct) {
    const variant = shopifyProduct.variants[0]; // Use first variant
    
    return {
      id: shopifyProduct.id,
      name: shopifyProduct.title,
      description: shopifyProduct.body_html?.replace(/<[^>]*>/g, ''), // Strip HTML
      category: shopifyProduct.product_type || 'general',
      price: parseFloat(variant.price),
      original_price: parseFloat(variant.compare_at_price) || parseFloat(variant.price),
      image_url: shopifyProduct.images[0]?.src,
      inventory: variant.inventory_quantity,
      sku: variant.sku
    };
  }

  shouldCreateOpportunity(product) {
    return product.status === 'active' && 
           product.variants.length > 0 && 
           parseFloat(product.variants[0].price) > 0;
  }
}

/**
 * WooCommerce Integration
 */
class WooCommerceLukhasIntegration extends LukhasMerchantSDK {
  constructor(config) {
    super(config);
    this.wooApiUrl = config.wooApiUrl;
    this.consumerKey = config.wooConsumerKey;
    this.consumerSecret = config.wooConsumerSecret;
  }

  async getWooProducts() {
    const auth = btoa(`${this.consumerKey}:${this.consumerSecret}`);
    const response = await fetch(`${this.wooApiUrl}/wp-json/wc/v3/products`, {
      headers: {
        'Authorization': `Basic ${auth}`
      }
    });

    return response.json();
  }

  convertWooProduct(wooProduct) {
    return {
      id: wooProduct.id,
      name: wooProduct.name,
      description: wooProduct.short_description,
      category: wooProduct.categories[0]?.name || 'general',
      price: parseFloat(wooProduct.price),
      original_price: parseFloat(wooProduct.regular_price),
      image_url: wooProduct.images[0]?.src,
      sku: wooProduct.sku
    };
  }
}

// Usage Examples

/**
 * Basic Usage Example
 */
async function basicExample() {
  const lukhas = new LukhasMerchantSDK({
    apiKey: 'sk_merchant_...',
    merchantId: 'merchant_123',
    sandbox: true
  });

  // Submit a product opportunity
  const result = await lukhas.submitOpportunity({
    id: 'prod_456',
    name: 'Wireless Headphones Pro',
    description: 'Premium noise-cancelling headphones',
    category: 'electronics',
    price: 199.99,
    original_price: 299.99,
    image_url: 'https://example.com/headphones.jpg'
  }, {
    campaignId: 'black_friday',
    commissionBps: 800, // 8% commission
    windowHours: 48,
    alignment: 0.9
  });

  if (result.success) {
    console.log('Opportunity submitted:', result.opportunity_id);
    
    // Track conversion when user purchases
    await lukhas.trackConversion(result.opportunity_id, {
      orderId: 'order_789',
      userId: 'lukhas_user_123',
      amount: 199.99,
      commission: 15.99,
      clickTime: Date.now() - 3600000, // 1 hour ago
      consentId: 'consent_abc123'
    });
  }
}

/**
 * Shopify Integration Example
 */
async function shopifyExample() {
  const shopifyLukhas = new ShopifyLukhasIntegration({
    apiKey: 'sk_merchant_...',
    merchantId: 'shopify_store_123',
    shopifyDomain: 'my-store',
    shopifyAccessToken: 'shpat_...'
  });

  // Sync entire product catalog
  const opportunities = await shopifyLukhas.syncProductCatalog();
  console.log(`Created ${opportunities.length} opportunities`);
}

/**
 * Compliance Check Example
 */
async function complianceExample() {
  const lukhas = new LukhasMerchantSDK({
    apiKey: 'sk_merchant_...',
    merchantId: 'merchant_123'
  });

  // Validate user consent before showing recommendations
  const consent = await lukhas.validateConsent('lukhas_user_456', [
    'purchase_history.read',
    'product_recommendations.receive'
  ]);

  if (consent.valid) {
    // Proceed with opportunity submission
    console.log('User consent valid until:', consent.expires);
  } else {
    console.log('Cannot show recommendations without consent');
  }
}

module.exports = {
  LukhasMerchantSDK,
  ShopifyLukhasIntegration,
  WooCommerceLukhasIntegration
};