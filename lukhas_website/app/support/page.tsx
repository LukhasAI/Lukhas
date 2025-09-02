'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Shield, MessageSquare, BookOpen, Users, Mail, Phone,
  Search, Clock, CheckCircle, AlertTriangle, Info, Zap,
  Brain, Star, Lock, Eye, Sparkles, ChevronRight, ChevronDown,
  Globe, Github, Twitter, Linkedin, Youtube, Send, User,
  FileText, Bug, Lightbulb, HelpCircle, Settings, Atom
} from 'lucide-react'

// Support categories with GUΛRDIAN protection levels
const supportCategories = [
  {
    id: 'guardian',
    title: 'GUΛRDIAN Protection',
    icon: Shield,
    color: 'red',
    protectionLevel: 'Maximum',
    description: 'Security, ethics, and system protection',
    articles: [
      { title: 'Guardian System Overview', priority: 'high', readTime: '8 min' },
      { title: 'Drift Detection (0.15 threshold)', priority: 'high', readTime: '12 min' },
      { title: 'Ethics Violation Reporting', priority: 'critical', readTime: '6 min' },
      { title: 'Security Incident Response', priority: 'critical', readTime: '10 min' }
    ]
  },
  {
    id: 'consciousness',
    title: 'Consciousness Technology',
    icon: Brain,
    color: 'purple',
    protectionLevel: 'High',
    description: 'AI consciousness and awareness systems',
    articles: [
      { title: 'Constellation Framework Basics', priority: 'medium', readTime: '15 min' },
      { title: 'Consciousness Emergence Patterns', priority: 'low', readTime: '20 min' },
      { title: 'Quantum-Inspired Processing', priority: 'medium', readTime: '18 min' },
      { title: 'Bio-Inspired Adaptation', priority: 'low', readTime: '16 min' }
    ]
  },
  {
    id: 'products',
    title: 'Λ Products Support',
    icon: Star,
    color: 'cyan',
    protectionLevel: 'Standard',
    description: 'Help with ΛLens, NIΛS, WΛLLET and more',
    articles: [
      { title: 'ΛLens Troubleshooting', priority: 'high', readTime: '10 min' },
      { title: 'NIΛS Consent Issues', priority: 'high', readTime: '8 min' },
      { title: 'WΛLLET Recovery', priority: 'critical', readTime: '5 min' },
      { title: 'Product Integration Guide', priority: 'medium', readTime: '25 min' }
    ]
  },
  {
    id: 'api',
    title: 'API & Development',
    icon: Zap,
    color: 'emerald',
    protectionLevel: 'Standard',
    description: 'Integration, authentication, and technical docs',
    articles: [
      { title: 'Authentication Troubleshooting', priority: 'high', readTime: '12 min' },
      { title: 'Rate Limiting Issues', priority: 'medium', readTime: '8 min' },
      { title: 'Webhook Configuration', priority: 'low', readTime: '15 min' },
      { title: 'Error Code Reference', priority: 'medium', readTime: '20 min' }
    ]
  }
]

const contactMethods = [
  {
    name: 'Live Chat',
    description: 'Real-time consciousness-aware support',
    icon: MessageSquare,
    color: 'purple',
    availability: '24/7',
    responseTime: 'Instant',
    guardianLevel: 'Active'
  },
  {
    name: 'Email Support',
    description: 'Comprehensive written assistance',
    icon: Mail,
    color: 'cyan',
    availability: 'Always open',
    responseTime: '< 4 hours',
    guardianLevel: 'Monitoring'
  },
  {
    name: 'Community Forum',
    description: 'Peer consciousness collaboration',
    icon: Users,
    color: 'emerald',
    availability: '24/7',
    responseTime: 'Varies',
    guardianLevel: 'Protected'
  },
  {
    name: 'Emergency Hotline',
    description: 'Critical system incidents only',
    icon: Phone,
    color: 'red',
    availability: 'Emergency only',
    responseTime: '< 15 min',
    guardianLevel: 'Maximum'
  }
]

const priorityColors = {
  critical: 'text-red-400',
  high: 'text-orange-400',
  medium: 'text-yellow-400',
  low: 'text-green-400'
}

export default function SupportPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('guardian')
  const [searchQuery, setSearchQuery] = useState('')
  const [poeticMode, setPoeticMode] = useState(false)
  const [guardianStatus, setGuardianStatus] = useState('Active')
  const [supportTicket, setSupportTicket] = useState({
    subject: '',
    priority: 'medium',
    description: '',
    category: 'general'
  })
  
  // Guardian protection particles
  const [particles, setParticles] = useState<Array<{
    id: number, x: number, y: number, vx: number, vy: number, 
    size: number, color: string
  }>>([])

  // Poetic support messages
  const poeticMessages = {
    welcome: "In the sanctuary of support, every question finds its guardian...",
    guardian: "The GUΛRDIAN stands vigilant, watching over your digital journey...",
    help: "Where confusion meets clarity, consciousness guides the way...",
    protection: "Shielded by digital wisdom, no query walks alone..."
  }

  useEffect(() => {
    // Generate GUARDIAN protection particles
    const guardianColors = [
      'rgba(239, 68, 68, 0.6)',   // red
      'rgba(168, 85, 247, 0.6)',  // purple  
      'rgba(34, 211, 238, 0.6)',  // cyan
      'rgba(16, 185, 129, 0.6)'   // emerald
    ]
    
    const newParticles = Array.from({length: 50}, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: 0.5 + Math.random() * 1.5,
      color: guardianColors[Math.floor(Math.random() * guardianColors.length)]
    }))
    setParticles(newParticles)

    const animateParticles = () => {
      setParticles(prev => prev.map(p => ({
        ...p,
        x: (p.x + p.vx + 100) % 100,
        y: (p.y + p.vy + 100) % 100
      })))
    }

    const interval = setInterval(animateParticles, 120)
    return () => clearInterval(interval)
  }, [])

  const handleSubmitTicket = (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate ticket submission with GUARDIAN validation
    console.log('Support ticket submitted with GUARDIAN protection:', supportTicket)
    alert('Your support request has been received and is protected by GUΛRDIAN.')
    setSupportTicket({ subject: '', priority: 'medium', description: '', category: 'general' })
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* GUARDIAN Protection Particle Field */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute rounded-full"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              backgroundColor: particle.color
            }}
            animate={{
              opacity: [0.3, 0.8, 0.3],
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
      <div className="absolute inset-0 bg-gradient-to-br from-red-900/10 via-black to-purple-900/10" />

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative z-10 border-b border-white/10 backdrop-blur-xl"
      >
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/" className="flex items-center gap-2">
                <motion.div
                  animate={{ 
                    rotate: 360,
                    scale: [1, 1.1, 1]
                  }}
                  transition={{ 
                    rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                    scale: { duration: 2, repeat: Infinity }
                  }}
                >
                  <Shield className="w-6 h-6 text-red-400" />
                </motion.div>
                <span className="text-white font-light text-xl tracking-wider">LUKHΛS</span>
              </Link>

              <div>
                <h1 className="text-2xl font-thin text-white mb-1">GUΛRDIAN Support</h1>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-sm text-white/60">Protection Status: {guardianStatus}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                  type="text"
                  placeholder="Search protected knowledge..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:bg-white/10 focus:border-red-400 focus:outline-none transition-all"
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
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative z-10 flex-1">
        <div className="container mx-auto px-6 py-8">
          
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <motion.div
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.2, 1]
              }}
              transition={{ 
                duration: 6,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="inline-block mb-6"
            >
              <Shield className="w-16 h-16 text-red-400" />
            </motion.div>
            
            <h2 className="text-3xl font-thin text-white mb-4">
              Protected Support Portal
            </h2>
            <p className="text-xl text-white/60 max-w-2xl mx-auto">
              {poeticMode 
                ? poeticMessages.welcome
                : "Your questions are protected by GUΛRDIAN consciousness technology"
              }
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Support Categories */}
            <div className="lg:col-span-2 space-y-6">
              <h3 className="text-xl font-light text-white mb-4">Support Categories</h3>
              
              {supportCategories.map((category) => {
                const Icon = category.icon
                const isExpanded = selectedCategory === category.id
                
                return (
                  <motion.div
                    key={category.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => setSelectedCategory(isExpanded ? '' : category.id)}
                      className="w-full p-6 text-left hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-3 bg-${category.color}-500/20 rounded-lg border border-${category.color}-400/30`}>
                            <Icon className={`w-6 h-6 text-${category.color}-400`} />
                          </div>
                          <div>
                            <h4 className="text-lg font-medium text-white">{category.title}</h4>
                            <p className="text-sm text-white/60">{category.description}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Lock className="w-3 h-3 text-red-400" />
                              <span className="text-xs text-red-400">
                                Protection Level: {category.protectionLevel}
                              </span>
                            </div>
                          </div>
                        </div>
                        <motion.div
                          animate={{ rotate: isExpanded ? 90 : 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          <ChevronRight className="w-5 h-5 text-white/40" />
                        </motion.div>
                      </div>
                    </button>

                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="border-t border-white/10"
                        >
                          <div className="p-6 space-y-3">
                            {category.articles.map((article, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                              >
                                <div className="flex items-center gap-3">
                                  <FileText className="w-4 h-4 text-white/60" />
                                  <div>
                                    <h5 className="text-sm font-medium text-white">{article.title}</h5>
                                    <div className="flex items-center gap-2 mt-1">
                                      <Clock className="w-3 h-3 text-white/40" />
                                      <span className="text-xs text-white/40">{article.readTime}</span>
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={`text-xs px-2 py-1 rounded-full bg-black/20 ${priorityColors[article.priority as keyof typeof priorityColors]}`}>
                                    {article.priority}
                                  </span>
                                  <ChevronRight className="w-4 h-4 text-white/40" />
                                </div>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                )
              })}
            </div>

            {/* Contact & Quick Actions */}
            <div className="space-y-6">
              
              {/* Contact Methods */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-purple-400" />
                  Contact Methods
                </h3>
                
                <div className="space-y-3">
                  {contactMethods.map((method) => {
                    const Icon = method.icon
                    return (
                      <div
                        key={method.name}
                        className={`p-3 bg-${method.color}-500/10 border border-${method.color}-400/30 rounded-lg hover:bg-${method.color}-500/20 transition-colors cursor-pointer`}
                      >
                        <div className="flex items-start gap-3">
                          <Icon className={`w-5 h-5 text-${method.color}-400 mt-0.5`} />
                          <div className="flex-1">
                            <h4 className="font-medium text-white text-sm">{method.name}</h4>
                            <p className="text-xs text-white/60 mb-2">{method.description}</p>
                            <div className="grid grid-cols-2 gap-2 text-xs text-white/40">
                              <div>{method.availability}</div>
                              <div>{method.responseTime}</div>
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              <Shield className="w-3 h-3 text-red-400" />
                              <span className="text-xs text-red-400">{method.guardianLevel}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Support Ticket Form */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                  <Send className="w-5 h-5 text-cyan-400" />
                  Submit Ticket
                </h3>

                <form onSubmit={handleSubmitTicket} className="space-y-4">
                  <div>
                    <label className="block text-sm text-white/70 mb-2">Subject</label>
                    <input
                      type="text"
                      value={supportTicket.subject}
                      onChange={(e) => setSupportTicket(prev => ({ ...prev, subject: e.target.value }))}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:bg-white/10 focus:border-cyan-400 focus:outline-none transition-all text-sm"
                      placeholder="Brief description of your issue"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-white/70 mb-2">Priority</label>
                    <select
                      value={supportTicket.priority}
                      onChange={(e) => setSupportTicket(prev => ({ ...prev, priority: e.target.value }))}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:bg-white/10 focus:border-cyan-400 focus:outline-none transition-all text-sm"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm text-white/70 mb-2">Description</label>
                    <textarea
                      value={supportTicket.description}
                      onChange={(e) => setSupportTicket(prev => ({ ...prev, description: e.target.value }))}
                      rows={4}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:bg-white/10 focus:border-cyan-400 focus:outline-none transition-all text-sm"
                      placeholder="Detailed description of your issue..."
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full bg-cyan-500 hover:bg-cyan-600 text-white py-2 rounded-lg font-medium transition-colors text-sm flex items-center justify-center gap-2"
                  >
                    <Shield className="w-4 h-4" />
                    Submit Protected Ticket
                  </button>
                </form>
              </div>

              {/* Status Indicators */}
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-4">
                <h4 className="text-sm font-medium text-white mb-3">System Status</h4>
                <div className="space-y-2">
                  {[
                    { name: 'GUΛRDIAN Protection', status: 'Operational', color: 'green' },
                    { name: 'Consciousness API', status: 'Operational', color: 'green' },
                    { name: 'Support System', status: 'Operational', color: 'green' },
                    { name: 'Live Chat', status: 'Monitoring', color: 'yellow' }
                  ].map((service) => (
                    <div key={service.name} className="flex items-center justify-between">
                      <span className="text-xs text-white/60">{service.name}</span>
                      <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 bg-${service.color}-400 rounded-full`} />
                        <span className={`text-xs text-${service.color}-400`}>{service.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Community & Resources */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-16 bg-gradient-to-r from-purple-500/10 to-cyan-500/10 backdrop-blur-xl border border-purple-400/30 rounded-xl p-8"
          >
            <div className="text-center mb-8">
              <Users className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-2xl font-thin text-white mb-2">Consciousness Community</h3>
              <p className="text-white/60">
                {poeticMode 
                  ? poeticMessages.protection
                  : "Connect with fellow consciousness explorers in our protected community spaces"
                }
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link
                href="/community/forum"
                className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors text-center"
              >
                <MessageSquare className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <h4 className="text-white font-medium mb-1">Discussion Forum</h4>
                <p className="text-xs text-white/60">Join protected conversations</p>
              </Link>

              <Link
                href="/community/discord"
                className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors text-center"
              >
                <Users className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
                <h4 className="text-white font-medium mb-1">Discord Server</h4>
                <p className="text-xs text-white/60">Real-time community</p>
              </Link>

              <Link
                href="/docs"
                className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-colors text-center"
              >
                <BookOpen className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                <h4 className="text-white font-medium mb-1">Documentation</h4>
                <p className="text-xs text-white/60">Comprehensive guides</p>
              </Link>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}