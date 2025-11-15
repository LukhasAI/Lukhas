# LUKHAS Morphing System

**Adapted from PR0T3US Voice-Modulated Morphing System**

A TypeScript-based vertex morphing engine for creating consciousness-inspired 3D animations.

## Features

- **Smooth Shape Morphing**: Interpolate between predefined 3D shapes
- **Voice Modulation** (Optional): React to voice intensity and frequency
- **Constellation Framework Shapes**: Built-in shapes for LUKHAS branding
  - `sphere` - Default spherical shape
  - `consciousness` - Pulsating consciousness orb
  - `guardian` - Shield-like protective shape (lukhas.com)
  - `identity` - Lambda-inspired pointed marker (lukhas.id)
  - `neural` - Bio-inspired neural network pattern
  - `quantum` - Superposition wave patterns
  - `cat` - Demo shape from PR0T3US
- **Custom Shapes**: Register your own vertex modifier functions
- **Performance Optimized**: Efficient vertex processing for 60 FPS

---

## Quick Start

###  Basic Usage

```typescript
import { MorphingEngine } from '@lukhas/ui'

// Create engine
const engine = new MorphingEngine({
  morphSpeed: 0.02, // 0.01-1.0 (slower = smoother)
  initialShape: 'sphere',
  enableVoiceModulation: false,
})

// Get available shapes
console.log(engine.getAvailableShapes())
// ['sphere', 'consciousness', 'guardian', 'identity', 'neural', 'quantum', 'cat']

// Morph to a different shape
engine.setTargetShape('consciousness')

// In your animation loop
function animate(time: number) {
  engine.update() // Update morph progress

  const vertices = getYourVertices() // From WebGL buffer
  const morphed = engine.processVertices(vertices, time)

  // Use morphed vertices for rendering
  updateWebGLBuffer(morphed)

  requestAnimationFrame(animate)
}
```

---

## Usage with Three.js

```typescript
import * as THREE from 'three'
import { MorphingEngine } from '@lukhas/ui'

const engine = new MorphingEngine()
const geometry = new THREE.IcosahedronGeometry(10, 4)

function animate() {
  engine.update()

  // Process vertices
  const positions = geometry.attributes.position.array
  const morphed = engine.processVertices(Array.from(positions), Date.now() * 0.001)

  // Update geometry
  geometry.attributes.position.array.set(morphed)
  geometry.attributes.position.needsUpdate = true

  renderer.render(scene, camera)
  requestAnimationFrame(animate)
}
```

---

## Custom Shapes

```typescript
engine.registerShape('custom', {
  name: 'My Custom Shape',
  vertexModifier: (vertex, time, voiceData) => {
    const { x, y, z } = vertex
    const radius = 10.0

    // Your transformation logic
    return {
      x: x * radius,
      y: y * radius * (1 + Math.sin(time * 2) * 0.2),
      z: z * radius,
    }
  },
})

engine.setTargetShape('custom')
```

---

## Voice Modulation

```typescript
const engine = new MorphingEngine({
  enableVoiceModulation: true,
})

// Set voice data from audio analysis
engine.setVoiceData({
  intensity: audioLevel, // 0-1
  frequency: dominantFreq, // Hz
})
```

---

## API Reference

### `MorphingEngine(config?)`

**Constructor**

- `config.morphSpeed` - Morph speed (0.01-1.0, default: 0.02)
- `config.initialShape` - Starting shape (default: 'sphere')
- `config.enableVoiceModulation` - Enable voice effects (default: false)

### Methods

#### `setTargetShape(shape: string): void`
Start morphing to a new shape.

#### `update(): void`
Update morph progress. Call this in your animation loop.

#### `processVertices(vertices: number[], time: number): number[]`
Apply morphing to a vertex array (flat array: `[x, y, z, x, y, z, ...]`).

#### `applyMorphing(vertex: Vector3, time: number): Vector3`
Apply morphing to a single vertex.

#### `setVoiceData(voiceData: Partial<VoiceData>): void`
Update voice modulation data.

#### `registerShape(name: string, definition: ShapeDefinition): void`
Register a custom shape.

#### `getAvailableShapes(): string[]`
Get list of registered shape names.

#### `setMorphSpeed(speed: number): void`
Change morph speed (0.01-1.0).

#### `isMorphing(): boolean`
Check if currently morphing between shapes.

#### `getMorphProgress(): number`
Get current morph progress (0-1).

#### `getCurrentShapeInfo(): ShapeDefinition | null`
Get current shape definition.

#### `destroy(): void`
Cleanup resources (if using animation frame IDs).

---

## Built-in Shapes

### `sphere`
Default spherical shape with optional voice modulation.

### `consciousness`
Pulsating orb representing AI consciousness. Slow, breathing effect.

### `guardian`
Shield-like flattened shape with protective glow. Perfect for lukhas.com (corporate/guardian).

### `identity`
Lambda-inspired pointed shape with stable base. Perfect for lukhas.id (identity/security).

### `neural`
Bio-inspired organic pulsing pattern. Represents neural network architecture.

### `quantum`
Superposition of multiple wave states. Represents quantum-inspired algorithms.

### `cat`
Demo shape from PR0T3US original system. Pointed ears, elongated body, tail.

---

## Performance Considerations

- **Vertex Count**: Keep under 10,000 vertices for 60 FPS on most devices
- **Morph Speed**: Lower values (0.01-0.02) create smoother transitions
- **Voice Modulation**: Adds computational overhead, disable if not needed
- **Update Frequency**: Call `engine.update()` once per frame only

---

## Integration Examples

### lukhas.com (Morphing Constellation Orbs)

```typescript
const engines = [
  new MorphingEngine({ initialShape: 'consciousness' }),
  new MorphingEngine({ initialShape: 'guardian' }),
  new MorphingEngine({ initialShape: 'neural' }),
  // ... 8 total for Constellation Framework
]

// Cycle through shapes
setInterval(() => {
  const shapes = ['consciousness', 'guardian', 'neural', 'quantum']
  engines.forEach((engine, i) => {
    engine.setTargetShape(shapes[(i + 1) % shapes.length])
  })
}, 8000)
```

### lukhas.id (Breathing Identity Marker)

```typescript
const engine = new MorphingEngine({
  initialShape: 'identity',
  morphSpeed: 0.01, // Slower, more deliberate
})

// Static shape with gentle breathing animation
// (breathing is built into the identity shape definition)
```

---

## Original Source

Adapted from **PR0T3US Voice-Modulated Morphing System**
Original location: `/THE_VAULT/.../web-team/js/morphing-system.js`

**Improvements in LUKHAS version:**
- TypeScript with full type safety
- Modular, framework-agnostic design
- Constellation Framework-specific shapes
- Cleaner API for React integration
- No global state dependencies
- Performance optimizations

---

## License

Copyright © 2025 LUKHAS AI. All rights reserved.

Based on PR0T3US morphing system (original author unknown).
