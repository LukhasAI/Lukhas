/**
 * LUKHAS Web UI Controller - Web-specific Emoji Grid Logic
 * 
 * This module implements web-specific UI control for emoji grid authentication
 * with constitutional enforcement and adaptive behavior based on user cognitive state.
 * 
 * Author: LUKHAS Team
 * Date: June 2025
 * Purpose: Web emoji grid authentication interface with constitutional compliance
 */

class LukhAsWebUIController {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container element with id '${containerId}' not found`);
        }
        
        this.options = {
            initialGridSize: options.initialGridSize || 9,
            maxGridSize: options.maxGridSize || 16,
            minGridSize: options.minGridSize || 4,
            timeoutSeconds: options.timeoutSeconds || 15,
            enableAnimations: options.enableAnimations !== false,
            enableHaptics: options.enableHaptics !== false,
            enableAudio: options.enableAudio || false,
            constitutionalMode: options.constitutionalMode !== false,
            adaptiveMode: options.adaptiveMode !== false,
            ...options
        };
        
        // UI state
        this.currentGridSize = this.options.initialGridSize;
        this.selectedEmojis = [];
        this.availableEmojis = [];
        this.isLocked = false;
        this.timeout = null;
        this.startTime = null;
        
        // Cognitive load tracking
        this.interactionHistory = [];
        this.mouseTracker = {
            movements: [],
            hesitation: 0,
            accuracy: 1.0
        };
        
        // Callbacks
        this.onSelectionComplete = null;
        this.onTimeout = null;
        this.onError = null;
        this.onCognitiveStateChange = null;
        
        // Constitutional enforcement (if available)
        this.constitutionalCompliance = this.options.constitutionalMode;
        
        this.initialize();
    }
    
    /**
     * Initialize the web UI controller
     */
    initialize() {
        this.createUIStructure();
        this.setupEventListeners();
        this.loadDefaultEmojis();
        
        if (this.options.adaptiveMode) {
            this.startCognitiveTracking();
        }
        
        console.log('LUKHAS Web UI Controller initialized');
    }
    
    /**
     * Create the basic UI structure
     */
    createUIStructure() {
        this.container.className = 'lukhas-auth-container';
        this.container.innerHTML = `
            <div class="lukhas-auth-header">
                <h3>LUKHAS Symbolic Authentication</h3>
                <div class="lukhas-timeout-indicator" id="timeoutIndicator"></div>
            </div>
            <div class="lukhas-emoji-grid" id="emojiGrid"></div>
            <div class="lukhas-selection-display" id="selectionDisplay">
                <p>Selected sequence: <span id="selectedSequence"></span></p>
            </div>
            <div class="lukhas-controls">
                <button id="clearBtn" class="lukhas-btn lukhas-btn-secondary">Clear</button>
                <button id="submitBtn" class="lukhas-btn lukhas-btn-primary" disabled>Authenticate</button>
            </div>
            <div class="lukhas-status" id="statusDisplay"></div>
        `;
        
        // Apply base styles
        this.applyBaseStyles();
        
        // Get references to key elements
        this.emojiGrid = this.container.querySelector('#emojiGrid');
        this.selectionDisplay = this.container.querySelector('#selectedSequence');
        this.timeoutIndicator = this.container.querySelector('#timeoutIndicator');
        this.statusDisplay = this.container.querySelector('#statusDisplay');
        this.clearBtn = this.container.querySelector('#clearBtn');
        this.submitBtn = this.container.querySelector('#submitBtn');
    }
    
    /**
     * Apply base CSS styles
     */
    applyBaseStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .lukhas-auth-container {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 500px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border-radius: 12px;
                color: white;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            .lukhas-auth-header {
                text-align: center;
                margin-bottom: 20px;
            }
            
            .lukhas-auth-header h3 {
                margin: 0 0 10px 0;
                font-weight: 300;
                letter-spacing: 1px;
            }
            
            .lukhas-timeout-indicator {
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
                overflow: hidden;
            }
            
            .lukhas-timeout-progress {
                height: 100%;
                background: linear-gradient(90deg, #00ff88, #ffaa00, #ff4444);
                border-radius: 2px;
                transition: width 0.1s ease;
            }
            
            .lukhas-emoji-grid {
                display: grid;
                gap: 8px;
                margin: 20px 0;
                justify-content: center;
            }
            
            .lukhas-emoji-item {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 12px;
                font-size: 24px;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 50px;
                user-select: none;
            }
            
            .lukhas-emoji-item:hover {
                background: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.5);
                transform: scale(1.05);
            }
            
            .lukhas-emoji-item.selected {
                background: rgba(0, 255, 136, 0.3);
                border-color: #00ff88;
                box-shadow: 0 0 12px rgba(0, 255, 136, 0.4);
            }
            
            .lukhas-emoji-item.disabled {
                opacity: 0.5;
                cursor: not-allowed;
                pointer-events: none;
            }
            
            .lukhas-selection-display {
                text-align: center;
                margin: 15px 0;
                min-height: 30px;
            }
            
            .lukhas-controls {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 20px 0;
            }
            
            .lukhas-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .lukhas-btn-primary {
                background: #00ff88;
                color: #1e3c72;
            }
            
            .lukhas-btn-primary:enabled:hover {
                background: #00cc6a;
                transform: translateY(-1px);
            }
            
            .lukhas-btn-primary:disabled {
                background: rgba(255, 255, 255, 0.2);
                color: rgba(255, 255, 255, 0.5);
                cursor: not-allowed;
            }
            
            .lukhas-btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            
            .lukhas-btn-secondary:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .lukhas-status {
                text-align: center;
                font-size: 12px;
                opacity: 0.8;
                min-height: 20px;
            }
            
            .lukhas-cognitive-indicator {
                position: absolute;
                top: 10px;
                right: 10px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #00ff88;
                opacity: 0.6;
            }
            
            .lukhas-cognitive-indicator.high-load {
                background: #ffaa00;
            }
            
            .lukhas-cognitive-indicator.overload {
                background: #ff4444;
                animation: pulse 1s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.6; }
                50% { opacity: 1; }
            }
            
            .lukhas-simplified {
                font-size: 18px;
            }
            
            .lukhas-simplified .lukhas-emoji-item {
                font-size: 32px;
                min-height: 60px;
                padding: 16px;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Grid interaction
        this.emojiGrid.addEventListener('click', (e) => this.handleEmojiClick(e));
        
        // Control buttons
        this.clearBtn.addEventListener('click', () => this.clearSelection());
        this.submitBtn.addEventListener('click', () => this.submitAuthentication());
        
        // Mouse tracking for cognitive load assessment
        this.container.addEventListener('mousemove', (e) => this.trackMouseMovement(e));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Touch support for mobile
        this.emojiGrid.addEventListener('touchstart', (e) => e.preventDefault());
        this.emojiGrid.addEventListener('touchend', (e) => this.handleEmojiClick(e));
    }
    
    /**
     * Load default emoji set with constitutional filtering
     */
    loadDefaultEmojis() {
        const defaultEmojis = [
            '😀', '😂', '🥰', '😎', '🤔', '😇', '🙃', '😊',
            '🌟', '⭐', '🌙', '☀️', '🌈', '🔥', '💧', '🌸',
            '🎯', '🎨', '🎭', '🎪', '🎵', '🎮', '🏆', '🎁',
            '🦄', '🐱', '🐶', '🦊', '🐝', '🦋', '🐢', '🐠',
            '🍎', '🍋', '🥑', '🍓', '🥕', '🌽', '🍯', '🧊',
            '⚡', '🔑', '🎲', '🧩', '💎', '🔮', '🎪', '🌺'
        ];
        
        // Apply constitutional filtering if enabled
        if (this.constitutionalCompliance) {
            this.availableEmojis = this.filterEmojisConstitutionally(defaultEmojis);
        } else {
            this.availableEmojis = defaultEmojis;
        }
        
        this.renderEmojiGrid();
    }
    
    /**
     * Apply constitutional filtering to emoji list
     */
    filterEmojisConstitutionally(emojis) {
        // Basic constitutional filtering
        const exclusions = ['🍖', '🥓', '🍷', '🍺', '🐷', '💀', '🖕', '💊'];
        const neurodivergentProblematic = ['⏰', '⏳', '📊', '📈'];
        
        return emojis.filter(emoji => 
            !exclusions.includes(emoji) && 
            !neurodivergentProblematic.includes(emoji)
        );
    }
    
    /**
     * Render the emoji grid based on current grid size
     */
    renderEmojiGrid() {
        const gridSizeClass = this.currentGridSize <= 4 ? 'grid-small' : 
                             this.currentGridSize <= 9 ? 'grid-medium' : 'grid-large';
        
        const columns = Math.ceil(Math.sqrt(this.currentGridSize));
        
        this.emojiGrid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
        this.emojiGrid.className = `lukhas-emoji-grid ${gridSizeClass}`;
        
        // Select random emojis for this grid
        const gridEmojis = this.selectRandomEmojis(this.currentGridSize);
        
        this.emojiGrid.innerHTML = gridEmojis.map((emoji, index) => `
            <div class="lukhas-emoji-item" data-emoji="${emoji}" data-index="${index}">
                ${emoji}
            </div>
        `).join('');
        
        this.updateStatus(`Grid: ${this.currentGridSize} emojis • Select your sequence`);
    }
    
    /**
     * Select random emojis from available set
     */
    selectRandomEmojis(count) {
        const shuffled = [...this.availableEmojis].sort(() => Math.random() - 0.5);
        return shuffled.slice(0, count);
    }
    
    /**
     * Handle emoji click/selection
     */
    handleEmojiClick(event) {
        if (this.isLocked) return;
        
        const emojiItem = event.target.closest('.lukhas-emoji-item');
        if (!emojiItem) return;
        
        const emoji = emojiItem.dataset.emoji;
        const index = parseInt(emojiItem.dataset.index);
        
        // Record interaction timing
        this.recordInteraction('emoji_select', {
            emoji,
            index,
            timestamp: Date.now(),
            timing: this.startTime ? Date.now() - this.startTime : 0
        });
        
        // Haptic feedback
        if (this.options.enableHaptics && navigator.vibrate) {
            navigator.vibrate(50);
        }
        
        // Visual feedback
        emojiItem.classList.add('selected');
        
        // Add to selection
        this.selectedEmojis.push(emoji);
        this.updateSelectionDisplay();
        
        // Check if selection is complete
        if (this.selectedEmojis.length >= 3) {
            this.submitBtn.disabled = false;
        }
        
        // Auto-submit if reached maximum selection
        if (this.selectedEmojis.length >= 6) {
            setTimeout(() => this.submitAuthentication(), 500);
        }
    }
    
    /**
     * Update selection display
     */
    updateSelectionDisplay() {
        this.selectionDisplay.textContent = this.selectedEmojis.join(' → ');
    }
    
    /**
     * Clear current selection
     */
    clearSelection() {
        this.selectedEmojis = [];
        this.updateSelectionDisplay();
        this.submitBtn.disabled = true;
        
        // Remove visual selection indicators
        this.emojiGrid.querySelectorAll('.lukhas-emoji-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        this.updateStatus('Selection cleared • Choose your emojis');
    }
    
    /**
     * Submit authentication
     */
    submitAuthentication() {
        if (this.selectedEmojis.length < 3) {
            this.updateStatus('Please select at least 3 emojis');
            return;
        }
        
        this.isLocked = true;
        this.clearTimeout();
        
        const authData = {
            selectedSequence: this.selectedEmojis,
            gridSize: this.currentGridSize,
            interactionHistory: this.interactionHistory,
            cognitiveMetrics: this.getCognitiveMetrics(),
            timestamp: new Date().toISOString()
        };
        
        this.updateStatus('Authenticating...');
        
        if (this.onSelectionComplete) {
            this.onSelectionComplete(authData);
        }
    }
    
    /**
     * Start authentication session with timeout
     */
    startAuthentication(timeoutSeconds = null) {
        this.startTime = Date.now();
        this.selectedEmojis = [];
        this.interactionHistory = [];
        this.isLocked = false;
        
        const timeout = timeoutSeconds || this.options.timeoutSeconds;
        
        this.clearSelection();
        this.renderEmojiGrid();
        this.startTimeout(timeout);
        
        this.updateStatus(`Authentication started • ${timeout}s timeout`);
    }
    
    /**
     * Start timeout countdown
     */
    startTimeout(seconds) {
        this.clearTimeout();
        
        let remainingTime = seconds;
        const progressBar = document.createElement('div');
        progressBar.className = 'lukhas-timeout-progress';
        progressBar.style.width = '100%';
        this.timeoutIndicator.appendChild(progressBar);
        
        this.timeout = setInterval(() => {
            remainingTime--;
            const percentage = (remainingTime / seconds) * 100;
            progressBar.style.width = `${percentage}%`;
            
            if (remainingTime <= 0) {
                this.handleTimeout();
            }
        }, 1000);
    }
    
    /**
     * Clear timeout
     */
    clearTimeout() {
        if (this.timeout) {
            clearInterval(this.timeout);
            this.timeout = null;
        }
        
        this.timeoutIndicator.innerHTML = '';
    }
    
    /**
     * Handle authentication timeout
     */
    handleTimeout() {
        this.isLocked = true;
        this.clearTimeout();
        this.updateStatus('Authentication timed out');
        
        if (this.onTimeout) {
            this.onTimeout({
                selectedEmojis: this.selectedEmojis,
                interactionHistory: this.interactionHistory
            });
        }
    }
    
    /**
     * Track mouse movement for cognitive load assessment
     */
    trackMouseMovement(event) {
        const rect = this.container.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        this.mouseTracker.movements.push({
            x, y, timestamp: Date.now()
        });
        
        // Keep only recent movements
        if (this.mouseTracker.movements.length > 50) {
            this.mouseTracker.movements = this.mouseTracker.movements.slice(-25);
        }
        
        // Calculate hesitation (rapid direction changes)
        if (this.mouseTracker.movements.length > 3) {
            this.calculateMouseHesitation();
        }
    }
    
    /**
     * Calculate mouse hesitation patterns
     */
    calculateMouseHesitation() {
        const recent = this.mouseTracker.movements.slice(-3);
        
        const dx1 = recent[1].x - recent[0].x;
        const dy1 = recent[1].y - recent[0].y;
        const dx2 = recent[2].x - recent[1].x;
        const dy2 = recent[2].y - recent[1].y;
        
        // Calculate direction change
        const angle1 = Math.atan2(dy1, dx1);
        const angle2 = Math.atan2(dy2, dx2);
        const angleChange = Math.abs(angle2 - angle1);
        
        if (angleChange > Math.PI / 2) {
            this.mouseTracker.hesitation += 0.1;
        }
        
        // Decay hesitation over time
        this.mouseTracker.hesitation *= 0.99;
    }
    
    /**
     * Record user interaction for cognitive assessment
     */
    recordInteraction(type, data) {
        this.interactionHistory.push({
            type,
            data,
            timestamp: Date.now()
        });
        
        // Limit history size
        if (this.interactionHistory.length > 100) {
            this.interactionHistory = this.interactionHistory.slice(-50);
        }
    }
    
    /**
     * Get cognitive load metrics
     */
    getCognitiveMetrics() {
        const totalTime = this.startTime ? Date.now() - this.startTime : 0;
        const interactionCount = this.interactionHistory.length;
        
        return {
            totalTime,
            interactionCount,
            averageResponseTime: interactionCount > 0 ? totalTime / interactionCount : 0,
            mouseHesitation: this.mouseTracker.hesitation,
            errorRate: this.calculateErrorRate(),
            cognitiveLoad: this.estimateCognitiveLoad()
        };
    }
    
    /**
     * Calculate error rate from interactions
     */
    calculateErrorRate() {
        // Simple error estimation based on hesitation and timing
        const hesitationFactor = Math.min(1.0, this.mouseTracker.hesitation / 5.0);
        return hesitationFactor;
    }
    
    /**
     * Estimate overall cognitive load
     */
    estimateCognitiveLoad() {
        const metrics = this.getCognitiveMetrics();
        
        const timeoutFactor = metrics.averageResponseTime > 3000 ? 0.3 : 0.0;
        const hesitationFactor = metrics.mouseHesitation * 0.4;
        const errorFactor = metrics.errorRate * 0.3;
        
        return Math.min(1.0, timeoutFactor + hesitationFactor + errorFactor);
    }
    
    /**
     * Start cognitive load tracking
     */
    startCognitiveTracking() {
        // Add cognitive load indicator
        const indicator = document.createElement('div');
        indicator.className = 'lukhas-cognitive-indicator';
        this.container.style.position = 'relative';
        this.container.appendChild(indicator);
        
        // Update cognitive state periodically
        setInterval(() => {
            const cognitiveLoad = this.estimateCognitiveLoad();
            
            if (cognitiveLoad > 0.7) {
                indicator.className = 'lukhas-cognitive-indicator overload';
                this.adaptUIForHighLoad();
            } else if (cognitiveLoad > 0.4) {
                indicator.className = 'lukhas-cognitive-indicator high-load';
            } else {
                indicator.className = 'lukhas-cognitive-indicator';
            }
            
            if (this.onCognitiveStateChange) {
                this.onCognitiveStateChange({
                    cognitiveLoad,
                    metrics: this.getCognitiveMetrics()
                });
            }
        }, 1000);
    }
    
    /**
     * Adapt UI for high cognitive load
     */
    adaptUIForHighLoad() {
        if (this.currentGridSize > 6) {
            this.currentGridSize = Math.max(4, this.currentGridSize - 2);
            this.renderEmojiGrid();
            this.updateStatus('UI simplified for easier interaction');
        }
        
        // Add simplified class for larger UI elements
        this.container.classList.add('lukhas-simplified');
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(event) {
        if (!this.container.contains(event.target)) return;
        
        switch (event.key) {
            case 'Escape':
                this.clearSelection();
                break;
            case 'Enter':
                if (!this.submitBtn.disabled) {
                    this.submitAuthentication();
                }
                break;
            case 'Backspace':
                if (this.selectedEmojis.length > 0) {
                    this.selectedEmojis.pop();
                    this.updateSelectionDisplay();
                    this.renderEmojiGrid();
                }
                break;
        }
    }
    
    /**
     * Update grid size (constitutional compliance)
     */
    updateGridSize(newSize) {
        const clampedSize = Math.max(
            this.options.minGridSize,
            Math.min(this.options.maxGridSize, newSize)
        );
        
        if (clampedSize !== this.currentGridSize) {
            this.currentGridSize = clampedSize;
            this.renderEmojiGrid();
            return true;
        }
        
        return false;
    }
    
    /**
     * Update status message
     */
    updateStatus(message) {
        this.statusDisplay.textContent = message;
    }
    
    /**
     * Get current UI state
     */
    getUIState() {
        return {
            gridSize: this.currentGridSize,
            selectedEmojis: [...this.selectedEmojis],
            isLocked: this.isLocked,
            cognitiveMetrics: this.getCognitiveMetrics(),
            constitutionalCompliance: this.constitutionalCompliance
        };
    }
    
    /**
     * Destroy the UI controller
     */
    destroy() {
        this.clearTimeout();
        
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeyboard);
        
        // Clear container
        this.container.innerHTML = '';
        this.container.className = '';
        
        console.log('LUKHAS Web UI Controller destroyed');
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LukhAsWebUIController;
}

// Global availability for direct HTML inclusion
if (typeof window !== 'undefined') {
    window.LukhAsWebUIController = LukhAsWebUIController;
}
