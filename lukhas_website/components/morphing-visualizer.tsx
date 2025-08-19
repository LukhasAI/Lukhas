'use client'

import React, { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, Float, MeshDistortMaterial } from '@react-three/drei'
import * as THREE from 'three'

interface ParticleCloudProps {
  shape: string
  voiceData: { intensity: number; frequency: number }
  particleCount: number
  morphSpeed: number
  trinityState: {
    identity: boolean
    consciousness: boolean
    guardian: boolean
  }
  accentColor?: string
  tempo?: number
  voiceSensitivity?: number
  renderMode?: 'particles' | 'mesh' | 'auto'
}

function ParticleCloud({
  shape,
  voiceData,
  particleCount,
  morphSpeed,
  trinityState,
  accentColor,
  tempo = 1,
  voiceSensitivity = 0.5,
  renderMode = 'particles'
}: ParticleCloudProps) {
  const particlesRef = useRef<THREE.Points>(null)
  const meshRef = useRef<THREE.Mesh>(null)
  const [morphProgress, setMorphProgress] = useState(0)
  const [currentPositions, setCurrentPositions] = useState<Float32Array>()
  const [targetPositions, setTargetPositions] = useState<Float32Array>()

  // Advanced shape generation system based on reference implementation
  const generateShapePositions = (shapeName: string, count: number): Float32Array => {
    const positions = new Float32Array(count * 3)
    const baseRadius = 3.0 // Consistent base radius
    
    for (let i = 0; i < count * 3; i += 3) {
      let x, y, z
      const particleIndex = i / 3
      const normalizedIndex = particleIndex / count
      
      switch (shapeName) {
        case 'cube':
          // Distribute particles in cube volume
          x = (Math.random() - 0.5) * baseRadius * 2
          y = (Math.random() - 0.5) * baseRadius * 2
          z = (Math.random() - 0.5) * baseRadius * 2
          break
          
        case 'torus':
          // Proper torus distribution
          const u = Math.random() * Math.PI * 2
          const v = Math.random() * Math.PI * 2
          const R = baseRadius * 0.8 // Major radius
          const r = baseRadius * 0.3 // Minor radius
          x = (R + r * Math.cos(v)) * Math.cos(u)
          y = r * Math.sin(v)
          z = (R + r * Math.cos(v)) * Math.sin(u)
          break
          
        case 'consciousness':
          // Complex icosahedral pattern with golden ratio
          const phi = (1 + Math.sqrt(5)) / 2
          const theta = normalizedIndex * Math.PI * 2 * phi
          const cosTheta = 1 - 2 * normalizedIndex
          const sinTheta = Math.sqrt(1 - cosTheta * cosTheta)
          const radius = baseRadius * (0.8 + Math.random() * 0.4)
          
          x = radius * sinTheta * Math.cos(theta)
          y = radius * cosTheta
          z = radius * sinTheta * Math.sin(theta)
          
          // Add consciousness spiraling
          const spiralPhase = normalizedIndex * Math.PI * 8
          x += Math.sin(spiralPhase + theta) * 0.3
          z += Math.cos(spiralPhase + theta) * 0.3
          y += Math.sin(normalizedIndex * Math.PI * 4) * 0.2
          break
          
        case 'cat':
          // More accurate cat shape distribution
          if (normalizedIndex < 0.15) {
            // Head - sphere
            const headTheta = Math.random() * Math.PI * 2
            const headPhi = Math.random() * Math.PI
            const headRadius = baseRadius * 0.4
            x = headRadius * Math.sin(headPhi) * Math.cos(headTheta)
            y = baseRadius * 0.7 + headRadius * Math.cos(headPhi)
            z = headRadius * Math.sin(headPhi) * Math.sin(headTheta)
          } else if (normalizedIndex < 0.25) {
            // Ears - triangular points
            const earSide = Math.random() > 0.5 ? 1 : -1
            x = earSide * baseRadius * (0.3 + Math.random() * 0.15)
            y = baseRadius * (0.9 + Math.random() * 0.3)
            z = (Math.random() - 0.5) * baseRadius * 0.2
          } else if (normalizedIndex < 0.75) {
            // Body - elongated ellipsoid
            const bodyTheta = Math.random() * Math.PI * 2
            const bodyPhi = Math.random() * Math.PI
            const bodyRadiusX = baseRadius * 0.6
            const bodyRadiusY = baseRadius * 0.8
            const bodyRadiusZ = baseRadius * 0.4
            x = bodyRadiusX * Math.sin(bodyPhi) * Math.cos(bodyTheta)
            y = bodyRadiusY * Math.cos(bodyPhi) * 0.3
            z = bodyRadiusZ * Math.sin(bodyPhi) * Math.sin(bodyTheta)
          } else {
            // Tail - curved parametric
            const tailT = (normalizedIndex - 0.75) / 0.25
            const tailAngle = tailT * Math.PI * 2
            x = -baseRadius * (0.8 + tailT * 0.5) + Math.sin(tailAngle) * baseRadius * 0.3
            y = -baseRadius * 0.3 + Math.cos(tailAngle * 2) * baseRadius * 0.2
            z = Math.sin(tailAngle * 3) * baseRadius * 0.25
          }
          break
          
        case 'heart':
          // Parametric heart equation
          const heartT = normalizedIndex * Math.PI * 2
          const heartScale = baseRadius * 0.15
          x = heartScale * 16 * Math.pow(Math.sin(heartT), 3)
          y = heartScale * (13 * Math.cos(heartT) - 5 * Math.cos(2 * heartT) - 2 * Math.cos(3 * heartT) - Math.cos(4 * heartT))
          z = (Math.random() - 0.5) * baseRadius * 0.3
          break
          
        case 'spiral':
        case 'helix':
          // DNA double helix
          const spiralT = normalizedIndex * Math.PI * 12
          const spiralRadius = baseRadius * 0.8
          const helixStrand = Math.floor(particleIndex) % 2
          const strandOffset = helixStrand * Math.PI
          
          x = spiralRadius * Math.cos(spiralT + strandOffset)
          z = spiralRadius * Math.sin(spiralT + strandOffset)
          y = (normalizedIndex - 0.5) * baseRadius * 3
          break
          
        default: // sphere
          // Uniform sphere distribution using Marsaglia method
          const u1 = Math.random()
          const u2 = Math.random()
          const theta = 2 * Math.PI * u1
          const phi = Math.acos(2 * u2 - 1)
          const radius = baseRadius * Math.cbrt(Math.random()) // Uniform volume distribution
          
          x = radius * Math.sin(phi) * Math.cos(theta)
          y = radius * Math.sin(phi) * Math.sin(theta)
          z = radius * Math.cos(phi)
      }
      
      positions[i] = x
      positions[i + 1] = y
      positions[i + 2] = z
    }
    return positions
  }

  // Initialize particle positions and create morphing system
  React.useEffect(() => {
    const current = generateShapePositions(shape, particleCount)
    setCurrentPositions(current)
    setTargetPositions(current.slice()) // Copy for morphing
  }, [shape, particleCount])

  // Generate new target positions when shape changes
  React.useEffect(() => {
    if (currentPositions) {
      const target = generateShapePositions(shape, particleCount)
      setTargetPositions(target)
      setMorphProgress(0) // Reset morphing
    }
  }, [shape, particleCount])

  // Main animation loop - particles only, no mesh
  useFrame((state) => {
    if (!particlesRef.current || !currentPositions || !targetPositions) return

    // Voice-reactive parameters
    const voiceIntensity = (voiceData.intensity || 0) * voiceSensitivity
    const voiceFrequency = (voiceData.frequency || 0) * voiceSensitivity
    
    // Slow, controlled rotation
    const rotationSpeed = morphSpeed * 0.1
    particlesRef.current.rotation.y += (rotationSpeed + voiceIntensity * 0.001) * tempo
    particlesRef.current.rotation.x += (rotationSpeed * 0.5 + voiceFrequency * 0.0001) * tempo
    
    // Dynamic particle scaling based on voice
    const baseScale = 1 + Math.sin(state.clock.elapsedTime * 1.5 * tempo) * 0.05
    const voiceScale = voiceIntensity * 0.2
    particlesRef.current.scale.setScalar(baseScale + voiceScale)
    
    // Shape morphing progress
    if (morphProgress < 1) {
      setMorphProgress((prev) => Math.min(1, prev + morphSpeed * 2))
    }
    
    // Update particle positions in real-time
    const geometry = particlesRef.current.geometry
    const positions = geometry.attributes.position.array as Float32Array
    
    for (let i = 0; i < positions.length; i += 3) {
      const particleIndex = i / 3
      
      // Get current and target positions
      const currentX = currentPositions[i]
      const currentY = currentPositions[i + 1]
      const currentZ = currentPositions[i + 2]
      const targetX = targetPositions[i]
      const targetY = targetPositions[i + 1]
      const targetZ = targetPositions[i + 2]
      
      // Interpolate between current and target (morphing)
      let x = currentX + (targetX - currentX) * morphProgress
      let y = currentY + (targetY - currentY) * morphProgress
      let z = currentZ + (targetZ - currentZ) * morphProgress
      
      // Voice-reactive particle movement
      const time = state.clock.elapsedTime
      const particlePhase = particleIndex * 0.01
      const waveAmplitude = voiceIntensity * 0.1
      
      x += Math.sin(time * 1.2 + particlePhase) * waveAmplitude
      y += Math.cos(time * 0.8 + particlePhase * 1.5) * waveAmplitude
      z += Math.sin(time * 1.0 + particlePhase * 2) * waveAmplitude
      
      // Frequency-based particle dispersion
      const dispersion = voiceFrequency * 0.0001
      x += (Math.random() - 0.5) * dispersion
      y += (Math.random() - 0.5) * dispersion
      z += (Math.random() - 0.5) * dispersion
      
      positions[i] = x
      positions[i + 1] = y
      positions[i + 2] = z
    }
    
    // Update morph progress for continuous animation
    if (morphProgress >= 1 && voiceIntensity > 0.1) {
      setMorphProgress(0) // Reset for continuous morphing with voice
    }
    
    geometry.attributes.position.needsUpdate = true
  })

  // Advanced dynamic color system with voice reactivity and configuration
  const getParticleColor = () => {
    if (accentColor) return accentColor
    
    const activeStates = Object.entries(trinityState).filter(([_, active]) => active)
    const voiceIntensity = (voiceData.intensity || 0) * voiceSensitivity
    const voiceFrequency = (voiceData.frequency || 0) * voiceSensitivity
    
    // Get base color from Trinity state
    let baseColor = '#ffffff'
    if (activeStates.length === 0) baseColor = '#666666'
    else if (activeStates.length === 3) baseColor = '#ffffff'
    else {
      const colors: Record<string, string> = {
        identity: '#8b5cf6',     // Purple
        consciousness: '#3b82f6', // Blue  
        guardian: '#22c55e'      // Green
      }
      baseColor = colors[activeStates[0][0]] || '#666666'
    }
    
    const color = new THREE.Color(baseColor)
    
    // Apply voice-reactive color changes if enabled
    if ((window as any).config?.voiceColorReactive && voiceIntensity > 0.05) {
      const hsl = { h: 0, s: 0, l: 0 }
      color.getHSL(hsl)
      
      const colorIntensity = (window as any).config?.colorIntensity || 0.5
      
      // Advanced voice-reactive color transformations
      switch ((window as any).config?.textureStyle || 'smooth') {
        case 'neural':
          // Neural: Rapid hue shifts with frequency
          hsl.h = (hsl.h + Math.sin(voiceFrequency * 0.001) * colorIntensity * 0.3) % 1
          hsl.s = Math.min(1, hsl.s + voiceIntensity * colorIntensity * 0.5)
          break
          
        case 'geometric':
          // Geometric: Stepped hue changes
          const steps = Math.floor(voiceFrequency * 0.0001 * 8) * 0.125
          hsl.h = (hsl.h + steps * colorIntensity) % 1
          hsl.s = Math.min(1, hsl.s + (voiceIntensity > 0.5 ? colorIntensity * 0.4 : 0))
          break
          
        case 'ethereal':
          // Ethereal: Subtle, flowing color changes
          hsl.h = (hsl.h + Math.sin(voiceFrequency * 0.0005) * colorIntensity * 0.15) % 1
          hsl.l = Math.min(0.9, hsl.l + Math.cos(voiceIntensity * 5) * colorIntensity * 0.3)
          break
          
        default: // smooth
          // Smooth: Continuous hue rotation with voice
          hsl.h = (hsl.h + voiceFrequency * 0.0002 * colorIntensity) % 1
          hsl.s = Math.min(1, hsl.s + voiceIntensity * colorIntensity * 0.3)
          hsl.l = Math.min(1, hsl.l + voiceIntensity * colorIntensity * 0.2)
      }
      
      color.setHSL(hsl.h, hsl.s, hsl.l)
    }
    
    return color
  }

  // Fallback mesh for performance mode
  const renderMesh = renderMode === 'mesh' && (
    <Float speed={0.5 * tempo} rotationIntensity={0.1} floatIntensity={0.2}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[3, 32, 32]} />
        <MeshDistortMaterial
          color={getParticleColor()}
          emissive={getParticleColor()}
          emissiveIntensity={0.3 + (voiceData.intensity || 0) * voiceSensitivity * 0.5}
          roughness={0.3}
          metalness={0.7}
          distort={0.2 + morphProgress * 0.3}
          speed={1 + (voiceData.frequency || 0) * 0.001}
          transparent
          opacity={0.8}
        />
      </mesh>
    </Float>
  )

  // Main particle cloud system with advanced effects
  const renderParticles = (renderMode === 'particles' || renderMode === 'auto') && currentPositions && (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={currentPositions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={(() => {
          const baseSize = 0.08
          const morphSize = morphProgress * 0.04
          const voiceSize = (voiceData.intensity || 0) * voiceSensitivity * 0.02
          const glowBoost = ((window as any).config?.glowIntensity || 0.3) * 0.03
          return baseSize + morphSize + voiceSize + glowBoost
        })()}
        color={getParticleColor()}
        transparent
        opacity={(() => {
          const baseOpacity = 0.9
          const glowIntensity = (window as any).config?.glowIntensity || 0.3
          const textureStyle = (window as any).config?.textureStyle || 'smooth'
          
          // Adjust opacity based on texture style
          switch (textureStyle) {
            case 'neural': return Math.min(1, baseOpacity + glowIntensity * 0.2)
            case 'geometric': return baseOpacity * (0.8 + glowIntensity * 0.3)
            case 'ethereal': return baseOpacity * (0.6 + glowIntensity * 0.5)
            default: return baseOpacity + glowIntensity * 0.1
          }
        })()}
        sizeAttenuation
        blending={(() => {
          const textureStyle = (window as any).config?.textureStyle || 'smooth'
          // Use different blending modes for different texture styles
          switch (textureStyle) {
            case 'neural': return THREE.AdditiveBlending
            case 'geometric': return THREE.NormalBlending
            case 'ethereal': return THREE.AdditiveBlending
            default: return THREE.AdditiveBlending
          }
        })()}
      />
    </points>
  )

  return (
    <>
      {renderMesh}
      {renderParticles}
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
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const [isCalmMode, setIsCalmMode] = useState(false)
  const animationRef = useRef<number>()

  useEffect(() => {
    // Check system preference for reduced motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)
    
    const handleMediaChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }
    
    mediaQuery.addEventListener('change', handleMediaChange)
    
    // Check for calm mode
    const checkCalmMode = () => {
      setIsCalmMode(document.body.classList.contains('calm-mode'))
    }
    
    checkCalmMode()
    
    // Listen for calm mode changes
    const handleCalmModeChange = (e: CustomEvent) => {
      setIsCalmMode(e.detail.enabled)
    }
    
    window.addEventListener('calmModeToggle', handleCalmModeChange as EventListener)
    
    return () => {
      mediaQuery.removeEventListener('change', handleMediaChange)
      window.removeEventListener('calmModeToggle', handleCalmModeChange as EventListener)
    }
  }, [])

  useEffect(() => {
    if (config.micEnabled && !audioContext) {
      // Initialize audio context for voice processing
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
      const analyserNode = ctx.createAnalyser()
      analyserNode.fftSize = 512 // Increased for better frequency resolution
      analyserNode.smoothingTimeConstant = 0.3
      
      navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
        .then(stream => {
          const source = ctx.createMediaStreamSource(stream)
          source.connect(analyserNode)
          setAudioContext(ctx)
          setAnalyser(analyserNode)
          
          // Start real-time audio analysis
          const analyzeAudio = () => {
            if (!analyserNode) return
            
            const bufferLength = analyserNode.frequencyBinCount
            const dataArray = new Uint8Array(bufferLength)
            analyserNode.getByteFrequencyData(dataArray)
            
            // Calculate intensity (average amplitude)
            let sum = 0
            for (let i = 0; i < bufferLength; i++) {
              sum += dataArray[i]
            }
            const intensity = sum / bufferLength / 255
            
            // Calculate dominant frequency
            let maxAmplitude = 0
            let dominantFrequency = 0
            for (let i = 0; i < bufferLength; i++) {
              if (dataArray[i] > maxAmplitude) {
                maxAmplitude = dataArray[i]
                dominantFrequency = i * (ctx.sampleRate / 2) / bufferLength
              }
            }
            
            // Update voice data with real audio analysis
            window.dispatchEvent(new CustomEvent('audioUpdate', {
              detail: {
                intensity: intensity * (config.voiceSensitivity || 0.5),
                frequency: dominantFrequency,
                rawData: dataArray
              }
            }))
            
            if (config.micEnabled) {
              animationRef.current = requestAnimationFrame(analyzeAudio)
            }
          }
          
          analyzeAudio()
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
  }, [config.micEnabled, config.voiceSensitivity])

  // Listen for real-time audio updates
  useEffect(() => {
    const handleAudioUpdate = (event: CustomEvent) => {
      const { intensity, frequency } = event.detail
      // Update voice data state for immediate response
      if (typeof window !== 'undefined') {
        (window as any).currentVoiceData = { intensity, frequency }
      }
    }

    window.addEventListener('audioUpdate', handleAudioUpdate as EventListener)
    return () => window.removeEventListener('audioUpdate', handleAudioUpdate as EventListener)
  }, [])

  const trinityState = {
    identity: config.trinityIdentity || false,
    consciousness: config.trinityConsciousness || false,
    guardian: config.trinityGuardian || false
  }

  // Calculate motion scale based on preferences
  const motionScale = prefersReducedMotion || isCalmMode ? 0 : 1
  const adjustedTempo = (config.tempo || 1) * motionScale
  const adjustedMorphSpeed = (config.morphSpeed || 0.005) * motionScale

  // Expose config globally for particle system access
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).config = config
    }
  }, [config])

  return (
    <div className="w-full h-full relative">
      <Canvas
        camera={{ position: [0, 0, 12], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={1.0} />
        <pointLight position={[-10, -10, -10]} intensity={0.7} />
        <pointLight position={[0, 0, 15]} intensity={0.8} />
        <spotLight
          position={[0, 10, 0]}
          angle={0.4}
          penumbra={1}
          intensity={0.7}
          color="#00d4ff"
        />
        
        {/* Dynamic Environment with sync support */}
        <Environment 
          preset={(() => {
            const environmentSync = config.environmentSync || 0.2
            const textureStyle = config.textureStyle || 'smooth'
            
            if (environmentSync < 0.3) return "city"
            
            // Choose environment based on texture style and sync level
            switch (textureStyle) {
              case 'neural': return "dawn"
              case 'geometric': return "warehouse"
              case 'ethereal': return "night"
              default: return "city"
            }
          })()} 
        />
        
        {/* New particle cloud system */}
        <ParticleCloud
          shape={config.shape || 'sphere'}
          voiceData={voiceData}
          particleCount={config.particleCount || 3000}
          morphSpeed={adjustedMorphSpeed}
          trinityState={trinityState}
          accentColor={config.accentColor}
          tempo={adjustedTempo}
          voiceSensitivity={config.voiceSensitivity || 0.5}
          renderMode={config.renderMode || 'particles'}
        />
        
        {/* Camera controls */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          autoRotate={!config.micEnabled && motionScale > 0}
          autoRotateSpeed={0.2 * motionScale}
          maxDistance={25}
          minDistance={8}
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