// Shader Modification System for Voice-Modulated Morphing
class ShaderModificationSystem {
    constructor() {
        this.voiceUniforms = {
            uVoiceIntensity: 0.0,
            uVoiceFrequency: 0.0,
            uMorphProgress: 0.0,
            uTargetShape: 0.0 // 0=default, 1=cat, 2=car, 3=person
        };

        this.originalShaders = {};
        this.modifiedShaders = {};

        this.init();
    }

    init() {
        // Wait for the WebGL system to be ready
        this.waitForWebGLSystem();
    }

    waitForWebGLSystem() {
        const checkSystem = () => {
            if (window.gl) {
                this.setupShaderModifications();
            } else {
                setTimeout(checkSystem, 100);
            }
        };
        checkSystem();
    }

    setupShaderModifications() {
        this.gl = window.gl;

        // Hook into the shader creation process
        this.hookIntoShaderSystem();

        // Set up uniform locations
        this.setupUniforms();

        console.log('Shader modification system initialized');
    }

    hookIntoShaderSystem() {
        // Store original shader functions
        this.originalCreateProgram = window.createProgram || this.gl.createProgram;
        this.originalUseProgram = window.useProgram || this.gl.useProgram;

        // Override shader creation to inject our modifications
        window.createProgram = this.createModifiedProgram.bind(this);
        window.useProgram = this.useModifiedProgram.bind(this);
    }

    createModifiedProgram(vertexSource, fragmentSource) {
        // Inject voice modulation code into vertex shader
        const modifiedVertexSource = this.injectVoiceModulation(vertexSource);

        // Create the program with modified shaders
        const program = this.originalCreateProgram(modifiedVertexSource, fragmentSource);

        // Store the program for later uniform updates
        this.modifiedShaders[program] = {
            vertexSource: modifiedVertexSource,
            fragmentSource: fragmentSource
        };

        return program;
    }

    injectVoiceModulation(vertexSource) {
        // Add voice modulation uniforms
        const uniformDeclarations = `
            uniform float uVoiceIntensity;
            uniform float uVoiceFrequency;
            uniform float uMorphProgress;
            uniform float uTargetShape;
        `;

        // Add voice modulation functions
        const voiceFunctions = `
            vec3 applyVoiceModulation(vec3 position, float time) {
                vec3 modulated = position;

                // Voice intensity affects overall scale
                float voiceScale = 1.0 + uVoiceIntensity * 0.2;
                modulated *= voiceScale;

                // Voice frequency creates subtle vibration
                float vibration = sin(time * 50.0 + uVoiceFrequency * 0.01) * uVoiceIntensity * 0.05;
                modulated += normalize(position) * vibration;

                return modulated;
            }

            vec3 applyShapeMorphing(vec3 position) {
                vec3 morphed = position;

                if (uTargetShape > 0.5) {
                    // Cat shape
                    if (uTargetShape < 1.5) {
                        vec3 normalized = normalize(position);
                        float y = normalized.y;

                        // Pointed ears
                        if (y > 0.7) {
                            morphed.x *= 0.8;
                            morphed.z *= 0.8;
                            morphed.y *= 1.3;
                        }

                        // Elongated body
                        if (abs(y) < 0.3) {
                            morphed.x *= 1.2;
                            morphed.z *= 1.2;
                        }

                        // Tail
                        if (y < -0.7) {
                            morphed.x *= 0.6;
                            morphed.z *= 0.6;
                            morphed.y *= 1.5;
                        }
                    }
                    // Car shape
                    else if (uTargetShape < 2.5) {
                        vec3 normalized = normalize(position);
                        float y = normalized.y;
                        float x = normalized.x;
                        float z = normalized.z;

                        // Car body
                        if (abs(y) < 0.4) {
                            morphed.x *= 1.8;
                            morphed.z *= 1.4;
                            morphed.y *= 0.6;
                        }

                        // Wheels
                        if (abs(x) > 0.7) {
                            morphed.x *= 1.1;
                            morphed.y *= 0.8;
                            morphed.z *= 0.9;
                        }

                        // Hood and trunk
                        if (z > 0.5) {
                            morphed.x *= 0.9;
                            morphed.y *= 0.8;
                            morphed.z *= 1.2;
                        }
                    }
                    // Person shape
                    else if (uTargetShape < 3.5) {
                        vec3 normalized = normalize(position);
                        float y = normalized.y;
                        float x = normalized.x;

                        // Head
                        if (y > 0.6) {
                            morphed.x *= 0.9;
                            morphed.z *= 0.9;
                            morphed.y *= 1.1;
                        }

                        // Torso
                        if (abs(y) < 0.3) {
                            morphed.x *= 1.1;
                            morphed.z *= 1.0;
                            morphed.y *= 1.2;
                        }

                        // Arms
                        if (abs(x) > 0.8 && abs(y) < 0.4) {
                            morphed.x *= 1.3;
                            morphed.y *= 0.9;
                            morphed.z *= 0.8;
                        }

                        // Legs
                        if (y < -0.5) {
                            morphed.x *= 0.8;
                            morphed.z *= 0.8;
                            morphed.y *= 1.4;
                        }
                    }
                }

                return morphed;
            }
        `;

        // Find the main function and inject our modifications
        let modifiedSource = vertexSource;

        // Add uniform declarations after existing uniforms
        const uniformMatch = modifiedSource.match(/uniform[^;]+;/g);
        if (uniformMatch) {
            const lastUniform = uniformMatch[uniformMatch.length - 1];
            const insertIndex = modifiedSource.lastIndexOf(lastUniform) + lastUniform.length;
            modifiedSource = modifiedSource.slice(0, insertIndex) + '\n' + uniformDeclarations + modifiedSource.slice(insertIndex);
        } else {
            // If no uniforms found, add at the beginning
            modifiedSource = uniformDeclarations + '\n' + modifiedSource;
        }

        // Add voice functions before the main function
        const mainFunctionMatch = modifiedSource.match(/void\s+main\s*\(/);
        if (mainFunctionMatch) {
            const insertIndex = mainFunctionMatch.index;
            modifiedSource = modifiedSource.slice(0, insertIndex) + voiceFunctions + '\n' + modifiedSource.slice(insertIndex);
        }

        // Modify the main function to apply voice modulation
        modifiedSource = this.modifyMainFunction(modifiedSource);

        return modifiedSource;
    }

    modifyMainFunction(vertexSource) {
        // Find the position assignment in the main function
        const positionMatch = vertexSource.match(/gl_Position\s*=\s*([^;]+);/);

        if (positionMatch) {
            const originalPosition = positionMatch[1];

            // Replace with voice-modulated position
            const modifiedPosition = `
                vec3 voiceModulated = applyVoiceModulation(${originalPosition}.xyz, uTime);
                vec3 shapeMorphed = applyShapeMorphing(voiceModulated);
                gl_Position = vec4(shapeMorphed, ${originalPosition}.w);
            `;

            return vertexSource.replace(positionMatch[0], modifiedPosition);
        }

        return vertexSource;
    }

    useModifiedProgram(program) {
        // Call original useProgram
        this.originalUseProgram(program);

        // Update voice uniforms if this is our modified program
        if (this.modifiedShaders[program]) {
            this.updateVoiceUniforms(program);
        }
    }

    setupUniforms() {
        // Get uniform locations for voice parameters
        this.uniformLocations = {};

        // This will be called when programs are created
        this.updateUniformLocations = (program) => {
            this.uniformLocations[program] = {
                voiceIntensity: this.gl.getUniformLocation(program, 'uVoiceIntensity'),
                voiceFrequency: this.gl.getUniformLocation(program, 'uVoiceFrequency'),
                morphProgress: this.gl.getUniformLocation(program, 'uMorphProgress'),
                targetShape: this.gl.getUniformLocation(program, 'uTargetShape')
            };
        };
    }

    updateVoiceUniforms(program) {
        const locations = this.uniformLocations[program];
        if (!locations) return;

        // Update uniform values
        if (locations.voiceIntensity) {
            this.gl.uniform1f(locations.voiceIntensity, this.voiceUniforms.uVoiceIntensity);
        }
        if (locations.voiceFrequency) {
            this.gl.uniform1f(locations.voiceFrequency, this.voiceUniforms.uVoiceFrequency);
        }
        if (locations.morphProgress) {
            this.gl.uniform1f(locations.morphProgress, this.voiceUniforms.uMorphProgress);
        }
        if (locations.targetShape) {
            this.gl.uniform1f(locations.targetShape, this.voiceUniforms.uTargetShape);
        }
    }

    setVoiceData(voiceData) {
        this.voiceUniforms.uVoiceIntensity = Math.min(voiceData.intensity / 128, 1.0);
        this.voiceUniforms.uVoiceFrequency = voiceData.frequency;
    }

    setMorphProgress(progress) {
        this.voiceUniforms.uMorphProgress = progress;
    }

    setTargetShape(shape) {
        const shapeMap = {
            'default': 0.0,
            'cat': 1.0,
            'car': 2.0,
            'person': 3.0
        };

        this.voiceUniforms.uTargetShape = shapeMap[shape] || 0.0;
    }

    // Method to get current uniform values
    getVoiceUniforms() {
        return { ...this.voiceUniforms };
    }
}

// Initialize the shader modification system
window.addEventListener('load', () => {
    setTimeout(() => {
        window.shaderModificationSystem = new ShaderModificationSystem();
    }, 500);
});
