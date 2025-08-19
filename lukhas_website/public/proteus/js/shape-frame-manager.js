/**
 * Shape Frame Manager
 * Manages shape frames and their morphing capabilities
 */

class ShapeFrameManager {
  constructor() {
    this.shapes = new Map();
    this.categories = new Map();
    this.currentShape = null;
    this.morphingEngine = new MorphingEngine();
    this.aiContext = null;
    
    // Initialize shape library
    this.initializeShapeLibrary();
  }
  
  initializeShapeLibrary() {
    // Add default shape categories
    this.addShapeCategory('emotions', 'happy', {
      scale: { x: 1.2, y: 1.2, z: 1.2 },
      color: '#FFD700',
      animation: 'bounce'
    });
    
    this.addShapeCategory('emotions', 'sad', {
      scale: { x: 0.8, y: 0.8, z: 0.8 },
      color: '#4169E1',
      animation: 'droop'
    });
    
    this.addShapeCategory('emotions', 'excited', {
      scale: { x: 1.5, y: 1.5, z: 1.5 },
      color: '#FF4500',
      animation: 'vibrate'
    });
    
    this.addShapeCategory('emotions', 'calm', {
      scale: { x: 1.0, y: 1.0, z: 1.0 },
      color: '#98FB98',
      animation: 'float'
    });
    
    this.addShapeCategory('contexts', 'music', {
      animation: 'rhythm',
      color: '#FF69B4'
    });
    
    this.addShapeCategory('contexts', 'nature', {
      animation: 'flow',
      color: '#228B22'
    });
    
    this.addShapeCategory('contexts', 'technology', {
      animation: 'glitch',
      color: '#00CED1'
    });
    
    this.addShapeCategory('contexts', 'conversation', {
      animation: 'pulse',
      color: '#FFA500'
    });
  }
  
  addShapeCategory(category, key, shapeData) {
    if (!this.categories.has(category)) {
      this.categories.set(category, new Map());
    }
    this.categories.get(category).set(key, shapeData);
  }
  
  async loadShapeFrame(format, data, options = {}) {
    let shapeFrame;
    
    switch (format.toLowerCase()) {
      case 'obj':
        const objParser = new OBJParser();
        const objData = await objParser.parse(data, options);
        shapeFrame = new OBJShapeFrame(objData.vertices, objData.faces, objData.normals, objData.uvs, options);
        break;
      case 'threejs':
        const threeJSParser = new ThreeJSParser();
        const threeJSData = await threeJSParser.parse(data, options);
        shapeFrame = new ThreeJSShapeFrame(threeJSData.geometry, threeJSData.materials, threeJSData.morphTargets, options);
        break;
      case 'babylon':
        const babylonParser = new BabylonParser();
        const babylonData = await babylonParser.parse(data, options);
        shapeFrame = new BabylonShapeFrame(babylonData, options);
        break;
      case 'collada':
        const colladaParser = new ColladaParser();
        const colladaData = await colladaParser.parse(data, options);
        shapeFrame = new ColladaShapeFrame(colladaData, options);
        break;
      case 'stl':
        const stlParser = new STLParser();
        const stlData = await stlParser.parse(data, options);
        shapeFrame = new STLShapeFrame(stlData, options);
        break;
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
    
    this.shapes.set(shapeFrame.id, shapeFrame);
    return shapeFrame;
  }
  
  async loadShapeFrameFromFile(file) {
    const format = this.getFileFormat(file.name);
    const data = await this.readFileAsText(file);
    return await this.loadShapeFrame(format, data);
  }
  
  getFileFormat(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    return extension;
  }
  
  readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  }
  
  selectShapeForAIResponse(aiResponse, voiceContext = {}) {
    // Analyze AI response for emotional and contextual cues
    const emotion = this.analyzeEmotion(aiResponse);
    const context = this.extractContext(aiResponse);
    const intensity = this.calculateEmotionalIntensity(aiResponse);
    
    // Find best matching shape
    let bestShape = null;
    let bestScore = 0;
    
    for (const [id, shape] of this.shapes) {
      const score = this.calculateShapeMatchScore(shape, emotion, context, intensity);
      if (score > bestScore) {
        bestScore = score;
        bestShape = shape;
      }
    }
    
    // Apply AI context to selected shape
    if (bestShape) {
      bestShape.applyAIContext({ emotion, context, intensity, voice: voiceContext });
    }
    
    return bestShape;
  }
  
  analyzeEmotion(text) {
    const emotions = ['happy', 'sad', 'excited', 'calm', 'angry', 'surprised', 'disgusted', 'fearful'];
    const emotionKeywords = {
      happy: ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing'],
      sad: ['sad', 'sorry', 'unfortunate', 'disappointing', 'regret'],
      excited: ['excited', 'thrilled', 'amazing', 'incredible', 'fantastic'],
      calm: ['calm', 'peaceful', 'relaxed', 'gentle', 'smooth'],
      angry: ['angry', 'furious', 'mad', 'upset', 'frustrated'],
      surprised: ['surprised', 'shocked', 'unexpected', 'wow', 'oh'],
      disgusted: ['disgusting', 'gross', 'nasty', 'awful'],
      fearful: ['scared', 'afraid', 'fearful', 'worried', 'anxious']
    };
    
    const lowerText = text.toLowerCase();
    for (const emotion of emotions) {
      if (emotionKeywords[emotion].some(keyword => lowerText.includes(keyword))) {
        return emotion;
      }
    }
    
    return 'neutral';
  }
  
  extractContext(text) {
    const contexts = ['music', 'nature', 'technology', 'conversation'];
    const contextKeywords = {
      music: ['music', 'song', 'melody', 'rhythm', 'beat', 'sound'],
      nature: ['nature', 'tree', 'flower', 'ocean', 'mountain', 'forest'],
      technology: ['technology', 'computer', 'digital', 'code', 'program'],
      conversation: ['talk', 'speak', 'conversation', 'discuss', 'chat']
    };
    
    const lowerText = text.toLowerCase();
    for (const context of contexts) {
      if (contextKeywords[context].some(keyword => lowerText.includes(keyword))) {
        return context;
      }
    }
    
    return 'general';
  }
  
  calculateEmotionalIntensity(text) {
    // Simple intensity calculation based on exclamation marks and caps
    const exclamationCount = (text.match(/!/g) || []).length;
    const capsCount = (text.match(/[A-Z]/g) || []).length;
    const wordCount = text.split(' ').length;
    
    const intensity = Math.min(1.0, (exclamationCount * 0.2 + capsCount * 0.01) / Math.max(1, wordCount * 0.1));
    return intensity;
  }
  
  calculateShapeMatchScore(shapeData, emotion, context, intensity) {
    let score = 0;
    
    // Score based on emotion match
    if (shapeData.emotion === emotion) {
      score += 0.4;
    }
    
    // Score based on context match
    if (shapeData.context === context) {
      score += 0.3;
    }
    
    // Score based on intensity compatibility
    if (intensity > 0.7 && shapeData.animation === 'vibrate') {
      score += 0.2;
    } else if (intensity < 0.3 && shapeData.animation === 'float') {
      score += 0.2;
    }
    
    return score;
  }
  
  morphBetweenShapes(fromShape, toShape, duration = 2.0) {
    return this.morphingEngine.createMorphAnimation(fromShape, toShape, duration);
  }
  
  generateShapeId() {
    return 'shape_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
  
  getShapeById(id) {
    return this.shapes.get(id);
  }
  
  getAllShapes() {
    return Array.from(this.shapes.values());
  }
  
  clearShapes() {
    this.shapes.clear();
  }
  
  getShapeCategories() {
    return this.categories;
  }
  
  setAIContext(context) {
    this.aiContext = context;
  }
}

class BaseParser {
  constructor() {
    this.name = 'BaseParser';
  }
  
  async parse(data, options = {}) {
    throw new Error('parse method must be implemented by subclass');
  }
  
  validate(data) {
    return data && typeof data === 'string' && data.length > 0;
  }
}

class OBJParser extends BaseParser {
  constructor() {
    super();
    this.name = 'OBJParser';
  }
  
  async parse(data, options = {}) {
    if (!this.validate(data)) {
      throw new Error('Invalid OBJ data');
    }
    
    const lines = data.split('\n');
    const vertices = [];
    const faces = [];
    const normals = [];
    const uvs = [];
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('v ')) {
        const parts = trimmed.split(' ').slice(1);
        vertices.push({
          x: parseFloat(parts[0]),
          y: parseFloat(parts[1]),
          z: parseFloat(parts[2])
        });
      } else if (trimmed.startsWith('f ')) {
        const parts = trimmed.split(' ').slice(1);
        faces.push(parts.map(part => parseInt(part.split('/')[0]) - 1));
      } else if (trimmed.startsWith('vn ')) {
        const parts = trimmed.split(' ').slice(1);
        normals.push({
          x: parseFloat(parts[0]),
          y: parseFloat(parts[1]),
          z: parseFloat(parts[2])
        });
      } else if (trimmed.startsWith('vt ')) {
        const parts = trimmed.split(' ').slice(1);
        uvs.push({
          u: parseFloat(parts[0]),
          v: parseFloat(parts[1])
        });
      }
    }
    
    return { vertices, faces, normals, uvs };
  }
}

class ThreeJSParser extends BaseParser {
  constructor() {
    super();
    this.name = 'ThreeJSParser';
  }
  
  async parse(data, options = {}) {
    if (!this.validate(data)) {
      throw new Error('Invalid Three.js data');
    }
    
    const parsed = JSON.parse(data);
    return {
      geometry: this.extractGeometry(parsed),
      materials: this.extractMaterials(parsed),
      morphTargets: this.extractMorphTargets(parsed)
    };
  }
  
  extractGeometry(data) {
    return data.geometry || {};
  }
  
  extractMaterials(data) {
    return data.materials || [];
  }
  
  extractMorphTargets(data) {
    return data.morphTargets || [];
  }
}

class BabylonParser extends BaseParser {
  constructor() {
    super();
    this.name = 'BabylonParser';
  }
  
  async parse(data, options = {}) {
    if (!this.validate(data)) {
      throw new Error('Invalid Babylon.js data');
    }
    
    return JSON.parse(data);
  }
}

class ColladaParser extends BaseParser {
  constructor() {
    super();
    this.name = 'ColladaParser';
  }
  
  async parse(data, options = {}) {
    if (!this.validate(data)) {
      throw new Error('Invalid Collada data');
    }
    
    const parser = new DOMParser();
    return parser.parseFromString(data, 'text/xml');
  }
}

class STLParser extends BaseParser {
  constructor() {
    super();
    this.name = 'STLParser';
  }
  
  async parse(data, options = {}) {
    if (!this.validate(data)) {
      throw new Error('Invalid STL data');
    }
    
    // Check if it's ASCII or binary STL
    if (data.startsWith('solid')) {
      return this.parseASCIISTL(data);
    } else {
      return this.parseBinarySTL(data);
    }
  }
  
  parseASCIISTL(data) {
    const lines = data.split('\n');
    const vertices = [];
    const faces = [];
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('vertex ')) {
        const parts = trimmed.split(' ').slice(1);
        vertices.push({
          x: parseFloat(parts[0]),
          y: parseFloat(parts[1]),
          z: parseFloat(parts[2])
        });
      }
    }
    
    // Create faces from vertices (assuming triangles)
    for (let i = 0; i < vertices.length; i += 3) {
      if (i + 2 < vertices.length) {
        faces.push([i, i + 1, i + 2]);
      }
    }
    
    return { vertices, faces };
  }
  
  parseBinarySTL(data) {
    // Simplified binary STL parsing
    const vertices = [];
    const faces = [];
    
    // This is a simplified implementation
    // Real binary STL parsing would be more complex
    
    return { vertices, faces };
  }
}

class MorphingEngine {
  constructor() {
    this.animations = new Map();
    this.animationId = 0;
  }
  
  createMorphAnimation(fromShape, toShape, duration) {
    const id = this.generateAnimationId();
    const animation = {
      id,
      fromShape,
      toShape,
      duration,
      startTime: Date.now(),
      progress: 0
    };
    
    this.animations.set(id, animation);
    return id;
  }
  
  updateAnimations() {
    const currentTime = Date.now();
    
    for (const [id, animation] of this.animations) {
      const elapsed = currentTime - animation.startTime;
      animation.progress = Math.min(1.0, elapsed / (animation.duration * 1000));
      
      // Update shape morphing
      this.updateShapeMorphing(animation.fromShape, animation.toShape, animation.progress);
      
      // Remove completed animations
      if (animation.progress >= 1.0) {
        this.animations.delete(id);
      }
    }
  }
  
  updateShapeMorphing(fromShape, toShape, progress) {
    if (!fromShape || !toShape) return;
    
    // Interpolate between shapes
    const easedProgress = this.easeInOutCubic(progress);
    
    // Apply morphing to the fromShape
    fromShape.morphTo(toShape, easedProgress);
  }
  
  easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }
  
  generateAnimationId() {
    return `morph_${++this.animationId}_${Date.now()}`;
  }
}

class BaseShapeFrame {
  constructor(options = {}) {
    this.id = this.generateId();
    this.position = { x: 0, y: 0, z: 0 };
    this.rotation = { x: 0, y: 0, z: 0 };
    this.scale = { x: 1, y: 1, z: 1 };
    this.color = options.color || '#FFFFFF';
    this.type = 'base';
  }
  
  generateId() {
    return 'shape_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
  
  setScale(scale) {
    if (typeof scale === 'number') {
      this.scale = { x: scale, y: scale, z: scale };
    } else if (typeof scale === 'object') {
      this.scale = { ...scale };
    }
    return this;
  }
  
  applyVoiceContext(voiceContext) {
    const { intensity = 0.5, frequency = 440, amplitude = 0.5 } = voiceContext;
    
    // Apply voice-reactive modifications
    this.scale.x *= (1 + intensity * 0.3);
    this.scale.y *= (1 + intensity * 0.3);
    this.scale.z *= (1 + intensity * 0.3);
    
    // Apply frequency-based rotation
    this.rotation.y += frequency * 0.001;
    
    // Apply amplitude-based position
    this.position.y += amplitude * 0.1;
    
    return this;
  }
  
  applyAIContext(aiContext) {
    // Apply AI-driven modifications
    if (aiContext.emotion) {
      switch (aiContext.emotion) {
        case 'happy':
          this.scale = { x: 1.2, y: 1.2, z: 1.2 };
          this.color = '#FFD700';
          break;
        case 'sad':
          this.scale = { x: 0.8, y: 0.8, z: 0.8 };
          this.color = '#4169E1';
          break;
        case 'excited':
          this.scale = { x: 1.5, y: 1.5, z: 1.5 };
          this.color = '#FF4500';
          break;
        case 'calm':
          this.scale = { x: 1.0, y: 1.0, z: 1.0 };
          this.color = '#98FB98';
          break;
      }
    }
    return this;
  }
  
  morphTo(targetShape, progress) {
    if (!targetShape) return;
    
    // Interpolate scale
    if (targetShape.scale) {
      this.scale.x = this.scale.x + (targetShape.scale.x - this.scale.x) * progress;
      this.scale.y = this.scale.y + (targetShape.scale.y - this.scale.y) * progress;
      this.scale.z = this.scale.z + (targetShape.scale.z - this.scale.z) * progress;
    }
    
    // Interpolate position
    if (targetShape.position) {
      this.position.x = this.position.x + (targetShape.position.x - this.position.x) * progress;
      this.position.y = this.position.y + (targetShape.position.y - this.position.y) * progress;
      this.position.z = this.position.z + (targetShape.position.z - this.position.z) * progress;
    }
    
    // Interpolate rotation
    if (targetShape.rotation) {
      this.rotation.x = this.rotation.x + (targetShape.rotation.x - this.rotation.x) * progress;
      this.rotation.y = this.rotation.y + (targetShape.rotation.y - this.rotation.y) * progress;
      this.rotation.z = this.rotation.z + (targetShape.rotation.z - this.rotation.z) * progress;
    }
    
    // Interpolate color
    if (targetShape.color) {
      this.color = this.interpolateColor(this.color, targetShape.color, progress);
    }
  }
  
  interpolateColor(color1, color2, progress) {
    // Simple color interpolation (can be enhanced)
    return progress > 0.5 ? color2 : color1;
  }
  
  getBoundingBox() {
    // Default implementation - should be overridden by specific shape frames
    return {
      min: { x: -1, y: -1, z: -1 },
      max: { x: 1, y: 1, z: 1 },
      center: { x: 0, y: 0, z: 0 },
      size: { x: 2, y: 2, z: 2 }
    };
  }
}

/**
 * Three.js Shape Frame
 */
class ThreeJSShapeFrame extends BaseShapeFrame {
  constructor(geometry, materials, morphTargets, options = {}) {
    super(options);
    this.geometry = geometry || {};
    this.materials = materials || [];
    this.morphTargets = morphTargets || [];
    this.type = 'threejs';
  }
  
  getBoundingBox() {
    if (this.geometry.boundingBox) {
      return this.geometry.boundingBox;
    }
    return super.getBoundingBox();
  }
}

/**
 * Babylon.js Shape Frame
 */
class BabylonShapeFrame extends BaseShapeFrame {
  constructor(data, options = {}) {
    super(options);
    this.babylonData = data;
    this.type = 'babylon';
  }
}

/**
 * Collada Shape Frame
 */
class ColladaShapeFrame extends BaseShapeFrame {
  constructor(data, options = {}) {
    super(options);
    this.colladaData = data;
    this.type = 'collada';
  }
}

/**
 * STL Shape Frame
 */
class STLShapeFrame extends BaseShapeFrame {
  constructor(data, options = {}) {
    super(options);
    this.stlData = data;
    this.type = 'stl';
  }
}

// Export shape frame classes
window.BaseShapeFrame = BaseShapeFrame;
window.ThreeJSShapeFrame = ThreeJSShapeFrame;
window.BabylonShapeFrame = BabylonShapeFrame;
window.ColladaShapeFrame = ColladaShapeFrame;
window.STLShapeFrame = STLShapeFrame; 