'use client'

import React, { useEffect, useRef } from 'react'

interface VoiceMorphingBridgeProps {
  config: any
  onVoiceDataUpdate: (data: { intensity: number; frequency: number }) => void
}

export default function VoiceMorphingBridge({ config, onVoiceDataUpdate }: VoiceMorphingBridgeProps) {
  const bridgeRef = useRef<HTMLDivElement>(null)
  const morphingSystemRef = useRef<any>(null)

  useEffect(() => {
    // Initialize connection to voice reactive morphing system
    const initializeMorphingSystem = () => {
      // Check if the voice reactive morphing system is available
      if (typeof window !== 'undefined') {
        // Create a bridge to the existing voice_reactive_morphing system
        const morphingSystem = {
          currentShape: config.shape || 'sphere',
          targetShape: config.shape || 'sphere',
          morphSpeed: config.morphSpeed || 0.005,
          particleCount: config.particleCount || 2000,
          voiceData: { intensity: 0, frequency: 0 },
          
          // Methods that mirror the original morphing system
          setShape: (shape: string) => {
            morphingSystem.targetShape = shape
            window.dispatchEvent(new CustomEvent('morphing-shape-change', {
              detail: { shape, morphSpeed: morphingSystem.morphSpeed }
            }))
          },
          
          setColor: (color: string) => {
            window.dispatchEvent(new CustomEvent('morphing-color-change', {
              detail: { color }
            }))
          },
          
          setParticleCount: (count: number) => {
            morphingSystem.particleCount = count
            window.dispatchEvent(new CustomEvent('morphing-particle-change', {
              detail: { count }
            }))
          },
          
          setMorphSpeed: (speed: number) => {
            morphingSystem.morphSpeed = speed
            window.dispatchEvent(new CustomEvent('morphing-speed-change', {
              detail: { speed }
            }))
          },
          
          setVoiceData: (voiceData: { intensity: number; frequency: number }) => {
            morphingSystem.voiceData = voiceData
            onVoiceDataUpdate(voiceData)
          },
          
          reset: () => {
            morphingSystem.currentShape = 'sphere'
            morphingSystem.targetShape = 'sphere'
            window.dispatchEvent(new CustomEvent('morphing-reset'))
          },
          
          toggleMicrophone: (enabled: boolean) => {
            window.dispatchEvent(new CustomEvent('morphing-mic-toggle', {
              detail: { enabled }
            }))
          },
          
          toggleAudio: (enabled: boolean) => {
            window.dispatchEvent(new CustomEvent('morphing-audio-toggle', {
              detail: { enabled }
            }))
          }
        }

        // Expose the system globally for integration
        if (typeof window !== 'undefined') {
          (window as any).morphingSystem = morphingSystem
        }
        morphingSystemRef.current = morphingSystem

        // Listen for external morphing commands
        const handleExternalCommand = (event: CustomEvent) => {
          const { command, data } = event.detail
          switch (command) {
            case 'setShape':
              if (data.shape) morphingSystem.setShape(data.shape)
              break
            case 'setColor':
              if (data.color) morphingSystem.setColor(data.color)
              break
            case 'setParticleCount':
              if (data.count) morphingSystem.setParticleCount(data.count)
              break
            case 'reset':
              morphingSystem.reset()
              break
          }
        }

        window.addEventListener('morphing-external-command', handleExternalCommand as EventListener)

        return () => {
          window.removeEventListener('morphing-external-command', handleExternalCommand as EventListener)
        }
      }
    }

    return initializeMorphingSystem()
  }, [])

  // Update morphing system when config changes
  useEffect(() => {
    if (morphingSystemRef.current) {
      const system = morphingSystemRef.current
      
      // Update shape if changed
      if (system.targetShape !== config.shape) {
        system.setShape(config.shape)
      }
      
      // Update particle count if changed
      if (system.particleCount !== config.particleCount) {
        system.setParticleCount(config.particleCount)
      }
      
      // Update morph speed if changed
      if (system.morphSpeed !== config.morphSpeed) {
        system.setMorphSpeed(config.morphSpeed)
      }
      
      // Update color if changed
      if (config.accentColor) {
        system.setColor(config.accentColor)
      }
    }
  }, [config.shape, config.particleCount, config.morphSpeed, config.accentColor])

  // Handle microphone and audio toggles
  useEffect(() => {
    if (morphingSystemRef.current) {
      morphingSystemRef.current.toggleMicrophone(config.micEnabled)
    }
  }, [config.micEnabled])

  useEffect(() => {
    if (morphingSystemRef.current) {
      morphingSystemRef.current.toggleAudio(config.audioEnabled)
    }
  }, [config.audioEnabled])

  // Provide LUKHAS integration API similar to the original
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).lukhasIntegration = {
        state: {
          micEnabled: config.micEnabled,
          audioEnabled: config.audioEnabled,
          isReady: true,
          apiConfig: {},
          visualConfig: {
            particleCount: config.particleCount,
            morphSpeed: config.morphSpeed,
            voiceIntensity: config.voiceSensitivity
          }
        },
        
        sendStatus: () => {
          window.dispatchEvent(new CustomEvent('lukhas-status', {
            detail: {
              ready: true,
              micEnabled: config.micEnabled,
              audioEnabled: config.audioEnabled,
              shape: config.shape,
              particleCount: config.particleCount
            }
          }))
        },
        
        applyVisualConfiguration: (visualConfig: any) => {
          if (morphingSystemRef.current) {
            const system = morphingSystemRef.current
            if (visualConfig.particleCount !== undefined) {
              system.setParticleCount(visualConfig.particleCount)
            }
            if (visualConfig.morphSpeed !== undefined) {
              system.setMorphSpeed(visualConfig.morphSpeed)
            }
            if (visualConfig.shape !== undefined) {
              system.setShape(visualConfig.shape)
            }
          }
        },
        
        toggleMicrophone: (enabled: boolean) => {
          if (morphingSystemRef.current) {
            morphingSystemRef.current.toggleMicrophone(enabled)
          }
        },
        
        toggleAudio: (enabled: boolean) => {
          if (morphingSystemRef.current) {
            morphingSystemRef.current.toggleAudio(enabled)
          }
        }
      }
    }
  }, [config])

  return (
    <div ref={bridgeRef} className="hidden">
      {/* Hidden bridge component - handles integration between systems */}
    </div>
  )
}