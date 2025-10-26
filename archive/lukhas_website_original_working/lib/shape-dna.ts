// lib/shape-dna.ts
// Shape DNA system for deterministic morphing patterns

import { mulberry32, seedFromString } from './prng'

export interface ShapeDNA {
  baseForm: 'sphere' | 'torus' | 'helix' | 'cube'
  complexity: number // 0-1, affects vertex count
  organicity: number // 0-1, how bio-inspired vs geometric
  flow: number // 0-1, how fluid the transitions
  signature: string // unique identifier
}

export interface MorphingTarget {
  positions: Float32Array
  normals?: Float32Array
  signature: string
  complexity: number
}

/**
 * Generate deterministic shape DNA from text input
 */
export function generateShapeDNA(text: string): ShapeDNA {
  const seed = seedFromString(text)
  const rng = mulberry32(seed)
  
  const forms: ShapeDNA['baseForm'][] = ['sphere', 'torus', 'helix', 'cube']
  const baseForm = forms[Math.floor(rng() * forms.length)]
  
  return {
    baseForm,
    complexity: 0.3 + rng() * 0.4, // 0.3-0.7 range for stability
    organicity: rng(),
    flow: 0.5 + rng() * 0.3, // Smoother transitions
    signature: `${text.slice(0, 8)}-${seed.toString(16).slice(0, 6)}`
  }
}

/**
 * Create morphing target from shape DNA
 */
export function createMorphingTarget(
  dna: ShapeDNA, 
  particleCount: number
): MorphingTarget {
  const positions = new Float32Array(particleCount * 3)
  const seed = seedFromString(dna.signature)
  const rng = mulberry32(seed)
  
  // Base radius with complexity variation
  const baseRadius = 2.0
  const radiusVariation = dna.complexity * 0.5
  
  for (let i = 0; i < particleCount; i++) {
    const idx = i * 3
    
    switch (dna.baseForm) {
      case 'sphere':
        const [x, y, z] = generateSpherePoint(rng, baseRadius, radiusVariation, dna.organicity)
        positions[idx] = x
        positions[idx + 1] = y
        positions[idx + 2] = z
        break
        
      case 'torus':
        const [tx, ty, tz] = generateTorusPoint(rng, baseRadius, radiusVariation, dna.organicity)
        positions[idx] = tx
        positions[idx + 1] = ty
        positions[idx + 2] = tz
        break
        
      case 'helix':
        const [hx, hy, hz] = generateHelixPoint(i, particleCount, rng, baseRadius, dna.organicity)
        positions[idx] = hx
        positions[idx + 1] = hy
        positions[idx + 2] = hz
        break
        
      case 'cube':
        const [cx, cy, cz] = generateCubePoint(rng, baseRadius, radiusVariation, dna.organicity)
        positions[idx] = cx
        positions[idx + 1] = cy
        positions[idx + 2] = cz
        break
    }
  }
  
  return {
    positions,
    signature: dna.signature,
    complexity: dna.complexity
  }
}

/**
 * Generate sphere point with organic variation
 */
function generateSpherePoint(
  rng: () => number, 
  radius: number, 
  variation: number, 
  organicity: number
): [number, number, number] {
  // Uniform sphere distribution
  const u = rng()
  const v = rng()
  const theta = 2 * Math.PI * u
  const phi = Math.acos(2 * v - 1)
  
  // Add organic noise
  const noise = organicity * (rng() - 0.5) * variation
  const r = radius + noise
  
  return [
    r * Math.sin(phi) * Math.cos(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.sin(theta)
  ]
}

/**
 * Generate torus point with organic variation
 */
function generateTorusPoint(
  rng: () => number,
  majorRadius: number,
  variation: number,
  organicity: number
): [number, number, number] {
  const minorRadius = majorRadius * 0.3
  const u = rng() * 2 * Math.PI
  const v = rng() * 2 * Math.PI
  
  // Add organic variation
  const noise = organicity * (rng() - 0.5) * variation
  const R = majorRadius + noise
  const r = minorRadius + noise * 0.5
  
  return [
    (R + r * Math.cos(v)) * Math.cos(u),
    r * Math.sin(v),
    (R + r * Math.cos(v)) * Math.sin(u)
  ]
}

/**
 * Generate helix point
 */
function generateHelixPoint(
  index: number,
  total: number,
  rng: () => number,
  radius: number,
  organicity: number
): [number, number, number] {
  const t = (index / total) * 4 * Math.PI // 2 full turns
  const height = 4.0
  const y = (t / (4 * Math.PI)) * height - height * 0.5
  
  // Add organic variation
  const noise = organicity * (rng() - 0.5) * 0.2
  const r = radius + noise
  
  return [
    r * Math.cos(t) + noise,
    y + noise,
    r * Math.sin(t) + noise
  ]
}

/**
 * Generate cube point with organic rounding
 */
function generateCubePoint(
  rng: () => number,
  size: number,
  variation: number,
  organicity: number
): [number, number, number] {
  // Start with cube surface
  const face = Math.floor(rng() * 6)
  const u = rng() - 0.5
  const v = rng() - 0.5
  
  let x: number, y: number, z: number
  
  switch (face) {
    case 0: [x, y, z] = [size, u * size, v * size]; break // +X
    case 1: [x, y, z] = [-size, u * size, v * size]; break // -X
    case 2: [x, y, z] = [u * size, size, v * size]; break // +Y
    case 3: [x, y, z] = [u * size, -size, v * size]; break // -Y
    case 4: [x, y, z] = [u * size, v * size, size]; break // +Z
    default: [x, y, z] = [u * size, v * size, -size]; break // -Z
  }
  
  // Apply organic rounding
  if (organicity > 0) {
    const len = Math.sqrt(x * x + y * y + z * z)
    const sphereRadius = size * Math.sqrt(3) // Cube diagonal
    const blend = organicity * 0.5
    
    const sphereX = (x / len) * sphereRadius
    const sphereY = (y / len) * sphereRadius
    const sphereZ = (z / len) * sphereRadius
    
    x = x * (1 - blend) + sphereX * blend
    y = y * (1 - blend) + sphereY * blend
    z = z * (1 - blend) + sphereZ * blend
  }
  
  // Add variation noise
  const noise = variation * (rng() - 0.5) * 0.3
  return [x + noise, y + noise, z + noise]
}

/**
 * Interpolate between two morphing targets
 */
export function interpolateMorphingTargets(
  current: MorphingTarget,
  target: MorphingTarget,
  progress: number
): Float32Array {
  const result = new Float32Array(current.positions.length)
  
  for (let i = 0; i < result.length; i++) {
    result[i] = current.positions[i] * (1 - progress) + target.positions[i] * progress
  }
  
  return result
}