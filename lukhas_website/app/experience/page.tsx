'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { Activity, ArrowLeft, Cpu, Layers, Shield, Sparkles, Zap } from 'lucide-react'
import dynamic from 'next/dynamic'
import Link from 'next/link'
import { useEffect, useState } from 'react'

// Plan1 integration - imports with fallbacks
import { callAI, type ApiResponse } from '@/lib/api/aiProviders'
import { calmDefaults, isViolent } from '@/lib/safety'
import { estimateTokensAndCost } from '@/lib/tokenEstimator'
import { mapKeywordsToColorTempo, sentimentScore } from '@/lib/toneSystem'
import Footer from '@/components/footer'

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

// TEMP fallbacks: remove once lib modules are present
const _fallbackSent = (s: string) => 0;
const _fallbackMap = (s: string) => ({} as { color?: string; tempo?: number });
const _fallbackIsViolent = (s: string) => false;
const _fallbackCalm = { accentColor: '#38bdf8', tempo: 0.75, morphSpeed: 0.018 };
const _fallbackEstimate = (text: string, model: string) => ({ 
  tokens: Math.max(60, Math.ceil(text.length / 4) + 80), 
  costUSD: 0 
});

// Resolve to real if available
const SENT = (typeof sentimentScore === 'function' ? sentimentScore : _fallbackSent);
const MAP = (typeof mapKeywordsToColorTempo === 'function' ? mapKeywordsToColorTempo : _fallbackMap);
const VIOL = (typeof isViolent === 'function' ? isViolent : _fallbackIsViolent);
const CALM = (typeof calmDefaults === 'object' ? calmDefaults : _fallbackCalm);
const EST = (typeof estimateTokensAndCost === 'function' ? estimateTokensAndCost : _fallbackEstimate);

// Hook to detect prefers-reduced-motion
function useReducedMotion() {
  const [reducedMotion, setReducedMotion] = useState(false)
  
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
    
    const handler = () => setReducedMotion(mediaQuery.matches)
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])
  
  return reducedMotion
}

// --- Keyword → Shape heuristic + Sentiment + Color/Tempo + MorphScript hook ---
type Intent = { shape?: string; text?: string }
type QueuedShape = { noun: string; ts: number }

// Supported shapes the runtime can render directly
const SUPPORTED_SHAPES = new Set(['sphere', 'torus', 'cube', 'consciousness'])

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

// Detect a likely noun request (single word, 3+ letters)
function detectUnknownNoun(msg: string): string | null {
  // Try quoted first: "cat" → cat
  const q = /"([a-zA-Z][a-zA-Z\s\-]{2,})"/.exec(msg)
  if (q?.[1]) {
    const word = q[1].trim()
    return SUPPORTED_SHAPES.has(word.toLowerCase()) ? null : word
  }
  // Then any noun-ish token after an action verb
  const m = /(make|turn|render|form|shape|draw)\s+([a-zA-Z][a-zA-Z\-]{2,})/i.exec(msg)
  if (m?.[2]) {
    const word = m[2].toLowerCase()
    return SUPPORTED_SHAPES.has(word) ? null : m[2]
  }
  return null
}

// Morph progress estimation
function estimatePlanDuration(plan: any) {
  const tl = plan?.timeline || []
  let total = 0
  for (const step of tl) {
    if (step.text || step.svg) total += (step.constraints?.holdMs || 900) + 1200
    else total += 800
  }
  return Math.max(total, 1200)
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

  // Truthful fallback for unsupported shapes: render glyph text first and queue noun
  if (!intent.shape && !intent.text) {
    const noun = detectUnknownNoun(msg)
    if (noun) {
      intent.text = noun.toUpperCase()
      // Inform ExperiencePage via window event for queueing
      try { 
        window.dispatchEvent(new CustomEvent('lukhas-queue-shape', { detail: { noun } })) 
      } catch { }
    }
  }

  // Special-case: cat stays nice :)
  if (!intent.shape && !intent.text && /\bcat(s)?\b/i.test(msg)) {
    intent.text = 'CAT'
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
  // Constants for layout
  const RIGHT_PANEL_WIDTH = 360 // px
  
  // Motion preferences
  const prefersReducedMotion = useReducedMotion()
  
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
  
  // Plan1 features state
  const [modStats, setModStats] = useState<{ sentiment: number; tempo: number; speed: number }>({ 
    sentiment: 0, tempo: 1, speed: 0.02 
  })
  const [morphBar, setMorphBar] = useState<{ active: boolean; value: number; label: string }>({ 
    active: false, value: 0, label: 'Morphing…' 
  })
  const [queuedShapes, setQueuedShapes] = useState<QueuedShape[]>([])
  const [showQueue, setShowQueue] = useState(false)
  const [truthNotice, setTruthNotice] = useState<{ active: boolean; noun?: string }>({ active: false })
  const [safetyActive, setSafetyActive] = useState(false)
  const [replyEst, setReplyEst] = useState<{ tokens: number; costUSD: number } | null>(null)

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
    activeModel: 'lukhas',
    tempo: 1.0,
    accentColor: '#8b5cf6'
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

  // Guardian calm function
  const activateGuardianCalm = () => {
    setSafetyActive(true)
    // calm palette + tempo
    handleConfigChange('accentColor', CALM.accentColor)
    handleConfigChange('tempo', CALM.tempo)
    handleConfigChange('morphSpeed', CALM.morphSpeed)
    setTimeout(() => setSafetyActive(false), 2000)
  }

  // Morph progress animation
  const playMorphProgress = (plan: any) => {
    const total = estimatePlanDuration(plan)
    const start = performance.now()
    setMorphBar({ active: true, value: 0, label: 'Morphing…' })
    function tick() {
      const v = Math.min(1, (performance.now() - start) / total)
      setMorphBar({ active: true, value: v, label: v < 1 ? 'Morphing…' : 'Complete' })
      if (v < 1) requestAnimationFrame(tick)
      else setTimeout(() => setMorphBar({ active: false, value: 1, label: 'Complete' }), 600)
    }
    requestAnimationFrame(tick)
  }

  // Handle message sending with Plan1 enhancements
  const handleSendMessage = async (message: string) => {
    setIsProcessing(true)
    
    // Auto-layout tweaks
    setSidebarCollapsed(true)
    setRightPanelOpen(true)
    
    // Heuristic: msg → intent (shape/text)
    const intent = extractIntentFromMessage(message)

    // Safety by design: cap energy if very negative or violent language
    const violent = VIOL(message)
    const sent = SENT(message)
    const danger = violent || sent < -0.6
    if (danger) {
      activateGuardianCalm()
    }

    // Estimate tokens & soft cost (for UI)
    try { 
      setReplyEst(EST(message, config?.activeModel || 'lukhas')) 
    } catch { }

    // Sentiment → morph speed (safety-capped)
    const s = SENT(message)
    const baseSpeed = config.morphSpeed ?? 0.02
    let effectiveSpeed = Math.min(0.1, Math.max(0.005, baseSpeed * (1 + s * 0.5)))
    if (danger) effectiveSpeed = Math.min(effectiveSpeed, CALM.morphSpeed)
    handleConfigChange('morphSpeed', effectiveSpeed)

    // Keyword → color/tempo
    const kt = MAP(message)
    if (kt.color && !danger) handleConfigChange('accentColor', kt.color)
    if (kt.tempo) handleConfigChange('tempo', kt.tempo)

    if (danger) {
      handleConfigChange('accentColor', CALM.accentColor)
      handleConfigChange('tempo', Math.min(CALM.tempo, (kt.tempo ?? 1)))
    }

    setModStats({ sentiment: s, tempo: kt.tempo ?? (config.tempo ?? 1), speed: effectiveSpeed })

    // Immediate visible response
    if (intent.shape) handleConfigChange('shape', intent.shape)

    // Build + run MorphScript plan (and store for Dev button)
    try {
      const plan = buildMorphScriptPlan(intent, config, effectiveSpeed)
      setLastPlan(plan)
      playMorphProgress(plan)
      runMorphScriptPlan(plan)
    } catch (e) {
      console.warn('Failed to run MorphScript plan:', e)
    }
    
    // Add user message to chat history
    const userMessage = {
      id: `msg-${Date.now()}-user`,
      role: 'user' as const,
      content: message,
      timestamp: new Date(),
      model: selectedModel
    }
    setMessages(prev => [...prev, userMessage])

    // Real API integration
    try {
      let response: ApiResponse | null = null
      
      if (config.activeModel === 'gpt-4o' && apiKeys.openai) {
        response = await callAI(message, 'openai', 'gpt-4o', apiKeys.openai)
      } else if (config.activeModel === 'gpt-4o-mini' && apiKeys.openai) {
        response = await callAI(message, 'openai', 'gpt-4o-mini', apiKeys.openai)
      } else if (config.activeModel === 'claude-3-sonnet' && apiKeys.anthropic) {
        response = await callAI(message, 'anthropic', 'claude-3-sonnet-20240229', apiKeys.anthropic)
      } else if (config.activeModel === 'claude-3-haiku' && apiKeys.anthropic) {
        response = await callAI(message, 'anthropic', 'claude-3-haiku-20240307', apiKeys.anthropic)
      } else if (config.activeModel === 'gemini-1.5-pro' && apiKeys.google) {
        response = await callAI(message, 'google', 'gemini-1.5-pro', apiKeys.google)
      } else if (config.activeModel === 'gemini-1.5-flash' && apiKeys.google) {
        response = await callAI(message, 'google', 'gemini-1.5-flash', apiKeys.google)
      } else if (config.activeModel === 'pplx-7b-online' && apiKeys.perplexity) {
        response = await callAI(message, 'perplexity', 'pplx-7b-online', apiKeys.perplexity)
      } else if (config.activeModel === 'pplx-70b-online' && apiKeys.perplexity) {
        response = await callAI(message, 'perplexity', 'pplx-70b-online', apiKeys.perplexity)
      }
      
      // Update voice data and processing state
      setVoiceData({
        intensity: Math.random() * 0.8 + 0.2,
        frequency: Math.random() * 1000 + 200
      })
      
      // Update usage tracking with real data if available
      if (response && !response.error) {
        // Only use response if there's no error
        setUsage(prev => ({
          tokens: prev.tokens + response.usage.tokens,
          costUSD: +(prev.costUSD + response.usage.costUSD).toFixed(6),
          creditsRemaining: Math.max(0, prev.creditsRemaining - response.usage.tokens)
        }))
        
        // Add response message to chat
        const assistantMessage = {
          id: `msg-${Date.now()}`,
          role: 'assistant' as const,
          content: response.content,
          timestamp: new Date(),
          model: response.model
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        // Fallback: Use LUKHAS local responses when error or no response
        if (response?.error) {
          console.warn('API Error (using fallback):', response.error)
        }
        
        // Generate appropriate LUKHAS fallback response
        const fallbackResponses = [
          '• Poetic: Understood. The field is listening.\n• Friendly: Ask for a shape or say a word in quotes to see it drawn in particles.\n• Insight: Legibility and convergence are prioritized; complex silhouettes are approximated before true assets are added.',
          'Morphing consciousness awaits your command. Speak a shape into being.',
          'The particle field responds to your intention. What form shall we manifest?'
        ]
        
        const fallbackMessage = {
          id: `msg-${Date.now()}`,
          role: 'assistant' as const,
          content: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
          timestamp: new Date(),
          model: 'LUKHAS'
        }
        setMessages(prev => [...prev, fallbackMessage])
        
        setUsage(prev => ({
          tokens: prev.tokens + 120,
          costUSD: +(prev.costUSD + 0.002).toFixed(4),
          creditsRemaining: Math.max(0, prev.creditsRemaining - 120)
        }))
      }
      
    } catch (error) {
      console.error('API call failed:', error)
      // Fallback to local processing
      setUsage(prev => ({
        tokens: prev.tokens + 120,
        costUSD: +(prev.costUSD + 0.002).toFixed(4),
        creditsRemaining: Math.max(0, prev.creditsRemaining - 120)
      }))
    } finally {
      setIsProcessing(false)
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

  // Queue system event listener
  useEffect(() => {
    function onQueue(e: any) {
      const noun = e?.detail?.noun
      if (!noun) return
      setQueuedShapes(prev => [{ noun, ts: Date.now() }, ...prev].slice(0, 20))
      // show truthful prompt once per noun
      setTruthNotice({ active: true, noun })
    }
    window.addEventListener('lukhas-queue-shape', onQueue)
    return () => window.removeEventListener('lukhas-queue-shape', onQueue)
  }, [])

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
      
      {/* Header - 3-Zone Grid Layout */}
      <header className="sticky top-0 z-40 backdrop-blur-lg bg-black/30 border-b border-white/10">
        <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14">
          <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 py-3 md:py-4">
            {/* Left: Brand / Back */}
            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="px-2 py-1 rounded-md bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <ArrowLeft className="w-4 h-4 inline mr-1 group-hover:-translate-x-0.5 transition-transform" />
                <span className="text-xs font-medium">Back</span>
              </Link>
              <div className="text-sm tracking-wide text-white/70">
                LUKHAS <span className="text-white/40">EXPERIENCE</span>
              </div>
              <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 bg-white/5 border border-white/10 rounded-full">
                <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse" />
                <span className="text-xs text-white/60">
                  Consciousness Active
                </span>
              </div>
            </div>

            {/* Center: Modes (segmented) */}
            <div className="flex items-center justify-center">
              <div className="inline-flex rounded-xl border border-white/10 bg-white/[0.04] p-1">
                {['morphing', 'trinity', 'hybrid'].map(m => (
                  <button
                    key={m}
                    className={`px-3 md:px-4 py-1.5 text-xs rounded-lg capitalize transition-all ${
                      visualizationMode === m
                        ? 'bg-white/15 text-white'
                        : 'text-white/60 hover:text-white'
                    }`}
                    onClick={() => setVisualizationMode(m as any)}
                  >
                    {m === 'morphing' && <Cpu className="w-3.5 h-3.5 inline mr-1.5" />}
                    {m === 'trinity' && <Layers className="w-3.5 h-3.5 inline mr-1.5" />}
                    {m === 'hybrid' && <Activity className="w-3.5 h-3.5 inline mr-1.5" />}
                    {m}
                  </button>
                ))}
              </div>
            </div>

            {/* Right: Utilities */}
            <div className="flex items-center justify-end gap-2 md:gap-3">
              <button
                onClick={activateGuardianCalm}
                aria-label="Instant Calm"
                className={`px-3 py-2 text-xs rounded-md border transition-colors ${
                  safetyActive
                    ? 'bg-cyan-600/30 border-cyan-400/30 text-cyan-200'
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
              >
                <Shield className="w-3.5 h-3.5 inline mr-1" />
                Calm
              </button>
              <button
                onClick={() => setShowQueue(v => !v)}
                className="px-3 py-2 text-xs rounded-md bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
              >
                Queue
                <span className="ml-1.5 px-1.5 py-0.5 text-[10px] rounded bg-white/10">
                  {queuedShapes.length}
                </span>
              </button>
              {lastPlan && (
                <button
                  onClick={() => runMorphScriptPlan(lastPlan)}
                  className="px-3 py-2 text-xs rounded-md bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <Zap className="w-3.5 h-3.5 inline mr-1" />
                  Play
                </button>
              )}

              {/* Status chip */}
              <div className="hidden md:block ml-1 px-3 py-2 rounded-md text-[11px] bg-white/5 border border-white/10 text-white/70">
                Sent {modStats.sentiment >= 0 ? '+' : ''}{modStats.sentiment.toFixed(2)} ·
                Tempo {modStats.tempo.toFixed(2)}x ·
                Speed {modStats.speed.toFixed(3)}
              </div>
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
        collapsed={sidebarCollapsed}
        onCollapsedChange={setSidebarCollapsed}
        usage={usage}
        onEncryptKey={(provider, glyph) => { console.log('Encrypted GLYPH for', provider, glyph) }}
      />
      
      {/* Main Visualization Area with Perfect Centering */}
      <main 
        className="h-screen pt-16 flex items-center justify-center relative transition-[padding] duration-300"
        style={{ 
          ['--rpw' as any]: `${RIGHT_PANEL_WIDTH}px`,
          paddingRight: rightPanelOpen ? `${RIGHT_PANEL_WIDTH}px` : '0'
        }}
        data-panel-open={rightPanelOpen ? '1' : '0'}
      >
        <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14 h-full py-8">
          <motion.div
            initial={prefersReducedMotion ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.5 }}
            className="w-full h-full relative"
          >
            {/* Visualization Container */}
            <div className="w-full h-full bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden">
              <AnimatePresence mode="wait">
                {visualizationMode === 'morphing' && (
                  <motion.div
                    key="morphing"
                    initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                    transition={prefersReducedMotion ? { duration: 0 } : undefined}
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
                    initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                    transition={prefersReducedMotion ? { duration: 0 } : undefined}
                    className="w-full h-full"
                  >
                    <TrinityInteractive />
                  </motion.div>
                )}
                
                {visualizationMode === 'hybrid' && (
                  <motion.div
                    key="hybrid"
                    initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                    transition={prefersReducedMotion ? { duration: 0 } : undefined}
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
            initial={{ x: RIGHT_PANEL_WIDTH, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: RIGHT_PANEL_WIDTH, opacity: 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 240 }}
            className="fixed right-0 top-[72px] bottom-24 bg-black/40 backdrop-blur-md border-l border-white/10 z-40"
            style={{ width: `${RIGHT_PANEL_WIDTH}px` }}
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

      {/* Morph Progress Bar */}
      {morphBar.active && (
        <div className="fixed left-1/2 -translate-x-1/2 bottom-8 z-50 w-[min(560px,90vw)]">
          <div className="mb-1 text-center text-[11px] text-white/70">
            {morphBar.label} {Math.round(morphBar.value * 100)}%
            {replyEst && (
              <span className="ml-2 text-white/50">· est ${replyEst.costUSD.toFixed(3)} / {replyEst.tokens} tok</span>
            )}
          </div>
          <div className="h-2 rounded-full bg-white/10 overflow-hidden border border-white/15">
            <div 
              className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-400 transition-all duration-100" 
              style={{ width: `${Math.round(morphBar.value * 100)}%` }} 
            />
          </div>
        </div>
      )}

      {/* Queue Popover */}
      {showQueue && (
        <div className="fixed right-4 top-20 z-40 w-64 rounded-xl bg-black/40 backdrop-blur-md border border-white/10 p-4">
          <div className="text-xs text-white/60 mb-2">Queued Shapes</div>
          <ul className="space-y-1 max-h-56 overflow-y-auto">
            {queuedShapes.map((q, i) => (
              <li key={q.ts + ':' + i} className="text-[11px] text-white/70 flex items-center justify-between">
                <span>{q.noun}</span>
                <span className="text-white/30">{new Date(q.ts).toLocaleTimeString()}</span>
              </li>
            ))}
            {queuedShapes.length === 0 && (
              <li className="text-[11px] text-white/40">Nothing queued yet.</li>
            )}
          </ul>
        </div>
      )}

      {/* Truth Notice Banner */}
      {truthNotice.active && (
        <div className="fixed left-1/2 -translate-x-1/2 bottom-24 z-50 w-[min(640px,92vw)] p-4 rounded-xl bg-black/40 backdrop-blur-md border border-white/10">
          <div className="text-sm text-white/90">That shape isn't in my library yet.</div>
          <div className="mt-1 text-[11px] text-white/60">Choose how to proceed for "{truthNotice.noun}":</div>
          <div className="mt-3 flex flex-wrap gap-2">
            <button 
              className="px-3 py-2 text-xs rounded-lg bg-white/10 border border-white/10 hover:bg-white/15 transition-colors" 
              onClick={() => setTruthNotice({ active: false })}
            >
              Render as GLYPH
            </button>
            <button 
              className="px-3 py-2 text-xs rounded-lg bg-white/10 border border-white/10 hover:bg-white/15 transition-colors" 
              onClick={() => { 
                handleConfigChange('shape', 'sphere'); 
                setTruthNotice({ active: false });
              }}
            >
              Approximate (simple form)
            </button>
            <button 
              className="px-3 py-2 text-xs rounded-lg bg-white/10 border border-white/10 hover:bg-white/15 transition-colors" 
              onClick={() => setTruthNotice({ active: false })}
            >
              Queue it (keep motion)
            </button>
          </div>
        </div>
      )}
      
      <Footer />
    </div>
  )
}