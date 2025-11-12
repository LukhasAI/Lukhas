import React, { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export type MorphingShape = 'sphere' | 'consciousness' | 'guardian' | 'identity' | 'neural' | 'quantum' | 'cat'

export interface VoiceData {
  intensity: number
  frequency: number
}

export interface MorphingParticlesProps {
  /** Current shape to display */
  shape?: MorphingShape
  /** Voice modulation data (optional) */
  voiceData?: VoiceData
  /** Number of particles (default: 4096) */
  particleCount?: number
  /** Rotation speed multiplier (default: 1.0) */
  rotationSpeed?: number
  /** Enable automatic rotation (default: true) */
  autoRotate?: boolean
  /** Color override (optional, uses shape-specific colors by default) */
  color?: string
  /** Particle size (default: 5.0) */
  baseParticleSize?: number
}

/**
 * MorphingParticles - WebGL particle system with Constellation Framework shapes
 *
 * A production-ready React Three Fiber component that renders a particle cloud
 * morphing between different shapes. Based on LUKHAS consciousness-inspired design.
 *
 * Features:
 * - 4,096 particles by default (configurable)
 * - GPU-accelerated vertex shader morphing
 * - Additive blending for glow effects
 * - Optional voice modulation
 * - 7 shapes: sphere, consciousness, guardian, identity, neural, quantum, cat (easter egg)
 *
 * @example
 * ```tsx
 * <Canvas>
 *   <MorphingParticles shape="consciousness" />
 * </Canvas>
 * ```
 *
 * @example With voice modulation
 * ```tsx
 * const [voiceData, setVoiceData] = useState({ intensity: 0, frequency: 0 })
 *
 * <Canvas>
 *   <MorphingParticles
 *     shape="neural"
 *     voiceData={voiceData}
 *     rotationSpeed={0.5}
 *   />
 * </Canvas>
 * ```
 */
export const MorphingParticles: React.FC<MorphingParticlesProps> = ({
  shape = 'sphere',
  voiceData = { intensity: 0, frequency: 0 },
  particleCount = 4096,
  rotationSpeed = 1.0,
  autoRotate = true,
  color,
  baseParticleSize = 5.0,
}) => {
  const meshRef = useRef<THREE.Points>(null)
  const materialRef = useRef<THREE.ShaderMaterial>(null)
  const timeRef = useRef(0)
  const morphProgressRef = useRef(1.0)
  const previousShapeRef = useRef(shape)
  const targetShapeRef = useRef(shape)

  // Shape value mapping for shader
  const shapeValues: Record<MorphingShape, number> = {
    sphere: 0,
    consciousness: 1,
    guardian: 2,
    identity: 3,
    neural: 4,
    quantum: 5,
    cat: 6,
  }

  // Generate particle geometry
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    const segments = Math.sqrt(particleCount)
    const rings = segments
    const radius = 2.0
    const positions: number[] = []

    for (let ring = 0; ring <= rings; ring++) {
      const phi = (ring / rings) * Math.PI
      for (let segment = 0; segment <= segments; segment++) {
        const theta = (segment / segments) * 2 * Math.PI
        const x = radius * Math.sin(phi) * Math.cos(theta)
        const y = radius * Math.cos(phi)
        const z = radius * Math.sin(phi) * Math.sin(theta)
        positions.push(x, y, z)
      }
    }

    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    return geo
  }, [particleCount])

  // Shader material
  const shaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        voiceIntensity: { value: 0 },
        currentShape: { value: 0 },
        morphProgress: { value: 1.0 },
        baseSize: { value: baseParticleSize },
        customColor: { value: color ? new THREE.Color(color) : null },
      },
      vertexShader: `
        precision mediump float;
        attribute vec3 position;
        uniform float time;
        uniform float voiceIntensity;
        uniform float currentShape;
        uniform float morphProgress;
        uniform float baseSize;
        varying float vSize;
        varying vec3 vColor;

        // Constellation Framework shape morphing functions
        vec3 consciousnessShape(vec3 pos, float intensity) {
          float pulse = sin(time * 0.8) * 0.15;
          float breath = sin(time * 1.2 + length(pos) * 2.0) * 0.1;
          return pos * (1.0 + pulse + breath + intensity * 0.2);
        }

        vec3 guardianShape(vec3 pos, float intensity) {
          float frontFlatten = pos.z > 0.0 ? 0.7 : 1.0;
          float glow = sin(time * 2.0) * 0.08;
          pos.z *= frontFlatten;
          pos.x *= 1.1 + glow;
          pos.y *= 1.1 + glow;
          return pos * (1.0 + intensity * 0.15);
        }

        vec3 identityShape(vec3 pos, float intensity) {
          float heightMod = pos.y > 0.6 ? 1.5 : (pos.y < -0.5 ? 0.8 : 1.0);
          float widthMod = pos.y > 0.6 ? 0.65 : (pos.y < -0.5 ? 1.2 : 1.0);
          float breath = sin(time * 1.5) * 0.06;
          pos.x *= widthMod * (1.0 + breath);
          pos.y *= heightMod * (1.0 + breath);
          pos.z *= widthMod * (1.0 + breath);
          return pos * (1.0 + intensity * 0.12);
        }

        vec3 neuralShape(vec3 pos, float intensity) {
          float pulse1 = sin(time * 2.0 + length(pos) * 5.0) * 0.12;
          float pulse2 = cos(time * 1.5 + pos.x * 4.0 + pos.y * 3.0) * 0.12;
          float pulse3 = sin(time * 1.8 + pos.z * 6.0) * 0.08;
          return pos * (1.0 + pulse1 + pulse2 + pulse3 + intensity * 0.2);
        }

        vec3 quantumShape(vec3 pos, float intensity) {
          float wave1 = sin(time * 3.0 + length(pos) * 8.0) * 0.15;
          float wave2 = cos(time * 2.5 + pos.x * 6.0) * 0.15;
          float wave3 = sin(time * 2.8 + pos.y * 7.0) * 0.12;
          float interference = (wave1 + wave2 + wave3) / 3.0;
          return pos * (1.0 + interference + intensity * 0.25);
        }

        vec3 catShape(vec3 pos, float intensity) {
          if (pos.y > 0.7) {
            pos.x *= 0.85;
            pos.z *= 0.85;
            pos.y *= 1.18 + 0.10 * intensity;
          } else if (abs(pos.y) < 0.3) {
            pos.x *= 1.10;
            pos.z *= 1.10;
          } else if (pos.y < -0.7) {
            pos.x *= 0.85;
            pos.z *= 0.85;
            pos.y *= 1.10;
          }
          return pos;
        }

        vec3 morphTarget(vec3 base, float shape, float intensity) {
          vec3 pos = base;
          if (shape < 0.5) {
            return pos;
          } else if (shape < 1.5) {
            return consciousnessShape(pos, intensity);
          } else if (shape < 2.5) {
            return guardianShape(pos, intensity);
          } else if (shape < 3.5) {
            return identityShape(pos, intensity);
          } else if (shape < 4.5) {
            return neuralShape(pos, intensity);
          } else if (shape < 5.5) {
            return quantumShape(pos, intensity);
          } else {
            return catShape(pos, intensity);
          }
        }

        void main() {
          float cappedIntensity = min(voiceIntensity, 1.0);
          float scale = 1.0 + cappedIntensity * 0.35;
          vec3 base = position * scale;
          vec3 target = morphTarget(base, currentShape, cappedIntensity);
          vec3 morphed = mix(base, target, morphProgress);

          float jitter = (fract(sin(dot(morphed.xyz, vec3(12.9898, 78.233, 45.164))) * 43758.5453 + time) - 0.5) * 0.08 * cappedIntensity;
          morphed += jitter;

          vSize = baseSize + 10.0 * cappedIntensity;

          // Shape-specific colors (Lambda Blue variants)
          if (currentShape < 1.5) {
            vColor = vec3(0.0, 0.83, 1.0); // Lambda Blue
          } else if (currentShape < 2.5) {
            vColor = vec3(0.2, 0.8, 1.0); // Guardian
          } else if (currentShape < 3.5) {
            vColor = vec3(0.4, 0.2, 1.0); // Identity purple
          } else if (currentShape < 4.5) {
            vColor = vec3(0.0, 1.0, 0.53); // Neural quantum green
          } else if (currentShape < 5.5) {
            vColor = mix(vec3(0.0, 0.83, 1.0), vec3(0.0, 1.0, 0.53), sin(time * 3.0 + length(position) * 8.0) * 0.5 + 0.5);
          } else {
            vColor = vec3(0.83, 0.69, 0.22); // Cat luke gold
          }

          gl_Position = projectionMatrix * modelViewMatrix * vec4(morphed, 1.0);
          gl_PointSize = vSize;
        }
      `,
      fragmentShader: `
        precision mediump float;
        uniform vec3 customColor;
        varying float vSize;
        varying vec3 vColor;

        void main() {
          float dist = length(gl_PointCoord - vec2(0.5));
          float alpha = smoothstep(0.5, 0.2, dist);
          vec3 finalColor = customColor != vec3(0.0) ? customColor : vColor;
          gl_FragColor = vec4(finalColor, alpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending, // Key for glow effect!
    })
  }, [baseParticleSize, color])

  // Trigger morph animation when shape changes
  useEffect(() => {
    if (shape !== previousShapeRef.current) {
      targetShapeRef.current = shape
      morphProgressRef.current = 0.0
      previousShapeRef.current = shape
    }
  }, [shape])

  // Animation loop
  useFrame((_, delta) => {
    if (!materialRef.current || !meshRef.current) return

    // Update time
    timeRef.current += delta
    materialRef.current.uniforms.time.value = timeRef.current

    // Update voice intensity
    const normalizedIntensity = Math.min(voiceData.intensity / 64.0, 1.0)
    materialRef.current.uniforms.voiceIntensity.value = normalizedIntensity

    // Update morph progress
    if (morphProgressRef.current < 1.0) {
      morphProgressRef.current = Math.min(1.0, morphProgressRef.current + delta * 2.0)
      materialRef.current.uniforms.morphProgress.value = morphProgressRef.current
    }

    // Update current shape
    materialRef.current.uniforms.currentShape.value = shapeValues[targetShapeRef.current]

    // Auto-rotate
    if (autoRotate) {
      meshRef.current.rotation.y += delta * 0.5 * rotationSpeed
      meshRef.current.rotation.x += delta * 0.3 * rotationSpeed
    }
  })

  return (
    <points ref={meshRef} geometry={geometry} material={shaderMaterial}>
      <shaderMaterial ref={materialRef} attach="material" {...shaderMaterial} />
    </points>
  )
}

export default MorphingParticles
