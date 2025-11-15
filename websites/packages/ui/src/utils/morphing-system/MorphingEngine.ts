/**
 * LUKHAS Morphing Engine
 *
 * Adapted from PR0T3US Voice-Modulated Morphing System
 * Modern TypeScript implementation for React + WebGL
 *
 * @author PR0T3US Team (original), LUKHAS AI (adaptation)
 * @license Copyright © 2025 LUKHAS AI
 */

export interface Vector3 {
  x: number
  y: number
  z: number
}

export interface VoiceData {
  intensity: number
  frequency: number
}

export type VertexModifierFn = (
  vertex: Vector3,
  time: number,
  voiceData: VoiceData
) => Vector3

export interface ShapeDefinition {
  name: string
  vertexModifier: VertexModifierFn
}

export interface MorphingEngineConfig {
  morphSpeed?: number
  enableVoiceModulation?: boolean
  initialShape?: string
}

export class MorphingEngine {
  private currentShape: string
  private targetShape: string
  private voiceData: VoiceData
  private morphProgress: number
  private morphSpeed: number
  private enableVoiceModulation: boolean
  private shapeDefinitions: Map<string, ShapeDefinition>
  private animationFrameId: number | null = null

  constructor(config: MorphingEngineConfig = {}) {
    this.currentShape = config.initialShape || 'sphere'
    this.targetShape = this.currentShape
    this.morphSpeed = config.morphSpeed || 0.02
    this.enableVoiceModulation = config.enableVoiceModulation ?? false
    this.morphProgress = 0
    this.voiceData = { intensity: 0, frequency: 0 }
    this.shapeDefinitions = new Map()

    this.registerDefaultShapes()
  }

  /**
   * Register built-in shape definitions
   */
  private registerDefaultShapes(): void {
    // Default Sphere
    this.registerShape('sphere', {
      name: 'Sphere',
      vertexModifier: (vertex, time, voiceData) => {
        const radius = 10.0 + (this.enableVoiceModulation ? voiceData.intensity * 0.1 : 0)
        const normalized = this.normalizeVector(vertex)
        return {
          x: normalized.x * radius,
          y: normalized.y * radius,
          z: normalized.z * radius,
        }
      },
    })

    // Constellation Framework: 8-Star Shapes
    this.registerShape('consciousness', {
      name: 'Consciousness Orb',
      vertexModifier: (vertex, time, voiceData) => {
        const normalized = this.normalizeVector(vertex)
        const radius = 10.0 + (this.enableVoiceModulation ? voiceData.intensity * 0.15 : 0)

        // Pulsating consciousness effect
        const pulse = Math.sin(time * 0.5) * 0.2
        const modulation = this.enableVoiceModulation
          ? Math.sin(time * 20 + voiceData.frequency * 0.01) * voiceData.intensity * 0.1
          : 0

        return {
          x: normalized.x * (radius + pulse + modulation),
          y: normalized.y * (radius + pulse + modulation),
          z: normalized.z * (radius + pulse + modulation),
        }
      },
    })

    // Guardian Shield shape (for lukhas.com)
    this.registerShape('guardian', {
      name: 'Guardian Shield',
      vertexModifier: (vertex, time, voiceData) => {
        const normalized = this.normalizeVector(vertex)
        const radius = 10.0

        let { x, y, z } = normalized

        // Shield-like flattening on one side
        if (z > 0) {
          x *= 1.2
          y *= 1.2
          z *= 0.6
        }

        // Protective glow effect
        const glow = Math.sin(time * 2) * 0.1
        x *= radius + glow
        y *= radius + glow
        z *= radius + glow

        return { x, y, z }
      },
    })

    // Identity Symbol (for lukhas.id)
    this.registerShape('identity', {
      name: 'Identity Marker',
      vertexModifier: (vertex, time, voiceData) => {
        const normalized = this.normalizeVector(vertex)
        const radius = 10.0

        let { x, y, z } = normalized

        // Lambda-inspired pointed top
        if (y > 0.7) {
          x *= 0.6
          z *= 0.6
          y *= 1.4
        }

        // Stable base
        if (y < -0.5) {
          x *= 1.2
          z *= 1.2
          y *= 0.8
        }

        // Gentle breathing for life
        const breath = Math.sin(time * 1.5) * 0.08

        return {
          x: x * radius + breath * normalized.x,
          y: y * radius + breath * normalized.y,
          z: z * radius + breath * normalized.z,
        }
      },
    })

    // Neural Network (bio-inspired)
    this.registerShape('neural', {
      name: 'Neural Network',
      vertexModifier: (vertex, time, voiceData) => {
        const normalized = this.normalizeVector(vertex)
        const radius = 10.0

        // Organic pulsing pattern
        const pulse1 = Math.sin(time * 2 + normalized.x * 5) * 0.15
        const pulse2 = Math.cos(time * 1.5 + normalized.y * 5) * 0.15
        const pulse3 = Math.sin(time * 1.8 + normalized.z * 5) * 0.15

        const combinedPulse = (pulse1 + pulse2 + pulse3) / 3

        return {
          x: normalized.x * (radius + combinedPulse),
          y: normalized.y * (radius + combinedPulse),
          z: normalized.z * (radius + combinedPulse),
        }
      },
    })

    // Quantum Superposition (multiple states)
    this.registerShape('quantum', {
      name: 'Quantum State',
      vertexModifier: (vertex, time, voiceData) => {
        const normalized = this.normalizeVector(vertex)
        const radius = 10.0

        // Multiple overlapping wave patterns
        const wave1 = Math.sin(time * 3 + normalized.x * 8) * 0.2
        const wave2 = Math.cos(time * 2.5 + normalized.y * 6) * 0.2
        const wave3 = Math.sin(time * 4 + normalized.z * 7) * 0.2

        const superposition = wave1 + wave2 + wave3

        return {
          x: normalized.x * (radius + superposition),
          y: normalized.y * (radius + superposition),
          z: normalized.z * (radius + superposition),
        }
      },
    })

    // Cat (from PR0T3US, kept for demo)
    this.registerShape('cat', {
      name: 'Cat',
      vertexModifier: (vertex, time, voiceData) => {
        const normalized = this.normalizeVector(vertex)
        const radius = 10.0 + (this.enableVoiceModulation ? voiceData.intensity * 0.2 : 0)

        let x = normalized.x * radius
        let y = normalized.y * radius
        let z = normalized.z * radius

        // Pointed ears
        if (y > 0.7) {
          x *= 0.8
          z *= 0.8
          y *= 1.3
        }

        // Elongated body
        if (Math.abs(y) < 0.3) {
          x *= 1.2
          z *= 1.2
        }

        // Tail
        if (y < -0.7) {
          x *= 0.6
          z *= 0.6
          y *= 1.5
        }

        // Purring effect
        if (this.enableVoiceModulation) {
          const purr =
            Math.sin(time * 20 + voiceData.frequency * 0.01) *
            voiceData.intensity *
            0.1
          x += purr * normalized.x
          y += purr * normalized.y
          z += purr * normalized.z
        }

        return { x, y, z }
      },
    })
  }

  /**
   * Register a custom shape definition
   */
  registerShape(name: string, definition: ShapeDefinition): void {
    this.shapeDefinitions.set(name, definition)
  }

  /**
   * Get all registered shape names
   */
  getAvailableShapes(): string[] {
    return Array.from(this.shapeDefinitions.keys())
  }

  /**
   * Set target shape for morphing
   */
  setTargetShape(shape: string): void {
    if (this.shapeDefinitions.has(shape)) {
      if (this.targetShape !== shape) {
        this.targetShape = shape
        this.morphProgress = 0
      }
    } else {
      console.warn(`Shape "${shape}" not registered`)
    }
  }

  /**
   * Set voice modulation data
   */
  setVoiceData(voiceData: Partial<VoiceData>): void {
    this.voiceData = {
      intensity: voiceData.intensity ?? this.voiceData.intensity,
      frequency: voiceData.frequency ?? this.voiceData.frequency,
    }
  }

  /**
   * Apply morphing to a single vertex
   */
  applyMorphing(vertex: Vector3, time: number): Vector3 {
    const currentDef = this.shapeDefinitions.get(this.currentShape)
    const targetDef = this.shapeDefinitions.get(this.targetShape)

    if (!currentDef || !targetDef) {
      return vertex
    }

    // Get current and target positions
    const currentPos = currentDef.vertexModifier(vertex, time, this.voiceData)
    const targetPos = targetDef.vertexModifier(vertex, time, this.voiceData)

    // Interpolate
    return {
      x: currentPos.x + (targetPos.x - currentPos.x) * this.morphProgress,
      y: currentPos.y + (targetPos.y - currentPos.y) * this.morphProgress,
      z: currentPos.z + (targetPos.z - currentPos.z) * this.morphProgress,
    }
  }

  /**
   * Process array of vertices (for WebGL buffer)
   */
  processVertices(vertices: number[], time: number): number[] {
    const morphedVertices: number[] = []

    for (let i = 0; i < vertices.length; i += 3) {
      const vertex = {
        x: vertices[i],
        y: vertices[i + 1],
        z: vertices[i + 2],
      }

      const morphed = this.applyMorphing(vertex, time)
      morphedVertices.push(morphed.x, morphed.y, morphed.z)
    }

    return morphedVertices
  }

  /**
   * Update morphing progress (call in animation loop)
   */
  update(): void {
    if (this.currentShape !== this.targetShape) {
      this.morphProgress = Math.min(1.0, this.morphProgress + this.morphSpeed)

      if (this.morphProgress >= 1.0) {
        this.currentShape = this.targetShape
        this.morphProgress = 0
      }
    }
  }

  /**
   * Normalize a vector to unit length
   */
  private normalizeVector(vector: Vector3): Vector3 {
    const length = Math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)
    if (length === 0) return { x: 0, y: 0, z: 0 }
    return {
      x: vector.x / length,
      y: vector.y / length,
      z: vector.z / length,
    }
  }

  /**
   * Get current shape info
   */
  getCurrentShapeInfo(): ShapeDefinition | null {
    return this.shapeDefinitions.get(this.currentShape) || null
  }

  /**
   * Get morphing progress (0-1)
   */
  getMorphProgress(): number {
    return this.morphProgress
  }

  /**
   * Check if currently morphing
   */
  isMorphing(): boolean {
    return this.currentShape !== this.targetShape
  }

  /**
   * Set morph speed (0.01 - 1.0)
   */
  setMorphSpeed(speed: number): void {
    this.morphSpeed = Math.max(0.01, Math.min(1.0, speed))
  }

  /**
   * Cleanup (if needed)
   */
  destroy(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }
  }
}
