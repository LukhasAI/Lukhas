'use client'

import React, { useRef, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Sphere, Box, MeshDistortMaterial, Float, Trail } from '@react-three/drei'
import { motion, AnimatePresence } from 'framer-motion'
import * as THREE from 'three'
import { Atom, Brain, Shield } from 'lucide-react'
import { mulberry32, seedFromString } from '@/lib/prng'

interface TrinityNodeProps {
  position: [number, number, number]
  color: string
  label: string
  icon: React.ElementType
  isActive: boolean
  onClick: () => void
}

function TrinityNode({ position, color, label, icon: Icon, isActive, onClick }: TrinityNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.005
      meshRef.current.rotation.y += 0.01

      const scale = hovered ? 1.2 : isActive ? 1.1 : 1
      meshRef.current.scale.lerp(new THREE.Vector3(scale, scale, scale), 0.1)
    }
  })

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <Trail
        width={5}
        length={10}
        color={new THREE.Color(color)}
        attenuation={(t) => t * t}
      >
        <mesh
          ref={meshRef}
          position={position}
          onClick={onClick}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
        >
          <sphereGeometry args={[1, 32, 32]} />
          <MeshDistortMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isActive ? 0.5 : 0.2}
            roughness={0.1}
            metalness={0.8}
            distort={0.3}
            speed={2}
            transparent
            opacity={isActive ? 1 : 0.8}
          />
        </mesh>
      </Trail>
    </Float>
  )
}

function ConnectionBeam({ start, end, color, intensity = 1 }: {
  start: [number, number, number]
  end: [number, number, number]
  color: string
  intensity?: number
}) {
  const ref = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (ref.current) {
      ref.current.material.opacity = 0.3 + Math.sin(state.clock.elapsedTime * 2) * 0.2
    }
  })

  const midPoint: [number, number, number] = [
    (start[0] + end[0]) / 2,
    (start[1] + end[1]) / 2,
    (start[2] + end[2]) / 2,
  ]

  return (
    <mesh ref={ref} position={midPoint}>
      <cylinderGeometry args={[0.05 * intensity, 0.05 * intensity,
        Math.sqrt(
          Math.pow(end[0] - start[0], 2) +
          Math.pow(end[1] - start[1], 2) +
          Math.pow(end[2] - start[2], 2)
        ), 8]} />
      <meshBasicMaterial color={color} transparent opacity={0.3} />
    </mesh>
  )
}

function ParticleField() {
  const particlesRef = useRef<THREE.Points>(null)
  const particleCount = 500

  const positions = React.useMemo(() => {
    const pos = new Float32Array(particleCount * 3)
    const rng = mulberry32(seedFromString('trinity-particles'))
    for (let i = 0; i < particleCount * 3; i += 3) {
      pos[i] = (rng() - 0.5) * 20
      pos[i + 1] = (rng() - 0.5) * 20
      pos[i + 2] = (rng() - 0.5) * 20
    }
    return pos
  }, [])

  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.05
      particlesRef.current.rotation.x = state.clock.elapsedTime * 0.03
    }
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#ffffff"
        transparent
        opacity={0.3}
        sizeAttenuation
      />
    </points>
  )
}

function CentralCore({ activeNodes }: { activeNodes: string[] }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.3
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.5
      meshRef.current.rotation.z = state.clock.elapsedTime * 0.2
    }
  })

  const getColor = () => {
    if (activeNodes.length === 3) return '#ffffff'
    if (activeNodes.includes('identity')) return '#6b46c1'
    if (activeNodes.includes('consciousness')) return '#0ea5e9'
    if (activeNodes.includes('guardian')) return '#10b981'
    return '#333333'
  }

  return (
    <Float speed={1} rotationIntensity={0.2} floatIntensity={0.3}>
      <mesh ref={meshRef} position={[0, 0, 0]}>
        <icosahedronGeometry args={[0.5, 1]} />
        <MeshDistortMaterial
          color={getColor()}
          emissive={getColor()}
          emissiveIntensity={0.5}
          roughness={0.1}
          metalness={0.9}
          distort={0.2}
          speed={5}
          transparent
          opacity={0.9}
        />
      </mesh>
    </Float>
  )
}

export default function TrinityInteractive() {
  const [activeNodes, setActiveNodes] = useState<string[]>([])
  const [rotation, setRotation] = useState(0)

  const nodes = [
    {
      id: 'identity',
      position: [0, 3, 0] as [number, number, number],
      color: '#6b46c1',
      label: 'Identity',
      icon: Atom,
      description: 'Authentic consciousness preservation'
    },
    {
      id: 'consciousness',
      position: [-2.6, -1.5, 0] as [number, number, number],
      color: '#0ea5e9',
      label: 'Consciousness',
      icon: Brain,
      description: 'Distributed awareness & processing'
    },
    {
      id: 'guardian',
      position: [2.6, -1.5, 0] as [number, number, number],
      color: '#10b981',
      label: 'Guardian',
      icon: Shield,
      description: 'Ethical safeguards & alignment'
    }
  ]

  const toggleNode = (nodeId: string) => {
    setActiveNodes(prev =>
      prev.includes(nodeId)
        ? prev.filter(id => id !== nodeId)
        : [...prev, nodeId]
    )
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setRotation(prev => prev + 0.01)
    }, 50)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative w-full h-full">
      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        <pointLight position={[-10, -10, -10]} intensity={0.3} />

        {/* Background particles */}
        <ParticleField />

        {/* Central core */}
        <CentralCore activeNodes={activeNodes} />

        {/* Trinity nodes */}
        {nodes.map((node) => (
          <TrinityNode
            key={node.id}
            position={node.position}
            color={node.color}
            label={node.label}
            icon={node.icon}
            isActive={activeNodes.includes(node.id)}
            onClick={() => toggleNode(node.id)}
          />
        ))}

        {/* Connection beams */}
        {activeNodes.length >= 2 && (
          <>
            {nodes.map((node1, i) =>
              nodes.slice(i + 1).map((node2) => {
                if (activeNodes.includes(node1.id) && activeNodes.includes(node2.id)) {
                  return (
                    <ConnectionBeam
                      key={`${node1.id}-${node2.id}`}
                      start={node1.position}
                      end={node2.position}
                      color="#ffffff"
                      intensity={0.5}
                    />
                  )
                }
                return null
              })
            )}
          </>
        )}

        <OrbitControls
          enablePan={false}
          enableZoom={false}
          autoRotate
          autoRotateSpeed={0.5}
          maxPolarAngle={Math.PI / 2}
          minPolarAngle={Math.PI / 3}
        />
      </Canvas>

      {/* UI Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Node Labels */}
        {nodes.map((node) => {
          const Icon = node.icon
          return (
            <motion.div
              key={node.id}
              className="absolute pointer-events-auto cursor-pointer"
              style={{
                left: '50%',
                top: '50%',
                transform: `translate(-50%, -50%) translate(${node.position[0] * 40}px, ${-node.position[1] * 40}px)`
              }}
              whileHover={{ scale: 1.1 }}
              onClick={() => toggleNode(node.id)}
            >
              <div className={`
                p-3 rounded-xl backdrop-blur-xl border transition-all
                ${activeNodes.includes(node.id)
                  ? 'bg-white/20 border-white/40 shadow-lg'
                  : 'bg-black/40 border-white/20 hover:bg-white/10'}
              `}>
                <div className="flex items-center gap-2">
                  <Icon className="w-5 h-5" style={{ color: node.color }} />
                  <span className="text-sm font-medium text-white">
                    {node.label}
                  </span>
                </div>
                <AnimatePresence>
                  {activeNodes.includes(node.id) && (
                    <motion.p
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="text-xs text-white/70 mt-1 overflow-hidden"
                    >
                      {node.description}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )
        })}

        {/* Status Display */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="px-4 py-2 bg-black/60 backdrop-blur-xl border border-white/20 rounded-full"
          >
            <div className="flex items-center gap-3">
              <div className="flex gap-2">
                {nodes.map((node) => (
                  <div
                    key={node.id}
                    className={`w-2 h-2 rounded-full transition-all ${
                      activeNodes.includes(node.id) ? 'scale-125' : 'scale-75 opacity-40'
                    }`}
                    style={{ backgroundColor: node.color }}
                  />
                ))}
              </div>
              <span className="text-xs text-white/60 font-medium tracking-wider uppercase">
                {activeNodes.length === 0 && 'Select nodes to activate'}
                {activeNodes.length === 1 && `${activeNodes[0]} active`}
                {activeNodes.length === 2 && 'Dual synergy active'}
                {activeNodes.length === 3 && 'Full trinity synergy'}
              </span>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
