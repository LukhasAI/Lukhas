'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'

export default function WhatIsMatada() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  const features = [
    {
      icon: '🧬',
      title: 'COGNITIVE DNA',
      description: 'Every thought and decision becomes a permanent, traceable node in the system\'s cognitive history'
    },
    {
      icon: '🔄',
      title: 'EVOLUTIONARY ARCHITECTURE',
      description: 'Nodes evolve and adapt based on outcomes, creating a self-improving cognitive system'
    },
    {
      icon: '🎯',
      title: 'DETERMINISTIC REASONING',
      description: 'Each decision follows a clear, auditable path through the cognitive node network'
    },
    {
      icon: '⚡',
      title: 'QUANTUM-INSPIRED PROCESSING',
      description: 'Leverages superposition principles for parallel cognitive exploration'
    }
  ]

  return (
    <section id="what" className="relative py-32 px-6" ref={ref}>
      <div className="container mx-auto max-w-6xl">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            WHAT IS MATADA
          </h2>
          <p className="font-thin text-4xl max-w-3xl mx-auto">
            A revolutionary cognitive architecture where consciousness emerges from interconnected, evolving nodes
          </p>
        </motion.div>

        {/* Core Concept */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="glass-panel p-12 rounded-2xl mb-16"
        >
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-6">
                COGNITIVE ARCHITECTURE REIMAGINED
              </h3>
              <p className="font-thin text-lg leading-relaxed mb-6">
                MATADA transforms artificial intelligence by treating every computational moment as a 
                permanent node in an ever-growing cognitive graph. Unlike traditional AI that processes 
                and discards, MATADA remembers, learns, and evolves.
              </p>
              <p className="font-thin text-lg leading-relaxed">
                Each node contains not just data, but context, confidence, emotional valence, and 
                causal relationships - creating a true cognitive DNA that can be traced, audited, 
                and understood.
              </p>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-trinity-identity/20 to-trinity-consciousness/20 p-8">
                <pre className="font-mono text-sm text-primary-light/80 overflow-auto">
{`{
  "id": "node_2025_001",
  "type": "DECISION",
  "state": {
    "confidence": 0.92,
    "valence": 0.7,
    "arousal": 0.3,
    "salience": 0.85
  },
  "links": ["node_2025_000"],
  "evolvesTo": "node_2025_002",
  "triggers": ["REFLECTION"],
  "reflections": {
    "outcome": "successful",
    "learnings": "pattern_recognized"
  }
}`}
                </pre>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className="glass-panel p-8 rounded-xl hover-lift"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-3">
                {feature.title}
              </h4>
              <p className="font-thin text-sm leading-relaxed text-primary-light/80">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}