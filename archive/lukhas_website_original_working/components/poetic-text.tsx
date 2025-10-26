'use client'

import React from 'react'
import { validatePoeticContent } from '@/lib/poeticGuard'

interface PoeticTextProps {
  children: string
  className?: string
  maxWords?: number
  showWordCount?: boolean
  fallback?: string
}

/**
 * PoeticText component that automatically validates and clamps poetic content
 * Ensures content stays within policy limits (≤40 words by default)
 */
export default function PoeticText({ 
  children, 
  className = '', 
  maxWords = 40,
  showWordCount = false,
  fallback = ''
}: PoeticTextProps) {
  const validation = validatePoeticContent(children, { maxWords, noClaims: true })
  
  // Log violations in development
  if (process.env.NODE_ENV === 'development' && !validation.isValid) {
    console.warn('[PoeticText] Content violations:', validation.violations)
  }
  
  const displayContent = validation.clampedContent || fallback
  
  return (
    <div className={`poetic-text ${className}`} data-tone="poetic">
      <div className="text-content">
        {displayContent}
      </div>
      {showWordCount && process.env.NODE_ENV === 'development' && (
        <div className="text-xs text-white/40 mt-1">
          Words: {validation.wordCount}/{maxWords}
          {!validation.isValid && (
            <span className="text-red-400 ml-2">
              Policy violations: {validation.violations.length}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * Hook version for use in other components
 */
export function usePoeticText(content: string, maxWords: number = 40) {
  const validation = validatePoeticContent(content, { maxWords, noClaims: true })
  
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development' && !validation.isValid) {
      console.warn('[usePoeticText] Content violations:', validation.violations)
    }
  }, [validation.isValid, validation.violations])
  
  return {
    text: validation.clampedContent,
    isValid: validation.isValid,
    wordCount: validation.wordCount,
    violations: validation.violations
  }
}