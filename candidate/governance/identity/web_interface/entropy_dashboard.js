/**
 * LUKHAS Enhanced Authentication Dashboard
 * Real-time monitoring with trust scoring integration
 */

class LukhasDashboard {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.isReconnecting = false;
        
        // Dashboard state
        this.currentData = {
            entropy: { level: 0, quality: 'unknown' },
            trustScore: { total_score: 0, trust_level: 'unknown', components: {} },
            sessions: new Map(),
            devices: new Map(),
            alerts: []
        };
        
        // Performance tracking
        this.lastUpdate = Date.now();
        this.updateCount = 0;
        
        this.initializeComponents();
        this.connect();
        
        // Start periodic updates
        setInterval(() => this.updateDisplay(), 1000);
        setInterval(() => this.checkConnectionHealth(), 5000);
    }
    
    initializeComponents() {
        // Get DOM elements
        this.elements = {
            connectionStatus: document.getElementById('connectionStatus'),
            entropyValue: document.getElementById('entropyValue'),
            entropyQuality: document.getElementById('entropyQuality'),
            entropyProgress: document.getElementById('entropyProgress'),
            trustValue: document.getElementById('trustValue'),
            trustLevel: document.getElementById('trustLevel'),
            trustEntropy: document.getElementById('trustEntropy'),
            trustBehavioral: document.getElementById('trustBehavioral'),
            trustDevice: document.getElementById('trustDevice'),
            trustContextual: document.getElementById('trustContextual'),
            sessionCount: document.getElementById('sessionCount'),
            sessionStatus: document.getElementById('sessionStatus'),
            deviceCount: document.getElementById('deviceCount'),
            deviceStatus: document.getElementById('deviceStatus'),
            sessionsList: document.getElementById('sessionsList'),
            alertsList: document.getElementById('alertsList')
        };
        
        // Initialize display
        this.updateConnectionStatus('disconnected');
        this.log('Dashboard initialized', 'info');
    }
    
    connect() {
        try {
            // Try both WebSocket protocols
            const protocols = ['ws://localhost:8080', 'ws://127.0.0.1:8080'];
            const protocol = protocols[this.reconnectAttempts % protocols.length];
            
            this.log(`Connecting to ${protocol}...`, 'info');
            this.updateConnectionStatus('reconnecting');
            
            this.socket = new WebSocket(protocol);
            
            this.socket.onopen = () => {
                this.log('WebSocket connected successfully', 'info');
                this.updateConnectionStatus('connected');
                this.reconnectAttempts = 0;
                this.isReconnecting = false;
                
                // Send initial handshake
                this.sendMessage({
                    type: 'dashboard_connect',
                    timestamp: Date.now(),
                    client_type: 'web_dashboard'
                });
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    this.log(`Failed to parse message: ${error.message}`, 'error');
                }
            };
            
            this.socket.onclose = (event) => {
                this.log(`WebSocket closed: ${event.code} - ${event.reason}`, 'warning');
                this.updateConnectionStatus('disconnected');
                this.handleDisconnection();
            };
            
            this.socket.onerror = (error) => {
                this.log(`WebSocket error: ${error.message || 'Connection failed'}`, 'error');
                this.updateConnectionStatus('disconnected');
            };
            
        } catch (error) {
            this.log(`Connection failed: ${error.message}`, 'error');
            this.handleDisconnection();
        }
    }
    
    handleMessage(data) {
        this.lastUpdate = Date.now();
        this.updateCount++;
        
        switch (data.type) {
            case 'entropy_update':
                this.handleEntropyUpdate(data);
                break;
                
            case 'trust_score_update':
                this.handleTrustScoreUpdate(data);
                break;
                
            case 'session_update':
                this.handleSessionUpdate(data);
                break;
                
            case 'device_update':
                this.handleDeviceUpdate(data);
                break;
                
            case 'security_alert':
                this.handleSecurityAlert(data);
                break;
                
            case 'system_status':
                this.handleSystemStatus(data);
                break;
                
            default:
                this.log(`Unknown message type: ${data.type}`, 'warning');
        }
    }
    
    handleEntropyUpdate(data) {
        if (data.entropy_level !== undefined) {
            this.currentData.entropy = {
                level: data.entropy_level,
                quality: data.entropy_quality || 'medium',
                source: data.entropy_source || 'system',
                timestamp: Date.now()
            };
            
            this.log(`Entropy updated: ${data.entropy_level}% (${this.currentData.entropy.quality})`, 'info');
        }
    }
    
    handleTrustScoreUpdate(data) {
        if (data.trust_score) {
            this.currentData.trustScore = {
                ...data.trust_score,
                timestamp: Date.now()
            };
            
            this.log(`Trust score updated: ${data.trust_score.total_score}% (${data.trust_score.trust_level})`, 'info');
        }
    }
    
    handleSessionUpdate(data) {
        if (data.session_id) {
            this.currentData.sessions.set(data.session_id, {
                id: data.session_id,
                trustScore: data.trust_score || 0,
                lastActive: Date.now(),
                deviceCount: data.device_count || 0,
                status: data.status || 'active'
            });
        }
    }
    
    handleDeviceUpdate(data) {
        if (data.device_id) {
            this.currentData.devices.set(data.device_id, {
                id: data.device_id,
                trustScore: data.device_trust || 0,
                lastSeen: Date.now(),
                type: data.device_type || 'unknown',
                status: data.status || 'active'
            });
        }
    }
    
    handleSecurityAlert(data) {
        const alert = {
            id: Date.now(),
            type: data.alert_type || 'warning',
            message: data.message || 'Security event detected',
            details: data.details || {},
            timestamp: Date.now()
        };
        
        this.currentData.alerts.unshift(alert);
        
        // Keep only last 10 alerts
        if (this.currentData.alerts.length > 10) {
            this.currentData.alerts = this.currentData.alerts.slice(0, 10);
        }
        
        this.log(`Security alert: ${alert.message}`, alert.type);
    }
    
    handleSystemStatus(data) {
        this.log(`System status: ${data.message || 'Status update received'}`, 'info');
    }
    
    updateDisplay() {
        this.updateEntropyDisplay();
        this.updateTrustScoreDisplay();
        this.updateSessionsDisplay();
        this.updateDevicesDisplay();
        this.updateAlertsDisplay();
    }
    
    updateEntropyDisplay() {
        const entropy = this.currentData.entropy;
        
        this.elements.entropyValue.textContent = `${entropy.level}%`;
        this.elements.entropyQuality.textContent = `Quality: ${entropy.quality.toUpperCase()}`;
        this.elements.entropyProgress.style.width = `${entropy.level}%`;
        
        // Color coding for entropy level
        const color = entropy.level > 80 ? '#00ff88' : 
                     entropy.level > 50 ? '#ffaa00' : '#ff4444';
        this.elements.entropyValue.style.color = color;
        this.elements.entropyProgress.style.background = 
            `linear-gradient(90deg, ${color}, ${color}88)`;
    }
    
    updateTrustScoreDisplay() {
        const trust = this.currentData.trustScore;
        
        this.elements.trustValue.textContent = `${trust.total_score?.toFixed(1) || '--'}%`;
        this.elements.trustLevel.textContent = `Level: ${(trust.trust_level || 'unknown').toUpperCase()}`;
        
        // Update component scores
        const components = trust.components || {};
        this.elements.trustEntropy.textContent = `${components.entropy?.toFixed(1) || '--'}`;
        this.elements.trustBehavioral.textContent = `${components.behavioral?.toFixed(1) || '--'}`;
        this.elements.trustDevice.textContent = `${components.device?.toFixed(1) || '--'}`;
        this.elements.trustContextual.textContent = `${components.contextual?.toFixed(1) || '--'}`;
        
        // Color coding for trust level
        const color = trust.total_score > 80 ? '#00ff88' : 
                     trust.total_score > 60 ? '#ffaa00' : '#ff4444';
        this.elements.trustValue.style.color = color;
    }
    
    updateSessionsDisplay() {
        const activeSessions = Array.from(this.currentData.sessions.values())
            .filter(session => session.status === 'active');
        
        this.elements.sessionCount.textContent = activeSessions.length;
        this.elements.sessionStatus.textContent = activeSessions.length > 0 ? 
            `${activeSessions.length} active session${activeSessions.length !== 1 ? 's' : ''}` :
            'No active sessions';
        
        // Update sessions list
        if (activeSessions.length === 0) {
            this.elements.sessionsList.innerHTML = `
                <div class="session-item">
                    <div class="session-info">
                        <div class="session-id">No active sessions</div>
                        <div class="session-trust">Waiting for connections...</div>
                    </div>
                    <span class="status-indicator status-inactive"></span>
                </div>
            `;
        } else {
            this.elements.sessionsList.innerHTML = activeSessions.map(session => `
                <div class="session-item">
                    <div class="session-info">
                        <div class="session-id">${session.id.substring(0, 16)}...</div>
                        <div class="session-trust">Trust: ${session.trustScore}% | Devices: ${session.deviceCount}</div>
                    </div>
                    <span class="status-indicator status-active"></span>
                </div>
            `).join('');
        }
    }
    
    updateDevicesDisplay() {
        const activeDevices = Array.from(this.currentData.devices.values())
            .filter(device => device.status === 'active');
        
        this.elements.deviceCount.textContent = activeDevices.length;
        this.elements.deviceStatus.textContent = activeDevices.length > 0 ? 
            `${activeDevices.length} device${activeDevices.length !== 1 ? 's' : ''} connected` :
            'No devices connected';
    }
    
    updateAlertsDisplay() {
        if (this.currentData.alerts.length === 0) {
            this.elements.alertsList.innerHTML = `
                <div class="alert-item info">
                    <div>
                        <strong>System Status:</strong> LUKHAS Authentication System operational. No alerts.
                    </div>
                </div>
            `;
        } else {
            this.elements.alertsList.innerHTML = this.currentData.alerts.map(alert => `
                <div class="alert-item ${alert.type}">
                    <div>
                        <strong>${new Date(alert.timestamp).toLocaleTimeString()}:</strong> ${alert.message}
                    </div>
                </div>
            `).join('');
        }
    }
    
    updateConnectionStatus(status) {
        const statusElement = this.elements.connectionStatus;
        const indicator = statusElement.querySelector('.status-indicator');
        
        statusElement.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                statusElement.innerHTML = '<span class="status-indicator status-active"></span>Connected';
                break;
            case 'disconnected':
                statusElement.innerHTML = '<span class="status-indicator status-error"></span>Disconnected';
                break;
            case 'reconnecting':
                statusElement.innerHTML = '<span class="status-indicator status-warning pulse"></span>Reconnecting...';
                break;
        }
    }
    
    handleDisconnection() {
        if (this.isReconnecting) return;
        
        this.isReconnecting = true;
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
            this.reconnectAttempts++;
            
            this.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`, 'warning');
            
            setTimeout(() => {
                this.connect();
            }, delay);
        } else {
            this.log('Max reconnection attempts reached. Please refresh the page.', 'error');
            this.updateConnectionStatus('disconnected');
        }
    }
    
    checkConnectionHealth() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            // Send ping to check connection
            this.sendMessage({
                type: 'ping',
                timestamp: Date.now()
            });
            
            // Check if we've received updates recently
            const timeSinceLastUpdate = Date.now() - this.lastUpdate;
            if (timeSinceLastUpdate > 30000) { // 30 seconds
                this.log('No updates received for 30 seconds', 'warning');
            }
        }
    }
    
    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            try {
                this.socket.send(JSON.stringify(message));
            } catch (error) {
                this.log(`Failed to send message: ${error.message}`, 'error');
            }
        }
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[${timestamp}] LUKHAS Dashboard:`;
        
        switch (type) {
            case 'error':
                console.error(`${prefix} ${message}`);
                break;
            case 'warning':
                console.warn(`${prefix} ${message}`);
                break;
            case 'info':
            default:
                console.log(`${prefix} ${message}`);
                break;
        }
    }
    
    // Public API methods
    refreshConnection() {
        if (this.socket) {
            this.socket.close();
        }
        this.reconnectAttempts = 0;
        this.connect();
    }
    
    getStatus() {
        return {
            connected: this.socket && this.socket.readyState === WebSocket.OPEN,
            reconnectAttempts: this.reconnectAttempts,
            lastUpdate: this.lastUpdate,
            updateCount: this.updateCount,
            currentData: this.currentData
        };
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.lukhasDashboard = new LukhasDashboard();
    
    // Expose refresh function to global scope
    window.refreshDashboard = () => {
        window.lukhasDashboard.refreshConnection();
    };
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'r':
                    event.preventDefault();
                    window.refreshDashboard();
                    break;
            }
        }
    });
});

// Export for module use if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LukhasDashboard;
}