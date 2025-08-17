'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain, Heart, Zap, Eye, Layers, Volume2, VolumeX, 
  RotateCcw, Sparkles, Play, Pause
} from 'lucide-react'
import ConsciousnessVisualizer from './ConsciousnessVisualizer'
import EmotionalResonance from './EmotionalResonance'
import TimelineExplorer from './TimelineExplorer'
import GlyphComposer from './GlyphComposer'
import MemoryIntegrator from './MemoryIntegrator'
import dreamCopy from './dw_copy.json'

type Phase = 'seed' | 'awakening' | 'exploration' | 'creation' | 'resonance' | 'integration' | 'crystallization'

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
  phase: Phase
}

interface ConsciousnessJourneyProps {
  dreamState: DreamState
  setDreamState: (state: DreamState | ((prev: DreamState) => DreamState)) => void
  onReset: () => void
  audioEnabled: boolean
  setAudioEnabled: (enabled: boolean) => void
}

export default function ConsciousnessJourney({ 
  dreamState, 
  setDreamState, 
  onReset, 
  audioEnabled, 
  setAudioEnabled 
}: ConsciousnessJourneyProps) {
  const [isPlaying, setIsPlaying] = useState(true)
  const [revealedElements, setRevealedElements] = useState<string[]>([])

  // Progressive revelation based on phase
  useEffect(() => {
    const revelationMap: Record<Phase, string[]> = {
      seed: [],
      awakening: ['consciousness'],
      exploration: ['consciousness', 'timeline'],
      creation: ['consciousness', 'timeline', 'glyphs'],
      resonance: ['consciousness', 'timeline', 'glyphs', 'emotions'],
      integration: ['consciousness', 'timeline', 'glyphs', 'emotions', 'memories'],
      crystallization: ['consciousness', 'timeline', 'glyphs', 'emotions', 'memories', 'narrative']
    }
    
    setRevealedElements(revelationMap[dreamState.phase] || [])
  }, [dreamState.phase])

  const getCurrentPhaseData = () => {
    return dreamCopy.phases[dreamState.phase] || dreamCopy.phases.seed
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
      
    } catch (error) {
      console.error('Failed to crystallize dream:', error)
      setDreamState(prev => ({
        ...prev,
        isProcessing: false
      }))
    }
  }

  const phaseData = getCurrentPhaseData()

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-indigo-950/10 to-purple-950/10">
      {/* Floating Control Panel */}
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 1 }}
        className="fixed top-6 left-6 right-6 z-50"
      >
        <div className="max-w-4xl mx-auto">
          <div className="glass-panel p-4 rounded-2xl flex items-center justify-between">
            {/* Phase Status */}
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-medium text-white breathe-text">
                  {phaseData.title}
                </h2>
                <p className="text-sm text-white/60" role="status" aria-live="polite">
                  {phaseData.status}
                </p>
              </div>
            </div>

            {/* Progress Indicator */}
            <div className="hidden md:flex items-center space-x-2">
              {Object.keys(dreamCopy.phases).map((phase, index) => (
                <div
                  key={phase}
                  className={`w-3 h-3 rounded-full transition-all duration-500 ${
                    index <= Object.keys(dreamCopy.phases).indexOf(dreamState.phase)
                      ? 'bg-purple-400 scale-110'
                      : 'bg-white/20'
                  }`}
                />
              ))}
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title={isPlaying ? 'Pause' : 'Resume'}
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              </button>
              <button
                onClick={() => setAudioEnabled(!audioEnabled)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Toggle Audio"
              >
                {audioEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
              <button
                onClick={onReset}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Reset Dream"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Journey Space */}
      <div className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            
            {/* Left Column - Consciousness Visualization */}
            <div className="space-y-6">
              <AnimatePresence>
                {revealedElements.includes('consciousness') && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="glass-panel p-6 rounded-2xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Brain className="w-5 h-5 text-purple-400" />
                        {dreamCopy.components.consciousness_mirror.title}
                      </h3>
                      <div className="flex gap-4 text-xs text-white/60">
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
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {revealedElements.includes('emotions') && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="glass-panel p-6 rounded-2xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Heart className="w-5 h-5 text-red-400" />
                        {dreamCopy.components.emotional_resonance.title}
                      </h3>
                    </div>
                    <EmotionalResonance
                      emotion={dreamState.emotion}
                      onEmotionChange={(emotion) => setDreamState(prev => ({ ...prev, emotion }))}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Right Column - Interactive Elements */}
            <div className="space-y-6">
              <AnimatePresence>
                {revealedElements.includes('timeline') && dreamState.phase === 'exploration' && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="glass-panel p-6 rounded-2xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Zap className="w-5 h-5 text-yellow-400" />
                        {dreamCopy.components.timeline_explorer.title}
                      </h3>
                    </div>
                    <TimelineExplorer
                      timeline={dreamState.timeline}
                      onBranchSelect={(branchPath) => setDreamState(prev => ({
                        ...prev,
                        timeline: { ...prev.timeline, selectedPath: branchPath }
                      }))}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {revealedElements.includes('glyphs') && (dreamState.phase === 'creation' || dreamState.phase === 'resonance') && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="glass-panel p-6 rounded-2xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Layers className="w-5 h-5 text-blue-400" />
                        {dreamCopy.components.glyph_composer.title}
                      </h3>
                    </div>
                    <GlyphComposer
                      glyphs={dreamState.glyphs}
                      onGlyphUpdate={(glyphs) => setDreamState(prev => ({ ...prev, glyphs }))}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {revealedElements.includes('memories') && dreamState.phase === 'integration' && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="glass-panel p-6 rounded-2xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium flex items-center gap-2">
                        <Eye className="w-5 h-5 text-purple-400" />
                        {dreamCopy.components.memory_weaver.title}
                      </h3>
                    </div>
                    <MemoryIntegrator
                      memories={dreamState.memories}
                      onMemoryAdd={(memory) => setDreamState(prev => ({
                        ...prev,
                        memories: [...prev.memories, memory]
                      }))}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {revealedElements.includes('narrative') && dreamState.narrative && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="glass-panel p-6 rounded-2xl"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-medium">Dream Crystallization</h3>
                    </div>
                    <div className="prose prose-invert max-w-none">
                      <p className="text-white/80 leading-relaxed">
                        {dreamState.narrative}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Crystallize Action */}
              <AnimatePresence>
                {dreamState.phase === 'integration' && !dreamState.narrative && (
                  <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1 }}
                  >
                    <motion.button
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={crystallizeDream}
                      disabled={dreamState.isProcessing}
                      className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover:from-purple-400 hover:to-pink-500 transition-all duration-500"
                    >
                      <Sparkles className="w-5 h-5" />
                      {dreamCopy.actions.crystallize_dream}
                    </motion.button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}