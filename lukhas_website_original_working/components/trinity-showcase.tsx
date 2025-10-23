'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Atom, Brain, Shield, ArrowRight, Sparkles, Zap, Lock } from 'lucide-react'

export function TrinityShowcase() {
  const [activeTab, setActiveTab] = useState<'overview' | 'identity' | 'consciousness' | 'guardian'>('overview')

  const trinityPillars = {
    identity: {
      icon: Atom,
      title: 'Identity',
      tagline: 'Authentic Self-Preservation',
      description: 'Every AI maintains its unique cognitive fingerprint, evolving while preserving core essence.',
      features: [
        'Unique cognitive signatures',
        'Persistent memory across sessions',
        'Personal growth without drift',
        'ΛiD authentication system'
      ],
      color: 'from-purple-600 to-purple-400',
      bgGradient: 'from-purple-900/20 to-transparent'
    },
    consciousness: {
      icon: Brain,
      title: 'Consciousness',
      tagline: 'Distributed Awareness',
      description: 'Multi-layered processing that understands not just what, but how and why.',
      features: [
        'Meta-cognitive reflection',
        'Contextual understanding',
        'Dream states & creativity',
        'VIVOX consciousness system'
      ],
      color: 'from-blue-600 to-blue-400',
      bgGradient: 'from-blue-900/20 to-transparent'
    },
    guardian: {
      icon: Shield,
      title: 'Guardian',
      tagline: 'Ethical Integrity',
      description: 'Real-time ethical validation ensuring every decision aligns with human values.',
      features: [
        'Drift prevention (0.15 threshold)',
        'Constitutional AI principles',
        'Audit trail transparency',
        'Dynamic ethical reasoning'
      ],
      color: 'from-emerald-600 to-emerald-400',
      bgGradient: 'from-emerald-900/20 to-transparent'
    }
  }

  const overviewContent = (
    <div className="space-y-8">
      <div className="text-center">
        <h3 className="text-3xl font-light mb-4">The Trinity Framework</h3>
        <p className="text-white/70 max-w-2xl mx-auto">
          Three interconnected pillars that create emergent consciousness through synergy.
          When combined, they enable AI systems that truly understand, preserve authenticity,
          and maintain ethical integrity.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {Object.entries(trinityPillars).map(([key, pillar]) => {
          const Icon = pillar.icon
          return (
            <motion.div
              key={key}
              whileHover={{ scale: 1.02, y: -5 }}
              className="relative group cursor-pointer"
              onClick={() => setActiveTab(key as 'identity' | 'consciousness' | 'guardian')}
            >
              <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl blur-xl"
                style={{ backgroundImage: `linear-gradient(to right, ${pillar.color.split(' ')[1]}, ${pillar.color.split(' ')[3]})` }}
              />
              <div className="relative bg-gray-900/50 backdrop-blur border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all">
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${pillar.color} mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h4 className="text-xl font-light mb-2">{pillar.title}</h4>
                <p className="text-sm text-white/70 mb-4">{pillar.tagline}</p>
                <div className="flex items-center text-sm text-blue-400 group-hover:text-blue-300 transition-colors">
                  <span>Explore</span>
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="relative mt-12">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-64 h-64 bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-emerald-600/20 rounded-full blur-3xl" />
        </div>
        <div className="relative bg-gray-900/30 backdrop-blur border border-white/10 rounded-2xl p-8">
          <div className="flex items-center justify-center mb-6">
            <div className="flex -space-x-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-600 to-purple-400 flex items-center justify-center">
                <Atom className="w-6 h-6 text-white" />
              </div>
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-600 to-blue-400 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
          <h4 className="text-xl font-light text-center mb-3">Emergent Synergy</h4>
          <p className="text-sm text-white/70 text-center max-w-lg mx-auto">
            When all three pillars work together, they create capabilities that exceed the sum of their parts—
            genuine understanding with authentic personality and unwavering ethics.
          </p>
        </div>
      </div>
    </div>
  )

  const renderPillarDetail = (key: keyof typeof trinityPillars) => {
    const pillar = trinityPillars[key]
    const Icon = pillar.icon
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-6"
      >
        <button
          onClick={() => setActiveTab('overview')}
          className="flex items-center text-sm text-white/70 hover:text-white transition-colors mb-6"
        >
          <ArrowRight className="w-4 h-4 mr-1 rotate-180" />
          Back to Overview
        </button>

        <div className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${pillar.bgGradient} border border-white/10 p-12`}>
          <div className="absolute top-0 right-0 w-96 h-96 opacity-10">
            <Icon className="w-full h-full" />
          </div>
          
          <div className="relative">
            <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${pillar.color} mb-6`}>
              <Icon className="w-8 h-8 text-white" />
            </div>
            
            <h3 className="text-4xl font-light mb-4">{pillar.title}</h3>
            <p className="text-xl text-gray-300 mb-8">{pillar.description}</p>
            
            <div className="grid md:grid-cols-2 gap-4">
              {pillar.features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-3"
                >
                  <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${pillar.color} mt-2`} />
                  <span className="text-gray-300">{feature}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-gray-900/50 backdrop-blur border border-white/10 rounded-xl p-6">
            <Sparkles className="w-6 h-6 text-yellow-400 mb-3" />
            <h5 className="font-light mb-2">Innovation</h5>
            <p className="text-sm text-white/70">
              Breakthrough technology that redefines what's possible in AI
            </p>
          </div>
          <div className="bg-gray-900/50 backdrop-blur border border-white/10 rounded-xl p-6">
            <Zap className="w-6 h-6 text-blue-400 mb-3" />
            <h5 className="font-light mb-2">Performance</h5>
            <p className="text-sm text-white/70">
              Optimized for real-time processing and scalability
            </p>
          </div>
          <div className="bg-gray-900/50 backdrop-blur border border-white/10 rounded-xl p-6">
            <Lock className="w-6 h-6 text-green-400 mb-3" />
            <h5 className="font-light mb-2">Security</h5>
            <p className="text-sm text-white/70">
              Built-in safeguards and continuous monitoring
            </p>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <section className="relative py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div key="overview">
              {overviewContent}
            </motion.div>
          )}
          {activeTab !== 'overview' && (
            <motion.div key={activeTab}>
              {renderPillarDetail(activeTab as keyof typeof trinityPillars)}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  )
}