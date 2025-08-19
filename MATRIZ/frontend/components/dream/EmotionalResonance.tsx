'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Heart, Activity, TrendingUp, Music, Zap } from 'lucide-react'

interface EmotionalResonanceProps {
  emotion: {
    valence: number // -1 to 1 (negative to positive)
    arousal: number // 0 to 1 (calm to excited)
    dominance: number // 0 to 1 (submissive to dominant)
  }
  onEmotionChange?: (emotion: { valence: number; arousal: number; dominance: number }) => void
}

export default function EmotionalResonance({ emotion, onEmotionChange }: EmotionalResonanceProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const [userEmotion, setUserEmotion] = useState(emotion)
  const [resonanceScore, setResonanceScore] = useState(0)
  const [harmonicFrequencies, setHarmonicFrequencies] = useState<number[]>([])

  useEffect(() => {
    // Calculate resonance between user and AI emotions
    const valenceResonance = 1 - Math.abs(userEmotion.valence - emotion.valence)
    const arousalResonance = 1 - Math.abs(userEmotion.arousal - emotion.arousal)
    const dominanceResonance = 1 - Math.abs(userEmotion.dominance - emotion.dominance)
    
    const totalResonance = (valenceResonance + arousalResonance + dominanceResonance) / 3
    setResonanceScore(totalResonance)

    // Generate harmonic frequencies based on emotions
    const baseFreq = 220 + (emotion.valence * 220) // A3 to A4
    const harmonics = [
      baseFreq,
      baseFreq * 1.5 * emotion.arousal,
      baseFreq * 2 * emotion.dominance,
      baseFreq * 2.5 * totalResonance
    ]
    setHarmonicFrequencies(harmonics)
  }, [emotion, userEmotion])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    let time = 0

    const drawHeatMap = () => {
      // Clear canvas with fade effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, width, height)

      // Draw emotion heat map
      const centerX = width / 2
      const centerY = height / 2

      // AI Emotion Center
      const aiX = centerX + (emotion.valence * width * 0.3)
      const aiY = centerY - (emotion.arousal * height * 0.3)

      // User Emotion Center
      const userX = centerX + (userEmotion.valence * width * 0.3)
      const userY = centerY - (userEmotion.arousal * height * 0.3)

      // Draw gradient circles for emotions
      for (let i = 0; i < 5; i++) {
        const radius = 20 + i * 15
        const alpha = 0.3 - i * 0.05

        // AI emotion gradient
        const aiGradient = ctx.createRadialGradient(aiX, aiY, 0, aiX, aiY, radius)
        aiGradient.addColorStop(0, `rgba(${255 * emotion.valence}, ${128 * emotion.arousal}, ${255 * emotion.dominance}, ${alpha})`)
        aiGradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
        ctx.fillStyle = aiGradient
        ctx.fillRect(0, 0, width, height)

        // User emotion gradient
        const userGradient = ctx.createRadialGradient(userX, userY, 0, userX, userY, radius)
        userGradient.addColorStop(0, `rgba(${255 * userEmotion.valence}, ${255 * userEmotion.arousal}, ${128 * userEmotion.dominance}, ${alpha})`)
        userGradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
        ctx.fillStyle = userGradient
        ctx.fillRect(0, 0, width, height)
      }

      // Draw resonance connection
      if (resonanceScore > 0.5) {
        ctx.strokeStyle = `rgba(${255 * resonanceScore}, ${255 * resonanceScore}, 255, ${resonanceScore * 0.5})`
        ctx.lineWidth = resonanceScore * 3
        ctx.beginPath()
        ctx.moveTo(aiX, aiY)
        
        // Create curved path based on resonance
        const controlX = centerX + Math.sin(time * 0.001) * 50 * resonanceScore
        const controlY = centerY + Math.cos(time * 0.001) * 50 * resonanceScore
        ctx.quadraticCurveTo(controlX, controlY, userX, userY)
        
        ctx.stroke()
      }

      // Draw waveforms based on harmonic frequencies
      ctx.strokeStyle = `rgba(255, 255, 255, 0.1)`
      ctx.lineWidth = 1
      harmonicFrequencies.forEach((freq, index) => {
        ctx.beginPath()
        for (let x = 0; x < width; x++) {
          const y = centerY + Math.sin((x + time) * freq * 0.0001) * 20 * (index + 1)
          if (x === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        }
        ctx.stroke()
      })

      time += 16
      animationRef.current = requestAnimationFrame(drawHeatMap)
    }

    drawHeatMap()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [emotion, userEmotion, resonanceScore, harmonicFrequencies])

  const handleEmotionAdjust = (dimension: 'valence' | 'arousal' | 'dominance', value: number) => {
    const newEmotion = { ...userEmotion, [dimension]: value }
    setUserEmotion(newEmotion)
    if (onEmotionChange) {
      onEmotionChange(newEmotion)
    }
  }

  const emotionColors = {
    valence: emotion.valence > 0 ? '#10b981' : '#ef4444',
    arousal: `hsl(${30 + emotion.arousal * 60}, 100%, 50%)`,
    dominance: `hsl(${240 + emotion.dominance * 60}, 100%, 50%)`
  }

  return (
    <div className="space-y-4">
      {/* Heat Map Canvas */}
      <div className="relative rounded-xl overflow-hidden bg-black/50">
        <canvas
          ref={canvasRef}
          width={400}
          height={200}
          className="w-full h-48"
        />
        
        {/* Overlay Labels */}
        <div className="absolute top-2 left-2 text-xs text-white/60">
          AI Emotion
        </div>
        <div className="absolute top-2 right-2 text-xs text-white/60">
          Your Emotion
        </div>
        <div className="absolute bottom-2 left-2 text-xs text-white/60">
          Resonance: {(resonanceScore * 100).toFixed(0)}%
        </div>
      </div>

      {/* Emotion Sliders */}
      <div className="space-y-3">
        {/* Valence */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4" style={{ color: emotionColors.valence }} />
              <span className="text-sm">Valence</span>
            </div>
            <span className="text-xs text-white/60">
              {userEmotion.valence > 0 ? 'Positive' : 'Negative'} ({(userEmotion.valence * 100).toFixed(0)}%)
            </span>
          </div>
          <div className="relative">
            <input
              type="range"
              min="-1"
              max="1"
              step="0.01"
              value={userEmotion.valence}
              onChange={(e) => handleEmotionAdjust('valence', parseFloat(e.target.value))}
              className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right, #ef4444 0%, #fbbf24 50%, #10b981 100%)`
              }}
            />
            <div 
              className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg pointer-events-none"
              style={{ left: `${(userEmotion.valence + 1) * 50}%`, transform: 'translateX(-50%) translateY(-50%)' }}
            />
          </div>
        </div>

        {/* Arousal */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" style={{ color: emotionColors.arousal }} />
              <span className="text-sm">Arousal</span>
            </div>
            <span className="text-xs text-white/60">
              {userEmotion.arousal > 0.5 ? 'Excited' : 'Calm'} ({(userEmotion.arousal * 100).toFixed(0)}%)
            </span>
          </div>
          <div className="relative">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={userEmotion.arousal}
              onChange={(e) => handleEmotionAdjust('arousal', parseFloat(e.target.value))}
              className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #06b6d4 0%, #fbbf24 50%, #ef4444 100%)`
              }}
            />
            <div 
              className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg pointer-events-none"
              style={{ left: `${userEmotion.arousal * 100}%`, transform: 'translateX(-50%) translateY(-50%)' }}
            />
          </div>
        </div>

        {/* Dominance */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" style={{ color: emotionColors.dominance }} />
              <span className="text-sm">Dominance</span>
            </div>
            <span className="text-xs text-white/60">
              {userEmotion.dominance > 0.5 ? 'Dominant' : 'Submissive'} ({(userEmotion.dominance * 100).toFixed(0)}%)
            </span>
          </div>
          <div className="relative">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={userEmotion.dominance}
              onChange={(e) => handleEmotionAdjust('dominance', parseFloat(e.target.value))}
              className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%)`
              }}
            />
            <div 
              className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg pointer-events-none"
              style={{ left: `${userEmotion.dominance * 100}%`, transform: 'translateX(-50%) translateY(-50%)' }}
            />
          </div>
        </div>
      </div>

      {/* Resonance Indicator */}
      <div className="p-4 bg-white/5 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Music className="w-4 h-4 text-purple-400" />
            <span className="text-sm">Emotional Resonance</span>
          </div>
          <span className="text-sm font-medium" style={{ 
            color: resonanceScore > 0.7 ? '#10b981' : resonanceScore > 0.4 ? '#fbbf24' : '#ef4444' 
          }}>
            {(resonanceScore * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
            initial={{ width: '0%' }}
            animate={{ width: `${resonanceScore * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
        <div className="mt-2 text-xs text-white/60">
          {resonanceScore > 0.7 ? 'Perfect harmony achieved' :
           resonanceScore > 0.4 ? 'Building emotional connection' :
           'Exploring emotional landscape'}
        </div>
      </div>

      {/* Harmonic Frequencies */}
      <div className="flex items-center justify-between p-2 bg-white/5 rounded-lg">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          <span className="text-xs text-white/60">Harmonic Frequencies</span>
        </div>
        <div className="flex gap-1">
          {harmonicFrequencies.map((freq, index) => (
            <div
              key={index}
              className="w-1 bg-gradient-to-t from-yellow-400 to-purple-400 rounded-full"
              style={{ height: `${Math.min(freq / 50, 20)}px` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}