// lib/visuals/enhanced-particle-system.ts
// GPU-instanced particle system with deterministic morphing

import * as THREE from 'three'
import { mulberry32, seedFromString } from '../prng'

export interface Particle {
  position: Float32Array
  velocity: Float32Array
  scale: number
  color: THREE.Color
}

export interface ParticleSystemConfig {
  particleCount: number
  baseSize: number
  colorIntensity: number
  morphSpeed: number
  voiceSensitivity: number
}

// Global glyph cache for signature morphing
const glyphCache = new Map<string, Float32Array>()

// Default configuration
export const DEFAULT_CONFIG: ParticleSystemConfig = {
  particleCount: 12000, // GPU instancing allows for high counts
  baseSize: 0.02, // Steve Jobs approved small particles
  colorIntensity: 0.8,
  morphSpeed: 0.05,
  voiceSensitivity: 1.0
}

/**
 * Generate base sphere form with deterministic seeding
 */
export function generateBaseForm(seed: number, particleCount: number): Float32Array {
  const positions = new Float32Array(particleCount * 3)
  const rng = mulberry32(seed)
  
  for (let i = 0; i < particleCount; i++) {
    // Uniform sphere distribution
    const u = rng()
    const v = rng()
    const theta = 2 * Math.PI * u
    const phi = Math.acos(2 * v - 1)
    const r = 2.0 + (rng() - 0.5) * 0.1 // Slight radius variation
    
    positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.cos(phi)
    positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta)
  }
  
  return positions
}

/**
 * Cache glyph target positions for reuse
 */
export function setGlyphTargetCached(key: string, glyphTarget: Float32Array): void {
  // Limit cache size to prevent memory issues
  if (glyphCache.size > 100) {
    const firstKey = glyphCache.keys().next().value
    glyphCache.delete(firstKey)
  }
  glyphCache.set(key, glyphTarget)
}

/**
 * Retrieve cached glyph target
 */
export function getGlyphTargetCached(key: string): Float32Array | undefined {
  return glyphCache.get(key)
}

/**
 * Cache signature glyph points for a message
 */
export function cacheGlyphPoints(messageId: string, points: Float32Array): void {
  const key = `glyph-${messageId}`
  setGlyphTargetCached(key, points)
}

/**
 * Create GPU-instanced particle mesh for performance
 */
export function createInstancedParticleMesh(
  particleCount: number,
  basePositions: Float32Array
): THREE.InstancedMesh {
  // Use simple sphere geometry for each particle
  const geometry = new THREE.SphereGeometry(1, 8, 6) // Low poly for performance
  
  // Metallic material with emissive properties
  const material = new THREE.MeshPhysicalMaterial({
    color: 0x00d4ff,
    emissive: 0x0066ff,
    emissiveIntensity: 0.2,
    metalness: 0.9,
    roughness: 0.1,
    transparent: true,
    opacity: 0.8,
  })
  
  // Create instanced mesh
  const instancedMesh = new THREE.InstancedMesh(geometry, material, particleCount)
  
  // Set initial positions
  const matrix = new THREE.Matrix4()
  const position = new THREE.Vector3()
  const scale = new THREE.Vector3(0.02, 0.02, 0.02) // Small particles
  
  for (let i = 0; i < particleCount; i++) {
    position.set(
      basePositions[i * 3],
      basePositions[i * 3 + 1],
      basePositions[i * 3 + 2]
    )
    
    matrix.makeScale(scale.x, scale.y, scale.z)
    matrix.setPosition(position)
    instancedMesh.setMatrixAt(i, matrix)
  }
  
  instancedMesh.instanceMatrix.needsUpdate = true
  return instancedMesh
}

/**
 * Update particle instances based on voice data
 */
export function updateParticlesWithVoice(
  instancedMesh: THREE.InstancedMesh,
  voiceIntensity: number,
  currentPositions: Float32Array,
  targetPositions: Float32Array,
  morphProgress: number,
  config: ParticleSystemConfig
): void {
  const matrix = new THREE.Matrix4()
  const position = new THREE.Vector3()
  const color = new THREE.Color()
  
  // Calculate color based on voice intensity
  const hue = 0.6 - voiceIntensity * 0.4 // Blue (calm) to Red (intense)
  const saturation = 0.8 + voiceIntensity * 0.2
  const lightness = 0.4 + voiceIntensity * 0.2
  color.setHSL(hue, saturation, lightness)
  
  // Update material color
  if (instancedMesh.material instanceof THREE.MeshPhysicalMaterial) {
    instancedMesh.material.color = color
    instancedMesh.material.emissiveIntensity = 0.2 + voiceIntensity * 0.3
  }
  
  // Update each particle instance
  const particleCount = instancedMesh.count
  const baseScale = config.baseSize * (1 + voiceIntensity * config.voiceSensitivity)
  
  for (let i = 0; i < particleCount; i++) {
    // Morph between current and target positions
    const t = morphProgress
    const x = currentPositions[i * 3] * (1 - t) + targetPositions[i * 3] * t
    const y = currentPositions[i * 3 + 1] * (1 - t) + targetPositions[i * 3 + 1] * t
    const z = currentPositions[i * 3 + 2] * (1 - t) + targetPositions[i * 3 + 2] * t
    
    // Add voice-reactive movement
    const wave = Math.sin(Date.now() * 0.001 + i * 0.1) * voiceIntensity * 0.05
    position.set(x + wave, y + wave * 0.5, z + wave * 0.3)
    
    // Scale based on voice intensity with particle variation
    const particleScale = baseScale * (1 + Math.sin(i * 0.5) * 0.2)
    matrix.makeScale(particleScale, particleScale, particleScale)
    matrix.setPosition(position)
    
    instancedMesh.setMatrixAt(i, matrix)
  }
  
  instancedMesh.instanceMatrix.needsUpdate = true
}

/**
 * Calculate FPS and provide performance metrics
 */
export class PerformanceMonitor {
  private lastTime: number = 0
  private frames: number = 0
  private fps: number = 60
  private adaptiveReduction: number = 1.0
  
  update(): { fps: number; shouldReduce: boolean } {
    this.frames++
    const currentTime = performance.now()
    
    if (currentTime >= this.lastTime + 1000) {
      this.fps = Math.round((this.frames * 1000) / (currentTime - this.lastTime))
      this.frames = 0
      this.lastTime = currentTime
      
      // Adaptive fallback if FPS drops below 30
      if (this.fps < 30 && this.adaptiveReduction === 1.0) {
        this.adaptiveReduction = 0.8 // Reduce particle count by 20%
        return { fps: this.fps, shouldReduce: true }
      }
    }
    
    return { fps: this.fps, shouldReduce: false }
  }
  
  getFPS(): number {
    return this.fps
  }
  
  getReductionFactor(): number {
    return this.adaptiveReduction
  }
}