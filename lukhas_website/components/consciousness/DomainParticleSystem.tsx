'use client'

import { useEffect, useRef, useState } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'

interface ParticleConfig {
  count: number
  speed: number
  size: number
  opacity: number
  color: string
  behavior: 'neural' | 'biometric' | 'quantum' | 'collaborative' | 'data' | 'creative' | 'cloud' | 'compliance' | 'enterprise' | 'experimental' | 'corporate'
}

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  hue: number
  phase: number
  energy: number
}

/**
 * Domain-Specific Particle System
 * 
 * Each LUKHAS domain has unique consciousness visualization patterns:
 * - lukhas.ai: Neural network patterns with synaptic connections
 * - lukhas.id: Biometric security patterns with authentication flows
 * - lukhas.team: Collaborative consciousness with team synchronization
 * - lukhas.dev: Data flow patterns with API connections
 * - lukhas.io: High-performance streaming data patterns
 * - lukhas.store: Creative marketplace energy with app interactions
 * - lukhas.cloud: Distributed computing patterns with cluster formations
 * - lukhas.eu: Compliance-aware patterns with regulatory boundaries
 * - lukhas.us: Enterprise stability patterns with business workflows
 * - lukhas.xyz: Experimental chaos patterns with research dynamics
 * - lukhas.com: Corporate structure patterns with professional flows
 */
export default function DomainParticleSystem() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const particlesRef = useRef<Particle[]>([])
  const [isInitialized, setIsInitialized] = useState(false)
  
  const { domainState } = useDomainConsciousness()
  
  // Domain-specific particle configurations
  const getParticleConfig = (domain: string): ParticleConfig => {
    const configs: Record<string, ParticleConfig> = {
      'lukhas.ai': {
        count: 150,
        speed: 0.8,
        size: 3,
        opacity: 0.7,
        color: '#00D4FF',
        behavior: 'neural'
      },
      'lukhas.id': {
        count: 80,
        speed: 0.5,
        size: 4,
        opacity: 0.8,
        color: '#7C3AED',
        behavior: 'biometric'
      },
      'lukhas.team': {
        count: 120,
        speed: 0.6,
        size: 3.5,
        opacity: 0.6,
        color: '#10B981',
        behavior: 'collaborative'
      },
      'lukhas.dev': {
        count: 200,
        speed: 1.2,
        size: 2,
        opacity: 0.9,
        color: '#06B6D4',
        behavior: 'data'
      },
      'lukhas.io': {
        count: 300,
        speed: 1.5,
        size: 1.5,
        opacity: 0.8,
        color: '#3B82F6',
        behavior: 'data'
      },
      'lukhas.store': {
        count: 100,
        speed: 0.7,
        size: 4,
        opacity: 0.7,
        color: '#F59E0B',
        behavior: 'creative'
      },
      'lukhas.cloud': {
        count: 250,
        speed: 0.4,
        size: 2.5,
        opacity: 0.5,
        color: '#8B5CF6',
        behavior: 'cloud'
      },
      'lukhas.eu': {
        count: 90,
        speed: 0.3,
        size: 3,
        opacity: 0.8,
        color: '#059669',
        behavior: 'compliance'
      },
      'lukhas.us': {
        count: 110,
        speed: 0.4,
        size: 3.2,
        opacity: 0.7,
        color: '#DC2626',
        behavior: 'enterprise'
      },
      'lukhas.xyz': {
        count: 180,
        speed: 2.0,
        size: 2.8,
        opacity: 0.9,
        color: '#EC4899',
        behavior: 'experimental'
      },
      'lukhas.com': {
        count: 100,
        speed: 0.3,
        size: 3.5,
        opacity: 0.6,
        color: '#6366F1',
        behavior: 'corporate'
      }
    }
    
    return configs[domain] || configs['lukhas.ai']
  }

  // Initialize particles based on domain
  const initializeParticles = (canvas: HTMLCanvasElement, config: ParticleConfig) => {
    const particles: Particle[] = []
    
    for (let i = 0; i < config.count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * config.speed,
        vy: (Math.random() - 0.5) * config.speed,
        size: config.size + Math.random() * 2,
        opacity: config.opacity + Math.random() * 0.3,
        hue: 0,
        phase: Math.random() * Math.PI * 2,
        energy: Math.random()
      })
    }
    
    return particles
  }

  // Render particles with domain-specific behaviors
  const renderParticles = (ctx: CanvasRenderingContext2D, particles: Particle[], config: ParticleConfig, coherence: number) => {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
    
    // Create gradient background based on consciousness coherence
    const gradient = ctx.createRadialGradient(
      ctx.canvas.width / 2, ctx.canvas.height / 2, 0,
      ctx.canvas.width / 2, ctx.canvas.height / 2, ctx.canvas.width / 2
    )
    
    const alpha = coherence * 0.1
    gradient.addColorStop(0, `${config.color}${Math.floor(alpha * 255).toString(16).padStart(2, '0')}`)
    gradient.addColorStop(1, `${config.color}00`)
    
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height)
    
    // Render connections between nearby particles
    if (config.behavior === 'neural' || config.behavior === 'collaborative') {
      ctx.strokeStyle = `${config.color}20`
      ctx.lineWidth = 1
      
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          if (distance < 100) {
            const opacity = (100 - distance) / 100 * coherence
            ctx.globalAlpha = opacity * 0.5
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }
    }
    
    // Render particles with domain-specific effects
    particles.forEach((particle, index) => {
      ctx.globalAlpha = particle.opacity * coherence
      
      // Apply domain-specific visual effects
      switch (config.behavior) {
        case 'neural':
          // Neural synapses - pulsing connections
          ctx.fillStyle = config.color
          ctx.shadowBlur = 15
          ctx.shadowColor = config.color
          break
          
        case 'biometric':
          // Biometric scanner patterns - concentric rings
          ctx.strokeStyle = config.color
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.arc(particle.x, particle.y, particle.size * (1 + Math.sin(particle.phase) * 0.5), 0, Math.PI * 2)
          ctx.stroke()
          break
          
        case 'quantum':
          // Quantum superposition - overlapping possibilities
          ctx.fillStyle = config.color
          ctx.globalAlpha *= 0.3
          for (let i = 0; i < 3; i++) {
            ctx.beginPath()
            ctx.arc(
              particle.x + Math.cos(particle.phase + i * Math.PI / 3) * 10,
              particle.y + Math.sin(particle.phase + i * Math.PI / 3) * 10,
              particle.size,
              0,
              Math.PI * 2
            )
            ctx.fill()
          }
          return
          
        case 'data':
          // Data streams - flowing patterns
          ctx.fillStyle = config.color
          ctx.shadowBlur = 8
          ctx.shadowColor = config.color
          break
          
        case 'experimental':
          // Chaotic patterns - random color shifts
          const hue = (particle.hue + index * 10) % 360
          ctx.fillStyle = `hsl(${hue}, 70%, 60%)`
          ctx.shadowBlur = 20
          ctx.shadowColor = ctx.fillStyle
          break
          
        default:
          ctx.fillStyle = config.color
          ctx.shadowBlur = 10
          ctx.shadowColor = config.color
      }
      
      // Draw main particle
      if (config.behavior !== 'biometric' && config.behavior !== 'quantum') {
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fill()
      }
      
      // Reset shadow
      ctx.shadowBlur = 0
    })
  }

  // Update particle positions and physics
  const updateParticles = (particles: Particle[], config: ParticleConfig, canvas: HTMLCanvasElement) => {
    particles.forEach((particle) => {
      // Update position
      particle.x += particle.vx
      particle.y += particle.vy
      
      // Update phase for animations
      particle.phase += 0.02
      
      // Update hue for experimental domain
      if (config.behavior === 'experimental') {
        particle.hue += 1
      }
      
      // Boundary conditions
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      // Keep particles in bounds
      particle.x = Math.max(0, Math.min(canvas.width, particle.x))
      particle.y = Math.max(0, Math.min(canvas.height, particle.y))
      
      // Add domain-specific behaviors
      switch (config.behavior) {
        case 'collaborative':
          // Particles tend to cluster
          const centerX = canvas.width / 2
          const centerY = canvas.height / 2
          const attractionForce = 0.001
          particle.vx += (centerX - particle.x) * attractionForce
          particle.vy += (centerY - particle.y) * attractionForce
          break
          
        case 'cloud':
          // Particles form cloud-like clusters
          particle.vx += (Math.random() - 0.5) * 0.01
          particle.vy += (Math.random() - 0.5) * 0.01
          particle.vx *= 0.998
          particle.vy *= 0.998
          break
          
        case 'experimental':
          // Chaotic movement
          particle.vx += (Math.random() - 0.5) * 0.1
          particle.vy += (Math.random() - 0.5) * 0.1
          particle.vx = Math.max(-3, Math.min(3, particle.vx))
          particle.vy = Math.max(-3, Math.min(3, particle.vy))
          break
      }
    })
  }

  // Animation loop
  const animate = () => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx || !domainState) return
    
    const config = getParticleConfig(domainState.domain)
    const particles = particlesRef.current
    
    if (particles.length === 0) {
      particlesRef.current = initializeParticles(canvas, config)
      return
    }
    
    updateParticles(particles, config, canvas)
    renderParticles(ctx, particles, config, domainState.coherence)
    
    animationRef.current = requestAnimationFrame(animate)
  }

  // Initialize and start animation
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !domainState || isInitialized) return
    
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
    }
    
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    
    const config = getParticleConfig(domainState.domain)
    particlesRef.current = initializeParticles(canvas, config)
    
    setIsInitialized(true)
    animate()
    
    return () => {
      window.removeEventListener('resize', resizeCanvas)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [domainState, isInitialized])

  // Restart animation when domain changes
  useEffect(() => {
    if (!domainState) return
    
    setIsInitialized(false)
    particlesRef.current = []
    
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
  }, [domainState?.domain])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ 
        background: 'transparent',
        zIndex: 1
      }}
    />
  )
}