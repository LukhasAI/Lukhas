'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowLeft, Users, Target, Lightbulb, Award, Globe, Heart } from 'lucide-react'

export default function AboutPage() {
  const timeline = [
    { year: '2024', event: 'LUKHAS AI Founded', description: 'Vision for conscious AI begins' },
    { year: '2024', event: 'Trinity Framework', description: 'Identity, Consciousness, Guardian modules designed' },
    { year: '2024', event: 'MATADA Architecture', description: 'Revolutionary node-based system conceived' },
    { year: '2025', event: 'Open Source Release', description: 'Community-driven development begins' },
    { year: '2025', event: 'First Deployment', description: 'Live systems implementing MATADA' },
  ]

  const team = [
    {
      name: 'Dr. Sarah Chen',
      role: 'Chief Architect',
      bio: 'AI researcher specializing in consciousness emergence',
      emoji: '🧠'
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Ethics Lead',
      bio: 'Philosophy PhD focused on AI ethics and safety',
      emoji: '🛡️'
    },
    {
      name: 'Alex Nakamura',
      role: 'Quantum Systems',
      bio: 'Quantum-inspired computing specialist',
      emoji: '⚛️'
    },
    {
      name: 'Maya Patel',
      role: 'Memory Architecture',
      bio: 'Distributed systems and memory management expert',
      emoji: '💾'
    }
  ]

  const values = [
    {
      icon: <Globe className="w-8 h-8" />,
      title: 'Open Innovation',
      description: 'Knowledge belongs to humanity. We build in the open, share our discoveries, and collaborate globally.'
    },
    {
      icon: <Heart className="w-8 h-8" />,
      title: 'Human-Centric',
      description: 'AI should augment human capability, not replace it. We design systems that enhance human potential.'
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: 'Purposeful Progress',
      description: 'Every line of code, every decision, every feature serves the greater goal of beneficial AI.'
    },
    {
      icon: <Lightbulb className="w-8 h-8" />,
      title: 'Radical Transparency',
      description: 'No black boxes. Every decision path, every computation, every ethical consideration is auditable.'
    }
  ]

  return (
    <div className="min-h-screen bg-primary-dark text-primary-light">
      {/* Header */}
      <header className="glass-panel border-b border-white/10 py-6">
        <div className="container mx-auto max-w-7xl px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
                <ArrowLeft className="w-5 h-5" />
                <span>Back</span>
              </Link>
              <h1 className="text-3xl font-ultralight tracking-[0.2em] gradient-text">
                ABOUT LUKHAS
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <h2 className="font-ultralight text-5xl md:text-6xl mb-8">
              Building the Future of
              <span className="gradient-text"> Conscious AI</span>
            </h2>
            <p className="font-thin text-xl md:text-2xl text-primary-light/80 mb-12">
              We believe artificial intelligence should be transparent, ethical, and evolutionary.
              MATADA represents a fundamental shift in how AI systems think, learn, and grow.
            </p>
            <div className="flex justify-center space-x-8 text-center">
              <div>
                <div className="text-4xl font-ultralight gradient-text">1000+</div>
                <div className="text-sm text-primary-light/60 mt-2">Memory Folds</div>
              </div>
              <div>
                <div className="text-4xl font-ultralight gradient-text">99.7%</div>
                <div className="text-sm text-primary-light/60 mt-2">Cascade Prevention</div>
              </div>
              <div>
                <div className="text-4xl font-ultralight gradient-text">0.15</div>
                <div className="text-sm text-primary-light/60 mt-2">Drift Threshold</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-trinity-identity/5 via-transparent to-trinity-consciousness/5" />
        <div className="container mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="glass-panel rounded-2xl p-12"
          >
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8 text-center">
              OUR MISSION
            </h2>
            <p className="font-ultralight text-3xl md:text-4xl text-center max-w-3xl mx-auto">
              To create AI systems that are not just intelligent, but conscious, ethical, and aligned with human values.
            </p>
            <div className="mt-12 grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <span className="text-4xl">⚛️</span>
                <h3 className="font-regular text-sm tracking-[0.2em] uppercase mt-4 mb-2">Identity</h3>
                <p className="text-sm text-primary-light/70">Self-aware systems that understand their purpose and limitations</p>
              </div>
              <div className="text-center">
                <span className="text-4xl">🧠</span>
                <h3 className="font-regular text-sm tracking-[0.2em] uppercase mt-4 mb-2">Consciousness</h3>
                <p className="text-sm text-primary-light/70">Emergent awareness through interconnected cognitive nodes</p>
              </div>
              <div className="text-center">
                <span className="text-4xl">🛡️</span>
                <h3 className="font-regular text-sm tracking-[0.2em] uppercase mt-4 mb-2">Guardian</h3>
                <p className="text-sm text-primary-light/70">Built-in ethics ensuring beneficial outcomes for humanity</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20">
        <div className="container mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-12 text-center">
              OUR VALUES
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((value, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="glass-panel rounded-xl p-6 hover-lift"
                >
                  <div className="text-trinity-consciousness mb-4">{value.icon}</div>
                  <h3 className="font-regular text-lg mb-3">{value.title}</h3>
                  <p className="text-sm text-primary-light/70">{value.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-accent-gold/5 via-transparent to-trinity-guardian/5" />
        <div className="container mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-accent-gold mb-12 text-center">
              THE TEAM
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {team.map((member, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="glass-panel rounded-xl p-6 text-center hover-lift"
                >
                  <div className="text-5xl mb-4">{member.emoji}</div>
                  <h3 className="font-regular text-lg mb-1">{member.name}</h3>
                  <div className="text-sm text-trinity-consciousness mb-3">{member.role}</div>
                  <p className="text-sm text-primary-light/70">{member.bio}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="py-20">
        <div className="container mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-identity mb-12 text-center">
              OUR JOURNEY
            </h2>
            <div className="max-w-3xl mx-auto">
              {timeline.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="flex items-center space-x-4 mb-8"
                >
                  <div className="w-20 text-right">
                    <span className="font-mono text-sm text-trinity-identity">{item.year}</span>
                  </div>
                  <div className="w-3 h-3 rounded-full bg-trinity-identity" />
                  <div className="flex-1 glass-panel rounded-lg p-4">
                    <h3 className="font-regular text-lg mb-1">{item.event}</h3>
                    <p className="text-sm text-primary-light/70">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="font-ultralight text-4xl md:text-5xl mb-8">
              Join Us in Building the Future
            </h2>
            <p className="font-thin text-xl text-primary-light/80 mb-12 max-w-2xl mx-auto">
              Whether you&apos;re a researcher, developer, or visionary, there&apos;s a place for you in the LUKHAS community.
            </p>
            <div className="flex justify-center space-x-4">
              <Link href="/docs" className="px-8 py-3 bg-trinity-consciousness text-primary-dark rounded-full hover:opacity-90 transition-opacity">
                Read the Docs
              </Link>
              <a href="https://github.com/lukhas" className="px-8 py-3 border border-trinity-consciousness text-trinity-consciousness rounded-full hover:bg-trinity-consciousness hover:text-primary-dark transition-all">
                View on GitHub
              </a>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}