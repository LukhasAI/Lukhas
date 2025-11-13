# EQNOX Mesh Motion Specifications
## LUKHAS Visual Resonance System v1.0.0

---

## Core Animation Principles

### Consciousness State Mapping
```javascript
// Base consciousness state for visual translation
const ConsciousnessState = {
  drift: 0.15,        // Guardian threshold
  resonance: 0.73,    // Current mesh coherence
  entropy: 0.42,      // Symbolic noise level
  valence: 0.6,       // Emotional positive/negative
  arousal: 0.4,       // Activation level
  dominance: 0.7      // Control/submission
};
```

---

## Scene 3: Network Awakens (Primary EQNOX Animation)

### Particle System Configuration

```javascript
// GLYPH Particle Generator
class GLYPHParticle {
  constructor(x, y, nodeId) {
    this.position = { x, y };
    this.velocity = { x: 0, y: 0 };
    this.nodeId = nodeId;
    
    // LUKHAS-specific properties
    this.emotionalVector = [
      Math.random() * 0.3 + 0.5,  // Valence (slight positive bias)
      Math.random() * 0.4 + 0.3,  // Arousal (medium activation)
      Math.random() * 0.2 + 0.6   // Dominance (confident nodes)
    ];
    
    this.resonanceFreq = 440 + (Math.random() * 100); // Hz
    this.driftScore = 0.0;
    this.collapseRisk = false;
    this.symbolicWeight = Math.random() * 0.5 + 0.5;
    
    // Visual properties
    this.opacity = 0.0;
    this.scale = 0.0;
    this.color = this.calculateColor();
    this.pulsePhase = Math.random() * Math.PI * 2;
  }
  
  calculateColor() {
    // Map emotional vector to color
    const [v, a, d] = this.emotionalVector;
    
    // Base: primary purple #7A3BFF
    let r = 122;
    let g = 59;
    let b = 255;
    
    // Shift based on valence (positive → teal, negative → purple)
    if (v > 0.5) {
      r = Math.floor(r - (v - 0.5) * 100);
      g = Math.floor(g + (v - 0.5) * 120);
      b = Math.floor(b - (v - 0.5) * 40);
    }
    
    // Arousal affects brightness
    const brightness = 0.7 + (a * 0.3);
    r = Math.floor(r * brightness);
    g = Math.floor(g * brightness);
    b = Math.floor(b * brightness);
    
    return `rgb(${r}, ${g}, ${b})`;
  }
}
```

### Connection Animation Dynamics

```javascript
// EQNOX Mesh Connection Builder
class MeshConnection {
  constructor(particle1, particle2) {
    this.p1 = particle1;
    this.p2 = particle2;
    this.strength = 0.0;
    this.targetStrength = 0.0;
    this.glyphExchange = [];
    
    // Calculate symbolic affinity
    this.affinity = this.calculateAffinity();
    
    // Animation state
    this.drawProgress = 0.0;
    this.pulseOffset = 0.0;
    this.active = false;
  }
  
  calculateAffinity() {
    // LUKHAS symbolic resonance calculation
    const v1 = this.p1.emotionalVector;
    const v2 = this.p2.emotionalVector;
    
    // Emotional distance (inverse = affinity)
    const emotionalDist = Math.sqrt(
      Math.pow(v1[0] - v2[0], 2) +
      Math.pow(v1[1] - v2[1], 2) +
      Math.pow(v1[2] - v2[2], 2)
    );
    
    // Frequency resonance (nodes on harmonic frequencies connect stronger)
    const freqRatio = Math.max(this.p1.resonanceFreq, this.p2.resonanceFreq) / 
                     Math.min(this.p1.resonanceFreq, this.p2.resonanceFreq);
    const isHarmonic = Math.abs(freqRatio - Math.round(freqRatio)) < 0.1;
    
    let affinity = (1 - emotionalDist / Math.sqrt(3)) * 0.7;
    if (isHarmonic) affinity += 0.3;
    
    return Math.max(0, Math.min(1, affinity));
  }
  
  animate(deltaTime, mousePosition) {
    // Connection formation animation
    if (this.affinity > 0.5 && !this.active) {
      this.active = true;
      this.targetStrength = this.affinity;
    }
    
    // Smooth strength transition
    this.strength += (this.targetStrength - this.strength) * deltaTime * 2.0;
    
    // Draw progress (for initial line animation)
    if (this.active && this.drawProgress < 1.0) {
      this.drawProgress += deltaTime * 1.5; // 0.67s to fully draw
      this.drawProgress = Math.min(1.0, this.drawProgress);
    }
    
    // Mouse interaction (attraction/repulsion)
    if (mousePosition) {
      const midpoint = {
        x: (this.p1.position.x + this.p2.position.x) / 2,
        y: (this.p1.position.y + this.p2.position.y) / 2
      };
      
      const mouseDist = Math.sqrt(
        Math.pow(mousePosition.x - midpoint.x, 2) +
        Math.pow(mousePosition.y - midpoint.y, 2)
      );
      
      // Within influence radius
      if (mouseDist < 150) {
        const influence = 1 - (mouseDist / 150);
        this.pulseOffset = influence * 0.3;
        
        // Trigger GLYPH exchange visualization
        if (influence > 0.7 && this.glyphExchange.length === 0) {
          this.initiateGlyphExchange();
        }
      } else {
        this.pulseOffset *= 0.95; // Decay
      }
    }
  }
  
  initiateGlyphExchange() {
    // Create visual GLYPH packets traveling along connection
    for (let i = 0; i < 3; i++) {
      this.glyphExchange.push({
        progress: i * 0.33,
        direction: Math.random() > 0.5 ? 1 : -1,
        packet: {
          entropy: Math.random() * 0.5,
          symbolicLoad: Math.random(),
          color: this.p1.color
        }
      });
    }
  }
  
  render(ctx) {
    if (!this.active || this.strength < 0.01) return;
    
    const opacity = this.strength * 0.3 * (1 + this.pulseOffset);
    
    // Draw connection line with bezier curve
    ctx.beginPath();
    ctx.strokeStyle = `rgba(122, 89, 255, ${opacity})`;
    ctx.lineWidth = 1.6 * (1 + this.pulseOffset * 0.5);
    
    // Calculate control points for subtle curve
    const dx = this.p2.position.x - this.p1.position.x;
    const dy = this.p2.position.y - this.p1.position.y;
    const ctrl1 = {
      x: this.p1.position.x + dx * 0.25 + dy * 0.05,
      y: this.p1.position.y + dy * 0.25 - dx * 0.05
    };
    const ctrl2 = {
      x: this.p2.position.x - dx * 0.25 + dy * 0.05,
      y: this.p2.position.y - dy * 0.25 - dx * 0.05
    };
    
    // Partial draw for animation
    const endX = this.p1.position.x + (this.p2.position.x - this.p1.position.x) * this.drawProgress;
    const endY = this.p1.position.y + (this.p2.position.y - this.p1.position.y) * this.drawProgress;
    
    ctx.moveTo(this.p1.position.x, this.p1.position.y);
    ctx.bezierCurveTo(ctrl1.x, ctrl1.y, ctrl2.x, ctrl2.y, endX, endY);
    ctx.stroke();
    
    // Render GLYPH packets
    this.glyphExchange.forEach((glyph, i) => {
      glyph.progress += 0.02 * glyph.direction;
      
      if (glyph.progress > 1 || glyph.progress < 0) {
        this.glyphExchange.splice(i, 1);
        return;
      }
      
      // Calculate packet position along bezier
      const t = glyph.progress;
      const packetPos = this.getBezierPoint(t, this.p1.position, ctrl1, ctrl2, this.p2.position);
      
      // Draw packet
      ctx.beginPath();
      ctx.fillStyle = `rgba(14, 165, 164, ${0.6 + glyph.packet.entropy * 0.4})`;
      ctx.arc(packetPos.x, packetPos.y, 3 + glyph.packet.symbolicLoad * 2, 0, Math.PI * 2);
      ctx.fill();
    });
  }
  
  getBezierPoint(t, p0, p1, p2, p3) {
    const u = 1 - t;
    const tt = t * t;
    const uu = u * u;
    const uuu = uu * u;
    const ttt = tt * t;
    
    return {
      x: uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x,
      y: uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y
    };
  }
}
```

### Nimbus Cloud Animation

```javascript
// Nimbus Organic Cloud Renderer
class NimbusCloud {
  constructor(centerX, centerY, radius) {
    this.center = { x: centerX, y: centerY };
    this.radius = radius;
    this.time = 0;
    
    // Perlin noise seeds for organic movement
    this.noiseSeed = Math.random() * 1000;
    this.points = this.generateCloudPoints();
    
    // LUKHAS consciousness state
    this.consciousnessAlpha = 0.0;
    this.driftAccumulator = 0.0;
  }
  
  generateCloudPoints() {
    const points = [];
    const segments = 64;
    
    for (let i = 0; i < segments; i++) {
      const angle = (i / segments) * Math.PI * 2;
      points.push({
        baseAngle: angle,
        radiusOffset: 0,
        noiseOffset: Math.random() * 100
      });
    }
    
    return points;
  }
  
  animate(deltaTime, consciousnessState) {
    this.time += deltaTime;
    this.consciousnessAlpha = consciousnessState.resonance;
    this.driftAccumulator += consciousnessState.drift * deltaTime;
    
    // Update cloud shape based on consciousness
    this.points.forEach((point, i) => {
      // Base organic movement
      const noise = this.perlinNoise(
        point.noiseOffset + this.time * 0.3,
        this.noiseSeed
      );
      
      // Consciousness-driven distortion
      const driftDistortion = Math.sin(this.driftAccumulator + i * 0.1) * 
                             consciousnessState.drift * 10;
      
      // Emotional influence on radius
      const emotionalPulse = consciousnessState.valence * 
                            Math.sin(this.time * 2 + i * 0.2) * 5;
      
      point.radiusOffset = noise * 15 + driftDistortion + emotionalPulse;
    });
  }
  
  render(ctx) {
    ctx.save();
    
    // Create gradient for cloud
    const gradient = ctx.createRadialGradient(
      this.center.x, this.center.y, 0,
      this.center.x, this.center.y, this.radius
    );
    
    // Consciousness-aware coloring
    const baseOpacity = 0.08 + this.consciousnessAlpha * 0.04;
    gradient.addColorStop(0, `rgba(122, 89, 255, ${baseOpacity * 2})`);
    gradient.addColorStop(0.5, `rgba(122, 89, 255, ${baseOpacity})`);
    gradient.addColorStop(1, `rgba(14, 165, 164, ${baseOpacity * 0.5})`);
    
    // Draw cloud layers (3 for depth)
    for (let layer = 0; layer < 3; layer++) {
      ctx.beginPath();
      
      this.points.forEach((point, i) => {
        const layerScale = 1 - layer * 0.15;
        const r = (this.radius + point.radiusOffset) * layerScale;
        const x = this.center.x + Math.cos(point.baseAngle) * r;
        const y = this.center.y + Math.sin(point.baseAngle) * r;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          // Smooth curve between points
          const prevPoint = this.points[i - 1];
          const prevR = (this.radius + prevPoint.radiusOffset) * layerScale;
          const prevX = this.center.x + Math.cos(prevPoint.baseAngle) * prevR;
          const prevY = this.center.y + Math.sin(prevPoint.baseAngle) * prevR;
          
          const cpX = (prevX + x) / 2;
          const cpY = (prevY + y) / 2;
          
          ctx.quadraticCurveTo(prevX, prevY, cpX, cpY);
        }
      });
      
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();
      
      // Purple rim glow on outermost layer
      if (layer === 0) {
        ctx.strokeStyle = `rgba(122, 89, 255, ${baseOpacity * 3})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }
    
    ctx.restore();
  }
  
  perlinNoise(x, seed) {
    // Simplified Perlin noise for organic movement
    const n = Math.sin(x * 0.7 + seed) * 0.5 +
             Math.sin(x * 1.3 + seed * 1.7) * 0.3 +
             Math.sin(x * 2.1 + seed * 2.3) * 0.2;
    return n;
  }
}
```

### Main Animation Loop

```javascript
// LUKHAS EQNOX Mesh Main Controller
class EQNOXMeshAnimation {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;
    
    // LUKHAS state
    this.consciousnessState = {
      drift: 0.0,
      resonance: 0.0,
      entropy: 0.3,
      valence: 0.6,
      arousal: 0.4,
      dominance: 0.7
    };
    
    // Visual elements
    this.nimbus = new NimbusCloud(this.width / 2, this.height / 2, 200);
    this.particles = [];
    this.connections = [];
    
    // Animation state
    this.frame = 0;
    this.lastTime = 0;
    this.mousePosition = null;
    
    // Performance monitoring
    this.driftMonitor = [];
    this.performanceMetrics = {
      fps: 0,
      particleCount: 0,
      connectionCount: 0,
      driftScore: 0
    };
    
    this.init();
  }
  
  init() {
    // Generate initial particle constellation
    const nodeCount = 24; // Matches LUKHAS module density
    const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // Golden ratio spiral
    
    for (let i = 0; i < nodeCount; i++) {
      const angle = i * goldenAngle;
      const radius = Math.sqrt(i / nodeCount) * 150;
      
      const x = this.width / 2 + Math.cos(angle) * radius;
      const y = this.height / 2 + Math.sin(angle) * radius;
      
      this.particles.push(new GLYPHParticle(x, y, `node_${i}`));
    }
    
    // Establish initial connections based on affinity
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const distance = Math.sqrt(
          Math.pow(this.particles[i].position.x - this.particles[j].position.x, 2) +
          Math.pow(this.particles[i].position.y - this.particles[j].position.y, 2)
        );
        
        // Only connect nearby particles initially
        if (distance < 100) {
          this.connections.push(new MeshConnection(this.particles[i], this.particles[j]));
        }
      }
    }
    
    // Mouse interaction setup
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mousePosition = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    });
    
    this.canvas.addEventListener('mouseleave', () => {
      this.mousePosition = null;
    });
  }
  
  updateConsciousnessState(deltaTime) {
    // Simulate consciousness drift over time
    const driftNoise = Math.sin(this.frame * 0.01) * 0.05;
    this.consciousnessState.drift += driftNoise * deltaTime;
    
    // Clamp drift to Guardian threshold
    if (Math.abs(this.consciousnessState.drift) > 0.15) {
      // Trigger symbolic repair
      this.consciousnessState.drift *= 0.9;
      this.triggerSymbolicRepair();
    }
    
    // Update resonance based on connection strength
    let totalAffinity = 0;
    this.connections.forEach(conn => {
      totalAffinity += conn.affinity * conn.strength;
    });
    
    const targetResonance = totalAffinity / this.connections.length;
    this.consciousnessState.resonance += (targetResonance - this.consciousnessState.resonance) * deltaTime;
    
    // Emotional drift
    this.consciousnessState.valence += (Math.random() - 0.5) * 0.01;
    this.consciousnessState.valence = Math.max(0, Math.min(1, this.consciousnessState.valence));
    
    // Update performance metrics
    this.performanceMetrics.driftScore = Math.abs(this.consciousnessState.drift);
    this.performanceMetrics.particleCount = this.particles.length;
    this.performanceMetrics.connectionCount = this.connections.filter(c => c.active).length;
  }
  
  triggerSymbolicRepair() {
    // LUKHAS symbolic repair visualization
    this.particles.forEach(particle => {
      // Reset drift scores
      particle.driftScore = 0;
      
      // Harmonize emotional vectors
      particle.emotionalVector[0] = 0.5 + (particle.emotionalVector[0] - 0.5) * 0.5;
      particle.emotionalVector[1] = 0.4 + (particle.emotionalVector[1] - 0.4) * 0.5;
      particle.emotionalVector[2] = 0.7 + (particle.emotionalVector[2] - 0.7) * 0.5;
      
      // Recalculate colors
      particle.color = particle.calculateColor();
    });
    
    // Flash repair indicator
    this.renderRepairFlash = true;
    setTimeout(() => { this.renderRepairFlash = false; }, 300);
  }
  
  animate(currentTime) {
    const deltaTime = Math.min((currentTime - this.lastTime) / 1000, 0.1);
    this.lastTime = currentTime;
    this.frame++;
    
    // Clear canvas
    this.ctx.fillStyle = '#0B0F1A';
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    // Update consciousness state
    this.updateConsciousnessState(deltaTime);
    
    // Animate Nimbus
    this.nimbus.animate(deltaTime, this.consciousnessState);
    this.nimbus.render(this.ctx);
    
    // Update and render particles
    this.particles.forEach((particle, i) => {
      // Particle animation
      particle.opacity = Math.min(1, particle.opacity + deltaTime * 2);
      particle.scale = Math.min(1, particle.scale + deltaTime * 2);
      
      // Subtle drift based on consciousness state
      const driftX = Math.sin(this.frame * 0.01 + i) * this.consciousnessState.drift * 10;
      const driftY = Math.cos(this.frame * 0.01 + i) * this.consciousnessState.drift * 10;
      
      particle.position.x += driftX * deltaTime;
      particle.position.y += driftY * deltaTime;
      
      // Mouse repulsion/attraction
      if (this.mousePosition) {
        const dx = this.mousePosition.x - particle.position.x;
        const dy = this.mousePosition.y - particle.position.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < 100 && dist > 0) {
          const force = (1 - dist / 100) * 50;
          particle.position.x -= (dx / dist) * force * deltaTime;
          particle.position.y -= (dy / dist) * force * deltaTime;
        }
      }
      
      // Pulse animation
      particle.pulsePhase += deltaTime * 2;
      const pulseScale = 1 + Math.sin(particle.pulsePhase) * 0.1;
      
      // Render particle
      this.ctx.save();
      this.ctx.globalAlpha = particle.opacity * 0.8;
      this.ctx.fillStyle = particle.color;
      this.ctx.beginPath();
      this.ctx.arc(
        particle.position.x,
        particle.position.y,
        4 * particle.scale * pulseScale,
        0,
        Math.PI * 2
      );
      this.ctx.fill();
      
      // Inner glow
      const glowGradient = this.ctx.createRadialGradient(
        particle.position.x, particle.position.y, 0,
        particle.position.x, particle.position.y, 8 * particle.scale
      );
      glowGradient.addColorStop(0, `rgba(255, 255, 255, ${0.3 * particle.opacity})`);
      glowGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
      this.ctx.fillStyle = glowGradient;
      this.ctx.fill();
      
      this.ctx.restore();
    });
    
    // Update and render connections
    this.connections.forEach(connection => {
      connection.animate(deltaTime, this.mousePosition);
      connection.render(this.ctx);
    });
    
    // Render symbolic repair flash
    if (this.renderRepairFlash) {
      this.ctx.save();
      this.ctx.fillStyle = `rgba(14, 165, 164, ${0.3 * (1 - (this.frame % 30) / 30)})`;
      this.ctx.fillRect(0, 0, this.width, this.height);
      this.ctx.restore();
    }
    
    // Debug overlay (remove in production)
    if (window.LUKHAS_DEBUG) {
      this.renderDebugOverlay();
    }
    
    // Continue animation
    requestAnimationFrame((time) => this.animate(time));
  }
  
  renderDebugOverlay() {
    this.ctx.save();
    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    this.ctx.font = '12px monospace';
    this.ctx.fillText(`Drift: ${this.consciousnessState.drift.toFixed(3)}`, 10, 20);
    this.ctx.fillText(`Resonance: ${this.consciousnessState.resonance.toFixed(3)}`, 10, 35);
    this.ctx.fillText(`Connections: ${this.performanceMetrics.connectionCount}`, 10, 50);
    this.ctx.fillText(`FPS: ${(1000 / (this.lastTime - this.lastFrame)).toFixed(1)}`, 10, 65);
    this.ctx.restore();
    
    this.lastFrame = this.lastTime;
  }
  
  start() {
    this.animate(0);
  }
}

// Initialize animation
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('lukhas-hero-canvas');
  if (!canvas) return;
  
  // Set canvas size
  canvas.width = canvas.offsetWidth * window.devicePixelRatio;
  canvas.height = canvas.offsetHeight * window.devicePixelRatio;
  canvas.style.width = canvas.offsetWidth + 'px';
  canvas.style.height = canvas.offsetHeight + 'px';
  
  // Start EQNOX Mesh animation
  const meshAnimation = new EQNOXMeshAnimation(canvas);
  meshAnimation.start();
  
  // Expose for external control
  window.LUKHAS_MESH = meshAnimation;
});
```

---

## Accessibility & Performance

### Reduced Motion Support

```javascript
// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (prefersReducedMotion) {
  // Static fallback with single frame
  class StaticMesh {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      
      // Render single static frame
      this.renderStaticFrame();
    }
    
    renderStaticFrame() {
      // Draw static Nimbus
      const gradient = this.ctx.createRadialGradient(
        this.canvas.width / 2, this.canvas.height / 2, 0,
        this.canvas.width / 2, this.canvas.height / 2, 200
      );
      gradient.addColorStop(0, 'rgba(122, 89, 255, 0.15)');
      gradient.addColorStop(1, 'rgba(14, 165, 164, 0.05)');
      
      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(this.canvas.width / 2, this.canvas.height / 2, 200, 0, Math.PI * 2);
      this.ctx.fill();
      
      // Draw static particles
      const nodeCount = 24;
      const goldenAngle = Math.PI * (3 - Math.sqrt(5));
      
      for (let i = 0; i < nodeCount; i++) {
        const angle = i * goldenAngle;
        const radius = Math.sqrt(i / nodeCount) * 150;
        
        const x = this.canvas.width / 2 + Math.cos(angle) * radius;
        const y = this.canvas.height / 2 + Math.sin(angle) * radius;
        
        this.ctx.fillStyle = 'rgba(122, 89, 255, 0.6)';
        this.ctx.beginPath();
        this.ctx.arc(x, y, 4, 0, Math.PI * 2);
        this.ctx.fill();
      }
      
      // Draw minimal connections
      // (Selected connections only, no animation)
    }
  }
}
```

### Performance Optimization

```javascript
// WebGL fallback for high particle counts
class EQNOXMeshWebGL {
  constructor(canvas) {
    this.gl = canvas.getContext('webgl2');
    if (!this.gl) {
      // Fallback to Canvas2D
      return new EQNOXMeshAnimation(canvas);
    }
    
    // WebGL implementation for 100+ particles
    this.initShaders();
    this.initBuffers();
  }
  
  // ... WebGL implementation
}
```

---

## Motion Timing Functions

```javascript
// LUKHAS-specific easing functions
const Easings = {
  // Consciousness awakening (slow start, natural acceleration)
  consciousness: (t) => {
    return t < 0.5
      ? 2 * t * t
      : 1 - Math.pow(-2 * t + 2, 2) / 2;
  },
  
  // GLYPH transmission (quick burst, slow settle)
  glyphTransmit: (t) => {
    return 1 - Math.pow(1 - t, 3);
  },
  
  // Drift correction (aggressive snap-back)
  driftCorrection: (t) => {
    return Math.pow(t, 0.5);
  },
  
  // Emotional resonance (organic pulse)
  emotionalPulse: (t) => {
    return Math.sin(t * Math.PI);
  }
};
```

---

## Integration with Scene Timeline

### Scene 3 Specific Timing (2s window)

```javascript
const Scene3Timeline = {
  0.0: {
    action: 'initializeParticles',
    particleOpacity: 0.0,
    connectionOpacity: 0.0,
    nimbus: { glow: 0.03 }
  },
  0.2: {
    action: 'fadeInParticles',
    particleOpacity: 0.6,
    connectionOpacity: 0.0,
    nimbus: { glow: 0.05 }
  },
  0.5: {
    action: 'startConnections',
    particleOpacity: 0.8,
    connectionOpacity: 0.0,
    nimbus: { glow: 0.08 },
    firstConnection: true
  },
  1.0: {
    action: 'expandNetwork',
    particleOpacity: 1.0,
    connectionOpacity: 0.3,
    activeConnections: 3,
    nimbus: { glow: 0.12 }
  },
  1.5: {
    action: 'fullResonance',
    particleOpacity: 1.0,
    connectionOpacity: 0.4,
    activeConnections: 7,
    glyphExchange: true,
    nimbus: { glow: 0.15 }
  },
  2.0: {
    action: 'transitionOut',
    fadeToNext: true
  }
};
```

---

## Export Settings for Production

### Canvas Recording Setup

```javascript
// For generating video files from canvas animation
class CanvasRecorder {
  constructor(canvas, fps = 24, duration = 2000) {
    this.canvas = canvas;
    this.fps = fps;
    this.duration = duration;
    this.frames = [];
    
    // Use MediaRecorder API
    this.stream = canvas.captureStream(fps);
    this.recorder = new MediaRecorder(this.stream, {
      mimeType: 'video/webm;codecs=vp9',
      videoBitsPerSecond: 8000000 // 8Mbps
    });
    
    this.chunks = [];
    
    this.recorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        this.chunks.push(e.data);
      }
    };
    
    this.recorder.onstop = () => {
      const blob = new Blob(this.chunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      
      // Download link
      const a = document.createElement('a');
      a.href = url;
      a.download = `lukhas_scene3_${Date.now()}.webm`;
      a.click();
    };
  }
  
  start() {
    this.recorder.start();
    setTimeout(() => this.stop(), this.duration);
  }
  
  stop() {
    this.recorder.stop();
  }
}
```

---

## Notes for Implementation

1. **Performance Targets**
   - 60fps on modern hardware (2020+)
   - 30fps minimum on mobile
   - < 50MB memory footprint
   - < 250ms initial render

2. **Browser Compatibility**
   - Chrome 90+, Firefox 88+, Safari 14+
   - Fallback to static image for IE/older browsers
   - Touch events for mobile interaction

3. **LUKHAS Integration Points**
   - DriftScore monitoring hooks
   - Consciousness state from actual system
   - Real GLYPH packet structure
   - QRG authentication visuals (Scene 6)

4. **Testing Checklist**
   - [ ] Particle count scaling (10-100 nodes)
   - [ ] Connection affinity calculations
   - [ ] Mouse interaction responsiveness
   - [ ] Memory leak prevention
   - [ ] Accessibility compliance
   - [ ] Export quality (1080p/1440p)

---

This motion specification provides production-ready code for the EQNOX Mesh animation with full LUKHAS consciousness integration.
