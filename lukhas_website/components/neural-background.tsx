'use client'

import { useEffect, useRef, useState } from 'react'

interface NeuralBackgroundProps {
  className?: string
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
}

export default function NeuralBackground({ className = '' }: NeuralBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animationRef = useRef<number>()
  const [showCanvas, setShowCanvas] = useState(false)

  const initCanvas = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    console.log('🧠 Initializing canvas neural network')

    // Set canvas size
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      
      // Reinitialize particles on resize
      particlesRef.current = Array.from({ length: 60 }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4
      }))
    }

    // Neural network animation - smooth constellation style
    const animate = () => {
      if (!canvas || !ctx) return
      
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Smooth neural network connections
      ctx.globalAlpha = 0.6
      ctx.strokeStyle = 'rgba(180, 200, 255, 0.25)'
      ctx.lineWidth = 1.5
      
      const particles = particlesRef.current
      
      // Update particles with gentle movement
      particles.forEach(p => {
        p.x += p.vx
        p.y += p.vy
        
        // Gentle bounce off edges
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1
        
        // Keep particles within bounds
        p.x = Math.max(0, Math.min(canvas.width, p.x))
        p.y = Math.max(0, Math.min(canvas.height, p.y))
      })

      // Draw constellation-style connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.hypot(dx, dy)
          
          // Constellation-style connection threshold
          if (distance < 140) {
            const opacity = (140 - distance) / 140 * 0.25
            ctx.globalAlpha = opacity
            
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }

      // Draw subtle nodes
      ctx.globalAlpha = 0.4
      ctx.fillStyle = 'rgba(180, 200, 255, 0.8)'
      particles.forEach(p => {
        ctx.beginPath()
        ctx.arc(p.x, p.y, 1.2, 0, Math.PI * 2)
        ctx.fill()
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    // Initialize
    resize()
    animate()
    
    // Handle resize
    window.addEventListener('resize', resize)
    
    return () => {
      window.removeEventListener('resize', resize)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }

  useEffect(() => {
    console.log('🧠 Neural background mounting...')
    
    // Check device capabilities for progressive enhancement
    const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const deviceMemory = (navigator as any).deviceMemory || 4
    const cores = navigator.hardwareConcurrency || 4
    const batterySaver = (navigator as any).connection?.saveData === true

    if (reduceMotion || batterySaver) {
      console.log('🧠 Reduced motion/battery saver - keeping SVG fallback')
      return
    }

    // Progressive enhancement to Canvas for capable devices
    if (deviceMemory >= 4 && cores >= 4) {
      console.log('🧠 Device capable - enhancing to Canvas')
      setShowCanvas(true)
      // Canvas initialization will happen after state update
    }
  }, [])

  // Initialize canvas when showCanvas becomes true
  useEffect(() => {
    if (showCanvas) {
      const cleanup = initCanvas()
      return cleanup
    }
  }, [showCanvas])

  return (
    <div className={`fixed inset-0 pointer-events-none z-0 ${className}`}>
      {/* SVG Fallback - Constellation Pattern */}
      <svg 
        ref={svgRef}
        className={`w-full h-full ${showCanvas ? 'hidden' : ''}`}
        aria-hidden="true" 
        role="img"
        aria-label="Neural constellation background"
      >
        <defs>
          <radialGradient id="neural-gradient" cx="50%" cy="50%">
            <stop offset="0%" stopColor="rgba(58,100,255,0.12)" />
            <stop offset="50%" stopColor="rgba(167,180,255,0.06)" />
            <stop offset="100%" stopColor="rgba(10,12,20,0.9)" />
          </radialGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#neural-gradient)" />
        
        {/* Static constellation pattern */}
        <g opacity="0.1" stroke="rgba(180,200,255,0.3)" strokeWidth="0.5" fill="none">
          {/* Constellation connections */}
          <line x1="15%" y1="25%" x2="35%" y2="15%" />
          <line x1="35%" y1="15%" x2="65%" y2="25%" />
          <line x1="65%" y1="25%" x2="85%" y2="35%" />
          <line x1="25%" y1="45%" x2="45%" y2="35%" />
          <line x1="45%" y1="35%" x2="75%" y2="45%" />
          <line x1="15%" y1="65%" x2="40%" y2="55%" />
          <line x1="40%" y1="55%" x2="70%" y2="65%" />
          <line x1="70%" y1="65%" x2="90%" y2="75%" />
          <line x1="20%" y1="85%" x2="50%" y2="80%" />
          <line x1="50%" y1="80%" x2="80%" y2="85%" />
          
          {/* Cross connections for neural network feel */}
          <line x1="15%" y1="25%" x2="25%" y2="45%" />
          <line x1="65%" y1="25%" x2="75%" y2="45%" />
          <line x1="35%" y1="15%" x2="40%" y2="55%" />
          <line x1="85%" y1="35%" x2="90%" y2="75%" />
        </g>
        
        {/* Constellation nodes */}
        <g opacity="0.4" fill="rgba(180,200,255,0.8)">
          <circle cx="15%" cy="25%" r="1.5" />
          <circle cx="35%" cy="15%" r="2" />
          <circle cx="65%" cy="25%" r="1.5" />
          <circle cx="85%" cy="35%" r="1" />
          <circle cx="25%" cy="45%" r="1" />
          <circle cx="45%" cy="35%" r="2" />
          <circle cx="75%" cy="45%" r="1.5" />
          <circle cx="15%" cy="65%" r="1" />
          <circle cx="40%" cy="55%" r="1.5" />
          <circle cx="70%" cy="65%" r="2" />
          <circle cx="90%" cy="75%" r="1" />
          <circle cx="20%" cy="85%" r="1.5" />
          <circle cx="50%" cy="80%" r="1" />
          <circle cx="80%" cy="85%" r="1.5" />
        </g>
      </svg>

      {/* Canvas Enhancement */}
      {showCanvas && (
        <canvas
          ref={canvasRef}
          className="w-full h-full"
          style={{ background: 'radial-gradient(ellipse at center, rgba(58,100,255,0.12) 0%, rgba(167,180,255,0.06) 50%, rgba(10,12,20,0.9) 100%)' }}
        />
      )}
    </div>
  )
}