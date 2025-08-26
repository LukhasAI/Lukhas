/**
 * LUKHAS WebSocket Client - Browser Entropy Synchronization
 *
 * This module implements WebSocket client functionality for browsers to participate
 * in multi-device entropy synchronization for LUKHAS authentication.
 *
 * Author: LUKHAS Team
 * Date: June 2025
 * Purpose: Browser-based entropy sync and real-time communication
 */

class LukhAsWebSocketClient {
    constructor(sessionId, options = {}) {
        this.sessionId = sessionId;
        this.deviceId = this.generateDeviceId();
        this.options = {
            serverUrl: options.serverUrl || 'ws://localhost:8080',
            reconnectAttempts: options.reconnectAttempts || 5,
            reconnectDelay: options.reconnectDelay || 1000,
            entropyCollectionInterval: options.entropyCollectionInterval || 500,
            ...options
        };

        this.websocket = null;
        this.isConnected = false;
        this.reconnectCount = 0;
        this.entropyBuffer = [];
        this.syncCallbacks = [];
        this.connectionCallbacks = [];

        // Entropy collection state
        this.mouseMovements = [];
        this.keystrokes = [];
        this.deviceMetrics = {};

        this.startEntropyCollection();
    }

    /**
     * Generate unique device ID for this browser session
     */
    generateDeviceId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2);
        const userAgent = navigator.userAgent.slice(0, 20);

        return btoa(`browser_${timestamp}_${random}_${userAgent}`).replace(/[^a-zA-Z0-9]/g, '').substring(0, 32);
    }

    /**
     * Connect to the LUKHAS entropy synchronization server
     */
    async connect() {
        try {
            const wsUrl = `${this.options.serverUrl}/sync/${this.sessionId}`;
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('LUKHAS WebSocket connected');
                this.isConnected = true;
                this.reconnectCount = 0;
                this.authenticateDevice();
                this.notifyConnectionCallbacks('connected');
            };

            this.websocket.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

            this.websocket.onclose = () => {
                console.log('LUKHAS WebSocket disconnected');
                this.isConnected = false;
                this.notifyConnectionCallbacks('disconnected');
                this.attemptReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('LUKHAS WebSocket error:', error);
                this.notifyConnectionCallbacks('error', error);
            };

            return true;
        } catch (error) {
            console.error('Failed to connect to entropy server:', error);
            return false;
        }
    }

    /**
     * Authenticate this browser device with the server
     */
    authenticateDevice() {
        if (!this.isConnected) return;

        const authMessage = {
            type: 'device_auth',
            device_id: this.deviceId,
            device_type: 'web_browser',
            capabilities: this.getDeviceCapabilities(),
            timestamp: new Date().toISOString()
        };

        this.websocket.send(JSON.stringify(authMessage));
    }

    /**
     * Get browser device capabilities
     */
    getDeviceCapabilities() {
        return {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
            deviceMemory: navigator.deviceMemory || 'unknown',
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null,
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            webgl: this.getWebGLInfo()
        };
    }

    /**
     * Get WebGL information for device fingerprinting
     */
    getWebGLInfo() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

            if (!gl) return null;

            return {
                vendor: gl.getParameter(gl.VENDOR),
                renderer: gl.getParameter(gl.RENDERER),
                version: gl.getParameter(gl.VERSION),
                shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION)
            };
        } catch (e) {
            return null;
        }
    }

    /**
     * Start collecting entropy from browser interactions
     */
    startEntropyCollection() {
        // Mouse movement entropy
        document.addEventListener('mousemove', (e) => {
            this.mouseMovements.push({
                x: e.clientX,
                y: e.clientY,
                timestamp: Date.now(),
                pressure: e.pressure || 0,
                buttons: e.buttons
            });

            // Keep buffer size manageable
            if (this.mouseMovements.length > 100) {
                this.mouseMovements = this.mouseMovements.slice(-50);
            }
        });

        // Keyboard timing entropy
        document.addEventListener('keydown', (e) => {
            this.keystrokes.push({
                code: e.code,
                timestamp: Date.now(),
                ctrlKey: e.ctrlKey,
                shiftKey: e.shiftKey,
                altKey: e.altKey
            });

            if (this.keystrokes.length > 50) {
                this.keystrokes = this.keystrokes.slice(-25);
            }
        });

        // Device orientation entropy (mobile/tablet)
        if (window.DeviceOrientationEvent) {
            window.addEventListener('deviceorientation', (e) => {
                this.deviceMetrics.orientation = {
                    alpha: e.alpha,
                    beta: e.beta,
                    gamma: e.gamma,
                    timestamp: Date.now()
                };
            });
        }

        // Device motion entropy (mobile/tablet)
        if (window.DeviceMotionEvent) {
            window.addEventListener('devicemotion', (e) => {
                this.deviceMetrics.motion = {
                    acceleration: e.acceleration,
                    accelerationIncludingGravity: e.accelerationIncludingGravity,
                    rotationRate: e.rotationRate,
                    timestamp: Date.now()
                };
            });
        }

        // Network timing entropy
        this.collectNetworkTiming();

        // Start periodic entropy transmission
        setInterval(() => {
            if (this.isConnected) {
                this.sendEntropyData();
            }
        }, this.options.entropyCollectionInterval);
    }

    /**
     * Collect network timing information for entropy
     */
    collectNetworkTiming() {
        if (performance && performance.timing) {
            this.deviceMetrics.networkTiming = {
                navigationStart: performance.timing.navigationStart,
                connectStart: performance.timing.connectStart,
                connectEnd: performance.timing.connectEnd,
                responseStart: performance.timing.responseStart,
                responseEnd: performance.timing.responseEnd,
                domLoading: performance.timing.domLoading,
                domComplete: performance.timing.domComplete
            };
        }

        // Collect resource timing if available
        if (performance && performance.getEntriesByType) {
            const resourceTimings = performance.getEntriesByType('resource').slice(-10);
            this.deviceMetrics.resourceTimings = resourceTimings.map(entry => ({
                name: entry.name.split('/').pop(), // Only keep filename for privacy
                duration: entry.duration,
                transferSize: entry.transferSize,
                encodedBodySize: entry.encodedBodySize
            }));
        }
    }

    /**
     * Send collected entropy data to the server
     */
    sendEntropyData() {
        if (!this.isConnected || this.mouseMovements.length === 0) return;

        const entropyData = {
            mouse_movements: this.mouseMovements.slice(-10), // Last 10 movements
            keystroke_timings: this.keystrokes.slice(-5),    // Last 5 keystrokes (without content)
            device_metrics: this.deviceMetrics,
            performance_timing: this.getPerformanceTiming(),
            random_samples: this.generateRandomSamples(),
            timestamp: new Date().toISOString()
        };

        const message = {
            type: 'entropy_data',
            device_id: this.deviceId,
            entropy: entropyData,
            timestamp: new Date().toISOString()
        };

        this.websocket.send(JSON.stringify(message));

        // Clear sent data
        this.mouseMovements = [];
        this.keystrokes = [];
    }

    /**
     * Get performance timing for entropy
     */
    getPerformanceTiming() {
        if (!performance || !performance.now) return null;

        return {
            now: performance.now(),
            memory: performance.memory ? {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            } : null,
            navigation: performance.navigation ? {
                type: performance.navigation.type,
                redirectCount: performance.navigation.redirectCount
            } : null
        };
    }

    /**
     * Generate additional random samples for entropy
     */
    generateRandomSamples() {
        const samples = [];

        for (let i = 0; i < 10; i++) {
            samples.push({
                crypto: crypto.getRandomValues ? Array.from(crypto.getRandomValues(new Uint8Array(4))) : null,
                math: Math.random(),
                timestamp: Date.now() + Math.random(),
                index: i
            });
        }

        return samples;
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(data) {
        switch (data.type) {
            case 'device_authenticated':
                console.log('Device authenticated with session:', data.session_id);
                break;

            case 'connection_rejected':
                console.warn('Connection rejected:', data.reason);
                this.notifyConnectionCallbacks('rejected', data.reason);
                break;

            case 'entropy_ack':
                console.log('Entropy acknowledged, quality score:', data.quality_score);
                break;

            case 'sync_complete':
                console.log('Entropy synchronization complete');
                this.notifySyncCallbacks(data);
                break;

            case 'error':
                console.error('Server error:', data.message);
                break;

            default:
                console.log('Unknown message type:', data.type);
        }
    }

    /**
     * Attempt to reconnect to the server
     */
    attemptReconnect() {
        if (this.reconnectCount >= this.options.reconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.notifyConnectionCallbacks('max_attempts_reached');
            return;
        }

        this.reconnectCount++;
        const delay = this.options.reconnectDelay * Math.pow(2, this.reconnectCount - 1); // Exponential backoff

        console.log(`Attempting reconnection ${this.reconnectCount}/${this.options.reconnectAttempts} in ${delay}ms`);

        setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Add callback for sync completion events
     */
    onSyncComplete(callback) {
        this.syncCallbacks.push(callback);
    }

    /**
     * Add callback for connection state changes
     */
    onConnectionChange(callback) {
        this.connectionCallbacks.push(callback);
    }

    /**
     * Notify sync completion callbacks
     */
    notifySyncCallbacks(data) {
        this.syncCallbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('Error in sync callback:', error);
            }
        });
    }

    /**
     * Notify connection state callbacks
     */
    notifyConnectionCallbacks(state, data = null) {
        this.connectionCallbacks.forEach(callback => {
            try {
                callback(state, data);
            } catch (error) {
                console.error('Error in connection callback:', error);
            }
        });
    }

    /**
     * Get current connection status
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            deviceId: this.deviceId,
            sessionId: this.sessionId,
            reconnectCount: this.reconnectCount,
            entropyBufferSize: this.entropyBuffer.length
        };
    }

    /**
     * Disconnect and cleanup
     */
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }

        this.isConnected = false;
        this.mouseMovements = [];
        this.keystrokes = [];
        this.deviceMetrics = {};

        console.log('LUKHAS WebSocket client disconnected and cleaned up');
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LukhAsWebSocketClient;
}

// Global availability for direct HTML inclusion
if (typeof window !== 'undefined') {
    window.LukhAsWebSocketClient = LukhAsWebSocketClient;
}
