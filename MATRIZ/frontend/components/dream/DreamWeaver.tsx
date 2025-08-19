'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sparkles, Brain, Heart, Zap, Eye, Layers, 
  Music, Download, Share2, Play, Pause, RefreshCw,
  Volume2, ChevronRight, Loader2, Send, Mic
} from 'lucide-react'
import { useSSE, type DreamEvent } from '@/hooks/useSSE'
import { useDreamContext } from '@/contexts/DreamContext'
import ConsciousnessVisualizer from './ConsciousnessVisualizer'
import TimelineExplorer from './TimelineExplorer'
import GlyphComposer from './GlyphComposer'
import EmotionalResonance from './EmotionalResonance'
import MemoryIntegrator from './MemoryIntegrator'

interface DreamState {
  seed: string
  consciousness: {
    awareness: number
    coherence: number
    depth: number
  }
  emotion: {
    valence: number
    arousal: number
    dominance: number
  }
  glyphs: string[]
  timeline: {
    branches: any[]
    selectedPath: number[]
  }
  memories: any[]
  narrative: string
  isProcessing: boolean
  phase: 'seed' | 'awakening' | 'exploration' | 'creation' | 'resonance' | 'integration' | 'crystallization'
}

export default function DreamWeaver() {
  const { setPhase, setIntensity } = useDreamContext()
  const [dreamState, setDreamState] = useState<DreamState>({
    seed: '',
    consciousness: {
      awareness: 0,
      coherence: 0,
      depth: 0
    },
    emotion: {
      valence: 0.5,
      arousal: 0.5,
      dominance: 0.5
    },
    glyphs: [],
    timeline: {
      branches: [],
      selectedPath: []
    },
    memories: [],
    narrative: '',
    isProcessing: false,
    phase: 'seed'
  })

  const [inputValue, setInputValue] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioEnabled, setAudioEnabled] = useState(true)
  const [voiceInput, setVoiceInput] = useState(false)
  
  // Replace WebSocket with resilient SSE
  const { data: streamData, connected, error } = useSSE<DreamEvent>('/api/dream/stream', { 
    debounceMs: 300,
    paused: !isPlaying 
  })
  
  const audioContextRef = useRef<AudioContext | null>(null)

  // Handle SSE stream data
  useEffect(() => {
    if (!streamData) return
    
    setDreamState(prev => ({
      ...prev,
      phase: streamData.phase || prev.phase,
      consciousness: {
        awareness: streamData.awareness || prev.consciousness.awareness,
        coherence: streamData.coherence || prev.consciousness.coherence,
        depth: streamData.depth || prev.consciousness.depth
      },
      emotion: streamData.emotion || prev.emotion,
      glyphs: streamData.glyphs ? [...prev.glyphs, ...streamData.glyphs].slice(-12) : prev.glyphs,
      narrative: streamData.narrative || prev.narrative
    }))
    
    if (audioEnabled && streamData.emotion) {
      playEmotionalTone(streamData.emotion)
    }
  }, [streamData, audioEnabled])

  // Sync phase changes with dream context for vignette overlay
  useEffect(() => {
    setPhase(dreamState.phase)
    // Calculate dynamic intensity based on consciousness metrics
    const intensity = (dreamState.consciousness.awareness + dreamState.consciousness.coherence + dreamState.consciousness.depth) / 3
    setIntensity(intensity)
  }, [dreamState.phase, dreamState.consciousness, setPhase, setIntensity])

  useEffect(() => {
    // Initialize audio context
    if (typeof window !== 'undefined') {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
    }

    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])


  const playEmotionalTone = (emotion: any) => {
    if (!audioContextRef.current) return

    const oscillator = audioContextRef.current.createOscillator()
    const gainNode = audioContextRef.current.createGain()
    
    // Map emotions to frequencies
    const baseFreq = 220 + (emotion.valence * 220) // A3 to A4
    const modFreq = emotion.arousal * 10
    
    oscillator.frequency.setValueAtTime(baseFreq, audioContextRef.current.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(
      baseFreq + modFreq,
      audioContextRef.current.currentTime + 0.5
    )
    
    gainNode.gain.setValueAtTime(0.1 * emotion.dominance, audioContextRef.current.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContextRef.current.currentTime + 0.5)
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContextRef.current.destination)
    
    oscillator.start()
    oscillator.stop(audioContextRef.current.currentTime + 0.5)
  }

  const initiateDream = async () => {
    if (!inputValue.trim()) return

    setDreamState(prev => ({
      ...prev,
      seed: inputValue,
      isProcessing: true,
      phase: 'awakening'
    }))
    setIsPlaying(true)

    try {
      const response = await fetch('/api/dream/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: inputValue })
      })

      if (!response.ok) throw new Error('Failed to initiate dream')

      const data = await response.json()
      
      setDreamState(prev => ({
        ...prev,
        isProcessing: false,
        consciousness: data?.consciousness || prev.consciousness,
        emotion: data?.consciousness?.emotion || prev.emotion,
        glyphs: data?.consciousness?.glyphs || prev.glyphs,
        timeline: {
          branches: data?.consciousness?.timeline?.branches || data?.timeline?.branches || [],
          selectedPath: prev.timeline.selectedPath || []
        },
        narrative: data?.interpretation || prev.narrative
      }))
      
      // SSE stream is automatically handled by useSSE hook
    } catch (error) {
      console.error('Failed to initiate dream:', error)
      setDreamState(prev => ({
        ...prev,
        isProcessing: false
      }))
      setIsPlaying(false)
    }
  }

  const handleTimelineBranch = (branchPath: number[]) => {
    setDreamState(prev => ({
      ...prev,
      timeline: {
        ...prev.timeline,
        selectedPath: branchPath
      }
    }))
    // Timeline selections will be handled by the consciousness stream
  }

  const handleGlyphComposition = (glyphs: string[]) => {
    setDreamState(prev => ({
      ...prev,
      glyphs
    }))
    // Glyph compositions will be handled by the consciousness stream
  }

  const handleMemoryIntegration = (memory: any) => {
    setDreamState(prev => ({
      ...prev,
      memories: [...prev.memories, memory]
    }))
    // Memory integrations will be handled by the consciousness stream
  }

  const crystallizeDream = async () => {
    setDreamState(prev => ({
      ...prev,
      phase: 'crystallization',
      isProcessing: true
    }))

    try {
      const response = await fetch('/api/dream/crystallize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dreamId: `dream-${Date.now()}`,
          seed: dreamState.seed,
          phase: dreamState.phase,
          consciousness: dreamState.consciousness,
          emotion: dreamState.emotion,
          glyphs: dreamState.glyphs,
          selectedBranches: (dreamState.timeline?.selectedPath || []).map(i => `branch-${i}`),
          memories: dreamState.memories,
          interactions: {
            glyphManipulations: dreamState.glyphs.length,
            timelineExplorations: (dreamState.timeline?.selectedPath || []).length,
            emotionalResonances: 10,
            memoryIntegrations: dreamState.memories.length
          }
        })
      })

      if (!response.ok) throw new Error('Failed to crystallize dream')

      const data = await response.json()
      
      setDreamState(prev => ({
        ...prev,
        narrative: data.artifact?.narrative || data.narrative,
        isProcessing: false
      }))
      
      // Show crystallized dream artifact
      if (data.artifact) {
        console.log('Dream crystallized:', data.artifact)
        // Could open a modal or redirect to view the artifact
      }
    } catch (error) {
      console.error('Failed to crystallize dream:', error)
      setDreamState(prev => ({
        ...prev,
        isProcessing: false
      }))
    }
  }

  const resetDream = () => {
    setDreamState({
      seed: '',
      consciousness: { awareness: 0, coherence: 0, depth: 0 },
      emotion: { valence: 0.5, arousal: 0.5, dominance: 0.5 },
      glyphs: [],
      timeline: { branches: [], selectedPath: [] },
      memories: [],
      narrative: '',
      isProcessing: false,
      phase: 'seed'
    })
    setInputValue('')
    setIsPlaying(false)
  }

  const phaseDescriptions = {
    seed: 'Plant your dream seed',
    awakening: 'Consciousness awakening...',
    exploration: 'Exploring timeline branches',
    creation: 'Composing symbolic GLYPHs',
    resonance: 'Achieving emotional resonance',
    integration: 'Weaving memories into dream',
    crystallization: 'Dream crystallizing into reality'
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-indigo-950/20 to-purple-950/20 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-5xl md:text-6xl font-ultralight mb-4">
            <span className="gradient-text">Dream Weaver</span>
          </h1>
          <p className="text-xl text-primary-light/70">
            {phaseDescriptions[dreamState.phase]}
          </p>
        </motion.div>

        {/* Control Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-panel p-6 rounded-2xl mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            {/* Dream Seed Input */}
            <div className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && initiateDream()}
                  placeholder="Enter your dream seed..."
                  disabled={dreamState.phase !== 'seed' || dreamState.isProcessing}
                  className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/40 focus:outline-none focus:border-trinity-consciousness/50 disabled:opacity-50"
                />
                <button
                  onClick={() => setVoiceInput(!voiceInput)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <Mic className={`w-5 h-5 ${voiceInput ? 'text-red-400' : 'text-white/60'}`} />
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              {dreamState.phase === 'seed' ? (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={initiateDream}
                  disabled={!inputValue.trim() || dreamState.isProcessing}
                  className="px-6 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {dreamState.isProcessing ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Sparkles className="w-5 h-5" />
                  )}
                  Begin Dream
                </motion.button>
              ) : (
                <>
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="p-4 bg-white/10 hover:bg-white/20 rounded-xl transition-colors"
                  >
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={resetDream}
                    className="p-4 bg-white/10 hover:bg-white/20 rounded-xl transition-colors"
                  >
                    <RefreshCw className="w-5 h-5" />
                  </button>
                </>
              )}
              
              <button
                onClick={() => setAudioEnabled(!audioEnabled)}
                className="p-4 bg-white/10 hover:bg-white/20 rounded-xl transition-colors"
              >
                <Volume2 className={`w-5 h-5 ${audioEnabled ? 'text-white' : 'text-white/40'}`} />
              </button>
            </div>
          </div>

          {/* Phase Progress */}
          {dreamState.phase !== 'seed' && (
            <div className="mt-6">
              <div className="flex items-center justify-between text-xs text-white/60 mb-2">
                <span>Dream Progress</span>
                <span className="capitalize">{dreamState.phase}</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-600"
                  initial={{ width: '0%' }}
                  animate={{ 
                    width: `${
                      ['seed', 'awakening', 'exploration', 'creation', 'resonance', 'integration', 'crystallization']
                        .indexOf(dreamState.phase) * (100 / 6)
                    }%` 
                  }}
                  transition={{ duration: 1 }}
                />
              </div>
            </div>
          )}
        </motion.div>

        {/* Main Dream Interface */}
        <AnimatePresence mode="wait">
          {dreamState.phase !== 'seed' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.5 }}
              className="grid lg:grid-cols-2 gap-6"
            >
              {/* Left Column - Visualizations */}
              <div className="space-y-6">
                {/* Consciousness Visualizer */}
                <div className="glass-panel p-6 rounded-2xl">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium flex items-center gap-2">
                      <Brain className="w-5 h-5 text-trinity-consciousness" />
                      Consciousness Mirror
                    </h3>
                    <div className="flex gap-4 text-xs">
                      <span>Awareness: {(dreamState.consciousness.awareness * 100).toFixed(0)}%</span>
                      <span>Coherence: {(dreamState.consciousness.coherence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className="h-64 rounded-lg overflow-hidden">
                    <ConsciousnessVisualizer
                      consciousness={dreamState.consciousness}
                      emotion={dreamState.emotion}
                      glyphs={dreamState.glyphs}
                    />
                  </div>
                </div>

                {/* Emotional Resonance */}
                <div className="glass-panel p-6 rounded-2xl">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium flex items-center gap-2">
                      <Heart className="w-5 h-5 text-red-400" />
                      Emotional Resonance
                    </h3>
                  </div>
                  <EmotionalResonance
                    emotion={dreamState.emotion}
                    onEmotionChange={(emotion) => setDreamState(prev => ({ ...prev, emotion }))}
                  />
                </div>
              </div>

              {/* Right Column - Interactive Elements */}
              <div className="space-y-6">
                {/* Timeline Explorer */}
                {(dreamState.phase === 'exploration' || dreamState.phase === 'awakening') && (
                  <div className="glass-panel p-6 rounded-2xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Zap className="w-5 h-5 text-yellow-400" />
                        Timeline Explorer
                      </h3>
                    </div>
                    <TimelineExplorer
                      timeline={dreamState.timeline || { branches: [], selectedPath: [] }}
                      onBranchSelect={handleTimelineBranch}
                    />
                  </div>
                )}

                {/* GLYPH Composer */}
                {(dreamState.phase === 'creation' || dreamState.phase === 'resonance') && (
                  <div className="glass-panel p-6 rounded-2xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Layers className="w-5 h-5 text-blue-400" />
                        GLYPH Composer
                      </h3>
                    </div>
                    <GlyphComposer
                      glyphs={dreamState.glyphs}
                      onGlyphUpdate={handleGlyphComposition}
                    />
                  </div>
                )}

                {/* Memory Integrator */}
                {dreamState.phase === 'integration' && (
                  <div className="glass-panel p-6 rounded-2xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Eye className="w-5 h-5 text-purple-400" />
                        Memory Weaver
                      </h3>
                    </div>
                    <MemoryIntegrator
                      memories={dreamState.memories}
                      onMemoryAdd={handleMemoryIntegration}
                    />
                  </div>
                )}

                {/* Dream Narrative */}
                {dreamState.narrative && (
                  <div className="glass-panel p-6 rounded-2xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium">Dream Narrative</h3>
                      <div className="flex gap-2">
                        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                          <Download className="w-4 h-4" />
                        </button>
                        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                          <Share2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="prose prose-invert max-w-none">
                      <p className="text-primary-light/80 leading-relaxed">
                        {dreamState.narrative}
                      </p>
                    </div>
                  </div>
                )}

                {/* Crystallize Button */}
                {dreamState.phase === 'integration' && !dreamState.narrative && (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={crystallizeDream}
                    disabled={dreamState.isProcessing}
                    className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {dreamState.isProcessing ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        Crystallize Dream
                      </>
                    )}
                  </motion.button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}