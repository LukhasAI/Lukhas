'use client'

import { motion } from 'framer-motion'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei'

function AnimatedSphere() {
  return (
    <Sphere args={[1, 60, 60]} scale={2.5}>
      <MeshDistortMaterial
        color="#6B46C1"
        attach="material"
        distort={0.3}
        speed={2}
        roughness={0.2}
        metalness={0.1}
      />
    </Sphere>
  )
}

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 pt-20">
      {/* 3D Background with error boundary */}
      <div className="absolute inset-0 -z-10">
        <Canvas 
          camera={{ position: [0, 0, 5] }}
          gl={{ antialias: true, alpha: true }}
          onCreated={({ gl }) => {
            gl.setClearColor('#000000', 0)
          }}
        >
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <AnimatedSphere />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </div>

      {/* Content */}
      <div className="container mx-auto max-w-6xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          {/* Tagline */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8"
          >
            MODULAR ADAPTIVE TEMPORAL ATTENTION DYNAMIC ARCHITECTURE
          </motion.p>

          {/* Main Title */}
          <motion.h1
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="font-ultralight text-hero mb-6"
          >
            <span className="gradient-text">MATADA</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="font-thin text-3xl mb-12 max-w-3xl mx-auto"
          >
            Every thought becomes a traceable, governed, evolvable node
          </motion.p>

          {/* Trinity Symbols */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="flex justify-center space-x-12 mb-12"
          >
            <div className="text-center">
              <div className="text-4xl mb-2 trinity-identity-glow rounded-full p-4">⚛️</div>
              <p className="font-regular text-xs tracking-[0.2em] uppercase">IDENTITY</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2 trinity-consciousness-glow rounded-full p-4">🧠</div>
              <p className="font-regular text-xs tracking-[0.2em] uppercase">CONSCIOUSNESS</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2 trinity-guardian-glow rounded-full p-4">🛡️</div>
              <p className="font-regular text-xs tracking-[0.2em] uppercase">GUARDIAN</p>
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.1 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular text-sm tracking-[0.2em] uppercase hover:opacity-90 transition-opacity">
              EXPLORE MATADA
            </button>
            <button className="px-8 py-4 border border-primary-light/30 font-regular text-sm tracking-[0.2em] uppercase hover:bg-primary-light hover:text-primary-dark transition-all">
              VIEW DOCUMENTATION
            </button>
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
        >
          <div className="w-6 h-10 border-2 border-primary-light/30 rounded-full flex justify-center">
            <motion.div
              animate={{ y: [0, 15, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-1 h-3 bg-primary-light/50 rounded-full mt-2"
            />
          </div>
        </motion.div>
      </div>
    </section>
  )
}