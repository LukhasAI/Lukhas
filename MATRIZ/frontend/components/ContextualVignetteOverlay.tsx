'use client'

import VignetteOverlay from './VignetteOverlay'
import { useDreamContext } from '../contexts/DreamContext'

// Phase-driven intensity mapping as specified in the helper bundle
const phaseMapping = {
  seed: 0.05,
  awakening: 0.1,
  exploration: 0.15,
  creation: 0.2,
  resonance: 0.25,
  integration: 0.3,
  crystallization: 0.35
}

export default function ContextualVignetteOverlay() {
  const { phase, intensity } = useDreamContext()
  
  return (
    <VignetteOverlay
      phase={phase}
      intensity={intensity || undefined}
      mapping={phaseMapping}
      respectReduceMotion={true}
    />
  )
}