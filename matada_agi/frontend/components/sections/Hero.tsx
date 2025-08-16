'use client'

import { motion } from 'framer-motion'
import { Atom, Brain, Shield } from 'lucide-react'
import HeroCanvas from './HeroCanvas'
import ClientOnly from '../ClientOnly'

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20">
      {/* 3D Background with error boundary and fallback */}
      <div className="absolute inset-0 -z-10">
        <ClientOnly fallback={
          <div className="absolute inset-0 bg-gradient-to-br from-trinity-identity/10 to-trinity-consciousness/10" />
        }>
          <HeroCanvas />
        </ClientOnly>
      </div>

      {/* Content */}
      <div className="w-full max-w-7xl mx-auto px-6 relative z-10">
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
              <div className="trinity-identity-glow rounded-full p-4 flex justify-center mb-2">
                <Atom className="w-10 h-10 text-white" />
              </div>
              <p className="font-regular text-xs tracking-[0.2em] uppercase">IDENTITY</p>
            </div>
            <div className="text-center">
              <div className="trinity-consciousness-glow rounded-full p-4 flex justify-center mb-2">
                <Brain className="w-10 h-10 text-white" />
              </div>
              <p className="font-regular text-xs tracking-[0.2em] uppercase">CONSCIOUSNESS</p>
            </div>
            <div className="text-center">
              <div className="trinity-guardian-glow rounded-full p-4 flex justify-center mb-2">
                <Shield className="w-10 h-10 text-white" />
              </div>
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
            <a href="#trinity">
              <button className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular text-sm tracking-[0.2em] uppercase hover:opacity-90 transition-opacity rounded-lg">
                EXPLORE MATADA
              </button>
            </a>
            <a href="/docs">
              <button className="px-8 py-4 border border-primary-light/30 font-regular text-sm tracking-[0.2em] uppercase hover:bg-primary-light hover:text-primary-dark transition-all rounded-lg">
                VIEW DOCUMENTATION
              </button>
            </a>
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