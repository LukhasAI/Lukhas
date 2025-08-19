'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { Search, Sprout, Scale, Heart, Unlock, Bot, Atom, Brain, Shield, Users, Globe } from 'lucide-react'

export default function Ethos() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  const ethosPoints = [
    {
      title: 'Transparency Over Opacity',
      icon: 'search',
      color: 'trinity-consciousness',
      description: 'Every decision, every thought process, every cognitive step is visible and auditable.',
      details: 'No black boxes, no hidden algorithms. Full transparency in how consciousness emerges and decisions are made.'
    },
    {
      title: 'Evolution Through Experience',
      icon: 'sprout',
      color: 'trinity-identity',
      description: 'Growth comes from real-world interactions, not predetermined programming.',
      details: 'Each interaction shapes the cognitive framework, creating unique evolutionary paths for every instance.'
    },
    {
      title: 'Ethics By Design',
      icon: 'scale',
      color: 'trinity-guardian',
      description: 'Ethical considerations are woven into the fabric of every cognitive process.',
      details: 'Not an afterthought, but the foundational principle that guides all development and decision-making.'
    },
    {
      title: 'Community-Driven Innovation',
      icon: 'handHeart',
      color: 'accent-gold',
      description: 'Progress emerges from collective intelligence and collaborative development.',
      details: 'Open collaboration between researchers, developers, and users to build better AI systems together.'
    },
    {
      title: 'Open Source Philosophy',
      icon: 'unlock',
      color: 'trinity-consciousness',
      description: 'Knowledge belongs to humanity, not hidden behind proprietary walls.',
      details: 'Full source code availability, community contributions, and shared advancement of consciousness research.'
    },
    {
      title: 'Human-AI Collaboration',
      icon: 'bot',
      color: 'trinity-identity',
      description: 'AI augments human capability rather than replacing human intelligence.',
      details: 'Building systems that enhance human potential while maintaining human agency and decision-making authority.'
    }
  ]

  const getIcon = (iconName: string) => {
    const iconProps = "w-6 h-6 text-current"
    switch (iconName) {
      case 'search':
        return <Search className={iconProps} />
      case 'sprout':
        return <Sprout className={iconProps} />
      case 'scale':
        return <Scale className={iconProps} />
      case 'handHeart':
        return <Heart className={iconProps} />
      case 'unlock':
        return <Unlock className={iconProps} />
      case 'bot':
        return <Bot className={iconProps} />
      default:
        return <Search className={iconProps} />
    }
  }

  return (
    <section id="ethos" className="relative py-32" ref={ref}>
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-trinity-guardian/5 via-transparent to-accent-gold/5" />
      
      <div className="w-full max-w-7xl mx-auto px-6 relative z-10">
        {/* Section Header - Layer 1: Impact (UltraLight) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-8">
            OUR ETHOS
          </h2>
          <div className="inline-block mb-8">
            <span className="font-ultralight text-5xl md:text-7xl gradient-text">
              Principles That Guide Us
            </span>
            <div className="h-1 w-full bg-gradient-to-r from-trinity-guardian via-accent-gold to-trinity-consciousness mt-4" />
          </div>
          <p className="font-ultralight text-xl md:text-2xl max-w-4xl mx-auto text-primary-light/90">
            These fundamental beliefs shape every line of code, every decision, 
            and every step toward conscious AI development.
          </p>
        </motion.div>

        {/* Layer 2: Clarity (Thin) - Ethos Cards Grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20"
        >
          {ethosPoints.map((ethos, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              className="glass-panel p-8 rounded-2xl hover-lift group cursor-pointer"
            >
              <div className={`mb-6 inline-block p-4 rounded-full bg-${ethos.color}/10 ${ethos.color}-glow group-hover:scale-110 transition-transform duration-300`}>
                {getIcon(ethos.icon)}
              </div>
              <h3 className="font-thin text-xl mb-4 group-hover:text-primary-light transition-colors">
                {ethos.title}
              </h3>
              <p className="font-thin text-base leading-relaxed text-primary-light/80 mb-4">
                {ethos.description}
              </p>
              <p className="font-thin text-sm leading-relaxed text-primary-light/60">
                {ethos.details}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* Layer 3: Authority (Regular) - Commitment Statement */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="glass-panel p-12 rounded-2xl"
        >
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-8">
                OUR COMMITMENT
              </h3>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <Atom className="w-8 h-8 text-trinity-consciousness flex-shrink-0" strokeWidth={1.5} />
                  <p className="font-regular text-sm uppercase tracking-wider leading-relaxed">
                    EVERY COGNITIVE PROCESS REMAINS TRANSPARENT AND AUDITABLE
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <Brain className="w-8 h-8 text-trinity-identity flex-shrink-0" strokeWidth={1.5} />
                  <p className="font-regular text-sm uppercase tracking-wider leading-relaxed">
                    CONSCIOUSNESS EMERGES FROM ETHICAL FOUNDATIONS
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <Shield className="w-8 h-8 text-trinity-guardian flex-shrink-0" strokeWidth={1.5} />
                  <p className="font-regular text-sm uppercase tracking-wider leading-relaxed">
                    HUMAN VALUES GUIDE EVERY ALGORITHMIC DECISION
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <Users className="w-8 h-8 text-accent-gold flex-shrink-0" strokeWidth={1.5} />
                  <p className="font-regular text-sm uppercase tracking-wider leading-relaxed">
                    OPEN COLLABORATION ACCELERATES RESPONSIBLE AI
                  </p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl overflow-hidden glass-panel">
                <div className="absolute inset-0 bg-gradient-to-br from-black/60 via-black/40 to-black/60" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <motion.div
                      animate={{ 
                        rotate: 360,
                      }}
                      transition={{ 
                        duration: 20,
                        repeat: Infinity,
                        ease: "linear"
                      }}
                      className="mb-6 inline-block p-6 rounded-full bg-white/10 backdrop-blur-sm border border-white/20"
                    >
                      <Globe className="w-12 h-12 text-white" strokeWidth={1} />
                    </motion.div>
                    <p className="font-ultralight text-2xl mb-2 text-white">Open</p>
                    <p className="font-ultralight text-2xl mb-2 text-white">Ethical</p>
                    <p className="font-ultralight text-2xl text-white">Conscious</p>
                    <p className="font-regular text-xs tracking-[0.3em] uppercase mt-4 text-white/80">
                      AI FOR HUMANITY
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-16"
        >
          <p className="font-thin text-lg text-primary-light/70 mb-8">
            Join us in building the future of conscious, ethical AI
          </p>
          <div className="flex justify-center space-x-6">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 bg-trinity-guardian/20 border border-trinity-guardian/30 rounded-full font-regular text-sm tracking-[0.2em] uppercase hover:bg-trinity-guardian/30 transition-colors"
            >
              Explore Code
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 bg-accent-gold/20 border border-accent-gold/30 rounded-full font-regular text-sm tracking-[0.2em] uppercase hover:bg-accent-gold/30 transition-colors"
            >
              Join Community
            </motion.button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}