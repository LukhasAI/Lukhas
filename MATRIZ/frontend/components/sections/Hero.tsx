'use client'

import { motion } from 'framer-motion'
import { Atom, Brain, Shield } from 'lucide-react'
import HeroCanvas from './HeroCanvas'
import ClientOnly from '../ClientOnly'

interface HeroProps {
  title: string;
  description: string;
}

export default function Hero({ title, description }: HeroProps) {
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
          {/* Architecture Tagline - Larger and more prominent */}
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="font-regular text-base md:text-lg tracking-[0.25em] uppercase text-trinity-consciousness mb-8 opacity-90"
          >
            MODULAR ADAPTIVE TEMPORAL ATTENTION DYNAMIC ARCHITECTURE
          </motion.p>

          {/* Main Title - MATADA */}
          <motion.h1
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="font-ultralight text-8xl md:text-9xl lg:text-[12rem] mb-8 leading-none"
          >
            <span className="gradient-text tracking-wide">{title}</span>
          </motion.h1>

          {/* Consciousness Manifesto - Poetic Layer */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="font-thin text-xl md:text-2xl lg:text-3xl mb-12 mx-auto text-center leading-relaxed"
            style={{ maxWidth: 'fit-content' }}
          >
            {description}
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

          {/* Call to Action - Lighter blue gradient */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0 }}
            className="flex flex-col sm:flex-row gap-6 justify-center"
          >
            <a href="#trinity">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(59, 130, 246, 0.3)" }}
                whileTap={{ scale: 0.98 }}
                className="px-10 py-4 bg-gradient-to-r from-blue-400 to-blue-600 text-white font-regular text-sm tracking-[0.2em] uppercase rounded-lg shadow-lg hover:shadow-xl transition-all duration-300"
              >
                EXPLORE TRINITY
              </motion.button>
            </a>
            <a href="/docs">
              <motion.button
                whileHover={{ scale: 1.05, borderColor: "rgba(59, 130, 246, 0.8)" }}
                whileTap={{ scale: 0.98 }}
                className="px-10 py-4 border-2 border-white/30 font-regular text-sm tracking-[0.2em] uppercase hover:bg-white hover:text-black transition-all duration-300 rounded-lg"
              >
                VIEW DOCUMENTATION
              </motion.button>
            </a>
          </motion.div>
        </motion.div>

      </div>
    </section>
  )
}
