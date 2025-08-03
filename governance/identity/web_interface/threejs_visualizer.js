/**
 * LUKHAS Three.js Visualizer - 3D Particle Authentication Interface
 * 
 * This module implements 3D particle visualization for LUKHAS authentication
 * using Three.js. It creates consciousness-aware particle systems that respond
 * to user entropy and cognitive state.
 * 
 * Author: LUKHAS Team
 * Date: June 2025
 * Purpose: 3D consciousness-aware authentication visualization
 */

class LukhAsThreeJSVisualizer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container element with id '${containerId}' not found`);
        }
        
        this.options = {
            particleCount: options.particleCount || 1000,
            consciousnessMode: options.consciousnessMode || true,
            quantumEffects: options.quantumEffects || true,
            interactiveParticles: options.interactiveParticles || true,
            responsiveToEntropy: options.responsiveToEntropy || true,
            neuralPatterns: options.neuralPatterns || true,
            ...options
        };
        
        // Three.js core objects
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.animationId = null;
        
        // Particle systems
        this.particleSystem = null;
        this.neuralNetwork = null;
        this.quantumField = null;
        
        // Consciousness state tracking
        this.consciousnessState = {
            awareness: 0.5,
            attention: 0.5,
            cognitive_load: 0.3,
            entropy_level: 0.0
        };
        
        // Animation state
        this.clock = null;
        this.mouse = { x: 0, y: 0 };
        this.isInitialized = false;
        
        // Check Three.js availability
        if (typeof THREE === 'undefined') {
            console.error('Three.js library not found. Please include Three.js before using LukhAsThreeJSVisualizer');
            return;
        }
        
        this.initialize();
    }
    
    /**
     * Initialize the Three.js visualization
     */
    initialize() {
        try {
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.setupLighting();
            this.setupParticleSystems();
            this.setupInteraction();
            this.startAnimation();
            
            this.isInitialized = true;
            console.log('LUKHAS Three.js Visualizer initialized');
        } catch (error) {
            console.error('Failed to initialize Three.js visualizer:', error);
        }
    }
    
    /**
     * Setup the Three.js scene
     */
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a); // Deep space background
        this.scene.fog = new THREE.Fog(0x0a0a0a, 50, 200);
        
        this.clock = new THREE.Clock();
    }
    
    /**
     * Setup the camera
     */
    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
        this.camera.position.set(0, 0, 50);
        this.camera.lookAt(0, 0, 0);
    }
    
    /**
     * Setup the WebGL renderer
     */
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true,
            powerPreference: 'high-performance'
        });
        
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        this.container.appendChild(this.renderer.domElement);
        
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    /**
     * Setup lighting for the scene
     */
    setupLighting() {
        // Ambient light for general illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        this.scene.add(ambientLight);
        
        // Dynamic consciousness light
        this.consciousnessLight = new THREE.PointLight(0x00ffff, 1, 100);
        this.consciousnessLight.position.set(0, 20, 10);
        this.consciousnessLight.castShadow = true;
        this.scene.add(this.consciousnessLight);
        
        // Entropy directional light
        this.entropyLight = new THREE.DirectionalLight(0xff6b6b, 0.5);
        this.entropyLight.position.set(-10, 10, 5);
        this.scene.add(this.entropyLight);
    }
    
    /**
     * Setup particle systems for consciousness visualization
     */
    setupParticleSystems() {
        this.createMainParticleSystem();
        
        if (this.options.neuralPatterns) {
            this.createNeuralNetwork();
        }
        
        if (this.options.quantumEffects) {
            this.createQuantumField();
        }
    }
    
    /**
     * Create main particle system representing consciousness
     */
    createMainParticleSystem() {
        const particleCount = this.options.particleCount;
        const geometry = new THREE.BufferGeometry();
        
        // Create particle positions
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);
        const velocities = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            
            // Random positions in sphere
            const radius = Math.random() * 30 + 10;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = radius * Math.cos(phi);
            
            // Consciousness-based colors (cyan to magenta spectrum)
            const hue = (Math.random() * 0.3) + 0.5; // 0.5-0.8 range
            const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
            
            // Random sizes
            sizes[i] = Math.random() * 2 + 0.5;
            
            // Initial velocities
            velocities[i3] = (Math.random() - 0.5) * 0.02;
            velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
            velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        // Store velocities for animation
        geometry.velocities = velocities;
        
        // Create particle material
        const material = new THREE.PointsMaterial({
            size: 1.5,
            sizeAttenuation: true,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });
        
        this.particleSystem = new THREE.Points(geometry, material);
        this.scene.add(this.particleSystem);
    }
    
    /**
     * Create neural network visualization
     */
    createNeuralNetwork() {
        const nodeCount = 20;
        const nodes = [];
        
        // Create neural nodes
        for (let i = 0; i < nodeCount; i++) {
            const geometry = new THREE.SphereGeometry(0.5, 8, 8);
            const material = new THREE.MeshBasicMaterial({ 
                color: 0x00ffaa,
                transparent: true,
                opacity: 0.7
            });
            
            const node = new THREE.Mesh(geometry, material);
            
            // Position nodes in 3D space
            const angle = (i / nodeCount) * Math.PI * 2;
            const layer = Math.floor(i / 5);
            node.position.set(
                Math.cos(angle) * (15 + layer * 5),
                Math.sin(angle) * (15 + layer * 5),
                (layer - 2) * 8
            );
            
            nodes.push(node);
            this.scene.add(node);
        }
        
        // Create connections between nodes
        this.createNeuralConnections(nodes);
        
        this.neuralNodes = nodes;
    }
    
    /**
     * Create connections between neural nodes
     */
    createNeuralConnections(nodes) {
        const connections = [];
        
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                // Connect nodes based on proximity and randomness
                const distance = nodes[i].position.distanceTo(nodes[j].position);
                
                if (distance < 25 && Math.random() > 0.7) {
                    const geometry = new THREE.BufferGeometry();
                    const positions = new Float32Array([
                        nodes[i].position.x, nodes[i].position.y, nodes[i].position.z,
                        nodes[j].position.x, nodes[j].position.y, nodes[j].position.z
                    ]);
                    
                    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                    
                    const material = new THREE.LineBasicMaterial({ 
                        color: 0x0088ff,
                        transparent: true,
                        opacity: 0.3
                    });
                    
                    const connection = new THREE.Line(geometry, material);
                    connections.push(connection);
                    this.scene.add(connection);
                }
            }
        }
        
        this.neuralConnections = connections;
    }
    
    /**
     * Create quantum field visualization
     */
    createQuantumField() {
        const fieldGeometry = new THREE.PlaneGeometry(100, 100, 32, 32);
        const fieldMaterial = new THREE.MeshBasicMaterial({
            color: 0x4444ff,
            transparent: true,
            opacity: 0.2,
            wireframe: true,
            side: THREE.DoubleSide
        });
        
        this.quantumField = new THREE.Mesh(fieldGeometry, fieldMaterial);
        this.quantumField.rotation.x = -Math.PI / 2;
        this.quantumField.position.y = -20;
        this.scene.add(this.quantumField);
    }
    
    /**
     * Setup mouse and touch interaction
     */
    setupInteraction() {
        const canvas = this.renderer.domElement;
        
        // Mouse movement tracking
        canvas.addEventListener('mousemove', (event) => {
            const rect = canvas.getBoundingClientRect();
            this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            
            this.onMouseMove(this.mouse);
        });
        
        // Touch interaction for mobile
        canvas.addEventListener('touchmove', (event) => {
            event.preventDefault();
            const touch = event.touches[0];
            const rect = canvas.getBoundingClientRect();
            
            this.mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
            this.mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
            
            this.onMouseMove(this.mouse);
        });
    }
    
    /**
     * Handle mouse movement for particle interaction
     */
    onMouseMove(mouse) {
        if (!this.options.interactiveParticles || !this.particleSystem) return;
        
        // Update consciousness state based on mouse movement
        this.consciousnessState.attention = Math.min(1.0, this.consciousnessState.attention + 0.01);
        
        // Create attraction force toward mouse position
        const mouseVector = new THREE.Vector3(mouse.x * 30, mouse.y * 30, 0);
        this.attractParticlesToPoint(mouseVector);
    }
    
    /**
     * Attract particles to a specific point
     */
    attractParticlesToPoint(targetPoint) {
        const positions = this.particleSystem.geometry.attributes.position.array;
        const velocities = this.particleSystem.geometry.velocities;
        
        for (let i = 0; i < positions.length; i += 3) {
            const particlePos = new THREE.Vector3(positions[i], positions[i + 1], positions[i + 2]);
            const distance = particlePos.distanceTo(targetPoint);
            
            if (distance < 20) {
                const force = targetPoint.clone().sub(particlePos).normalize().multiplyScalar(0.001);
                velocities[i] += force.x;
                velocities[i + 1] += force.y;
                velocities[i + 2] += force.z;
            }
        }
    }
    
    /**
     * Update consciousness state
     */
    updateConsciousnessState(newState) {
        this.consciousnessState = { ...this.consciousnessState, ...newState };
        
        // Update visual elements based on consciousness state
        this.updateVisualsFromConsciousness();
    }
    
    /**
     * Update visuals based on consciousness state
     */
    updateVisualsFromConsciousness() {
        if (!this.isInitialized) return;
        
        const { awareness, attention, cognitive_load, entropy_level } = this.consciousnessState;
        
        // Update consciousness light intensity and color
        if (this.consciousnessLight) {
            this.consciousnessLight.intensity = 0.5 + awareness * 0.5;
            this.consciousnessLight.color.setHSL(0.5 + attention * 0.2, 0.8, 0.5);
        }
        
        // Update particle colors based on cognitive load
        if (this.particleSystem) {
            const colors = this.particleSystem.geometry.attributes.color.array;
            
            for (let i = 0; i < colors.length; i += 3) {
                const hue = 0.5 + (cognitive_load * 0.3) + (Math.sin(Date.now() * 0.001 + i) * 0.1);
                const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
                
                colors[i] = color.r;
                colors[i + 1] = color.g;
                colors[i + 2] = color.b;
            }
            
            this.particleSystem.geometry.attributes.color.needsUpdate = true;
        }
        
        // Update neural network activity
        if (this.neuralNodes) {
            this.neuralNodes.forEach((node, index) => {
                const activity = awareness + (Math.sin(Date.now() * 0.002 + index) * 0.3);
                node.material.opacity = Math.max(0.3, Math.min(1.0, activity));
            });
        }
    }
    
    /**
     * Start the animation loop
     */
    startAnimation() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            
            const deltaTime = this.clock.getDelta();
            const elapsedTime = this.clock.getElapsedTime();
            
            this.updateParticles(deltaTime, elapsedTime);
            this.updateNeuralNetwork(elapsedTime);
            this.updateQuantumField(elapsedTime);
            this.updateCamera(elapsedTime);
            
            this.renderer.render(this.scene, this.camera);
        };
        
        animate();
    }
    
    /**
     * Update particle system animation
     */
    updateParticles(deltaTime, elapsedTime) {
        if (!this.particleSystem) return;
        
        const positions = this.particleSystem.geometry.attributes.position.array;
        const velocities = this.particleSystem.geometry.velocities;
        const sizes = this.particleSystem.geometry.attributes.size.array;
        
        for (let i = 0; i < positions.length; i += 3) {
            // Apply velocities
            positions[i] += velocities[i];
            positions[i + 1] += velocities[i + 1];
            positions[i + 2] += velocities[i + 2];
            
            // Apply consciousness-based forces
            const consciousnessForce = Math.sin(elapsedTime + i * 0.01) * 0.001 * this.consciousnessState.awareness;
            velocities[i + 1] += consciousnessForce;
            
            // Boundary checking - keep particles in view
            const maxDistance = 40;
            const distance = Math.sqrt(positions[i] ** 2 + positions[i + 1] ** 2 + positions[i + 2] ** 2);
            
            if (distance > maxDistance) {
                velocities[i] *= -0.1;
                velocities[i + 1] *= -0.1;
                velocities[i + 2] *= -0.1;
            }
            
            // Apply damping
            velocities[i] *= 0.99;
            velocities[i + 1] *= 0.99;
            velocities[i + 2] *= 0.99;
            
            // Update particle sizes based on entropy
            const baseSize = 0.5 + this.consciousnessState.entropy_level;
            sizes[i / 3] = baseSize + Math.sin(elapsedTime * 2 + i) * 0.2;
        }
        
        this.particleSystem.geometry.attributes.position.needsUpdate = true;
        this.particleSystem.geometry.attributes.size.needsUpdate = true;
        
        // Rotate particle system slowly
        this.particleSystem.rotation.y += 0.001;
    }
    
    /**
     * Update neural network animation
     */
    updateNeuralNetwork(elapsedTime) {
        if (!this.neuralNodes) return;
        
        this.neuralNodes.forEach((node, index) => {
            // Pulse based on consciousness state
            const pulse = 1 + Math.sin(elapsedTime * 3 + index * 0.5) * 0.2 * this.consciousnessState.awareness;
            node.scale.setScalar(pulse);
            
            // Gentle floating motion
            node.position.y += Math.sin(elapsedTime + index) * 0.01;
        });
        
        // Update neural connections opacity
        if (this.neuralConnections) {
            this.neuralConnections.forEach((connection, index) => {
                const activity = this.consciousnessState.attention + Math.sin(elapsedTime * 2 + index) * 0.2;
                connection.material.opacity = Math.max(0.1, Math.min(0.6, activity));
            });
        }
    }
    
    /**
     * Update quantum field animation
     */
    updateQuantumField(elapsedTime) {
        if (!this.quantumField) return;
        
        // Subtle rotation and scale pulsing
        this.quantumField.rotation.z += 0.0005;
        
        const scale = 1 + Math.sin(elapsedTime * 0.5) * 0.1 * this.consciousnessState.entropy_level;
        this.quantumField.scale.setScalar(scale);
        
        // Update material opacity based on consciousness
        this.quantumField.material.opacity = 0.1 + this.consciousnessState.awareness * 0.2;
    }
    
    /**
     * Update camera position and movement
     */
    updateCamera(elapsedTime) {
        // Gentle camera movement for dynamic view
        const radius = 50;
        const speed = 0.1;
        
        this.camera.position.x = Math.cos(elapsedTime * speed) * radius * 0.2;
        this.camera.position.z = radius + Math.sin(elapsedTime * speed * 0.7) * 10;
        
        this.camera.lookAt(0, 0, 0);
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        if (!this.isInitialized) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }
    
    /**
     * Get current visualization state
     */
    getVisualizationState() {
        return {
            isInitialized: this.isInitialized,
            consciousnessState: this.consciousnessState,
            particleCount: this.options.particleCount,
            neuralNodesCount: this.neuralNodes ? this.neuralNodes.length : 0,
            renderInfo: this.renderer ? this.renderer.info : null
        };
    }
    
    /**
     * Cleanup and destroy the visualizer
     */
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
            if (this.renderer.domElement && this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
        }
        
        // Clean up geometries and materials
        this.scene?.traverse((object) => {
            if (object.geometry) object.geometry.dispose();
            if (object.material) {
                if (object.material.map) object.material.map.dispose();
                object.material.dispose();
            }
        });
        
        console.log('LUKHAS Three.js Visualizer destroyed');
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LukhAsThreeJSVisualizer;
}

// Global availability for direct HTML inclusion
if (typeof window !== 'undefined') {
    window.LukhAsThreeJSVisualizer = LukhAsThreeJSVisualizer;
}
