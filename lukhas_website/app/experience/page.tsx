'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Sparkles, Cpu, Layers, Activity } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'

// Dynamic imports for better performance
const ExperienceSidebar = dynamic(() => import('@/components/experience-sidebar'), { 
  ssr: false,
  loading: () => <div className="fixed left-0 top-16 bottom-0 w-80 bg-black/40 animate-pulse" />
})

const ChatInterface = dynamic(() => import('@/components/chat-interface'), { 
  ssr: false 
})

const TrinityInteractive = dynamic(() => import('@/components/trinity-interactive'), { 
  ssr: false,
  loading: () => <div className="w-full h-full bg-black/20 animate-pulse rounded-2xl" />
})

const MorphingVisualizer = dynamic(() => import('@/components/morphing-visualizer'), { 
  ssr: false,
  loading: () => <div className="w-full h-full bg-black/20 animate-pulse rounded-2xl" />
})

type VisualizationMode = 'morphing' | 'trinity' | 'hybrid'

export default function ExperiencePage() {
  const [visualizationMode, setVisualizationMode] = useState<VisualizationMode>('morphing')
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedModel, setSelectedModel] = useState('LUKHAS')
  
  // Voice data state
  const [voiceData, setVoiceData] = useState({
    intensity: 0,
    frequency: 0
  })

  // Configuration state
  const [config, setConfig] = useState({
    micEnabled: false,
    audioEnabled: true,
    particleCount: 1000,
    morphSpeed: 0.02,
    shape: 'sphere',
    voiceSensitivity: 0.5,
    consciousnessMode: 'aware',
    trinityIdentity: true,
    trinityConsciousness: true,
    trinityGuardian: true,
    activeModel: 'lukhas'
  })

  // API Keys state
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
    google: '',
    perplexity: ''
  })

  // Handle configuration changes
  const handleConfigChange = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }))
    
    // Update selected model when activeModel changes
    if (key === 'activeModel') {
      const modelMap: Record<string, string> = {
        lukhas: 'LUKHAS',
        'gpt-4': 'GPT-4',
        'claude-3': 'Claude 3',
        'gemini-pro': 'Gemini Pro',
        perplexity: 'Perplexity'
      }
      setSelectedModel(modelMap[value] || 'LUKHAS')
    }
  }

  // Handle API key changes
  const handleApiKeyChange = (provider: string, key: string) => {
    setApiKeys(prev => ({ ...prev, [provider]: key }))
  }

  // Handle message sending
  const handleSendMessage = async (message: string) => {
    setIsProcessing(true)
    
    // Simulate processing and voice data update
    setTimeout(() => {
      setVoiceData({
        intensity: Math.random() * 0.8 + 0.2,
        frequency: Math.random() * 1000 + 200
      })
      setIsProcessing(false)
    }, 2000)

    // Here you would integrate with actual AI APIs
    if (config.activeModel === 'gpt-4' && apiKeys.openai) {
      // Call OpenAI API
    } else if (config.activeModel === 'claude-3' && apiKeys.anthropic) {
      // Call Anthropic API
    } else if (config.activeModel === 'gemini-pro' && apiKeys.google) {
      // Call Google API
    } else if (config.activeModel === 'perplexity' && apiKeys.perplexity) {
      // Call Perplexity API
    } else {
      // Use LUKHAS AI system
    }
  }

  // Simulate voice data updates when mic is enabled
  useEffect(() => {
    if (config.micEnabled) {
      const interval = setInterval(() => {
        setVoiceData({
          intensity: Math.random() * 0.6,
          frequency: Math.random() * 800 + 100
        })
      }, 100)
      return () => clearInterval(interval)
    } else {
      setVoiceData({ intensity: 0, frequency: 0 })
    }
  }, [config.micEnabled])

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Gradient background */}
      <div className="fixed inset-0 bg-gradient-to-br from-purple-900/10 via-black to-blue-900/10 pointer-events-none" />
      
      {/* Animated background particles */}
      <div className="fixed inset-0 pointer-events-none">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white/20 rounded-full"
            initial={{ 
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1920,
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1080
            }}
            animate={{
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1920,
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1080,
            }}
            transition={{
              duration: 20 + Math.random() * 20,
              repeat: Infinity,
              repeatType: 'reverse',
              ease: 'linear'
            }}
          />
        ))}
      </div>
      
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-black/40 backdrop-blur-2xl border-b border-white/10">
        <div className="px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-6">
              <Link 
                href="/" 
                className="flex items-center gap-2 text-white/60 hover:text-white transition-colors group"
              >
                <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                <span className="text-sm font-medium tracking-wider uppercase">Back</span>
              </Link>
              
              <div className="h-6 w-px bg-white/20" />
              
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 blur-xl opacity-50" />
                  <h1 className="relative text-xl font-light tracking-[0.3em] uppercase bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                    LUKHAS Experience
                  </h1>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 bg-white/5 border border-white/10 rounded-full">
                  <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse" />
                  <span className="text-xs text-white/60 font-medium">
                    Consciousness Active
                  </span>
                </div>
              </div>
            </div>
            
            {/* Visualization Mode Selector */}
            <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-lg p-1">
              <button
                onClick={() => setVisualizationMode('morphing')}
                className={`px-4 py-2 rounded-md text-xs font-medium transition-all ${
                  visualizationMode === 'morphing'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  <span>Morphing</span>
                </div>
              </button>
              <button
                onClick={() => setVisualizationMode('trinity')}
                className={`px-4 py-2 rounded-md text-xs font-medium transition-all ${
                  visualizationMode === 'trinity'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4" />
                  <span>Trinity</span>
                </div>
              </button>
              <button
                onClick={() => setVisualizationMode('hybrid')}
                className={`px-4 py-2 rounded-md text-xs font-medium transition-all ${
                  visualizationMode === 'hybrid'
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  <span>Hybrid</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Sidebar */}
      <ExperienceSidebar
        config={config}
        onConfigChange={handleConfigChange}
        apiKeys={apiKeys}
        onApiKeyChange={handleApiKeyChange}
      />
      
      {/* Main Visualization Area */}
      <main className="h-screen pt-16 pb-24 flex items-center justify-center">
        <div className="w-full h-full max-w-7xl mx-auto px-6 py-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="w-full h-full relative"
          >
            {/* Visualization Container */}
            <div className="w-full h-full bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden">
              <AnimatePresence mode="wait">
                {visualizationMode === 'morphing' && (
                  <motion.div
                    key="morphing"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="w-full h-full"
                  >
                    <MorphingVisualizer 
                      config={config}
                      voiceData={voiceData}
                    />
                  </motion.div>
                )}
                
                {visualizationMode === 'trinity' && (
                  <motion.div
                    key="trinity"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="w-full h-full"
                  >
                    <TrinityInteractive />
                  </motion.div>
                )}
                
                {visualizationMode === 'hybrid' && (
                  <motion.div
                    key="hybrid"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="w-full h-full grid grid-cols-2 gap-4 p-4"
                  >
                    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden">
                      <MorphingVisualizer 
                        config={config}
                        voiceData={voiceData}
                      />
                    </div>
                    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden">
                      <TrinityInteractive />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {/* Floating Status Indicators */}
            <div className="absolute top-4 right-4">
              <div className="space-y-2">
                {config.micEnabled && (
                  <motion.div
                    initial={{ x: 20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    className="flex items-center gap-2 px-3 py-2 bg-black/60 backdrop-blur-xl border border-green-500/30 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-xs text-green-400">Voice Active</span>
                  </motion.div>
                )}
                
                {config.audioEnabled && (
                  <motion.div
                    initial={{ x: 20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="flex items-center gap-2 px-3 py-2 bg-black/60 backdrop-blur-xl border border-blue-500/30 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                    <span className="text-xs text-blue-400">Audio Enabled</span>
                  </motion.div>
                )}
                
                <motion.div
                  initial={{ x: 20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="flex items-center gap-2 px-3 py-2 bg-black/60 backdrop-blur-xl border border-purple-500/30 rounded-lg"
                >
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <span className="text-xs text-purple-400">
                    {config.consciousnessMode.charAt(0).toUpperCase() + config.consciousnessMode.slice(1)} Mode
                  </span>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
      
      {/* Chat Interface */}
      <ChatInterface 
        onSendMessage={handleSendMessage}
        selectedModel={selectedModel}
        isProcessing={isProcessing}
      />
    </div>
  )
}