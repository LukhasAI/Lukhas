'use client'

import { useState, useEffect } from 'react'

interface Quote {
  text: string
  attribution?: string
}

const CURATED_QUOTES: Quote[] = [
  {
    text: "We build tools that serve human agency.",
  },
  {
    text: "Intelligence that remembers consent before convenience.",
  },
  {
    text: "The substrate for thought emerges from intentional design.",
  },
  {
    text: "Privacy is not a feature—it's a foundation.",
  },
  {
    text: "Building consciousness you can trust.",
  },
  {
    text: "Ethical intelligence begins with ethical design.",
  }
]

const STORAGE_KEY = 'lukhas:lastQuoteId'

export function useVisitQuote(): Quote {
  const [quote, setQuote] = useState<Quote>(CURATED_QUOTES[0])

  useEffect(() => {
    let selectedQuote: Quote

    try {
      // "Once per visit": use sessionStorage  
      const storedQuote = sessionStorage.getItem(STORAGE_KEY)
      
      if (storedQuote) {
        // Find stored quote by ID
        const quoteIndex = CURATED_QUOTES.findIndex((_, i) => i.toString() === storedQuote)
        selectedQuote = quoteIndex >= 0 ? CURATED_QUOTES[quoteIndex] : CURATED_QUOTES[0]
      } else {
        // Deterministic pick that avoids immediate repeat
        const lastVisitQuote = localStorage.getItem(STORAGE_KEY)
        let idx = Math.floor(Math.random() * CURATED_QUOTES.length)
        
        if (lastVisitQuote) {
          const lastIdx = parseInt(lastVisitQuote)
          if (lastIdx === idx) {
            idx = (idx + 1) % CURATED_QUOTES.length
          }
        }

        selectedQuote = CURATED_QUOTES[idx]
        
        // Store index for this visit and for cross-visit repeat avoidance  
        sessionStorage.setItem(STORAGE_KEY, idx.toString())
        localStorage.setItem(STORAGE_KEY, idx.toString())
      }

      setQuote(selectedQuote)
    } catch (error) {
      // Fallback for private browsing mode or storage issues
      console.warn('Storage not available, using fallback quote')
      const fallbackIndex = Math.floor(Math.random() * CURATED_QUOTES.length)
      setQuote(CURATED_QUOTES[fallbackIndex])
    }
  }, [])

  return quote
}