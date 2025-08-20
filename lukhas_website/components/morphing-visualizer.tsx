'use client'

import React, { useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, Float, MeshDistortMaterial } from '@react-three/drei'
import * as THREE from 'three'
import { glyphToTargets, makeGlyphSamplerCache, getOptimalRenderMode } from '@/lib/glyphSampler'
import { mulberry32, seedFromString } from '@/lib/prng'

interface ParticleFormProps {
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
  renderMode?: 'particles' | 'mesh+particles'
  glyphText?: string // for glyph rendering
}

// Glyph cache for text rendering
const glyphCache = makeGlyphSamplerCache(24)

function ParticleForm({
  voiceData,
  particleCount,
  morphSpeed,
  trinityState,
  accentColor,
  tempo = 1,
  voiceSensitivity = 0.5,
  renderMode = 'particles',
  glyphText
}: ParticleFormProps) {
  const particlesRef = useRef<THREE.Points>(null)
  const meshRef = useRef<THREE.Mesh>(null)
  const [morphProgress, setMorphProgress] = useState(0)
  const [currentPositions, setCurrentPositions] = useState<Float32Array>()
  const [targetPositions, setTargetPositions] = useState<Float32Array>()

  // Simplified sphere-based form generation (no complex shapes)
  const generateSpherePositions = (count: number): Float32Array => {
    const positions = new Float32Array(count * 3)
    const baseRadius = 3.0
    
    for (let i = 0; i < count * 3; i += 3) {
      // Uniform sphere distribution using Marsaglia method
      const u1 = Math.random()
      const u2 = Math.random()
      const theta = 2 * Math.PI * u1
      const phi = Math.acos(2 * u2 - 1)
      const radius = baseRadius * Math.cbrt(Math.random()) // Uniform volume distribution
      
      positions[i] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i + 2] = radius * Math.cos(phi)
    }
    return positions
  }

  // Generate glyph positions when glyphText is provided
  const generateGlyphPositions = (text: string, count: number): Float32Array => {
    const positions = new Float32Array(count * 3)
    if (!text || text.trim().length === 0) {
      return generateSpherePositions(count)
    }
    
    try {
      // Create seeded RNG for this text
      const seed = seedFromString(text.toUpperCase())
      const rng = mulberry32(seed)
      
      // Use cached glyph sampler with seeded RNG
      return glyphCache.get(text, count, {
        canvasW: 768,
        canvasH: 384,
        fontPx: 180,
        worldScale: 1.6,
        sampleStride: 2,
        jitter: 0.02,
        alphaThreshold: 180,
        centerBias: 0.35,
        bold: true,
        uppercase: true,
        deterministic: true,
        rng  // Pass seeded RNG
      })
    } catch (e) {
      console.warn('[ParticleForm] Glyph generation failed, falling back to sphere:', e)
      return generateSpherePositions(count)
    }
  }

  // Initialize particle positions and create morphing system
  React.useEffect(() => {
    const current = glyphText ? generateGlyphPositions(glyphText, particleCount) : generateSpherePositions(particleCount)
    setCurrentPositions(current)
    setTargetPositions(current.slice()) // Copy for morphing
  }, [particleCount])

  // Generate new target positions when glyph text changes
  React.useEffect(() => {
    if (currentPositions) {
      const target = glyphText ? generateGlyphPositions(glyphText, particleCount) : generateSpherePositions(particleCount)
      setTargetPositions(target)
      setMorphProgress(0) // Reset morphing
      
      // Trigger legibility hold event for glyph rendering
      if (glyphText && glyphText.trim().length > 0) {
        window.dispatchEvent(new CustomEvent('legibilityHold', {
          detail: { text: glyphText, duration: 2000 }
        }))
      }
    }
  }, [glyphText, particleCount])

  // Main animation loop - particles only, no mesh
  useFrame((state) => {
    if (!particlesRef.current || !currentPositions || !targetPositions) return

    // Voice-reactive parameters
    const voiceIntensity = (voiceData.intensity || 0) * voiceSensitivity
    const voiceFrequency = (voiceData.frequency || 0) * voiceSensitivity
    
    // Slow, controlled rotation
    const rotationSpeed = morphSpeed * 0.3
    particlesRef.current.rotation.y += (rotationSpeed + voiceIntensity * 0.001) * tempo
    particlesRef.current.rotation.x += (rotationSpeed * 0.3 + voiceFrequency * 0.0001) * tempo
    
    // Dynamic particle scaling based on voice
    const baseScale = 1 + Math.sin(state.clock.elapsedTime * 1.5 * tempo) * 0.05
    const voiceScale = voiceIntensity * 0.2
    particlesRef.current.scale.setScalar(baseScale + voiceScale)
    
    // Shape morphing progress
    if (morphProgress < 1) {
      setMorphProgress((prev) => Math.min(1, prev + morphSpeed * 3))
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
    
    // Complete morphing transition
    if (morphProgress >= 1) {
      setCurrentPositions(targetPositions.slice()) // Update current to target
      setMorphProgress(1) // Keep at 1 until new shape selected
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

  // Single sphere geometry for mesh mode
  const getGeometry = () => {
    return <sphereGeometry args={[2, 32, 32]} />
  }

  // Metallic base mesh for mesh+particles mode
  const renderMesh = renderMode === 'mesh+particles' && (
    <Float speed={0.8 * tempo} rotationIntensity={0.2} floatIntensity={0.3}>
      <mesh ref={meshRef}>
        {getGeometry()}
        <MeshDistortMaterial
          color={getParticleColor()}
          emissive={getParticleColor()}
          emissiveIntensity={(0.2 + (voiceData.intensity || 0) * voiceSensitivity * 0.3) * (0.8 + 0.2 * tempo)}
          roughness={0.1}
          metalness={0.9}
          distort={0.2 + morphProgress * 0.5}
          speed={1.5 + (voiceData.frequency || 0) * 0.008}
          transparent
          opacity={0.25}
          wireframe={false}
        />
      </mesh>
    </Float>
  )

  // Enhanced metallic particle system with proper sizing
  const renderParticles = currentPositions && (
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
        size={0.8 + morphProgress * 0.2 + (voiceData.intensity || 0) * voiceSensitivity * 0.3}
        color={getParticleColor()}
        transparent
        opacity={0.7 + (voiceData.intensity || 0) * voiceSensitivity * 0.2}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
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
  const [optimalRenderMode, setOptimalRenderMode] = useState<'particles' | 'mesh+particles'>('particles')
  const [legibilityHold, setLegibilityHold] = useState<{text: string, visible: boolean}>({text: '', visible: false})
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
    
    // Listen for legibility hold events
    const handleLegibilityHold = (e: CustomEvent) => {
      const { text, duration } = e.detail
      setLegibilityHold({ text, visible: true })
      setTimeout(() => {
        setLegibilityHold(prev => ({ ...prev, visible: false }))
      }, duration || 2000)
    }
    
    // Detect optimal render mode based on GPU capability
    setOptimalRenderMode(getOptimalRenderMode())
    
    window.addEventListener('calmModeToggle', handleCalmModeChange as EventListener)
    window.addEventListener('legibilityHold', handleLegibilityHold as EventListener)
    
    return () => {
      mediaQuery.removeEventListener('change', handleMediaChange)
      window.removeEventListener('calmModeToggle', handleCalmModeChange as EventListener)
      window.removeEventListener('legibilityHold', handleLegibilityHold as EventListener)
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
  const adjustedMorphSpeed = (config.morphSpeed || 0.02) * motionScale

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
        
        {/* Enhanced particle form system */}
        <ParticleForm
          voiceData={voiceData}
          particleCount={config.particleCount || 1000}
          morphSpeed={adjustedMorphSpeed}
          trinityState={trinityState}
          accentColor={config.accentColor}
          tempo={adjustedTempo}
          voiceSensitivity={config.voiceSensitivity || 0.5}
          renderMode={config.renderMode || optimalRenderMode}
          glyphText={config.glyphText}
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
                {config.glyphText ? `"${config.glyphText}"` : 'Form Field'} Mode
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Legibility hold indicator */}
      {legibilityHold.visible && (
        <div className="absolute top-4 right-4 pointer-events-none">
          <div className="bg-black/60 backdrop-blur-xl border border-yellow-500/30 rounded-lg px-4 py-2 animate-pulse">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full" />
              <span className="text-xs text-yellow-500/90 font-medium">
                Legibility hold: "{legibilityHold.text}"
              </span>
            </div>
          </div>
        </div>
      )}
      
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