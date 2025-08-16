'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState, Suspense } from 'react'
import dynamic from 'next/dynamic'

// Dynamic import with no SSR for Canvas components
const TrinityCanvas = dynamic(() => import('./TrinityCanvas'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-trinity-identity/10 via-trinity-consciousness/10 to-trinity-guardian/10">
      <span className="text-sm text-neutral-gray">Loading 3D visualization...</span>
    </div>
  )
})

export default function Trinity() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const [activeTab, setActiveTab] = useState<'identity' | 'consciousness' | 'guardian'>('identity')

  const trinityData = {
    identity: {
      icon: 'Atom',
      emoji: '⚛️',
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
      emoji: '🧠',
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
      emoji: '🛡️',
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
          <Suspense fallback={
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-trinity-identity/10 via-trinity-consciousness/10 to-trinity-guardian/10">
              <span className="text-sm text-neutral-gray">Loading 3D visualization...</span>
            </div>
          }>
            <TrinityCanvas />
          </Suspense>
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
                  onClick={() => setActiveTab(key as 'identity' | 'consciousness' | 'guardian')}
                  className={`px-8 py-3 rounded-full font-regular text-sm tracking-[0.2em] uppercase transition-all ${
                    activeTab === key 
                      ? `bg-${data.color} text-primary-dark` 
                      : 'hover:bg-white/10'
                  }`}
                >
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