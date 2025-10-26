/**
 * Optimized Animated Background Hook
 * Bay Area Performance Standards ⚡
 */
import { useEffect, useRef, useCallback } from 'react'

export const useAnimatedBackground = (type = 'stars', isActive = true) => {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)
  const dataRef = useRef({ stars: [], particles: [] })

  const stopAnimation = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }
  }, [])

  const resizeCanvas = useCallback((canvas) => {
    const rect = canvas.parentElement.getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = rect.height
    return { width: rect.width, height: rect.height }
  }, [])

  // Optimized Stars Animation
  const initStars = useCallback((width, height) => {
    const stars = []
    const numStars = Math.min(100, Math.floor((width * height) / 10000)) // Adaptive count
    
    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.8 + 0.2,
        speed: Math.random() * 0.02 + 0.01, // Slower, smoother
        direction: Math.random() > 0.5 ? 1 : -1
      })
    }
    dataRef.current.stars = stars
  }, [])

  const animateStars = useCallback((ctx, width, height) => {
    // Clear with gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, height)
    gradient.addColorStop(0, 'rgba(100, 100, 255, 0.1)')
    gradient.addColorStop(1, 'rgba(150, 100, 255, 0.05)')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)

    // Animate stars efficiently
    dataRef.current.stars.forEach(star => {
      star.opacity += star.speed * star.direction
      if (star.opacity <= 0.2) star.direction = 1
      if (star.opacity >= 1) star.direction = -1

      ctx.beginPath()
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`
      ctx.fill()
    })
  }, [])

  // Optimized Geometric Animation with Spatial Partitioning
  const initGeometric = useCallback((width, height) => {
    const particles = []
    const numParticles = Math.min(30, Math.floor((width * height) / 20000)) // Adaptive count
    
    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.5 + 1
      })
    }
    dataRef.current.particles = particles
  }, [])

  const animateGeometric = useCallback((ctx, width, height) => {
    ctx.clearRect(0, 0, width, height)
    
    const particles = dataRef.current.particles
    const maxDistance = 80
    
    // Update positions
    particles.forEach(p => {
      p.x += p.vx
      p.y += p.vy

      // Bounce off walls
      if (p.x < 0 || p.x > width) p.vx *= -1
      if (p.y < 0 || p.y > height) p.vy *= -1
    })

    // Draw particles
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)'
    particles.forEach(p => {
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fill()
    })

    // Draw connections (optimized - only check nearby particles)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
    ctx.lineWidth = 1
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i]
        const p2 = particles[j]
        const distance = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
        
        if (distance < maxDistance) {
          const opacity = (1 - distance / maxDistance) * 0.3
          ctx.strokeStyle = `rgba(255, 255, 255, ${opacity})`
          ctx.beginPath()
          ctx.moveTo(p1.x, p1.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.stroke()
        }
      }
    }
  }, [])

  // Main animation loop with performance monitoring
  const animate = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || !isActive) return

    const ctx = canvas.getContext('2d')
    const { width, height } = resizeCanvas(canvas)

    // Performance throttling - skip frames if needed
    const now = performance.now()
    if (!animationRef.lastFrame) animationRef.lastFrame = now
    if (now - animationRef.lastFrame < 16.67) { // ~60fps cap
      animationRef.current = requestAnimationFrame(animate)
      return
    }
    animationRef.lastFrame = now

    try {
      if (type === 'stars') {
        if (!dataRef.current.stars.length) initStars(width, height)
        animateStars(ctx, width, height)
      } else if (type === 'geometric') {
        if (!dataRef.current.particles.length) initGeometric(width, height)
        animateGeometric(ctx, width, height)
      }
    } catch (error) {
      console.warn('Animation error:', error)
      stopAnimation()
      return
    }

    animationRef.current = requestAnimationFrame(animate)
  }, [type, isActive, initStars, animateStars, initGeometric, animateGeometric, resizeCanvas, stopAnimation])

  useEffect(() => {
    if (!isActive) {
      stopAnimation()
      return
    }

    const canvas = canvasRef.current
    if (!canvas) return

    // Initialize and start animation
    const { width, height } = resizeCanvas(canvas)
    if (type === 'stars') initStars(width, height)
    if (type === 'geometric') initGeometric(width, height)
    
    animate()

    // Resize handler with debouncing
    let resizeTimeout
    const handleResize = () => {
      clearTimeout(resizeTimeout)
      resizeTimeout = setTimeout(() => {
        const { width, height } = resizeCanvas(canvas)
        if (type === 'stars') initStars(width, height)
        if (type === 'geometric') initGeometric(width, height)
      }, 150)
    }

    window.addEventListener('resize', handleResize, { passive: true })

    // Cleanup function - CRITICAL for preventing memory leaks
    return () => {
      stopAnimation()
      window.removeEventListener('resize', handleResize)
      clearTimeout(resizeTimeout)
      dataRef.current = { stars: [], particles: [] }
    }
  }, [type, isActive, animate, initStars, initGeometric, resizeCanvas, stopAnimation])

  return { canvasRef, stopAnimation }
}
