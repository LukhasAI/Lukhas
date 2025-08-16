'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

type Phase = 'seed' | 'awakening' | 'exploration' | 'creation' | 'resonance' | 'integration' | 'crystallization'

interface DreamContextValue {
  phase: Phase
  intensity: number
  setPhase: (phase: Phase) => void
  setIntensity: (intensity: number) => void
}

const DreamContext = createContext<DreamContextValue | null>(null)

export function DreamProvider({ children }: { children: ReactNode }) {
  const [phase, setPhase] = useState<Phase>('seed')
  const [intensity, setIntensity] = useState(0)

  return (
    <DreamContext.Provider value={{ phase, intensity, setPhase, setIntensity }}>
      {children}
    </DreamContext.Provider>
  )
}

export function useDreamContext() {
  const context = useContext(DreamContext)
  if (!context) {
    throw new Error('useDreamContext must be used within a DreamProvider')
  }
  return context
}