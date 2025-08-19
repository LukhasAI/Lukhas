/**
 * Shape Frames Implementation
 * Individual shape frame classes for different 3D formats
 * with morphing capabilities and AI integration
 */

/**
 * Base Shape Frame Class
 */
class ShapeFrame {
  constructor(geometry, materials, options = {}) {
    this.geometry = geometry;
    this.materials = materials;
    this.options = options;
    this.id = null;
    this.name = options.name || 'Unnamed Shape';
    this.category = options.category || 'unknown';
    this.morphTargets = options.morphTargets || [];
    this.animations = new Map();
    this.aiContext = null;
    
    // Morphing properties
    this.originalGeometry = this.cloneGeometry(geometry);
    this.currentMorphTarget = null;
    this.morphProgress = 0;
    
    // Voice-reactive properties
    this.voiceScale = 1.0;
    this.voiceRotation = { x: 0, y: 0, z: 0 };
    this.voiceColor = null;
  }
  
  /**
   * Clone geometry for morphing
   */
  cloneGeometry(geometry) {
    // Implementation depends on the specific geometry type
    return JSON.parse(JSON.stringify(geometry));
  }
  
  /**
   * Apply AI context to shape
   */
  applyAIContext(context) {
    this.aiContext = context;
    
    // Apply emotional modifications
    if (context.emotion) {
      this.applyEmotionalModification(context.emotion, context.intensity || 0.5);
    }
    
    // Apply contextual modifications
    if (context.context) {
      this.applyContextualModification(context.context);
    }
    
    // Apply voice modifications
    if (context.voice) {
      this.applyVoiceModification(context.voice);
    }
  }
  
  /**
   * Apply emotional modification
   */
  applyEmotionalModification(emotion, intensity) {
    switch (emotion) {
      case 'happy':
        this.scale(1 + intensity * 0.3);
        this.setColor('#FFD700');
        this.addAnimation('bounce', { duration: 1.0, loop: true });
        break;
      case 'sad':
        this.scale(1 - intensity * 0.2);
        this.setColor('#4169E1');
        this.addAnimation('droop', { duration: 2.0, loop: false });
        break;
      case 'excited':
        this.scale(1 + intensity * 0.5);
        this.setColor('#FF4500');
        this.addAnimation('vibrate', { duration: 0.5, loop: true });
        break;
      case 'calm':
        this.scale(1 + intensity * 0.1);
        this.setColor('#98FB98');
        this.addAnimation('float', { duration: 3.0, loop: true });
        break;
    }
  }
  
  /**
   * Apply contextual modification
   */
  applyContextualModification(context) {
    switch (context) {
      case 'music':
        this.addAnimation('rhythm', { duration: 0.8, loop: true });
        break;
      case 'nature':
        this.addAnimation('flow', { duration: 2.5, loop: true });
        break;
      case 'technology':
        this.addAnimation('glitch', { duration: 0.3, loop: true });
        break;
      case 'conversation':
        this.addAnimation('pulse', { duration: 1.2, loop: true });
        break;
    }
  }
  
  /**
   * Apply voice modification
   */
  applyVoiceModification(voiceContext) {
    const { pitch, volume, speechRate, emotion } = voiceContext;
    
    // Scale based on volume
    this.voiceScale = 1 + volume * 0.5;
    this.scale(this.voiceScale);
    
    // Rotation based on pitch
    this.voiceRotation.y = pitch * Math.PI * 2;
    this.rotate(this.voiceRotation);
    
    // Animation speed based on speech rate
    this.setAnimationSpeed(1 + speechRate * 0.5);
    
    // Color based on emotion
    if (emotion) {
      this.voiceColor = this.getEmotionColor(emotion);
      this.setColor(this.voiceColor);
    }
  }
  
  /**
   * Get emotion color
   */
  getEmotionColor(emotion) {
    const colors = {
      happy: '#FFD700',
      sad: '#4169E1',
      excited: '#FF4500',
      calm: '#98FB98',
      angry: '#FF0000',
      surprised: '#FF69B4',
      disgusted: '#8B4513',
      fearful: '#800080'
    };
    return colors[emotion] || '#FFFFFF';
  }
  
  /**
   * Scale the shape
   */
  scale(factor) {
    if (this.geometry.vertices) {
      this.geometry.vertices.forEach(vertex => {
        vertex.x *= factor;
        vertex.y *= factor;
        vertex.z *= factor;
      });
    }
  }
  
  /**
   * Rotate the shape
   */
  rotate(rotation) {
    // Implementation for rotating vertices
    if (this.geometry.vertices) {
      this.geometry.vertices.forEach(vertex => {
        // Apply rotation matrices
        const cosX = Math.cos(rotation.x);
        const sinX = Math.sin(rotation.x);
        const cosY = Math.cos(rotation.y);
        const sinY = Math.sin(rotation.y);
        const cosZ = Math.cos(rotation.z);
        const sinZ = Math.sin(rotation.z);
        
        // Rotate around X axis
        const y1 = vertex.y * cosX - vertex.z * sinX;
        const z1 = vertex.y * sinX + vertex.z * cosX;
        
        // Rotate around Y axis
        const x2 = vertex.x * cosY + z1 * sinY;
        const z2 = -vertex.x * sinY + z1 * cosY;
        
        // Rotate around Z axis
        const x3 = x2 * cosZ - y1 * sinZ;
        const y3 = x2 * sinZ + y1 * cosZ;
        
        vertex.x = x3;
        vertex.y = y3;
        vertex.z = z2;
      });
    }
  }
  
  /**
   * Set color
   */
  setColor(color) {
    if (this.materials && this.materials.length > 0) {
      this.materials.forEach(material => {
        if (material.color) {
          material.color.setHex(parseInt(color.replace('#', ''), 16));
        }
      });
    }
  }
  
  /**
   * Add animation
   */
  addAnimation(name, options) {
    this.animations.set(name, {
      name,
      startTime: Date.now(),
      duration: options.duration || 1.0,
      loop: options.loop || false,
      easing: options.easing || this.easeInOutCubic,
      ...options
    });
  }
  
  /**
   * Set animation speed
   */
  setAnimationSpeed(speed) {
    this.animations.forEach(animation => {
      animation.duration = animation.duration / speed;
    });
  }
  
  /**
   * Update animations
   */
  updateAnimations() {
    const currentTime = Date.now();
    
    this.animations.forEach((animation, name) => {
      const elapsed = (currentTime - animation.startTime) / 1000;
      const progress = (elapsed / animation.duration) % 1;
      
      // Apply easing
      const easedProgress = animation.easing(progress);
      
      // Apply animation effect
      this.applyAnimationEffect(name, easedProgress);
      
      // Remove non-looping completed animations
      if (!animation.loop && progress >= 1.0) {
        this.animations.delete(name);
      }
    });
  }
  
  /**
   * Apply animation effect
   */
  applyAnimationEffect(name, progress) {
    switch (name) {
      case 'bounce':
        this.applyBounceEffect(progress);
        break;
      case 'droop':
        this.applyDroopEffect(progress);
        break;
      case 'vibrate':
        this.applyVibrateEffect(progress);
        break;
      case 'float':
        this.applyFloatEffect(progress);
        break;
      case 'rhythm':
        this.applyRhythmEffect(progress);
        break;
      case 'flow':
        this.applyFlowEffect(progress);
        break;
      case 'glitch':
        this.applyGlitchEffect(progress);
        break;
      case 'pulse':
        this.applyPulseEffect(progress);
        break;
    }
  }
  
  /**
   * Animation effects
   */
  applyBounceEffect(progress) {
    const bounce = Math.sin(progress * Math.PI * 4) * 0.1;
    this.scale(1 + bounce);
  }
  
  applyDroopEffect(progress) {
    const droop = Math.sin(progress * Math.PI) * 0.3;
    this.scale(1 - droop);
  }
  
  applyVibrateEffect(progress) {
    const vibrate = Math.sin(progress * Math.PI * 20) * 0.05;
    this.scale(1 + vibrate);
  }
  
  applyFloatEffect(progress) {
    const float = Math.sin(progress * Math.PI * 2) * 0.05;
    this.scale(1 + float);
  }
  
  applyRhythmEffect(progress) {
    const rhythm = Math.sin(progress * Math.PI * 8) * 0.15;
    this.scale(1 + rhythm);
  }
  
  applyFlowEffect(progress) {
    const flow = Math.sin(progress * Math.PI * 1.5) * 0.08;
    this.scale(1 + flow);
  }
  
  applyGlitchEffect(progress) {
    const glitch = Math.random() * 0.1;
    this.scale(1 + glitch);
  }
  
  applyPulseEffect(progress) {
    const pulse = Math.sin(progress * Math.PI * 2) * 0.12;
    this.scale(1 + pulse);
  }
  
  /**
   * Easing functions
   */
  easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
  }
  
  /**
   * Morph to target shape
   */
  morphTo(targetShape, progress) {
    if (!targetShape || !this.geometry.vertices) return;
    
    this.morphProgress = progress;
    
    // Interpolate vertices
    this.geometry.vertices.forEach((vertex, i) => {
      if (targetShape.geometry.vertices[i]) {
        const target = targetShape.geometry.vertices[i];
        vertex.x = vertex.x + (target.x - vertex.x) * progress;
        vertex.y = vertex.y + (target.y - vertex.y) * progress;
        vertex.z = vertex.z + (target.z - vertex.z) * progress;
      }
    });
  }
  
  /**
   * Get shape data for rendering
   */
  getRenderData() {
    return {
      geometry: this.geometry,
      materials: this.materials,
      animations: Array.from(this.animations.values()),
      morphProgress: this.morphProgress,
      voiceScale: this.voiceScale,
      voiceRotation: this.voiceRotation,
      voiceColor: this.voiceColor
    };
  }
}

/**
 * OBJ Shape Frame
 */
class OBJShapeFrame extends ShapeFrame {
  constructor(vertices, faces, normals = [], uvs = [], options = {}) {
    const geometry = {
      vertices: vertices,
      faces: faces,
      normals: normals,
      uvs: uvs
    };
    
    super(geometry, [], options);
    this.format = 'obj';
  }
  
  /**
   * Parse OBJ data
   */
  static parseOBJ(data) {
    const lines = data.split('\n');
    const vertices = [];
    const faces = [];
    const normals = [];
    const uvs = [];
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('v ')) {
        const coords = trimmed.split(' ').slice(1).map(Number);
        vertices.push({ x: coords[0], y: coords[1], z: coords[2] });
      } else if (trimmed.startsWith('f ')) {
        const indices = trimmed.split(' ').slice(1).map(i => parseInt(i) - 1);
        faces.push(indices);
      } else if (trimmed.startsWith('vn ')) {
        const coords = trimmed.split(' ').slice(1).map(Number);
        normals.push({ x: coords[0], y: coords[1], z: coords[2] });
      } else if (trimmed.startsWith('vt ')) {
        const coords = trimmed.split(' ').slice(1).map(Number);
        uvs.push({ u: coords[0], v: coords[1] });
      }
    });
    
    return new OBJShapeFrame(vertices, faces, normals, uvs);
  }
  
  /**
   * Convert to Three.js geometry
   */
  toThreeJSGeometry() {
    const geometry = new THREE.BufferGeometry();
    
    // Convert vertices to Float32Array
    const positions = new Float32Array(this.geometry.vertices.length * 3);
    this.geometry.vertices.forEach((vertex, i) => {
      positions[i * 3] = vertex.x;
      positions[i * 3 + 1] = vertex.y;
      positions[i * 3 + 2] = vertex.z;
    });
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    // Convert faces to indices
    if (this.geometry.faces.length > 0) {
      const indices = [];
      this.geometry.faces.forEach(face => {
        if (face.length === 3) {
          indices.push(...face);
        } else if (face.length === 4) {
          // Triangulate quad
          indices.push(face[0], face[1], face[2]);
          indices.push(face[0], face[2], face[3]);
        }
      });
      geometry.setIndex(indices);
    }
    
    // Add normals if available
    if (this.geometry.normals.length > 0) {
      const normals = new Float32Array(this.geometry.normals.length * 3);
      this.geometry.normals.forEach((normal, i) => {
        normals[i * 3] = normal.x;
        normals[i * 3 + 1] = normal.y;
        normals[i * 3 + 2] = normal.z;
      });
      geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    }
    
    // Add UVs if available
    if (this.geometry.uvs.length > 0) {
      const uvs = new Float32Array(this.geometry.uvs.length * 2);
      this.geometry.uvs.forEach((uv, i) => {
        uvs[i * 2] = uv.u;
        uvs[i * 2 + 1] = uv.v;
      });
      geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    }
    
    geometry.computeVertexNormals();
    return geometry;
  }
}

/**
 * Three.js Shape Frame
 */
class ThreeJSShapeFrame extends ShapeFrame {
  constructor(geometry, materials, morphTargets = [], options = {}) {
    super(geometry, materials, options);
    this.format = 'threejs';
    this.morphTargets = morphTargets;
    this.morphTargetInfluences = new Array(morphTargets.length).fill(0);
  }
  
  /**
   * Apply morph target
   */
  applyMorphTarget(targetName, influence) {
    const index = this.morphTargets.indexOf(targetName);
    if (index !== -1) {
      this.morphTargetInfluences[index] = influence;
    }
  }
  
  /**
   * Get morph target influence
   */
  getMorphTargetInfluence(targetName) {
    const index = this.morphTargets.indexOf(targetName);
    return index !== -1 ? this.morphTargetInfluences[index] : 0;
  }
  
  /**
   * Set all morph target influences
   */
  setMorphTargetInfluences(influences) {
    this.morphTargetInfluences = influences.slice(0, this.morphTargets.length);
  }
}

/**
 * Babylon.js Shape Frame
 */
class BabylonShapeFrame extends ShapeFrame {
  constructor(data, options = {}) {
    super(data.geometry, data.materials, options);
    this.format = 'babylon';
    this.babylonData = data;
  }
  
  /**
   * Convert to Babylon.js mesh
   */
  toBabylonMesh(scene) {
    // Implementation for creating Babylon.js mesh
    // This would depend on the specific Babylon.js version and setup
    return null;
  }
}

/**
 * Collada Shape Frame
 */
class ColladaShapeFrame extends ShapeFrame {
  constructor(data, options = {}) {
    super(data.geometry, data.materials, options);
    this.format = 'collada';
    this.colladaData = data;
  }
  
  /**
   * Parse Collada XML
   */
  static parseCollada(xmlData) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlData, 'text/xml');
    
    // Extract geometry, materials, and animations from Collada XML
    // Implementation would depend on the specific Collada structure
    
    return new ColladaShapeFrame({
      geometry: {},
      materials: []
    });
  }
}

/**
 * STL Shape Frame
 */
class STLShapeFrame extends ShapeFrame {
  constructor(data, options = {}) {
    super(data.geometry, data.materials, options);
    this.format = 'stl';
    this.stlData = data;
  }
  
  /**
   * Parse STL data (binary or ASCII)
   */
  static parseSTL(data) {
    // Check if it's ASCII or binary STL
    const isASCII = data.startsWith('solid');
    
    if (isASCII) {
      return STLShapeFrame.parseASCIISTL(data);
    } else {
      return STLShapeFrame.parseBinarySTL(data);
    }
  }
  
  /**
   * Parse ASCII STL
   */
  static parseASCIISTL(data) {
    const lines = data.split('\n');
    const vertices = [];
    const faces = [];
    
    let currentFace = [];
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('vertex ')) {
        const coords = trimmed.split(' ').slice(1).map(Number);
        vertices.push({ x: coords[0], y: coords[1], z: coords[2] });
        currentFace.push(vertices.length - 1);
      } else if (trimmed.startsWith('endfacet')) {
        if (currentFace.length === 3) {
          faces.push([...currentFace]);
        }
        currentFace = [];
      }
    });
    
    return new STLShapeFrame({
      geometry: { vertices, faces },
      materials: []
    });
  }
  
  /**
   * Parse binary STL
   */
  static parseBinarySTL(data) {
    // Implementation for binary STL parsing
    // This would involve reading binary data with DataView
    return new STLShapeFrame({
      geometry: { vertices: [], faces: [] },
      materials: []
    });
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ShapeFrame,
    OBJShapeFrame,
    ThreeJSShapeFrame,
    BabylonShapeFrame,
    ColladaShapeFrame,
    STLShapeFrame
  };
} 