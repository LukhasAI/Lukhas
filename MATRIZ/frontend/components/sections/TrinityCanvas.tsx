'use client'

import { useEffect, useRef } from 'react'

export default function TrinityCanvas() {
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

    // Trinity system components
    interface TrinityNode {
      x: number
      y: number
      label: string
      color: string
      glowColor: string
      icon: string
      particles: Particle[]
      rotation: number
    }

    class Particle {
      angle: number
      radius: number
      speed: number
      size: number
      opacity: number

      constructor() {
        this.angle = Math.random() * Math.PI * 2
        this.radius = Math.random() * 60 + 40
        this.speed = (Math.random() - 0.5) * 0.02
        this.size = Math.random() * 2 + 1
        this.opacity = Math.random() * 0.5 + 0.5
      }

      update() {
        this.angle += this.speed
        this.opacity = 0.5 + Math.sin(this.angle * 2) * 0.3
      }
    }

    // Initialize trinity nodes
    const width = canvas.offsetWidth
    const height = canvas.offsetHeight
    const centerX = width / 2
    const centerY = height / 2
    const triangleRadius = Math.min(width, height) * 0.25

    const nodes: TrinityNode[] = [
      {
        x: centerX,
        y: centerY - triangleRadius,
        label: 'Identity',
        color: '#6B46C1',
        glowColor: 'rgba(107, 70, 193, 0.3)',
        icon: '⚛️',
        particles: Array(20).fill(null).map(() => new Particle()),
        rotation: 0
      },
      {
        x: centerX - triangleRadius * Math.cos(Math.PI / 6),
        y: centerY + triangleRadius * Math.sin(Math.PI / 6),
        label: 'Consciousness',
        color: '#0EA5E9',
        glowColor: 'rgba(14, 165, 233, 0.3)',
        icon: '🧠',
        particles: Array(20).fill(null).map(() => new Particle()),
        rotation: 0
      },
      {
        x: centerX + triangleRadius * Math.cos(Math.PI / 6),
        y: centerY + triangleRadius * Math.sin(Math.PI / 6),
        label: 'Guardian',
        color: '#10B981',
        glowColor: 'rgba(16, 185, 129, 0.3)',
        icon: '🛡️',
        particles: Array(20).fill(null).map(() => new Particle()),
        rotation: 0
      }
    ]

    // Animation variables
    let animationId: number
    let time = 0

    const drawNode = (node: TrinityNode) => {
      // Draw particles orbit
      node.particles.forEach(particle => {
        particle.update()
        const px = node.x + Math.cos(particle.angle + node.rotation) * particle.radius
        const py = node.y + Math.sin(particle.angle + node.rotation) * particle.radius

        ctx.globalAlpha = particle.opacity * 0.3
        ctx.fillStyle = node.color
        ctx.beginPath()
        ctx.arc(px, py, particle.size, 0, Math.PI * 2)
        ctx.fill()
      })

      // Draw glow effect
      const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, 80)
      gradient.addColorStop(0, node.glowColor)
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)')

      ctx.globalAlpha = 0.6 + Math.sin(time * 0.002) * 0.2
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(node.x, node.y, 80, 0, Math.PI * 2)
      ctx.fill()

      // Draw core circle
      ctx.globalAlpha = 1
      ctx.strokeStyle = node.color
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(node.x, node.y, 30, 0, Math.PI * 2)
      ctx.stroke()

      // Draw inner rotating rings
      ctx.save()
      ctx.translate(node.x, node.y)
      ctx.rotate(node.rotation)

      ctx.strokeStyle = node.color
      ctx.lineWidth = 1
      ctx.globalAlpha = 0.6

      // First ring
      ctx.beginPath()
      ctx.ellipse(0, 0, 45, 20, 0, 0, Math.PI * 2)
      ctx.stroke()

      // Second ring
      ctx.rotate(Math.PI / 3)
      ctx.beginPath()
      ctx.ellipse(0, 0, 45, 20, 0, 0, Math.PI * 2)
      ctx.stroke()

      // Third ring
      ctx.rotate(Math.PI / 3)
      ctx.beginPath()
      ctx.ellipse(0, 0, 45, 20, 0, 0, Math.PI * 2)
      ctx.stroke()

      ctx.restore()

      // Draw icon
      ctx.globalAlpha = 1
      ctx.font = '24px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(node.icon, node.x, node.y)

      // Draw label
      ctx.fillStyle = node.color
      ctx.font = '12px Inter, sans-serif'
      ctx.fillText(node.label, node.x, node.y + 55)
    }

    const drawConnections = () => {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
      ctx.lineWidth = 1
      ctx.setLineDash([5, 5])

      // Draw triangular connections
      for (let i = 0; i < nodes.length; i++) {
        const nextIndex = (i + 1) % nodes.length

        // Create gradient along the line
        const gradient = ctx.createLinearGradient(
          nodes[i].x, nodes[i].y,
          nodes[nextIndex].x, nodes[nextIndex].y
        )
        gradient.addColorStop(0, nodes[i].color)
        gradient.addColorStop(1, nodes[nextIndex].color)

        ctx.strokeStyle = gradient
        ctx.globalAlpha = 0.3 + Math.sin(time * 0.001 + i) * 0.2

        ctx.beginPath()
        ctx.moveTo(nodes[i].x, nodes[i].y)
        ctx.lineTo(nodes[nextIndex].x, nodes[nextIndex].y)
        ctx.stroke()
      }

      ctx.setLineDash([])
    }

    const drawCenterEnergy = () => {
      // Draw central energy core
      const energyGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 50)
      energyGradient.addColorStop(0, 'rgba(255, 255, 255, 0.3)')
      energyGradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.1)')
      energyGradient.addColorStop(1, 'rgba(255, 255, 255, 0)')

      ctx.globalAlpha = 0.5 + Math.sin(time * 0.003) * 0.3
      ctx.fillStyle = energyGradient
      ctx.beginPath()
      ctx.arc(centerX, centerY, 50 + Math.sin(time * 0.002) * 10, 0, Math.PI * 2)
      ctx.fill()

      // Draw rotating energy lines
      ctx.save()
      ctx.translate(centerX, centerY)
      ctx.rotate(time * 0.001)

      for (let i = 0; i < 3; i++) {
        ctx.rotate((Math.PI * 2) / 3)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(triangleRadius * 0.6, 0)
        ctx.stroke()
      }

      ctx.restore()
    }

    const animate = () => {
      // Clear canvas with slight trail effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
      ctx.fillRect(0, 0, width, height)

      // Update rotations
      nodes.forEach((node, index) => {
        node.rotation += 0.01 * (index + 1) * 0.5
      })

      // Draw components
      drawConnections()
      drawCenterEnergy()
      nodes.forEach(drawNode)

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
