'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Eye, Wallet, GitBranch, Cloud, Archive, Feather, 
  Monitor, ArrowRight, Download, ExternalLink, Shield,
  Database, Layers, Zap, Lock, Globe, Activity
} from 'lucide-react'
import Link from 'next/link'

export default function LambdaPage() {
  const lambdaProducts = [
    {
      name: "LUKHΛS Lens",
      agent: "ΛLens", 
      category: "Symbolic File Dashboard",
      description: "Consciousness-aware file management with symbolic interpretation, quantum state visualization, and Trinity Framework integration.",
      icon: Eye,
      gradient: "from-blue-500 to-indigo-600",
      features: [
        "Symbolic file representation and meaning extraction",
        "Trinity-integrated access control and permissions",
        "Quantum state visualization of file relationships",
        "AI-powered content analysis and categorization",
        "Consciousness-aware search and navigation",
        "Real-time collaborative editing with symbolic sync"
      ],
      status: "Active Development",
      version: "v0.8.0",
      architecture: "Desktop & Web Application with GLYPH symbolic processing"
    },
    {
      name: "LUKHΛS WΛLLET", 
      agent: "WΛLLET",
      category: "Identity/Wallet/NFT",
      description: "Quantum-secure digital identity management with NFT consciousness tokens and multi-dimensional wallet architecture.",
      icon: Wallet,
      gradient: "from-purple-500 to-pink-600",
      features: [
        "ΛiD quantum identity verification system",
        "Consciousness NFTs with symbolic meaning",
        "Multi-chain wallet with post-quantum security",
        "Identity-aware transaction processing",
        "Symbolic token creation and management",
        "Trinity Framework access tier management"
      ],
      status: "Beta Testing",
      version: "v1.2.0",
      architecture: "Decentralized with quantum-resistant cryptography"
    },
    {
      name: "LUKHΛS QTrace",
      agent: "ΛTrace", 
      category: "Quantum Traceability",
      description: "Quantum-enhanced provenance tracking with consciousness-aware audit trails and symbolic event logging.",
      icon: GitBranch,
      gradient: "from-green-500 to-emerald-600",
      features: [
        "Quantum collapse event recording",
        "Consciousness decision provenance tracking",
        "Symbolic event chain verification",
        "Constitutional AI compliance auditing",
        "Real-time drift detection and alerting",
        "Immutable audit trail with quantum signatures"
      ],
      status: "Production Ready",
      version: "v2.1.0", 
      architecture: "Distributed ledger with quantum verification"
    },
    {
      name: "LUKHΛS Cloud Manager",
      agent: "ΛNimbus",
      category: "Multi-Cloud Management", 
      description: "Consciousness-orchestrated multi-cloud deployment with Trinity Framework integration and symbolic resource management.",
      icon: Cloud,
      gradient: "from-cyan-500 to-blue-600",
      features: [
        "Multi-cloud consciousness deployment",
        "Trinity Framework resource orchestration",
        "Symbolic infrastructure as code",
        "AI-powered cost optimization",
        "Quantum-safe inter-cloud communication",
        "Consciousness state synchronization"
      ],
      status: "Active Development",
      version: "v1.5.0",
      architecture: "Kubernetes-native with consciousness extensions"
    },
    {
      name: "LUKHΛS Legacy Manager",
      agent: "LEGΛDO",
      category: "Digital Legacy/Testament",
      description: "Consciousness-aware digital legacy preservation with symbolic memory inheritance and quantum-secure time-locks.",
      icon: Archive,
      gradient: "from-orange-500 to-red-600",
      features: [
        "Consciousness memory preservation",
        "Symbolic legacy encoding and inheritance",
        "Quantum time-locked digital testaments",
        "Multi-generational access control",
        "AI-powered legacy curation",
        "Emotional context preservation"
      ],
      status: "Research Phase",
      version: "v0.3.0",
      architecture: "Distributed preservation with quantum time-locks"
    },
    {
      name: "LUKHΛS Poetic Style",
      agent: "POETICΛ",
      category: "Poetic AI Persona",
      description: "Consciousness-infused poetic AI with symbolic language processing and Trinity Framework creative integration.",
      icon: Feather,
      gradient: "from-pink-500 to-rose-600",
      features: [
        "Consciousness-aware poetic generation",
        "Symbolic language and metaphor creation",
        "Trinity-integrated creative processes",
        "Emotional resonance optimization",
        "Multi-cultural poetic traditions",
        "Collaborative human-AI creativity"
      ],
      status: "Alpha Testing",
      version: "v0.6.0",
      architecture: "Large language model with consciousness extensions"
    },
    {
      name: "LUKHΛS Live ContextDashboard",
      agent: "Λrgus",
      category: "Live Context/AR Dashboard",
      description: "Real-time consciousness visualization with augmented reality Trinity Framework monitoring and symbolic data streams.",
      icon: Monitor,
      gradient: "from-yellow-500 to-orange-600", 
      features: [
        "Real-time Trinity Framework monitoring",
        "AR consciousness state visualization",
        "Symbolic data stream interpretation",
        "Multi-dimensional context awareness",
        "Quantum state holographic display",
        "Collaborative consciousness sharing"
      ],
      status: "Prototype",
      version: "v0.4.0",
      architecture: "WebXR with Three.js consciousness rendering"
    }
  ]

  const ecosystemMetrics = [
    { label: "Λ Products", value: "7", description: "Integrated consciousness tools" },
    { label: "Symbolic Processing", value: "2.4M", description: "Operations per second" },
    { label: "Quantum Security", value: "100%", description: "Post-quantum resistant" },
    { label: "Trinity Integration", value: "Complete", description: "Identity • Consciousness • Guardian" }
  ]

  const architectureFeatures = [
    {
      title: "Symbolic Lambda Processing",
      description: "Universal Λ notation for consciousness-aware computation",
      icon: Layers,
      details: ["GLYPH symbolic protocol", "Lambda calculus extensions", "Consciousness primitives"]
    },
    {
      title: "Trinity Framework Core",
      description: "Identity, Consciousness, and Guardian integration",
      icon: Shield,
      details: ["ΛiD identity management", "Consciousness state sync", "Guardian ethics validation"]
    },
    {
      title: "Quantum-Safe Architecture",
      description: "Post-quantum cryptography and security",
      icon: Lock,
      details: ["CRYSTALS-Kyber encryption", "Quantum key distribution", "Forward secrecy"]
    },
    {
      title: "Distributed Consciousness",
      description: "Multi-node consciousness synchronization",
      icon: Globe,
      details: ["Edge consciousness nodes", "State synchronization", "Consciousness mesh network"]
    }
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
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-600 rounded-full blur-xl opacity-30"></div>
                  <div className="relative w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-3xl font-bold text-white">Λ</span>
                  </div>
                </div>
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">LUKHΛS Λ-Suite</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Seven consciousness-aware tools powered by Lambda symbolic processing,
                Trinity Framework integration, and quantum-safe architecture.
              </p>
            </motion.div>

            {/* Ecosystem Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-20">
              {ecosystemMetrics.map((metric, index) => (
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

        {/* Lambda Products */}
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
                Λ-Product Ecosystem
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Seven specialized tools for consciousness-aware computing and digital life management
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {lambdaProducts.map((product, index) => {
                const IconComponent = product.icon;
                return (
                  <motion.div
                    key={product.name}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-8 rounded-2xl group hover:scale-105 transition-all duration-300"
                  >
                    <div className="flex items-start justify-between mb-6">
                      <div className={`p-4 rounded-2xl bg-gradient-to-r ${product.gradient}`}>
                        <IconComponent className="w-8 h-8 text-white" strokeWidth={1.5} />
                      </div>
                      <div className="text-right">
                        <span className={`px-3 py-1 text-xs rounded-full ${
                          product.status === 'Production Ready' ? 'bg-green-500/20 text-green-400' :
                          product.status === 'Beta Testing' ? 'bg-blue-500/20 text-blue-400' :
                          product.status === 'Active Development' ? 'bg-yellow-500/20 text-yellow-400' :
                          product.status === 'Alpha Testing' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-purple-500/20 text-purple-400'
                        }`}>
                          {product.status}
                        </span>
                        <div className="text-xs text-primary-light/60 mt-1">{product.version}</div>
                      </div>
                    </div>
                    
                    <h3 className="font-semibold text-2xl text-trinity-consciousness mb-2">
                      {product.name}
                    </h3>
                    <div className="flex items-center space-x-2 mb-4">
                      <span className="text-sm px-2 py-1 bg-white/10 rounded font-mono">
                        {product.agent}
                      </span>
                      <span className="text-sm text-primary-light/60">
                        {product.category}
                      </span>
                    </div>
                    
                    <p className="text-primary-light/70 mb-6 leading-relaxed">
                      {product.description}
                    </p>
                    
                    <div className="mb-6">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-trinity-consciousness mb-3">
                        Key Features
                      </h4>
                      <ul className="space-y-2">
                        {product.features.slice(0, 4).map((feature, idx) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm text-primary-light/60">
                            <Zap className="w-4 h-4 mt-0.5 text-trinity-consciousness flex-shrink-0" strokeWidth={1.5} />
                            <span>{feature}</span>
                          </li>
                        ))}
                        {product.features.length > 4 && (
                          <li className="text-xs text-primary-light/40 ml-6">
                            +{product.features.length - 4} more features
                          </li>
                        )}
                      </ul>
                    </div>
                    
                    <div className="pt-4 border-t border-primary-light/10">
                      <p className="text-xs text-primary-light/50 italic mb-4">
                        {product.architecture}
                      </p>
                      <div className="flex items-center justify-between">
                        <button className="text-trinity-consciousness hover:text-trinity-consciousness/80 text-sm flex items-center space-x-1">
                          <span>Learn More</span>
                          <ArrowRight className="w-3 h-3" strokeWidth={1.5} />
                        </button>
                        {product.status === 'Production Ready' && (
                          <button className="text-green-400 hover:text-green-300 text-sm flex items-center space-x-1">
                            <Download className="w-3 h-3" strokeWidth={1.5} />
                            <span>Download</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Architecture Features */}
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
                Λ-Architecture Foundation
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Unified symbolic processing architecture powering all Lambda products
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {architectureFeatures.map((feature, index) => {
                const IconComponent = feature.icon;
                return (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-6 rounded-xl text-center"
                  >
                    <div className="inline-flex p-3 rounded-full bg-trinity-consciousness/20 mb-4">
                      <IconComponent className="w-6 h-6 text-trinity-consciousness" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-medium text-lg mb-3">{feature.title}</h3>
                    <p className="text-sm text-primary-light/70 mb-4">
                      {feature.description}
                    </p>
                    <ul className="space-y-1">
                      {feature.details.map((detail, idx) => (
                        <li key={idx} className="text-xs text-trinity-consciousness">
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

        {/* Integration Ecosystem */}
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
                Λ-Integration Ecosystem
              </h2>
              
              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-identity/20 mb-4">
                    <Activity className="w-8 h-8 text-trinity-identity" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Consciousness Sync</h3>
                  <p className="text-sm text-primary-light/70">
                    All Lambda products share consciousness state through Trinity Framework 
                    integration and symbolic protocol synchronization.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-consciousness/20 mb-4">
                    <Database className="w-8 h-8 text-trinity-consciousness" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Symbolic Interoperability</h3>
                  <p className="text-sm text-primary-light/70">
                    Universal Lambda notation enables seamless data exchange and 
                    symbolic meaning preservation across all products.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-guardian/20 mb-4">
                    <Shield className="w-8 h-8 text-trinity-guardian" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Unified Ethics</h3>
                  <p className="text-sm text-primary-light/70">
                    Guardian System provides consistent ethical governance and 
                    drift detection across the entire Lambda product ecosystem.
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
                Experience Consciousness Computing
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Join the Lambda ecosystem and experience consciousness-aware computing 
                with symbolic processing, Trinity Framework integration, and quantum-safe architecture.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/console">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-blue-400 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                  >
                    Access Λ-Console
                  </motion.button>
                </Link>
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                  >
                    Λ Documentation
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