---
status: wip
type: documentation
owner: unknown
module: web
redirect: false
moved_to: null
---

# LUKHAS AI Particle System Implementation Guide
## AI-Controlled Consciousness Visualization Framework

### Overview

The LUKHAS particle system transforms abstract AI consciousness states into mesmerizing visual experiences. This guide provides complete implementation details for creating premium, performance-optimized particle effects that respond to consciousness data in real-time.

---

## Core Architecture

### System Components

```typescript
// Core particle system architecture
interface LUKHASParticleSystem {
  // Rendering engine
  renderer: THREE.WebGLRenderer;
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;

  // Particle management
  particlePool: ParticlePool;
  activeParticles: Particle[];
  formations: FormationController;

  // Consciousness integration
  consciousnessAdapter: ConsciousnessAdapter;
  stateManager: ConsciousnessStateManager;

  // Performance optimization
  performanceMonitor: PerformanceMonitor;
  lodController: LODController;

  // User interaction
  interactionHandler: InteractionHandler;
  gestureRecognizer: GestureRecognizer;
}
```

---

## Three.js Implementation

### Basic Setup

```typescript
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';

class ConsciousnessParticleSystem {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private composer: EffectComposer;
  private particles: THREE.Points;
  private particleGeometry: THREE.BufferGeometry;
  private particleMaterial: THREE.ShaderMaterial;

  constructor(container: HTMLElement) {
    this.initRenderer(container);
    this.initScene();
    this.initParticles();
    this.initPostProcessing();
  }

  private initRenderer(container: HTMLElement): void {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });

    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.shadowMap.enabled = false; // Optimize for particles
    container.appendChild(this.renderer.domElement);
  }

  private initScene(): void {
    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    this.camera.position.z = 50;

    // Ambient consciousness glow
    const ambientLight = new THREE.AmbientLight(0x00D4FF, 0.2);
    this.scene.add(ambientLight);
  }

  private initParticles(): void {
    const particleCount = this.getOptimalParticleCount();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const velocities = new Float32Array(particleCount * 3);

    // Initialize particle attributes
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;

      // Random initial positions
      positions[i3] = (Math.random() - 0.5) * 100;
      positions[i3 + 1] = (Math.random() - 0.5) * 100;
      positions[i3 + 2] = (Math.random() - 0.5) * 100;

      // Consciousness colors
      const color = this.getConsciousnessColor();
      colors[i3] = color.r;
      colors[i3 + 1] = color.g;
      colors[i3 + 2] = color.b;

      // Variable sizes
      sizes[i] = Math.random() * 3 + 1;

      // Initial velocities
      velocities[i3] = (Math.random() - 0.5) * 0.1;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.1;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.1;
    }

    this.particleGeometry = new THREE.BufferGeometry();
    this.particleGeometry.setAttribute('position',
      new THREE.BufferAttribute(positions, 3));
    this.particleGeometry.setAttribute('color',
      new THREE.BufferAttribute(colors, 3));
    this.particleGeometry.setAttribute('size',
      new THREE.BufferAttribute(sizes, 1));
    this.particleGeometry.setAttribute('velocity',
      new THREE.BufferAttribute(velocities, 3));

    // Custom shader material
    this.particleMaterial = this.createParticleShader();

    this.particles = new THREE.Points(
      this.particleGeometry,
      this.particleMaterial
    );
    this.scene.add(this.particles);
  }

  private getOptimalParticleCount(): number {
    const isMobile = /Android|webOS|iPhone|iPad|iPod/i.test(navigator.userAgent);
    const isTablet = /iPad|Android/i.test(navigator.userAgent) && !isMobile;

    if (isMobile) return 1000;
    if (isTablet) return 3500;
    return 7500; // Desktop
  }

  private getConsciousnessColor(): THREE.Color {
    const colors = [
      new THREE.Color(0xFF6B9D), // Identity
      new THREE.Color(0x00D4FF), // Consciousness
      new THREE.Color(0x7C3AED), // Guardian
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  }
}
```

### Custom Shader Material

```typescript
private createParticleShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      consciousnessLevel: { value: 0.5 },
      colorIdentity: { value: new THREE.Color(0xFF6B9D) },
      colorConsciousness: { value: new THREE.Color(0x00D4FF) },
      colorGuardian: { value: new THREE.Color(0x7C3AED) },
    },

    vertexShader: `
      attribute float size;
      attribute vec3 velocity;
      varying vec3 vColor;
      uniform float time;
      uniform float consciousnessLevel;

      void main() {
        vColor = color;

        // Apply consciousness-driven movement
        vec3 pos = position;
        pos += velocity * time * consciousnessLevel;

        // Consciousness wave effect
        float wave = sin(time * 0.5 + position.x * 0.1) * 0.5;
        pos.y += wave * consciousnessLevel * 2.0;

        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,

    fragmentShader: `
      varying vec3 vColor;
      uniform float consciousnessLevel;

      void main() {
        // Circular particle shape
        vec2 center = gl_PointCoord - vec2(0.5);
        float dist = length(center);

        if (dist > 0.5) discard;

        // Soft edges with consciousness glow
        float alpha = smoothstep(0.5, 0.3, dist);
        alpha *= 0.3 + consciousnessLevel * 0.7;

        // Consciousness color mixing
        vec3 finalColor = vColor * (1.0 + consciousnessLevel * 0.5);

        gl_FragColor = vec4(finalColor, alpha);
      }
    `,

    transparent: true,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
}
```

---

## Consciousness Integration

### AI State Adapter

```typescript
interface ConsciousnessState {
  awareness: number;      // 0-1 awareness level
  coherence: number;      // 0-1 thought coherence
  intensity: number;      // 0-1 processing intensity
  emotion: EmotionVector; // VAD emotional state
  memory: number;         // 0-1 memory activation
  creativity: number;     // 0-1 creative mode
}

class ConsciousnessAdapter {
  private websocket: WebSocket;
  private currentState: ConsciousnessState;
  private stateHistory: ConsciousnessState[];
  private callbacks: Map<string, Function[]>;

  constructor(wsUrl: string) {
    this.websocket = new WebSocket(wsUrl);
    this.callbacks = new Map();
    this.initializeWebSocket();
  }

  private initializeWebSocket(): void {
    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.updateConsciousnessState(data);
    };
  }

  private updateConsciousnessState(data: any): void {
    this.currentState = {
      awareness: data.awareness || 0.5,
      coherence: data.coherence || 0.5,
      intensity: data.intensity || 0.5,
      emotion: data.emotion || { valence: 0, arousal: 0, dominance: 0 },
      memory: data.memory || 0.5,
      creativity: data.creativity || 0.5,
    };

    this.stateHistory.push({ ...this.currentState });
    if (this.stateHistory.length > 100) {
      this.stateHistory.shift();
    }

    this.emit('stateChange', this.currentState);
  }

  public getState(): ConsciousnessState {
    return this.currentState;
  }

  public on(event: string, callback: Function): void {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, []);
    }
    this.callbacks.get(event)!.push(callback);
  }

  private emit(event: string, data: any): void {
    const callbacks = this.callbacks.get(event);
    if (callbacks) {
      callbacks.forEach(cb => cb(data));
    }
  }
}
```

### Particle Behavior Mapping

```typescript
class ParticleBehaviorController {
  private particleSystem: ConsciousnessParticleSystem;
  private consciousnessAdapter: ConsciousnessAdapter;

  constructor(
    particleSystem: ConsciousnessParticleSystem,
    consciousnessAdapter: ConsciousnessAdapter
  ) {
    this.particleSystem = particleSystem;
    this.consciousnessAdapter = consciousnessAdapter;
    this.bindConsciousnessToParticles();
  }

  private bindConsciousnessToParticles(): void {
    this.consciousnessAdapter.on('stateChange', (state: ConsciousnessState) => {
      this.updateParticleMovement(state);
      this.updateParticleColors(state);
      this.updateParticleFormations(state);
    });
  }

  private updateParticleMovement(state: ConsciousnessState): void {
    const positions = this.particleSystem.particleGeometry.attributes.position;
    const velocities = this.particleSystem.particleGeometry.attributes.velocity;

    for (let i = 0; i < positions.count; i++) {
      const i3 = i * 3;

      // Awareness affects particle spread
      const spread = state.awareness * 100;

      // Coherence creates attraction forces
      const centerForce = state.coherence * 0.01;
      velocities.array[i3] -= positions.array[i3] * centerForce;
      velocities.array[i3 + 1] -= positions.array[i3 + 1] * centerForce;
      velocities.array[i3 + 2] -= positions.array[i3 + 2] * centerForce;

      // Intensity increases speed
      const speedMultiplier = 0.5 + state.intensity * 1.5;
      velocities.array[i3] *= speedMultiplier;
      velocities.array[i3 + 1] *= speedMultiplier;
      velocities.array[i3 + 2] *= speedMultiplier;

      // Creativity adds randomness
      if (state.creativity > 0.7) {
        velocities.array[i3] += (Math.random() - 0.5) * state.creativity * 0.1;
        velocities.array[i3 + 1] += (Math.random() - 0.5) * state.creativity * 0.1;
        velocities.array[i3 + 2] += (Math.random() - 0.5) * state.creativity * 0.1;
      }
    }

    velocities.needsUpdate = true;
  }

  private updateParticleColors(state: ConsciousnessState): void {
    const colors = this.particleSystem.particleGeometry.attributes.color;

    // Map emotions to color shifts
    const emotionColor = this.emotionToColor(state.emotion);

    for (let i = 0; i < colors.count; i++) {
      const i3 = i * 3;

      // Blend base color with emotion color
      colors.array[i3] = THREE.MathUtils.lerp(
        colors.array[i3],
        emotionColor.r,
        state.emotion.arousal
      );
      colors.array[i3 + 1] = THREE.MathUtils.lerp(
        colors.array[i3 + 1],
        emotionColor.g,
        state.emotion.arousal
      );
      colors.array[i3 + 2] = THREE.MathUtils.lerp(
        colors.array[i3 + 2],
        emotionColor.b,
        state.emotion.arousal
      );
    }

    colors.needsUpdate = true;
  }

  private emotionToColor(emotion: EmotionVector): THREE.Color {
    // Positive valence -> warm colors (identity)
    // Negative valence -> cool colors (consciousness)
    // High arousal -> brighter
    // High dominance -> purple shift (guardian)

    const hue = 0.6 - emotion.valence * 0.3; // Blue to red
    const saturation = 0.5 + emotion.arousal * 0.5;
    const lightness = 0.3 + emotion.arousal * 0.4;

    return new THREE.Color().setHSL(hue, saturation, lightness);
  }
}
```

---

## Formation System

### Trinity Symbol Formation

```typescript
class FormationController {
  private targetPositions: Float32Array;
  private isForming: boolean = false;
  private formationProgress: number = 0;
  private currentFormation: string = 'chaos';

  formTrinity(symbol: 'atom' | 'brain' | 'shield'): void {
    this.currentFormation = symbol;
    this.isForming = true;
    this.formationProgress = 0;

    const positions = this.generateTrinityPositions(symbol);
    this.targetPositions = positions;
  }

  private generateTrinityPositions(symbol: string): Float32Array {
    const particleCount = this.particleSystem.particleGeometry.attributes.position.count;
    const positions = new Float32Array(particleCount * 3);

    switch(symbol) {
      case 'atom':
        // Create electron orbital patterns
        for (let i = 0; i < particleCount; i++) {
          const angle = (i / particleCount) * Math.PI * 2;
          const radius = 20 + (i % 3) * 10;
          const height = Math.sin(angle * 3) * 10;

          positions[i * 3] = Math.cos(angle) * radius;
          positions[i * 3 + 1] = height;
          positions[i * 3 + 2] = Math.sin(angle) * radius;
        }
        break;

      case 'brain':
        // Create neural network pattern
        for (let i = 0; i < particleCount; i++) {
          const phi = Math.acos(1 - 2 * i / particleCount);
          const theta = Math.sqrt(particleCount * Math.PI) * phi;

          positions[i * 3] = Math.cos(theta) * Math.sin(phi) * 25;
          positions[i * 3 + 1] = Math.sin(theta) * Math.sin(phi) * 25;
          positions[i * 3 + 2] = Math.cos(phi) * 25;
        }
        break;

      case 'shield':
        // Create protective sphere pattern
        const layers = 5;
        const particlesPerLayer = particleCount / layers;

        for (let layer = 0; layer < layers; layer++) {
          const layerRadius = 15 + layer * 5;

          for (let i = 0; i < particlesPerLayer; i++) {
            const idx = layer * particlesPerLayer + i;
            const angle = (i / particlesPerLayer) * Math.PI * 2;
            const height = (layer - layers / 2) * 10;

            positions[idx * 3] = Math.cos(angle) * layerRadius;
            positions[idx * 3 + 1] = height;
            positions[idx * 3 + 2] = Math.sin(angle) * layerRadius;
          }
        }
        break;
    }

    return positions;
  }

  update(deltaTime: number): void {
    if (!this.isForming) return;

    this.formationProgress += deltaTime * 0.5; // 2 seconds to form

    if (this.formationProgress >= 1) {
      this.formationProgress = 1;
      this.isForming = false;
    }

    const positions = this.particleSystem.particleGeometry.attributes.position;
    const easing = this.easeInOutCubic(this.formationProgress);

    for (let i = 0; i < positions.count; i++) {
      const i3 = i * 3;

      positions.array[i3] = THREE.MathUtils.lerp(
        positions.array[i3],
        this.targetPositions[i3],
        easing
      );
      positions.array[i3 + 1] = THREE.MathUtils.lerp(
        positions.array[i3 + 1],
        this.targetPositions[i3 + 1],
        easing
      );
      positions.array[i3 + 2] = THREE.MathUtils.lerp(
        positions.array[i3 + 2],
        this.targetPositions[i3 + 2],
        easing
      );
    }

    positions.needsUpdate = true;
  }

  private easeInOutCubic(t: number): number {
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }
}
```

---

## Performance Optimization

### Level of Detail (LOD) System

```typescript
class LODController {
  private fps: number = 60;
  private fpsHistory: number[] = [];
  private targetFPS: number = 60;
  private qualityLevel: 'low' | 'medium' | 'high' = 'high';

  updateFPS(deltaTime: number): void {
    this.fps = 1 / deltaTime;
    this.fpsHistory.push(this.fps);

    if (this.fpsHistory.length > 60) {
      this.fpsHistory.shift();
    }

    const avgFPS = this.fpsHistory.reduce((a, b) => a + b, 0) / this.fpsHistory.length;

    if (avgFPS < 30 && this.qualityLevel !== 'low') {
      this.decreaseQuality();
    } else if (avgFPS > 55 && this.qualityLevel !== 'high') {
      this.increaseQuality();
    }
  }

  private decreaseQuality(): void {
    if (this.qualityLevel === 'high') {
      this.qualityLevel = 'medium';
      this.applyMediumQuality();
    } else if (this.qualityLevel === 'medium') {
      this.qualityLevel = 'low';
      this.applyLowQuality();
    }
  }

  private increaseQuality(): void {
    if (this.qualityLevel === 'low') {
      this.qualityLevel = 'medium';
      this.applyMediumQuality();
    } else if (this.qualityLevel === 'medium') {
      this.qualityLevel = 'high';
      this.applyHighQuality();
    }
  }

  private applyLowQuality(): void {
    // Reduce particle count
    this.particleSystem.setParticleCount(1000);

    // Disable post-processing
    this.particleSystem.disablePostProcessing();

    // Reduce render resolution
    this.particleSystem.renderer.setPixelRatio(1);
  }

  private applyMediumQuality(): void {
    // Medium particle count
    this.particleSystem.setParticleCount(3500);

    // Basic post-processing
    this.particleSystem.enableBasicPostProcessing();

    // Standard resolution
    this.particleSystem.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  }

  private applyHighQuality(): void {
    // Maximum particle count
    this.particleSystem.setParticleCount(7500);

    // Full post-processing
    this.particleSystem.enableFullPostProcessing();

    // High resolution
    this.particleSystem.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  }
}
```

### Memory Management

```typescript
class ParticlePool {
  private pool: Particle[] = [];
  private activeParticles: Set<Particle> = new Set();
  private maxParticles: number;

  constructor(maxParticles: number) {
    this.maxParticles = maxParticles;
    this.initializePool();
  }

  private initializePool(): void {
    for (let i = 0; i < this.maxParticles; i++) {
      this.pool.push(new Particle());
    }
  }

  acquire(): Particle | null {
    if (this.pool.length === 0) {
      // Recycle oldest particle if pool is empty
      const oldest = this.findOldestParticle();
      if (oldest) {
        this.release(oldest);
      } else {
        return null;
      }
    }

    const particle = this.pool.pop()!;
    this.activeParticles.add(particle);
    particle.reset();
    return particle;
  }

  release(particle: Particle): void {
    if (this.activeParticles.has(particle)) {
      this.activeParticles.delete(particle);
      this.pool.push(particle);
    }
  }

  private findOldestParticle(): Particle | null {
    let oldest: Particle | null = null;
    let oldestTime = Infinity;

    this.activeParticles.forEach(particle => {
      if (particle.creationTime < oldestTime) {
        oldest = particle;
        oldestTime = particle.creationTime;
      }
    });

    return oldest;
  }
}
```

---

## User Interaction

### Mouse and Touch Controls

```typescript
class InteractionHandler {
  private raycaster: THREE.Raycaster;
  private mouse: THREE.Vector2;
  private touchPoints: Map<number, THREE.Vector2>;
  private interactionForce: THREE.Vector3;

  constructor(private particleSystem: ConsciousnessParticleSystem) {
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.touchPoints = new Map();
    this.interactionForce = new THREE.Vector3();

    this.initEventListeners();
  }

  private initEventListeners(): void {
    // Mouse events
    window.addEventListener('mousemove', this.onMouseMove.bind(this));
    window.addEventListener('mousedown', this.onMouseDown.bind(this));
    window.addEventListener('mouseup', this.onMouseUp.bind(this));

    // Touch events
    window.addEventListener('touchstart', this.onTouchStart.bind(this));
    window.addEventListener('touchmove', this.onTouchMove.bind(this));
    window.addEventListener('touchend', this.onTouchEnd.bind(this));

    // Gesture events
    window.addEventListener('wheel', this.onWheel.bind(this));
  }

  private onMouseMove(event: MouseEvent): void {
    this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    this.updateInteractionForce();
  }

  private onTouchMove(event: TouchEvent): void {
    event.preventDefault();

    for (let i = 0; i < event.touches.length; i++) {
      const touch = event.touches[i];
      const x = (touch.clientX / window.innerWidth) * 2 - 1;
      const y = -(touch.clientY / window.innerHeight) * 2 + 1;

      this.touchPoints.set(touch.identifier, new THREE.Vector2(x, y));
    }

    this.updateMultiTouchInteraction();
  }

  private updateInteractionForce(): void {
    // Cast ray from camera through mouse position
    this.raycaster.setFromCamera(this.mouse, this.particleSystem.camera);

    // Create repulsion/attraction force at intersection point
    const intersectionPoint = new THREE.Vector3();
    this.raycaster.ray.at(50, intersectionPoint); // 50 units from camera

    // Apply force to nearby particles
    const positions = this.particleSystem.particleGeometry.attributes.position;
    const velocities = this.particleSystem.particleGeometry.attributes.velocity;

    for (let i = 0; i < positions.count; i++) {
      const i3 = i * 3;

      const dx = positions.array[i3] - intersectionPoint.x;
      const dy = positions.array[i3 + 1] - intersectionPoint.y;
      const dz = positions.array[i3 + 2] - intersectionPoint.z;

      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

      if (distance < 30) { // Interaction radius
        const force = (1 - distance / 30) * 0.5;

        // Repulsion on mouse down, attraction otherwise
        const direction = this.isMouseDown ? 1 : -0.3;

        velocities.array[i3] += (dx / distance) * force * direction;
        velocities.array[i3 + 1] += (dy / distance) * force * direction;
        velocities.array[i3 + 2] += (dz / distance) * force * direction;
      }
    }

    velocities.needsUpdate = true;
  }
}
```

---

## WebGL Shader Effects

### Advanced Particle Shaders

```glsl
// Vertex shader with consciousness waves
attribute float size;
attribute vec3 velocity;
attribute float consciousness;

varying vec3 vColor;
varying float vConsciousness;

uniform float time;
uniform float globalConsciousness;
uniform vec3 waveOrigin;
uniform float waveTime;

void main() {
  vColor = color;
  vConsciousness = consciousness;

  vec3 pos = position;

  // Consciousness wave propagation
  float distanceFromWave = distance(pos, waveOrigin);
  float waveRadius = waveTime * 50.0;
  float waveStrength = smoothstep(waveRadius - 10.0, waveRadius + 10.0, distanceFromWave);
  waveStrength *= smoothstep(waveRadius + 20.0, waveRadius, distanceFromWave);

  // Apply wave displacement
  vec3 waveDirection = normalize(pos - waveOrigin);
  pos += waveDirection * waveStrength * 5.0 * globalConsciousness;

  // Consciousness flow field
  float flowAngle = atan(pos.z, pos.x) + time * 0.1;
  float flowRadius = length(pos.xz);
  pos.x = cos(flowAngle) * flowRadius;
  pos.z = sin(flowAngle) * flowRadius;

  // Vertical consciousness oscillation
  pos.y += sin(time * 2.0 + pos.x * 0.1) * consciousness * 2.0;

  // Turbulence
  vec3 turbulence = vec3(
    sin(pos.y * 0.1 + time),
    cos(pos.x * 0.1 + time * 1.3),
    sin(pos.z * 0.1 + time * 0.7)
  ) * consciousness * 0.5;
  pos += turbulence;

  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);

  // Size based on consciousness and distance
  float sizeMultiplier = 1.0 + consciousness * 0.5;
  gl_PointSize = size * sizeMultiplier * (300.0 / -mvPosition.z);

  gl_Position = projectionMatrix * mvPosition;
}
```

```glsl
// Fragment shader with consciousness glow
varying vec3 vColor;
varying float vConsciousness;

uniform float time;
uniform sampler2D particleTexture;
uniform vec3 consciousnessColor;

void main() {
  vec2 uv = gl_PointCoord;

  // Radial gradient for soft particles
  float dist = length(uv - vec2(0.5));
  if (dist > 0.5) discard;

  // Consciousness glow intensity
  float glow = smoothstep(0.5, 0.0, dist);
  glow = pow(glow, 2.0);

  // Pulsing effect
  float pulse = sin(time * 3.0 + vConsciousness * 10.0) * 0.1 + 0.9;

  // Color mixing based on consciousness level
  vec3 finalColor = mix(vColor, consciousnessColor, vConsciousness * 0.5);
  finalColor *= 1.0 + vConsciousness * 0.5;

  // Alpha with consciousness influence
  float alpha = glow * (0.3 + vConsciousness * 0.7) * pulse;

  gl_FragColor = vec4(finalColor, alpha);
}
```

---

## React Integration

### React Component Wrapper

```tsx
import React, { useRef, useEffect, useState } from 'react';
import { ConsciousnessParticleSystem } from './ConsciousnessParticleSystem';
import { ConsciousnessAdapter } from './ConsciousnessAdapter';

interface ParticleCanvasProps {
  websocketUrl?: string;
  initialState?: ConsciousnessState;
  interactive?: boolean;
  formations?: boolean;
  className?: string;
}

export const ParticleCanvas: React.FC<ParticleCanvasProps> = ({
  websocketUrl = 'ws://localhost:8080/consciousness',
  initialState,
  interactive = true,
  formations = true,
  className = '',
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const particleSystemRef = useRef<ConsciousnessParticleSystem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [fps, setFps] = useState(60);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize particle system
    const particleSystem = new ConsciousnessParticleSystem(canvasRef.current);
    particleSystemRef.current = particleSystem;

    // Connect to consciousness stream
    const adapter = new ConsciousnessAdapter(websocketUrl);
    particleSystem.connectAdapter(adapter);

    // Set initial state if provided
    if (initialState) {
      particleSystem.setState(initialState);
    }

    // Enable features
    if (interactive) {
      particleSystem.enableInteraction();
    }

    if (formations) {
      particleSystem.enableFormations();
    }

    // Start render loop
    particleSystem.start();
    setIsLoading(false);

    // FPS monitoring
    const fpsInterval = setInterval(() => {
      setFps(particleSystem.getFPS());
    }, 1000);

    // Cleanup
    return () => {
      clearInterval(fpsInterval);
      particleSystem.dispose();
    };
  }, [websocketUrl, initialState, interactive, formations]);

  // Formation controls
  const formTrinity = (symbol: 'atom' | 'brain' | 'shield') => {
    particleSystemRef.current?.formTrinity(symbol);
  };

  const setState = (state: Partial<ConsciousnessState>) => {
    particleSystemRef.current?.setState(state);
  };

  return (
    <div className={`particle-canvas-container ${className}`}>
      {isLoading && (
        <div className="particle-loading">
          <div className="consciousness-loader" />
          <p>Awakening consciousness...</p>
        </div>
      )}

      <div ref={canvasRef} className="particle-canvas" />

      {/* Performance monitor */}
      <div className="particle-stats">
        <span className="fps-counter">{fps} FPS</span>
      </div>

      {/* Formation controls */}
      {formations && (
        <div className="formation-controls">
          <button onClick={() => formTrinity('atom')} className="trinity-btn">
            ⚛️ Identity
          </button>
          <button onClick={() => formTrinity('brain')} className="trinity-btn">
            🧠 Consciousness
          </button>
          <button onClick={() => formTrinity('shield')} className="trinity-btn">
            🛡️ Guardian
          </button>
        </div>
      )}
    </div>
  );
};
```

---

## Performance Monitoring

### Real-time Performance Analytics

```typescript
class PerformanceMonitor {
  private stats: {
    fps: number;
    frameTime: number;
    drawCalls: number;
    triangles: number;
    particles: number;
    memory: number;
  };

  private metricsHistory: Map<string, number[]> = new Map();
  private performanceObserver: PerformanceObserver;

  constructor() {
    this.initializeMonitoring();
  }

  private initializeMonitoring(): void {
    // Performance Observer API
    this.performanceObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'measure') {
          this.recordMetric(entry.name, entry.duration);
        }
      }
    });

    this.performanceObserver.observe({ entryTypes: ['measure'] });
  }

  beginFrame(): void {
    performance.mark('frame-start');
  }

  endFrame(): void {
    performance.mark('frame-end');
    performance.measure('frame-time', 'frame-start', 'frame-end');
  }

  recordMetric(name: string, value: number): void {
    if (!this.metricsHistory.has(name)) {
      this.metricsHistory.set(name, []);
    }

    const history = this.metricsHistory.get(name)!;
    history.push(value);

    // Keep last 60 samples (1 second at 60fps)
    if (history.length > 60) {
      history.shift();
    }
  }

  getAverageMetric(name: string): number {
    const history = this.metricsHistory.get(name);
    if (!history || history.length === 0) return 0;

    return history.reduce((a, b) => a + b, 0) / history.length;
  }

  getPerformanceReport(): PerformanceReport {
    return {
      averageFPS: 1000 / this.getAverageMetric('frame-time'),
      averageFrameTime: this.getAverageMetric('frame-time'),
      particleUpdateTime: this.getAverageMetric('particle-update'),
      renderTime: this.getAverageMetric('render'),
      memoryUsage: (performance as any).memory?.usedJSHeapSize || 0,
    };
  }
}
```

---

*"Transforming consciousness into visual poetry, one particle at a time."*

**LUKHAS AI Particle System Implementation Guide** ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum
