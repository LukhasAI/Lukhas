/**
 * Simple Performance Monitor Hook
 * Bay Area Standards: Monitor Core Web Vitals ⚡
 */
import { useEffect, useState } from 'react'

export const usePerformanceMonitor = () => {
  const [fps, setFps] = useState(0)

  useEffect(() => {
    let frameCount = 0
    let lastTime = Date.now()
    let rafId

    const updateFps = () => {
      frameCount++
      const currentTime = Date.now()
      
      if (currentTime - lastTime >= 1000) {
        setFps(Math.round((frameCount * 1000) / (currentTime - lastTime)))
        frameCount = 0
        lastTime = currentTime
      }
      
      rafId = requestAnimationFrame(updateFps)
    }

    rafId = requestAnimationFrame(updateFps)

    return () => {
      if (rafId) cancelAnimationFrame(rafId)
    }
  }, [])

  return { fps }
}
