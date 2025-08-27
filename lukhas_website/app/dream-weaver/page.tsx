'use client'

import { useState } from 'react'
import { Mic, Send } from 'lucide-react'
import { DreamScene } from '@/components/dream/DreamScene'

// Define the structure of the Dream Manifest for TypeScript
interface DreamManifest {
  narrative: string
  visuals: {
    geometry: string
    movement: string
    colors: string[]
    particle_count: number
  }
  audio_url: string
  texture_url: string
  dream_id: string
}

export default function DreamWeaverPage() {
  const [dreamSeed, setDreamSeed] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [dreamManifest, setDreamManifest] = useState<DreamManifest | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleWeaveDream = async () => {
    if (!dreamSeed.trim()) return
    setIsLoading(true)
    setError(null)
    setDreamManifest(null)

    try {
      const response = await fetch('/api/dream-weaver', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: dreamSeed }),
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`)
      }

      const data: DreamManifest = await response.json()
      setDreamManifest(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceInput = () => {
    // TODO: Implement Whisper API integration here.
    alert('Voice input is not yet implemented.')
  }

  const handleCrystallize = async (manifest: DreamManifest) => {
    try {
      const response = await fetch('/api/dream-weaver/crystallize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(manifest),
      });

      if (!response.ok) {
        throw new Error('Failed to crystallize dream');
      }

      const result = await response.json();
      alert(`Dream crystallized successfully! Memory ID: ${result.memoryId}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-5xl font-thin mb-4">Dream Weaver</h1>
        <p className="text-lg text-gray-400 mb-8">
          Plant a seed of thought, and watch a dream unfold.
        </p>

        <div className="flex items-center bg-gray-800 border border-gray-700 rounded-lg p-2">
          <input
            type="text"
            value={dreamSeed}
            onChange={(e) => setDreamSeed(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleWeaveDream()}
            placeholder="What should the AI dream about?"
            className="flex-grow bg-transparent focus:outline-none p-2"
            disabled={isLoading}
          />
          <button
            onClick={handleVoiceInput}
            className="p-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            disabled={isLoading}
            aria-label="Use voice input"
          >
            <Mic className="w-5 h-5" />
          </button>
          <button
            onClick={handleWeaveDream}
            className="p-2 bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            disabled={isLoading || !dreamSeed.trim()}
            aria-label="Weave Dream"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {isLoading && (
          <div className="mt-8">
            <p className="text-gray-400 animate-pulse">Weaving your dream...</p>
          </div>
        )}

        {error && (
          <div className="mt-8 p-4 bg-red-900/50 border border-red-500 rounded-lg">
            <p className="text-red-400">Error: {error}</p>
          </div>
        )}

        {dreamManifest && (
          <>
            <DreamScene manifest={dreamManifest} />
            <div className="mt-4 text-center">
              <button
                onClick={() => handleCrystallize(dreamManifest)}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                Crystallize this Dream into Memory
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
