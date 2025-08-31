'use client'

import { useState, useEffect, useRef } from 'react'
import { Brain, Sparkles, Settings, Layers, Activity, Play, Pause } from 'lucide-react'
import Link from 'next/link'

// Enhanced Particle System with Purple Theme
interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  hue: number
  life: number
  maxLife: number
}

export default function PurpleExperience() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const [particles, setParticles] = useState<Particle[]>([])
  const [isPlaying, setIsPlaying] = useState(true)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [config, setConfig] = useState({
    particleCount: 200,
    morphSpeed: 1.0,
    attractionForce: 0.5,
    particleSize: 2.0,
    colorIntensity: 0.8
  })

  // Initialize particles
  const initializeParticles = () => {
    const newParticles: Particle[] = []
    for (let i = 0; i < config.particleCount; i++) {
      newParticles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        size: Math.random() * config.particleSize + 1,
        opacity: Math.random() * 0.8 + 0.2,
        hue: Math.random() * 60 + 240, // Purple to blue range
        life: Math.random() * 200 + 100,
        maxLife: 300
      })
    }
    setParticles(newParticles)
  }

  // Animation loop
  const animate = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.fillStyle = 'rgba(10, 10, 30, 0.05)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Update and draw particles
    setParticles(prev => {
      const updated = prev.map(particle => {
        // Mouse attraction
        const dx = mousePos.x - particle.x
        const dy = mousePos.y - particle.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 150) {
          const force = (150 - distance) / 150 * config.attractionForce * 0.1
          particle.vx += (dx / distance) * force
          particle.vy += (dy / distance) * force
        }

        // Update position
        particle.x += particle.vx * config.morphSpeed
        particle.y += particle.vy * config.morphSpeed
        
        // Update life
        particle.life -= 1
        particle.opacity = (particle.life / particle.maxLife) * config.colorIntensity
        
        // Bounce off walls
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -0.8
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -0.8
        
        // Keep particles in bounds
        particle.x = Math.max(0, Math.min(canvas.width, particle.x))
        particle.y = Math.max(0, Math.min(canvas.height, particle.y))
        
        return particle
      }).filter(particle => particle.life > 0)

      // Add new particles if needed
      while (updated.length < config.particleCount) {
        updated.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          size: Math.random() * config.particleSize + 1,
          opacity: Math.random() * 0.8 + 0.2,
          hue: Math.random() * 60 + 240,
          life: Math.random() * 200 + 100,
          maxLife: 300
        })
      }

      // Draw particles
      updated.forEach(particle => {
        ctx.save()
        ctx.globalAlpha = particle.opacity
        ctx.fillStyle = `hsl(${particle.hue}, 80%, 60%)`
        ctx.shadowBlur = 10
        ctx.shadowColor = `hsl(${particle.hue}, 80%, 60%)`
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fill()
        ctx.restore()
      })

      // Draw connections
      ctx.strokeStyle = 'rgba(138, 43, 226, 0.3)'
      ctx.lineWidth = 1
      for (let i = 0; i < updated.length; i++) {
        for (let j = i + 1; j < updated.length; j++) {
          const dx = updated[i].x - updated[j].x
          const dy = updated[i].y - updated[j].y
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          if (distance < 80) {
            ctx.globalAlpha = (80 - distance) / 80 * 0.5
            ctx.beginPath()
            ctx.moveTo(updated[i].x, updated[i].y)
            ctx.lineTo(updated[j].x, updated[j].y)
            ctx.stroke()
          }
        }
      }

      return updated
    })

    if (isPlaying) {
      animationRef.current = requestAnimationFrame(animate)
    }
  }

  // Handle mouse movement
  const handleMouseMove = (e: React.MouseEvent) => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const rect = canvas.getBoundingClientRect()
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
  }

  // Setup canvas and start animation
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    initializeParticles()

    window.addEventListener('resize', resizeCanvas)
    
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(animate)
    }

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying, config])

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-black text-white relative overflow-hidden">
      {/* Particle Canvas */}
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-auto cursor-crosshair"
        onMouseMove={handleMouseMove}
        style={{ zIndex: 1 }}
      />

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-20 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-screen-2xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link
              href="/"
              className="text-2xl font-thin tracking-wider text-white hover:text-purple-300 transition-colors"
            >
              LUKHΛS
            </Link>
            <div className="text-xs text-white/60">Purple Experience</div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 rounded-lg bg-white/10 border border-white/20 hover:bg-white/20 transition-colors"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <Link
              href="/experience"
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg hover:opacity-90 transition-opacity text-sm"
            >
              Full Experience
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen pt-20">
        {/* LUKHAS Logo */}
        <div className="text-center mb-12">
          <div className="inline-block p-8 bg-gradient-to-br from-purple-600/20 to-indigo-600/20 rounded-3xl border border-white/20 backdrop-blur-xl shadow-2xl">
            <h1 className="text-8xl md:text-9xl font-thin tracking-[0.3em] text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-indigo-300 to-blue-300 mb-4">
              LUKHΛS
            </h1>
            <p className="text-sm uppercase tracking-[0.2em] text-purple-300/80">
              Consciousness Technology
            </p>
          </div>
        </div>

        {/* Trinity Framework Icons */}
        <div className="flex justify-center space-x-16 mb-16">
          <div className="text-center group">
            <div className="p-4 bg-purple-600/20 rounded-2xl border border-purple-400/30 group-hover:bg-purple-600/30 transition-colors mb-3">
              <Brain className="w-8 h-8 text-purple-300" />
            </div>
            <p className="text-xs uppercase tracking-wider text-purple-200">Identity</p>
          </div>
          <div className="text-center group">
            <div className="p-4 bg-indigo-600/20 rounded-2xl border border-indigo-400/30 group-hover:bg-indigo-600/30 transition-colors mb-3">
              <Sparkles className="w-8 h-8 text-indigo-300" />
            </div>
            <p className="text-xs uppercase tracking-wider text-indigo-200">Consciousness</p>
          </div>
          <div className="text-center group">
            <div className="p-4 bg-blue-600/20 rounded-2xl border border-blue-400/30 group-hover:bg-blue-600/30 transition-colors mb-3">
              <Activity className="w-8 h-8 text-blue-300" />
            </div>
            <p className="text-xs uppercase tracking-wider text-blue-200">Guardian</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-16">
          <Link
            href="/studio"
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:opacity-90 transition-opacity font-medium"
          >
            <Brain className="w-5 h-5 inline mr-2" />
            Open Studio
          </Link>
          <Link
            href="/experience"
            className="px-8 py-4 border border-white/30 rounded-xl hover:bg-white/10 transition-colors font-medium"
          >
            <Layers className="w-5 h-5 inline mr-2" />
            Full Experience
          </Link>
        </div>

        {/* Particle System Description */}
        <div className="max-w-2xl text-center text-white/80 mb-8">
          <p className="text-lg mb-4">
            Experience consciousness through interactive particle systems.
            Move your cursor to attract and influence the flowing neural network.
          </p>
          <p className="text-sm text-white/60">
            Each particle represents a node of awareness, connecting and evolving
            in response to your presence and intention.
          </p>
        </div>
      </main>

      {/* Controls Panel */}
      <div className="fixed bottom-6 left-6 z-20 bg-black/40 backdrop-blur-xl border border-white/20 rounded-2xl p-6 max-w-sm">
        <h3 className="text-lg font-medium mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2 text-purple-300" />
          Particle Controls
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-white/70 mb-2">
              Particle Count: {config.particleCount}
            </label>
            <input
              type="range"
              min="50"
              max="500"
              value={config.particleCount}
              onChange={(e) => setConfig(prev => ({ ...prev, particleCount: parseInt(e.target.value) }))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label className="block text-sm text-white/70 mb-2">
              Morph Speed: {config.morphSpeed.toFixed(1)}x
            </label>
            <input
              type="range"
              min="0.1"
              max="3.0"
              step="0.1"
              value={config.morphSpeed}
              onChange={(e) => setConfig(prev => ({ ...prev, morphSpeed: parseFloat(e.target.value) }))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label className="block text-sm text-white/70 mb-2">
              Attraction: {config.attractionForce.toFixed(1)}
            </label>
            <input
              type="range"
              min="0.1"
              max="2.0"
              step="0.1"
              value={config.attractionForce}
              onChange={(e) => setConfig(prev => ({ ...prev, attractionForce: parseFloat(e.target.value) }))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label className="block text-sm text-white/70 mb-2">
              Particle Size: {config.particleSize.toFixed(1)}
            </label>
            <input
              type="range"
              min="0.5"
              max="5.0"
              step="0.1"
              value={config.particleSize}
              onChange={(e) => setConfig(prev => ({ ...prev, particleSize: parseFloat(e.target.value) }))}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-white/20">
          <div className="flex justify-between text-sm text-white/60">
            <span>Particles: {particles.length}</span>
            <span>FPS: ~60</span>
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="fixed top-20 right-6 z-20 space-y-2">
        <div className="bg-black/40 backdrop-blur-xl border border-green-500/30 rounded-lg px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-green-400">System Active</span>
          </div>
        </div>
        
        <div className="bg-black/40 backdrop-blur-xl border border-purple-500/30 rounded-lg px-4 py-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full" />
            <span className="text-sm text-purple-400">Consciousness Mode</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: linear-gradient(135deg, #8b5cf6, #6366f1);
          cursor: pointer;
          border: 2px solid white;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        
        .slider::-webkit-slider-track {
          width: 100%;
          height: 8px;
          cursor: pointer;
          background: rgba(255,255,255,0.2);
          border-radius: 4px;
        }
      `}</style>
    </div>
  )
}
