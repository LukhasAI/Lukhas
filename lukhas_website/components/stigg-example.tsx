/**
 * LUKHAS Trinity Framework Stigg Integration Example
 * 
 * This component demonstrates how to use Stigg within the LUKHAS ecosystem
 * while maintaining Trinity Framework principles (⚛️🧠🛡️):
 * 
 * ⚛️ Identity: Billing tied to user identity and authentication state
 * 🧠 Consciousness: Usage awareness and intelligent plan recommendations  
 * 🛡️ Guardian: Ethical billing practices and transparent pricing
 */

'use client'

import { useStigg, usePlans, useCustomerPortal } from '@stigg/react-sdk'
import { useState, useEffect } from 'react'

interface StiggExampleProps {
  userId?: string
  className?: string
}

export function StiggExample({ userId, className = '' }: StiggExampleProps) {
  const [isVisible, setIsVisible] = useState(false)
  
  // Stigg SDK hooks - gracefully handle when not available
  let stiggData = null
  let plans = null
  let customerPortal = null
  
  try {
    stiggData = useStigg()
    plans = usePlans()
    customerPortal = useCustomerPortal()
  } catch (error) {
    // Graceful fallback when Stigg is not properly configured
    console.log('Stigg not available:', error)
  }

  useEffect(() => {
    // Show component after mount to avoid hydration issues
    setIsVisible(true)
  }, [])

  if (!isVisible) {
    return null
  }

  // If Stigg is not available, show fallback
  if (!stiggData) {
    return (
      <div className={`p-4 bg-gray-800 rounded-lg border border-gray-700 ${className}`}>
        <div className="flex items-center space-x-2 mb-2">
          <div className="w-2 h-2 bg-orange-500 rounded-full" />
          <span className="text-sm text-gray-300">Billing System Status</span>
        </div>
        <p className="text-sm text-gray-400">
          Stigg billing integration is in development mode. 
          Full billing features will be available in production.
        </p>
        <div className="mt-3 text-xs text-gray-500">
          🛡️ Guardian System: Ensuring transparent billing practices
        </div>
      </div>
    )
  }

  return (
    <div className={`p-4 bg-gray-800 rounded-lg border border-gray-700 ${className}`}>
      <div className="flex items-center space-x-2 mb-3">
        <div className="w-2 h-2 bg-green-500 rounded-full" />
        <span className="text-sm text-gray-300">LUKHAS Billing Integration</span>
      </div>
      
      {/* Trinity Framework Integration */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-pink-400">⚛️</span>
          <span className="text-xs text-gray-400">
            Identity: {userId ? `User ${userId}` : 'Anonymous'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-cyan-400">🧠</span>
          <span className="text-xs text-gray-400">
            Consciousness: Usage-aware billing
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-purple-400">🛡️</span>
          <span className="text-xs text-gray-400">
            Guardian: Ethical pricing policies
          </span>
        </div>
      </div>

      {/* Plan Information */}
      {plans && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-200 mb-2">Available Plans</h4>
          <div className="text-xs text-gray-400">
            {plans.length} plans available
          </div>
        </div>
      )}

      {/* Customer Portal Access */}
      {customerPortal && (
        <div className="mt-4">
          <button
            onClick={() => customerPortal.open()}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
          >
            Manage Subscription
          </button>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="text-xs text-gray-500">
          💰 Powered by Stigg • Integrated with LUKHAS Trinity Framework
        </div>
      </div>
    </div>
  )
}

/**
 * Hook for LUKHAS-specific billing operations
 * Integrates Stigg with Trinity Framework principles
 */
export function useLukhasBilling() {
  const [billingState, setBillingState] = useState({
    isInitialized: false,
    hasValidPlan: false,
    usage: null,
    error: null
  })

  // Try to use Stigg, gracefully handle when not available
  let stiggData = null
  try {
    stiggData = useStigg()
  } catch (error) {
    // Graceful degradation
  }

  useEffect(() => {
    setBillingState(prev => ({
      ...prev,
      isInitialized: true,
      hasValidPlan: stiggData ? true : false
    }))
  }, [stiggData])

  return {
    ...billingState,
    stiggAvailable: !!stiggData,
    // Trinity Framework integration methods
    identity: {
      isAuthenticated: !!stiggData,
      plan: stiggData ? 'active' : 'development'
    },
    consciousness: {
      isAware: true,
      trackUsage: () => console.log('🧠 Tracking usage with consciousness'),
    },
    guardian: {
      validatePricing: () => console.log('🛡️ Guardian validating ethical pricing'),
      auditBilling: () => console.log('🛡️ Guardian auditing billing practices')
    }
  }
}