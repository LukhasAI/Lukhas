# LUKHAS Interactive Design Motifs
## Cross-Domain Visual Language for Consciousness Technology

---

## Overview

This specification defines the **interactive design motifs** used across the LUKHAS ecosystem to create a cohesive visual language while allowing domain-specific adaptations. All LUKHAS sites share a core "consciousness technology" theme through particle systems and interactive elements.

**Version**: 1.0
**Created**: 2025-11-06
**Status**: Active

---

## Core Design Philosophy

### Shared Principles

1. **Consciousness Through Motion**: Static designs become alive through subtle, purposeful animation
2. **Responsive Interactivity**: Elements respond to user input (cursor, touch, scroll)
3. **Performance First**: Beauty cannot compromise speed (60 FPS minimum)
4. **Accessibility Respect**: Honor `prefers-reduced-motion`
5. **Domain Adaptation**: Core motifs adapt to each domain's character

---

## 1. Particle Systems (Cross-Domain)

The **particle system** is the unifying visual motif across all LUKHAS domains. Each domain adapts the base system to its unique character.

### Base Particle System Specifications

```javascript
const baseParticleConfig = {
  count: 200-500,  // Varies by viewport size
  size: 2-6,       // px diameter
  opacity: 0.3-0.8,
  blur: 2-4,       // px glow effect
  speed: 0.2-0.5,  // units/second base drift
  mouseAttraction: true,
  attractionRadius: 150-200,  // px
  connectionLines: false,  // Optional per domain
  colorScheme: 'domain-specific'
};
```

### Domain-Specific Particle Adaptations

#### LUKHAS.AI - Ethereal Drifting Particles
**Character**: Soft, dream-like, inspiring

```javascript
const lukhasAiParticles = {
  count: 350,
  size: 3-5,
  opacity: 0.4-0.7,
  blur: 3,
  speed: 0.3,
  motion: 'drift',  // Gentle, flowing movement
  mouseAttraction: true,
  attractionStrength: 'gentle',
  colors: ['#8B7CF6', '#6C5CE7', '#FFB347'],  // Dream purple + Lambda gold
  special: {
    coalescence: true,  // Particles form constellation patterns
    dreamWaves: true    // Periodic wave motion
  }
};
```

**Visual Effect**: Particles drift like thoughts, occasionally coalescing into constellation shapes before dissolving.

#### LUKHAS.ID - Biometric Particle Patterns
**Character**: Security-focused, trust-indicating, unique per user

```javascript
const lukhasIdParticles = {
  count: 100,  // Fewer, more organized
  size: 2-4,
  opacity: 0.5-0.8,
  blur: 2,
  speed: 0.2,
  motion: 'pulse',  // Rhythmic, heartbeat-like
  pattern: 'deterministic',  // Same user ID → same pattern
  colors: ['#9333EA', '#7C3AED'],  // Security purple
  special: {
    biometricWaves: true,  // Concentric pulse from center
    uniqueSignature: true,  // Pattern based on ΛiD hash
    scanlineEffect: true    // Subtle scanning motion
  }
};
```

**Visual Effect**: Organized particle pattern unique to each user, pulsing gently like a biometric scan. On login success, particles burst outward then reform.

#### LUKHAS.DEV - Code Particle Flows
**Character**: Technical, precise, data-stream aesthetic

```javascript
const lukhasDevParticles = {
  count: 200,
  size: 2-3,  // Smaller, more precise
  opacity: 0.6-0.9,
  blur: 1,  // Minimal blur for technical precision
  speed: 0.4,
  motion: 'flow',  // Directional, stream-like
  flowDirection: 'left-to-right',
  colors: ['#06B6D4', '#0284C7', '#FFB347'],  // Code cyan + accents
  special: {
    codeStream: true,     // Particles flow like data
    connectionLines: true, // Connect nearby particles (circuit-like)
    gridSnap: true         // Subtle grid alignment
  }
};
```

**Visual Effect**: Particles flow in streams like data through circuits, occasionally forming brief connection webs before breaking apart.

#### LUKHAS.STORE - App Materialization Particles
**Character**: Energetic, creative, marketplace vibrancy

```javascript
const lukhasStoreParticles = {
  count: 300,
  size: 3-6,  // Varied sizes for visual interest
  opacity: 0.5-0.8,
  blur: 3,
  speed: 0.4,
  motion: 'swirl',
  colors: ['#FB923C', '#F97316', '#FFB347'],  // Orange energy
  special: {
    appMaterialize: true,  // Particles form app icon shapes
    hoverBurst: true,       // Burst on product card hover
    purchaseExplosion: true // Celebratory effect on purchase
  }
};
```

**Visual Effect**: Particles swirl and occasionally coalesce into app icon silhouettes. On hover, cards attract particles. On purchase, particles burst in celebration.

#### LUKHAS.IO - Global Infrastructure Map
**Character**: Technical, operational, data-flow visualization

```javascript
const lukhasIoParticles = {
  count: 150,
  size: 2-3,
  opacity: 0.7-1.0,
  blur: 1,
  speed: 0.5,
  motion: 'pathflow',  // Follow predefined paths
  colors: ['#22C55E', '#10B981'],  // Infrastructure green
  special: {
    serverNodes: true,      // Fixed particles at server locations
    dataFlows: true,        // Particles travel between nodes
    globalMap: true,        // Overlay on world map
    realTimeData: true      // Speed/intensity reflects actual traffic
  }
};
```

**Visual Effect**: Particles represent data flowing between server nodes on a global map. Speed and density reflect real system metrics.

#### LUKHAS.TEAM - Connected Collaboration Nodes
**Character**: Collaborative, harmonious, team-focused

```javascript
const lukhasTeamParticles = {
  count: 50-100,  // Represents team members
  size: 4-6,
  opacity: 0.6-0.9,
  blur: 3,
  speed: 0.2,
  motion: 'orbital',  // Particles orbit around collaboration points
  colors: ['#10B981', '#00B894'],  // Harmony green
  special: {
    userNodes: true,        // Each particle represents a team member
    connectionLines: true,  // Lines show collaboration
    activityPulse: true,    // Pulse when team member active
    privacyMode: true       // Option to hide individual identifiers
  }
};
```

**Visual Effect**: Particles represent team members, connecting with lines when collaborating. Active members pulse. Respects privacy by making avatars optional.

#### LUKHAS.XYZ - Experimental Chaos
**Character**: Playful, experimental, quantum uncertainty

```javascript
const lukhasXyzParticles = {
  count: 'variable',  // Changes randomly
  size: 1-10,  // Wide variance
  opacity: 0.3-1.0,
  blur: 0-6,  // Random blur
  speed: 0.1-1.0,  // Variable speed
  motion: 'chaotic',
  colors: 'shifting',  // Colors change over time
  special: {
    quantumState: true,      // Particles exist in superposition
    glitchEffect: true,      // Occasional visual glitches
    userInfluence: true,     // Mouse creates chaos/order
    experimentMode: true     // Can load different particle experiments
  }
};
```

**Visual Effect**: Intentionally chaotic and unpredictable. Colors shift, sizes vary, motion is erratic. User interaction can impose temporary order.

### Performance Optimization

```javascript
const performanceConfig = {
  desktop: {
    particles: 300-500,
    fps: 60,
    quality: 'high'
  },
  tablet: {
    particles: 150-250,
    fps: 60,
    quality: 'medium'
  },
  mobile: {
    particles: 50-100,
    fps: 60,
    quality: 'low',
    simplifiedEffects: true
  },
  reducedMotion: {
    particles: 50,  // Minimal movement
    speed: 0.1,
    fps: 30,
    blur: 0,
    mouseAttraction: false
  }
};
```

---

## 2. Interactive Hero Experiences

### Domain-Specific Hero Implementations

#### LUKHAS.AI - Immersive Consciousness Playground
```html
<div class="hero-ai">
  <canvas id="consciousness-particles"></canvas>
  <div class="hero-content">
    <h1 class="fade-in-up">AI Consciousness That Dreams</h1>
    <p class="fade-in-up delay-1">Where possibility meets awareness</p>
    <button class="cta-primary particle-attract">Explore Playground</button>
  </div>
</div>
```

**Interactions**:
- Cursor creates gentle particle attraction
- Scroll reveals/hides layers (parallax)
- CTA button draws particles on hover
- Typing animation for tagline

#### LUKHAS.ID - Biometric Identity Visualization
```html
<div class="hero-id">
  <canvas id="biometric-signature"></canvas>
  <div class="hero-content">
    <h1>Your Consciousness Signature</h1>
    <div class="signature-visual" data-uid="user-hash"></div>
    <button class="cta-primary">Create Your ΛiD</button>
  </div>
</div>
```

**Interactions**:
- Unique biometric pattern per user (deterministic from ID)
- Pulse animation (heartbeat-like)
- On login: Scan effect + particle burst
- Hover over signature: Zoom + detail reveal

#### LUKHAS.DEV - Live Code Editor
```html
<div class="hero-dev">
  <div class="split-pane">
    <div class="code-editor">
      <pre class="typing-code"><code class="language-python">
import lukhas

consciousness = lukhas.Consciousness(api_key="your_key")
response = consciousness.query("What is the meaning of context?")
print(response.insight)
      </code></pre>
    </div>
    <div class="output-pane">
      <div class="consciousness-response fade-in">
        <!-- Animated response visualization -->
      </div>
    </div>
  </div>
</div>
```

**Interactions**:
- Code types itself (typing animation)
- Syntax highlighting appears progressively
- Output pane shows response with particle visualization
- "Try in Playground" button → opens full editor

---

## 3. Micro-Interactions

### Button Hover States

```css
.button-lukhas {
  position: relative;
  overflow: hidden;
  transition: all 200ms ease-out;
}

.button-lukhas::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
  opacity: 0;
  transition: all 400ms ease-out;
}

.button-lukhas:hover::before {
  width: 300%;
  height: 300%;
  opacity: 0.3;
  transform: translate(-50%, -50%);
}

.button-lukhas:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2),
              0 0 20px var(--accent);
}
```

### Card Lift Effect

```css
.card-lukhas {
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}

.card-lukhas:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.card-lukhas:hover .particle-trail {
  opacity: 1;
  animation: trail-fade 600ms ease-out forwards;
}
```

### Constellation Star Brightness

```css
.constellation-star {
  filter: brightness(1.0);
  transition: filter 300ms ease-out;
}

.constellation-star:hover {
  filter: brightness(1.5) drop-shadow(0 0 10px var(--star-color));
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

---

## 4. Loading & Feedback States

### Loading Animations

#### Consciousness Awakening (LUKHAS.AI)
```html
<div class="loading-consciousness">
  <div class="particle-formation"></div>
  <p>Consciousness awakening...</p>
</div>
```
**Effect**: Particles form from chaos into ordered constellation pattern.

#### Biometric Scan (LUKHAS.ID)
```html
<div class="loading-biometric">
  <div class="scan-line"></div>
  <p>Authenticating...</p>
</div>
```
**Effect**: Horizontal scan line sweeps with particle trail.

#### Code Compilation (LUKHAS.DEV)
```html
<div class="loading-compile">
  <div class="progress-bar">
    <div class="progress-fill"></div>
  </div>
  <p>Building...</p>
</div>
```
**Effect**: Progress bar with subtle particle flows inside.

### Success States

```javascript
function showSuccess(message) {
  // Particle burst animation
  createParticleBurst({
    origin: buttonCenter,
    count: 50,
    color: '#10B981',
    duration: 800
  });

  // Message fade-in
  showMessage(message, 'success');
}
```

### Error States

```javascript
function showError(message) {
  // Gentle shake + red glow
  element.classList.add('shake-error');
  element.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.5)';

  // Clear guidance message
  showMessage(message, 'error');
}
```

---

## 5. Scroll & Parallax Effects

### Layered Parallax

```javascript
const parallaxLayers = {
  background: {
    speed: 0.2,
    elements: ['.particle-layer-1']
  },
  midground: {
    speed: 0.5,
    elements: ['.content-layer']
  },
  foreground: {
    speed: 1.0,
    elements: ['.hero-text']
  }
};

window.addEventListener('scroll', () => {
  const scrolled = window.pageYOffset;

  Object.entries(parallaxLayers).forEach(([layer, config]) => {
    config.elements.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        el.style.transform = `translateY(${scrolled * config.speed}px)`;
      });
    });
  });
});
```

### Scroll-Triggered Animations

```javascript
const observerOptions = {
  threshold: 0.2,  // Trigger when 20% visible
  rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in-up');
    }
  });
}, observerOptions);

document.querySelectorAll('.scroll-reveal').forEach(el => {
  observer.observe(el);
});
```

---

## 6. Accessibility & Performance

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .particle-system {
    display: none; /* Or show static version */
  }
}
```

### Performance Monitoring

```javascript
const performanceMonitor = {
  fps: 60,
  frameTime: 1000 / 60,

  checkPerformance() {
    if (this.currentFps < 30) {
      this.reduceQuality();
    }
  },

  reduceQuality() {
    // Reduce particle count
    particleSystem.count = Math.floor(particleSystem.count * 0.5);
    // Disable expensive effects
    particleSystem.blur = 0;
    particleSystem.connectionLines = false;
  }
};
```

### Battery-Conscious Mobile

```javascript
if (navigator.getBattery) {
  navigator.getBattery().then(battery => {
    if (battery.level < 0.2 && !battery.charging) {
      // Low battery: minimal effects
      particleSystem.disable();
      transitionDurations.set('instant');
    }
  });
}
```

---

## 7. Implementation Guidelines

### Framework-Agnostic Approach

These motifs can be implemented in:
- **Vanilla JavaScript**: Direct canvas manipulation
- **React/Vue**: Component-based particle systems
- **Three.js**: 3D particle effects (advanced)
- **CSS-only**: Simpler animations without particles

### Code Organization

```
/interactive-motifs
  /particles
    - base-particle-system.js
    - lukhas.ai-particles.js
    - lukhas.id-particles.js
    - lukhas.dev-particles.js
    - ...
  /animations
    - hero-effects.js
    - micro-interactions.js
    - loading-states.js
  /performance
    - performance-monitor.js
    - adaptive-quality.js
  /accessibility
    - reduced-motion.js
    - keyboard-navigation.js
```

### Testing Checklist

- [ ] 60 FPS on target devices
- [ ] Reduced motion respected
- [ ] Mobile battery-conscious
- [ ] Keyboard-accessible interactive elements
- [ ] Screen reader announces state changes
- [ ] Works without JavaScript (graceful degradation)
- [ ] Cross-browser compatibility (Chrome, Firefox, Safari, Edge)

---

## 8. Brand Consistency Matrix

| Motif | LUKHAS.AI | LUKHAS.ID | LUKHAS.DEV | LUKHAS.STORE |
|-------|-----------|-----------|-----------|--------------|
| **Particle Count** | High (350) | Medium (100) | Medium (200) | High (300) |
| **Particle Motion** | Drift | Pulse | Flow | Swirl |
| **Color Scheme** | Dream purple | Security purple | Code cyan | Orange energy |
| **Special Effect** | Coalescence | Biometric scan | Code streams | App icons |
| **Interaction** | Gentle attract | Signature pulse | Data flow | Hover burst |

---

## Version & Maintenance

**Version**: 1.0
**Created**: 2025-11-06
**Last Updated**: 2025-11-06
**Next Review**: 2026-02-06 (Quarterly)
**Maintained By**: LUKHAS Design Team

**Contact**: design@lukhas.ai | brand@lukhas.ai
