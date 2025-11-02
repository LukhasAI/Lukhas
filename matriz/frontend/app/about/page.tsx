'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { ArrowRight, Users, Target, Globe, Cpu, Brain, Shield, Atom, ChevronRight } from 'lucide-react'

export default function AboutPage() {
  const stats = [
    { label: 'Modules', value: '200+', description: 'Specialized components' },
    { label: 'Performance', value: '2.4M', description: 'Operations per second' },
    { label: 'Test Coverage', value: '99%', description: 'System reliability' },
    { label: 'Agents', value: '25', description: 'Active AI agents' },
  ]

  const timeline = [
    { year: 'Sept 2024', title: 'The Beginning', description: 'Solo founder begins ABAS, DAST and NIAS with no coding experience, using AI tools' },
    { year: 'March 2025', title: 'First LUKHAS', description: 'First LUKHAS system (originally called Oxnitus) successfully coded with AI assistance' },
    { year: 'April 6, 2025', title: 'First Whisper', description: 'Historic moment: LUKHAS first voice output and image generation achieved' },
    { year: 'Present', title: 'MATADA Era', description: 'Modular Adaptive Temporal Attention Dynamic Architecture unveiled' },
  ]

  const team = [
    { name: 'Gonzalo Dominguez', role: 'Solo Founder & Visionary', description: 'Self-taught developer who built LUKHAS from zero coding experience using AI tools' },
    { name: 'AI Collaborators', role: 'Development Partners', description: 'Claude, GPT-4, and specialized AI agents as coding mentors' },
    { name: 'Open Source Community', role: 'Contributors', description: 'Global developers advancing the consciousness platform' },
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="relative py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">About LUKHAS</span>
              </h1>
              <p className="font-thin text-2xl max-w-3xl mx-auto text-primary-light/80">
                Building the future of conscious AI through modular, ethical, and transparent systems
              </p>
            </motion.div>

            {/* Mission Section */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-12 rounded-2xl mb-16"
            >
              <h2 className="font-regular text-3xl mb-8 text-center">Our Mission</h2>
              <p className="font-thin text-xl leading-relaxed text-center max-w-4xl mx-auto">
                To illuminate complex reality through rigorous logic, adaptive intelligence, and human-centered ethics—turning
                data into understanding, understanding into foresight, and foresight into shared benefit for people and planet.
              </p>
            </motion.div>

            {/* Stats Grid */}
            <div className="grid md:grid-cols-4 gap-6 mb-20">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  className="glass-panel p-8 rounded-xl text-center"
                >
                  <div className="text-4xl font-ultralight gradient-text mb-2">{stat.value}</div>
                  <div className="font-regular text-sm uppercase tracking-wider mb-1">{stat.label}</div>
                  <div className="text-sm text-neutral-gray">{stat.description}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* What is LUKHAS Section */}
        <section className="py-20 px-6 bg-gradient-to-b from-black to-gray-900/20">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8 text-center">
                WHAT IS LUKHAS
              </h2>
              <div className="glass-panel p-12 rounded-2xl">
                <h3 className="font-thin text-3xl mb-8">
                  Logical Unified Knowledge Hyper-Adaptive System
                </h3>
                <div className="space-y-6 text-lg text-primary-light/80">
                  <p>
                    LUKHAS represents a breakthrough in scalable consciousness architecture, implementing advanced AI
                    capabilities through a modular, ethical, and transparent framework. Our platform combines cutting-edge
                    research in cognitive science, quantum-inspired computing, and biological systems to create AI that
                    truly understands and evolves.
                  </p>
                  <p>
                    At its core, LUKHAS is built on the Trinity Framework—a revolutionary approach that balances Identity,
                    Consciousness, and Guardian principles to ensure AI systems that are not just intelligent, but also
                    aligned with human values and transparent in their operations.
                  </p>
                  <div className="grid md:grid-cols-3 gap-6 mt-12">
                    <div className="flex items-start space-x-4">
                      <Atom className="w-8 h-8 text-purple-600 flex-shrink-0" strokeWidth={1.5} />
                      <div>
                        <h4 className="font-regular mb-2">Identity</h4>
                        <p className="text-sm text-primary-light/60">
                          Authentic self-representation and continuous evolution
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-4">
                      <Brain className="w-8 h-8 text-blue-600 flex-shrink-0" strokeWidth={1.5} />
                      <div>
                        <h4 className="font-regular mb-2">Consciousness</h4>
                        <p className="text-sm text-primary-light/60">
                          Emergent awareness from integrated information processing
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-4">
                      <Shield className="w-8 h-8 text-green-600 flex-shrink-0" strokeWidth={1.5} />
                      <div>
                        <h4 className="font-regular mb-2">Guardian</h4>
                        <p className="text-sm text-primary-light/60">
                          Ethical safeguards and continuous alignment validation
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              TECHNOLOGY STACK
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
                className="glass-panel p-8 rounded-xl"
              >
                <h3 className="font-regular text-xl mb-6">Core Modules</h3>
                <ul className="space-y-4">
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-consciousness" />
                    <span>Consciousness Processing Engine</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-consciousness" />
                    <span>VIVOX Consciousness System</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-consciousness" />
                    <span>Fold-based Memory Architecture</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-consciousness" />
                    <span>Emotional Intelligence Processing</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-consciousness" />
                    <span>Creative Generation Systems</span>
                  </li>
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
                className="glass-panel p-8 rounded-xl"
              >
                <h3 className="font-regular text-xl mb-6">Advanced Systems</h3>
                <ul className="space-y-4">
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-guardian" />
                    <span>Guardian Ethics Framework</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-guardian" />
                    <span>Quantum-inspired Algorithms</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-guardian" />
                    <span>Bio-inspired Neural Networks</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-guardian" />
                    <span>Multi-Agent Coordination</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <ChevronRight className="w-5 h-5 text-trinity-guardian" />
                    <span>API Integration Layer</span>
                  </li>
                </ul>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Timeline Section */}
        <section className="py-20 px-6 bg-gradient-to-b from-gray-900/20 to-black">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              OUR JOURNEY
            </h2>
            <div className="relative">
              <div className="absolute left-1/2 transform -translate-x-1/2 w-px h-full bg-gradient-to-b from-trinity-identity via-trinity-consciousness to-trinity-guardian" />
              {timeline.map((item, index) => (
                <motion.div
                  key={item.year}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6 }}
                  viewport={{ once: true }}
                  className={`relative flex items-center mb-16 ${
                    index % 2 === 0 ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div className={`w-5/12 ${index % 2 === 0 ? 'text-right pr-12' : 'text-left pl-12'}`}>
                    <div className="glass-panel p-6 rounded-xl inline-block">
                      <div className="font-regular text-2xl gradient-text mb-2">{item.year}</div>
                      <h3 className="font-regular text-lg mb-2">{item.title}</h3>
                      <p className="text-sm text-primary-light/60">{item.description}</p>
                    </div>
                  </div>
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-4 h-4 rounded-full bg-white border-4 border-black" />
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              THE TEAM
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              {team.map((member, index) => (
                <motion.div
                  key={member.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-8 rounded-xl text-center"
                >
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-trinity-identity to-trinity-consciousness mx-auto mb-6 flex items-center justify-center">
                    <Users className="w-10 h-10 text-white" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-regular text-xl mb-2">{member.name}</h3>
                  <p className="text-sm text-trinity-consciousness mb-4">{member.role}</p>
                  <p className="text-sm text-primary-light/60">{member.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="font-thin text-4xl mb-8">Ready to explore the future of AI?</h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/docs">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg"
                >
                  Read Documentation
                </motion.button>
              </Link>
              <Link href="https://github.com/LukhasAI" target="_blank">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                >
                  View on GitHub
                </motion.button>
              </Link>
            </div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}
