'use client'

import { useState, useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'

interface CookiePreferences {
  necessary: boolean
  functional: boolean
  analytics: boolean
  marketing: boolean
}

interface CookieConsentProps {
  onAccept?: (preferences: CookiePreferences) => void
  onDecline?: () => void
}

export default function CookiesConsent({ onAccept, onDecline }: CookieConsentProps) {
  const [showModal, setShowModal] = useState(false)
  const [consentState, setConsentState] = useState<'initial' | 'choosing' | 'rewarded'>('initial')
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    functional: false,
    analytics: false,
    marketing: false
  })
  const [privacyPoints, setPrivacyPoints] = useState(6)
  const [rewardTier, setRewardTier] = useState(3)
  
  // Check if consent has already been given
  useEffect(() => {
    const storedConsent = localStorage.getItem('lukhas_cookie_consent')
    if (!storedConsent) {
      // Show consent after a short delay
      setTimeout(() => setShowModal(true), 1000)
    }
  }, [])
  
  // Calculate privacy points based on preferences
  useEffect(() => {
    let points = 6 // Start with maximum points
    
    // Subtract points for each optional cookie type enabled
    if (preferences.functional) points -= 1
    if (preferences.analytics) points -= 2
    if (preferences.marketing) points -= 3
    
    setPrivacyPoints(points)
    
    // Set reward tier based on privacy points
    if (points >= 6) {
      setRewardTier(3) // Highest tier (most private)
    } else if (points >= 4) {
      setRewardTier(2) // Mid tier
    } else if (points >= 1) {
      setRewardTier(1) // Basic tier
    } else {
      setRewardTier(0) // No reward (least private)
    }
  }, [preferences])
  
  // Toggle cookie preference
  const togglePreference = (type: keyof CookiePreferences) => {
    if (type === 'necessary') return // Can't disable necessary cookies
    
    setPreferences(prev => ({
      ...prev,
      [type]: !prev[type]
    }))
  }
  
  // Submit cookie consent
  const submitConsent = () => {
    setConsentState('rewarded')
    
    // Store consent in localStorage
    localStorage.setItem('lukhas_cookie_consent', JSON.stringify({
      preferences,
      timestamp: new Date().toISOString(),
      privacyPoints,
      rewardTier
    }))
    
    // Notify parent component
    if (onAccept) {
      onAccept(preferences)
    }
    
    // Close modal after showing reward
    setTimeout(() => {
      setShowModal(false)
    }, rewardTier > 0 ? 3000 : 1000)
  }
  
  // Decline all optional cookies
  const declineAll = () => {
    const minimalPreferences = {
      necessary: true,
      functional: false,
      analytics: false,
      marketing: false
    }
    
    setPreferences(minimalPreferences)
    setConsentState('rewarded')
    
    // Store consent
    localStorage.setItem('lukhas_cookie_consent', JSON.stringify({
      preferences: minimalPreferences,
      timestamp: new Date().toISOString(),
      privacyPoints: 6,
      rewardTier: 3
    }))
    
    if (onDecline) {
      onDecline()
    }
    
    setTimeout(() => setShowModal(false), 3000)
  }
  
  if (!showModal) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={() => consentState === 'rewarded' && setShowModal(false)}
      />
      
      {/* Modal */}
      <div className="relative max-w-md w-full bg-black/50 backdrop-blur-xl border border-white/20 rounded-lg overflow-hidden">
        {/* Close button (only show after consent) */}
        {consentState === 'rewarded' && (
          <button
            onClick={() => setShowModal(false)}
            className="absolute top-4 right-4 text-white/60 hover:text-white transition-colors"
            aria-label="Close"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        )}
        
        {/* Initial State */}
        {consentState === 'initial' && (
          <div className="p-8">
            <h2 className="text-xl font-light text-white mb-4">
              Privacy Preferences
            </h2>
            <p className="text-white/70 text-sm leading-relaxed mb-6">
              We value your privacy. Unlike most sites, we reward you for protecting your data. 
              Disable optional cookies to unlock enhanced features and experiences.
            </p>
            
            <div className="space-y-3">
              <button
                onClick={() => setConsentState('choosing')}
                className="w-full py-3 bg-white/10 hover:bg-white/20 border border-white/30 text-white rounded-lg transition-all text-sm font-light tracking-wider"
              >
                Choose Preferences
              </button>
              
              <button
                onClick={declineAll}
                className="w-full py-3 bg-transparent hover:bg-white/5 text-white/70 rounded-lg transition-all text-sm font-light tracking-wider"
              >
                Privacy First (Recommended)
              </button>
            </div>
          </div>
        )}
        
        {/* Choosing State */}
        {consentState === 'choosing' && (
          <div className="p-8">
            <h2 className="text-xl font-light text-white mb-6">
              Select Preferences
            </h2>
            
            {/* Cookie Options */}
            <div className="space-y-4 mb-6">
              {/* Necessary Cookies - Always on */}
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-white text-sm">Necessary</div>
                  <div className="text-white/60 text-xs mt-1">Required for basic functionality</div>
                </div>
                <div className="relative">
                  <div className="w-12 h-6 bg-white/20 rounded-full opacity-50"></div>
                  <div className="absolute top-0.5 left-6 w-5 h-5 bg-white rounded-full opacity-50"></div>
                </div>
              </div>
              
              {/* Functional Cookies */}
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-white text-sm">Functional</div>
                  <div className="text-white/60 text-xs mt-1">
                    Store preferences (-1 privacy point)
                  </div>
                </div>
                <button
                  onClick={() => togglePreference('functional')}
                  className="relative w-12 h-6 rounded-full transition-colors"
                  style={{ backgroundColor: preferences.functional ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.2)' }}
                >
                  <div 
                    className="absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform"
                    style={{ transform: preferences.functional ? 'translateX(24px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>
              
              {/* Analytics Cookies */}
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-white text-sm">Analytics</div>
                  <div className="text-white/60 text-xs mt-1">
                    Track usage (-2 privacy points)
                  </div>
                </div>
                <button
                  onClick={() => togglePreference('analytics')}
                  className="relative w-12 h-6 rounded-full transition-colors"
                  style={{ backgroundColor: preferences.analytics ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.2)' }}
                >
                  <div 
                    className="absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform"
                    style={{ transform: preferences.analytics ? 'translateX(24px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>
              
              {/* Marketing Cookies */}
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-white text-sm">Marketing</div>
                  <div className="text-white/60 text-xs mt-1">
                    Personalized content (-3 privacy points)
                  </div>
                </div>
                <button
                  onClick={() => togglePreference('marketing')}
                  className="relative w-12 h-6 rounded-full transition-colors"
                  style={{ backgroundColor: preferences.marketing ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.2)' }}
                >
                  <div 
                    className="absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform"
                    style={{ transform: preferences.marketing ? 'translateX(24px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>
            </div>
            
            {/* Privacy Rewards Display */}
            <div className="mb-6 border border-white/10 rounded-lg p-4">
              <div className="text-white/80 text-sm font-light tracking-wider mb-3">
                Privacy Rewards
              </div>
              
              {/* Points Bar */}
              <div className="flex items-center mb-3">
                <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-600 to-blue-600 transition-all duration-500"
                    style={{ width: `${(privacyPoints / 6) * 100}%` }}
                  />
                </div>
                <div className="ml-3 text-white text-sm">{privacyPoints}/6</div>
              </div>
              
              {/* Rewards List */}
              <div className="space-y-2">
                <div className={`flex items-center ${rewardTier >= 1 ? 'text-white' : 'text-white/40'}`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${rewardTier >= 1 ? 'bg-white' : 'bg-white/20'}`} />
                  <div className="text-xs">Enhanced security protocols</div>
                </div>
                <div className={`flex items-center ${rewardTier >= 2 ? 'text-white' : 'text-white/40'}`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${rewardTier >= 2 ? 'bg-white' : 'bg-white/20'}`} />
                  <div className="text-xs">Faster application performance</div>
                </div>
                <div className={`flex items-center ${rewardTier >= 3 ? 'text-white' : 'text-white/40'}`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${rewardTier >= 3 ? 'bg-white' : 'bg-white/20'}`} />
                  <div className="text-xs">Advanced dashboard features</div>
                </div>
              </div>
            </div>
            
            <button
              onClick={submitConsent}
              className="w-full py-3 bg-white/10 hover:bg-white/20 border border-white/30 text-white rounded-lg transition-all text-sm font-light tracking-wider"
            >
              Confirm Choices
            </button>
          </div>
        )}
        
        {/* Rewarded State */}
        {consentState === 'rewarded' && (
          <div className="p-8 text-center">
            <div className="text-5xl mb-4">
              {rewardTier === 0 && '📊'}
              {rewardTier === 1 && '🔒'}
              {rewardTier === 2 && '🛡️'}
              {rewardTier === 3 && '✨'}
            </div>
            
            <h2 className="text-xl font-light text-white mb-3">
              {rewardTier === 0 && 'Standard Experience'}
              {rewardTier === 1 && 'Enhanced Security'}
              {rewardTier === 2 && 'Advanced Privacy'}
              {rewardTier === 3 && 'Maximum Privacy'}
            </h2>
            
            <p className="text-white/70 text-sm leading-relaxed">
              {rewardTier === 0 && 'Preferences saved. Your experience includes all personalization features.'}
              {rewardTier === 1 && 'You\'ve unlocked enhanced security protocols by protecting some of your data.'}
              {rewardTier === 2 && 'You\'ve unlocked faster performance and enhanced security by valuing your privacy.'}
              {rewardTier === 3 && 'You\'ve unlocked all privacy rewards. Thank you for prioritizing your data privacy.'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}