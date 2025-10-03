// dashboard/sseClient.js
// Example SSE client for Matriz cockpit integration
// Connects to MCP SSE streams and provides both structured + narrative events

class LukhasMCPCockpit {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.connections = new Map(); // topic -> EventSource
        this.listeners = new Map(); // event -> Set<callback>
    }

    /**
     * Subscribe to a topic (job/<id>, canary/<id>, or global/*)
     * Returns EventSource for manual control if needed
     */
    subscribe(topic) {
        if (this.connections.has(topic)) {
            console.warn(`Already subscribed to ${topic}`);
            return this.connections.get(topic);
        }

        const url = new URL(`${this.baseUrl}/sse`);
        url.searchParams.set('topic', topic);
        if (this.apiKey) url.searchParams.set('key', this.apiKey);

        const es = new EventSource(url);
        this.connections.set(topic, es);

        // Forward all events to listeners
        es.onopen = () => this.emit('open', { topic, url: url.toString() });
        es.onmessage = (e) => this.emit('message', { topic, data: this.parseData(e.data) });
        es.onerror = (e) => this.emit('error', { topic, error: e });

        // Specific MCP events
        ['queued', 'running', 'completed', 'failed',
            'metric', 'promoted', 'rolled_back', 'aborted'].forEach(eventType => {
                es.addEventListener(eventType, (e) => {
                    this.emit(eventType, {
                        topic,
                        eventType,
                        data: this.parseData(e.data),
                        narrative: this.toNarrative(eventType, this.parseData(e.data))
                    });
                });
            });

        return es;
    }

    /**
     * Unsubscribe from topic
     */
    unsubscribe(topic) {
        const es = this.connections.get(topic);
        if (es) {
            es.close();
            this.connections.delete(topic);
            this.emit('unsubscribed', { topic });
        }
    }

    /**
     * Subscribe to specific events
     */
    on(eventType, callback) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, new Set());
        }
        this.listeners.get(eventType).add(callback);
    }

    /**
     * Unsubscribe from events
     */
    off(eventType, callback) {
        const callbacks = this.listeners.get(eventType);
        if (callbacks) {
            callbacks.delete(callback);
        }
    }

    /**
     * Emit events to listeners
     */
    emit(eventType, data) {
        const callbacks = this.listeners.get(eventType);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`Error in ${eventType} callback:`, e);
                }
            });
        }
    }

    /**
     * Parse SSE data (JSON or plain text)
     */
    parseData(data) {
        try {
            return JSON.parse(data);
        } catch {
            return data;
        }
    }

    /**
     * Convert structured events to human-readable narrative
     */
    toNarrative(eventType, data) {
        const ts = new Date().toISOString().slice(0, 19).replace('T', ' ');

        switch (eventType) {
            case 'queued':
                return `[${ts}] ${data.jobId || data.canaryId} → queued for processing`;

            case 'running':
                return `[${ts}] ${data.jobId || data.canaryId} → executing ${data.taskId || data.modelId}`;

            case 'completed':
                return `[${ts}] ${data.jobId} → completed successfully (${data.duration || 'unknown'}s)`;

            case 'failed':
                return `[${ts}] ${data.jobId} → failed: ${data.error || 'unknown error'}`;

            case 'metric':
                const lat = data.latency_p95_ms ? `lat=${Math.round(data.latency_p95_ms)}ms` : '';
                const err = data.error_rate ? `err=${(data.error_rate * 100).toFixed(1)}%` : '';
                return `[${ts}] ${data.canaryId} → ${lat} ${err} (${data.gate})`;

            case 'promoted':
                return `[${ts}] ${data.canaryId} → promoted ${data.modelId} → ${data.toGate}`;

            case 'rolled_back':
                const reason = data.reason || 'SLO breach';
                return `[${ts}] ${data.canaryId} → rollback after ${data.duration || 'unknown'}m due to ${reason}`;

            case 'aborted':
                return `[${ts}] ${data.canaryId} → aborted by operator: ${data.reason || 'manual'}`;

            default:
                return `[${ts}] ${eventType}: ${JSON.stringify(data)}`;
        }
    }

    /**
     * Close all connections
     */
    disconnect() {
        this.connections.forEach((es, topic) => {
            es.close();
        });
        this.connections.clear();
        this.emit('disconnected', {});
    }
}

// Usage examples:
/*
// Initialize cockpit
const cockpit = new LukhasMCPCockpit('http://localhost:8766', 'your-api-key');

// Listen to all events with narrative
cockpit.on('queued', (event) => {
  console.log('Structured:', event.data);
  console.log('Narrative:', event.narrative);
});

// Subscribe to specific job
cockpit.subscribe('job/abc123');

// Subscribe to all canary events
cockpit.subscribe('canary/*');

// For Matriz UI integration:
cockpit.on('narrative', (event) => {
  document.getElementById('audit-scroll').appendChild(
    createElement('div', { className: 'audit-entry' }, event.narrative)
  );
});
*/

// Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LukhasMCPCockpit };
}

// Browser compatibility
if (typeof window !== 'undefined') {
    window.LukhasMCPCockpit = LukhasMCPCockpit;
}