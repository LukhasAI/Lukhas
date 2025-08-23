'use client'

import { useEffect, useRef } from 'react'

interface NeuralBackgroundProps {
  className?: string
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  opacity: number
  size: number
}

export default function NeuralBackground({ className = '' }: NeuralBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animationRef = useRef<number>()
  const isActiveRef = useRef(true)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Check for reduced motion preference
    const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const deviceMemory = (navigator as any).deviceMemory || 4
    const cores = navigator.hardwareConcurrency || 4
    const batterySaver = (navigator as any).connection?.saveData === true

    if (reduceMotion || batterySaver) {
      // Show static pattern
      drawStaticPattern(ctx, canvas.width, canvas.height)
      return
    }

    // Progressive enhancement based on device capabilities
    let particleCount = 30
    if (deviceMemory >= 8 && cores >= 8) {
      particleCount = 60
    } else if (deviceMemory >= 4 && cores >= 4) {
      particleCount = 40
    }

    const resize = () => {
      const { innerWidth, innerHeight } = window
      canvas.width = innerWidth
      canvas.height = innerHeight
      
      // Reinitialize particles on resize
      initParticles(canvas.width, canvas.height, particleCount)
    }

    const initParticles = (width: number, height: number, count: number) => {
      particlesRef.current = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.5 + 0.2,
        size: Math.random() * 2 + 1
      }))
    }

    const animate = () => {
      if (!isActiveRef.current) return
      
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Draw background gradient
      const gradient = ctx.createRadialGradient(
        canvas.width * 0.5, 
        canvas.height * 0.3, 
        0,
        canvas.width * 0.5, 
        canvas.height * 0.3, 
        Math.max(canvas.width, canvas.height) * 0.8
      )
      gradient.addColorStop(0, 'rgba(58,100,255,0.05)')
      gradient.addColorStop(0.5, 'rgba(167,180,255,0.02)')
      gradient.addColorStop(1, 'rgba(10,12,20,0.95)')
      
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      const particles = particlesRef.current
      
      // Update particles
      particles.forEach(particle => {
        particle.x += particle.vx
        particle.y += particle.vy
        
        // Bounce off edges with some dampening
        if (particle.x < 0 || particle.x > canvas.width) {
          particle.vx *= -0.9
          particle.x = Math.max(0, Math.min(canvas.width, particle.x))
        }
        if (particle.y < 0 || particle.y > canvas.height) {
          particle.vy *= -0.9
          particle.y = Math.max(0, Math.min(canvas.height, particle.y))
        }
        
        // Subtle opacity pulsing
        particle.opacity += (Math.random() - 0.5) * 0.01
        particle.opacity = Math.max(0.1, Math.min(0.6, particle.opacity))
      })

      // Draw connections
      ctx.strokeStyle = 'rgba(180,200,255,0.15)'
      ctx.lineWidth = 0.5
      
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.hypot(dx, dy)
          
          if (distance < 120) {
            const opacity = (120 - distance) / 120 * 0.3
            ctx.globalAlpha = opacity * Math.min(particles[i].opacity, particles[j].opacity)
            
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }

      // Draw particles (nodes)
      particles.forEach(particle => {
        ctx.globalAlpha = particle.opacity
        ctx.fillStyle = 'rgba(180,200,255,0.6)'
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fill()
      })
      
      ctx.globalAlpha = 1

      animationRef.current = requestAnimationFrame(animate)
    }

    // Initialize
    resize()
    animate()
    
    window.addEventListener('resize', resize)
    
    // Pause animation when tab is not visible
    const handleVisibilityChange = () => {
      isActiveRef.current = !document.hidden
      if (isActiveRef.current && !animationRef.current) {
        animate()
      }
    }
    
    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      window.removeEventListener('resize', resize)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      isActiveRef.current = false
    }
  }, [])

  const drawStaticPattern = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    // Static fallback pattern for reduced motion
    const gradient = ctx.createRadialGradient(width * 0.5, height * 0.3, 0, width * 0.5, height * 0.3, Math.max(width, height) * 0.8)
    gradient.addColorStop(0, 'rgba(58,100,255,0.03)')
    gradient.addColorStop(1, 'rgba(10,12,20,0.98)')
    
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)
    
    // Draw static nodes
    ctx.fillStyle = 'rgba(180,200,255,0.1)'
    ctx.strokeStyle = 'rgba(180,200,255,0.05)'
    ctx.lineWidth = 1
    
    const nodes = [
      { x: width * 0.2, y: height * 0.3 },
      { x: width * 0.8, y: height * 0.2 },
      { x: width * 0.6, y: height * 0.7 },
      { x: width * 0.3, y: height * 0.8 },
    ]
    
    // Draw connections
    ctx.beginPath()
    ctx.moveTo(nodes[0].x, nodes[0].y)
    ctx.lineTo(nodes[1].x, nodes[1].y)
    ctx.moveTo(nodes[2].x, nodes[2].y)
    ctx.lineTo(nodes[3].x, nodes[3].y)
    ctx.stroke()
    
    // Draw nodes
    nodes.forEach(node => {
      ctx.beginPath()
      ctx.arc(node.x, node.y, 3, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  return (
    <div className={`fixed inset-0 pointer-events-none z-0 ${className}`}>
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ background: '#0a0c14' }}
        aria-hidden="true"
        role="img"
        aria-label="Neural network background animation"
      />
      
      {/* SVG fallback for very low-end devices */}
      <noscript>
        <svg 
          className="absolute inset-0 w-full h-full" 
          aria-hidden="true" 
          role="img"
        >
          <defs>
            <radialGradient id="neural-gradient" cx="50%" cy="30%">
              <stop offset="0%" stopColor="rgba(58,100,255,0.03)" />
              <stop offset="100%" stopColor="rgba(10,12,20,0.98)" />
            </radialGradient>
          </defs>
          <rect width="100%" height="100%" fill="url(#neural-gradient)" />
          <g opacity="0.1" stroke="rgba(180,200,255,0.3)" strokeWidth="1" fill="rgba(180,200,255,0.1)">
            <circle cx="20%" cy="30%" r="3" />
            <circle cx="80%" cy="20%" r="3" />
            <circle cx="60%" cy="70%" r="3" />
            <circle cx="30%" cy="80%" r="3" />
            <line x1="20%" y1="30%" x2="80%" y2="20%" />
            <line x1="60%" y1="70%" x2="30%" y2="80%" />
          </g>
        </svg>
      </noscript>
    </div>
  )
}