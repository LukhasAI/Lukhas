'use client'

import { Canvas } from '@react-three/fiber'
import { OrbitControls, useTexture } from '@react-three/drei'
import { useEffect, useRef } from 'react'

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
  // Load the texture from the URL provided in the manifest
  const texture = useTexture(manifest.texture_url)

  // TODO: Implement generative logic based on manifest.visuals
  // For now, we render a single spinning box as a placeholder.

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <mesh rotation={[0, 0, 0]}>
        <boxGeometry args={[3, 3, 3]} />
        <meshStandardMaterial map={texture} />
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
      <Canvas>
        <OrbitControls />
        <SceneContent manifest={manifest} />
      </Canvas>
      <audio ref={audioRef} controls className="w-full mt-2 hidden" />
      <p className="text-center text-gray-400 text-sm p-4 italic">
        "{manifest.narrative}"
      </p>
    </div>
  )
}
