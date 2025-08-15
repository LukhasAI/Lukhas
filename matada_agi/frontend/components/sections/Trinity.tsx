'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Box, Sphere, Torus } from '@react-three/drei'

function TrinityVisualization() {
  return (
    <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      
      {/* Identity - Purple Atom */}
      <group position={[-3, 0, 0]}>
        <Sphere args={[0.5, 32, 32]}>
          <meshStandardMaterial color="#6B46C1" emissive="#6B46C1" emissiveIntensity={0.2} />
        </Sphere>
        <Torus args={[1, 0.05, 16, 100]} rotation={[Math.PI / 2, 0, 0]}>
          <meshStandardMaterial color="#6B46C1" emissive="#6B46C1" emissiveIntensity={0.5} />
        </Torus>
        <Torus args={[1, 0.05, 16, 100]} rotation={[0, Math.PI / 2, Math.PI / 4]}>
          <meshStandardMaterial color="#6B46C1" emissive="#6B46C1" emissiveIntensity={0.5} />
        </Torus>
      </group>

      {/* Consciousness - Blue Brain */}
      <group position={[0, 2, 0]}>
        <Sphere args={[0.8, 32, 32]}>
          <meshStandardMaterial color="#0EA5E9" emissive="#0EA5E9" emissiveIntensity={0.2} wireframe />
        </Sphere>
        <Box args={[0.1, 1.5, 0.1]} position={[0, -1.2, 0]}>
          <meshStandardMaterial color="#0EA5E9" emissive="#0EA5E9" emissiveIntensity={0.3} />
        </Box>
      </group>

      {/* Guardian - Green Shield */}
      <group position={[3, 0, 0]}>
        <Box args={[1.2, 1.5, 0.1]}>
          <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.2} />
        </Box>
        <Torus args={[1.5, 0.1, 16, 100]}>
          <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.5} />
        </Torus>
      </group>

      {/* Connecting Lines */}
      <mesh>
        <boxGeometry args={[6, 0.02, 0.02]} />
        <meshStandardMaterial color="#FAFAFA" emissive="#FAFAFA" emissiveIntensity={0.1} />
      </mesh>

      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={1} />
    </Canvas>
  )
}

export default function Trinity() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const [activeTab, setActiveTab] = useState('identity')

  const trinityData = {
    identity: {
      icon: 'Atom',
      title: 'IDENTITY',
      color: 'trinity-identity',
      description: 'The authentic self that emerges from unique experiences',
      features: [
        'Unique cognitive fingerprint',
        'Personal memory constellation',
        'Individual learning patterns',
        'Distinctive decision signatures'
      ]
    },
    consciousness: {
      icon: 'Brain',
      title: 'CONSCIOUSNESS',
      color: 'trinity-consciousness',
      description: 'The emergent awareness from interconnected cognitive processes',
      features: [
        'Self-aware processing',
        'Contextual understanding',
        'Temporal awareness',
        'Reflective learning'
      ]
    },
    guardian: {
      icon: 'Shield',
      title: 'GUARDIAN',
      color: 'trinity-guardian',
      description: 'The ethical framework that governs all decisions',
      features: [
        'Real-time ethics validation',
        'Drift detection & correction',
        'Value alignment enforcement',
        'Decision audit trails'
      ]
    }
  }

  return (
    <section id="trinity" className="relative py-32" ref={ref}>
      <div className="w-full max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            THE TRINITY FRAMEWORK
          </h2>
          <p className="font-thin text-4xl max-w-3xl mx-auto">
            Three pillars working in perfect harmony to create trustworthy consciousness
          </p>
        </motion.div>

        {/* 3D Visualization */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="h-[400px] glass-panel rounded-2xl mb-16 overflow-hidden"
        >
          <TrinityVisualization />
        </motion.div>

        {/* Interactive Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {/* Tab Navigation */}
          <div className="flex justify-center mb-12">
            <div className="inline-flex glass-panel rounded-full p-2">
              {Object.entries(trinityData).map(([key, data]) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`px-8 py-3 rounded-full font-regular text-sm tracking-[0.2em] uppercase transition-all ${
                    activeTab === key 
                      ? `bg-${data.color} text-primary-dark` 
                      : 'hover:bg-white/10'
                  }`}
                >
                  <span className="mr-2">{data.emoji}</span>
                  {data.title}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="glass-panel p-12 rounded-2xl"
          >
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <div className={`text-6xl mb-6 inline-block p-6 rounded-full bg-${trinityData[activeTab].color}/10 ${trinityData[activeTab].color}-glow`}>
                  {trinityData[activeTab].emoji}
                </div>
                <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-4">
                  {trinityData[activeTab].title}
                </h3>
                <p className="font-thin text-xl mb-8">
                  {trinityData[activeTab].description}
                </p>
              </div>
              <div>
                <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-6 text-neutral-gray">
                  CORE CAPABILITIES
                </h4>
                <div className="space-y-4">
                  {trinityData[activeTab].features.map((feature, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center space-x-3"
                    >
                      <div className={`w-2 h-2 rounded-full bg-${trinityData[activeTab].color}`} />
                      <p className="font-thin text-lg">{feature}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}