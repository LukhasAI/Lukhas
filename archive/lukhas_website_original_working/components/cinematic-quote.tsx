'use client'

import { useState, useEffect } from 'react'

interface CinematicQuoteProps {
  text: string
  delay?: number // Delay between characters in ms
  onComplete?: () => void // Callback when animation completes
}

export default function CinematicQuote({ text, delay = 50, onComplete }: CinematicQuoteProps) {
  const [visibleChars, setVisibleChars] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    if (visibleChars < text.length) {
      const timer = setTimeout(() => {
        setVisibleChars(prev => prev + 1)
      }, delay)
      
      return () => clearTimeout(timer)
    } else {
      setIsComplete(true)
      // Call onComplete callback when animation finishes
      if (onComplete) {
        // Give a moment for the cursor to appear before calling complete
        setTimeout(onComplete, 800)
      }
    }
  }, [visibleChars, text.length, delay, onComplete])

  // Split text into words for better line breaks
  const words = text.split(' ')
  let charIndex = 0

  return (
    <div className="text-center leading-relaxed max-w-4xl mx-auto">
      <div className="inline-block" style={{ 
        fontFamily: '"Helvetica Neue", -apple-system, BlinkMacSystemFont, sans-serif',
        fontWeight: 100, // Ultra light
        letterSpacing: '0.02em'
      }}>
        {words.map((word, wordIndex) => (
          <span key={wordIndex} className="inline-block mr-2">
            {word.split('').map((char, charInWordIndex) => {
              const currentCharIndex = charIndex++
              return (
                <span
                  key={currentCharIndex}
                  className={`inline-block transition-opacity duration-300 ease-out ${
                    currentCharIndex < visibleChars ? 'opacity-100' : 'opacity-0'
                  }`}
                  style={{
                    transitionDelay: `${currentCharIndex * delay}ms`
                  }}
                >
                  {char}
                </span>
              )
            })}
            {wordIndex < words.length - 1 && (
              <span
                className={`inline-block transition-opacity duration-300 ease-out ${
                  charIndex - 1 < visibleChars ? 'opacity-100' : 'opacity-0'
                }`}
                style={{
                  transitionDelay: `${(charIndex - 1) * delay}ms`
                }}
              >
                &nbsp;
              </span>
            )}
          </span>
        ))}
        {isComplete && (
          <span 
            className="animate-pulse ml-1 opacity-40"
            style={{ fontFamily: '"Helvetica Neue", monospace' }}
          >
            |
          </span>
        )}
      </div>
    </div>
  )
}