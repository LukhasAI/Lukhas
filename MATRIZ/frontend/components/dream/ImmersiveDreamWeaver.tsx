'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDreamContext } from '@/contexts/DreamContext'
import { useSSE, type DreamEvent } from '@/hooks/useSSE'
import DreamSeedPortal from './DreamSeedPortal'
import ConsciousnessJourney from './ConsciousnessJourney'
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

export default function ImmersiveDreamWeaver() {
  const { setPhase, setIntensity } = useDreamContext()
  const [dreamState, setDreamState] = useState<DreamState>({
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

  const [hasBegun, setHasBegun] = useState(false)
  const [audioEnabled, setAudioEnabled] = useState(true)
  const audioContextRef = useRef<AudioContext | null>(null)

  // SSE connection for consciousness stream
  const { data: streamData, connected, error } = useSSE<DreamEvent>('/api/dream/stream', { 
    debounceMs: 300,
    paused: !hasBegun 
  })

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

  // Initialize audio context
  useEffect(() => {
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

  const handleDreamBegin = async (seed: string) => {
    setDreamState(prev => ({
      ...prev,
      seed,
      isProcessing: true,
      phase: 'awakening'
    }))
    setHasBegun(true)

    try {
      const response = await fetch('/api/dream/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed })
      })

      if (!response.ok) throw new Error('Failed to initiate dream')

      const data = await response.json()
      
      setDreamState(prev => ({
        ...prev,
        isProcessing: false,
        consciousness: data.consciousness || prev.consciousness,
        emotion: data.consciousness?.emotion || prev.emotion,
        glyphs: data.consciousness?.glyphs || prev.glyphs,
        timeline: {
          branches: data.consciousness?.timeline?.branches || [],
          selectedPath: []
        },
        narrative: data.interpretation || prev.narrative
      }))
      
    } catch (error) {
      console.error('Failed to initiate dream:', error)
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
    setHasBegun(false)
  }

  return (
    <div className="relative overflow-hidden">
      {/* Vignette overlay responds to consciousness state */}
      <div className="dw-vignette-overlay" />
      
      <AnimatePresence mode="wait">
        {!hasBegun ? (
          <motion.div key="portal">
            <DreamSeedPortal onDreamBegin={handleDreamBegin} />
          </motion.div>
        ) : (
          <motion.div 
            key="journey"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 2 }}
          >
            <ConsciousnessJourney 
              dreamState={dreamState}
              setDreamState={setDreamState}
              onReset={resetDream}
              audioEnabled={audioEnabled}
              setAudioEnabled={setAudioEnabled}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}