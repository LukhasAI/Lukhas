'use client'

import React from 'react'
import dynamic from 'next/dynamic'

// Dynamically import the actual visualizer to avoid SSR issues
const MorphingVisualizerInner = dynamic(
  () => import('@/components/morphing-visualizer'),
  { 
    ssr: false,
    loading: () => <div className="w-full h-full bg-black/50 backdrop-blur-xl animate-pulse" />
  }
)

interface AdvancedMorphingVisualizerProps {
  quotedText?: string
  mode?: 'AI' | 'Human'
  voiceIntensity?: number
  showStats?: boolean
  config?: any
}

export default function AdvancedMorphingVisualizer({ 
  quotedText = '',
  mode = 'AI',
  voiceIntensity = 0,
  showStats = false,
  config = {}
}: AdvancedMorphingVisualizerProps) {
  // For now, pass through to the existing MorphingVisualizer
  // We'll enhance this with the advanced features progressively
  const enhancedConfig = {
    ...config,
    particleCount: config.particleCount || 12000,
    baseSize: 0.02,
    glyphText: quotedText,
    voiceSensitivity: config.voiceSensitivity || 1.0
  }
  
  const voiceData = {
    intensity: voiceIntensity,
    frequency: 0
  }
  
  return (
    <div className="w-full h-full relative">
      <MorphingVisualizerInner 
        config={enhancedConfig}
        voiceData={voiceData}
      />
      
      {/* Mode indicator overlay */}
      <div className="absolute top-4 left-4 pointer-events-none">
        <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-lg px-3 py-2">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${mode === 'AI' ? 'bg-blue-500' : 'bg-green-500'}`} />
            <span className="text-xs text-white/80 font-medium">
              {mode} Mode {quotedText && `• "${quotedText.slice(0, 20)}${quotedText.length > 20 ? '...' : ''}"`}
            </span>
          </div>
        </div>
      </div>
      
      {/* Stats overlay if enabled */}
      {showStats && (
        <div className="absolute top-4 right-4 pointer-events-none">
          <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-lg px-3 py-2">
            <div className="text-xs text-white/60">
              Particles: {enhancedConfig.particleCount}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}