/**
 * User Journey State Machine
 * Based on visual_studio.json specifications
 * Handles the complete flow: BOOT → QUOTE_IN → CONSENT_PENDING → MARKETING_MODE → LOGIN_FLOW → STUDIO
 */

export type AppState = 
  | 'BOOT'
  | 'QUOTE_IN' 
  | 'CONSENT_PENDING'
  | 'QUOTE_WITH_OPTIONS'
  | 'MARKETING_MODE'
  | 'LOGIN_FLOW'
  | 'STUDIO'

export type AppEvent =
  | 'SYSTEM_READY'
  | 'QUOTE_DISPLAYED'
  | 'CONSENT_REQUIRED'
  | 'CONSENT_GIVEN'
  | 'MARKETING_COMPLETE'
  | 'LOGIN_INITIATED'
  | 'LOGIN_SUCCESS'
  | 'ENTER_STUDIO'
  | 'RESET'

export interface StateConfig {
  state: AppState
  duration?: number // milliseconds
  autoTransition?: {
    event: AppEvent
    delay: number
  }
  effects?: string[] // CSS classes or animation triggers
  allowedTransitions: AppEvent[]
}

export const STATE_CONFIGS: Record<AppState, StateConfig> = {
  BOOT: {
    state: 'BOOT',
    duration: 1500,
    autoTransition: {
      event: 'SYSTEM_READY',
      delay: 1500
    },
    effects: ['loading-spinner'],
    allowedTransitions: ['SYSTEM_READY', 'RESET']
  },
  
  QUOTE_IN: {
    state: 'QUOTE_IN',
    duration: 3000,
    autoTransition: {
      event: 'QUOTE_DISPLAYED',
      delay: 3000
    },
    effects: ['quote-dissolve-in'],
    allowedTransitions: ['QUOTE_DISPLAYED', 'CONSENT_REQUIRED', 'RESET']
  },
  
  CONSENT_PENDING: {
    state: 'CONSENT_PENDING',
    effects: ['consent-banner-active'],
    allowedTransitions: ['CONSENT_GIVEN', 'RESET']
  },

  QUOTE_WITH_OPTIONS: {
    state: 'QUOTE_WITH_OPTIONS',
    effects: ['quote-visible', 'options-visible'],
    allowedTransitions: ['MARKETING_COMPLETE', 'ENTER_STUDIO', 'RESET']
  },
  
  MARKETING_MODE: {
    state: 'MARKETING_MODE',
    effects: ['marketing-active', 'top-bar-visible'],
    allowedTransitions: ['LOGIN_INITIATED', 'ENTER_STUDIO', 'CONSENT_REQUIRED', 'RESET']
  },
  
  LOGIN_FLOW: {
    state: 'LOGIN_FLOW',
    effects: ['login-modal-active'],
    allowedTransitions: ['LOGIN_SUCCESS', 'MARKETING_COMPLETE', 'RESET']
  },
  
  STUDIO: {
    state: 'STUDIO',
    effects: ['studio-active', 'top-bar-auto-hide'],
    allowedTransitions: ['RESET']
  }
}

export const STATE_TRANSITIONS: Record<AppState, Partial<Record<AppEvent, AppState>>> = {
  BOOT: {
    SYSTEM_READY: 'QUOTE_IN',
    RESET: 'BOOT'
  },
  
  QUOTE_IN: {
    QUOTE_DISPLAYED: 'CONSENT_PENDING',
    CONSENT_REQUIRED: 'CONSENT_PENDING',
    RESET: 'BOOT'
  },
  
  CONSENT_PENDING: {
    CONSENT_GIVEN: 'QUOTE_WITH_OPTIONS',
    RESET: 'BOOT'
  },

  QUOTE_WITH_OPTIONS: {
    MARKETING_COMPLETE: 'MARKETING_MODE',
    ENTER_STUDIO: 'STUDIO',
    RESET: 'BOOT'
  },
  
  MARKETING_MODE: {
    LOGIN_INITIATED: 'LOGIN_FLOW',
    ENTER_STUDIO: 'STUDIO',
    CONSENT_REQUIRED: 'CONSENT_PENDING',
    RESET: 'BOOT'
  },
  
  LOGIN_FLOW: {
    LOGIN_SUCCESS: 'STUDIO',
    MARKETING_COMPLETE: 'MARKETING_MODE', // Back to marketing if login fails
    RESET: 'BOOT'
  },
  
  STUDIO: {
    RESET: 'BOOT'
  }
}

export class UserJourneyStateMachine {
  private currentState: AppState = 'BOOT'
  private listeners: Array<(state: AppState, event?: AppEvent) => void> = []
  private timeouts: Map<string, NodeJS.Timeout> = new Map()

  constructor(initialState: AppState = 'BOOT') {
    this.currentState = initialState
    console.log('🎯 State machine initialized:', initialState)
    this.setupAutoTransitions()
  }

  public getCurrentState(): AppState {
    return this.currentState
  }

  public getStateConfig(): StateConfig {
    return STATE_CONFIGS[this.currentState]
  }

  public canTransition(event: AppEvent): boolean {
    const config = this.getStateConfig()
    return config.allowedTransitions.includes(event)
  }

  public transition(event: AppEvent): boolean {
    if (!this.canTransition(event)) {
      console.warn(`Invalid transition: ${event} not allowed from ${this.currentState}`)
      return false
    }

    const nextState = STATE_TRANSITIONS[this.currentState][event]
    
    if (!nextState) {
      console.warn(`No transition defined for ${event} from ${this.currentState}`)
      return false
    }

    console.log(`State transition: ${this.currentState} --[${event}]--> ${nextState}`)
    
    this.currentState = nextState
    this.setupAutoTransitions()
    this.notifyListeners(event)
    
    return true
  }

  public subscribe(listener: (state: AppState, event?: AppEvent) => void): () => void {
    this.listeners.push(listener)
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  private notifyListeners(event?: AppEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentState, event)
      } catch (error) {
        console.error('State machine listener error:', error)
      }
    })
  }

  private setupAutoTransitions(): void {
    // Clear existing timeouts
    this.timeouts.forEach(timeout => clearTimeout(timeout))
    this.timeouts.clear()

    const config = this.getStateConfig()
    
    if (config.autoTransition) {
      const timeout = setTimeout(() => {
        if (this.canTransition(config.autoTransition!.event)) {
          this.transition(config.autoTransition!.event)
        }
      }, config.autoTransition.delay)
      
      this.timeouts.set(`auto_${this.currentState}`, timeout)
    }
  }

  public destroy(): void {
    this.timeouts.forEach(timeout => clearTimeout(timeout))
    this.timeouts.clear()
    this.listeners.length = 0
  }

  // Utility methods for common state checks
  public isBootState(): boolean {
    return this.currentState === 'BOOT'
  }

  public isQuoteState(): boolean {
    return this.currentState === 'QUOTE_IN'
  }

  public isConsentPending(): boolean {
    return this.currentState === 'CONSENT_PENDING'
  }

  public isQuoteWithOptions(): boolean {
    return this.currentState === 'QUOTE_WITH_OPTIONS'
  }

  public isMarketingMode(): boolean {
    return this.currentState === 'MARKETING_MODE'
  }

  public isLoginFlow(): boolean {
    return this.currentState === 'LOGIN_FLOW'
  }

  public isStudioActive(): boolean {
    return this.currentState === 'STUDIO'
  }

  // Get current state effects for CSS/UI
  public getActiveEffects(): string[] {
    return this.getStateConfig().effects || []
  }

  // Check if user has completed onboarding
  public hasCompletedOnboarding(): boolean {
    return this.currentState === 'MARKETING_MODE' || this.currentState === 'STUDIO'
  }
}

// Global singleton instance
let globalStateMachine: UserJourneyStateMachine | null = null

export function getGlobalStateMachine(): UserJourneyStateMachine {
  if (!globalStateMachine) {
    globalStateMachine = new UserJourneyStateMachine()
  }
  return globalStateMachine
}

export function resetGlobalStateMachine(): void {
  if (globalStateMachine) {
    globalStateMachine.destroy()
  }
  globalStateMachine = new UserJourneyStateMachine()
}