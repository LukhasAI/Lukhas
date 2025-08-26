'use client'

import React, { useState, useEffect } from 'react'

interface CalmModeToggleProps {
  className?: string
}

export default function CalmModeToggle({ className = '' }: CalmModeToggleProps) {
  const [isCalmMode, setIsCalmMode] = useState(false)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    // Check system preference for reduced motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    // Listen for changes to system preference
    const handleMediaChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
      if (e.matches) {
        setIsCalmMode(true) // Auto-enable calm mode if system prefers reduced motion
      }
    }

    mediaQuery.addEventListener('change', handleMediaChange)

    // Check for saved calm mode preference
    const savedCalmMode = localStorage.getItem('calm-mode')
    if (savedCalmMode === 'true' || mediaQuery.matches) {
      setIsCalmMode(true)
      document.body.classList.add('calm-mode')
    }

    return () => {
      mediaQuery.removeEventListener('change', handleMediaChange)
    }
  }, [])

  const toggleCalmMode = () => {
    const newCalmMode = !isCalmMode
    setIsCalmMode(newCalmMode)

    // Update body class
    if (newCalmMode) {
      document.body.classList.add('calm-mode')
    } else {
      document.body.classList.remove('calm-mode')
    }

    // Save preference
    localStorage.setItem('calm-mode', newCalmMode.toString())

    // Dispatch custom event for React components to listen to
    window.dispatchEvent(new CustomEvent('calmModeToggle', {
      detail: {
        enabled: newCalmMode,
        reason: 'user-toggle'
      }
    }))
  }

  // Don't show toggle if system already prefers reduced motion
  if (prefersReducedMotion) {
    return null
  }

  return (
    <button
      onClick={toggleCalmMode}
      className={`calm-mode-toggle ${className}`}
      aria-label={isCalmMode ? "Enable animations" : "Disable animations (Calm Mode)"}
      title={isCalmMode ? "Enable animations" : "Disable animations for focus and accessibility"}
    >
      <span className="icon-motion" aria-hidden="true">
        🌟
      </span>
      <span className="icon-calm" aria-hidden="true">
        😌
      </span>
      <span className="ml-2">
        {isCalmMode ? 'Enable Animations' : 'Calm Mode'}
      </span>
    </button>
  )
}
