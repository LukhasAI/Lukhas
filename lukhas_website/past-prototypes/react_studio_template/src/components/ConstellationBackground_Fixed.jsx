import React, { useEffect, useRef, useCallback } from 'react'

const ConstellationBackground = () => {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  const dataRef = useRef({ stars: [], connections: [] })

  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return { width: 0, height: 0 }
    
    const rect = canvas.parentElement?.getBoundingClientRect() || { width: window.innerWidth, height: window.innerHeight }
    canvas.width = rect.width
    canvas.height = rect.height
    return { width: rect.width, height: rect.height }
  }, [])

  const initStarsAndConnections = useCallback((width, height) => {
    if (width === 0 || height === 0) return

    const numStars = Math.min(120, Math.floor((width * height) / 8000))
    const stars = []
    const connections = []

    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 1.5 + 0.5,
        brightness: Math.random() * 0.6 + 0.4,
        twinkleSpeed: Math.random() * 0.015 + 0.008,
        phase: Math.random() * Math.PI * 2
      })
    }

    const maxConnections = Math.min(stars.length * 3, 300)
    let connectionCount = 0
    
    for (let i = 0; i < stars.length && connectionCount < maxConnections; i++) {
      for (let j = i + 1; j < stars.length && connectionCount < maxConnections; j++) {
        const dx = stars[i].x - stars[j].x
        const dy = stars[i].y - stars[j].y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 100) {
          connections.push({
            star1: i,
            star2: j,
            opacity: Math.max(0, (1 - distance / 100) * 0.25),
            baseOpacity: Math.max(0, (1 - distance / 100) * 0.25)
          })
          connectionCount++
        }
      }
    }

    dataRef.current = { stars, connections }
  }, [])

  const animate = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const { width, height } = { width: canvas.width, height: canvas.height }
    
    const now = performance.now()
    if (!animationRef.lastFrame) animationRef.lastFrame = now
    if (now - animationRef.lastFrame < 16.67) {
      animationRef.current = requestAnimationFrame(animate)
      return
    }
    animationRef.lastFrame = now

    ctx.clearRect(0, 0, width, height)
    
    const time = now * 0.001
    const { stars, connections } = dataRef.current

    if (connections.length > 0) {
      ctx.lineWidth = 0.5
      connections.forEach(connection => {
        const star1 = stars[connection.star1]
        const star2 = stars[connection.star2]
        if (!star1 || !star2) return
        
        const pulseOpacity = connection.baseOpacity * (0.7 + 0.3 * Math.sin(time * 1.5))
        
        ctx.beginPath()
        ctx.moveTo(star1.x, star1.y)
        ctx.lineTo(star2.x, star2.y)
        ctx.strokeStyle = `rgba(99, 179, 237, ${pulseOpacity})`
        ctx.stroke()
      })
    }

    if (stars.length > 0) {
      stars.forEach((star) => {
        const twinkle = Math.sin(time * star.twinkleSpeed * 2 + star.phase) * 0.25 + 0.75
        const brightness = star.brightness * twinkle

        ctx.beginPath()
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`
        ctx.fill()

        if (star.size > 1) {
          ctx.beginPath()
          ctx.arc(star.x, star.y, star.size * 1.8, 0, Math.PI * 2)
          ctx.fillStyle = `rgba(99, 179, 237, ${brightness * 0.15})`
          ctx.fill()
        }
      })
    }

    animationRef.current = requestAnimationFrame(animate)
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const { width, height } = resizeCanvas()
    initStarsAndConnections(width, height)
    animate()

    let resizeTimeout
    const handleResize = () => {
      clearTimeout(resizeTimeout)
      resizeTimeout = setTimeout(() => {
        const { width, height } = resizeCanvas()
        initStarsAndConnections(width, height)
      }, 200)
    }

    window.addEventListener('resize', handleResize, { passive: true })

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      window.removeEventListener('resize', handleResize)
      clearTimeout(resizeTimeout)
      dataRef.current = { stars: [], connections: [] }
    }
  }, [resizeCanvas, initStarsAndConnections, animate])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      style={{ 
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)'
      }}
    />
  )
}

export default ConstellationBackground
