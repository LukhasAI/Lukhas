'use client'

import { useState, useEffect } from 'react'
import { useVisitQuote } from './useVisitQuote'

interface QuoteProps {
  onComplete?: () => void
  className?: string
}

export default function Quote({ onComplete, className = '' }: QuoteProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [animationComplete, setAnimationComplete] = useState(false)
  const quote = useVisitQuote()

  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (prefersReducedMotion) {
      // Present quote instantly for reduced motion users
      setIsVisible(true)
      setAnimationComplete(true)
      onComplete?.()
    } else {
      // Start fade-in animation after a brief delay for others
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 300)

      return () => clearTimeout(timer)
    }
  }, [onComplete])

  useEffect(() => {
    if (isVisible && !animationComplete) {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

      // Mark animation as complete after appropriate duration
      const completeTimer = setTimeout(() => {
        setAnimationComplete(true)
        onComplete?.()
      }, prefersReducedMotion ? 0 : 2000) // Instant for reduced motion, 2s for others

      return () => clearTimeout(completeTimer)
    }
  }, [isVisible, animationComplete, onComplete])

  return (
    <div className={`quote-container ${className}`}>
      <blockquote
        className={`
          text-2xl md:text-4xl lg:text-5xl
          text-white
          leading-relaxed
          text-center
          font-light
          tracking-wide
          transition-all
          duration-2000
          ease-out
          ${isVisible
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 translate-y-8'
          }
        `}
        role="text"
        aria-live="polite"
      >
        "{quote.text}"
      </blockquote>

      <cite
        className={`
          block
          text-center
          text-lg
          text-white/70
          mt-8
          font-light
          transition-all
          duration-2000
          ease-out
          delay-500
          ${isVisible
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 translate-y-4'
          }
        `}
      >
        — Lukhʌs
      </cite>
    </div>
  )
}
