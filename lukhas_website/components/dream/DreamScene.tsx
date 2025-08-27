'use client'

import React from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { useEffect, useRef, Suspense } from 'react'
import { useLoader } from '@react-three/fiber'
import { TextureLoader } from 'three'

class DreamErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: any) {
    return { hasError: true }
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('Dream visualization error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }

    return this.props.children
  }
}

// Define the structure of the Dream Manifest for TypeScript
interface DreamManifest {
  narrative: string
  visuals: {
    geometry: string
    movement: string
    colors: string[]
    particle_count: number
  }
  audio_url: string
  texture_url: string
  dream_id: string
}

interface DreamSceneProps {
  manifest: DreamManifest
}

function SceneContent({ manifest }: DreamSceneProps) {
  // Convert colors from hex to RGB for Three.js
  const primaryColor = manifest.visuals.colors[0] || '#6a0dad'

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <mesh rotation={[0, 0, 0]}>
        <boxGeometry args={[3, 3, 3]} />
        <meshStandardMaterial color={primaryColor} />
      </mesh>
    </>
  )
}

function TexturedSceneContent({ manifest }: DreamSceneProps) {
  const texture = useLoader(TextureLoader, manifest.texture_url)
  const primaryColor = manifest.visuals.colors[0] || '#6a0dad'

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <mesh rotation={[0, 0, 0]}>
        <boxGeometry args={[3, 3, 3]} />
        <meshStandardMaterial 
          map={texture} 
          color={primaryColor}
        />
      </mesh>
    </>
  )
}

export function DreamScene({ manifest }: DreamSceneProps) {
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    // Play the audio when the scene is mounted
    if (audioRef.current) {
      audioRef.current.src = manifest.audio_url
      audioRef.current.play().catch(e => console.error("Audio play failed:", e))
    }
  }, [manifest.audio_url])

  return (
    <div className="w-full h-[500px] bg-gray-950 rounded-lg border border-gray-700 mt-8">
      <DreamErrorBoundary 
        fallback={
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 rounded-lg mx-auto mb-4"></div>
              <p className="text-white/60">Dream visualization loading...</p>
            </div>
          </div>
        }
      >
        <Canvas>
          <OrbitControls />
          <Suspense fallback={<SceneContent manifest={manifest} />}>
            <TexturedSceneContent manifest={manifest} />
          </Suspense>
        </Canvas>
      </DreamErrorBoundary>
      <audio ref={audioRef} controls className="w-full mt-2 hidden" />
      <p className="text-center text-gray-400 text-sm p-4 italic">
        "{manifest.narrative}"
      </p>
    </div>
  )
}
