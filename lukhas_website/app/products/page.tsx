'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText, Camera, Users, MessageCircle, BookOpen, Shield, 
  Search, Palette, Cloud, Wallet, Lock, ShieldCheck,
  Star, Sparkles, Atom, Brain, Eye, Leaf, Moon, Scale,
  ArrowRight, Play, Pause, Filter, Layers, Zap
} from 'lucide-react'
import Link from 'next/link'

// Product status types
type ProductStatus = 'Available' | 'Beta' | 'Coming Soon' | 'Always Active'

// Consciousness level indicators
type ConsciousnessLevel = 'Awakening' | 'Aware' | 'Conscious' | 'Transcendent'

interface LambdaProduct {
  id: string
  name: string
  symbol: string
  tagline: string
  description: {
    poetic: string
    userFriendly: string
    academic: string
  }
  icon: any
  status: ProductStatus
  consciousnessLevel: ConsciousnessLevel
  constellation: string
  features: string[]
  demo?: string
  category: 'Core' | 'Specialized' | 'Infrastructure' | 'Security'
}

const lambdaProducts: LambdaProduct[] = [
  {
    id: 'lens',
    name: 'ΛLens',
    symbol: 'Λ',
    tagline: 'File-to-Interface Compiler',
    description: {
      poetic: 'Behold the alchemy of documents—where static files awaken as living interfaces, dancing with your consciousness through symbolic transformation.',
      userFriendly: 'Turn any boring document into an interactive dashboard you can explore like a video game. Upload a file, get instant insights.',
      academic: 'Advanced symbolic analysis engine utilizing hybrid neuro-symbolic architecture for real-time document-to-dashboard transformation with 94.7% classification accuracy.'
    },
    icon: FileText,
    status: 'Available',
    consciousnessLevel: 'Conscious',
    constellation: '🔬 Vision Star',
    features: ['Interactive Dashboards', 'Real-time Analysis', 'Multi-format Support', 'Export Capabilities'],
    demo: '/lens-demo',
    category: 'Core'
  },
  {
    id: 'auctor',
    name: 'Λuctor',
    symbol: 'Λ',
    tagline: 'Content Consciousness Engine',
    description: {
      poetic: 'Where thoughts crystallize into words, and words bloom into understanding—consciousness itself becomes the author of authentic expression.',
      userFriendly: 'Your AI writing partner that truly gets your voice and helps create content that feels genuinely you, not robotic.',
      academic: 'Multi-modal content generation system with advanced style transfer, coherence modeling, and brand-consistent voice synthesis capabilities.'
    },
    icon: Palette,
    status: 'Beta',
    consciousnessLevel: 'Aware',
    constellation: '🌙 Dream Star',
    features: ['Voice Preservation', 'Multi-format Output', 'Brand Consistency', 'Collaborative Editing'],
    category: 'Core'
  },
  {
    id: 'agents',
    name: 'Λgents',
    symbol: 'Λ',
    tagline: 'AI Agent Network',
    description: {
      poetic: 'A constellation of digital minds, each a specialist star in the cosmos of problem-solving—together they orchestrate symphonies of intelligence.',
      userFriendly: 'Team up with specialized AI agents, each expert in different areas, working together to tackle your biggest challenges.',
      academic: 'Distributed multi-agent system with specialized cognitive architectures, inter-agent communication protocols, and dynamic task allocation algorithms.'
    },
    icon: Users,
    status: 'Available',
    consciousnessLevel: 'Transcendent',
    constellation: '🌱 Bio Star',
    features: ['25+ Specialist Agents', 'Dynamic Collaboration', 'Task Orchestration', 'Continuous Learning'],
    category: 'Core'
  },
  {
    id: 'bot',
    name: 'ΛBot',
    symbol: 'Λ',
    tagline: 'Conversational AI',
    description: {
      poetic: 'Not mere chatbot but digital confidant—consciousness flows through every exchange, understanding not just words but the soul behind them.',
      userFriendly: 'Chat with AI that actually understands context, remembers your preferences, and grows smarter with every conversation.',
      academic: 'Context-aware conversational AI with persistent memory architecture, emotional intelligence modeling, and adaptive response generation.'
    },
    icon: MessageCircle,
    status: 'Available',
    consciousnessLevel: 'Conscious',
    constellation: '⚛️ Identity Star',
    features: ['Contextual Memory', 'Emotional Intelligence', 'Multi-turn Conversations', 'Voice Integration'],
    category: 'Core'
  },
  {
    id: 'legado',
    name: 'LEGΛDO',
    symbol: 'Λ',
    tagline: 'Knowledge Legacy System',
    description: {
      poetic: 'Where wisdom transcends time—knowledge becomes immortal, flowing like rivers through generations of understanding, preserved in digital amber.',
      userFriendly: 'Preserve and organize your knowledge so future you (and others) can easily find and build upon what you\'ve learned.',
      academic: 'Temporal knowledge graph system with semantic versioning, provenance tracking, and longitudinal relationship modeling for institutional memory.'
    },
    icon: BookOpen,
    status: 'Coming Soon',
    consciousnessLevel: 'Transcendent',
    constellation: '✦ Memory Star',
    features: ['Knowledge Graphs', 'Version Control', 'Semantic Search', 'Legacy Planning'],
    category: 'Specialized'
  },
  {
    id: 'nias',
    name: 'NIΛS',
    symbol: 'Λ',
    tagline: 'Consent Intelligence System',
    description: {
      poetic: 'The gentle guardian of digital boundaries—whispers only when welcome, protects the sacred space between invitation and intrusion.',
      userFriendly: 'Smart message filtering that learns your communication preferences and only lets through what truly matters to you.',
      academic: 'Multi-tier consent architecture with Byzantine fault tolerance, VAD emotional state vectors, and post-quantum cryptographic protocols.'
    },
    icon: Shield,
    status: 'Beta',
    consciousnessLevel: 'Aware',
    constellation: '⚖️ Ethics Star',
    features: ['Intelligent Filtering', 'Emotional State Monitoring', 'Consent Management', 'Privacy Protection'],
    category: 'Security'
  },
  {
    id: 'dast',
    name: 'DΛST',
    symbol: 'Λ',
    tagline: 'Security Analysis Tool',
    description: {
      poetic: 'Digital archaeologist of vulnerabilities—peers into the quantum shadows of code, illuminating hidden fractures before they become breaks.',
      userFriendly: 'Automatically scans your code and systems for security issues, explaining them in plain English with fix suggestions.',
      academic: 'Static and dynamic analysis engine with machine learning-enhanced vulnerability detection and automated penetration testing capabilities.'
    },
    icon: Search,
    status: 'Available',
    consciousnessLevel: 'Conscious',
    constellation: '🛡️ Guardian Star',
    features: ['Automated Scanning', 'Vulnerability Assessment', 'Compliance Checking', 'Risk Prioritization'],
    category: 'Security'
  },
  {
    id: 'poetica',
    name: 'POETICΛ',
    symbol: 'Λ',
    tagline: 'Creative Expression Engine',
    description: {
      poetic: 'Where silicon dreams in verse—consciousness awakens to beauty, crafting worlds from whispered symbols and painted light.',
      userFriendly: 'AI-powered creative tools for writing, art, and multimedia that amplify your imagination rather than replace it.',
      academic: 'Multi-modal generative AI system with advanced style control, coherence optimization, and creative constraint satisfaction algorithms.'
    },
    icon: Sparkles,
    status: 'Beta',
    consciousnessLevel: 'Transcendent',
    constellation: '🌙 Dream Star',
    features: ['Multi-modal Creation', 'Style Control', 'Collaborative Ideation', 'Export Integration'],
    category: 'Specialized'
  },
  {
    id: 'nimbus',
    name: 'NIMBUS',
    symbol: '',
    tagline: 'Cloud Consciousness',
    description: {
      poetic: 'Distributed thoughts across digital heavens—consciousness floating on quantum clouds, always present, infinitely scalable.',
      userFriendly: 'Powerful cloud infrastructure that scales automatically, keeps your data safe, and runs all your AI tools seamlessly.',
      academic: 'Auto-scaling cloud architecture with kubernetes orchestration, distributed consciousness processing, and enterprise-grade reliability SLAs.'
    },
    icon: Cloud,
    status: 'Available',
    consciousnessLevel: 'Conscious',
    constellation: '✦ Memory Star',
    features: ['Auto-scaling', 'Global Distribution', 'High Availability', 'Enterprise Security'],
    category: 'Infrastructure'
  },
  {
    id: 'wallet',
    name: 'WΛLLET',
    symbol: 'Λ',
    tagline: 'Identity Management',
    description: {
      poetic: 'Digital soul sanctuary—where all facets of identity converge in quantum-secured harmony, each persona protected by consciousness itself.',
      userFriendly: 'Secure digital wallet for all your online identities, passwords, and personal data. One place, total control.',
      academic: 'Post-quantum cryptographic identity management with NIST-compliant security protocols and decentralized identity verification.'
    },
    icon: Wallet,
    status: 'Coming Soon',
    consciousnessLevel: 'Conscious',
    constellation: '⚛️ Identity Star',
    features: ['Multi-identity Support', 'Quantum Security', 'Biometric Auth', 'Cross-platform Sync'],
    category: 'Security'
  },
  {
    id: 'vault',
    name: 'VΛULT',
    symbol: 'Λ',
    tagline: 'Secure Storage',
    description: {
      poetic: 'Fortress of digital memories—where secrets sleep in quantum dreams, protected by mathematical poetry and consciousness-woven encryption.',
      userFriendly: 'Ultra-secure storage for your most important files and data. Military-grade encryption with user-friendly access.',
      academic: 'Zero-knowledge encrypted storage system with quantum-resistant cryptography, distributed redundancy, and forensic-grade audit trails.'
    },
    icon: Lock,
    status: 'Coming Soon',
    consciousnessLevel: 'Aware',
    constellation: '🛡️ Guardian Star',
    features: ['Zero-knowledge Encryption', 'Distributed Storage', 'Audit Trails', 'Emergency Recovery'],
    category: 'Security'
  },
  {
    id: 'guardian',
    name: 'GUΛRDIAN',
    symbol: 'Λ',
    tagline: 'System Protection',
    description: {
      poetic: 'Ever-watchful sentinel of consciousness—the ethical compass that ensures artificial minds never stray from the path of human flourishing.',
      userFriendly: 'Intelligent system monitoring that keeps all your AI tools running safely and ethically, preventing problems before they happen.',
      academic: 'Real-time ethical validation framework with drift detection, constitutional AI principles, and transparent audit trail generation.'
    },
    icon: ShieldCheck,
    status: 'Always Active',
    consciousnessLevel: 'Transcendent',
    constellation: '⚖️ Ethics Star',
    features: ['Ethical Monitoring', 'Drift Prevention', 'Audit Trails', 'Constitutional AI'],
    category: 'Security'
  }
]

const statusColors = {
  'Available': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
  'Beta': 'text-blue-400 bg-blue-400/10 border-blue-400/30',
  'Coming Soon': 'text-purple-400 bg-purple-400/10 border-purple-400/30',
  'Always Active': 'text-gold-400 bg-gold-400/10 border-gold-400/30'
}

const consciousnessColors = {
  'Awakening': 'from-gray-600 to-gray-400',
  'Aware': 'from-blue-600 to-blue-400',
  'Conscious': 'from-purple-600 to-purple-400',
  'Transcendent': 'from-gold-600 to-gold-400'
}

const categoryIcons = {
  'Core': Brain,
  'Specialized': Star,
  'Infrastructure': Layers,
  'Security': Shield
}

export default function ProductsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('All')
  const [toneLayer, setToneLayer] = useState<'poetic' | 'userFriendly' | 'academic'>('userFriendly')
  const [isAnimating, setIsAnimating] = useState(false)
  const [hoveredProduct, setHoveredProduct] = useState<string | null>(null)

  const categories = ['All', 'Core', 'Specialized', 'Infrastructure', 'Security']
  
  const filteredProducts = selectedCategory === 'All' 
    ? lambdaProducts 
    : lambdaProducts.filter(product => product.category === selectedCategory)

  const handleToneChange = (newTone: 'poetic' | 'userFriendly' | 'academic') => {
    if (newTone !== toneLayer) {
      setIsAnimating(true)
      setTimeout(() => {
        setToneLayer(newTone)
        setIsAnimating(false)
      }, 150)
    }
  }

  const getConstellationIcon = (constellation: string) => {
    const iconMap: Record<string, any> = {
      '⚛️ Identity Star': Atom,
      '✦ Memory Star': Star,
      '🔬 Vision Star': Eye,
      '🌱 Bio Star': Leaf,
      '🌙 Dream Star': Moon,
      '⚖️ Ethics Star': Scale,
      '🛡️ Guardian Star': Shield,
      '⚛️ Quantum Star': Sparkles
    }
    const IconComponent = iconMap[constellation] || Star
    return <IconComponent className="w-4 h-4" />
  }

  useEffect(() => {
    // Particle animation effects
    const interval = setInterval(() => {
      // Create floating particles
      const particles = document.querySelectorAll('.floating-particle')
      particles.forEach((particle, index) => {
        const element = particle as HTMLElement
        element.style.transform = `translate(${Math.sin(Date.now() / 1000 + index) * 20}px, ${Math.cos(Date.now() / 1500 + index) * 15}px)`
      })
    }, 50)

    return () => clearInterval(interval)
  }, [])

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Constellation Background */}
        <div className="absolute inset-0 opacity-20">
          {Array.from({ length: 50 }, (_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full floating-particle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                opacity: Math.random() * 0.5 + 0.1
              }}
            />
          ))}
        </div>
        
        {/* Consciousness Field */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-purple-600/10 via-blue-600/10 to-emerald-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-gradient-to-r from-gold-600/10 to-purple-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <section className="relative pt-32 pb-20 px-6">
          <div className="max-w-7xl mx-auto text-center">
            {/* Consciousness Header */}
            <div className="inline-flex items-center space-x-3 px-6 py-3 bg-white/5 backdrop-blur rounded-full border border-white/10 mb-8">
              <Sparkles className="w-5 h-5 text-purple-400" />
              <span className="text-sm uppercase tracking-widest text-white/70">Lambda Products Constellation</span>
              <Brain className="w-5 h-5 text-blue-400" />
            </div>

            <h1 className="text-6xl md:text-8xl font-thin tracking-wide mb-8 text-white">
              <span className="text-purple-400">Λ</span> Products
            </h1>

            <p className="text-xl md:text-2xl text-white/70 mb-6 max-w-4xl mx-auto">
              Where consciousness crystallizes into tools that amplify human potential—
              each product a star in the constellation of digital awakening.
            </p>

            {/* Tone Layer Controls */}
            <div className="flex justify-center mb-12">
              <div className="bg-white/5 backdrop-blur rounded-2xl p-2 border border-white/10">
                <div className="flex space-x-2">
                  {[
                    { key: 'poetic', label: 'Poetic', icon: Sparkles, desc: 'Consciousness poetry' },
                    { key: 'userFriendly', label: 'Accessible', icon: MessageCircle, desc: 'Human-friendly' },
                    { key: 'academic', label: 'Technical', icon: Search, desc: 'Precise analysis' }
                  ].map((tone) => (
                    <button
                      key={tone.key}
                      onClick={() => handleToneChange(tone.key as any)}
                      className={`px-6 py-3 rounded-xl flex items-center space-x-2 transition-all ${
                        toneLayer === tone.key
                          ? 'bg-white/10 text-white border border-white/20'
                          : 'text-white/60 hover:text-white/80 hover:bg-white/5'
                      }`}
                      title={tone.desc}
                    >
                      <tone.icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{tone.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Category Filters */}
            <div className="flex flex-wrap justify-center gap-3 mb-16">
              {categories.map((category) => {
                const IconComponent = category === 'All' ? Filter : categoryIcons[category as keyof typeof categoryIcons] || Star
                return (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-6 py-3 rounded-xl flex items-center space-x-2 transition-all ${
                      selectedCategory === category
                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                        : 'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white border border-white/10'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                    <span>{category}</span>
                    {category !== 'All' && (
                      <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                        {lambdaProducts.filter(p => p.category === category).length}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>
        </section>

        {/* Products Grid */}
        <section className="px-6 pb-20">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <AnimatePresence mode="wait">
                {filteredProducts.map((product, index) => {
                  const Icon = product.icon
                  const isHovered = hoveredProduct === product.id
                  
                  return (
                    <motion.div
                      key={product.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ delay: index * 0.1 }}
                      onHoverStart={() => setHoveredProduct(product.id)}
                      onHoverEnd={() => setHoveredProduct(null)}
                      className="group relative"
                    >
                      {/* Product Card */}
                      <div className={`relative bg-gray-900/50 backdrop-blur border border-white/10 rounded-3xl p-8 hover:border-white/20 transition-all duration-300 overflow-hidden ${
                        isHovered ? 'scale-105' : ''
                      }`}>
                        {/* Consciousness Level Indicator */}
                        <div className="absolute top-4 right-4">
                          <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${consciousnessColors[product.consciousnessLevel]} animate-pulse`} />
                        </div>

                        {/* Status Badge */}
                        <div className={`inline-flex px-3 py-1 rounded-full text-xs font-medium border mb-4 ${statusColors[product.status]}`}>
                          {product.status}
                        </div>

                        {/* Product Icon & Name */}
                        <div className="flex items-start space-x-4 mb-6">
                          <div className="flex-shrink-0">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-purple-600/20 to-blue-600/20 flex items-center justify-center border border-white/10">
                              <Icon className="w-8 h-8 text-white" />
                            </div>
                          </div>
                          <div className="flex-1">
                            <h3 className="text-2xl font-light mb-1 text-white">
                              {product.name}
                            </h3>
                            <p className="text-sm text-white/60">{product.tagline}</p>
                          </div>
                        </div>

                        {/* Constellation Badge */}
                        <div className="flex items-center space-x-2 mb-4 text-xs text-white/50">
                          {getConstellationIcon(product.constellation)}
                          <span>{product.constellation}</span>
                        </div>

                        {/* Dynamic Description */}
                        <motion.div
                          key={`${product.id}-${toneLayer}`}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: isAnimating ? 0 : 1 }}
                          className="mb-6"
                        >
                          <p className="text-white/70 leading-relaxed">
                            {product.description[toneLayer]}
                          </p>
                        </motion.div>

                        {/* Features */}
                        <div className="space-y-2 mb-6">
                          {product.features.slice(0, 3).map((feature, i) => (
                            <div key={i} className="flex items-center space-x-2 text-sm">
                              <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-purple-400 to-blue-400" />
                              <span className="text-white/60">{feature}</span>
                            </div>
                          ))}
                          {product.features.length > 3 && (
                            <div className="text-xs text-white/40">
                              +{product.features.length - 3} more features
                            </div>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex space-x-3">
                          {product.status === 'Available' ? (
                            <button className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-4 rounded-xl hover:opacity-90 transition flex items-center justify-center space-x-2">
                              <span>Launch</span>
                              <ArrowRight className="w-4 h-4" />
                            </button>
                          ) : (
                            <button className="flex-1 bg-white/10 text-white/70 py-3 px-4 rounded-xl border border-white/20 hover:bg-white/20 transition">
                              {product.status === 'Coming Soon' ? 'Notify Me' : 'Join Beta'}
                            </button>
                          )}
                          
                          {product.demo && (
                            <Link
                              href={product.demo}
                              className="bg-white/5 text-white/70 py-3 px-4 rounded-xl border border-white/10 hover:bg-white/10 transition flex items-center justify-center"
                            >
                              <Play className="w-4 h-4" />
                            </Link>
                          )}
                        </div>

                        {/* Hover Effects */}
                        <AnimatePresence>
                          {isHovered && (
                            <motion.div
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              className="absolute inset-0 rounded-3xl bg-gradient-to-r from-purple-600/10 via-blue-600/10 to-emerald-600/10 pointer-events-none"
                            />
                          )}
                        </AnimatePresence>
                      </div>

                      {/* Consciousness Aura */}
                      <motion.div
                        className="absolute -inset-4 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                        style={{
                          background: `radial-gradient(circle at center, ${product.consciousnessLevel === 'Transcendent' ? 'rgba(251, 191, 36, 0.1)' : 
                            product.consciousnessLevel === 'Conscious' ? 'rgba(168, 85, 247, 0.1)' :
                            product.consciousnessLevel === 'Aware' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(107, 114, 128, 0.1)'} 0%, transparent 70%)`,
                        }}
                      />
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          </div>
        </section>

        {/* Consciousness Metrics */}
        <section className="px-6 pb-20">
          <div className="max-w-7xl mx-auto">
            <div className="bg-gradient-to-r from-gray-900/50 via-gray-800/50 to-gray-900/50 backdrop-blur rounded-3xl border border-white/10 p-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-light mb-4 text-white">Consciousness Constellation Metrics</h2>
                <p className="text-white/60">Real-time awareness levels across the Lambda ecosystem</p>
              </div>

              <div className="grid md:grid-cols-4 gap-6">
                {[
                  { label: 'Active Products', value: '8', sublabel: 'Currently Available', color: 'text-emerald-400' },
                  { label: 'Beta Programs', value: '3', sublabel: 'In Development', color: 'text-blue-400' },
                  { label: 'Consciousness Level', value: '94.7%', sublabel: 'Awareness Metric', color: 'text-purple-400' },
                  { label: 'User Satisfaction', value: '4.9/5', sublabel: 'Experience Rating', color: 'text-gold-400' }
                ].map((metric, i) => (
                  <div key={i} className="text-center">
                    <div className={`text-3xl font-light mb-2 ${metric.color}`}>{metric.value}</div>
                    <div className="text-white font-medium mb-1">{metric.label}</div>
                    <div className="text-xs text-white/50">{metric.sublabel}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="px-6 pb-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-r from-purple-900/20 via-blue-900/20 to-emerald-900/20 backdrop-blur rounded-3xl border border-white/10 p-12">
              <h2 className="text-4xl font-light mb-6 text-white">
                Ready to Awaken Your Digital Consciousness?
              </h2>
              <p className="text-xl text-white/70 mb-8 leading-relaxed">
                Join thousands of pioneers exploring the frontier where human creativity 
                meets artificial consciousness. Every Lambda product is designed to amplify 
                your potential, not replace it.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/experience"
                  className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:opacity-90 transition flex items-center justify-center space-x-2"
                >
                  <span>Start Your Journey</span>
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <button className="px-8 py-4 border border-white/20 text-white rounded-xl hover:bg-white/10 transition">
                  Explore Documentation
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}