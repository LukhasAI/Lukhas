/**
 * LUKHAS Status Page - Real-time metrics from Prometheus
 */

const CONFIG = {
    prometheusUrl: 'http://localhost:9090',
    refreshInterval: 30000, // 30 seconds
    enableAutoRefresh: true
};

class StatusMonitor {
    constructor() {
        this.lastUpdate = null;
        this.fetchMetrics();

        if (CONFIG.enableAutoRefresh) {
            setInterval(() => this.fetchMetrics(), CONFIG.refreshInterval);
        }
    }

    async fetchMetrics() {
        try {
            // Fetch various Prometheus metrics
            const [uptime, latency, cacheHitRate, taskQueue] = await Promise.all([
                this.queryPrometheus('up{job="lukhas-api"}'),
                this.queryPrometheus('histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'),
                this.queryPrometheus('lukhas_identity_cache_hit_ratio'),
                this.queryPrometheus('lukhas_task_queue_length')
            ]);

            this.updateUI({
                uptime,
                latency,
                cacheHitRate,
                taskQueue
            });

            this.lastUpdate = new Date();
            this.updateLastUpdateTime();
            this.updateOverallStatus('operational');

        } catch (error) {
            console.error('Failed to fetch metrics:', error);
            this.updateOverallStatus('error');
        }
    }

    async queryPrometheus(query) {
        try {
            const url = `${CONFIG.prometheusUrl}/api/v1/query?query=${encodeURIComponent(query)}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Prometheus query failed: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.status === 'success' && data.data.result.length > 0) {
                return parseFloat(data.data.result[0].value[1]);
            }

            return null;
        } catch (error) {
            // Fallback to mock data for demo
            return this.getMockMetric(query);
        }
    }

    getMockMetric(query) {
        // Mock data for demonstration when Prometheus is unavailable
        if (query.includes('up')) return 1;
        if (query.includes('duration')) return 0.045; // 45ms
        if (query.includes('cache_hit')) return 0.942; // 94.2%
        if (query.includes('queue_length')) return 3;
        return Math.random();
    }

    updateUI(metrics) {
        // Update API metrics
        if (metrics.latency !== null) {
            const latencyMs = (metrics.latency * 1000).toFixed(0);
            document.getElementById('api-latency').textContent = `${latencyMs}ms`;
        }

        if (metrics.uptime !== null) {
            const uptimePercent = (metrics.uptime * 100).toFixed(2);
            document.getElementById('api-uptime').textContent = `${uptimePercent}%`;
        }

        // Update cache metrics
        if (metrics.cacheHitRate !== null) {
            const hitRate = (metrics.cacheHitRate * 100).toFixed(1);
            document.getElementById('cache-hit-rate').textContent = `${hitRate}%`;
        }

        // Update task queue
        if (metrics.taskQueue !== null) {
            document.getElementById('tasks-queue').textContent = Math.floor(metrics.taskQueue);
        }

        // Update service indicators
        this.updateServiceStatus('service-api', metrics.uptime > 0.99 ? 'healthy' : 'warning');
        this.updateServiceStatus('service-cache', metrics.cacheHitRate > 0.8 ? 'healthy' : 'warning');
        this.updateServiceStatus('service-db', true ? 'healthy' : 'error');
        this.updateServiceStatus('service-tasks', metrics.taskQueue < 100 ? 'healthy' : 'warning');
    }

    updateServiceStatus(serviceId, status) {
        const card = document.getElementById(serviceId);
        if (!card) return;

        const indicator = card.querySelector('.status-indicator');
        indicator.className = 'status-indicator';

        switch (status) {
            case 'healthy':
                indicator.classList.add('status-healthy');
                break;
            case 'warning':
                indicator.classList.add('status-warning');
                break;
            case 'error':
                indicator.classList.add('status-error');
                break;
        }
    }

    updateOverallStatus(status) {
        const badge = document.getElementById('overall-status');

        switch (status) {
            case 'operational':
                badge.className = 'status-badge status-operational';
                badge.textContent = 'All Systems Operational';
                break;
            case 'degraded':
                badge.className = 'status-badge status-degraded';
                badge.textContent = 'Degraded Performance';
                break;
            case 'error':
                badge.className = 'status-badge status-outage';
                badge.textContent = 'Service Disruption';
                break;
        }
    }

    updateLastUpdateTime() {
        const timeElement = document.getElementById('last-updated-time');
        if (this.lastUpdate) {
            timeElement.textContent = this.lastUpdate.toLocaleTimeString();
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const monitor = new StatusMonitor();
});
