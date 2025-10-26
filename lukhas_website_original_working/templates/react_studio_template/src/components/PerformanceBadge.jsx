/**
 * Performance Badge Component
 * Bay Area Standards: Real-time performance monitoring ⚡
 */
import React from 'react'
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor.js'

export const PerformanceBadge = ({ className = '' }) => {
  const { fps } = usePerformanceMonitor()

  // Hide in production
  if (process.env.NODE_ENV === 'production') return null

  const getFpsColor = (fps) => {
    if (fps >= 55) return 'text-green-400'
    if (fps >= 30) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className={`fixed top-4 right-4 z-50 bg-black/80 backdrop-blur-sm rounded-lg px-3 py-2 text-xs font-mono ${className}`}>
      <span className={getFpsColor(fps)}>
        FPS: {fps}
      </span>
    </div>
  )
}

export default PerformanceBadge
