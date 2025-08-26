'use client'

import { useEffect, useRef, useState } from 'react'
import { Loader2 } from 'lucide-react'

interface ProteusVisualizerProps {
  micEnabled?: boolean
  audioEnabled?: boolean
}

export default function ProteusVisualizer({
  micEnabled = false,
  audioEnabled = true
}: ProteusVisualizerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Send messages to the iframe when props change
    if (iframeRef.current && iframeRef.current.contentWindow) {
      const message = {
        type: 'updateSettings',
        micEnabled,
        audioEnabled,
      }

      // Wait a bit for iframe to fully load before sending messages
      setTimeout(() => {
        iframeRef.current?.contentWindow?.postMessage(message, '*')
      }, 1000)
    }
  }, [micEnabled, audioEnabled])

  useEffect(() => {
    // Listen for messages from the iframe
    const handleMessage = (event: MessageEvent) => {
      // Security: Only accept messages from our own domain or localhost
      if (event.origin !== window.location.origin && !event.origin.includes('localhost')) {
        return
      }

      if (event.data.type === 'proteusReady') {
        setIsLoading(false)
      } else if (event.data.type === 'proteusError') {
        setError(event.data.message)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [])

  const handleIframeLoad = () => {
    // Give the iframe content time to initialize
    setTimeout(() => {
      setIsLoading(false)
    }, 500)
  }

  const handleIframeError = () => {
    setError('Failed to load PR0T3US visualizer')
    setIsLoading(false)
  }

  // Get the base URL for the voice reactive morphing system
  const getVisualizerUrl = () => {
    // In production, this would be a built and deployed version
    // For development, we'll serve it from the local directory
    const baseUrl = process.env.NEXT_PUBLIC_PROTEUS_URL || '/proteus'
    const params = new URLSearchParams({
      embedded: 'true',
      mic: micEnabled.toString(),
      audio: audioEnabled.toString(),
    })
    return `${baseUrl}?${params.toString()}`
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition"
          >
            Reload
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full">
      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-10">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-4" />
            <p className="text-gray-400">Initializing PR0T3US consciousness engine...</p>
          </div>
        </div>
      )}

      {/* Iframe embedding the PR0T3US system */}
      <iframe
        ref={iframeRef}
        src={getVisualizerUrl()}
        className="w-full h-full border-0"
        allow="microphone; camera"
        onLoad={handleIframeLoad}
        onError={handleIframeError}
        title="PR0T3US Voice-Reactive Morphing System"
      />

      {/* Alternative: Direct integration approach */}
      {/*
        For a more integrated approach, we could:
        1. Import the PR0T3US scripts directly
        2. Initialize them in a useEffect
        3. Render directly to a canvas element

        This would require bundling the voice_reactive_morphing assets
        with the Next.js build process.
      */}
    </div>
  )
}

// Hook for controlling the visualizer from parent components
export function useProteusControl() {
  const sendCommand = (command: string, data?: any) => {
    window.postMessage({
      type: 'proteusCommand',
      command,
      data,
    }, '*')
  }

  return {
    setShape: (shape: string) => sendCommand('setShape', { shape }),
    setColor: (color: string) => sendCommand('setColor', { color }),
    setParticleCount: (count: number) => sendCommand('setParticleCount', { count }),
    reset: () => sendCommand('reset'),
    toggleMic: () => sendCommand('toggleMic'),
    toggleAudio: () => sendCommand('toggleAudio'),
  }
}
