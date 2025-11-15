/**
 * MorphingParticles Usage Examples
 *
 * This file demonstrates how to use the MorphingParticles component
 * in different scenarios for the LUKHAS websites.
 */

import React, { useState, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { MorphingParticles, type MorphingShape, type VoiceData } from './MorphingParticles'

/**
 * Example 1: Basic Usage
 * Simple particle cloud with consciousness shape
 */
export function BasicExample() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <MorphingParticles shape="consciousness" />
      </Canvas>
    </div>
  )
}

/**
 * Example 2: Interactive Shape Selector
 * User can click buttons to change shapes
 */
export function InteractiveExample() {
  const [shape, setShape] = useState<MorphingShape>('sphere')

  const shapes: MorphingShape[] = ['sphere', 'consciousness', 'guardian', 'identity', 'neural', 'quantum', 'cat']

  return (
    <div>
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {shapes.map((s) => (
          <button
            key={s}
            onClick={() => setShape(s)}
            style={{
              padding: '0.5rem 1rem',
              background: shape === s ? '#00d4ff' : 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'white',
              cursor: 'pointer',
              textTransform: 'uppercase',
              fontSize: '0.875rem',
              letterSpacing: '0.05em',
            }}
          >
            {s}
          </button>
        ))}
      </div>

      <div style={{ width: '100%', height: '600px' }}>
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <MorphingParticles shape={shape} />
        </Canvas>
      </div>
    </div>
  )
}

/**
 * Example 3: Voice Modulation
 * Particles react to microphone input
 */
export function VoiceModulationExample() {
  const [shape, setShape] = useState<MorphingShape>('neural')
  const [voiceData, setVoiceData] = useState<VoiceData>({ intensity: 0, frequency: 0 })
  const [isListening, setIsListening] = useState(false)

  useEffect(() => {
    let audioContext: AudioContext
    let analyser: AnalyserNode
    let animationFrameId: number

    if (isListening) {
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          audioContext = new AudioContext()
          const source = audioContext.createMediaStreamSource(stream)
          analyser = audioContext.createAnalyser()
          analyser.fftSize = 256

          source.connect(analyser)

          const dataArray = new Uint8Array(analyser.frequencyBinCount)

          const analyze = () => {
            analyser.getByteFrequencyData(dataArray)

            let sum = 0
            for (let i = 0; i < dataArray.length; i++) {
              sum += dataArray[i]
            }

            const intensity = sum / dataArray.length
            setVoiceData({ intensity, frequency: intensity * 100 })

            animationFrameId = requestAnimationFrame(analyze)
          }

          analyze()
        })
        .catch((error) => {
          console.error('Microphone access denied:', error)
          setIsListening(false)
        })
    }

    return () => {
      if (audioContext) audioContext.close()
      if (animationFrameId) cancelAnimationFrame(animationFrameId)
    }
  }, [isListening])

  return (
    <div>
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button
          onClick={() => setIsListening(!isListening)}
          style={{
            padding: '0.5rem 1rem',
            background: isListening ? '#00ff88' : '#00d4ff',
            border: 'none',
            color: '#0a0a0a',
            cursor: 'pointer',
            textTransform: 'uppercase',
            fontSize: '0.875rem',
            letterSpacing: '0.05em',
            fontWeight: 'bold',
          }}
        >
          {isListening ? 'Stop Voice' : 'Start Voice'}
        </button>
        <span style={{ color: 'rgba(255,255,255,0.6)', fontFamily: 'monospace', fontSize: '0.875rem' }}>
          Intensity: {Math.round(voiceData.intensity)} | Frequency: {Math.round(voiceData.frequency)}
        </span>
      </div>

      <div style={{ width: '100%', height: '600px' }}>
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <MorphingParticles shape={shape} voiceData={voiceData} />
        </Canvas>
      </div>
    </div>
  )
}

/**
 * Example 4: Custom Configuration
 * More particles, custom rotation, orbit controls
 */
export function CustomConfigExample() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas camera={{ position: [0, 0, 10], fov: 45 }}>
        <MorphingParticles
          shape="quantum"
          particleCount={8192} // More particles for denser cloud
          rotationSpeed={0.3} // Slower rotation
          baseParticleSize={4.0} // Smaller particles
          color="#9333EA" // Custom purple color
        />
        <OrbitControls enableZoom={true} enablePan={false} />
      </Canvas>
    </div>
  )
}

/**
 * Example 5: lukhas.id - Identity Page Hero
 * Lambda-inspired identity shape with purple accent
 */
export function LukhasIdHero() {
  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <MorphingParticles shape="identity" color="#9333EA" rotationSpeed={0.4} />
      </Canvas>

      {/* Overlay content */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          color: 'white',
          zIndex: 10,
        }}
      >
        <h1
          style={{
            fontSize: '4rem',
            fontWeight: 100,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            marginBottom: '1rem',
          }}
        >
          LUKHAS
        </h1>
        <p style={{ fontSize: '1.25rem', fontWeight: 300, letterSpacing: '0.1em', opacity: 0.8 }}>
          Identity & Authentication
        </p>
      </div>
    </div>
  )
}

/**
 * Example 6: lukhas.com - Platform Page with Auto-Cycling Shapes
 * Automatically cycles through Constellation shapes
 */
export function LukhasComPlatform() {
  const shapes: MorphingShape[] = ['consciousness', 'guardian', 'neural', 'quantum']
  const [shapeIndex, setShapeIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setShapeIndex((prev) => (prev + 1) % shapes.length)
    }, 5000) // Change shape every 5 seconds

    return () => clearInterval(interval)
  }, [shapes.length])

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <MorphingParticles shape={shapes[shapeIndex]} rotationSpeed={0.5} />
      </Canvas>
    </div>
  )
}

/**
 * Example 7: Cat Easter Egg
 * Fun cat shape with Luke Gold color
 */
export function CatEasterEgg() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <MorphingParticles shape="cat" color="#d4af37" rotationSpeed={0.6} autoRotate={true} />
      </Canvas>

      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          color: '#d4af37',
          fontSize: '3rem',
        }}
      >
        🐱 Meow!
      </div>
    </div>
  )
}
