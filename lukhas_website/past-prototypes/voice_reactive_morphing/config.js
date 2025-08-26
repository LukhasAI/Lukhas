// Advanced Configuration for AI Voice Integration
// Set your API keys and configure advanced features

const Config = {
    // API Keys - Set these for your AI services
    // ⚠️ SECURITY: Never commit real API keys to version control
    // Use environment variables in production
    apiKeys: {
        openai: null, // 'sk-your-openai-api-key-here'
        claude: null, // 'sk-ant-your-claude-api-key-here'
        azure: null, // 'your-azure-openai-api-key-here'
        gemini: null, // 'your-gemini-api-key-here'
        perplexity: null, // 'your-perplexity-api-key-here'
    },

    // Advanced Performance Settings
    performance: {
        maxResponseTime: 5000, // 5 seconds timeout
        cacheExpiry: 300000, // 5 minutes cache
        maxCacheSize: 1000, // Max cached responses
        enableCompression: true,
        enableGzip: true,
    },

    // Cost Management
    costControl: {
        dailyBudget: 10.00, // $10 daily limit
        monthlyBudget: 100.00, // $100 monthly limit
        enableCostAlerts: true,
        costAlertThreshold: 0.80, // Alert at 80% of budget
        autoSwitchToCheaperAI: true,
    },

    // Rate Limiting
    rateLimits: {
        openai: { requests: 100, window: 60000 }, // 100/min
        claude: { requests: 50, window: 60000 },  // 50/min
        azure: { requests: 80, window: 60000 },   // 80/min
        gemini: { requests: 60, window: 60000 },  // 60/min
        perplexity: { requests: 40, window: 60000 }, // 40/min
    },

    // Voice Analysis Settings
    voiceAnalysis: {
        sampleRate: 44100,
        fftSize: 2048,
        smoothingTimeConstant: 0.8,
        minVolumeThreshold: 0.1,
        maxVolumeThreshold: 0.9,
        pitchDetectionSensitivity: 0.7,
        emotionDetectionEnabled: true,
        speechRecognitionEnabled: true,
    },

    // AI Model Preferences
    aiModels: {
        openai: {
            primary: 'gpt-4',
            fallback: 'gpt-3.5-turbo',
            maxTokens: 150,
            temperature: 0.7,
            topP: 0.9,
        },
        claude: {
            primary: 'claude-3-sonnet-20240229',
            fallback: 'claude-3-haiku-20240307',
            maxTokens: 150,
            temperature: 0.7,
        },
        azure: {
            primary: 'gpt-4',
            fallback: 'gpt-35-turbo',
            maxTokens: 150,
            temperature: 0.7,
        },
        gemini: {
            primary: 'gemini-pro',
            fallback: 'gemini-pro-vision',
            maxTokens: 150,
            temperature: 0.7,
        },
        perplexity: {
            primary: 'llama-3.1-sonar-small-128k-online',
            fallback: 'llama-3.1-sonar-small-128k',
            maxTokens: 150,
            temperature: 0.7,
        },
    },

    // Shape Generation Settings
    shapeGeneration: {
        enableProceduralGeneration: true,
        enable3DModelLibrary: true,
        enableMathematicalShapes: true,
        enableEmotionalShapes: true,
        enableContextualShapes: true,
        maxShapeComplexity: 1000, // vertices
        shapeInterpolationSpeed: 0.5, // seconds
        enableShapeCaching: true,
    },

    // Advanced Features
    advancedFeatures: {
        enableAutoOptimization: true,
        enablePerformanceMonitoring: true,
        enableCostOptimization: true,
        enableIntelligentFallbacks: true,
        enableResponseCaching: true,
        enableErrorRecovery: true,
        enableLoadBalancing: true,
        enablePredictiveCaching: true,
    },

    // Security Settings
    security: {
        enableAPIKeyEncryption: true,
        enableRequestSigning: true,
        enableRateLimitBypass: false,
        enableDebugMode: false,
        enableErrorLogging: true,
        enablePerformanceLogging: true,
    },

    // Advanced Voice Features
    advancedVoice: {
        enableNoiseReduction: true,
        enableEchoCancellation: true,
        enableVoiceActivityDetection: true,
        enableSpeakerRecognition: false,
        enableEmotionAnalysis: true,
        enableSentimentAnalysis: true,
        enableLanguageDetection: true,
        enableAccentDetection: false,
    },

    // Real-time Settings
    realtime: {
        updateFrequency: 60, // FPS
        enableInterpolation: true,
        enableSmoothing: true,
        enablePrediction: true,
        enableAdaptiveQuality: true,
        enableDynamicScaling: true,
    },

    // Debug and Development
    debug: {
        enableConsoleLogging: true,
        enablePerformanceProfiling: false,
        enableAPIResponseLogging: false,
        enableVoiceDataLogging: false,
        enableShapeDataLogging: false,
        enableErrorStackTraces: true,
    },

    // Advanced Monitoring
    monitoring: {
        enableRealTimeMetrics: true,
        enableCostTracking: true,
        enablePerformanceTracking: true,
        enableErrorTracking: true,
        enableUsageAnalytics: true,
        enablePredictiveMaintenance: true,
    },

    // Customization
    customization: {
        enableCustomShapes: true,
        enableCustomAnimations: true,
        enableCustomColors: true,
        enableCustomEmotions: true,
        enableCustomVoiceResponses: true,
        enableCustomAIPrompts: true,
    },

    // Integration Settings
    integration: {
        enableWebSocketSupport: false,
        enableRESTAPI: false,
        enableGraphQL: false,
        enableWebhookSupport: false,
        enableEventStreaming: false,
        enableMessageQueue: false,
    },

    // Advanced Optimization
    optimization: {
        enableLazyLoading: true,
        enableCodeSplitting: true,
        enableTreeShaking: true,
        enableMinification: true,
        enableCompression: true,
        enableCDN: false,
        enableServiceWorker: false,
    },

    // Validation
    validateConfig() {
        const errors = [];

        // Check if at least one API key is set
        const hasValidAPIKey = Object.values(this.apiKeys).some(key => key && key.length > 0);
        if (!hasValidAPIKey) {
            errors.push('At least one API key must be configured');
        }

        // Validate performance settings
        if (this.performance.maxResponseTime < 1000) {
            errors.push('Max response time should be at least 1000ms');
        }

        // Validate cost settings
        if (this.costControl.dailyBudget <= 0) {
            errors.push('Daily budget must be greater than 0');
        }

        // Validate voice settings
        if (this.voiceAnalysis.sampleRate < 8000) {
            errors.push('Sample rate should be at least 8000Hz');
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },

    // Get optimized settings based on current performance
    getOptimizedSettings() {
        return {
            // Auto-adjust based on performance metrics
            performance: {
                ...this.performance,
                maxResponseTime: this.getOptimalResponseTime(),
                cacheExpiry: this.getOptimalCacheExpiry(),
            },

            // Auto-adjust based on cost
            costControl: {
                ...this.costControl,
                dailyBudget: this.getOptimalDailyBudget(),
            },

            // Auto-adjust based on voice quality
            voiceAnalysis: {
                ...this.voiceAnalysis,
                fftSize: this.getOptimalFFTSize(),
            },
        };
    },

    // Helper methods for optimization
    getOptimalResponseTime() {
        // Return optimal response time based on current performance
        return 5000; // Default 5 seconds
    },

    getOptimalCacheExpiry() {
        // Return optimal cache expiry based on usage patterns
        return 300000; // Default 5 minutes
    },

    getOptimalDailyBudget() {
        // Return optimal daily budget based on usage
        return 10.00; // Default $10
    },

    getOptimalFFTSize() {
        // Return optimal FFT size based on performance
        return 2048; // Default 2048
    },

    // Export configuration
    export() {
        return {
            ...this,
            exportDate: new Date().toISOString(),
            version: '1.0.0',
        };
    },

    // Import configuration
    import(config) {
        Object.assign(this, config);
        const validation = this.validateConfig();
        if (!validation.isValid) {
            console.warn('Configuration validation failed:', validation.errors);
        }
        return validation;
    },
};

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Config;
} else {
    window.Config = Config;
}

// Auto-validate on load
const validation = Config.validateConfig();
if (!validation.isValid) {
    console.warn('Config validation failed:', validation.errors);
}
