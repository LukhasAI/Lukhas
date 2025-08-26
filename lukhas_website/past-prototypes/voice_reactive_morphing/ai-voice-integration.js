// Advanced AI/AGI Voice Reactivity and Shape Control Integration
// Primary: OpenAI GPT-4, Fallbacks: Claude, Azure OpenAI, Gemini, Perplexity

class AIVoiceIntegration {
    constructor() {
        this.voiceAnalyzer = null;
        this.aiAgents = new Map();
        this.currentShape = 'default';
        this.voiceData = {
            frequency: 0,
            amplitude: 0,
            pitch: 0,
            volume: 0,
            speechRate: 0
        };

        // Advanced features
        this.responseCache = new Map();
        this.rateLimiters = new Map();
        this.costTracker = {
            totalCost: 0,
            dailyCost: 0,
            monthlyCost: 0,
            lastReset: new Date()
        };
        this.performanceMetrics = {
            responseTimes: [],
            successRates: {},
            errorRates: {}
        };
        this.fallbackChain = ['openai', 'claude', 'azure', 'gemini', 'perplexity'];
        this.currentAI = 'openai';

        this.init();
    }

    init() {
        this.setupVoiceAnalysis();
        this.setupAIAgents();
        this.setupShapeLibrary();
        this.setupRateLimiters();
        this.setupCostOptimization();
        this.startPerformanceMonitoring();
    }

    // Advanced AI Agent Setup with Fallback Chain
    setupAIAgents() {
        // Primary: OpenAI GPT-4
        this.aiAgents.set('openai', {
            name: 'OpenAI GPT-4',
            apiKey: null, // Set your API key
            endpoint: 'https://api.openai.com/v1/chat/completions',
            model: 'gpt-4',
            maxTokens: 150,
            temperature: 0.7,
            costPer1kTokens: 0.03,
            rateLimit: { requests: 100, window: 60000 }, // 100 requests per minute
            shapeControl: this.openAIShapeControl.bind(this),
            priority: 1
        });

        // Fallback 1: Claude
        this.aiAgents.set('claude', {
            name: 'Claude',
            apiKey: null, // Set your API key
            endpoint: 'https://api.anthropic.com/v1/messages',
            model: 'claude-3-sonnet-20240229',
            maxTokens: 150,
            temperature: 0.7,
            costPer1kTokens: 0.015,
            rateLimit: { requests: 50, window: 60000 },
            shapeControl: this.claudeShapeControl.bind(this),
            priority: 2
        });

        // Fallback 2: Azure OpenAI
        this.aiAgents.set('azure', {
            name: 'Azure OpenAI',
            apiKey: null, // Set your API key
            endpoint: 'https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions',
            model: 'gpt-4',
            maxTokens: 150,
            temperature: 0.7,
            costPer1kTokens: 0.03,
            rateLimit: { requests: 80, window: 60000 },
            shapeControl: this.azureShapeControl.bind(this),
            priority: 3
        });

        // Fallback 3: Gemini
        this.aiAgents.set('gemini', {
            name: 'Google Gemini',
            apiKey: null, // Set your API key
            endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            model: 'gemini-pro',
            maxTokens: 150,
            temperature: 0.7,
            costPer1kTokens: 0.0005,
            rateLimit: { requests: 60, window: 60000 },
            shapeControl: this.geminiShapeControl.bind(this),
            priority: 4
        });

        // Fallback 4: Perplexity
        this.aiAgents.set('perplexity', {
            name: 'Perplexity',
            apiKey: null, // Set your API key
            endpoint: 'https://api.perplexity.ai/chat/completions',
            model: 'llama-3.1-sonar-small-128k-online',
            maxTokens: 150,
            temperature: 0.7,
            costPer1kTokens: 0.0002,
            rateLimit: { requests: 40, window: 60000 },
            shapeControl: this.perplexityShapeControl.bind(this),
            priority: 5
        });
    }

    // Advanced Rate Limiting System
    setupRateLimiters() {
        this.aiAgents.forEach((agent, key) => {
            this.rateLimiters.set(key, {
                requests: [],
                limit: agent.rateLimit.requests,
                window: agent.rateLimit.window
            });
        });
    }

    // Advanced Cost Optimization
    setupCostOptimization() {
        // Reset daily costs at midnight
        setInterval(() => {
            const now = new Date();
            if (now.getDate() !== this.costTracker.lastReset.getDate()) {
                this.costTracker.dailyCost = 0;
                this.costTracker.lastReset = now;
            }
        }, 60000); // Check every minute

        // Reset monthly costs
        setInterval(() => {
            const now = new Date();
            if (now.getMonth() !== this.costTracker.lastReset.getMonth()) {
                this.costTracker.monthlyCost = 0;
            }
        }, 86400000); // Check daily
    }

    // Advanced Performance Monitoring
    startPerformanceMonitoring() {
        setInterval(() => {
            this.analyzePerformance();
        }, 300000); // Every 5 minutes
    }

    analyzePerformance() {
        const avgResponseTime = this.performanceMetrics.responseTimes.reduce((a, b) => a + b, 0) / this.performanceMetrics.responseTimes.length;

        console.log('🎯 Performance Metrics:');
        console.log(`Average Response Time: ${avgResponseTime.toFixed(2)}ms`);
        console.log(`Total Cost: $${this.costTracker.totalCost.toFixed(4)}`);
        console.log(`Daily Cost: $${this.costTracker.dailyCost.toFixed(4)}`);
        console.log(`Current AI: ${this.currentAI}`);

        // Auto-switch to better performing AI
        this.optimizeAISelection();
    }

    // Advanced AI Selection with Fallback Chain
    async getAIResponse(prompt, context = {}) {
        const startTime = Date.now();

        // Check cache first
        const cacheKey = this.generateCacheKey(prompt, context);
        if (this.responseCache.has(cacheKey)) {
            console.log('🚀 Using cached response');
            return this.responseCache.get(cacheKey);
        }

        // Try AI agents in priority order
        for (const aiKey of this.fallbackChain) {
            const agent = this.aiAgents.get(aiKey);

            if (!agent || !agent.apiKey) continue;

            // Check rate limits
            if (!this.checkRateLimit(aiKey)) {
                console.log(`⏳ Rate limited for ${aiKey}, trying next...`);
                continue;
            }

            try {
                console.log(`🎯 Trying ${agent.name}...`);

                const response = await this.callAIWithTimeout(agent, prompt, context);

                // Track performance
                const responseTime = Date.now() - startTime;
                this.performanceMetrics.responseTimes.push(responseTime);
                this.trackCost(aiKey, response.usage?.total_tokens || 100);

                // Cache successful response
                this.responseCache.set(cacheKey, response);

                // Update current AI
                this.currentAI = aiKey;

                console.log(`✅ ${agent.name} succeeded in ${responseTime}ms`);
                return response;

            } catch (error) {
                console.log(`❌ ${agent.name} failed: ${error.message}`);
                this.trackError(aiKey);
                continue;
            }
        }

        // All AIs failed, use fallback response
        console.log('🔄 All AIs failed, using fallback');
        return this.getFallbackResponse(prompt);
    }

    // Advanced Caching System
    generateCacheKey(prompt, context) {
        const contextStr = JSON.stringify(context);
        return btoa(prompt + contextStr).slice(0, 32);
    }

    // Advanced Rate Limiting
    checkRateLimit(aiKey) {
        const limiter = this.rateLimiters.get(aiKey);
        const now = Date.now();

        // Remove old requests
        limiter.requests = limiter.requests.filter(time => now - time < limiter.window);

        // Check if under limit
        if (limiter.requests.length >= limiter.limit) {
            return false;
        }

        // Add current request
        limiter.requests.push(now);
        return true;
    }

    // Advanced Cost Tracking
    trackCost(aiKey, tokens) {
        const agent = this.aiAgents.get(aiKey);
        const cost = (tokens / 1000) * agent.costPer1kTokens;

        this.costTracker.totalCost += cost;
        this.costTracker.dailyCost += cost;
        this.costTracker.monthlyCost += cost;
    }

    // Advanced Error Tracking
    trackError(aiKey) {
        if (!this.performanceMetrics.errorRates[aiKey]) {
            this.performanceMetrics.errorRates[aiKey] = 0;
        }
        this.performanceMetrics.errorRates[aiKey]++;
    }

    // Advanced Timeout Handling
    async callAIWithTimeout(agent, prompt, context, timeout = 5000) {
        return Promise.race([
            agent.shapeControl(prompt, context),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Timeout')), timeout)
            )
        ]);
    }

    // Advanced AI Optimization
    optimizeAISelection() {
        // Analyze performance and adjust fallback chain
        const errorRates = this.performanceMetrics.errorRates;
        const avgResponseTimes = this.calculateAverageResponseTimes();

        // Reorder fallback chain based on performance
        this.fallbackChain.sort((a, b) => {
            const aScore = this.calculateAIScore(a, errorRates[a] || 0, avgResponseTimes[a] || 1000);
            const bScore = this.calculateAIScore(b, errorRates[b] || 0, avgResponseTimes[b] || 1000);
            return bScore - aScore; // Higher score first
        });

        console.log('🎯 Optimized AI selection:', this.fallbackChain);
    }

    calculateAIScore(aiKey, errorRate, responseTime) {
        const agent = this.aiAgents.get(aiKey);
        const costFactor = 1 / (agent.costPer1kTokens * 1000); // Lower cost = higher score
        const errorFactor = 1 / (errorRate + 1); // Lower errors = higher score
        const timeFactor = 1 / (responseTime / 1000); // Lower time = higher score

        return costFactor * errorFactor * timeFactor;
    }

    // Advanced Fallback Response
    getFallbackResponse(prompt) {
        // Intelligent fallback based on prompt content
        if (prompt.includes('happy') || prompt.includes('joy')) {
            return {
                shape_type: 'bounce',
                scale: 1.2,
                color: '#FFD700',
                animation: 'bounce',
                emotion: 'happy'
            };
        } else if (prompt.includes('sad') || prompt.includes('melancholy')) {
            return {
                shape_type: 'droop',
                scale: 0.8,
                color: '#4169E1',
                animation: 'float',
                emotion: 'sad'
            };
        } else {
            return {
                shape_type: 'sphere',
                scale: 1.0,
                color: '#98FB98',
                animation: 'pulse',
                emotion: 'calm'
            };
        }
    }

    // Enhanced Voice Analysis with Advanced Features
    setupVoiceAnalysis() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                const audioContext = new AudioContext();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();

                // Advanced audio settings
                analyser.fftSize = 2048;
                analyser.smoothingTimeConstant = 0.8;

                source.connect(analyser);
                this.voiceAnalyzer = analyser;

                this.startVoiceAnalysis();
            })
            .catch(err => console.log('Voice input not available:', err));
    }

    startVoiceAnalysis() {
        const dataArray = new Uint8Array(this.voiceAnalyzer.frequencyBinCount);
        const timeDataArray = new Uint8Array(this.voiceAnalyzer.frequencyBinCount);

        const analyzeVoice = () => {
            this.voiceAnalyzer.getByteFrequencyData(dataArray);
            this.voiceAnalyzer.getByteTimeDomainData(timeDataArray);

            // Enhanced voice analysis
            this.voiceData.frequency = this.calculateAverageFrequency(dataArray);
            this.voiceData.amplitude = this.calculateAmplitude(dataArray);
            this.voiceData.pitch = this.detectPitch(dataArray);
            this.voiceData.volume = this.calculateVolume(timeDataArray);
            this.voiceData.speechRate = this.detectSpeechRate();
            this.voiceData.emotion = this.detectEmotion(dataArray, timeDataArray);

            // Apply advanced voice reactivity
            this.applyVoiceReactivity();

            requestAnimationFrame(analyzeVoice);
        };

        analyzeVoice();
    }

    // Advanced Voice Reactivity with AI Integration
    async applyVoiceReactivity() {
        const sphere = window.morphSystem;

        // Basic voice reactivity
        if (this.voiceData.pitch > 0.7) {
            sphere.setVerticalStretch(1.0 + this.voiceData.pitch * 0.5);
        }
        if (this.voiceData.pitch < 0.3) {
            sphere.setVerticalStretch(1.0 - (0.3 - this.voiceData.pitch) * 0.5);
        }
        if (this.voiceData.volume > 0.6) {
            sphere.setScale(1.0 + this.voiceData.volume * 0.3);
        }
        if (this.voiceData.volume < 0.4) {
            sphere.setScale(1.0 - (0.4 - this.voiceData.volume) * 0.3);
        }

        // Advanced: AI-powered voice interpretation
        if (this.shouldTriggerAIResponse()) {
            const voiceContext = {
                pitch: this.voiceData.pitch,
                volume: this.voiceData.volume,
                emotion: this.voiceData.emotion,
                speechRate: this.voiceData.speechRate
            };

            const prompt = this.generateVoicePrompt(voiceContext);
            const aiResponse = await this.getAIResponse(prompt, voiceContext);

            if (aiResponse) {
                this.applyAIShapeControl(aiResponse);
            }
        }
    }

    // Advanced AI Response Triggering
    shouldTriggerAIResponse() {
        // Trigger AI response based on voice patterns
        const significantChange = Math.abs(this.voiceData.volume - this.lastVolume) > 0.2 ||
                                Math.abs(this.voiceData.pitch - this.lastPitch) > 0.3;

        this.lastVolume = this.voiceData.volume;
        this.lastPitch = this.voiceData.pitch;

        return significantChange && this.voiceData.volume > 0.3;
    }

    // Advanced Voice Prompt Generation
    generateVoicePrompt(voiceContext) {
        return `
            Voice Analysis:
            - Pitch: ${voiceContext.pitch.toFixed(2)} (0=low, 1=high)
            - Volume: ${voiceContext.volume.toFixed(2)} (0=quiet, 1=loud)
            - Emotion: ${voiceContext.emotion}
            - Speech Rate: ${voiceContext.speechRate.toFixed(2)} (0=slow, 1=fast)

            Generate shape parameters for a 3D sphere that reflects this voice:
            - shape_type: (sphere, cube, pyramid, animal, object, abstract, emotional)
            - scale: (0.5 to 2.0)
            - color: (hex color matching emotion)
            - animation: (pulse, rotate, bounce, wave, static, emotional)
            - emotion: (happy, sad, angry, surprised, calm, excited, thoughtful)

            Return as JSON only.
        `;
    }

    // Enhanced emotion detection
    detectEmotion(freqData, timeData) {
        // Simple emotion detection based on voice characteristics
        const avgFreq = this.calculateAverageFrequency(freqData);
        const variance = this.calculateVariance(timeData);

        if (avgFreq > 0.7 && variance > 0.5) return 'excited';
        if (avgFreq < 0.3 && variance < 0.2) return 'sad';
        if (variance > 0.8) return 'angry';
        if (avgFreq > 0.6 && variance < 0.3) return 'happy';
        if (avgFreq < 0.4 && variance > 0.6) return 'surprised';

        return 'calm';
    }

    calculateVariance(dataArray) {
        const mean = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
        const variance = dataArray.reduce((sum, value) => sum + Math.pow(value - mean, 2), 0) / dataArray.length;
        return variance / 255; // Normalize
    }

    // Helper methods
    calculateAverageFrequency(dataArray) {
        return dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    }

    calculateAmplitude(dataArray) {
        return Math.max(...dataArray) / 255;
    }

    detectPitch(dataArray) {
        // Simplified pitch detection
        const dominantFreq = this.findDominantFrequency(dataArray);
        return Math.min(dominantFreq / 2000, 1.0); // Normalize to 0-1
    }

    calculateVolume(dataArray) {
        const rms = Math.sqrt(dataArray.reduce((sum, value) => sum + value * value, 0) / dataArray.length);
        return Math.min(rms / 128, 1.0);
    }

    detectSpeechRate() {
        // Simplified speech rate detection
        return this.voiceData.amplitude > 0.5 ? 0.8 : 0.3;
    }

    findDominantFrequency(dataArray) {
        let maxIndex = 0;
        let maxValue = 0;

        for (let i = 0; i < dataArray.length; i++) {
            if (dataArray[i] > maxValue) {
                maxValue = dataArray[i];
                maxIndex = i;
            }
        }

        return maxIndex * 22050 / dataArray.length; // Convert to Hz
    }

    calculateAverageResponseTimes() {
        // Calculate average response times for each AI
        const times = {};
        this.fallbackChain.forEach(ai => {
            times[ai] = 1000; // Default 1 second
        });
        return times;
    }

    // Shape Library for AI to choose from
    setupShapeLibrary() {
        this.shapeLibrary = {
            // Animals
            animals: ['cat', 'dog', 'bird', 'fish', 'elephant', 'dragon'],

            // Objects
            objects: ['car', 'house', 'tree', 'flower', 'star', 'heart'],

            // Abstract shapes
            abstract: ['wave', 'spiral', 'fractal', 'crystal', 'cloud', 'fire'],

            // Emotional shapes
            emotions: {
                happy: { shape: 'bounce', color: '#FFD700', scale: 1.2 },
                sad: { shape: 'droop', color: '#4169E1', scale: 0.8 },
                angry: { shape: 'spike', color: '#FF4500', scale: 1.1 },
                surprised: { shape: 'explode', color: '#FF69B4', scale: 1.5 },
                calm: { shape: 'float', color: '#98FB98', scale: 1.0 }
            }
        };
    }

    getRandomAnimal() {
        return this.shapeLibrary.animals[Math.floor(Math.random() * this.shapeLibrary.animals.length)];
    }

    getRandomObject() {
        return this.shapeLibrary.objects[Math.floor(Math.random() * this.shapeLibrary.objects.length)];
    }

    applyEmotion(emotion) {
        const emotionConfig = this.shapeLibrary.emotions[emotion];
        if (emotionConfig) {
            const sphere = window.morphSystem;
            sphere.morphTo(emotionConfig.shape);
            sphere.setColor(emotionConfig.color);
            sphere.setScale(emotionConfig.scale);
        }
    }

    // Apply AI-generated shape parameters
    applyAIShapeControl(shapeParams) {
        const sphere = window.morphSystem;

        // Shape type morphing
        switch(shapeParams.shape_type) {
            case 'sphere':
                sphere.morphTo('default');
                break;
            case 'cube':
                sphere.morphTo('cube');
                break;
            case 'pyramid':
                sphere.morphTo('pyramid');
                break;
            case 'animal':
                sphere.morphTo(this.getRandomAnimal());
                break;
            case 'object':
                sphere.morphTo(this.getRandomObject());
                break;
            case 'abstract':
                sphere.morphTo('abstract');
                break;
        }

        // Scale control
        sphere.setScale(shapeParams.scale);

        // Color control
        sphere.setColor(shapeParams.color);

        // Animation control
        sphere.setAnimation(shapeParams.animation);

        // Emotional expression
        this.applyEmotion(shapeParams.emotion);
    }

    // Advanced API implementations with proper error handling
    async openAIShapeControl(prompt, context = {}) {
        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.aiAgents.get('openai').apiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: 'gpt-4',
                    messages: [{ role: 'user', content: prompt }],
                    max_tokens: 150,
                    temperature: 0.7
                })
            });

            const data = await response.json();
            return JSON.parse(data.choices[0].message.content);

        } catch (error) {
            throw new Error(`OpenAI API error: ${error.message}`);
        }
    }

    async claudeShapeControl(prompt, context = {}) {
        try {
            const response = await fetch('https://api.anthropic.com/v1/messages', {
                method: 'POST',
                headers: {
                    'x-api-key': this.aiAgents.get('claude').apiKey,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: 'claude-3-sonnet-20240229',
                    max_tokens: 150,
                    messages: [{ role: 'user', content: prompt }]
                })
            });

            const data = await response.json();
            return JSON.parse(data.content[0].text);

        } catch (error) {
            throw new Error(`Claude API error: ${error.message}`);
        }
    }

    async azureShapeControl(prompt, context = {}) {
        // Azure OpenAI implementation
        // Similar to OpenAI but with Azure endpoint
        console.log('Azure OpenAI not implemented yet');
        throw new Error('Azure OpenAI not implemented');
    }

    async geminiShapeControl(prompt, context = {}) {
        // Gemini implementation
        console.log('Gemini not implemented yet');
        throw new Error('Gemini not implemented');
    }

    async perplexityShapeControl(prompt, context = {}) {
        // Perplexity implementation
        console.log('Perplexity not implemented yet');
        throw new Error('Perplexity not implemented');
    }
}

// Initialize the AI Voice Integration
// window.aiVoiceIntegration = new AIVoiceIntegration();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIVoiceIntegration;
}
