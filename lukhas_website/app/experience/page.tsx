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

// --- Keyword → Shape heuristic + Sentiment + Color/Tempo + MorphScript hook ---
type Intent = { shape?: string; text?: string }

const SHAPE_KEYWORDS: { re: RegExp; shape: string }[] = [
  { re: /\btorus|donut\b/i, shape: 'torus' },
  { re: /\bcube|box\b/i, shape: 'cube' },
  { re: /\bsphere|ball|orb\b/i, shape: 'sphere' },
  { re: /\bhelix|spiral\b/i, shape: 'consciousness' },
  { re: /\bheart\b/i, shape: 'consciousness' },
  { re: /\bconscious(ness)?\b/i, shape: 'consciousness' },
  // Animal shapes (map to consciousness for now, can extend with custom geometries later)
  { re: /\bcat|kitten|feline\b/i, shape: 'consciousness' },
  { re: /\bdog|puppy|canine\b/i, shape: 'sphere' },
  { re: /\bbird|eagle|dove\b/i, shape: 'consciousness' },
  { re: /\bfish|shark|whale\b/i, shape: 'torus' }
]

const POSITIVE_WORDS = /(love|great|awesome|amazing|calm|peace|serene|happy|nice|cool|excited|fast|energetic|bright|beautiful|wonderful|fantastic|excellent|perfect|joy|bliss)/i
const NEGATIVE_WORDS = /(sad|angry|slow|dark|bad|worse|worst|tired|heavy|cold|gloom|dull|boring|hate|ugly|terrible|awful|horrible)/i

function sentimentScore(msg: string): number {
  const pos = msg.match(new RegExp(POSITIVE_WORDS, 'gi'))?.length || 0
  const neg = msg.match(new RegExp(NEGATIVE_WORDS, 'gi'))?.length || 0
  return Math.tanh((pos - neg) * 0.8) // clamp to [-1,1]
}

function mapKeywordsToColorTempo(msg: string): { color?: string; tempo?: number } {
  const m = msg.toLowerCase()
  if (/love|heart|romance|passion/.test(m)) return { color: '#ec4899', tempo: 1.15 }
  if (/calm|serene|breathe|meditat/.test(m)) return { color: '#38bdf8', tempo: 0.75 }
  if (/focus|clarity|clean|minimal/.test(m)) return { color: '#e5e7eb', tempo: 0.9 }
  if (/energy|hype|party|neon|glow|excited|fast/.test(m)) return { color: '#a78bfa', tempo: 1.25 }
  if (/nature|grow|heal|guardian|safe|trust/.test(m)) return { color: '#22c55e', tempo: 0.95 }
  if (/cat|kitten|feline/.test(m)) return { color: '#f97316', tempo: 1.1 } // Orange for cats
  if (/dog|puppy/.test(m)) return { color: '#84cc16', tempo: 1.2 } // Lime for dogs
  if (/torus|donut/.test(m)) return { color: '#60a5fa', tempo: 1.05 }
  if (/cube|box/.test(m)) return { color: '#93c5fd', tempo: 0.9 }
  if (/sphere|orb|ball/.test(m)) return { color: '#e5e7eb', tempo: 1.0 }
  if (/helix|spiral|conscious/.test(m)) return { color: '#8b5cf6', tempo: 1.1 }
  return {}
}

function extractIntentFromMessage(msg: string): Intent {
  const intent: Intent = {}

  // Quoted text: e.g. text: "LUKHΛS"
  const quoted = /"([^"]+)"/.exec(msg)
  if (quoted?.[1]) intent.text = quoted[1].trim()

  // text: prefix or verbs near the end of the prompt
  const textMatch = /(?:^|\s)(?:text|write|spell|show|render)\s*:?\s*([^\n]+)$/i.exec(msg)
  if (!intent.text && textMatch?.[1]) intent.text = textMatch[1].trim()

  // Shape keywords
  for (const k of SHAPE_KEYWORDS) {
    if (k.re.test(msg)) { intent.shape = k.shape; break }
  }

  if (!intent.shape && !intent.text) intent.shape = 'sphere'
  return intent
}

function buildMorphScriptPlan(intent: Intent, currentConfig: any, effectiveMorphSpeed?: number) {
  const startShape = currentConfig.shape || 'sphere'
  const targetShape = intent.shape || startShape
  const hasText = !!intent.text

  const plan: any = {
    version: '1.0',
    globals: {
      morphSpeed: effectiveMorphSpeed ?? currentConfig.morphSpeed ?? 0.02,
      legibility: hasText ? { chamferMax: 0.1, holdMs: 700 } : undefined
    },
    timeline: [] as any[]
  }

  plan.timeline.push({ t: 0.0, shape: startShape })

  if (hasText) {
    plan.timeline.push({ t: 0.6, text: intent.text, constraints: { chamferMax: 0.1, holdMs: 900 } })
    if (targetShape) plan.timeline.push({ t: 2.0, shape: targetShape })
  } else if (targetShape && targetShape !== startShape) {
    plan.timeline.push({ t: 0.6, shape: targetShape })
  }

  return plan
}

function runMorphScriptPlan(plan: any) {
  if (typeof window === 'undefined') return false
  const ms: any = (window as any).morphScript
  if (ms && typeof ms.run === 'function') { ms.run(plan); return true }
  console.warn('[MorphScript] runtime not found; skip plan execution')
  return false
}
// --- end heuristic + hook ---

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

  // New state for enhanced features
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [rightPanelOpen, setRightPanelOpen] = useState(false)
  const [messages, setMessages] = useState<{ id: string; role: 'user'|'assistant'; content: string; timestamp: Date; model?: string }[]>([])
  const [usage, setUsage] = useState({ tokens: 0, costUSD: 0, creditsRemaining: 1000 })
  const [lastPlan, setLastPlan] = useState<any | null>(null)

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
    
    // Auto-layout tweaks
    setSidebarCollapsed(true)
    setRightPanelOpen(true)
    
    // Heuristic: msg → intent (shape/text)
    const intent = extractIntentFromMessage(message)

    // Sentiment → morphSpeed (positive = faster, negative = slower)
    const s = sentimentScore(message) // [-1, 1]
    const baseSpeed = config.morphSpeed ?? 0.02
    const effectiveSpeed = Math.min(0.1, Math.max(0.005, baseSpeed * (1 + s * 0.5)))
    handleConfigChange('morphSpeed', effectiveSpeed)

    // Keyword → color/tempo
    const kt = mapKeywordsToColorTempo(message)
    if (kt.color) handleConfigChange('accentColor', kt.color)
    if (kt.tempo) handleConfigChange('tempo', kt.tempo)

    // Immediate visible response
    if (intent.shape) handleConfigChange('shape', intent.shape)

    // Build + run MorphScript plan (and store for Dev button)
    try {
      const plan = buildMorphScriptPlan(intent, config, effectiveSpeed)
      setLastPlan(plan)
      runMorphScriptPlan(plan)
    } catch (e) {
      console.warn('Failed to run MorphScript plan:', e)
    }
    
    // Simulate processing and voice data update
    setTimeout(() => {
      setVoiceData({
        intensity: Math.random() * 0.8 + 0.2,
        frequency: Math.random() * 1000 + 200
      })
      setIsProcessing(false)
      
      // Update usage tracking
      setUsage(prev => ({
        tokens: prev.tokens + 120, // placeholder until wired to real APIs
        costUSD: +(prev.costUSD + 0.002).toFixed(4),
        creditsRemaining: Math.max(0, (prev.creditsRemaining || 1000) - 120)
      }))
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

  // Optional: Load legibility harness
  useEffect(() => {
    if (typeof window === 'undefined') return
    if ((window as any).legibilityHarness) return
    const s = document.createElement('script')
    s.src = '/legibility_harness.js' // put the file in /public
    s.async = true
    s.onload = () => console.log('[Legibility] harness loaded')
    s.onerror = () => console.log('[Legibility] harness not found (optional)')
    document.body.appendChild(s)
    return () => { try { document.body.removeChild(s) } catch {} }
  }, [])

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Gradient background */}
      <div className="fixed inset-0 bg-gradient-to-br from-purple-900/10 via-black to-blue-900/10 pointer-events-none" />
      
      {/* Animated background particles (CSS-driven for stability) */}
      <div className="fixed inset-0 pointer-events-none z-0">
        {[...Array(80)].map((_, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-white/20 star"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              width: '2px',
              height: '2px',
              animationDelay: `${Math.random() * 30}s`,
              animationDuration: `${20 + Math.random() * 30}s`
            }}
          />
        ))}
        <style jsx>{`
          .star { animation-name: drift; animation-timing-function: linear; animation-iteration-count: infinite; animation-direction: alternate; will-change: transform; }
          @keyframes drift { from { transform: translate3d(0,0,0); } to { transform: translate3d(0,-40px,0); } }
        `}</style>
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
            
            {/* Dev: Replay last MorphScript plan */}
            {lastPlan && (
              <button
                onClick={() => { if (lastPlan) runMorphScriptPlan(lastPlan) }}
                className="ml-3 px-3 py-2 rounded-md text-xs font-medium bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                title="Replay last plan"
              >
                Play Plan
              </button>
            )}
          </div>
        </div>
      </header>
      
      {/* Sidebar */}
      <ExperienceSidebar
        config={config}
        onConfigChange={handleConfigChange}
        apiKeys={apiKeys}
        onApiKeyChange={handleApiKeyChange}
        collapsed={sidebarCollapsed}
        onCollapsedChange={setSidebarCollapsed}
        usage={usage}
        onEncryptKey={(provider, glyph) => { console.log('Encrypted GLYPH for', provider, glyph) }}
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
        onTyping={() => { setSidebarCollapsed(true); setRightPanelOpen(true) }}
        onMessage={(m) => setMessages(prev => [...prev, m])}
        showInlineHistory={false}
      />
      
      {/* Right-side Message Panel */}
      <AnimatePresence>
        {rightPanelOpen && (
          <motion.aside
            key="right-panel"
            initial={{ x: 360, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 360, opacity: 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 240 }}
            className="fixed right-0 top-16 bottom-24 w-[360px] bg-black/70 backdrop-blur-2xl border-l border-white/10 z-40"
          >
            <div className="h-full overflow-y-auto p-4 space-y-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-medium text-white/60 tracking-wider uppercase">Conversation</h3>
                <button onClick={() => setRightPanelOpen(false)} className="text-white/40 hover:text-white/80 text-xs">Close</button>
              </div>
              {messages.map((m) => (
                <div key={m.id} className={`px-3 py-2 rounded-lg border ${m.role === 'user' ? 'bg-white/5 border-white/10' : 'bg-gradient-to-r from-purple-600/15 to-blue-600/15 border-purple-500/20'}`}>
                  <div className="text-[11px] text-white/40 mb-1">{m.role === 'user' ? 'You' : (m.model || 'Assistant')} • {new Date(m.timestamp).toLocaleTimeString()}</div>
                  <div className="text-sm text-white/90 whitespace-pre-wrap">{m.content}</div>
                </div>
              ))}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  )
}