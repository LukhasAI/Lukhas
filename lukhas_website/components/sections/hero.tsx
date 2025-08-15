'use client'

import { useRef, useEffect, useState } from 'react'
import { motion, useAnimation, AnimatePresence } from 'framer-motion'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Sphere, MeshDistortMaterial, Float } from '@react-three/drei'
import { ChevronDown, Atom, Brain, Shield } from 'lucide-react'
import SplitType from 'split-type'
import { gsap } from 'gsap'

const taglines = [
  'Building Consciousness You Can Trust',
  'Where AI Meets Ethics',
  'Trinity Framework: Identity • Consciousness • Guardian',
  'Powered by MATADA',
]

function AnimatedSphere() {
  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere args={[1, 100, 200]} scale={2.5}>
        <MeshDistortMaterial
          color="#6B46C1"
          attach="material"
          distort={0.4}
          speed={2}
          roughness={0}
          metalness={0.1}
        />
      </Sphere>
    </Float>
  )
}

export function Hero() {
  const titleRef = useRef<HTMLHeadingElement>(null)
  const [currentTagline, setCurrentTagline] = useState(0)
  const controls = useAnimation()

  // Typewriter effect for taglines
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTagline((prev) => (prev + 1) % taglines.length)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  // Split text animation
  useEffect(() => {
    if (titleRef.current) {
      const split = new SplitType(titleRef.current, {
        types: 'chars',
        tagName: 'span',
      })

      gsap.from(split.chars, {
        opacity: 0,
        y: 50,
        rotateX: -90,
        stagger: 0.02,
        duration: 1,
        ease: 'power4.out',
      })

      return () => {
        split.revert()
      }
    }
  }, [])

  const scrollToContent = () => {
    window.scrollTo({
      top: window.innerHeight,
      behavior: 'smooth',
    })
  }

  return (
    <section className="hero-section relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* 3D Background */}
      <div className="hero-bg absolute inset-0 -z-10">
        <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <AnimatedSphere />
          <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </div>

      {/* Gradient Mesh Overlay */}
      <div className="absolute inset-0 -z-5">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-bg-primary/50 to-bg-primary" />
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
          className="text-center"
        >
          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="font-regular text-xs md:text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8"
          >
            LOGICAL UNIFIED KNOWLEDGE HYPER-ADAPTIVE SUPERIOR SYSTEMS
          </motion.p>

          {/* Main Title */}
          <h1
            ref={titleRef}
            className="font-ultralight text-hero uppercase mb-8 leading-none"
          >
            LUKHAS
          </h1>

          {/* Animated Tagline */}
          <div className="h-16 mb-12 flex items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={currentTagline}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="font-light text-xl md:text-3xl text-text-secondary"
              >
                {taglines[currentTagline]}
              </motion.p>
            </AnimatePresence>
          </div>

          {/* Trinity Symbols */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="flex justify-center space-x-8 md:space-x-16 mb-12"
          >
            <TrinitySymbol
              icon={Atom}
              label="IDENTITY"
              color="trinity-identity"
              delay={0.7}
            />
            <TrinitySymbol
              icon={Brain}
              label="CONSCIOUSNESS"
              color="trinity-consciousness"
              delay={0.8}
            />
            <TrinitySymbol
              icon={Shield}
              label="GUARDIAN"
              color="trinity-guardian"
              delay={0.9}
            />
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-bg-primary font-regular text-sm tracking-[0.2em] uppercase hover:opacity-90 transition-opacity"
            >
              EXPLORE MATADA
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 border border-glass-border hover:bg-glass font-regular text-sm tracking-[0.2em] uppercase transition-all"
            >
              VIEW PRODUCTS
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.button
          onClick={scrollToContent}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 group"
          aria-label="Scroll to content"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="flex flex-col items-center space-y-2"
          >
            <span className="text-text-tertiary text-xs uppercase tracking-widest">Scroll</span>
            <div className="w-6 h-10 border-2 border-glass-border rounded-full flex justify-center group-hover:border-trinity-consciousness transition-colors">
              <motion.div
                animate={{ y: [0, 15, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-1 h-3 bg-text-secondary rounded-full mt-2"
              />
            </div>
          </motion.div>
        </motion.button>
      </div>
    </section>
  )
}

function TrinitySymbol({
  icon: Icon,
  label,
  color,
  delay,
}: {
  icon: any
  label: string
  color: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.5, type: 'spring' }}
      className="text-center group cursor-pointer"
    >
      <motion.div
        whileHover={{ scale: 1.1, rotate: 360 }}
        transition={{ duration: 0.5 }}
        className={`mb-3 inline-block p-4 rounded-full bg-${color}/10 group-hover:glow-${color.split('-')[1]}`}
      >
        <Icon className="w-12 h-12 md:w-16 md:h-16 text-white" />
      </motion.div>
      <p className="font-regular text-xs tracking-[0.2em] uppercase text-text-tertiary group-hover:text-text-primary transition-colors">
        {label}
      </p>
    </motion.div>
  )
}