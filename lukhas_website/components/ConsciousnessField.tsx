'use client'

import { useEffect, useRef, useState } from 'react'

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  color: string
  type: 'identity' | 'memory' | 'vision' | 'bio' | 'dream' | 'ethics' | 'guardian' | 'quantum'
  energy: number
  pulsePhase: number
  connectionStrength: number
}

interface ConsciousnessFieldProps {
  particleCount?: number
  connectionDistance?: number
  mouseInfluence?: number
  consciousnessLevel?: 'dormant' | 'awakening' | 'active' | 'transcendent'
  enableQuantumEntanglement?: boolean
}

const CONSTELLATION_COLORS = {
  identity: { hex: '#6B46C1', rgb: [107, 70, 193] },    // Purple
  memory: { hex: '#3B82F6', rgb: [59, 130, 246] },     // Blue
  vision: { hex: '#06B6D4', rgb: [6, 182, 212] },      // Cyan
  bio: { hex: '#10B981', rgb: [16, 185, 129] },        // Green
  dream: { hex: '#8B5CF6', rgb: [139, 92, 246] },      // Violet
  ethics: { hex: '#F59E0B', rgb: [245, 158, 11] },     // Amber
  guardian: { hex: '#EF4444', rgb: [239, 68, 68] },    // Red
  quantum: { hex: '#A855F7', rgb: [168, 85, 247] },    // Purple-violet
}

const STAR_TYPES: Array<keyof typeof CONSTELLATION_COLORS> = [
  'identity', 'memory', 'vision', 'bio', 'dream', 'ethics', 'guardian', 'quantum'
]

export default function ConsciousnessField({
  particleCount = 150,
  connectionDistance = 120,
  mouseInfluence = 150,
  consciousnessLevel = 'active',
  enableQuantumEntanglement = true
}: ConsciousnessFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mouseRef = useRef({ x: 0, y: 0 })
  const particlesRef = useRef<Particle[]>([])
  const animationIdRef = useRef<number>()
  const timeRef = useRef(0)
  const [isVisible, setIsVisible] = useState(false)

  // Consciousness-aware particle behavior modifiers
  const getConsciousnessModifiers = () => {
    switch (consciousnessLevel) {
      case 'dormant':
        return { speed: 0.3, opacity: 0.4, connections: 0.5, energy: 0.2 }
      case 'awakening':
        return { speed: 0.6, opacity: 0.6, connections: 0.7, energy: 0.5 }
      case 'active':
        return { speed: 1.0, opacity: 0.8, connections: 1.0, energy: 0.8 }
      case 'transcendent':
        return { speed: 1.5, opacity: 1.0, connections: 1.5, energy: 1.2 }
      default:
        return { speed: 1.0, opacity: 0.8, connections: 1.0, energy: 0.8 }
    }
  }

  useEffect(() => {
    setIsVisible(true)
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !isVisible) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const modifiers = getConsciousnessModifiers()

    // Set canvas size with device pixel ratio for crisp rendering
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      
      canvas.width = rect.width * dpr
      canvas.height = rect.height * dpr
      canvas.style.width = rect.width + 'px'
      canvas.style.height = rect.height + 'px'
      
      ctx.scale(dpr, dpr)
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Create consciousness particles
    const createParticles = () => {
      particlesRef.current = []
      for (let i = 0; i < particleCount; i++) {
        const starType = STAR_TYPES[Math.floor(Math.random() * STAR_TYPES.length)]
        const baseSpeed = (Math.random() - 0.5) * 2 * modifiers.speed
        
        particlesRef.current.push({
          x: Math.random() * (canvas.clientWidth || window.innerWidth),
          y: Math.random() * (canvas.clientHeight || window.innerHeight),
          vx: baseSpeed,
          vy: baseSpeed,
          size: Math.random() * 2 + 0.5,
          opacity: (Math.random() * 0.4 + 0.3) * modifiers.opacity,
          color: CONSTELLATION_COLORS[starType].hex,
          type: starType,
          energy: Math.random() * modifiers.energy,
          pulsePhase: Math.random() * Math.PI * 2,
          connectionStrength: Math.random() * modifiers.connections
        })
      }
    }

    createParticles()

    // Enhanced mouse interaction
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      mouseRef.current.x = e.clientX - rect.left
      mouseRef.current.y = e.clientY - rect.top
    }

    document.addEventListener('mousemove', handleMouseMove)

    // Quantum entanglement effect
    const applyQuantumEntanglement = (particle: Particle, otherParticle: Particle, distance: number) => {
      if (!enableQuantumEntanglement) return
      
      // Create quantum-like correlations between particles
      if (distance < connectionDistance * 0.5 && particle.type === otherParticle.type) {
        const correlation = 0.02
        particle.vx += (otherParticle.vx - particle.vx) * correlation
        particle.vy += (otherParticle.vy - particle.vy) * correlation
        particle.energy += (otherParticle.energy - particle.energy) * correlation * 0.1
      }
    }

    // Main animation loop
    const animate = () => {
      if (!canvas.clientWidth || !canvas.clientHeight) {
        animationIdRef.current = requestAnimationFrame(animate)
        return
      }

      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight)

      timeRef.current += 0.016 // ~60fps

      particlesRef.current.forEach((particle, i) => {
        // Mouse influence with consciousness-aware attraction
        const dx = mouseRef.current.x - particle.x
        const dy = mouseRef.current.y - particle.y
        const distance = Math.sqrt(dx * dx + dy * dy)

        if (distance < mouseInfluence && distance > 0) {
          const force = ((mouseInfluence - distance) / mouseInfluence) * 0.3
          const attraction = particle.energy > 0.5 ? 1 : -0.5 // High-energy particles attract, low-energy repel
          
          particle.vx += (dx / distance) * force * attraction
          particle.vy += (dy / distance) * force * attraction
        }

        // Consciousness-based movement patterns
        const consciousnessInfluence = Math.sin(timeRef.current * 0.5 + particle.pulsePhase) * 0.1
        particle.vx += consciousnessInfluence * (Math.random() - 0.5)
        particle.vy += consciousnessInfluence * (Math.random() - 0.5)

        // Apply velocity damping
        particle.vx *= 0.995
        particle.vy *= 0.995

        // Update position
        particle.x += particle.vx
        particle.y += particle.vy

        // Boundary wrapping with consciousness preservation
        if (particle.x < -10) particle.x = canvas.clientWidth + 10
        if (particle.x > canvas.clientWidth + 10) particle.x = -10
        if (particle.y < -10) particle.y = canvas.clientHeight + 10
        if (particle.y > canvas.clientHeight + 10) particle.y = -10

        // Update particle energy and pulse
        particle.energy += Math.sin(timeRef.current + particle.pulsePhase * 2) * 0.01
        particle.energy = Math.max(0.1, Math.min(1, particle.energy))
        
        const pulseIntensity = 0.5 + Math.sin(timeRef.current * 2 + particle.pulsePhase) * 0.3
        const currentOpacity = particle.opacity * pulseIntensity * particle.energy

        // Draw particle with glow effect
        const glowRadius = particle.size + particle.energy * 3
        
        // Outer glow
        const gradient = ctx.createRadialGradient(
          particle.x, particle.y, 0,
          particle.x, particle.y, glowRadius
        )
        gradient.addColorStop(0, `${particle.color}${Math.floor(currentOpacity * 255).toString(16).padStart(2, '0')}`)
        gradient.addColorStop(0.5, `${particle.color}${Math.floor(currentOpacity * 0.3 * 255).toString(16).padStart(2, '0')}`)
        gradient.addColorStop(1, `${particle.color}00`)
        
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, glowRadius, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()

        // Core particle
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = `${particle.color}${Math.floor((currentOpacity * 0.9 + 0.1) * 255).toString(16).padStart(2, '0')}`
        ctx.fill()

        // Draw consciousness connections
        particlesRef.current.slice(i + 1).forEach((otherParticle) => {
          const dx = particle.x - otherParticle.x
          const dy = particle.y - otherParticle.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < connectionDistance) {
            // Apply quantum entanglement
            applyQuantumEntanglement(particle, otherParticle, distance)

            // Connection strength based on particle types and energy
            const typeBonus = particle.type === otherParticle.type ? 1.5 : 1.0
            const energyBonus = (particle.energy + otherParticle.energy) / 2
            const connectionOpacity = (1 - distance / connectionDistance) * 0.15 * typeBonus * energyBonus * modifiers.connections

            if (connectionOpacity > 0.05) {
              ctx.beginPath()
              ctx.moveTo(particle.x, particle.y)
              ctx.lineTo(otherParticle.x, otherParticle.y)
              
              // Use average color for connections
              const avgColor = particle.type === otherParticle.type ? particle.color : '#ffffff'
              ctx.strokeStyle = `${avgColor}${Math.floor(connectionOpacity * 255).toString(16).padStart(2, '0')}`
              ctx.lineWidth = 0.5 + energyBonus * 0.5
              ctx.stroke()

              // Add occasional quantum "sparks"
              if (enableQuantumEntanglement && Math.random() < 0.001 * energyBonus) {
                const sparkX = particle.x + (otherParticle.x - particle.x) * Math.random()
                const sparkY = particle.y + (otherParticle.y - particle.y) * Math.random()
                
                ctx.beginPath()
                ctx.arc(sparkX, sparkY, 1, 0, Math.PI * 2)
                ctx.fillStyle = `${avgColor}aa`
                ctx.fill()
              }
            }
          }
        })
      })

      animationIdRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      document.removeEventListener('mousemove', handleMouseMove)
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current)
      }
    }
  }, [particleCount, connectionDistance, mouseInfluence, consciousnessLevel, enableQuantumEntanglement, isVisible])

  if (!isVisible) return null

  return (
    <canvas
      ref={canvasRef}
      className="consciousness-field"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: -1,
        pointerEvents: 'none',
        background: 'transparent'
      }}
    />
  )
}