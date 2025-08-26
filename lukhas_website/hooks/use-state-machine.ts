/**
 * React Hook for User Journey State Machine
 * Provides reactive state management for the app flow
 */

import { useEffect, useState, useCallback } from 'react'
import {
  AppState,
  AppEvent,
  StateConfig,
  UserJourneyStateMachine,
  getGlobalStateMachine
} from '@/lib/state-machine'

export interface UseStateMachineResult {
  // Current state
  currentState: AppState
  stateConfig: StateConfig

  // State checkers
  isBootState: boolean
  isQuoteState: boolean
  isConsentPending: boolean
  isQuoteWithOptions: boolean
  isMarketingMode: boolean
  isLoginFlow: boolean
  isStudioActive: boolean
  hasCompletedOnboarding: boolean

  // Actions
  transition: (event: AppEvent) => boolean
  canTransition: (event: AppEvent) => boolean
  reset: () => void

  // Effects
  activeEffects: string[]

  // Convenience actions
  enterStudio: () => void
  startLogin: () => void
  giveConsent: () => void
  completeQuote: () => void
}

export function useStateMachine(): UseStateMachineResult {
  const [stateMachine] = useState<UserJourneyStateMachine>(() => getGlobalStateMachine())
  const [currentState, setCurrentState] = useState<AppState>(stateMachine.getCurrentState())

  // Update local state when state machine changes
  useEffect(() => {
    const unsubscribe = stateMachine.subscribe((newState, event) => {
      setCurrentState(newState)

      // Log state changes for debugging
      if (process.env.NODE_ENV === 'development') {
        console.log(`🎯 State changed to: ${newState}`, { event })
      }
    })

    return unsubscribe
  }, [stateMachine])

  // Convenience actions
  const enterStudio = useCallback(() => {
    return stateMachine.transition('ENTER_STUDIO')
  }, [stateMachine])

  const startLogin = useCallback(() => {
    return stateMachine.transition('LOGIN_INITIATED')
  }, [stateMachine])

  const giveConsent = useCallback(() => {
    return stateMachine.transition('CONSENT_GIVEN')
  }, [stateMachine])

  const completeQuote = useCallback(() => {
    return stateMachine.transition('QUOTE_DISPLAYED')
  }, [stateMachine])

  const reset = useCallback(() => {
    return stateMachine.transition('RESET')
  }, [stateMachine])

  const transition = useCallback((event: AppEvent) => {
    return stateMachine.transition(event)
  }, [stateMachine])

  const canTransition = useCallback((event: AppEvent) => {
    return stateMachine.canTransition(event)
  }, [stateMachine])

  return {
    // Current state
    currentState,
    stateConfig: stateMachine.getStateConfig(),

    // State checkers
    isBootState: stateMachine.isBootState(),
    isQuoteState: stateMachine.isQuoteState(),
    isConsentPending: stateMachine.isConsentPending(),
    isQuoteWithOptions: stateMachine.isQuoteWithOptions(),
    isMarketingMode: stateMachine.isMarketingMode(),
    isLoginFlow: stateMachine.isLoginFlow(),
    isStudioActive: stateMachine.isStudioActive(),
    hasCompletedOnboarding: stateMachine.hasCompletedOnboarding(),

    // Actions
    transition,
    canTransition,
    reset,

    // Effects
    activeEffects: stateMachine.getActiveEffects(),

    // Convenience actions
    enterStudio,
    startLogin,
    giveConsent,
    completeQuote
  }
}

/**
 * Hook for components that only need to read state
 */
export function useStateMachineState(): {
  currentState: AppState
  isBootState: boolean
  isQuoteState: boolean
  isConsentPending: boolean
  isMarketingMode: boolean
  isLoginFlow: boolean
  isStudioActive: boolean
  hasCompletedOnboarding: boolean
  activeEffects: string[]
} {
  const {
    currentState,
    isBootState,
    isQuoteState,
    isConsentPending,
    isMarketingMode,
    isLoginFlow,
    isStudioActive,
    hasCompletedOnboarding,
    activeEffects
  } = useStateMachine()

  return {
    currentState,
    isBootState,
    isQuoteState,
    isConsentPending,
    isMarketingMode,
    isLoginFlow,
    isStudioActive,
    hasCompletedOnboarding,
    activeEffects
  }
}

/**
 * Hook for triggering state transitions with error handling
 */
export function useStateMachineActions(): {
  transition: (event: AppEvent) => Promise<boolean>
  canTransition: (event: AppEvent) => boolean
  reset: () => Promise<boolean>
  enterStudio: () => Promise<boolean>
  startLogin: () => Promise<boolean>
  giveConsent: () => Promise<boolean>
  completeQuote: () => Promise<boolean>
} {
  const {
    transition: syncTransition,
    canTransition,
    reset: syncReset,
    enterStudio: syncEnterStudio,
    startLogin: syncStartLogin,
    giveConsent: syncGiveConsent,
    completeQuote: syncCompleteQuote
  } = useStateMachine()

  // Wrap transitions with promises for async/await usage
  const transition = useCallback(async (event: AppEvent): Promise<boolean> => {
    try {
      return syncTransition(event)
    } catch (error) {
      console.error(`State transition failed: ${event}`, error)
      return false
    }
  }, [syncTransition])

  const reset = useCallback(async (): Promise<boolean> => {
    try {
      return syncReset()
    } catch (error) {
      console.error('State reset failed', error)
      return false
    }
  }, [syncReset])

  const enterStudio = useCallback(async (): Promise<boolean> => {
    try {
      return syncEnterStudio()
    } catch (error) {
      console.error('Enter studio failed', error)
      return false
    }
  }, [syncEnterStudio])

  const startLogin = useCallback(async (): Promise<boolean> => {
    try {
      return syncStartLogin()
    } catch (error) {
      console.error('Start login failed', error)
      return false
    }
  }, [syncStartLogin])

  const giveConsent = useCallback(async (): Promise<boolean> => {
    try {
      return syncGiveConsent()
    } catch (error) {
      console.error('Give consent failed', error)
      return false
    }
  }, [syncGiveConsent])

  const completeQuote = useCallback(async (): Promise<boolean> => {
    try {
      return syncCompleteQuote()
    } catch (error) {
      console.error('Complete quote failed', error)
      return false
    }
  }, [syncCompleteQuote])

  return {
    transition,
    canTransition,
    reset,
    enterStudio,
    startLogin,
    giveConsent,
    completeQuote
  }
}
