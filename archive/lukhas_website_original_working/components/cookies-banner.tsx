'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon, ShieldCheckIcon, EyeIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import { useStateMachineActions } from '@/hooks/use-state-machine'

interface CookiePreferences {
  necessary: boolean
  functional: boolean
  analytics: boolean
  marketing: boolean
}

interface CookieBannerProps {
  onAccept?: (preferences: CookiePreferences) => void
  onDecline?: () => void
}

export default function CookiesBanner({ onAccept, onDecline }: CookieBannerProps) {
  const { giveConsent } = useStateMachineActions()
  const [showBanner, setShowBanner] = useState(true)
  const [isVisible, setIsVisible] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    functional: false,
    analytics: false,
    marketing: false
  })
  const [privacyPoints, setPrivacyPoints] = useState(6)

  // Smooth entry animation
  useEffect(() => {
    const storedConsent = localStorage.getItem('lukhas_cookie_consent')
    console.log('🍪 CookieBanner mount - stored consent:', storedConsent)
    if (storedConsent) {
      console.log('🍪 Consent already given, hiding banner')
      setShowBanner(false)
    } else {
      console.log('🍪 No consent found, showing banner in 300ms')
      // Smooth entry from bottom
      const timer = setTimeout(() => setIsVisible(true), 300)
      return () => clearTimeout(timer)
    }
  }, [])

  // Calculate privacy points
  useEffect(() => {
    let points = 6
    if (preferences.functional) points -= 1
    if (preferences.analytics) points -= 2
    if (preferences.marketing) points -= 3
    setPrivacyPoints(Math.max(0, points))
  }, [preferences])

  const handleAccept = async () => {
    localStorage.setItem('lukhas_cookie_consent', JSON.stringify({
      preferences,
      timestamp: new Date().toISOString(),
      privacyPoints
    }))

    // Smooth exit first
    setIsVisible(false)
    setTimeout(() => {
      setShowBanner(false)
      if (onAccept) onAccept(preferences)
    }, 500)
  }

  const handleDeclineAll = async () => {
    const minimalPreferences = {
      necessary: true,
      functional: false,
      analytics: false,
      marketing: false
    }

    localStorage.setItem('lukhas_cookie_consent', JSON.stringify({
      preferences: minimalPreferences,
      timestamp: new Date().toISOString(),
      privacyPoints: 6
    }))

    // Smooth exit first
    setIsVisible(false)
    setTimeout(() => {
      setShowBanner(false)
      if (onDecline) onDecline()
    }, 500)
  }

  const togglePreference = (type: keyof CookiePreferences) => {
    if (type === 'necessary') return
    setPreferences(prev => ({ ...prev, [type]: !prev[type] }))
  }

  if (!showBanner) return null

  return (
    <div 
      className={`fixed bottom-0 left-0 right-0 z-40 transform transition-transform duration-500 ease-out ${
        isVisible ? 'translate-y-0' : 'translate-y-full'
      }`}
    >
      {/* Main Banner */}
      <div className="bg-black/90 backdrop-blur-xl border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Content */}
            <div className="flex-1 pr-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  <ShieldCheckIcon className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-white text-sm leading-relaxed">
                    We respect your privacy. Choose how we can improve your experience while protecting your data.
                    {!showDetails && (
                      <button 
                        onClick={() => setShowDetails(true)}
                        className="text-blue-400 hover:text-blue-300 ml-2 underline text-sm"
                      >
                        Cookie preferences
                      </button>
                    )}
                  </p>
                  
                  {/* Privacy Points Indicator */}
                  <div className="flex items-center mt-2 space-x-2">
                    <div className="flex items-center space-x-1">
                      <ShieldCheckIcon className="w-4 h-4 text-green-400" />
                      <span className="text-green-400 text-xs font-medium">
                        Privacy Score: {privacyPoints}/6
                      </span>
                    </div>
                    {privacyPoints === 6 && (
                      <span className="text-xs text-green-300">Maximum Privacy</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-3">
              <button
                onClick={handleDeclineAll}
                className="px-4 py-2 text-sm text-white/80 hover:text-white border border-white/20 rounded-md hover:bg-white/5 transition-colors"
              >
                Decline non-essential cookies
              </button>
              <button
                onClick={handleAccept}
                className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
              >
                Accept Selected
              </button>
            </div>
          </div>

          {/* Detailed Preferences */}
          {showDetails && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="grid md:grid-cols-3 gap-4">
                {/* Necessary */}
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    <ShieldCheckIcon className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-white">Essential</h4>
                      <div className="w-8 h-4 bg-green-600 rounded-full flex items-center justify-end pr-1">
                        <div className="w-3 h-3 bg-white rounded-full" />
                      </div>
                    </div>
                    <p className="text-xs text-white/60 mt-1">Required for basic functionality</p>
                  </div>
                </div>

                {/* Functional */}
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    <EyeIcon className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-white">Functional</h4>
                      <button
                        onClick={() => togglePreference('functional')}
                        className={`w-8 h-4 rounded-full flex items-center transition-colors ${
                          preferences.functional ? 'bg-blue-600 justify-end pr-1' : 'bg-gray-600 justify-start pl-1'
                        }`}
                      >
                        <div className="w-3 h-3 bg-white rounded-full" />
                      </button>
                    </div>
                    <p className="text-xs text-white/60 mt-1">Enhanced features and preferences</p>
                  </div>
                </div>

                {/* Analytics */}
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    <ChartBarIcon className="w-4 h-4 text-orange-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-white">Analytics</h4>
                      <button
                        onClick={() => togglePreference('analytics')}
                        className={`w-8 h-4 rounded-full flex items-center transition-colors ${
                          preferences.analytics ? 'bg-orange-600 justify-end pr-1' : 'bg-gray-600 justify-start pl-1'
                        }`}
                      >
                        <div className="w-3 h-3 bg-white rounded-full" />
                      </button>
                    </div>
                    <p className="text-xs text-white/60 mt-1">Help us improve the experience</p>
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center mt-4">
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-sm text-white/60 hover:text-white/80"
                >
                  ← Back
                </button>
                <div className="text-xs text-white/40">
                  We never sell your data. Read our <a href="/privacy" className="text-blue-400 hover:text-blue-300">privacy policy</a>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}