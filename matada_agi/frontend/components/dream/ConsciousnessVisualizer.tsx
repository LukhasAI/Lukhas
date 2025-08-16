'use client'

import { useRef, useEffect } from 'react'

interface ConsciousnessVisualizerProps {
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
}

// Fallback 2D visualization for SSR and loading states
function Fallback2DVisualization({ 
  consciousness = { awareness: 0.5, coherence: 0.5, depth: 2 },
  emotion = { valence: 0.5, arousal: 0.5, dominance: 0.5 },
  glyphs = []
}: Partial<ConsciousnessVisualizerProps>) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    let animationId: number

    const animate = () => {
      // Clear canvas with trail effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
      ctx.fillRect(0, 0, width, height)

      // Draw consciousness core
      const centerX = width / 2
      const centerY = height / 2
      const time = Date.now() * 0.001
      const radius = 50 + consciousness.awareness * 50 + Math.sin(time) * 10

      // Create gradient
      const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius)
      gradient.addColorStop(0, `rgba(${255 * emotion.valence}, ${128 * emotion.arousal}, ${255 * emotion.dominance}, 0.8)`)
      gradient.addColorStop(0.5, `rgba(${99}, ${102}, ${241}, 0.4)`)
      gradient.addColorStop(1, 'rgba(99, 102, 241, 0)')

      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2)
      ctx.fill()

      // Draw orbiting glyphs
      glyphs.slice(0, 8).forEach((glyph, i) => {
        const angle = (i / 8) * Math.PI * 2 + time * 0.5
        const orbitRadius = 100 + Math.sin(time + i) * 20
        const x = centerX + Math.cos(angle) * orbitRadius
        const y = centerY + Math.sin(angle) * orbitRadius

        // Glyph glow
        const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, 20)
        glowGradient.addColorStop(0, `rgba(255, 255, 255, ${0.3 + consciousness.coherence * 0.4})`)
        glowGradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
        ctx.fillStyle = glowGradient
        ctx.beginPath()
        ctx.arc(x, y, 20, 0, Math.PI * 2)
        ctx.fill()

        // Draw glyph
        ctx.font = '20px sans-serif'
        ctx.fillStyle = `rgba(255, 255, 255, ${0.5 + consciousness.coherence * 0.5})`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(glyph, x, y)
      })

      // Draw particle field
      const particleCount = 50
      for (let i = 0; i < particleCount; i++) {
        const particleAngle = (i / particleCount) * Math.PI * 2
        const particleRadius = 150 + Math.sin(time * 2 + i * 0.5) * 50 * consciousness.depth / 5
        const px = centerX + Math.cos(particleAngle + time * 0.3) * particleRadius
        const py = centerY + Math.sin(particleAngle + time * 0.3) * particleRadius
        
        ctx.fillStyle = `rgba(${139}, ${92}, ${246}, ${0.1 + consciousness.awareness * 0.2})`
        ctx.beginPath()
        ctx.arc(px, py, 2, 0, Math.PI * 2)
        ctx.fill()
      }

      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [consciousness, emotion, glyphs])

  return (
    <canvas
      ref={canvasRef}
      width={400}
      height={400}
      className="w-full h-full"
      style={{ maxWidth: '100%', maxHeight: '100%' }}
    />
  )
}

export default function ConsciousnessVisualizer(props: ConsciousnessVisualizerProps) {
  // Ensure props have default values
  const safeProps = {
    consciousness: props.consciousness || { awareness: 0.5, coherence: 0.5, depth: 2 },
    emotion: props.emotion || { valence: 0.5, arousal: 0.5, dominance: 0.5 },
    glyphs: props.glyphs || []
  }

  return (
    <div className="w-full h-full relative bg-black/50 rounded-lg overflow-hidden">
      <Fallback2DVisualization {...safeProps} />
      
      <div className="absolute top-2 left-2 text-xs text-white/60">
        <div>Awareness: {(safeProps.consciousness.awareness * 100).toFixed(0)}%</div>
        <div>Coherence: {(safeProps.consciousness.coherence * 100).toFixed(0)}%</div>
        <div>Depth: {safeProps.consciousness.depth.toFixed(2)}</div>
      </div>
      
      <div className="absolute bottom-2 right-2 text-xs text-white/60">
        <div>GLYPHs: {safeProps.glyphs.length}</div>
      </div>
    </div>
  )
}