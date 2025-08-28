'use client'

import React, { useEffect, useRef, Suspense, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import * as THREE from 'three'
import { useLoader } from '@react-three/fiber'
import { TextureLoader } from 'three'
import { ErrorBoundary } from 'react-error-boundary'

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

function DreamyObject({ manifest }: DreamSceneProps) {
  const meshRef = useRef<THREE.Mesh>(null!)
  const texture = useLoader(TextureLoader, manifest.texture_url)

  const geometry = useMemo(() => {
    switch (manifest.visuals.geometry.toLowerCase()) {
      case 'sphere':
        return new THREE.SphereGeometry(2, 32, 32)
      case 'torus':
        return new THREE.TorusGeometry(2, 0.5, 16, 100)
      case 'icosahedron':
        return new THREE.IcosahedronGeometry(2, 0)
      case 'cone':
        return new THREE.ConeGeometry(2, 3, 32)
      default:
        return new THREE.BoxGeometry(3, 3, 3)
    }
  }, [manifest.visuals.geometry])

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    switch (manifest.visuals.movement.toLowerCase()) {
      case 'gentle rotation':
        meshRef.current.rotation.x += delta * 0.1
        meshRef.current.rotation.y += delta * 0.2
        break
      case 'pulsating':
        meshRef.current.scale.setScalar(Math.sin(state.clock.elapsedTime) * 0.1 + 1)
        break
      case 'drifting':
        meshRef.current.position.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.5
        meshRef.current.position.y = Math.cos(state.clock.elapsedTime * 0.3) * 0.5
        break;
      default:
        meshRef.current.rotation.y += delta * 0.2
    }
  })

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial
        map={texture}
        color={manifest.visuals.colors[1] || '#ffffff'}
        emissive={manifest.visuals.colors[2] || '#000000'}
        roughness={0.2}
        metalness={0.8}
      />
    </mesh>
  )
}

function SceneContent({ manifest }: DreamSceneProps) {
  const primaryColor = manifest.visuals.colors[0] || '#6a0dad'

  return (
    <>
      <color attach="background" args={[primaryColor]} />
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} color={manifest.visuals.colors[1] || '#ffffff'} intensity={1} />
      <pointLight position={[-10, -10, -10]} color={manifest.visuals.colors[2] || '#ff00ff'} intensity={0.5} />
      <Stars radius={100} depth={50} count={manifest.visuals.particle_count || 5000} factor={4} saturation={0} fade />
      <Suspense fallback={null}>
        <DreamyObject manifest={manifest} />
      </Suspense>
    </>
  )
}

function ErrorFallback({ error }: { error: Error }) {
  return (
    <div role="alert" className="flex items-center justify-center h-full text-center text-white">
      <div>
        <p className="text-lg font-bold">Something went wrong in the dream scape:</p>
        <pre className="mt-2 text-sm text-red-400">{error.message}</pre>
      </div>
    </div>
  )
}

export function DreamScene({ manifest }: DreamSceneProps) {
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.src = manifest.audio_url
      audioRef.current.play().catch(e => console.error("Audio play failed:", e))
    }
  }, [manifest.audio_url])

  return (
    <div className="w-full h-[500px] bg-gray-950 rounded-lg border border-gray-700 mt-8 relative">
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <Canvas>
          <OrbitControls />
          <SceneContent manifest={manifest} />
        </Canvas>
      </ErrorBoundary>
      <div className="absolute bottom-0 left-0 w-full p-4 bg-gradient-to-t from-gray-950 to-transparent">
        <p className="text-center text-gray-300 text-sm italic">
          "{manifest.narrative}"
        </p>
        <audio ref={audioRef} controls className="w-full mt-2 h-8" />
      </div>
    </div>
  )
}
