'use client'

/**
 * State-aware Layout Component
 * Clean 5-state flow: BOOT → QUOTE_IN → CONSENT_PENDING → QUOTE_WITH_OPTIONS → MARKETING_MODE
 */

import { useEffect, useState } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import CookiesBanner from '@/components/cookies-banner'
import Quote from '@/components/Quote'
import EssentialModeBanner from '@/components/essential-mode-banner'

type LayoutState = 'BOOT' | 'QUOTE_IN' | 'CONSENT_PENDING' | 'QUOTE_WITH_OPTIONS' | 'MARKETING_MODE'

interface StateLayoutProps {
  children?: React.ReactNode
}

export default function StateLayout({ children }: StateLayoutProps) {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const isStudioRoute = pathname.startsWith('/studio')
  const isSettingsRoute = pathname.startsWith('/settings')
  const isAppRoute = isStudioRoute || isSettingsRoute
  
  // Check for skipState query parameter to bypass state machine
  const skipState = searchParams.get('skipState') === 'true'
  
  // Add all domain routes to bypass list
  const domainRoutes = ['/ai', '/id', '/team', '/dev', '/io', '/store', '/cloud', '/eu', '/us', '/xyz', '/com']
  const isDomainRoute = domainRoutes.includes(pathname)
    
  const shouldSkip = isAppRoute || pathname === '/showcase' || skipState || (isDomainRoute && skipState)
  
  // Always declare ALL hooks first (Rules of Hooks)
  const [currentState, setCurrentState] = useState<LayoutState>('BOOT')
  const [consentGiven, setConsentGiven] = useState(false)
  const [consentType, setConsentType] = useState<'none' | 'essential' | 'full'>('none')

  // Check if consent was already given and URL parameters
  useEffect(() => {
    // Skip effect if we should bypass the state machine
    if (shouldSkip) return
    
    const storedConsent = localStorage.getItem('lukhas_cookie_consent')
    const storedType = localStorage.getItem('lukhas_cookie_type') as 'essential' | 'full' | null

    if (storedConsent) {
      setConsentGiven(true)
      setConsentType(storedType || 'essential')
    }

    // Check for direct marketing mode (e.g., from Studio)
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('mode') === 'marketing' && storedConsent) {
      setCurrentState('MARKETING_MODE')
    }
  }, [shouldSkip])

  // State machine transitions with timer-based flow
  useEffect(() => {
    // Skip effect if we should bypass the state machine
    if (shouldSkip) return
    
    let timer: NodeJS.Timeout

    switch (currentState) {
      case 'BOOT':
        timer = setTimeout(() => setCurrentState('QUOTE_IN'), 800)
        break

      case 'QUOTE_IN':
        // Quote component will call handleQuoteComplete after animation
        break

      case 'CONSENT_PENDING':
        // Wait for user interaction with cookie banner
        break

      case 'QUOTE_WITH_OPTIONS':
        timer = setTimeout(() => setCurrentState('MARKETING_MODE'), 3800)
        break

      case 'MARKETING_MODE':
        // Final state - user can interact with the full website
        break
    }

    return () => {
      if (timer) clearTimeout(timer)
    }
  }, [currentState, shouldSkip])

  // Handle quote animation completion
  const handleQuoteComplete = () => {
    if (consentGiven) {
      setCurrentState('QUOTE_WITH_OPTIONS')
    } else {
      setCurrentState('CONSENT_PENDING')
    }
  }

  // Handle cookie consent
  const handleConsentAccepted = () => {
    setConsentGiven(true)
    setConsentType('full')
    setCurrentState('QUOTE_WITH_OPTIONS')

    // Store full consent
    localStorage.setItem('lukhas_cookie_type', 'full')

    // Emit event for external systems that might be listening
    window.dispatchEvent(new CustomEvent('lukhas:cookies:accepted'))
  }

  const handleConsentDeclined = () => {
    setConsentGiven(true)
    setConsentType('essential')
    setCurrentState('QUOTE_WITH_OPTIONS')

    // Store essential-only consent
    localStorage.setItem('lukhas_cookie_type', 'essential')

    // Emit event for external systems that might be listening
    window.dispatchEvent(new CustomEvent('lukhas:cookies:declined'))
  }

  // Handle preference change request
  const handleChangePreferences = () => {
    setCurrentState('CONSENT_PENDING')
  }

  // Apply state-based CSS classes to body
  useEffect(() => {
    // Skip effect if we should bypass the state machine
    if (shouldSkip) return
    
    const className = `state-${currentState.toLowerCase()}`
    document.body.classList.add(className)

    return () => {
      document.body.classList.remove(className)
    }
  }, [currentState, shouldSkip])


  // Early return for app routes, showcase, and skipState AFTER all hooks are declared
  if (shouldSkip) {
    return <>{children}</>
  }
  
  // Debug logging in development
  if (process.env.NODE_ENV === 'development' && !shouldSkip) {
    console.log('🎭 StateLayout:', { pathname, isAppRoute, isStudioRoute, currentState, consentGiven, skipState, shouldSkip })
  }

  return (
    <div className={`state-layout state-${currentState.toLowerCase()}`}>
      {/* Boot State - Simple loading */}
      {currentState === 'BOOT' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-blue-200 text-sm">Initializing LUKHAS...</p>
          </div>
        </div>
      )}

      {/* Quote In State - Show quote with fade-in animation */}
      {currentState === 'QUOTE_IN' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <div className="w-full max-w-5xl">
            <Quote onComplete={handleQuoteComplete} />
          </div>
        </div>
      )}

      {/* Consent Pending State - Show quote with cookie banner */}
      {currentState === 'CONSENT_PENDING' && (
        <>
          <div className="fixed inset-0 z-40 flex items-center justify-center px-4">
            <div className="w-full max-w-5xl">
              <Quote />
            </div>
          </div>
          <CookiesBanner
            onAccept={handleConsentAccepted}
            onDecline={handleConsentDeclined}
          />
        </>
      )}

      {/* Quote with Options State - Show quote with navigation options */}
      {currentState === 'QUOTE_WITH_OPTIONS' && (
        <>
          <div className="fixed inset-0 z-40 flex items-center justify-center px-4">
            <div className="w-full max-w-5xl">
              <Quote />
            </div>
          </div>

          {/* Navigation Options */}
          <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50">
            <div className="flex items-center space-x-4 bg-black/20 backdrop-blur-md rounded-full px-6 py-3 border border-white/10">
              <button
                onClick={() => setCurrentState('MARKETING_MODE')}
                className="px-4 py-2 text-white/80 hover:text-white transition-colors text-sm"
              >
                Explore LUKHAS
              </button>
              <div className="w-px h-4 bg-white/20" />
              <a
                href="/studio"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors text-sm"
              >
                Enter LUKHΛS Studio
              </a>
              <a
                href="/settings/layout"
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-full transition-colors text-sm"
              >
                Settings
              </a>
            </div>
          </div>
        </>
      )}

      {/* Marketing Mode - Full Website */}
      {currentState === 'MARKETING_MODE' && (
        <div className="min-h-screen">
          {/* Essential Mode Banner */}
          {consentType === 'essential' && (
            <EssentialModeBanner onChangePreferences={handleChangePreferences} />
          )}

          {/* Top navigation bar */}
          <nav className={`fixed left-0 right-0 z-30 bg-black/20 backdrop-blur-md border-b border-white/10 ${
            consentType === 'essential' ? 'top-12' : 'top-0'
          }`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <span className="text-2xl text-white lukhas-brand">LUKHΛS</span>
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
                  <a
                    href="/login"
                    className="text-white/80 hover:text-white transition-colors"
                  >
                    Sign In
                  </a>
                  <a
                    href="/studio"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    Enter LUKHΛS Studio
                  </a>
                </div>
              </div>
            </div>
          </nav>

          {/* Marketing content */}
          <main className={consentType === 'essential' ? 'pt-28' : 'pt-16'}>
            {children}
          </main>
        </div>
      )}

      {/* Always render children for routes that need them */}
      {currentState !== 'BOOT' && currentState !== 'QUOTE_IN' && (
        <div className={currentState === 'MARKETING_MODE' ? '' : 'invisible'}>
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
