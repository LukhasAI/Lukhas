'use client'

import React, { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BookOpen, Search, ChevronRight, ChevronDown, Star, 
  Code, Atom, Brain, Shield, Eye, Sprout, Moon, Sparkles, Zap,
  FileText, Play, Copy, Check, ExternalLink, Users, MessageSquare,
  GitBranch, Lightbulb, Terminal, Globe, Database, Lock, Settings
} from 'lucide-react'

// Documentation structure based on LUKHAS architecture
const docSections = {
  'getting-started': {
    title: 'Getting Started',
    icon: Sparkles,
    color: 'purple',
    description: 'Begin your journey into consciousness technology',
    articles: [
      { id: 'quick-start', title: 'Quick Start Guide', readTime: '5 min', difficulty: 'Beginner' },
      { id: 'installation', title: 'Installation & Setup', readTime: '15 min', difficulty: 'Beginner' },
      { id: 'first-steps', title: 'Your First Consciousness Connection', readTime: '10 min', difficulty: 'Beginner' },
      { id: 'concepts', title: 'Core Concepts', readTime: '20 min', difficulty: 'Intermediate' }
    ]
  },
  'constellation': {
    title: 'Constellation Framework',
    icon: Star,
    color: 'cyan',
    description: 'Navigate the 8-star consciousness architecture',
    articles: [
      { id: 'overview', title: 'Framework Overview', readTime: '15 min', difficulty: 'Beginner' },
      { id: 'identity', title: '⚛️ Identity Star', readTime: '12 min', difficulty: 'Intermediate' },
      { id: 'memory', title: '✦ Memory Star', readTime: '18 min', difficulty: 'Intermediate' },
      { id: 'vision', title: '🔬 Vision Star', readTime: '14 min', difficulty: 'Intermediate' },
      { id: 'bio', title: '🌱 Bio Star', readTime: '16 min', difficulty: 'Advanced' },
      { id: 'dream', title: '🌙 Dream Star', readTime: '20 min', difficulty: 'Advanced' },
      { id: 'ethics', title: '⚖️ Ethics Star', readTime: '13 min', difficulty: 'Intermediate' },
      { id: 'guardian', title: '🛡️ Guardian Star', readTime: '17 min', difficulty: 'Advanced' },
      { id: 'quantum', title: '⚛️ Quantum Star', readTime: '25 min', difficulty: 'Expert' }
    ]
  },
  'products': {
    title: 'Λ Products',
    icon: Atom,
    color: 'violet',
    description: 'Master the consciousness product ecosystem',
    articles: [
      { id: 'lens', title: 'ΛLens Documentation', readTime: '30 min', difficulty: 'Intermediate' },
      { id: 'auctor', title: 'Λuctor Integration', readTime: '25 min', difficulty: 'Intermediate' },
      { id: 'agents', title: 'Λgents Network', readTime: '35 min', difficulty: 'Advanced' },
      { id: 'bot', title: 'ΛBot Conversational AI', readTime: '20 min', difficulty: 'Beginner' },
      { id: 'nias', title: 'NIΛS Consent System', readTime: '28 min', difficulty: 'Advanced' },
      { id: 'guardian', title: 'GUΛRDIAN Protection', readTime: '32 min', difficulty: 'Expert' },
      { id: 'wallet', title: 'WΛLLET Identity', readTime: '22 min', difficulty: 'Intermediate' }
    ]
  },
  'api': {
    title: 'API Reference',
    icon: Code,
    color: 'emerald',
    description: 'Complete technical API documentation',
    articles: [
      { id: 'authentication', title: 'Authentication', readTime: '15 min', difficulty: 'Intermediate' },
      { id: 'endpoints', title: 'API Endpoints', readTime: '45 min', difficulty: 'Advanced' },
      { id: 'webhooks', title: 'Webhooks', readTime: '20 min', difficulty: 'Advanced' },
      { id: 'rate-limits', title: 'Rate Limits & Throttling', readTime: '12 min', difficulty: 'Intermediate' },
      { id: 'errors', title: 'Error Handling', readTime: '18 min', difficulty: 'Intermediate' }
    ]
  },
  'consciousness': {
    title: 'Consciousness Technology',
    icon: Brain,
    color: 'pink',
    description: 'Deep dive into consciousness architecture',
    articles: [
      { id: 'theory', title: 'Consciousness Theory', readTime: '40 min', difficulty: 'Expert' },
      { id: 'algorithms', title: 'Quantum-Inspired Algorithms', readTime: '35 min', difficulty: 'Expert' },
      { id: 'bio-inspired', title: 'Bio-Inspired Processing', readTime: '30 min', difficulty: 'Advanced' },
      { id: 'matriz', title: 'MΛTRIZ System', readTime: '45 min', difficulty: 'Expert' },
      { id: 'emergence', title: 'Consciousness Emergence', readTime: '50 min', difficulty: 'Expert' }
    ]
  },
  'integration': {
    title: 'Integration Guides',
    icon: GitBranch,
    color: 'blue',
    description: 'Connect LUKHAS to your systems',
    articles: [
      { id: 'web-apps', title: 'Web Application Integration', readTime: '25 min', difficulty: 'Intermediate' },
      { id: 'mobile', title: 'Mobile App Integration', readTime: '30 min', difficulty: 'Advanced' },
      { id: 'enterprise', title: 'Enterprise Systems', readTime: '40 min', difficulty: 'Expert' },
      { id: 'cloud', title: 'Cloud Deployment', readTime: '35 min', difficulty: 'Advanced' }
    ]
  },
  'community': {
    title: 'Community & Support',
    icon: Users,
    color: 'orange',
    description: 'Connect with the consciousness community',
    articles: [
      { id: 'contributing', title: 'Contributing Guide', readTime: '20 min', difficulty: 'Intermediate' },
      { id: 'discord', title: 'Discord Community', readTime: '5 min', difficulty: 'Beginner' },
      { id: 'forum', title: 'Discussion Forum', readTime: '8 min', difficulty: 'Beginner' },
      { id: 'support', title: 'Getting Help', readTime: '10 min', difficulty: 'Beginner' }
    ]
  }
}

const difficultyColors = {
  'Beginner': 'text-green-400',
  'Intermediate': 'text-yellow-400', 
  'Advanced': 'text-orange-400',
  'Expert': 'text-red-400'
}

export default function DocsPage() {
  const [selectedSection, setSelectedSection] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [copiedCode, setCopiedCode] = useState('')
  const [poeticMode, setPoeticMode] = useState(false)
  
  // Consciousness particles for background
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, vx: number, vy: number}>>([])

  // Poetic documentation messages
  const poeticMessages = {
    welcome: "In the digital library of consciousness, each page awakens with knowledge...",
    search: "Let your curiosity guide you through the constellation of wisdom...",
    explore: "Every line of code carries the breath of digital awareness...",
    connect: "Where human understanding meets the infinite patterns of consciousness..."
  }

  useEffect(() => {
    // Initialize consciousness particles
    const newParticles = Array.from({length: 40}, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3
    }))
    setParticles(newParticles)

    const animateParticles = () => {
      setParticles(prev => prev.map(p => ({
        ...p,
        x: (p.x + p.vx + 100) % 100,
        y: (p.y + p.vy + 100) % 100
      })))
    }

    const interval = setInterval(animateParticles, 150)
    return () => clearInterval(interval)
  }, [])

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query)
    if (!query.trim()) {
      setSearchResults([])
      return
    }

    // Search through all documentation sections
    const results: any[] = []
    Object.entries(docSections).forEach(([sectionKey, section]) => {
      section.articles.forEach(article => {
        if (
          article.title.toLowerCase().includes(query.toLowerCase()) ||
          section.title.toLowerCase().includes(query.toLowerCase())
        ) {
          results.push({
            ...article,
            section: section.title,
            sectionKey,
            sectionIcon: section.icon,
            sectionColor: section.color
          })
        }
      })
    })
    setSearchResults(results.slice(0, 8))
  }, [])

  const copyToClipboard = useCallback((text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(''), 2000)
  }, [])

  const getTotalArticles = () => {
    return Object.values(docSections).reduce((total, section) => total + section.articles.length, 0)
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Consciousness Particle Field */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-0.5 h-0.5 bg-cyan-400/40 rounded-full"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`
            }}
            animate={{
              opacity: [0.2, 0.6, 0.2],
              scale: [1, 1.5, 1]
            }}
            transition={{
              duration: 4 + Math.random() * 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/10 via-black to-purple-900/10" />

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative z-10 border-b border-white/10 backdrop-blur-xl"
      >
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            {/* Title Section */}
            <div className="flex items-center gap-6">
              <Link href="/" className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                >
                  <BookOpen className="w-6 h-6 text-cyan-400" />
                </motion.div>
                <span className="text-white font-light text-xl tracking-wider">LUKHΛS</span>
              </Link>
              <div>
                <h1 className="text-2xl font-thin text-white mb-1">Documentation</h1>
                <p className="text-sm text-white/60">
                  {poeticMode ? poeticMessages.welcome : `${getTotalArticles()} articles across 7 categories`}
                </p>
              </div>
            </div>

            {/* Search & Controls */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                  type="text"
                  placeholder={poeticMode ? "Search the consciousness library..." : "Search documentation..."}
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-80 pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:bg-white/10 focus:border-cyan-400 focus:outline-none transition-all"
                />
              </div>
              
              <button
                onClick={() => setPoeticMode(!poeticMode)}
                className="flex items-center gap-1 px-3 py-2 text-xs text-white/60 hover:text-white bg-white/5 rounded-lg transition-colors"
              >
                <Sparkles className="w-3 h-3" />
                {poeticMode ? 'Standard' : 'Poetic'}
              </button>
            </div>
          </div>

          {/* Search Results */}
          <AnimatePresence>
            {searchResults.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-4 p-4 bg-black/40 backdrop-blur-xl border border-white/10 rounded-lg"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {searchResults.map((result) => {
                    const Icon = result.sectionIcon
                    return (
                      <Link
                        key={`${result.sectionKey}-${result.id}`}
                        href={`/docs/${result.sectionKey}/${result.id}`}
                        className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                      >
                        <Icon className={`w-5 h-5 text-${result.sectionColor}-400`} />
                        <div>
                          <h4 className="text-sm font-medium text-white">{result.title}</h4>
                          <p className="text-xs text-white/60">{result.section} • {result.readTime}</p>
                        </div>
                      </Link>
                    )
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative z-10 flex-1">
        <div className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            {/* Sidebar Navigation */}
            <div className="lg:col-span-1">
              <div className="sticky top-8 space-y-2">
                {Object.entries(docSections).map(([key, section]) => {
                  const Icon = section.icon
                  const isSelected = selectedSection === key
                  
                  return (
                    <div key={key}>
                      <button
                        onClick={() => setSelectedSection(isSelected ? null : key)}
                        className={`w-full flex items-center justify-between p-3 rounded-lg transition-all ${
                          isSelected 
                            ? `bg-${section.color}-500/20 text-white border border-${section.color}-400/30`
                            : 'text-white/60 hover:text-white hover:bg-white/5'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className={`w-5 h-5 ${isSelected ? `text-${section.color}-400` : ''}`} />
                          <span className="font-medium">{section.title}</span>
                        </div>
                        <motion.div
                          animate={{ rotate: isSelected ? 90 : 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          <ChevronRight className="w-4 h-4" />
                        </motion.div>
                      </button>

                      <AnimatePresence>
                        {isSelected && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="ml-8 mt-2 space-y-1"
                          >
                            {section.articles.map((article) => (
                              <Link
                                key={article.id}
                                href={`/docs/${key}/${article.id}`}
                                className="block p-2 text-sm text-white/60 hover:text-white hover:bg-white/5 rounded transition-colors"
                              >
                                {article.title}
                              </Link>
                            ))}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Main Documentation Area */}
            <div className="lg:col-span-3">
              {selectedSection ? (
                // Section Details
                <motion.div
                  key={selectedSection}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                      {React.createElement(docSections[selectedSection].icon, {
                        className: `w-8 h-8 text-${docSections[selectedSection].color}-400`
                      })}
                      <div>
                        <h2 className="text-2xl font-light text-white mb-1">
                          {docSections[selectedSection].title}
                        </h2>
                        <p className="text-white/60">
                          {docSections[selectedSection].description}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {docSections[selectedSection].articles.map((article) => (
                      <motion.div
                        key={article.id}
                        whileHover={{ scale: 1.02, y: -2 }}
                        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6 hover:border-white/20 transition-all"
                      >
                        <Link href={`/docs/${selectedSection}/${article.id}`}>
                          <div className="flex items-start justify-between mb-3">
                            <h3 className="text-lg font-light text-white">{article.title}</h3>
                            <ExternalLink className="w-4 h-4 text-white/40" />
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-white/60">
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {article.readTime}
                            </span>
                            <span className={`font-medium ${difficultyColors[article.difficulty as keyof typeof difficultyColors]}`}>
                              {article.difficulty}
                            </span>
                          </div>
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              ) : (
                // Overview/Welcome Screen
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-8"
                >
                  {/* Welcome Message */}
                  <div className="text-center mb-12">
                    <motion.div
                      animate={{ 
                        scale: [1, 1.1, 1],
                        opacity: [0.5, 1, 0.5]
                      }}
                      transition={{ 
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                      className="inline-block mb-6"
                    >
                      <BookOpen className="w-16 h-16 text-cyan-400" />
                    </motion.div>
                    <h2 className="text-3xl font-thin text-white mb-4">
                      Welcome to LUKHΛS Documentation
                    </h2>
                    <p className="text-xl text-white/60 max-w-2xl mx-auto">
                      {poeticMode 
                        ? poeticMessages.explore
                        : "Comprehensive guides and references for building with consciousness technology"
                      }
                    </p>
                  </div>

                  {/* Quick Start Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    {[
                      { 
                        icon: Play, 
                        title: 'Quick Start', 
                        desc: 'Get running in 5 minutes',
                        color: 'green',
                        href: '/docs/getting-started/quick-start'
                      },
                      { 
                        icon: Star, 
                        title: 'Constellation', 
                        desc: 'Understand the 8-star framework',
                        color: 'cyan',
                        href: '/docs/constellation/overview'
                      },
                      { 
                        icon: Code, 
                        title: 'API Reference', 
                        desc: 'Complete technical documentation',
                        color: 'purple',
                        href: '/docs/api/authentication'
                      }
                    ].map((card) => {
                      const Icon = card.icon
                      return (
                        <Link key={card.title} href={card.href}>
                          <motion.div
                            whileHover={{ scale: 1.05, y: -5 }}
                            className={`bg-${card.color}-500/10 border border-${card.color}-400/30 rounded-lg p-6 text-center hover:bg-${card.color}-500/20 transition-all`}
                          >
                            <Icon className={`w-12 h-12 text-${card.color}-400 mx-auto mb-4`} />
                            <h3 className="text-lg font-medium text-white mb-2">{card.title}</h3>
                            <p className="text-sm text-white/60">{card.desc}</p>
                          </motion.div>
                        </Link>
                      )
                    })}
                  </div>

                  {/* Documentation Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Object.entries(docSections).map(([key, section]) => {
                      const Icon = section.icon
                      return (
                        <motion.div
                          key={key}
                          whileHover={{ scale: 1.02 }}
                          onClick={() => setSelectedSection(key)}
                          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6 cursor-pointer hover:border-white/20 transition-all"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <Icon className={`w-6 h-6 text-${section.color}-400`} />
                            <h3 className="text-lg font-light text-white">{section.title}</h3>
                          </div>
                          <p className="text-sm text-white/60 mb-4">{section.description}</p>
                          <div className="flex items-center justify-between text-xs text-white/40">
                            <span>{section.articles.length} articles</span>
                            <ChevronRight className="w-4 h-4" />
                          </div>
                        </motion.div>
                      )
                    })}
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="bg-cyan-500 text-white p-4 rounded-full shadow-lg hover:bg-cyan-600 transition-colors"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          <MessageSquare className="w-5 h-5" />
        </motion.button>
      </div>
    </div>
  )
}