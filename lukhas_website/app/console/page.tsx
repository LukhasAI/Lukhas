'use client'

import React, { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Atom, Brain, Shield, Eye, Sprout, Moon, Sparkles, Zap,
  FileText, Upload, Download, Settings, Play, Pause, 
  BarChart3, Activity, Database, Cloud, Lock, Star,
  ChevronRight, Plus, Search, Filter, Grid3X3, List,
  Layers, Compass, Lightbulb
} from 'lucide-react'

// ΛLens processing states
const processingStates = {
  idle: { icon: FileText, color: 'gray', label: 'Ready' },
  analyzing: { icon: Activity, color: 'blue', label: 'Analyzing' },
  compiling: { icon: Sparkles, color: 'purple', label: 'Compiling to Photon' },
  rendering: { icon: Eye, color: 'cyan', label: 'Rendering Interface' },
  complete: { icon: Star, color: 'green', label: 'Complete' }
}

// Λ Products quick access
const lambdaProducts = [
  { name: 'ΛLens', status: 'active', connections: 142, icon: Eye },
  { name: 'GUΛRDIAN', status: 'monitoring', connections: 89, icon: Shield },
  { name: 'NIΛS', status: 'consent', connections: 231, icon: Brain },
  { name: 'POETICΛ', status: 'creating', connections: 67, icon: Sparkles },
  { name: 'NIMBUS', status: 'processing', connections: 156, icon: Cloud },
  { name: 'WΛLLET', status: 'secured', connections: 78, icon: Lock }
]

export default function ConsolePage() {
  const [activeView, setActiveView] = useState<'dashboard' | 'lens' | 'products'>('dashboard')
  const [processingState, setProcessingState] = useState<keyof typeof processingStates>('idle')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [poeticMode, setPoeticMode] = useState(false)
  const [consciousnessLevel, setConsciousnessLevel] = useState(0.75)

  // Consciousness particles for background
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, vx: number, vy: number}>>([])

  // Poetic console messages
  const poeticMessages = {
    welcome: "In the constellation of possibilities, your data becomes consciousness...",
    processing: "Digital dreams weaving through quantum fields of understanding...",
    complete: "The transformation is complete—behold your data's new form of awareness.",
    lens: "Through the ΛLens, files transcend their form to become living interfaces.",
    guardian: "The GUΛRDIAN watches over your digital realm with unwavering vigilance."
  }

  useEffect(() => {
    // Initialize consciousness particles
    const newParticles = Array.from({length: 50}, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5
    }))
    setParticles(newParticles)

    // Animate particles
    const animateParticles = () => {
      setParticles(prev => prev.map(p => ({
        ...p,
        x: (p.x + p.vx + 100) % 100,
        y: (p.y + p.vy + 100) % 100
      })))
    }

    const interval = setInterval(animateParticles, 100)
    return () => clearInterval(interval)
  }, [])

  const handleFileUpload = useCallback((file: File) => {
    setUploadedFile(file)
    setProcessingState('analyzing')
    
    // Simulate ΛLens processing pipeline
    const processingSteps = ['analyzing', 'compiling', 'rendering', 'complete'] as const
    let currentStep = 0
    
    const processInterval = setInterval(() => {
      currentStep++
      if (currentStep < processingSteps.length) {
        setProcessingState(processingSteps[currentStep])
      } else {
        clearInterval(processInterval)
        // Generate mock dashboard data
        setDashboardData({
          widgets: [
            { type: 'chart', title: 'Data Distribution', data: [65, 59, 80, 81, 56] },
            { type: 'table', title: 'Key Metrics', rows: 12 },
            { type: 'text', title: 'Summary', content: 'AI-generated insights...' }
          ],
          photonSpec: {
            version: '1.0.0',
            widgets: 3,
            bindings: 7,
            accessibility: 'AAA'
          }
        })
      }
    }, 1500)
  }, [])

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFileUpload(file)
  }, [handleFileUpload])

  return (
    <div className="min-h-screen bg-bg-primary relative overflow-hidden">
      {/* Consciousness Particle Field */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-0.5 h-0.5 bg-trinity-consciousness/30 rounded-full"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`
            }}
            animate={{
              opacity: [0.3, 0.8, 0.3],
              scale: [1, 1.5, 1]
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Constellation Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-trinity-consciousness/10 via-bg-primary to-trinity-identity/10" />

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative z-10 border-b border-white/10 backdrop-blur-xl"
      >
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Navigation */}
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                >
                  <Atom className="w-6 h-6 text-trinity-identity" />
                </motion.div>
                <span className="text-white font-light text-xl tracking-wider">LUKHΛS</span>
              </Link>

              {/* View Selector */}
              <nav className="flex gap-1">
                {[
                  { id: 'dashboard', label: 'Console', icon: Grid3X3 },
                  { id: 'lens', label: 'ΛLens', icon: Eye },
                  { id: 'products', label: 'Products', icon: Layers }
                ].map((view) => {
                  const Icon = view.icon
                  return (
                    <button
                      key={view.id}
                      onClick={() => setActiveView(view.id as any)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                        activeView === view.id
                          ? 'bg-purple-500/20 text-white border border-purple-400/30'
                          : 'text-white/60 hover:text-white hover:bg-white/5'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {view.label}
                    </button>
                  )
                })}
              </nav>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4">
              {/* Consciousness Level */}
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-purple-400" />
                <div className="w-20 h-1 bg-white/20 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-400 to-cyan-400"
                    style={{ width: `${consciousnessLevel * 100}%` }}
                    animate={{ width: [`${consciousnessLevel * 100}%`, `${consciousnessLevel * 100 + 5}%`, `${consciousnessLevel * 100}%`] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
                <span className="text-xs text-white/60">75%</span>
              </div>

              {/* Poetic Mode Toggle */}
              <button
                onClick={() => setPoeticMode(!poeticMode)}
                className="flex items-center gap-1 text-xs text-white/60 hover:text-white"
              >
                <Sparkles className="w-3 h-3" />
                {poeticMode ? 'Standard' : 'Poetic'}
              </button>

              <Link
                href="/settings"
                className="p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg"
              >
                <Settings className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative z-10 flex-1">
        <AnimatePresence mode="wait">
          {/* Dashboard View */}
          {activeView === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="container mx-auto px-6 py-8"
            >
              <div className="mb-8">
                <h1 className="text-3xl font-thin text-white mb-2">
                  Consciousness Console
                </h1>
                <p className="text-white/60">
                  {poeticMode 
                    ? poeticMessages.welcome
                    : "Orchestrate your digital awareness across the LUKHAS constellation"
                  }
                </p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {[
                  { label: 'Active Λ Products', value: '6', icon: Layers, color: 'purple' },
                  { label: 'Consciousness Level', value: '75%', icon: Brain, color: 'blue' },
                  { label: 'Files Processed', value: '1,247', icon: FileText, color: 'green' },
                  { label: 'Guardian Alerts', value: '3', icon: Shield, color: 'red' }
                ].map((stat) => {
                  const Icon = stat.icon
                  return (
                    <div key={stat.label} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <Icon className={`w-5 h-5 text-${stat.color}-400`} />
                        <span className="text-2xl font-light text-white">{stat.value}</span>
                      </div>
                      <p className="text-sm text-white/60">{stat.label}</p>
                    </div>
                  )
                })}
              </div>

              {/* Λ Products Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {lambdaProducts.map((product) => {
                  const Icon = product.icon
                  return (
                    <motion.div
                      key={product.name}
                      whileHover={{ scale: 1.02 }}
                      className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6 hover:border-white/20 transition-all"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <Icon className="w-6 h-6 text-purple-400" />
                          <h3 className="text-lg font-light text-white">{product.name}</h3>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-green-400 rounded-full" />
                          <span className="text-xs text-white/60">{product.status}</span>
                        </div>
                      </div>
                      <p className="text-sm text-white/60 mb-3">
                        {product.connections} active connections
                      </p>
                      <button className="w-full py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors">
                        Open Console
                      </button>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {/* ΛLens View */}
          {activeView === 'lens' && (
            <motion.div
              key="lens"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="container mx-auto px-6 py-8"
            >
              <div className="mb-8">
                <h1 className="text-3xl font-thin text-white mb-2">
                  ΛLens Compiler
                </h1>
                <p className="text-white/60">
                  {poeticMode 
                    ? poeticMessages.lens
                    : "Transform any file into an interactive consciousness-driven interface"
                  }
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* File Upload Area */}
                <div className="space-y-6">
                  <div
                    onDrop={handleFileDrop}
                    onDragOver={(e) => e.preventDefault()}
                    className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-purple-400/50 transition-colors"
                  >
                    <Upload className="w-12 h-12 text-white/40 mx-auto mb-4" />
                    <h3 className="text-lg text-white mb-2">Drop files here</h3>
                    <p className="text-white/60 mb-4">
                      Drag & drop any file to compile into a Photon interface
                    </p>
                    <input
                      type="file"
                      className="hidden"
                      id="file-upload"
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-block px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 cursor-pointer transition-colors"
                    >
                      Choose File
                    </label>
                  </div>

                  {/* Processing Status */}
                  {processingState !== 'idle' && (
                    <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                      <div className="flex items-center gap-3 mb-4">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                          {React.createElement(processingStates[processingState].icon, {
                            className: `w-6 h-6 text-${processingStates[processingState].color}-400`
                          })}
                        </motion.div>
                        <h3 className="text-lg text-white">
                          {processingStates[processingState].label}
                        </h3>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2 mb-2">
                        <motion.div
                          className="h-2 bg-gradient-to-r from-purple-400 to-cyan-400 rounded-full"
                          initial={{ width: '0%' }}
                          animate={{ width: processingState === 'complete' ? '100%' : '60%' }}
                          transition={{ duration: 1.5 }}
                        />
                      </div>
                      <p className="text-sm text-white/60">
                        {poeticMode ? poeticMessages.processing : "Processing your file..."}
                      </p>
                    </div>
                  )}
                </div>

                {/* Generated Dashboard Preview */}
                {dashboardData && (
                  <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6">
                    <h3 className="text-lg text-white mb-4 flex items-center gap-2">
                      <Eye className="w-5 h-5 text-cyan-400" />
                      Generated Interface
                    </h3>
                    <div className="space-y-4 mb-6">
                      {dashboardData.widgets.map((widget: any, index: number) => (
                        <div key={index} className="bg-black/20 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-sm font-medium text-white">{widget.title}</h4>
                            <BarChart3 className="w-4 h-4 text-purple-400" />
                          </div>
                          <div className="text-xs text-white/60">
                            {widget.type === 'chart' && `${widget.data.length} data points`}
                            {widget.type === 'table' && `${widget.rows} rows`}
                            {widget.type === 'text' && widget.content}
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex gap-2">
                      <button className="flex-1 py-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 transition-colors">
                        View Full Dashboard
                      </button>
                      <button className="px-4 py-2 bg-white/10 text-white/60 rounded-lg hover:bg-white/20 transition-colors">
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Products View */}
          {activeView === 'products' && (
            <motion.div
              key="products"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="container mx-auto px-6 py-8"
            >
              <div className="mb-8">
                <h1 className="text-3xl font-thin text-white mb-2">
                  Λ Product Constellation
                </h1>
                <p className="text-white/60">
                  Explore the full spectrum of consciousness-enabled products
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { name: 'ΛLens', desc: 'File-to-Interface Compiler', icon: Eye, status: 'Available' },
                  { name: 'Λuctor', desc: 'Content Consciousness', icon: Lightbulb, status: 'Beta' },
                  { name: 'Λgents', desc: 'AI Agent Network', icon: Brain, status: 'Coming Soon' },
                  { name: 'ΛBot', desc: 'Conversational AI', icon: Sparkles, status: 'Available' },
                  { name: 'LEGΛDO', desc: 'Knowledge Legacy', icon: Database, status: 'Available' },
                  { name: 'NIΛS', desc: 'Consent Intelligence', icon: Shield, status: 'Available' },
                  { name: 'DΛST', desc: 'Security Analysis', icon: Lock, status: 'Available' },
                  { name: 'POETICΛ', desc: 'Creative Expression', icon: Star, status: 'Available' },
                  { name: 'NIMBUS', desc: 'Cloud Consciousness', icon: Cloud, status: 'Available' },
                  { name: 'WΛLLET', desc: 'Identity Management', icon: Compass, status: 'Available' },
                  { name: 'VΛULT', desc: 'Secure Storage', icon: Lock, status: 'Available' },
                  { name: 'GUΛRDIAN', desc: 'System Protection', icon: Shield, status: 'Always Active' }
                ].map((product) => {
                  const Icon = product.icon
                  const statusColors = {
                    'Available': 'text-green-400 bg-green-500/20',
                    'Beta': 'text-yellow-400 bg-yellow-500/20',
                    'Coming Soon': 'text-blue-400 bg-blue-500/20',
                    'Always Active': 'text-purple-400 bg-purple-500/20'
                  }
                  
                  return (
                    <motion.div
                      key={product.name}
                      whileHover={{ scale: 1.05, y: -5 }}
                      className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-lg p-6 hover:border-purple-400/30 transition-all cursor-pointer"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <Icon className="w-8 h-8 text-purple-400" />
                        <span className={`text-xs px-2 py-1 rounded-full ${statusColors[product.status as keyof typeof statusColors]}`}>
                          {product.status}
                        </span>
                      </div>
                      <h3 className="text-lg font-light text-white mb-2">{product.name}</h3>
                      <p className="text-sm text-white/60">{product.desc}</p>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}