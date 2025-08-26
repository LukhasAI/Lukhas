// Voice-Modulated Morphing System
class MorphingSystem {
    constructor() {
        this.currentShape = 'default';
        this.targetShape = 'default';
        this.voiceData = {
            intensity: 0,
            frequency: 0
        };
        this.morphProgress = 0;
        this.morphSpeed = 0.02;

        // Shape definitions for different morphs
        this.shapeDefinitions = {
            default: {
                name: 'Default Sphere',
                vertexModifier: (vertex, time, voiceData) => {
                    // Default spherical shape with subtle voice modulation
                    const radius = 10.0 + voiceData.intensity * 0.1;
                    const normalized = this.normalizeVector(vertex);
                    return {
                        x: normalized.x * radius,
                        y: normalized.y * radius,
                        z: normalized.z * radius
                    };
                }
            },

            cat: {
                name: 'Cat Shape',
                vertexModifier: (vertex, time, voiceData) => {
                    const normalized = this.normalizeVector(vertex);
                    const radius = 10.0 + voiceData.intensity * 0.2;

                    // Cat-like features
                    let x = normalized.x * radius;
                    let y = normalized.y * radius;
                    let z = normalized.z * radius;

                    // Pointed ears (top vertices)
                    if (y > 0.7) {
                        x *= 0.8;
                        z *= 0.8;
                        y *= 1.3;
                    }

                    // Elongated body
                    if (Math.abs(y) < 0.3) {
                        x *= 1.2;
                        z *= 1.2;
                    }

                    // Tail (bottom vertices)
                    if (y < -0.7) {
                        x *= 0.6;
                        z *= 0.6;
                        y *= 1.5;
                    }

                    // Voice modulation - cat purring effect
                    const purr = Math.sin(time * 20 + voiceData.frequency * 0.01) * voiceData.intensity * 0.1;
                    x += purr * normalized.x;
                    y += purr * normalized.y;
                    z += purr * normalized.z;

                    return { x, y, z };
                }
            },

            car: {
                name: 'Car Shape',
                vertexModifier: (vertex, time, voiceData) => {
                    const normalized = this.normalizeVector(vertex);
                    const radius = 10.0 + voiceData.intensity * 0.15;

                    let x = normalized.x * radius;
                    let y = normalized.y * radius;
                    let z = normalized.z * radius;

                    // Car body - elongated and flattened
                    if (Math.abs(y) < 0.4) {
                        x *= 1.8; // Wider
                        z *= 1.4; // Longer
                        y *= 0.6; // Flatter
                    }

                    // Wheels (side vertices)
                    if (Math.abs(x) > 0.7) {
                        x *= 1.1;
                        y *= 0.8;
                        z *= 0.9;
                    }

                    // Hood and trunk
                    if (z > 0.5) {
                        x *= 0.9;
                        y *= 0.8;
                        z *= 1.2;
                    }

                    // Engine vibration effect
                    const vibration = Math.sin(time * 50 + voiceData.frequency * 0.02) * voiceData.intensity * 0.05;
                    x += vibration * normalized.x;
                    y += vibration * normalized.y;
                    z += vibration * normalized.z;

                    return { x, y, z };
                }
            },

            person: {
                name: 'Person Shape',
                vertexModifier: (vertex, time, voiceData) => {
                    const normalized = this.normalizeVector(vertex);
                    const radius = 10.0 + voiceData.intensity * 0.12;

                    let x = normalized.x * radius;
                    let y = normalized.y * radius;
                    let z = normalized.z * radius;

                    // Head (top vertices)
                    if (y > 0.6) {
                        x *= 0.9;
                        z *= 0.9;
                        y *= 1.1;
                    }

                    // Torso (middle section)
                    if (Math.abs(y) < 0.3) {
                        x *= 1.1;
                        z *= 1.0;
                        y *= 1.2;
                    }

                    // Arms (side vertices)
                    if (Math.abs(x) > 0.8 && Math.abs(y) < 0.4) {
                        x *= 1.3;
                        y *= 0.9;
                        z *= 0.8;
                    }

                    // Legs (bottom vertices)
                    if (y < -0.5) {
                        x *= 0.8;
                        z *= 0.8;
                        y *= 1.4;
                    }

                    // Breathing effect
                    const breath = Math.sin(time * 2 + voiceData.frequency * 0.005) * voiceData.intensity * 0.08;
                    x += breath * normalized.x;
                    y += breath * normalized.y;
                    z += breath * normalized.z;

                    return { x, y, z };
                }
            }
        };

        this.init();
    }

    init() {
        // Wait for the main WebGL system to be ready
        this.waitForWebGLSystem();
    }

    waitForWebGLSystem() {
        const checkSystem = () => {
            if (window.gl && window.icosahedronData) {
                this.setupMorphing();
            } else {
                setTimeout(checkSystem, 100);
            }
        };
        checkSystem();
    }

    setupMorphing() {
        // Hook into the existing WebGL system
        this.hookIntoExistingSystem();

        // Set up the morphing system
        this.startMorphingLoop();

        console.log('Morphing system initialized');
    }

    hookIntoExistingSystem() {
        // Store reference to the existing system
        this.gl = window.gl;
        this.icosahedronData = window.icosahedronData;

        // Override the vertex processing to include our morphing
        this.originalVertexProcessing = window.processVertices || this.defaultVertexProcessing;
        window.processVertices = this.processVerticesWithMorphing.bind(this);

        // Make the system globally accessible
        window.morphSystem = this;
    }

    processVerticesWithMorphing(vertices, time) {
        const morphedVertices = [];

        for (let i = 0; i < vertices.length; i += 3) {
            const vertex = {
                x: vertices[i],
                y: vertices[i + 1],
                z: vertices[i + 2]
            };

            // Apply morphing based on current and target shapes
            const morphedVertex = this.applyMorphing(vertex, time);

            morphedVertices.push(morphedVertex.x, morphedVertex.y, morphedVertex.z);
        }

        return morphedVertices;
    }

    applyMorphing(vertex, time) {
        const currentShapeDef = this.shapeDefinitions[this.currentShape];
        const targetShapeDef = this.shapeDefinitions[this.targetShape];

        // Get current and target vertex positions
        const currentPos = currentShapeDef.vertexModifier(vertex, time, this.voiceData);
        const targetPos = targetShapeDef.vertexModifier(vertex, time, this.voiceData);

        // Interpolate between current and target
        const morphedVertex = {
            x: currentPos.x + (targetPos.x - currentPos.x) * this.morphProgress,
            y: currentPos.y + (targetPos.y - currentPos.y) * this.morphProgress,
            z: currentPos.z + (targetPos.z - currentPos.z) * this.morphProgress
        };

        return morphedVertex;
    }

    startMorphingLoop() {
        const morphLoop = () => {
            // Update morph progress
            if (this.currentShape !== this.targetShape) {
                this.morphProgress += this.morphSpeed;
                if (this.morphProgress >= 1.0) {
                    this.morphProgress = 1.0;
                    this.currentShape = this.targetShape;
                }
            }

            // Continue the loop
            requestAnimationFrame(morphLoop);
        };

        morphLoop();
    }

    setVoiceData(voiceData) {
        this.voiceData = {
            intensity: voiceData.intensity || 0,
            frequency: voiceData.frequency || 0
        };
    }

    setTargetShape(shape) {
        if (this.shapeDefinitions[shape]) {
            this.targetShape = shape;
            this.morphProgress = 0;
        }
    }

    normalizeVector(vector) {
        const length = Math.sqrt(vector.x * vector.x + vector.y * vector.y + vector.z * vector.z);
        return {
            x: vector.x / length,
            y: vector.y / length,
            z: vector.z / length
        };
    }

    defaultVertexProcessing(vertices, time) {
        return vertices;
    }

    getCurrentShapeInfo() {
        return this.shapeDefinitions[this.currentShape];
    }
}

// Initialize the morphing system when the script loads
window.addEventListener('DOMContentLoaded', () => {
    window.morphingSystem = new MorphingSystem();
});
