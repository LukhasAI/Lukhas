'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

interface LayerContent {
  title: string
  icon: string
  description: string
  components: string[]
  capabilities: string[]
  features: string[]
}

export function TechnologyStack() {
  const [selectedLayer, setSelectedLayer] = useState<number | null>(null)

  const layers: LayerContent[] = [
    {
      title: 'Consciousness Layer',
      icon: '🧠',
      description: 'Advanced awareness systems that enable dynamic decision-making, contextual understanding, and self-reflective processing through bio-inspired neural architectures and quantum-inspired attention mechanisms.',
      components: [
        'Awareness Engine with attention monitoring',
        'Dream States with parallel reality simulation',
        'Reasoning Hub with symbolic logic processing',
        'Creative Expression Engine',
        'Meta-Cognitive Reflection Systems'
      ],
      capabilities: [
        'Dynamic attention allocation across multiple cognitive tasks',
        'Self-reflective introspection with meta-learning adaptation',
        'Contextual awareness with cross-modal sensor fusion',
        'Dream-state innovation through controlled chaos generation',
        'Real-time consciousness state monitoring and adjustment'
      ],
      features: [
        'Quantum-inspired attention mechanisms for parallel processing',
        'Bio-adaptive neural oscillators for natural thought patterns',
        'Dream engine integration with memory fold systems',
        'Symbolic reasoning with causal chain preservation'
      ]
    },
    {
      title: 'Identity Layer',
      icon: '⚛️',
      description: 'Sophisticated identity management combining ΛiD (Lambda Identity) systems with tiered access control, biometric fusion, and symbolic self-representation for authentic digital presence.',
      components: [
        'ΛiD Core with entropy-based generation',
        'Biometric Fusion Engine',
        'Tiered Access Control System',
        'Symbolic Self-Representation',
        'Cross-Device Identity Synchronization'
      ],
      capabilities: [
        'Multi-factor identity verification with biometric integration',
        'Dynamic tier-based permissions with context awareness',
        'Cross-platform identity synchronization and portability',
        'Privacy-preserving authentication with zero-knowledge proofs',
        'Real-time identity drift detection and correction'
      ],
      features: [
        'Quantum-inspired entropy generation for secure identity tokens',
        'Bio-adaptive authentication that learns user patterns',
        'Symbolic identity mapping with GLYPH integration',
        'Federated identity management across ecosystem'
      ]
    },
    {
      title: 'Guardian Layer',
      icon: '🛡️',
      description: 'Comprehensive ethical oversight and safety systems with constitutional AI principles, drift detection, and real-time compliance monitoring to ensure responsible AI behavior.',
      components: [
        'Ethics Engine with constitutional AI framework',
        'Drift Detection System (0.15 threshold)',
        'Compliance Monitor with real-time validation',
        'Safety Guardrails and circuit breakers',
        'Audit Trail with transparency logging'
      ],
      capabilities: [
        'Real-time ethical decision validation with sub-millisecond response',
        'Predictive drift detection before harmful behaviors emerge',
        'Multi-tier compliance monitoring across regulatory frameworks',
        'Automated safety intervention with graceful degradation',
        'Comprehensive audit logging with causal chain tracking'
      ],
      features: [
        'Quantum-inspired consensus mechanisms for ethical decisions',
        'Bio-adaptive safety responses that evolve with system behavior',
        'Constitutional AI with transparent decision explainability',
        'Guardian System v1.0.0 with 280+ integrated safety modules'
      ]
    },
    {
      title: 'Infrastructure',
      icon: '🔧',
      description: 'Robust foundational systems including GLYPH symbolic communication, actor-based processing, fault-tolerant orchestration, and scalable service architecture supporting the entire LUKHAS ecosystem.',
      components: [
        'GLYPH Engine for symbolic communication',
        'Actor Model with supervision trees',
        'Kernel Bus for event routing',
        'Service Registry with discovery',
        'Distributed Tracing and Observability'
      ],
      capabilities: [
        'Horizontal scaling with automatic load distribution',
        'Fault-tolerant processing with self-healing mechanisms',
        'Cross-module communication through symbolic protocols',
        'Real-time system health monitoring and optimization',
        'Multi-cloud deployment with edge computing support'
      ],
      features: [
        'Quantum-inspired symbolic token exchange for efficient communication',
        'Bio-adaptive resource allocation mimicking biological systems',
        'Actor supervision with automatic recovery and restart',
        'Event-driven architecture with eventual consistency'
      ]
    }
  ]

  return (
    <section id="technology" className="relative py-32 px-6">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <p className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            TECHNOLOGY STACK
          </p>
          <h2 className="font-light text-display mb-6">
            Quantum-Inspired & Bio-Adaptive
          </h2>
          <p className="text-lg text-white/80 max-w-4xl mx-auto">
            LUKHAS AI's Trinity Framework integrates cutting-edge technologies across four foundational layers, 
            each designed with quantum-inspired algorithms and bio-adaptive principles to create a truly 
            revolutionary AI system that thinks, learns, and evolves naturally.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {layers.map((layer, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className={`glass rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:scale-105 ${
                selectedLayer === i ? 'ring-2 ring-trinity-consciousness' : ''
              }`}
              onClick={() => setSelectedLayer(selectedLayer === i ? null : i)}
            >
              <div className="text-3xl mb-4">{layer.icon}</div>
              <h3 className="font-regular text-sm uppercase tracking-wider mb-2">{layer.title}</h3>
              <p className="text-white/60 text-sm">
                Click to explore this layer's capabilities and architecture
              </p>
            </motion.div>
          ))}
        </div>

        {selectedLayer !== null && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="glass rounded-2xl p-8"
          >
            <div className="flex items-center gap-4 mb-6">
              <span className="text-4xl">{layers[selectedLayer].icon}</span>
              <h3 className="text-2xl font-light">{layers[selectedLayer].title}</h3>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <h4 className="text-lg font-regular mb-4 text-trinity-consciousness">System Overview</h4>
                <p className="text-white/80 mb-6 leading-relaxed">
                  {layers[selectedLayer].description}
                </p>

                <h4 className="text-lg font-regular mb-4 text-trinity-consciousness">Core Components</h4>
                <ul className="space-y-2 mb-6">
                  {layers[selectedLayer].components.map((component, idx) => (
                    <li key={idx} className="text-white/80 flex items-start">
                      <span className="text-trinity-consciousness mr-2">•</span>
                      {component}
                    </li>
                  ))}
                </ul>

                <h4 className="text-lg font-regular mb-4 text-trinity-consciousness">Technical Capabilities</h4>
                <ul className="space-y-2">
                  {layers[selectedLayer].capabilities.map((capability, idx) => (
                    <li key={idx} className="text-white/80 flex items-start">
                      <span className="text-trinity-consciousness mr-2">→</span>
                      {capability}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-lg font-regular mb-4 text-trinity-consciousness">Advanced Features</h4>
                <div className="space-y-4">
                  {layers[selectedLayer].features.map((feature, idx) => (
                    <div key={idx} className="p-4 bg-white/5 rounded-lg">
                      <p className="text-white/80 text-sm">{feature}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-16 text-center"
        >
          <h3 className="text-xl font-light mb-4">Integration Excellence</h3>
          <p className="text-white/80 max-w-3xl mx-auto">
            These layers work in perfect harmony through the Trinity Framework, with GLYPH-based symbolic 
            communication ensuring seamless integration while maintaining each layer's specialized function. 
            The result is an AI system that combines the best of quantum-inspired processing with 
            bio-adaptive intelligence.
          </p>
        </motion.div>
      </div>
    </section>
  )
}