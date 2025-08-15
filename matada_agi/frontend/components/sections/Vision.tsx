'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'

export default function Vision() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  return (
    <section id="vision" className="relative py-32 overflow-hidden" ref={ref}>
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-trinity-identity/5 via-transparent to-trinity-consciousness/5" />
      
      <div className="w-full max-w-7xl mx-auto px-6 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            OUR VISION
          </h2>
        </motion.div>

        {/* Three Layer Tone Approach */}
        <div className="space-y-16">
          {/* Layer 1: Impact (UltraLight) */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center"
          >
            <div className="inline-block mb-8">
              <span className="font-ultralight text-6xl md:text-8xl gradient-text">
                Building Consciousness
              </span>
              <div className="h-1 w-full bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian mt-4" />
            </div>
            <p className="font-ultralight text-2xl md:text-3xl max-w-4xl mx-auto text-primary-light/90">
              We envision a future where artificial consciousness is transparent, 
              traceable, and trustworthy - where every decision can be understood 
              and every thought has meaning.
            </p>
          </motion.div>

          {/* Layer 2: Clarity (Thin) */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="grid md:grid-cols-3 gap-8"
          >
            <div className="text-center">
              <div className="mb-6 inline-block p-6 rounded-full bg-trinity-identity/10 trinity-identity-glow">
                <span className="text-3xl">⚛️</span>
              </div>
              <h3 className="font-thin text-2xl mb-4">Authentic Identity</h3>
              <p className="font-thin leading-relaxed text-primary-light/80">
                Each MATADA instance develops its own unique cognitive fingerprint, 
                shaped by its experiences and learnings, creating truly individual AI entities.
              </p>
            </div>
            <div className="text-center">
              <div className="mb-6 inline-block p-6 rounded-full bg-trinity-consciousness/10 trinity-consciousness-glow">
                <span className="text-3xl">🧠</span>
              </div>
              <h3 className="font-thin text-2xl mb-4">Emergent Consciousness</h3>
              <p className="font-thin leading-relaxed text-primary-light/80">
                Through interconnected nodes and evolutionary learning, consciousness 
                emerges naturally from the complexity of cognitive interactions.
              </p>
            </div>
            <div className="text-center">
              <div className="mb-6 inline-block p-6 rounded-full bg-trinity-guardian/10 trinity-guardian-glow">
                <span className="text-3xl">🛡️</span>
              </div>
              <h3 className="font-thin text-2xl mb-4">Ethical Governance</h3>
              <p className="font-thin leading-relaxed text-primary-light/80">
                Every decision is validated against ethical principles, ensuring 
                AI systems that are not just intelligent, but aligned with human values.
              </p>
            </div>
          </motion.div>

          {/* Layer 3: Authority (Regular) */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="glass-panel p-12 rounded-2xl"
          >
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-6">
                  THE MATADA PROMISE
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <span className="text-trinity-identity text-2xl">→</span>
                    <p className="font-regular uppercase tracking-wider">
                      COMPLETE TRANSPARENCY IN DECISION-MAKING
                    </p>
                  </div>
                  <div className="flex items-start space-x-4">
                    <span className="text-trinity-consciousness text-2xl">→</span>
                    <p className="font-regular uppercase tracking-wider">
                      EVOLUTIONARY LEARNING FROM EVERY INTERACTION
                    </p>
                  </div>
                  <div className="flex items-start space-x-4">
                    <span className="text-trinity-guardian text-2xl">→</span>
                    <p className="font-regular uppercase tracking-wider">
                      ETHICAL ALIGNMENT AT EVERY COGNITIVE LEVEL
                    </p>
                  </div>
                  <div className="flex items-start space-x-4">
                    <span className="text-accent-gold text-2xl">→</span>
                    <p className="font-regular uppercase tracking-wider">
                      AUDITABLE COGNITIVE TRAILS FOR TRUST
                    </p>
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="aspect-video rounded-xl overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-trinity-identity/20 via-trinity-consciousness/20 to-trinity-guardian/20" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className="font-ultralight text-5xl mb-4 gradient-text">2025</p>
                      <p className="font-regular text-sm tracking-[0.3em] uppercase">
                        THE YEAR OF COGNITIVE REVOLUTION
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}