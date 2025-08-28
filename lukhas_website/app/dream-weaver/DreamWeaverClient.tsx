'use client'

import { useState, useRef } from 'react'
import { Mic, Send, Sparkles } from 'lucide-react'
import { DreamScene } from '@/components/dream/DreamScene'
import { toast } from 'sonner'
import Textarea from 'react-textarea-autosize'
import { motion, AnimatePresence } from 'framer-motion'

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
  texture_url:string
  dream_id: string
}

export default function DreamWeaverClient() {
  const [dreamSeed, setDreamSeed] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [dreamManifest, setDreamManifest] = useState<DreamManifest | null>(null)
  const [isInputError, setIsInputError] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const handleWeaveDream = async () => {
    if (!dreamSeed.trim()) {
      setIsInputError(true)
      setTimeout(() => setIsInputError(false), 500)
      return
    }
    setIsLoading(true)
    setDreamManifest(null)
    toast.info('Weaving your dream... This can take a moment.')

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
      toast.success('Your dream has unfolded!')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred'
      toast.error(`Failed to weave dream: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        toast.loading('Transcribing your voice...');
        try {
          const response = await fetch('/api/dream-weaver/transcribe', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Transcription failed');
          }

          const result = await response.json();
          setDreamSeed(result.transcription);
          toast.success('Transcription complete!');
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
          toast.error(`Transcription failed: ${errorMessage}`);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      toast.success('Recording started...');
    } catch (err) {
      toast.error('Could not start recording. Please grant microphone permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      toast.info('Recording stopped.');
    }
  };

  const handleVoiceInput = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleCrystallize = async (manifest: DreamManifest) => {
    toast.loading('Crystallizing dream into memory...')
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
      toast.success(`Dream crystallized successfully! Memory ID: ${result.memoryId}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred'
      toast.error(`Crystallization failed: ${errorMessage}`)
    }
  };

  const shakeAnimation = {
    x: [0, -10, 10, -10, 10, 0],
    transition: { duration: 0.5 },
  }

  const buttonHoverTap = {
    hover: { scale: 1.05 },
    tap: { scale: 0.95 },
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <motion.div
        className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-4"
        animate={isInputError ? shakeAnimation : {}}
      >
        <Textarea
          value={dreamSeed}
          onChange={(e) => setDreamSeed(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleWeaveDream()}
          placeholder="Describe the dream you wish to see... or use your voice."
          className="w-full bg-transparent focus:outline-none p-2 text-lg resize-none"
          minRows={2}
          maxRows={6}
          disabled={isLoading}
        />
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2 text-gray-400">
            <motion.button
              onClick={handleVoiceInput}
              className={`p-2 hover:text-white transition-colors disabled:opacity-50 ${isRecording ? 'text-red-500' : ''}`}
              disabled={isLoading}
              aria-label="Use voice input"
              variants={buttonHoverTap}
              whileHover="hover"
              whileTap="tap"
            >
              <Mic className="w-5 h-5" />
            </motion.button>
            <Sparkles className="w-5 h-5 text-purple-400" />
            <span className="text-sm">Powered by MΛTRIZ</span>
          </div>
          <motion.button
            onClick={handleWeaveDream}
            className="px-4 py-2 bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            disabled={isLoading || !dreamSeed.trim()}
            aria-label="Weave Dream"
            variants={buttonHoverTap}
            whileHover="hover"
            whileTap="tap"
          >
            <Send className="w-5 h-5" />
            <span>Weave</span>
          </motion.button>
        </div>
      </motion.div>

      <AnimatePresence>
        {dreamManifest && (
          <motion.div
            className="mt-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <DreamScene manifest={dreamManifest} />
            <div className="mt-4 text-center">
              <motion.button
                onClick={() => handleCrystallize(dreamManifest)}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                variants={buttonHoverTap}
                whileHover="hover"
                whileTap="tap"
              >
                Crystallize this Dream into Memory
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
