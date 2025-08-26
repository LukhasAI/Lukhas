'use client'

import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface SimpleParticlesProps {
  count: number
  size: number
  color: string
  voiceData?: { intensity: number; frequency: number }
  morphSpeed?: number
}

export function SimpleParticles({ count, size, color, voiceData, morphSpeed = 0.05 }: SimpleParticlesProps) {
  const pointsRef = useRef<THREE.Points>(null)

  // Generate sophisticated particle positions and colors
  const { positions, colors } = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const cols = new Float32Array(count * 3)

    for (let i = 0; i < count; i++) {
      const i3 = i * 3

      // Sophisticated distribution combining sphere and structured patterns
      const t = i / count
      const layer = Math.floor(i / (count / 5)) // 5 layers

      // Base spherical distribution
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      const baseRadius = 2.5 + Math.sin(t * Math.PI * 4) * 0.5

      // Add structured variation based on layer
      const layerOffset = (layer * 0.3) - 0.6
      const radius = baseRadius + layerOffset + Math.random() * 0.3

      pos[i3] = radius * Math.sin(phi) * Math.cos(theta)
      pos[i3 + 1] = radius * Math.cos(phi)
      pos[i3 + 2] = radius * Math.sin(phi) * Math.sin(theta)

      // Sophisticated color gradients
      const r = 0.1 + t * 0.3 + Math.sin(t * Math.PI * 2) * 0.2
      const g = 0.6 + t * 0.4 + Math.cos(t * Math.PI * 3) * 0.3
      const b = 0.9 + Math.sin(t * Math.PI * 5) * 0.1

      cols[i3] = r
      cols[i3 + 1] = g
      cols[i3 + 2] = b
    }
    return { positions: pos, colors: cols }
  }, [count])

  // Sophisticated animation with voice reactivity
  useFrame((state) => {
    if (pointsRef.current) {
      const time = state.clock.elapsedTime
      const voiceIntensity = voiceData?.intensity || 0
      const voiceFrequency = voiceData?.frequency || 0

      // Multi-axis rotation with voice influence
      const baseRotationSpeed = morphSpeed * 0.3
      pointsRef.current.rotation.y += baseRotationSpeed + voiceIntensity * 0.02
      pointsRef.current.rotation.x += baseRotationSpeed * 0.5 + Math.sin(time * 0.5) * 0.01
      pointsRef.current.rotation.z += baseRotationSpeed * 0.2 + voiceFrequency * 0.0001

      // Complex voice-reactive scaling and breathing
      const breathe = Math.sin(time * 2) * 0.02
      const voiceScale = voiceIntensity * 0.4
      const scale = 1 + breathe + voiceScale
      pointsRef.current.scale.setScalar(scale)

      // Subtle position oscillation
      pointsRef.current.position.y = Math.sin(time * 0.8) * 0.1
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={size}
        sizeAttenuation={true}
        transparent
        opacity={0.9}
        vertexColors={true}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        alphaTest={0.001}
      />
    </points>
  )
}
