/**
 * LUKHAS Publisher SDK - Production Template
 * Ready-to-ship publisher integration for weekend deployment
 */

class LukhasPublisherSDK {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.publisherId = config.publisherId;
    this.baseURL = config.baseURL || 'https://api.lukhas.ai/v1';
    this.environment = config.environment || 'production';
    
    // Validate required config
    if (!this.apiKey || !this.publisherId) {
      throw new Error('apiKey and publisherId are required');
    }
    
    // ABAS gate integration
    this.abasEnabled = config.abasEnabled !== false; // Default true
    this.userStateProvider = config.userStateProvider || this._defaultUserState;
    
    // Performance tracking
    this.metrics = {
      requests: 0,
      rendered: 0,
      blocked: 0,
      conversions: 0
    };
  }

  /**
   * Request contextual opportunities for content
   * @param {Object} context - Content and audience context
   * @returns {Promise<Array>} Filtered opportunities
   */
  async requestOpportunities(context) {
    this.metrics.requests++;
    
    // Build request payload
    const request = {
      publisher_id: this.publisherId,
      context: {
        content_type: context.contentType || 'article',
        category: context.category,
        tags: context.tags || [],
        audience_size: context.audienceSize,
        geo_location: context.geoLocation || await this._detectGeoLocation(),
        language: context.language || 'en',
        device_type: this._detectDeviceType(),
        referrer: context.referrer || document?.referrer
      },
      preferences: {
        max_opportunities: context.maxOpportunities || 3,
        min_alignment: context.minAlignment || 0.6,
        excluded_domains: context.excludedDomains || [],
        preferred_formats: context.preferredFormats || ['display', 'native']
      },
      timestamp: new Date().toISOString()
    };

    try {
      // Get opportunities from LUKHAS
      const response = await this._apiCall('POST', '/publishers/opportunities', request);
      const opportunities = response.opportunities || [];
      
      // Apply ABAS filtering if enabled
      if (this.abasEnabled) {
        const userState = await this.userStateProvider();
        const filteredOps = await this._applyAbasFilter(opportunities, userState);
        this.metrics.blocked += (opportunities.length - filteredOps.length);
        return filteredOps;
      }
      
      return opportunities;
      
    } catch (error) {
      console.error('LUKHAS Publisher SDK Error:', error.message);
      return []; // Graceful fallback
    }
  }

  /**
   * Render opportunity as HTML element
   * @param {Object} opportunity 
   * @param {Object} options - Rendering options
   * @returns {HTMLElement} Rendered ad element
   */
  renderOpportunity(opportunity, options = {}) {
    this.metrics.rendered++;
    
    const container = document.createElement('div');
    container.className = `lukhas-opportunity ${options.className || ''}`;
    container.setAttribute('data-opportunity-id', opportunity.id);
    container.setAttribute('data-publisher-id', this.publisherId);
    
    // Add tracking attributes
    container.addEventListener('click', () => this._trackClick(opportunity));
    container.addEventListener('mouseenter', () => this._trackImpression(opportunity));
    
    // Render based on format
    switch (opportunity.format || 'display') {
      case 'native':
        this._renderNativeAd(container, opportunity, options);
        break;
      case 'display':
        this._renderDisplayAd(container, opportunity, options);
        break;
      case 'text':
        this._renderTextAd(container, opportunity, options);
        break;
      default:
        this._renderDisplayAd(container, opportunity, options);
    }
    
    return container;
  }

  /**
   * Auto-inject opportunities into content
   * @param {Object} config - Auto-injection configuration
   */
  async autoInject(config = {}) {
    const context = await this._extractPageContext();
    const opportunities = await this.requestOpportunities(context);
    
    if (opportunities.length === 0) return;
    
    const selectors = config.selectors || [
      'article p:nth-child(3)', // After 3rd paragraph
      '.content p:nth-child(5)', // After 5th paragraph in .content
      'main section:last-child'  // End of main content
    ];
    
    for (let i = 0; i < Math.min(opportunities.length, selectors.length); i++) {
      const element = document.querySelector(selectors[i]);
      if (element) {
        const adElement = this.renderOpportunity(opportunities[i], {
          className: 'lukhas-auto-inject',
          style: config.style || 'margin: 20px 0; padding: 15px; border: 1px solid #e0e0e0;'
        });
        
        // Insert after target element
        element.parentNode.insertBefore(adElement, element.nextSibling);
      }
    }
  }

  /**
   * Track conversion event
   * @param {Object} conversionData 
   */
  async trackConversion(conversionData) {
    this.metrics.conversions++;
    
    const payload = {
      publisher_id: this.publisherId,
      opportunity_id: conversionData.opportunityId,
      conversion_type: conversionData.type || 'click',
      value_usd: conversionData.valueUsd || 0,
      metadata: {
        page_url: window.location.href,
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        ...conversionData.metadata
      }
    };
    
    return await this._apiCall('POST', '/publishers/conversions', payload);
  }

  /**
   * Get publisher performance metrics
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Performance data
   */
  async getMetrics(options = {}) {
    const params = new URLSearchParams({
      start_date: options.startDate || this._getLastWeek(),
      end_date: options.endDate || new Date().toISOString(),
      granularity: options.granularity || 'day'
    });

    const response = await this._apiCall(
      'GET', 
      `/publishers/${this.publisherId}/metrics?${params}`
    );
    
    return {
      ...response,
      client_metrics: this.metrics
    };
  }

  /**
   * Configure content matching preferences
   * @param {Object} preferences 
   */
  async updatePreferences(preferences) {
    const config = {
      content_categories: preferences.categories || [],
      blocked_merchants: preferences.blockedMerchants || [],
      min_commission_bps: preferences.minCommissionBps || 300,
      audience_segments: preferences.audienceSegments || [],
      geographic_targets: preferences.geoTargets || [],
      content_safety_level: preferences.safetyLevel || 'moderate'
    };

    return await this._apiCall(
      'PUT', 
      `/publishers/${this.publisherId}/preferences`, 
      config
    );
  }

  // Private helper methods

  async _applyAbasFilter(opportunities, userState) {
    const filtered = [];
    
    for (const opportunity of opportunities) {
      // Simple ABAS gate check (client-side version)
      const gateDecision = this._checkAbasGate(userState, opportunity);
      
      if (gateDecision.approved) {
        filtered.push({
          ...opportunity,
          abas_confidence: gateDecision.confidence
        });
      } else {
        console.log(`ABAS blocked opportunity: ${gateDecision.reason}`);
      }
    }
    
    return filtered;
  }

  _checkAbasGate(userState, opportunity) {
    // Client-side ABAS gate (simplified version of server implementation)
    
    // Safety block - absolute priority
    if (userState.driving) {
      return { approved: false, reason: 'safety_block', confidence: 1.0 };
    }
    
    // Stress protection
    if ((userState.stress || 0) > 0.8) {
      return { approved: false, reason: 'stress_block', confidence: 0.9 };
    }
    
    // Flow state protection
    if (userState.flowState) {
      return { approved: false, reason: 'flow_protection', confidence: 0.95 };
    }
    
    // Deep focus protection
    if ((userState.focusLevel || 0) > 0.8) {
      return { approved: false, reason: 'deep_focus', confidence: 0.8 };
    }
    
    // Quiet hours protection
    if (userState.hour !== undefined) {
      const isQuietHours = (userState.hour >= 22 || userState.hour < 7);
      if (isQuietHours) {
        return { approved: false, reason: 'quiet_hours', confidence: 0.7 };
      }
    }
    
    // Low alignment protection
    const alignment = opportunity.risk?.alignment || 0.5;
    if (alignment < 0.3) {
      return { approved: false, reason: 'low_alignment', confidence: 0.6 };
    }
    
    // Stress-sensitive opportunities
    if (opportunity.risk?.stressBlock && (userState.stress || 0) > 0.5) {
      return { approved: false, reason: 'stress_sensitive', confidence: 0.7 };
    }
    
    // Calculate approval confidence
    const stressFactor = 1.0 - (userState.stress || 0) * 0.5;
    const alignmentFactor = Math.min(alignment * 1.2, 1.0);
    const timingFactor = (userState.hour >= 9 && userState.hour <= 21) ? 0.9 : 0.6;
    const confidence = (stressFactor + alignmentFactor + timingFactor) / 3;
    
    return { approved: true, reason: null, confidence };
  }

  _renderNativeAd(container, opportunity, options) {
    const nativeHTML = `
      <div class="lukhas-native-ad">
        <div class="lukhas-ad-label">Sponsored</div>
        <div class="lukhas-ad-content">
          <img src="${opportunity.media?.thumbnail_url || opportunity.media?.image_url}" 
               alt="${opportunity.title}" class="lukhas-ad-image" />
          <div class="lukhas-ad-text">
            <h4 class="lukhas-ad-title">${this._escapeHtml(opportunity.title)}</h4>
            <p class="lukhas-ad-description">${this._escapeHtml(opportunity.description || '')}</p>
            <span class="lukhas-ad-price">$${opportunity.economics?.base_price_usd || ''}</span>
          </div>
        </div>
      </div>
    `;
    
    container.innerHTML = nativeHTML;
    container.onclick = () => this._handleClick(opportunity);
  }

  _renderDisplayAd(container, opportunity, options) {
    const displayHTML = `
      <div class="lukhas-display-ad">
        <div class="lukhas-ad-label">Ad</div>
        <img src="${opportunity.media?.image_url}" alt="${opportunity.title}" style="max-width: 100%;" />
        <div class="lukhas-ad-overlay">
          <h4>${this._escapeHtml(opportunity.title)}</h4>
          <button class="lukhas-cta-button">Learn More</button>
        </div>
      </div>
    `;
    
    container.innerHTML = displayHTML;
    container.onclick = () => this._handleClick(opportunity);
  }

  _renderTextAd(container, opportunity, options) {
    const textHTML = `
      <div class="lukhas-text-ad">
        <span class="lukhas-ad-label">Sponsored</span>
        <h4 class="lukhas-ad-title">${this._escapeHtml(opportunity.title)}</h4>
        <p class="lukhas-ad-description">${this._escapeHtml(opportunity.description || '')}</p>
      </div>
    `;
    
    container.innerHTML = textHTML;
    container.onclick = () => this._handleClick(opportunity);
  }

  async _handleClick(opportunity) {
    // Track click
    await this.trackConversion({
      opportunityId: opportunity.id,
      type: 'click'
    });
    
    // Open affiliate link
    const affiliateUrl = opportunity.economics?.affiliate_link;
    if (affiliateUrl) {
      window.open(affiliateUrl, '_blank');
    }
  }

  async _trackClick(opportunity) {
    await this.trackConversion({
      opportunityId: opportunity.id,
      type: 'click'
    });
  }

  async _trackImpression(opportunity) {
    await this.trackConversion({
      opportunityId: opportunity.id,
      type: 'impression'
    });
  }

  async _extractPageContext() {
    // Extract context from current page
    const meta = {
      title: document.title,
      description: document.querySelector('meta[name="description"]')?.content || '',
      keywords: document.querySelector('meta[name="keywords"]')?.content || '',
      category: this._detectCategory(),
      contentType: this._detectContentType()
    };
    
    return {
      contentType: meta.contentType,
      category: meta.category,
      tags: meta.keywords.split(',').map(k => k.trim()).filter(Boolean),
      audienceSize: await this._estimateAudienceSize(),
      geoLocation: await this._detectGeoLocation()
    };
  }

  _detectCategory() {
    // Simple category detection based on URL and content
    const url = window.location.pathname.toLowerCase();
    const categories = {
      tech: ['tech', 'technology', 'gadget', 'software'],
      fashion: ['fashion', 'style', 'clothing', 'apparel'],
      health: ['health', 'fitness', 'wellness', 'medical'],
      travel: ['travel', 'vacation', 'trip', 'hotel'],
      food: ['food', 'recipe', 'cooking', 'restaurant']
    };
    
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => url.includes(keyword))) {
        return category;
      }
    }
    
    return 'general';
  }

  _detectContentType() {
    // Detect content type based on page structure
    if (document.querySelector('article')) return 'article';
    if (document.querySelector('.product, .product-page')) return 'product';
    if (document.querySelector('.blog, .post')) return 'blog';
    if (document.querySelector('video, .video')) return 'video';
    return 'page';
  }

  _detectDeviceType() {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }

  async _detectGeoLocation() {
    // Simple geo detection (in production, use IP geolocation service)
    try {
      const response = await fetch('https://ipapi.co/country_code/');
      return await response.text();
    } catch {
      return 'US'; // Default fallback
    }
  }

  async _estimateAudienceSize() {
    // Estimate based on page views, social shares, etc.
    // This is a simplified implementation
    const views = parseInt(document.querySelector('.view-count')?.textContent || '1000');
    return Math.max(views, 1000);
  }

  _defaultUserState() {
    // Default user state provider
    const hour = new Date().getHours();
    const stress = Math.random() * 0.4; // Random baseline stress
    
    return {
      hour,
      stress,
      driving: false, // Would integrate with navigation APIs
      flowState: false,
      focusLevel: Math.random() * 0.6
    };
  }

  async _apiCall(method, endpoint, data = null) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': 'LukhasPublisherSDK/1.0.0',
      'X-Publisher-ID': this.publisherId
    };

    const options = { method, headers };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'API error' }));
      throw new Error(`API Error ${response.status}: ${error.message}`);
    }

    return await response.json();
  }

  _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  _getLastWeek() {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString();
  }
}

// Usage examples
const examples = {
  
  // Basic initialization
  initialization: () => {
    const sdk = new LukhasPublisherSDK({
      apiKey: 'sk_publisher_live_xyz789...',
      publisherId: 'pub_123',
      abasEnabled: true
    });
  },

  // Manual opportunity request
  manualRequest: async (sdk) => {
    const opportunities = await sdk.requestOpportunities({
      contentType: 'article',
      category: 'technology',
      tags: ['smartphones', 'reviews'],
      audienceSize: 50000,
      maxOpportunities: 3,
      minAlignment: 0.7
    });

    // Render first opportunity
    if (opportunities.length > 0) {
      const adElement = sdk.renderOpportunity(opportunities[0], {
        className: 'my-ad-style'
      });
      document.getElementById('ad-container').appendChild(adElement);
    }
  },

  // Auto-injection setup
  autoInjection: async (sdk) => {
    await sdk.autoInject({
      selectors: [
        'article p:nth-child(3)',
        'article p:nth-child(7)',
        '.content .section:last-child'
      ],
      style: 'margin: 30px 0; padding: 20px; background: #f9f9f9; border-radius: 8px;'
    });
  },

  // Performance tracking
  performanceTracking: async (sdk) => {
    // Track custom conversion
    await sdk.trackConversion({
      opportunityId: 'opp_123_456',
      type: 'purchase',
      valueUsd: 99.99,
      metadata: {
        product_id: 'prod_789',
        category: 'electronics'
      }
    });

    // Get metrics
    const metrics = await sdk.getMetrics({
      startDate: '2024-01-01T00:00:00Z',
      endDate: '2024-01-31T23:59:59Z'
    });

    console.log('Publisher Performance:', {
      impressions: metrics.impressions,
      clicks: metrics.clicks,
      conversions: metrics.conversions,
      revenue: metrics.revenue_usd,
      ctr: metrics.clicks / metrics.impressions,
      conversion_rate: metrics.conversions / metrics.clicks
    });
  },

  // WordPress integration
  wordPressIntegration: (sdk) => {
    // WordPress shortcode: [lukhas_ad category="tech" max="2"]
    function lukhasAdShortcode(atts) {
      const attributes = {
        category: atts.category || 'general',
        max: parseInt(atts.max) || 1,
        alignment: parseFloat(atts.alignment) || 0.6
      };

      const containerId = 'lukhas-wp-' + Math.random().toString(36).substr(2, 9);
      
      // Return placeholder div
      setTimeout(async () => {
        const opportunities = await sdk.requestOpportunities({
          category: attributes.category,
          maxOpportunities: attributes.max,
          minAlignment: attributes.alignment
        });

        const container = document.getElementById(containerId);
        if (container && opportunities.length > 0) {
          opportunities.forEach(opp => {
            const adElement = sdk.renderOpportunity(opp, {
              className: 'lukhas-wp-ad'
            });
            container.appendChild(adElement);
          });
        }
      }, 100);

      return `<div id="${containerId}" class="lukhas-wp-container"></div>`;
    }
  }
};

// CSS styles for rendered ads
const defaultCSS = `
.lukhas-opportunity {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.lukhas-opportunity:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.lukhas-ad-label {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.lukhas-native-ad {
  background: white;
  padding: 16px;
}

.lukhas-ad-content {
  display: flex;
  gap: 12px;
}

.lukhas-ad-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}

.lukhas-ad-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px 0;
  color: #333;
}

.lukhas-ad-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.lukhas-ad-price {
  font-size: 14px;
  font-weight: 600;
  color: #007cba;
}

.lukhas-display-ad {
  position: relative;
  background: white;
}

.lukhas-ad-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  color: white;
  padding: 20px;
}

.lukhas-cta-button {
  background: #007cba;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
}

.lukhas-text-ad {
  background: white;
  padding: 16px;
  border-left: 4px solid #007cba;
}

.lukhas-auto-inject {
  border: 1px solid #e0e0e0;
  margin: 20px 0;
}

.lukhas-wp-container {
  margin: 20px 0;
}
`;

// Inject default styles
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = defaultCSS;
  document.head.appendChild(style);
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { LukhasPublisherSDK, examples };
} else if (typeof window !== 'undefined') {
  window.LukhasPublisherSDK = LukhasPublisherSDK;
}

export { LukhasPublisherSDK, examples };