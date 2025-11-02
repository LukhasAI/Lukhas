'use client'

import { useEffect, useRef } from 'react'

export default function HeroCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Particle system
    class Particle {
      x: number
      y: number
      z: number
      vx: number
      vy: number
      size: number
      color: string
      pulsePhase: number

      constructor(width: number, height: number) {
        this.x = Math.random() * width
        this.y = Math.random() * height
        this.z = Math.random() * 1000
        this.vx = (Math.random() - 0.5) * 0.5
        this.vy = (Math.random() - 0.5) * 0.5
        this.size = Math.random() * 2 + 1
        this.pulsePhase = Math.random() * Math.PI * 2

        // MATADA consciousness colors
        const colors = ['#6B46C1', '#8B5CF6', '#A78BFA', '#C4B5FD']
        this.color = colors[Math.floor(Math.random() * colors.length)]
      }

      update(width: number, height: number, time: number) {
        this.x += this.vx
        this.y += this.vy

        // Wrap around edges
        if (this.x < 0) this.x = width
        if (this.x > width) this.x = 0
        if (this.y < 0) this.y = height
        if (this.y > height) this.y = 0

        // Pulse effect
        this.size = (Math.sin(time * 0.002 + this.pulsePhase) + 1) * 1.5 + 1
      }

      draw(ctx: CanvasRenderingContext2D, centerX: number, centerY: number, time: number) {
        const distance = Math.sqrt(
          Math.pow(this.x - centerX, 2) +
          Math.pow(this.y - centerY, 2)
        )

        // Create consciousness field effect
        const maxDistance = 200
        const fieldStrength = Math.max(0, 1 - distance / maxDistance)

        // Apply field distortion
        const angle = Math.atan2(this.y - centerY, this.x - centerX)
        const spiralOffset = time * 0.001
        const distortedX = this.x + Math.cos(angle + spiralOffset) * fieldStrength * 20
        const distortedY = this.y + Math.sin(angle + spiralOffset) * fieldStrength * 20

        // Calculate opacity based on z-depth and field strength
        const opacity = (1 - this.z / 1000) * 0.8 + fieldStrength * 0.2

        ctx.globalAlpha = opacity
        ctx.fillStyle = this.color
        ctx.shadowBlur = 10 * fieldStrength
        ctx.shadowColor = this.color

        ctx.beginPath()
        ctx.arc(distortedX, distortedY, this.size, 0, Math.PI * 2)
        ctx.fill()

        ctx.shadowBlur = 0
        ctx.globalAlpha = 1
      }
    }

    // Create particles
    const particles: Particle[] = []
    const particleCount = 100

    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle(canvas.offsetWidth, canvas.offsetHeight))
    }

    // Animation loop
    let animationId: number
    let time = 0

    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)

      const centerX = canvas.offsetWidth / 2
      const centerY = canvas.offsetHeight / 2

      // Draw central consciousness sphere
      const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 100)
      gradient.addColorStop(0, 'rgba(107, 70, 193, 0.3)')
      gradient.addColorStop(0.5, 'rgba(107, 70, 193, 0.1)')
      gradient.addColorStop(1, 'rgba(107, 70, 193, 0)')

      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(centerX, centerY, 100 + Math.sin(time * 0.002) * 10, 0, Math.PI * 2)
      ctx.fill()

      // Update and draw particles
      particles.forEach(particle => {
        particle.update(canvas.offsetWidth, canvas.offsetHeight, time)
        particle.draw(ctx, centerX, centerY, time)
      })

      // Draw connection lines between nearby particles
      ctx.strokeStyle = 'rgba(107, 70, 193, 0.1)'
      ctx.lineWidth = 0.5

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const distance = Math.sqrt(
            Math.pow(particles[i].x - particles[j].x, 2) +
            Math.pow(particles[i].y - particles[j].y, 2)
          )

          if (distance < 50) {
            ctx.globalAlpha = 1 - distance / 50
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }

      ctx.globalAlpha = 1
      time++
      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full"
      style={{
        background: 'transparent',
        width: '100%',
        height: '100%'
      }}
    />
  )
}
