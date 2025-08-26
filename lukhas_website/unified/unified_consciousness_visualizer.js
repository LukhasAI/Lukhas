/**
 * LUKHAS Unified Consciousness Visualizer
 * ========================================
 * A comprehensive 3D visualization engine that unifies text-to-shape and voice-reactive
 * morphing capabilities with LUKHAS consciousness systems.
 *
 * Features:
 * - Text to 3D shape conversion with particle effects
 * - Voice-reactive morphing and animations
 * - Consciousness state visualization
 * - AI-driven shape interpretation
 * - High-performance WebGL rendering with Three.js
 *
 * @module UnifiedConsciousnessVisualizer
 * @requires Three.js
 */

(function(global) {
    'use strict';

    class UnifiedConsciousnessVisualizer {
        constructor(config = {}) {
            this.config = {
                containerId: config.containerId || 'lukhas-visualizer',
                particleCount: config.particleCount || 20000,
                enableVoice: config.enableVoice !== false,
                enableText: config.enableText !== false,
                enableConsciousness: config.enableConsciousness !== false,
                apiKeys: config.apiKeys || {},
                ...config
            };

            // Core systems
            this.scene = null;
            this.camera = null;
            this.renderer = null;
            this.clock = null;

            // Particle systems
            this.particleSystem = null;
            this.particleGeometry = null;
            this.particleMaterial = null;
            this.particlePositions = null;
            this.particleVelocities = null;
            this.particleTargets = null;
            this.particleColors = null;

            // Shape morphing
            this.morphEngine = null;
            this.currentShape = 'sphere';
            this.targetShape = 'sphere';
            this.morphProgress = 0;
            this.morphSpeed = 0.02;

            // Text rendering
            this.textEngine = null;
            this.textCanvas = null;
            this.textContext = null;
            this.currentText = '';

            // Voice analysis
            this.voiceAnalyzer = null;
            this.voiceData = {
                frequency: 0,
                amplitude: 0,
                pitch: 0,
                volume: 0,
                intensity: 0,
                emotion: 'neutral'
            };

            // Consciousness state
            this.consciousnessState = {
                awareness: 0.5,
                coherence: 0.5,
                depth: 2,
                attention: 0.5,
                entropy: 0.3,
                emotion: {
                    valence: 0.5,
                    arousal: 0.5,
                    dominance: 0.5
                }
            };

            // Performance tracking
            this.stats = null;
            this.frameCount = 0;
            this.lastFrameTime = 0;

            // Initialize system
            this.initialize();
        }

        /**
         * Initialize all subsystems
         */
        async initialize() {
            try {
                // Check Three.js availability
                if (typeof THREE === 'undefined') {
                    throw new Error('Three.js is required but not found');
                }

                // Setup core rendering
                this.setupScene();
                this.setupCamera();
                this.setupRenderer();
                this.setupLighting();

                // Initialize engines
                this.initializeMorphEngine();
                this.initializeTextEngine();
                this.initializeParticleSystem();

                // Setup optional features
                if (this.config.enableVoice) {
                    await this.initializeVoiceSystem();
                }

                if (this.config.enableConsciousness) {
                    this.initializeConsciousnessIntegration();
                }

                // Setup controls and UI
                this.setupControls();
                this.setupUI();

                // Start animation loop
                this.startAnimation();

                console.log('✨ LUKHAS Unified Visualizer initialized successfully');

            } catch (error) {
                console.error('Failed to initialize visualizer:', error);
            }
        }

        /**
         * Setup Three.js scene
         */
        setupScene() {
            this.scene = new THREE.Scene();
            this.scene.background = new THREE.Color(0x0a0a0f);
            this.scene.fog = new THREE.Fog(0x0a0a0f, 50, 200);
            this.clock = new THREE.Clock();
        }

        /**
         * Setup camera
         */
        setupCamera() {
            const container = document.getElementById(this.config.containerId);
            const aspect = container ? container.clientWidth / container.clientHeight : window.innerWidth / window.innerHeight;

            this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
            this.camera.position.set(0, 0, 50);
            this.camera.lookAt(0, 0, 0);
        }

        /**
         * Setup WebGL renderer
         */
        setupRenderer() {
            const container = document.getElementById(this.config.containerId);

            this.renderer = new THREE.WebGLRenderer({
                antialias: true,
                alpha: true,
                powerPreference: 'high-performance'
            });

            const width = container ? container.clientWidth : window.innerWidth;
            const height = container ? container.clientHeight : window.innerHeight;

            this.renderer.setSize(width, height);
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            this.renderer.shadowMap.enabled = true;
            this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            if (container) {
                container.appendChild(this.renderer.domElement);
            } else {
                document.body.appendChild(this.renderer.domElement);
            }

            // Handle resize
            window.addEventListener('resize', () => this.handleResize());
        }

        /**
         * Setup lighting
         */
        setupLighting() {
            // Ambient light
            const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
            this.scene.add(ambientLight);

            // Consciousness light (dynamic)
            this.consciousnessLight = new THREE.PointLight(0x00d4ff, 1, 100);
            this.consciousnessLight.position.set(0, 20, 10);
            this.consciousnessLight.castShadow = true;
            this.scene.add(this.consciousnessLight);

            // Identity light (pink)
            this.identityLight = new THREE.PointLight(0xff6b9d, 0.8, 80);
            this.identityLight.position.set(-20, 10, 5);
            this.scene.add(this.identityLight);

            // Guardian light (purple)
            this.guardianLight = new THREE.PointLight(0x7c3aed, 0.8, 80);
            this.guardianLight.position.set(20, 10, 5);
            this.scene.add(this.guardianLight);
        }

        /**
         * Initialize particle system
         */
        initializeParticleSystem() {
            const count = this.config.particleCount;

            // Create geometry
            this.particleGeometry = new THREE.BufferGeometry();

            // Position array
            this.particlePositions = new Float32Array(count * 3);
            this.particleVelocities = new Float32Array(count * 3);
            this.particleTargets = new Float32Array(count * 3);

            // Color array
            this.particleColors = new Float32Array(count * 3);

            // Size array
            const sizes = new Float32Array(count);

            // Initialize particles in sphere formation
            for (let i = 0; i < count; i++) {
                const i3 = i * 3;

                // Random sphere distribution
                const radius = Math.random() * 20 + 10;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.random() * Math.PI;

                this.particlePositions[i3] = radius * Math.sin(phi) * Math.cos(theta);
                this.particlePositions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
                this.particlePositions[i3 + 2] = radius * Math.cos(phi);

                // Copy to targets
                this.particleTargets[i3] = this.particlePositions[i3];
                this.particleTargets[i3 + 1] = this.particlePositions[i3 + 1];
                this.particleTargets[i3 + 2] = this.particlePositions[i3 + 2];

                // Random velocities
                this.particleVelocities[i3] = (Math.random() - 0.5) * 0.02;
                this.particleVelocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
                this.particleVelocities[i3 + 2] = (Math.random() - 0.5) * 0.02;

                // Consciousness-inspired colors
                const hue = 0.5 + Math.random() * 0.3; // Cyan to purple range
                const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
                this.particleColors[i3] = color.r;
                this.particleColors[i3 + 1] = color.g;
                this.particleColors[i3 + 2] = color.b;

                // Random sizes
                sizes[i] = Math.random() * 2 + 0.5;
            }

            // Set attributes
            this.particleGeometry.setAttribute('position', new THREE.BufferAttribute(this.particlePositions, 3));
            this.particleGeometry.setAttribute('color', new THREE.BufferAttribute(this.particleColors, 3));
            this.particleGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

            // Create material with custom shader
            this.particleMaterial = new THREE.PointsMaterial({
                size: 1.5,
                sizeAttenuation: true,
                vertexColors: true,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });

            // Create particle system
            this.particleSystem = new THREE.Points(this.particleGeometry, this.particleMaterial);
            this.scene.add(this.particleSystem);
        }

        /**
         * Initialize morphing engine
         */
        initializeMorphEngine() {
            this.morphEngine = {
                shapes: {
                    sphere: (i, count) => {
                        const phi = Math.acos(1 - 2 * i / count);
                        const theta = Math.sqrt(count * Math.PI) * phi;
                        const radius = 15;
                        return {
                            x: radius * Math.sin(phi) * Math.cos(theta),
                            y: radius * Math.sin(phi) * Math.sin(theta),
                            z: radius * Math.cos(phi)
                        };
                    },
                    cube: (i, count) => {
                        const side = Math.cbrt(count);
                        const x = (i % side) - side / 2;
                        const y = (Math.floor(i / side) % side) - side / 2;
                        const z = Math.floor(i / (side * side)) - side / 2;
                        const scale = 2;
                        return { x: x * scale, y: y * scale, z: z * scale };
                    },
                    torus: (i, count) => {
                        const u = (i % Math.sqrt(count)) / Math.sqrt(count) * Math.PI * 2;
                        const v = Math.floor(i / Math.sqrt(count)) / Math.sqrt(count) * Math.PI * 2;
                        const R = 12, r = 5;
                        return {
                            x: (R + r * Math.cos(v)) * Math.cos(u),
                            y: (R + r * Math.cos(v)) * Math.sin(u),
                            z: r * Math.sin(v)
                        };
                    },
                    helix: (i, count) => {
                        const t = i / count * Math.PI * 4;
                        const radius = 10;
                        const height = 30;
                        return {
                            x: radius * Math.cos(t),
                            y: (i / count - 0.5) * height,
                            z: radius * Math.sin(t)
                        };
                    },
                    heart: (i, count) => {
                        const t = i / count * Math.PI * 2;
                        const scale = 0.8;
                        const x = 16 * Math.pow(Math.sin(t), 3);
                        const y = 13 * Math.cos(t) - 5 * Math.cos(2*t) - 2 * Math.cos(3*t) - Math.cos(4*t);
                        const z = (Math.random() - 0.5) * 5;
                        return { x: x * scale, y: y * scale, z: z };
                    },
                    dna: (i, count) => {
                        const t = i / count * Math.PI * 4;
                        const radius = 8;
                        const height = 40;
                        const strand = i % 2;
                        return {
                            x: radius * Math.cos(t + strand * Math.PI),
                            y: (i / count - 0.5) * height,
                            z: radius * Math.sin(t + strand * Math.PI)
                        };
                    },
                    galaxy: (i, count) => {
                        const angle = i / count * Math.PI * 4;
                        const radius = Math.sqrt(i / count) * 25;
                        const armOffset = (i % 3) * Math.PI * 2 / 3;
                        return {
                            x: radius * Math.cos(angle + armOffset),
                            y: (Math.random() - 0.5) * 2,
                            z: radius * Math.sin(angle + armOffset)
                        };
                    }
                },

                morphTo: (shapeName) => {
                    if (this.morphEngine.shapes[shapeName]) {
                        this.targetShape = shapeName;
                        this.morphProgress = 0;
                        this.updateParticleTargets(shapeName);
                    }
                }
            };
        }

        /**
         * Initialize text rendering engine
         */
        initializeTextEngine() {
            // Create offscreen canvas for text rendering
            this.textCanvas = document.createElement('canvas');
            this.textCanvas.width = 512;
            this.textCanvas.height = 256;
            this.textContext = this.textCanvas.getContext('2d');

            this.textEngine = {
                renderText: (text) => {
                    const ctx = this.textContext;
                    const canvas = this.textCanvas;

                    // Clear canvas
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    // Setup text style
                    ctx.fillStyle = 'white';
                    ctx.font = 'bold 48px Inter, sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    // Draw text
                    ctx.fillText(text, canvas.width / 2, canvas.height / 2);

                    // Get pixel data
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const pixels = imageData.data;

                    // Convert to point cloud
                    const points = [];
                    const step = 4; // Sample every 4th pixel

                    for (let y = 0; y < canvas.height; y += step) {
                        for (let x = 0; x < canvas.width; x += step) {
                            const index = (y * canvas.width + x) * 4;
                            const brightness = pixels[index]; // Use red channel

                            if (brightness > 128) {
                                points.push({
                                    x: (x / canvas.width - 0.5) * 40,
                                    y: -(y / canvas.height - 0.5) * 20,
                                    z: (Math.random() - 0.5) * 5
                                });
                            }
                        }
                    }

                    return points;
                },

                morphToText: (text) => {
                    this.currentText = text;
                    const points = this.textEngine.renderText(text);
                    this.applyTextPoints(points);
                }
            };
        }

        /**
         * Initialize voice analysis system
         */
        async initializeVoiceSystem() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                const analyser = audioContext.createAnalyser();

                analyser.fftSize = 2048;
                analyser.smoothingTimeConstant = 0.8;
                source.connect(analyser);

                this.voiceAnalyzer = {
                    analyser: analyser,
                    dataArray: new Uint8Array(analyser.frequencyBinCount),
                    timeArray: new Uint8Array(analyser.frequencyBinCount),

                    analyze: () => {
                        analyser.getByteFrequencyData(this.voiceAnalyzer.dataArray);
                        analyser.getByteTimeDomainData(this.voiceAnalyzer.timeArray);

                        // Calculate voice metrics
                        const data = this.voiceAnalyzer.dataArray;
                        const timeData = this.voiceAnalyzer.timeArray;

                        // Frequency analysis
                        let sum = 0;
                        let maxFreq = 0;
                        for (let i = 0; i < data.length; i++) {
                            sum += data[i];
                            if (data[i] > maxFreq) maxFreq = data[i];
                        }

                        this.voiceData.frequency = sum / data.length / 255;
                        this.voiceData.amplitude = maxFreq / 255;

                        // Volume calculation
                        let rms = 0;
                        for (let i = 0; i < timeData.length; i++) {
                            const normalized = (timeData[i] - 128) / 128;
                            rms += normalized * normalized;
                        }
                        this.voiceData.volume = Math.sqrt(rms / timeData.length);

                        // Pitch detection (simplified)
                        this.voiceData.pitch = this.detectPitch(data);

                        // Intensity (combination of volume and frequency)
                        this.voiceData.intensity = (this.voiceData.volume + this.voiceData.frequency) / 2;

                        // Emotion detection (simplified)
                        this.voiceData.emotion = this.detectEmotion();
                    },

                    detectPitch: (data) => {
                        // Find dominant frequency bin
                        let maxIndex = 0;
                        let maxValue = 0;
                        for (let i = 0; i < data.length / 2; i++) {
                            if (data[i] > maxValue) {
                                maxValue = data[i];
                                maxIndex = i;
                            }
                        }
                        // Normalize to 0-1 range
                        return maxIndex / (data.length / 2);
                    },

                    detectEmotion: () => {
                        const { volume, pitch, frequency } = this.voiceData;

                        if (volume > 0.7 && pitch > 0.6) return 'excited';
                        if (volume < 0.3 && pitch < 0.4) return 'calm';
                        if (frequency > 0.6 && volume > 0.5) return 'happy';
                        if (frequency < 0.4 && volume < 0.4) return 'sad';

                        return 'neutral';
                    }
                };

                console.log('🎤 Voice system initialized');

            } catch (error) {
                console.warn('Voice input not available:', error);
            }
        }

        /**
         * Initialize consciousness integration
         */
        initializeConsciousnessIntegration() {
            // Connect to LUKHAS consciousness systems if available
            if (global.lukhas && global.lukhas.consciousness) {
                this.consciousnessConnection = {
                    update: () => {
                        const state = global.lukhas.consciousness.getState();
                        if (state) {
                            this.consciousnessState = {
                                ...this.consciousnessState,
                                ...state
                            };
                        }
                    }
                };
            }

            // Simulate consciousness states if not connected
            this.consciousnessSimulator = {
                simulate: (deltaTime) => {
                    const time = this.clock.getElapsedTime();

                    // Oscillating awareness
                    this.consciousnessState.awareness = 0.5 + Math.sin(time * 0.5) * 0.3;

                    // Coherence affected by voice
                    if (this.voiceData.intensity > 0) {
                        this.consciousnessState.coherence = Math.min(1, this.consciousnessState.coherence + this.voiceData.intensity * 0.01);
                    } else {
                        this.consciousnessState.coherence *= 0.99; // Decay
                    }

                    // Depth based on complexity
                    this.consciousnessState.depth = 2 + Math.sin(time * 0.3) * 1;

                    // Emotion evolution
                    this.consciousnessState.emotion.valence = 0.5 + Math.sin(time * 0.4) * 0.3;
                    this.consciousnessState.emotion.arousal = this.voiceData.volume;
                    this.consciousnessState.emotion.dominance = this.consciousnessState.coherence;
                }
            };
        }

        /**
         * Update particle targets for shape morphing
         */
        updateParticleTargets(shapeName) {
            const shapeFunction = this.morphEngine.shapes[shapeName];
            if (!shapeFunction) return;

            const count = this.config.particleCount;

            for (let i = 0; i < count; i++) {
                const position = shapeFunction(i, count);
                const i3 = i * 3;

                this.particleTargets[i3] = position.x;
                this.particleTargets[i3 + 1] = position.y;
                this.particleTargets[i3 + 2] = position.z;
            }
        }

        /**
         * Apply text points to particle system
         */
        applyTextPoints(points) {
            const count = this.config.particleCount;
            const pointCount = points.length;

            if (pointCount === 0) return;

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;

                if (i < pointCount) {
                    // Map particle to text point
                    const point = points[i % pointCount];
                    this.particleTargets[i3] = point.x;
                    this.particleTargets[i3 + 1] = point.y;
                    this.particleTargets[i3 + 2] = point.z;
                } else {
                    // Distribute remaining particles around text
                    const point = points[Math.floor(Math.random() * pointCount)];
                    const offset = 5;
                    this.particleTargets[i3] = point.x + (Math.random() - 0.5) * offset;
                    this.particleTargets[i3 + 1] = point.y + (Math.random() - 0.5) * offset;
                    this.particleTargets[i3 + 2] = point.z + (Math.random() - 0.5) * offset;
                }
            }

            this.morphProgress = 0;
        }

        /**
         * Setup interactive controls
         */
        setupControls() {
            // Orbit controls for camera
            if (typeof THREE.OrbitControls !== 'undefined') {
                this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
                this.controls.enableDamping = true;
                this.controls.dampingFactor = 0.05;
                this.controls.minDistance = 20;
                this.controls.maxDistance = 100;
            }

            // Mouse interaction
            this.mouse = new THREE.Vector2();
            this.raycaster = new THREE.Raycaster();

            this.renderer.domElement.addEventListener('mousemove', (event) => {
                const rect = this.renderer.domElement.getBoundingClientRect();
                this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

                // Update consciousness attention based on mouse
                this.consciousnessState.attention = Math.sqrt(this.mouse.x * this.mouse.x + this.mouse.y * this.mouse.y);
            });
        }

        /**
         * Setup user interface
         */
        setupUI() {
            const ui = document.createElement('div');
            ui.id = 'lukhas-unified-ui';
            ui.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1000;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
                color: white;
                font-family: 'Inter', sans-serif;
                min-width: 300px;
            `;

            ui.innerHTML = `
                <h3 style="margin: 0 0 15px 0; color: #00d4ff;">LUKHAS Consciousness Visualizer</h3>

                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #aaa;">Shape Morph</label>
                    <select id="shape-select" style="width: 100%; padding: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white;">
                        <option value="sphere">Sphere</option>
                        <option value="cube">Cube</option>
                        <option value="torus">Torus</option>
                        <option value="helix">Helix</option>
                        <option value="heart">Heart</option>
                        <option value="dna">DNA</option>
                        <option value="galaxy">Galaxy</option>
                    </select>
                </div>

                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #aaa;">Text Shape</label>
                    <input type="text" id="text-input" placeholder="Enter text..." style="width: 100%; padding: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: white;">
                </div>

                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-size: 12px; color: #aaa;">Morph Speed</label>
                    <input type="range" id="speed-slider" min="0.001" max="0.1" step="0.001" value="0.02" style="width: 100%;">
                </div>

                <div id="consciousness-display" style="font-size: 11px; color: #aaa; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; margin-top: 10px;">
                    <div>Awareness: <span id="awareness">0.5</span></div>
                    <div>Coherence: <span id="coherence">0.5</span></div>
                    <div>Voice Intensity: <span id="voice-intensity">0</span></div>
                </div>
            `;

            document.body.appendChild(ui);

            // Wire up controls
            document.getElementById('shape-select').addEventListener('change', (e) => {
                this.morphEngine.morphTo(e.target.value);
            });

            document.getElementById('text-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.textEngine.morphToText(e.target.value);
                }
            });

            document.getElementById('speed-slider').addEventListener('input', (e) => {
                this.morphSpeed = parseFloat(e.target.value);
            });
        }

        /**
         * Main animation loop
         */
        animate() {
            requestAnimationFrame(() => this.animate());

            const deltaTime = this.clock.getDelta();
            const elapsedTime = this.clock.getElapsedTime();

            // Update voice analysis
            if (this.voiceAnalyzer) {
                this.voiceAnalyzer.analyze();
            }

            // Update consciousness
            if (this.consciousnessConnection) {
                this.consciousnessConnection.update();
            } else {
                this.consciousnessSimulator.simulate(deltaTime);
            }

            // Update particles
            this.updateParticles(deltaTime, elapsedTime);

            // Update lights
            this.updateLights(elapsedTime);

            // Update controls
            if (this.controls) {
                this.controls.update();
            }

            // Update UI
            this.updateUI();

            // Render
            this.renderer.render(this.scene, this.camera);

            this.frameCount++;
        }

        /**
         * Update particle positions and properties
         */
        updateParticles(deltaTime, elapsedTime) {
            // Update morph progress
            this.morphProgress = Math.min(1, this.morphProgress + this.morphSpeed);

            const positions = this.particleGeometry.attributes.position.array;
            const colors = this.particleGeometry.attributes.color.array;
            const count = this.config.particleCount;

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;

                // Morph to target position
                const targetX = this.particleTargets[i3];
                const targetY = this.particleTargets[i3 + 1];
                const targetZ = this.particleTargets[i3 + 2];

                // Smooth interpolation with easing
                const t = this.easeInOutCubic(this.morphProgress);

                positions[i3] += (targetX - positions[i3]) * t * 0.1;
                positions[i3 + 1] += (targetY - positions[i3 + 1]) * t * 0.1;
                positions[i3 + 2] += (targetZ - positions[i3 + 2]) * t * 0.1;

                // Apply voice influence
                if (this.voiceData.intensity > 0) {
                    const voiceInfluence = this.voiceData.intensity * 0.5;
                    positions[i3] += Math.sin(elapsedTime * 2 + i * 0.01) * voiceInfluence;
                    positions[i3 + 1] += Math.cos(elapsedTime * 2 + i * 0.01) * voiceInfluence;
                    positions[i3 + 2] += Math.sin(elapsedTime * 3 + i * 0.01) * voiceInfluence;
                }

                // Apply consciousness influence on colors
                const hue = 0.5 + this.consciousnessState.awareness * 0.3 + Math.sin(elapsedTime + i * 0.01) * 0.1;
                const saturation = 0.6 + this.consciousnessState.coherence * 0.4;
                const lightness = 0.5 + this.voiceData.intensity * 0.3;

                const color = new THREE.Color().setHSL(hue, saturation, lightness);
                colors[i3] = color.r;
                colors[i3 + 1] = color.g;
                colors[i3 + 2] = color.b;

                // Apply velocities with damping
                this.particleVelocities[i3] *= 0.98;
                this.particleVelocities[i3 + 1] *= 0.98;
                this.particleVelocities[i3 + 2] *= 0.98;

                positions[i3] += this.particleVelocities[i3];
                positions[i3 + 1] += this.particleVelocities[i3 + 1];
                positions[i3 + 2] += this.particleVelocities[i3 + 2];
            }

            // Update geometry
            this.particleGeometry.attributes.position.needsUpdate = true;
            this.particleGeometry.attributes.color.needsUpdate = true;

            // Rotate particle system
            this.particleSystem.rotation.y += 0.001;
        }

        /**
         * Update dynamic lighting based on consciousness state
         */
        updateLights(elapsedTime) {
            // Consciousness light pulses
            this.consciousnessLight.intensity = 0.8 + Math.sin(elapsedTime * 2) * 0.2 * this.consciousnessState.awareness;
            this.consciousnessLight.color.setHSL(0.5 + this.consciousnessState.coherence * 0.2, 0.8, 0.5);

            // Identity light responds to voice
            this.identityLight.intensity = 0.6 + this.voiceData.intensity * 0.4;

            // Guardian light stabilizes
            this.guardianLight.intensity = 0.6 + this.consciousnessState.coherence * 0.4;
        }

        /**
         * Update UI displays
         */
        updateUI() {
            if (this.frameCount % 10 === 0) { // Update every 10 frames
                const awarenessEl = document.getElementById('awareness');
                const coherenceEl = document.getElementById('coherence');
                const voiceEl = document.getElementById('voice-intensity');

                if (awarenessEl) awarenessEl.textContent = this.consciousnessState.awareness.toFixed(2);
                if (coherenceEl) coherenceEl.textContent = this.consciousnessState.coherence.toFixed(2);
                if (voiceEl) voiceEl.textContent = this.voiceData.intensity.toFixed(2);
            }
        }

        /**
         * Easing function for smooth animations
         */
        easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }

        /**
         * Start animation loop
         */
        startAnimation() {
            this.animate();
        }

        /**
         * Handle window resize
         */
        handleResize() {
            const container = document.getElementById(this.config.containerId);
            const width = container ? container.clientWidth : window.innerWidth;
            const height = container ? container.clientHeight : window.innerHeight;

            this.camera.aspect = width / height;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(width, height);
        }

        /**
         * Public API Methods
         */

        /**
         * Morph to a named shape
         */
        morphToShape(shapeName) {
            this.morphEngine.morphTo(shapeName);
        }

        /**
         * Morph to text representation
         */
        morphToText(text) {
            this.textEngine.morphToText(text);
        }

        /**
         * Update consciousness state
         */
        updateConsciousnessState(state) {
            this.consciousnessState = {
                ...this.consciousnessState,
                ...state
            };
        }

        /**
         * Get current state
         */
        getState() {
            return {
                currentShape: this.currentShape,
                targetShape: this.targetShape,
                morphProgress: this.morphProgress,
                voiceData: this.voiceData,
                consciousnessState: this.consciousnessState,
                particleCount: this.config.particleCount,
                fps: this.frameCount / this.clock.getElapsedTime()
            };
        }

        /**
         * Cleanup and destroy
         */
        destroy() {
            // Stop animation
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }

            // Dispose Three.js resources
            if (this.particleGeometry) this.particleGeometry.dispose();
            if (this.particleMaterial) this.particleMaterial.dispose();
            if (this.renderer) this.renderer.dispose();

            // Remove DOM elements
            const ui = document.getElementById('lukhas-unified-ui');
            if (ui) ui.remove();

            if (this.renderer && this.renderer.domElement) {
                this.renderer.domElement.remove();
            }

            console.log('LUKHAS Visualizer destroyed');
        }
    }

    // Export for use
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = UnifiedConsciousnessVisualizer;
    }

    // Make available globally
    global.UnifiedConsciousnessVisualizer = UnifiedConsciousnessVisualizer;
    global.LUKHASVisualizer = UnifiedConsciousnessVisualizer; // Alias

})(typeof window !== 'undefined' ? window : globalThis);
