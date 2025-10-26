'use client'

import { useT } from '@/lib/i18n'
import { Float, MeshDistortMaterial, OrbitControls, Sphere } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { AnimatePresence, motion, useAnimation } from 'framer-motion'
import { gsap } from 'gsap'
import { Atom, BookOpen, Brain, Layers3, Shield, Sparkles } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import SplitType from 'split-type'

// 3-Layer Tone System options for hero taglines
type ToneLayer = 'poetic' | 'userFriendly' | 'academic'

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
  const [toneLayer, setToneLayer] = useState<ToneLayer>('poetic')
  const controls = useAnimation()
  const { t } = useT()
  
  // Dynamic taglines based on tone layer
  const getTagline = () => {
    switch(toneLayer) {
      case 'poetic':
        return t('hero.poetic')
      case 'userFriendly':
        return t('hero.userFriendly')
      case 'academic':
        return t('hero.academic')
      default:
        return t('hero.title')
    }
  }

  // Cycle through tone layers
  useEffect(() => {
    const layers: ToneLayer[] = ['poetic', 'userFriendly', 'academic']
    let currentIndex = 0
    
    const interval = setInterval(() => {
      currentIndex = (currentIndex + 1) % layers.length
      setToneLayer(layers[currentIndex])
    }, 5000)

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
            {t('hero.subtitle')}
          </motion.p>

          {/* Main Title */}
          <h1
            ref={titleRef}
            className="font-ultralight text-hero uppercase mb-8 leading-none"
          >
            LUKHAS
          </h1>

          {/* Animated Tagline with 3-Layer Tone System */}
          <div className="mb-12">
            {/* Tone Layer Indicator */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="flex justify-center space-x-4 mb-6"
            >
              <button
                onClick={() => setToneLayer('poetic')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all ${
                  toneLayer === 'poetic' 
                    ? 'bg-trinity-identity/20 text-trinity-identity' 
                    : 'text-text-tertiary hover:text-text-secondary'
                }`}
              >
                <Sparkles className="w-4 h-4" />
                <span className="text-xs uppercase tracking-wider">Poetic</span>
              </button>
              <button
                onClick={() => setToneLayer('userFriendly')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all ${
                  toneLayer === 'userFriendly' 
                    ? 'bg-trinity-consciousness/20 text-trinity-consciousness' 
                    : 'text-text-tertiary hover:text-text-secondary'
                }`}
              >
                <Layers3 className="w-4 h-4" />
                <span className="text-xs uppercase tracking-wider">Friendly</span>
              </button>
              <button
                onClick={() => setToneLayer('academic')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all ${
                  toneLayer === 'academic' 
                    ? 'bg-trinity-guardian/20 text-trinity-guardian' 
                    : 'text-text-tertiary hover:text-text-secondary'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span className="text-xs uppercase tracking-wider">Academic</span>
              </button>
            </motion.div>
            
            {/* Animated Tagline */}
            <div className="min-h-[120px] flex items-center justify-center px-6">
              <AnimatePresence mode="wait">
                <motion.p
                  key={toneLayer}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.5 }}
                  className={`font-light text-lg md:text-2xl lg:text-3xl text-center max-w-5xl ${
                    toneLayer === 'poetic' ? 'text-text-secondary italic' :
                    toneLayer === 'academic' ? 'text-text-primary' :
                    'text-text-secondary'
                  }`}
                >
                  {getTagline()}
                </motion.p>
              </AnimatePresence>
            </div>
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
              {t('hero.cta.explore')}
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 border border-glass-border hover:bg-glass font-regular text-sm tracking-[0.2em] uppercase transition-all"
            >
              {t('hero.cta.documentation')}
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