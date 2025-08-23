'use client'

/**
 * State-aware Layout Component
 * Renders different UI based on the current state machine state
 */

import { useEffect } from 'react'
import { useStateMachine } from '@/hooks/use-state-machine'
import NeuralBackground from '@/components/neural-background'
import CookiesBanner from '@/components/cookies-banner'
import CinematicQuote from '@/components/cinematic-quote'
import QuoteOptions from '@/components/quote-options'
import { getWelcomeQuote } from '@/lib/quote-bank'

interface StateLayoutProps {
  children?: React.ReactNode
}

export default function StateLayout({ children }: StateLayoutProps) {
  const {
    currentState,
    activeEffects,
    isBootState,
    isQuoteState,
    isConsentPending,
    isQuoteWithOptions,
    isMarketingMode,
    isLoginFlow,
    isStudioActive,
    transition,
    completeQuote
  } = useStateMachine()

  // Get a quote for this session
  const quote = getWelcomeQuote()

  // Handle quote completion - wait for user to read before showing cookies
  const handleQuoteComplete = () => {
    console.log('📝 Quote animation complete, current state:', currentState)
    console.log('📝 Waiting for user to absorb quote (3 seconds)...')
    // Give user time to read and appreciate the quote (3 seconds)
    setTimeout(() => {
      console.log('🍪 Absorption time complete, transitioning to CONSENT_REQUIRED')
      const success = transition('CONSENT_REQUIRED')
      console.log('🍪 Transition result:', success)
    }, 3000)
  }

  // Auto-start the state machine on mount
  useEffect(() => {
    if (isBootState) {
      // Auto-transition from BOOT to QUOTE_IN after initialization
      console.log('🚀 Auto-starting state machine transition')
      const timer = setTimeout(() => {
        console.log('🔄 Triggering SYSTEM_READY transition')
        transition('SYSTEM_READY')
      }, 1500)
      
      return () => clearTimeout(timer)
    }
  }, [isBootState, transition])

  // Quote state is now handled by the onComplete callback
  // No automatic transitions from quote state

  // Apply state-based CSS classes to body
  useEffect(() => {
    const bodyClasses = [
      `state-${currentState.toLowerCase()}`,
      ...activeEffects
    ]

    // Add classes
    bodyClasses.forEach(className => {
      document.body.classList.add(className)
    })

    // Cleanup on unmount or state change
    return () => {
      bodyClasses.forEach(className => {
        document.body.classList.remove(className)
      })
    }
  }, [currentState, activeEffects])

  // Debug logging
  console.log('🎭 StateLayout render:', { currentState, activeEffects })

  return (
    <div className={`state-layout state-${currentState.toLowerCase()}`}>
      {/* Neural background - always present */}
      <NeuralBackground />
      
      {/* Boot State - Loading */}
      {isBootState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-blue-200 text-sm">Initializing Lukhas...</p>
          </div>
        </div>
      )}

      {/* Quote State - Cinematic Quote Display */}
      {isQuoteState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <div className="w-full max-w-5xl">
            <blockquote className="text-2xl md:text-4xl lg:text-5xl text-white leading-relaxed">
              <CinematicQuote text={quote.text} delay={40} onComplete={handleQuoteComplete} />
            </blockquote>
          </div>
        </div>
      )}

      {/* Consent Pending State - Bottom Banner */}
      {isConsentPending && (
        <CookiesBanner 
          onAccept={() => transition('CONSENT_GIVEN')}
          onDecline={() => transition('CONSENT_GIVEN')}
        />
      )}

      {/* Quote with Options State - Show quote and navigation options */}
      {isQuoteWithOptions && (
        <>
          <div className="fixed inset-0 z-40 flex items-center justify-center px-4">
            <div className="w-full max-w-5xl">
              <blockquote className="text-2xl md:text-4xl lg:text-5xl text-white leading-relaxed">
                <CinematicQuote text={quote.text} delay={40} />
              </blockquote>
            </div>
          </div>
          <QuoteOptions />
        </>
      )}

      {/* Marketing Mode - Full Website */}
      {isMarketingMode && (
        <div className="min-h-screen">
          {/* Top navigation bar */}
          <nav className="fixed top-0 left-0 right-0 z-30 bg-black/20 backdrop-blur-md border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <span className="text-2xl font-bold text-white">LUKHλS</span>
                </div>
                <div className="hidden md:block">
                  <div className="flex items-center space-x-8">
                    <a href="#about" className="text-white/80 hover:text-white transition-colors">About</a>
                    <a href="#research" className="text-white/80 hover:text-white transition-colors">Research</a>
                    <a href="#team" className="text-white/80 hover:text-white transition-colors">Team</a>
                    <a href="#careers" className="text-white/80 hover:text-white transition-colors">Careers</a>
                    <a href="#blog" className="text-white/80 hover:text-white transition-colors">Blog</a>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => transition('LOGIN_INITIATED')}
                    className="text-white/80 hover:text-white transition-colors"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => transition('ENTER_STUDIO')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    Enter Studio
                  </button>
                </div>
              </div>
            </div>
          </nav>

          {/* Marketing content */}
          <main className="pt-16">
            {children}
          </main>
        </div>
      )}

      {/* Login Flow State */}
      {isLoginFlow && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 max-w-md w-full mx-4 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Welcome to Lukhas</h2>
            
            <div className="space-y-4">
              <button
                onClick={() => transition('LOGIN_SUCCESS')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-md transition-colors flex items-center justify-center space-x-2"
              >
                <span>🔐</span>
                <span>Sign in with Passkey</span>
              </button>
              
              <div className="text-center">
                <span className="text-white/60 text-sm">or</span>
              </div>
              
              <button
                onClick={() => transition('LOGIN_SUCCESS')}
                className="w-full border border-white/20 text-white py-3 px-4 rounded-md transition-colors hover:bg-white/5"
              >
                Continue with Email
              </button>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => transition('MARKETING_COMPLETE')}
                className="text-white/60 hover:text-white/80 text-sm transition-colors"
              >
                Back to main site
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Studio State */}
      {isStudioActive && (
        <div className="h-screen overflow-hidden">
          {children}
        </div>
      )}

      {/* Debug info in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 right-4 z-[9999] bg-black/80 text-white text-xs p-2 rounded font-mono">
          State: {currentState}
        </div>
      )}
    </div>
  )
}