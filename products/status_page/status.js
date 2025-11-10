/**
 * LUKHAS AI Status Page - Real-time Prometheus Metrics
 *
 * Fetches metrics from Prometheus and updates the status page in real-time.
 * Supports both production (Prometheus) and development (mock data) modes.
 */

const CONFIG = {
    prometheusUrl: process.env.PROMETHEUS_URL || 'http://localhost:9090',
    refreshInterval: 30000, // 30 seconds
    mockMode: true  // Set to false in production with real Prometheus
};

// Mock data for development/testing
const MOCK_DATA = {
    api_uptime: 99.99,
    api_p95_latency: 45,
    db_status: 'Healthy',
    cache_hit_rate: 87.5,
    matriz_uptime: 99.95,
    matriz_p95_latency: 120,
    dream_uptime: 99.98,
    dream_p95_latency: 230,
    identity_uptime: 99.97,
    identity_p95_latency: 35,
    overall_status: 'healthy'
};

/**
 * Fetch a Prometheus metric
 * @param {string} query - PromQL query
 * @returns {Promise<number|string>}
 */
async function fetchMetric(query) {
    if (CONFIG.mockMode) {
        return getMockMetric(query);
    }

    try {
        const encodedQuery = encodeURIComponent(query);
        const url = `${CONFIG.prometheusUrl}/api/v1/query?query=${encodedQuery}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            console.error(`Prometheus query failed: ${response.status}`);
            return null;
        }

        const data = await response.json();

        if (data.status !== 'success' || !data.data.result.length) {
            console.warn(`No data for query: ${query}`);
            return null;
        }

        return data.data.result[0].value[1];
    } catch (error) {
        console.error('Error fetching metric:', error);
        return null;
    }
}

/**
 * Get mock metric data for development
 * @param {string} query - PromQL query (used to determine which mock value to return)
 * @returns {number|string}
 */
function getMockMetric(query) {
    // Simple query pattern matching for mock data
    if (query.includes('up{job="api"}')) return MOCK_DATA.api_uptime;
    if (query.includes('http_request_duration_p95{service="api"}')) return MOCK_DATA.api_p95_latency;
    if (query.includes('postgres_health')) return MOCK_DATA.db_status;
    if (query.includes('redis_hit_rate')) return MOCK_DATA.cache_hit_rate;
    if (query.includes('up{job="matriz"}')) return MOCK_DATA.matriz_uptime;
    if (query.includes('http_request_duration_p95{service="matriz"}')) return MOCK_DATA.matriz_p95_latency;
    if (query.includes('up{job="dream"}')) return MOCK_DATA.dream_uptime;
    if (query.includes('http_request_duration_p95{service="dream"}')) return MOCK_DATA.dream_p95_latency;
    if (query.includes('up{job="identity"}')) return MOCK_DATA.identity_uptime;
    if (query.includes('http_request_duration_p95{service="identity"}')) return MOCK_DATA.identity_p95_latency;

    return 0;
}

/**
 * Update service status indicators
 * @param {string} serviceId - Service identifier
 * @param {string} status - 'healthy', 'degraded', or 'down'
 */
function updateServiceStatus(serviceId, status) {
    const card = document.querySelector(`[data-service="${serviceId}"]`);
    if (!card) return;

    const indicator = card.querySelector('.status-indicator');
    if (!indicator) return;

    // Remove all status classes
    indicator.classList.remove('status-healthy', 'status-degraded', 'status-down');

    // Add new status class
    indicator.classList.add(`status-${status}`);
}

/**
 * Update a metric value in the UI
 * @param {string} elementId - Element ID to update
 * @param {string|number} value - New value
 */
function updateMetricValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Determine service health status based on uptime
 * @param {number} uptime - Uptime percentage
 * @returns {string} - 'healthy', 'degraded', or 'down'
 */
function getHealthStatus(uptime) {
    if (uptime >= 99.5) return 'healthy';
    if (uptime >= 95.0) return 'degraded';
    return 'down';
}

/**
 * Update overall system status
 * @param {Array<string>} serviceStatuses - Array of service status strings
 */
function updateOverallStatus(serviceStatuses) {
    const overallStatusEl = document.getElementById('overall-status');
    if (!overallStatusEl) return;

    const indicator = overallStatusEl.querySelector('.status-indicator');
    const text = overallStatusEl.querySelector('span:last-child');

    if (!indicator || !text) return;

    // Determine overall status
    let overallStatus = 'healthy';
    let statusText = 'All Systems Operational';

    if (serviceStatuses.includes('down')) {
        overallStatus = 'down';
        statusText = 'System Outage';
    } else if (serviceStatuses.includes('degraded')) {
        overallStatus = 'degraded';
        statusText = 'Partial Service Degradation';
    }

    // Update indicator
    indicator.classList.remove('status-healthy', 'status-degraded', 'status-down');
    indicator.classList.add(`status-${overallStatus}`);

    // Update text
    text.textContent = statusText;
}

/**
 * Fetch and update all metrics
 */
async function updateAllMetrics() {
    try {
        // API Server metrics
        const apiUptime = await fetchMetric('avg_over_time(up{job="api"}[24h]) * 100');
        const apiP95 = await fetchMetric('histogram_quantile(0.95, http_request_duration_seconds_bucket{service="api"})');

        if (apiUptime !== null) {
            updateMetricValue('api-uptime', `${apiUptime.toFixed(2)}%`);
            updateServiceStatus('api', getHealthStatus(apiUptime));
        }

        if (apiP95 !== null) {
            updateMetricValue('api-p95', `${Math.round(apiP95)}ms`);
        }

        // Database metrics
        const dbStatus = await fetchMetric('postgres_health{instance="primary"}');
        if (dbStatus !== null) {
            const dbHealthy = dbStatus === 'Healthy' || dbStatus === 1;
            updateMetricValue('db-status', dbHealthy ? 'Healthy' : 'Degraded');
            updateServiceStatus('database', dbHealthy ? 'healthy' : 'degraded');
        }

        // Cache metrics
        const cacheHitRate = await fetchMetric('rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100');
        if (cacheHitRate !== null) {
            updateMetricValue('cache-hit-rate', `${cacheHitRate.toFixed(1)}%`);
            updateServiceStatus('cache', cacheHitRate >= 70 ? 'healthy' : 'degraded');
        }

        // MATRIZ metrics
        const matrizUptime = await fetchMetric('avg_over_time(up{job="matriz"}[24h]) * 100');
        const matrizP95 = await fetchMetric('histogram_quantile(0.95, http_request_duration_seconds_bucket{service="matriz"})');

        if (matrizUptime !== null) {
            updateMetricValue('matriz-uptime', `${matrizUptime.toFixed(2)}%`);
            updateServiceStatus('matriz', getHealthStatus(matrizUptime));
        }

        if (matrizP95 !== null) {
            updateMetricValue('matriz-p95', `${Math.round(matrizP95)}ms`);
        }

        // Dream Engine metrics
        const dreamUptime = await fetchMetric('avg_over_time(up{job="dream"}[24h]) * 100');
        const dreamP95 = await fetchMetric('histogram_quantile(0.95, http_request_duration_seconds_bucket{service="dream"})');

        if (dreamUptime !== null) {
            updateMetricValue('dream-uptime', `${dreamUptime.toFixed(2)}%`);
            updateServiceStatus('dream', getHealthStatus(dreamUptime));
        }

        if (dreamP95 !== null) {
            updateMetricValue('dream-p95', `${Math.round(dreamP95)}ms`);
        }

        // Identity Service metrics
        const identityUptime = await fetchMetric('avg_over_time(up{job="identity"}[24h]) * 100');
        const identityP95 = await fetchMetric('histogram_quantile(0.95, http_request_duration_seconds_bucket{service="identity"})');

        if (identityUptime !== null) {
            updateMetricValue('identity-uptime', `${identityUptime.toFixed(2)}%`);
            updateServiceStatus('identity', getHealthStatus(identityUptime));
        }

        if (identityP95 !== null) {
            updateMetricValue('identity-p95', `${Math.round(identityP95)}ms`);
        }

        // Update overall status
        const serviceStatuses = [
            getHealthStatus(apiUptime || 100),
            dbStatus !== null ? (dbStatus === 'Healthy' || dbStatus === 1 ? 'healthy' : 'degraded') : 'healthy',
            cacheHitRate !== null ? (cacheHitRate >= 70 ? 'healthy' : 'degraded') : 'healthy',
            getHealthStatus(matrizUptime || 100),
            getHealthStatus(dreamUptime || 100),
            getHealthStatus(identityUptime || 100)
        ];

        updateOverallStatus(serviceStatuses);

        // Update last checked time
        const now = new Date();
        updateMetricValue('last-checked', now.toLocaleTimeString());
        updateMetricValue('last-updated', now.toLocaleString());

    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

/**
 * Initialize the status page
 */
function init() {
    console.log('LUKHAS AI Status Page initialized');
    console.log(`Mode: ${CONFIG.mockMode ? 'Mock (Development)' : 'Production (Prometheus)'}`);

    // Add service data attributes to cards for easy targeting
    const serviceCards = [
        { selector: '.metric-card:nth-of-type(1)', service: 'api' },
        { selector: '.metric-card:nth-of-type(2)', service: 'database' },
        { selector: '.metric-card:nth-of-type(3)', service: 'cache' },
        { selector: '.metric-card:nth-of-type(4)', service: 'matriz' },
        { selector: '.metric-card:nth-of-type(5)', service: 'dream' },
        { selector: '.metric-card:nth-of-type(6)', service: 'identity' }
    ];

    serviceCards.forEach(({ selector, service }) => {
        const card = document.querySelector(selector);
        if (card) {
            card.setAttribute('data-service', service);
        }
    });

    // Initial update
    updateAllMetrics();

    // Set up periodic refresh
    setInterval(updateAllMetrics, CONFIG.refreshInterval);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
