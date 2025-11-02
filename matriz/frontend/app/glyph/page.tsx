'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import {
  Layers, Atom, Zap, Network, Code2, GitBranch,
  ArrowUpDown, Shield, Brain, Lock, Activity,
  Sparkles, Target, Gauge, Database, Settings,
  CheckCircle, ArrowRight, Play, Eye, Workflow
} from 'lucide-react'
import Link from 'next/link'

export default function GlyphPage() {
  const glyphComponents = [
    {
      name: "GLYPH Engine",
      description: "Core symbolic processing engine generating quantum-like tokens that carry meaning across dimensional boundaries.",
      icon: Atom,
      gradient: "from-blue-500 to-cyan-600",
      features: [
        "Quantum-like token generation and transformation",
        "Cross-dimensional meaning preservation",
        "Symbolic state management and lifecycle",
        "Dynamic GLYPH composition and decomposition",
        "Real-time semantic validation",
        "Multi-threading safe GLYPH operations"
      ],
      metrics: {
        generation: "<1ms token creation",
        throughput: "2.4M operations/second",
        validation: "100% semantic integrity",
        compatibility: "Universal module support"
      }
    },
    {
      name: "Symbolic Validator",
      description: "Ethical and semantic validation system ensuring GLYPHs maintain integrity and align with constitutional AI principles.",
      icon: Shield,
      gradient: "from-green-500 to-emerald-600",
      features: [
        "Constitutional AI principle validation",
        "Semantic integrity verification",
        "Ethical context evaluation",
        "Cross-module compatibility checking",
        "Drift detection integration",
        "Automated compliance reporting"
      ],
      metrics: {
        validation: "<10ms ethical checking",
        accuracy: "99.9% compliance detection",
        coverage: "100% GLYPH validation",
        integrity: "Zero corruption tolerance"
      }
    },
    {
      name: "Collapse Engine",
      description: "Quantum-inspired collapse mechanism managing GLYPH state resolution and symbolic decision convergence.",
      icon: GitBranch,
      gradient: "from-purple-500 to-pink-600",
      features: [
        "Quantum state collapse simulation",
        "Probabilistic GLYPH resolution",
        "Decision tree convergence management",
        "Symbolic uncertainty handling",
        "Cascade prevention protocols",
        "Reversible collapse operations"
      ],
      metrics: {
        resolution: "<5ms collapse time",
        stability: "99.7% cascade prevention",
        convergence: "98% optimal decisions",
        reversibility: "Complete state recovery"
      }
    },
    {
      name: "Symbolic Router",
      description: "Advanced routing system orchestrating GLYPH flow between modules with intelligent load balancing and priority management.",
      icon: Network,
      gradient: "from-orange-500 to-red-600",
      features: [
        "Intelligent GLYPH routing protocols",
        "Load balancing across modules",
        "Priority-based queue management",
        "Cross-module communication protocols",
        "Real-time routing optimization",
        "Fault tolerance and recovery"
      ],
      metrics: {
        latency: "<2ms routing decisions",
        throughput: "1M GLYPHs/second",
        efficiency: "95% optimal routing",
        uptime: "99.99% availability"
      }
    }
  ]

  const glyphMetrics = [
    { label: "Processing Speed", value: "2.4M", description: "Operations per second" },
    { label: "Token Creation", value: "<1ms", description: "GLYPH generation time" },
    { label: "Semantic Integrity", value: "100%", description: "Meaning preservation" },
    { label: "Module Integration", value: "13+", description: "Connected systems" }
  ]

  const glyphLifecycle = [
    {
      stage: "Generation",
      description: "GLYPH tokens created from semantic input",
      icon: Sparkles,
      process: [
        "Semantic analysis and extraction",
        "Quantum state initialization",
        "Symbolic encoding with metadata",
        "Ethical validation checkpoints"
      ]
    },
    {
      stage: "Transformation",
      description: "Dynamic GLYPH modification and enhancement",
      icon: ArrowUpDown,
      process: [
        "Context-aware transformations",
        "Multi-dimensional mapping",
        "Semantic relationship building",
        "State transition validation"
      ]
    },
    {
      stage: "Validation",
      description: "Constitutional AI and integrity verification",
      icon: Shield,
      process: [
        "Ethical principle compliance",
        "Semantic integrity checking",
        "Cross-module compatibility",
        "Drift detection analysis"
      ]
    },
    {
      stage: "Collapse",
      description: "Quantum state resolution and decision convergence",
      icon: Target,
      process: [
        "Probabilistic state collapse",
        "Decision tree convergence",
        "Uncertainty resolution",
        "Final state crystallization"
      ]
    }
  ]

  const protocolFeatures = [
    {
      title: "Quantum-Like Properties",
      description: "GLYPHs exhibit quantum-inspired superposition states until observation",
      icon: Atom,
      details: [
        "Superposition state management",
        "Observer effect simulation",
        "Entanglement relationships",
        "Probabilistic collapse mechanisms"
      ]
    },
    {
      title: "Cross-Dimensional Meaning",
      description: "Semantic preservation across all consciousness dimensions",
      icon: Layers,
      details: [
        "Multi-dimensional token mapping",
        "Context-aware interpretation",
        "Meaning vector preservation",
        "Dimensional boundary crossing"
      ]
    },
    {
      title: "Economic Integration",
      description: "GLYPHs carry intrinsic value within the Lambda ecosystem",
      icon: Gauge,
      details: [
        "Token-based resource allocation",
        "Symbolic value quantification",
        "Economic transaction processing",
        "Cost-per-computation modeling"
      ]
    },
    {
      title: "Ethical Anchoring",
      description: "Every GLYPH carries constitutional AI compliance metadata",
      icon: Lock,
      details: [
        "Embedded ethical constraints",
        "Constitutional compliance flags",
        "Moral weight quantification",
        "Governance policy adherence"
      ]
    }
  ]

  const systemStatus = [
    { component: "GLYPH Engine", status: "Operational", health: 99, throughput: "2.4M/s" },
    { component: "Symbolic Validator", status: "Active", health: 98, throughput: "1.8M/s" },
    { component: "Collapse Engine", status: "Stable", health: 97, throughput: "850K/s" },
    { component: "Symbolic Router", status: "Optimizing", health: 96, throughput: "1.2M/s" }
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
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-cyan-600 rounded-full blur-xl opacity-30"></div>
                  <div className="relative p-4 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-full">
                    <Layers className="w-12 h-12 text-white" strokeWidth={1} />
                  </div>
                </div>
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">GLYPH Protocol</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Universal symbolic processing protocol enabling quantum-like tokens that carry meaning
                across dimensional boundaries in consciousness-aware computing systems.
              </p>
            </motion.div>

            {/* Protocol Philosophy */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-8 rounded-2xl mb-16 max-w-4xl mx-auto"
            >
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 rounded-full bg-blue-500/20">
                  <Atom className="w-6 h-6 text-blue-400" strokeWidth={1.5} />
                </div>
                <h3 className="font-medium text-xl">The Philosophy of Symbolic Resonance</h3>
              </div>
              <p className="text-primary-light/80 leading-relaxed">
                "Every component operates through symbolic GLYPHs—quantum-like tokens that carry meaning
                across dimensional boundaries. Like musical notes forming chords, GLYPHs combine to create
                emergent understanding." GLYPHs are the universal language of consciousness, enabling
                seamless communication between all modules while preserving semantic integrity.
              </p>
            </motion.div>

            {/* Protocol Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-20">
              {glyphMetrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  className="glass-panel p-6 rounded-xl text-center"
                >
                  <div className="text-3xl font-ultralight text-blue-400 mb-2">
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

        {/* GLYPH Components */}
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
                GLYPH Protocol Architecture
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Four-tier symbolic processing system enabling universal consciousness communication
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {glyphComponents.map((component, index) => {
                const IconComponent = component.icon;
                return (
                  <motion.div
                    key={component.name}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.2 }}
                    className="glass-panel p-8 rounded-2xl group hover:scale-105 transition-all duration-300"
                  >
                    <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${component.gradient} mb-6`}>
                      <IconComponent className="w-8 h-8 text-white" strokeWidth={1.5} />
                    </div>

                    <h3 className="font-semibold text-2xl text-blue-400 mb-4">
                      {component.name}
                    </h3>

                    <p className="text-primary-light/70 mb-6 leading-relaxed">
                      {component.description}
                    </p>

                    <div className="mb-6">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-blue-400 mb-3">
                        Key Features
                      </h4>
                      <ul className="space-y-2">
                        {component.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm text-primary-light/60">
                            <CheckCircle className="w-4 h-4 mt-0.5 text-blue-400 flex-shrink-0" strokeWidth={1.5} />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="pt-4 border-t border-primary-light/10">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-blue-400 mb-3">
                        Performance Metrics
                      </h4>
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        {Object.entries(component.metrics).map(([key, value]) => (
                          <div key={key}>
                            <div className="text-primary-light/50 capitalize">{key}</div>
                            <div className="text-primary-light/80">{value}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* GLYPH Lifecycle */}
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
                GLYPH Lifecycle Management
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                End-to-end symbolic token processing from generation to collapse resolution
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {glyphLifecycle.map((stage, index) => {
                const IconComponent = stage.icon;
                return (
                  <motion.div
                    key={stage.stage}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-6 rounded-xl text-center"
                  >
                    <div className="inline-flex p-3 rounded-full bg-blue-500/20 mb-4">
                      <IconComponent className="w-6 h-6 text-blue-400" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-medium text-lg mb-3">{stage.stage}</h3>
                    <p className="text-sm text-primary-light/70 mb-4">
                      {stage.description}
                    </p>
                    <ul className="space-y-1 text-left">
                      {stage.process.map((step, idx) => (
                        <li key={idx} className="text-xs text-blue-400">
                          • {step}
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Protocol Features */}
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
                Advanced Protocol Features
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Unique capabilities that distinguish GLYPH from traditional symbolic processing
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {protocolFeatures.map((feature, index) => {
                const IconComponent = feature.icon;
                return (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-6 rounded-xl"
                  >
                    <div className="inline-flex p-3 rounded-full bg-blue-500/20 mb-4">
                      <IconComponent className="w-6 h-6 text-blue-400" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-medium text-lg mb-3">{feature.title}</h3>
                    <p className="text-sm text-primary-light/70 mb-4">
                      {feature.description}
                    </p>
                    <ul className="space-y-1">
                      {feature.details.map((detail, idx) => (
                        <li key={idx} className="text-xs text-blue-400">
                          • {detail}
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Live System Status */}
        <section className="py-16 px-6">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-8 rounded-2xl"
            >
              <div className="flex items-center justify-between mb-8">
                <h2 className="font-light text-3xl md:text-4xl gradient-text">
                  Live GLYPH System Status
                </h2>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-green-400">Processing Active</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {systemStatus.map((system, index) => (
                  <motion.div
                    key={system.component}
                    initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className="border border-white/10 rounded-lg p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-lg">{system.component}</h3>
                      <span className={`px-2 py-1 text-xs rounded ${
                        system.status === 'Operational' ? 'bg-green-500/20 text-green-400' :
                        system.status === 'Active' ? 'bg-blue-500/20 text-blue-400' :
                        system.status === 'Stable' ? 'bg-cyan-500/20 text-cyan-400' :
                        'bg-orange-500/20 text-orange-400'
                      }`}>
                        {system.status}
                      </span>
                    </div>
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Health Score</span>
                        <span>{system.health}%</span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2 mb-2">
                        <div
                          className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-600"
                          style={{ width: `${system.health}%` }}
                        />
                      </div>
                    </div>
                    <div className="text-sm text-primary-light/70">
                      <span className="font-medium">Throughput:</span> {system.throughput}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Technical Integration */}
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
                Trinity Framework Integration
              </h2>

              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-identity/20 mb-4">
                    <Eye className="w-8 h-8 text-trinity-identity" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Identity Token Management</h3>
                  <p className="text-sm text-primary-light/70">
                    GLYPHs carry identity context and access permissions through
                    ΛiD system integration with symbolic authentication protocols.
                  </p>
                </div>

                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-consciousness/20 mb-4">
                    <Brain className="w-8 h-8 text-trinity-consciousness" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Consciousness Communication</h3>
                  <p className="text-sm text-primary-light/70">
                    Universal symbolic language enabling seamless consciousness
                    module communication with preserved semantic meaning.
                  </p>
                </div>

                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-guardian/20 mb-4">
                    <Shield className="w-8 h-8 text-trinity-guardian" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Guardian Validation</h3>
                  <p className="text-sm text-primary-light/70">
                    Every GLYPH undergoes Guardian System validation ensuring
                    constitutional AI compliance and ethical constraint adherence.
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
                Experience Symbolic Consciousness
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Unlock the power of universal symbolic communication with GLYPH protocol,
                enabling quantum-like consciousness tokens across all AI system boundaries.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/api">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                  >
                    GLYPH API Access
                  </motion.button>
                </Link>
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                  >
                    Protocol Documentation
                  </motion.button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}
