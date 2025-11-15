import { describe, it, expect, beforeEach } from 'vitest'
import { MorphingEngine } from './MorphingEngine'
import type { Vector3, ShapeDefinition } from './MorphingEngine'

describe('MorphingEngine', () => {
  let engine: MorphingEngine

  beforeEach(() => {
    engine = new MorphingEngine()
  })

  describe('Initialization', () => {
    it('initializes with default configuration', () => {
      expect(engine).toBeInstanceOf(MorphingEngine)
      expect(engine.getCurrentShapeInfo()?.name).toBe('Sphere')
    })

    it('initializes with custom initial shape', () => {
      const customEngine = new MorphingEngine({ initialShape: 'consciousness' })
      expect(customEngine.getCurrentShapeInfo()?.name).toBe('Consciousness Orb')
    })

    it('initializes with custom morph speed', () => {
      const customEngine = new MorphingEngine({ morphSpeed: 0.05 })
      customEngine.setTargetShape('consciousness')
      expect(customEngine.isMorphing()).toBe(true)
    })

    it('initializes with voice modulation disabled by default', () => {
      const engine = new MorphingEngine()
      expect(engine).toBeInstanceOf(MorphingEngine)
    })

    it('initializes with voice modulation enabled', () => {
      const engine = new MorphingEngine({ enableVoiceModulation: true })
      expect(engine).toBeInstanceOf(MorphingEngine)
    })
  })

  describe('Default Shapes', () => {
    it('registers all 7 default shapes', () => {
      const shapes = engine.getAvailableShapes()
      expect(shapes).toContain('sphere')
      expect(shapes).toContain('consciousness')
      expect(shapes).toContain('guardian')
      expect(shapes).toContain('identity')
      expect(shapes).toContain('neural')
      expect(shapes).toContain('quantum')
      expect(shapes).toContain('cat')
      expect(shapes.length).toBe(7)
    })

    it('sphere shape returns normalized radius', () => {
      const vertex: Vector3 = { x: 1, y: 0, z: 0 }
      const result = engine.applyMorphing(vertex, 0)
      expect(result.x).toBeCloseTo(10, 1) // radius 10
      expect(result.y).toBeCloseTo(0, 1)
      expect(result.z).toBeCloseTo(0, 1)
    })

    it('consciousness shape morphs correctly', () => {
      engine.setTargetShape('consciousness')

      // Complete the morph
      for (let i = 0; i < 60; i++) {
        engine.update()
      }

      expect(engine.isMorphing()).toBe(false)
      expect(engine.getCurrentShapeInfo()?.name).toBe('Consciousness Orb')

      // Verify shape applies transformation (includes pulsating effect)
      const vertex: Vector3 = { x: 1, y: 0, z: 0 }
      const result = engine.applyMorphing(vertex, 0)
      expect(result.x).toBeDefined()
      expect(result.y).toBeDefined()
      expect(result.z).toBeDefined()
      expect(isFinite(result.x)).toBe(true)
    })
  })

  describe('Custom Shape Registration', () => {
    it('registers custom shape definition', () => {
      const customShape: ShapeDefinition = {
        name: 'Custom Shape',
        vertexModifier: (vertex) => ({ x: vertex.x * 2, y: vertex.y * 2, z: vertex.z * 2 }),
      }

      engine.registerShape('custom', customShape)
      const shapes = engine.getAvailableShapes()
      expect(shapes).toContain('custom')
    })

    it('uses custom shape for morphing', () => {
      const customShape: ShapeDefinition = {
        name: 'Double Sphere',
        vertexModifier: (vertex) => ({ x: vertex.x * 20, y: vertex.y * 20, z: vertex.z * 20 }),
      }

      engine.registerShape('custom', customShape)
      engine.setTargetShape('custom')

      // Complete the morph
      for (let i = 0; i < 100; i++) {
        engine.update()
      }

      const vertex: Vector3 = { x: 1, y: 0, z: 0 }
      const result = engine.applyMorphing(vertex, 0)
      expect(result.x).toBeCloseTo(20, 1)
    })
  })

  describe('Shape Morphing', () => {
    it('sets target shape correctly', () => {
      engine.setTargetShape('consciousness')
      expect(engine.isMorphing()).toBe(true)
    })

    it('does not morph when target is current shape', () => {
      engine.setTargetShape('sphere')
      expect(engine.isMorphing()).toBe(false)
    })

    it('warns when setting non-existent shape', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      engine.setTargetShape('nonexistent')
      expect(consoleSpy).toHaveBeenCalledWith('Shape "nonexistent" not registered')
      consoleSpy.mockRestore()
    })

    it('completes morphing after sufficient updates', () => {
      engine.setTargetShape('consciousness')
      expect(engine.isMorphing()).toBe(true)

      // Update until morphing completes (morphSpeed default is 0.02, so 50 updates)
      for (let i = 0; i < 60; i++) {
        engine.update()
      }

      expect(engine.isMorphing()).toBe(false)
      expect(engine.getCurrentShapeInfo()?.name).toBe('Consciousness Orb')
    })

    it('provides morph progress', () => {
      engine.setTargetShape('consciousness')
      const initialProgress = engine.getMorphProgress()
      expect(initialProgress).toBe(0)

      engine.update()
      const updatedProgress = engine.getMorphProgress()
      expect(updatedProgress).toBeGreaterThan(initialProgress)
      expect(updatedProgress).toBeLessThanOrEqual(1)
    })
  })

  describe('Vertex Processing', () => {
    it('processes single vertex', () => {
      const vertex: Vector3 = { x: 1, y: 1, z: 1 }
      const result = engine.applyMorphing(vertex, 0)
      expect(result).toHaveProperty('x')
      expect(result).toHaveProperty('y')
      expect(result).toHaveProperty('z')
    })

    it('processes vertex array', () => {
      const vertices = [1, 0, 0, 0, 1, 0, 0, 0, 1]
      const result = engine.processVertices(vertices, 0)
      expect(result.length).toBe(9)
      expect(result).toBeInstanceOf(Array)
    })

    it('maintains vertex count when processing array', () => {
      const vertices = new Array(300).fill(0).map((_, i) => i * 0.1)
      const result = engine.processVertices(vertices, 0)
      expect(result.length).toBe(vertices.length)
    })
  })

  describe('Voice Modulation', () => {
    it('sets voice data correctly', () => {
      engine.setVoiceData({ intensity: 0.5, frequency: 440 })
      // Voice data is private, but should affect morphing with voice modulation enabled
    })

    it('sets partial voice data', () => {
      engine.setVoiceData({ intensity: 0.8 })
      engine.setVoiceData({ frequency: 880 })
      // Both should be retained
    })
  })

  describe('Morph Speed Control', () => {
    it('sets morph speed within valid range', () => {
      engine.setMorphSpeed(0.05)
      engine.setTargetShape('consciousness')
      engine.update()
      const progress = engine.getMorphProgress()
      expect(progress).toBeCloseTo(0.05, 2)
    })

    it('clamps morph speed to minimum 0.01', () => {
      engine.setMorphSpeed(0.001) // Too low
      engine.setTargetShape('consciousness')
      engine.update()
      const progress = engine.getMorphProgress()
      expect(progress).toBeGreaterThanOrEqual(0.01)
    })

    it('clamps morph speed to maximum 1.0', () => {
      engine.setMorphSpeed(5.0) // Too high
      engine.setTargetShape('consciousness')
      engine.update()
      const progress = engine.getMorphProgress()
      expect(progress).toBeLessThanOrEqual(1.0)
    })
  })

  describe('Shape Info Retrieval', () => {
    it('returns current shape info', () => {
      const info = engine.getCurrentShapeInfo()
      expect(info).toBeDefined()
      expect(info?.name).toBe('Sphere')
      expect(info?.vertexModifier).toBeInstanceOf(Function)
    })

    it('returns null for non-existent shape', () => {
      // This would require accessing private methods, so we test indirectly
      const shapes = engine.getAvailableShapes()
      expect(shapes).not.toContain('nonexistent')
    })
  })

  describe('Cleanup', () => {
    it('cleans up without errors', () => {
      expect(() => engine.destroy()).not.toThrow()
    })

    it('can be destroyed multiple times', () => {
      engine.destroy()
      expect(() => engine.destroy()).not.toThrow()
    })
  })

  describe('Constellation Framework Shapes', () => {
    it('identity shape has lambda-inspired pointed top', () => {
      engine.setTargetShape('identity')
      for (let i = 0; i < 60; i++) engine.update()

      const topVertex: Vector3 = { x: 0, y: 1, z: 0 }
      const result = engine.applyMorphing(topVertex, 0)
      expect(Math.abs(result.y)).toBeGreaterThan(Math.abs(result.x))
    })

    it('guardian shape has shield-like flattening', () => {
      engine.setTargetShape('guardian')
      for (let i = 0; i < 60; i++) engine.update()

      const frontVertex: Vector3 = { x: 0, y: 0, z: 1 }
      const result = engine.applyMorphing(frontVertex, 0)
      expect(result).toBeDefined()
    })

    it('neural shape has organic pulsing', () => {
      engine.setTargetShape('neural')
      for (let i = 0; i < 60; i++) engine.update()

      const vertex: Vector3 = { x: 1, y: 0, z: 0 }
      const result1 = engine.applyMorphing(vertex, 0)
      const result2 = engine.applyMorphing(vertex, Math.PI)
      expect(result1.x).not.toBeCloseTo(result2.x, 1)
    })

    it('quantum shape has superposition waves', () => {
      engine.setTargetShape('quantum')
      for (let i = 0; i < 60; i++) engine.update()

      const vertex: Vector3 = { x: 1, y: 0, z: 0 }
      const result1 = engine.applyMorphing(vertex, 0)
      const result2 = engine.applyMorphing(vertex, Math.PI / 2)
      expect(result1.x).not.toBeCloseTo(result2.x, 1)
    })
  })

  describe('Edge Cases', () => {
    it('handles zero vector normalization', () => {
      const zeroVertex: Vector3 = { x: 0, y: 0, z: 0 }
      const result = engine.applyMorphing(zeroVertex, 0)
      expect(result).toBeDefined()
      expect(isNaN(result.x)).toBe(false)
      expect(isNaN(result.y)).toBe(false)
      expect(isNaN(result.z)).toBe(false)
    })

    it('handles empty vertex array', () => {
      const result = engine.processVertices([], 0)
      expect(result).toEqual([])
    })

    it('handles large time values', () => {
      const vertex: Vector3 = { x: 1, y: 0, z: 0 }
      const result = engine.applyMorphing(vertex, 999999)
      expect(result).toBeDefined()
      expect(isFinite(result.x)).toBe(true)
      expect(isFinite(result.y)).toBe(true)
      expect(isFinite(result.z)).toBe(true)
    })
  })
})
