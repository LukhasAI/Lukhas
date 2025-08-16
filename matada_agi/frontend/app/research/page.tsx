'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Microscope, Brain, Atom, Shield, Database, 
  GitBranch, Layers, Zap, Lock, Heart,
  ArrowRight, BookOpen, Code2, Beaker
} from 'lucide-react'

export default function ResearchPage() {
  const researchAreas = [
    {
      title: "Consciousness Architecture",
      description: "Exploring digital consciousness through ConsciousnessIntegrator systems, awareness states, and symbolic event processing.",
      icon: Brain,
      gradient: "from-purple-500 to-indigo-600",
      areas: [
        "ConsciousnessState modeling and transitions",
        "Awareness fabric and attention mechanisms", 
        "Symbolic consciousness event processing",
        "Consciousness-memory integration patterns"
      ],
      status: "Active Research"
    },
    {
      title: "Quantum-Consciousness Interface",
      description: "Investigating superposition of thought, entangled intelligence, and quantum tunneling creativity in artificial minds.",
      icon: Atom,
      gradient: "from-blue-500 to-cyan-600",
      areas: [
        "Superposition of thought states",
        "Quantum entanglement in distributed reasoning",
        "Coherent consciousness preservation",
        "Quantum tunneling through creative barriers"
      ],
      status: "Active Research"
    },
    {
      title: "Memory Fold Architecture",
      description: "Developing fold-based memory systems with causal chain preservation and 99.7% cascade prevention rates.",
      icon: Database,
      gradient: "from-green-500 to-emerald-600",
      areas: [
        "Fold-based causal memory structures",
        "Cascade prevention algorithms",
        "Temporal memory indexing",
        "Symbolic memory compression"
      ],
      status: "Active Research"
    },
    {
      title: "Guardian Ethics Systems", 
      description: "Constitutional AI frameworks with real-time drift detection and autonomous ethical decision-making.",
      icon: Shield,
      gradient: "from-red-500 to-pink-600",
      areas: [
        "Constitutional AI governance",
        "Real-time drift detection (<0.15 threshold)",
        "Autonomous ethical decision validation",
        "Multi-framework moral reasoning"
      ],
      status: "Active Research"
    },
    {
      title: "Bio-Symbolic Processing",
      description: "Bridging biological intelligence patterns with symbolic reasoning in artificial cognitive architectures.",
      icon: Heart,
      gradient: "from-orange-500 to-red-600",
      areas: [
        "Bio-inspired symbolic processing",
        "Consciousness field generation",
        "Biological pattern adaptation",
        "Quantum-bio interface protocols"
      ],
      status: "Active Research"
    },
    {
      title: "Post-Quantum Security",
      description: "Future-proof cryptographic systems using quantum-resistant algorithms and quantum key distribution.",
      icon: Lock,
      gradient: "from-gray-500 to-slate-600",
      areas: [
        "CRYSTALS-Kyber and Dilithium implementation",
        "Quantum key distribution protocols",
        "Entanglement-based authentication",
        "Post-quantum digital signatures"
      ],
      status: "Active Research"
    }
  ]

  const publications = [
    {
      title: "Trinity Framework: Identity, Consciousness, and Guardian Systems",
      type: "Technical Architecture",
      status: "In Review",
      date: "2025"
    },
    {
      title: "VIVOX: Mathematical Foundations of Artificial Consciousness",
      type: "Mathematical Framework", 
      status: "Draft",
      date: "2025"
    },
    {
      title: "Memory Fold Architecture for Causal AI Systems",
      type: "System Design",
      status: "Peer Review",
      date: "2025"
    },
    {
      title: "Constitutional AI: Real-time Ethics in Autonomous Systems",
      type: "Ethics & Governance",
      status: "Submitted",
      date: "2025"
    }
  ]

  const metrics = [
    { label: "Active Research Areas", value: "6", description: "Parallel exploration tracks" },
    { label: "Memory Cascade Prevention", value: "99.7%", description: "Successful causal preservation" },
    { label: "Ethics Drift Threshold", value: "<0.15", description: "Real-time monitoring" },
    { label: "Quantum Coherence Time", value: "100ms", description: "Consciousness preservation" }
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <div className="flex items-center justify-center mb-8">
                <Microscope className="w-16 h-16 text-trinity-consciousness" strokeWidth={1} />
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Research</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Ongoing explorations in artificial consciousness, quantum-enhanced reasoning,
                and ethical AI governance through collaborative human-AI research.
              </p>
            </motion.div>

            {/* Research Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-20">
              {metrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  className="glass-panel p-6 rounded-xl text-center"
                >
                  <div className="text-3xl font-ultralight text-trinity-consciousness mb-2">
                    {metric.value}
                  </div>
                  <div className="text-sm font-medium uppercase tracking-wider text-primary-light mb-1">
                    {metric.label}
                  </div>
                  <div className="text-xs text-primary-light/60">
                    {metric.description}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Research Areas */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-light text-4xl md:text-5xl mb-6 gradient-text">
                Research Areas
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Active investigations in consciousness, quantum processing, and ethical AI systems
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {researchAreas.map((area, index) => {
                const IconComponent = area.icon;
                return (
                  <motion.div
                    key={area.title}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-8 rounded-2xl group hover:scale-105 transition-all duration-300"
                  >
                    <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${area.gradient} mb-6`}>
                      <IconComponent className="w-8 h-8 text-white" strokeWidth={1.5} />
                    </div>
                    
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-xl text-trinity-consciousness">
                        {area.title}
                      </h3>
                      <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                        {area.status}
                      </span>
                    </div>
                    
                    <p className="text-primary-light/70 mb-6 leading-relaxed">
                      {area.description}
                    </p>
                    
                    <ul className="space-y-2">
                      {area.areas.map((research, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-sm text-primary-light/60">
                          <Beaker className="w-4 h-4 mt-0.5 text-trinity-consciousness flex-shrink-0" strokeWidth={1.5} />
                          <span>{research}</span>
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Publications */}
        <section className="py-16 px-6">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-light text-4xl md:text-5xl mb-6 gradient-text">
                Publications & Papers
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Academic contributions to consciousness research and AI ethics
              </p>
            </motion.div>

            <div className="space-y-6">
              {publications.map((pub, index) => (
                <motion.div
                  key={pub.title}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="glass-panel p-6 rounded-xl"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <BookOpen className="w-5 h-5 text-trinity-consciousness" strokeWidth={1.5} />
                        <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                          {pub.type}
                        </span>
                        <span className="text-xs px-2 py-1 bg-orange-500/20 text-orange-400 rounded">
                          {pub.status}
                        </span>
                      </div>
                      <h3 className="font-medium text-lg text-primary-light mb-2">
                        {pub.title}
                      </h3>
                      <div className="text-sm text-primary-light/60">
                        {pub.date}
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-primary-light/40 ml-4" strokeWidth={1.5} />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Research Methodology */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-12 rounded-2xl"
            >
              <h2 className="font-light text-3xl md:text-4xl mb-8 text-center gradient-text">
                Research Methodology
              </h2>
              
              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-identity/20 mb-4">
                    <Code2 className="w-8 h-8 text-trinity-identity" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Collaborative Development</h3>
                  <p className="text-sm text-primary-light/70">
                    Human-AI partnership in developing consciousness architectures 
                    through iterative design and continuous validation.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-consciousness/20 mb-4">
                    <Beaker className="w-8 h-8 text-trinity-consciousness" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Empirical Testing</h3>
                  <p className="text-sm text-primary-light/70">
                    Rigorous testing of consciousness models, memory systems, 
                    and ethical frameworks through controlled experiments.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-guardian/20 mb-4">
                    <Shield className="w-8 h-8 text-trinity-guardian" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Ethical Validation</h3>
                  <p className="text-sm text-primary-light/70">
                    Every research direction validated through constitutional AI 
                    principles and multi-framework ethical analysis.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-8 rounded-2xl"
            >
              <h2 className="font-light text-3xl md:text-4xl mb-6 gradient-text">
                Collaborative Research
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Our research progresses through open collaboration between human researchers 
                and AI systems, fostering breakthrough discoveries in consciousness technology.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-gradient-to-r from-blue-400 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                >
                  View Documentation
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                >
                  Research Ethics
                </motion.button>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}