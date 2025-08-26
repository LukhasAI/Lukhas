/**
 * Optimized Animated Background Component - Epilepsy Safe
 * Bay Area Performance Standards ⚡
 */
import React, { memo } from 'react'
import { useAnimatedBackground } from '../hooks/useAnimatedBackground'
import ConstellationBackground from './ConstellationBackground'

const AnimatedBackground = memo(({
  type = 'constellation',
  isActive = true,
  className = '',
  style = {}
}) => {
  const { canvasRef } = useAnimatedBackground(type, isActive)

  // Use dedicated constellation component - our main safe background
  if (type === 'constellation') {
    return <ConstellationBackground />
  }

  // Only safe, non-flickering backgrounds allowed
  const gradientStyle = {
    background: type === 'clouds'
      ? 'linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #2c3e50 100%)'
      : 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
    ...style
  }

  // For clouds, we use a subtle static gradient only
  if (type === 'clouds') {
    return (
      <div
        className={`fixed inset-0 pointer-events-none z-0 ${className}`}
        style={gradientStyle}
      />
    )
  }

  return (
    <div
      className={`fixed inset-0 pointer-events-none z-0 ${className}`}
      style={gradientStyle}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{
          opacity: isActive ? 1 : 0,
          transition: 'opacity 0.3s ease-in-out'
        }}
      />
    </div>
  )
})

AnimatedBackground.displayName = 'AnimatedBackground'

export default AnimatedBackground
