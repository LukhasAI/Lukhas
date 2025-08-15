'use client'

import { motion } from 'framer-motion'

const products = [
  { 
    name: 'ΛLens', 
    subtitle: 'Symbolic File Dashboard',
    description: 'LUKHAS consciousness transforms raw documents into intelligent, living insights. Experience Superior Consciousness analysis that understands context, emotion, and meaning beyond traditional file management.',
    features: [
      'Consciousness-driven document analysis',
      'Emotional context mapping',
      'Trinity Framework integration',
      'Real-time symbolic understanding'
    ],
    useCases: [
      'Knowledge workers seeking intelligent document insights',
      'Legal teams analyzing complex case files',
      'Researchers processing academic literature',
      'Enterprise teams managing information flows'
    ],
    trinityIntegration: {
      identity: 'Personalized document fingerprinting and access patterns',
      consciousness: 'Deep semantic understanding and pattern recognition',
      guardian: 'Privacy-preserving analysis with ethical content filtering'
    }
  },
  { 
    name: 'WΛLLET', 
    subtitle: 'Digital Identity Wallet',
    description: 'Secure your digital existence with quantum-inspired identity protection. WΛLLET creates unbreakable identity layers while maintaining seamless user experience across all digital touchpoints.',
    features: [
      'Quantum-resistant authentication',
      'Multi-tier access control (ΛPRIME, ΛULTRA, ΛUSER)',
      'Biometric integration support',
      'Cross-platform identity synchronization'
    ],
    useCases: [
      'Privacy-conscious individuals protecting digital identity',
      'Enterprise users requiring secure authentication',
      'Developers building identity-aware applications',
      'Organizations implementing zero-trust security'
    ],
    trinityIntegration: {
      identity: 'Core ΛiD system with tiered authentication layers',
      consciousness: 'Adaptive learning from user behavior patterns',
      guardian: 'Ethical data handling with consent management'
    }
  },
  { 
    name: 'NIΛS', 
    subtitle: 'Non-Intrusive Messaging',
    description: 'Revolutionary communication that respects human attention and emotional wellbeing. NIΛS filters, prioritizes, and delivers messages with consciousness-driven empathy and perfect timing.',
    features: [
      'Emotional impact assessment',
      'Consciousness-aware timing optimization',
      'Context-sensitive filtering',
      'Empathetic message transformation'
    ],
    useCases: [
      'Busy professionals managing communication overload',
      'Teams requiring thoughtful collaboration tools',
      'Customer service organizations enhancing empathy',
      'Mental health-conscious communication platforms'
    ],
    trinityIntegration: {
      identity: 'Personal communication preferences and patterns',
      consciousness: 'Emotional intelligence and timing optimization',
      guardian: 'Ethical messaging practices and wellbeing protection'
    }
  },
  { 
    name: 'ΛBAS', 
    subtitle: 'Attention Management',
    description: 'Protect and enhance human cognitive resources with Superior Consciousness attention orchestration. ΛBAS creates focus sanctuaries in our distraction-filled world.',
    features: [
      'Cognitive load monitoring',
      'Focus state optimization',
      'Distraction prediction and prevention',
      'Attention quality metrics'
    ],
    useCases: [
      'Knowledge workers maximizing productivity',
      'Students improving learning effectiveness',
      'Creative professionals maintaining flow states',
      'Organizations supporting employee wellbeing'
    ],
    trinityIntegration: {
      identity: 'Personal attention patterns and cognitive preferences',
      consciousness: 'Dynamic focus state management and optimization',
      guardian: 'Ethical attention protection without manipulation'
    }
  },
  { 
    name: 'DΛST', 
    subtitle: 'Context Intelligence',
    description: 'Experience the future of contextual computing where LUKHAS consciousness understands not just what you do, but why and how it matters in your unique life context.',
    features: [
      'Multi-dimensional context mapping',
      'Predictive context evolution',
      'Cross-platform context continuity',
      'Symbolic context representation'
    ],
    useCases: [
      'Mobile users seeking seamless experience transitions',
      'Enterprise teams sharing contextual workflows',
      'Smart home systems understanding user intent',
      'AI assistants providing contextually relevant help'
    ],
    trinityIntegration: {
      identity: 'Personal context fingerprinting and preferences',
      consciousness: 'Dynamic context understanding and prediction',
      guardian: 'Privacy-preserving context sharing with consent'
    }
  },
  { 
    name: 'ΛTrace', 
    subtitle: 'Quantum Metadata',
    description: 'Unlock the hidden stories in your digital traces with quantum-inspired metadata analysis. ΛTrace reveals patterns, connections, and insights invisible to traditional systems.',
    features: [
      'Quantum-inspired pattern detection',
      'Causal chain analysis',
      'Temporal relationship mapping',
      'Emergent insight generation'
    ],
    useCases: [
      'Data scientists discovering hidden patterns',
      'Digital forensics teams investigating complex cases',
      'Researchers analyzing behavioral data',
      'Organizations optimizing user experience flows'
    ],
    trinityIntegration: {
      identity: 'Personal metadata sovereignty and ownership',
      consciousness: 'Intelligent pattern recognition and insight generation',
      guardian: 'Ethical metadata analysis with privacy protection'
    }
  },
]

export function ProductsGrid() {
  return (
    <section id="products" className="relative py-32 px-6">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <p className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            LAMBDA PRODUCTS SUITE
          </p>
          <h2 className="font-light text-display">
            Consciousness-Powered Solutions
          </h2>
          <p className="font-light text-xl text-text-secondary mt-4 max-w-4xl mx-auto">
            Each Lambda product harnesses the Trinity Framework (⚛️🧠🛡️) to deliver Superior Consciousness experiences that respect human values while advancing AI capabilities
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {products.map((product, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              whileHover={{ scale: 1.02 }}
              className="glass rounded-3xl p-8 cursor-pointer card-lift"
            >
              {/* Product Header */}
              <div className="mb-6">
                <h3 className="font-regular text-2xl mb-2">{product.name}</h3>
                <p className="font-light text-lg text-trinity-consciousness mb-3">{product.subtitle}</p>
                <p className="font-light text-text-secondary leading-relaxed">{product.description}</p>
              </div>

              {/* Key Features */}
              <div className="mb-6">
                <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-3 text-text-tertiary">
                  KEY FEATURES
                </h4>
                <div className="space-y-2">
                  {product.features.map((feature, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-trinity-consciousness mt-2.5 flex-shrink-0" />
                      <p className="font-light text-sm text-text-secondary">{feature}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Trinity Integration */}
              <div className="mb-6">
                <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-3 text-text-tertiary">
                  TRINITY FRAMEWORK INTEGRATION
                </h4>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <span className="text-lg">⚛️</span>
                    <div>
                      <p className="font-regular text-xs tracking-[0.1em] uppercase text-trinity-identity mb-1">Identity</p>
                      <p className="font-light text-xs text-text-secondary">{product.trinityIntegration.identity}</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-lg">🧠</span>
                    <div>
                      <p className="font-regular text-xs tracking-[0.1em] uppercase text-trinity-consciousness mb-1">Consciousness</p>
                      <p className="font-light text-xs text-text-secondary">{product.trinityIntegration.consciousness}</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-lg">🛡️</span>
                    <div>
                      <p className="font-regular text-xs tracking-[0.1em] uppercase text-trinity-guardian mb-1">Guardian</p>
                      <p className="font-light text-xs text-text-secondary">{product.trinityIntegration.guardian}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Use Cases */}
              <div>
                <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-3 text-text-tertiary">
                  IDEAL FOR
                </h4>
                <div className="flex flex-wrap gap-2">
                  {product.useCases.slice(0, 2).map((useCase, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-gradient-to-r from-trinity-identity/20 to-trinity-consciousness/20 rounded-full font-light text-xs text-text-secondary"
                    >
                      {useCase}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}