'use client'

import React, { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, Float, MeshDistortMaterial } from '@react-three/drei'
import * as THREE from 'three'

interface MorphingMeshProps {
  shape: string
  voiceData: { intensity: number; frequency: number }
  particleCount: number
  morphSpeed: number
  trinityState: {
    identity: boolean
    consciousness: boolean
    guardian: boolean
  }
}

function MorphingMesh({ shape, voiceData, particleCount, morphSpeed, trinityState }: MorphingMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const particlesRef = useRef<THREE.Points>(null)
  const [morphProgress, setMorphProgress] = useState(0)

  // Generate particle positions around the mesh
  const particlePositions = React.useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    for (let i = 0; i < particleCount * 3; i += 3) {
      const theta = Math.random() * Math.PI * 2
      const phi = Math.random() * Math.PI
      const radius = 3 + Math.random() * 2
      
      positions[i] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i + 2] = radius * Math.cos(phi)
    }
    return positions
  }, [particleCount])

  useFrame((state) => {
    if (meshRef.current) {
      // Voice-reactive morphing
      const intensity = voiceData.intensity || 0
      const frequency = voiceData.frequency || 0
      
      // Base rotation
      meshRef.current.rotation.x += 0.005 + intensity * 0.01
      meshRef.current.rotation.y += 0.01 + frequency * 0.0001
      
      // Scale pulsing with voice
      const scale = 1 + intensity * 0.2 + Math.sin(state.clock.elapsedTime * 2) * 0.05
      meshRef.current.scale.setScalar(scale)
      
      // Morph progress animation
      setMorphProgress((prev) => {
        const target = intensity > 0.5 ? 1 : 0
        return prev + (target - prev) * morphSpeed
      })
    }
    
    if (particlesRef.current) {
      // Animate particles
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.1
      particlesRef.current.rotation.x = state.clock.elapsedTime * 0.05
      
      // Particles respond to voice
      const scale = 1 + voiceData.intensity * 0.3
      particlesRef.current.scale.setScalar(scale)
    }
  })

  // Get color based on Trinity state
  const getMeshColor = () => {
    const activeStates = Object.entries(trinityState).filter(([_, active]) => active)
    if (activeStates.length === 0) return '#666666'
    if (activeStates.length === 3) return '#ffffff'
    
    const colors: Record<string, string> = {
      identity: '#8b5cf6',
      consciousness: '#3b82f6',
      guardian: '#22c55e'
    }
    
    return colors[activeStates[0][0]] || '#666666'
  }

  // Shape geometry selection
  const getGeometry = () => {
    switch (shape) {
      case 'cube':
        return <boxGeometry args={[2, 2, 2]} />
      case 'torus':
        return <torusGeometry args={[1.5, 0.6, 16, 100]} />
      case 'consciousness':
        return <icosahedronGeometry args={[2, 4]} />
      default:
        return <sphereGeometry args={[2, 32, 32]} />
    }
  }

  return (
    <>
      {/* Main morphing mesh */}
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <mesh ref={meshRef}>
          {getGeometry()}
          <MeshDistortMaterial
            color={getMeshColor()}
            emissive={getMeshColor()}
            emissiveIntensity={0.3 + voiceData.intensity * 0.5}
            roughness={0.2}
            metalness={0.8}
            distort={0.3 + morphProgress * 0.7}
            speed={2 + voiceData.frequency * 0.01}
            transparent
            opacity={0.9}
            wireframe={morphProgress > 0.5}
          />
        </mesh>
      </Float>
      
      {/* Particle cloud */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={particleCount}
            array={particlePositions}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.02}
          color={getMeshColor()}
          transparent
          opacity={0.6}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </points>
    </>
  )
}

interface MorphingVisualizerProps {
  config: any
  voiceData: { intensity: number; frequency: number }
}

export default function MorphingVisualizer({ config, voiceData }: MorphingVisualizerProps) {
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null)
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null)
  const animationRef = useRef<number>()

  useEffect(() => {
    if (config.micEnabled && !audioContext) {
      // Initialize audio context for voice processing
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
      const analyserNode = ctx.createAnalyser()
      analyserNode.fftSize = 256
      
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const source = ctx.createMediaStreamSource(stream)
          source.connect(analyserNode)
          setAudioContext(ctx)
          setAnalyser(analyserNode)
        })
        .catch(err => {
          console.error('Microphone access denied:', err)
        })
    }
    
    return () => {
      if (audioContext) {
        audioContext.close()
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [config.micEnabled])

  const trinityState = {
    identity: config.trinityIdentity || false,
    consciousness: config.trinityConsciousness || false,
    guardian: config.trinityGuardian || false
  }

  return (
    <div className="w-full h-full relative">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={0.8} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        <spotLight
          position={[0, 10, 0]}
          angle={0.3}
          penumbra={1}
          intensity={0.5}
          color="#00d4ff"
        />
        
        {/* Environment for reflections */}
        <Environment preset="city" />
        
        {/* Main morphing visualization */}
        <MorphingMesh
          shape={config.shape || 'sphere'}
          voiceData={voiceData}
          particleCount={config.particleCount || 1000}
          morphSpeed={config.morphSpeed || 0.02}
          trinityState={trinityState}
        />
        
        {/* Camera controls */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          autoRotate={!config.micEnabled}
          autoRotateSpeed={0.5}
          maxDistance={20}
          minDistance={5}
        />
      </Canvas>
      
      {/* Status overlay */}
      <div className="absolute top-4 left-4 pointer-events-none">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg px-3 py-2">
          <div className="flex items-center gap-3">
            {config.micEnabled && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs text-white/60">Voice Active</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              <span className="text-xs text-white/60">
                {config.shape || 'Sphere'} Mode
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Voice intensity indicator */}
      {config.micEnabled && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-none">
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-full px-4 py-2">
            <div className="flex items-center gap-3">
              <span className="text-xs text-white/60">Voice Intensity</span>
              <div className="w-32 h-1 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-100"
                  style={{ width: `${voiceData.intensity * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}