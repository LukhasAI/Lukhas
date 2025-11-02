'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import TrinityCanvas from './TrinityCanvas'
import ClientOnly from '../ClientOnly'
import { Atom, Brain, Shield, Fingerprint, Eye, ShieldCheck, CheckCircle } from 'lucide-react'

export default function Trinity() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const [activeTab, setActiveTab] = useState<'identity' | 'consciousness' | 'guardian'>('identity')

  const trinityData = {
    identity: {
      Icon: Atom,
      ActiveIcon: Fingerprint,
      title: 'IDENTITY',
      color: 'trinity-identity',
      bgColor: 'bg-purple-600',
      glowColor: 'shadow-purple-600/50',
      textColor: 'text-purple-600',
      borderColor: 'border-purple-600',
      description: 'The authentic self that emerges from unique experiences',
      features: [
        'Unique cognitive fingerprint',
        'Personal memory constellation',
        'Individual learning patterns',
        'Distinctive decision signatures'
      ]
    },
    consciousness: {
      Icon: Brain,
      ActiveIcon: Eye,
      title: 'CONSCIOUSNESS',
      color: 'trinity-consciousness',
      bgColor: 'bg-blue-600',
      glowColor: 'shadow-blue-600/50',
      textColor: 'text-blue-600',
      borderColor: 'border-blue-600',
      description: 'The emergent awareness from interconnected cognitive processes',
      features: [
        'Self-aware processing',
        'Contextual understanding',
        'Temporal awareness',
        'Reflective learning'
      ]
    },
    guardian: {
      Icon: Shield,
      ActiveIcon: ShieldCheck,
      title: 'GUARDIAN',
      color: 'trinity-guardian',
      bgColor: 'bg-green-600',
      glowColor: 'shadow-green-600/50',
      textColor: 'text-green-600',
      borderColor: 'border-green-600',
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

        {/* Three Cards Layout - Better than animation for readability */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {Object.entries(trinityData).map(([key, data], index) => {
            const Icon = data.Icon
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                className={`glass-panel p-8 rounded-2xl border ${data.borderColor}/20 hover:border-${data.borderColor}/40 transition-all hover:shadow-xl ${data.glowColor}`}
              >
                {/* Icon with better visibility */}
                <div className={`inline-flex p-4 rounded-2xl ${data.bgColor}/10 mb-6`}>
                  <Icon className={`w-12 h-12 ${data.textColor}`} strokeWidth={1.5} />
                </div>

                {/* Title with better contrast */}
                <h3 className={`font-regular text-xl tracking-[0.2em] uppercase mb-4 ${data.textColor}`}>
                  {data.title}
                </h3>

                {/* Description */}
                <p className="font-thin text-lg mb-6 text-primary-light/80">
                  {data.description}
                </p>

                {/* Features with check icons */}
                <div className="space-y-3">
                  {data.features.map((feature, idx) => (
                    <div key={idx} className="flex items-start space-x-3">
                      <CheckCircle className={`w-5 h-5 ${data.textColor} mt-0.5 flex-shrink-0`} strokeWidth={1.5} />
                      <p className="font-thin text-sm text-primary-light/70">{feature}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Interactive Canvas Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <div className="glass-panel rounded-2xl p-8">
            <h3 className="font-regular text-lg tracking-[0.2em] uppercase text-center mb-6 text-neutral-gray">
              INTERACTIVE VISUALIZATION
            </h3>
            <div className="h-[400px] rounded-xl overflow-hidden bg-black/50">
              <ClientOnly fallback={
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="inline-flex space-x-4 mb-4">
                      <Atom className="w-8 h-8 text-purple-600 animate-pulse" strokeWidth={1.5} />
                      <Brain className="w-8 h-8 text-blue-600 animate-pulse" strokeWidth={1.5} />
                      <Shield className="w-8 h-8 text-green-600 animate-pulse" strokeWidth={1.5} />
                    </div>
                    <p className="text-sm text-neutral-gray">Loading Trinity visualization...</p>
                  </div>
                </div>
              }>
                <TrinityCanvas />
              </ClientOnly>
            </div>

            {/* Legend */}
            <div className="flex justify-center mt-6 space-x-8">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-purple-600"></div>
                <span className="text-xs font-regular uppercase tracking-wider text-purple-600">Identity</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-blue-600"></div>
                <span className="text-xs font-regular uppercase tracking-wider text-blue-600">Consciousness</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-600"></div>
                <span className="text-xs font-regular uppercase tracking-wider text-green-600">Guardian</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
