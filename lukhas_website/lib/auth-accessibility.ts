// LUKHAS AI Authentication Accessibility Enhancements
// Ensures WCAG 2.1 AA compliance for ΛiD authentication system

import { AnnouncementManager, FocusManager } from './accessibility'

/**
 * Authentication-specific accessibility utilities
 */
export class AuthAccessibility {

  /**
   * Enhance passkey authentication flow for screen readers
   */
  static enhancePasskeyFlow() {
    // Add live region for passkey status
    const passkeyRegion = document.createElement('div')
    passkeyRegion.setAttribute('aria-live', 'polite')
    passkeyRegion.setAttribute('aria-label', 'Passkey authentication status')
    passkeyRegion.className = 'sr-only'
    passkeyRegion.id = 'passkey-status'
    document.body.appendChild(passkeyRegion)

    // Enhance passkey buttons with proper ARIA
    const passkeyButtons = document.querySelectorAll('[data-passkey-action]')
    passkeyButtons.forEach(button => {
      button.setAttribute('aria-describedby', 'passkey-help')

      // Add help text if not present
      if (!document.getElementById('passkey-help')) {
        const helpText = document.createElement('div')
        helpText.id = 'passkey-help'
        helpText.className = 'sr-only'
        helpText.textContent = 'Use your device biometric sensor or security key to authenticate. Touch ID, Face ID, Windows Hello, or FIDO2 security keys are supported.'
        button.parentElement?.appendChild(helpText)
      }
    })
  }

  /**
   * Enhance magic link flow accessibility
   */
  static enhanceMagicLinkFlow() {
    const emailInputs = document.querySelectorAll('input[type="email"]')
    emailInputs.forEach(input => {
      // Add proper autocomplete
      if (!input.getAttribute('autocomplete')) {
        input.setAttribute('autocomplete', 'email')
      }

      // Enhance validation messages
      input.addEventListener('invalid', (e) => {
        const target = e.target as HTMLInputElement
        const errorMsg = target.validationMessage
        AnnouncementManager.announce(`Email validation error: ${errorMsg}`, 'assertive')
      })
    })
  }

  /**
   * Enhance multi-step registration flow
   */
  static enhanceRegistrationFlow() {
    // Add landmark for progress indicator
    const progressElements = document.querySelectorAll('[role="progressbar"]')
    progressElements.forEach(progress => {
      const currentStep = progress.getAttribute('aria-valuenow')
      const maxStep = progress.getAttribute('aria-valuemax')

      if (currentStep && maxStep) {
        const stepAnnouncement = `Registration step ${currentStep} of ${maxStep}`
        AnnouncementManager.announce(stepAnnouncement, 'polite')
      }
    })

    // Enhance step navigation
    const stepButtons = document.querySelectorAll('[data-step-button]')
    stepButtons.forEach(button => {
      button.addEventListener('click', () => {
        setTimeout(() => {
          const firstInput = document.querySelector('input:not([disabled])') as HTMLInputElement
          if (firstInput) {
            FocusManager.pushFocus(firstInput)
          }
        }, 100)
      })
    })
  }

  /**
   * Add keyboard shortcuts for common authentication actions
   */
  static addKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Enter for primary action
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const primaryButton = document.querySelector('[data-primary-action]') as HTMLButtonElement
        if (primaryButton && !primaryButton.disabled) {
          e.preventDefault()
          primaryButton.click()
        }
      }

      // Escape to cancel/go back
      if (e.key === 'Escape') {
        const backButton = document.querySelector('[data-back-action]') as HTMLButtonElement
        const cancelButton = document.querySelector('[data-cancel-action]') as HTMLButtonElement
        const targetButton = cancelButton || backButton

        if (targetButton) {
          e.preventDefault()
          targetButton.click()
        }
      }
    })
  }

  /**
   * Enhance error handling accessibility
   */
  static enhanceErrorHandling() {
    // Auto-focus first error
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node instanceof Element && node.getAttribute('role') === 'alert') {
              // Focus the error for immediate attention
              setTimeout(() => {
                const focusableError = node.querySelector('button, a, [tabindex]') as HTMLElement
                if (focusableError) {
                  FocusManager.pushFocus(focusableError)
                } else {
                  // Make the error itself focusable if no interactive elements
                  node.setAttribute('tabindex', '-1')
                  FocusManager.pushFocus(node as HTMLElement)
                }
              }, 100)
            }
          })
        }
      })
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true
    })
  }

  /**
   * Enhance loading states for screen readers
   */
  static enhanceLoadingStates() {
    const loadingObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'aria-busy') {
          const target = mutation.target as HTMLElement
          const isBusy = target.getAttribute('aria-busy') === 'true'

          if (isBusy) {
            AnnouncementManager.announce('Processing your request, please wait...', 'polite')
          }
        }
      })
    })

    // Observe all form elements for loading states
    const forms = document.querySelectorAll('form')
    forms.forEach(form => {
      loadingObserver.observe(form, {
        attributes: true,
        attributeFilter: ['aria-busy']
      })
    })
  }

  /**
   * Add high contrast mode support
   */
  static addHighContrastSupport() {
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      document.documentElement.classList.add('high-contrast')

      // Enhance contrast for Lambda symbols
      const lambdaSymbols = document.querySelectorAll('[aria-label*="Lambda"], [aria-label*="LUKHAS"]')
      lambdaSymbols.forEach(symbol => {
        symbol.classList.add('high-contrast-lambda')
      })
    }

    // Listen for contrast preference changes
    window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
      if (e.matches) {
        document.documentElement.classList.add('high-contrast')
      } else {
        document.documentElement.classList.remove('high-contrast')
      }
    })
  }

  /**
   * Enhance reduced motion support
   */
  static addReducedMotionSupport() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.documentElement.classList.add('reduce-motion')

      // Replace animations with instant state changes
      const animations = document.querySelectorAll('[data-animation]')
      animations.forEach(element => {
        element.classList.add('no-animation')
      })
    }
  }

  /**
   * Add voice control enhancements
   */
  static addVoiceControlSupport() {
    // Add voice labels to key elements
    const authButtons = document.querySelectorAll('button[type="submit"], [data-passkey-action]')
    authButtons.forEach((button, index) => {
      if (!button.getAttribute('data-voice-label')) {
        const buttonText = button.textContent?.trim() || `Authentication button ${index + 1}`
        button.setAttribute('data-voice-label', buttonText)
      }
    })

    // Add landmarks for voice navigation
    const mainContent = document.querySelector('main')
    if (mainContent && !mainContent.getAttribute('aria-label')) {
      mainContent.setAttribute('aria-label', 'Authentication form')
    }
  }

  /**
   * Initialize all authentication accessibility enhancements
   */
  static initialize() {
    if (typeof window === 'undefined') return

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.setupAccessibilityFeatures()
      })
    } else {
      this.setupAccessibilityFeatures()
    }
  }

  private static setupAccessibilityFeatures() {
    this.enhancePasskeyFlow()
    this.enhanceMagicLinkFlow()
    this.enhanceRegistrationFlow()
    this.addKeyboardShortcuts()
    this.enhanceErrorHandling()
    this.enhanceLoadingStates()
    this.addHighContrastSupport()
    this.addReducedMotionSupport()
    this.addVoiceControlSupport()

    // Add skip links if not present
    this.addSkipLinks()

    // Ensure proper focus management
    this.setupFocusManagement()
  }

  private static addSkipLinks() {
    if (!document.querySelector('.skip-link')) {
      const skipLink = document.createElement('a')
      skipLink.href = '#main-content'
      skipLink.className = 'skip-link sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-trinity-identity text-white px-4 py-2 rounded focus:outline-none focus:ring-2 focus:ring-white z-50'
      skipLink.textContent = 'Skip to main content'
      document.body.insertBefore(skipLink, document.body.firstChild)
    }
  }

  private static setupFocusManagement() {
    // Ensure first interactive element gets focus on page load
    setTimeout(() => {
      const firstInteractive = document.querySelector('input:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])') as HTMLElement
      if (firstInteractive && !document.activeElement?.matches('input, button, [tabindex]')) {
        firstInteractive.focus()
      }
    }, 100)
  }
}

/**
 * Color contrast validation for WCAG compliance
 */
export class AuthColorContrast {

  /**
   * Validate authentication page color contrasts
   */
  static validateAuthColors() {
    const colorPairs = [
      { fg: '#ffffff', bg: '#000000', context: 'primary text' },
      { fg: '#8b5cf6', bg: '#000000', context: 'trinity-identity on dark' },
      { fg: '#06b6d4', bg: '#000000', context: 'trinity-consciousness on dark' },
      { fg: '#10b981', bg: '#000000', context: 'trinity-guardian on dark' },
      { fg: '#ef4444', bg: '#000000', context: 'error text on dark' },
      { fg: '#f59e0b', bg: '#000000', context: 'warning text on dark' }
    ]

    colorPairs.forEach(pair => {
      const ratio = this.calculateContrastRatio(pair.fg, pair.bg)
      const meetsAA = ratio >= 4.5
      const meetsAAA = ratio >= 7

      if (!meetsAA) {
        console.warn(`⚠️ WCAG AA contrast failure: ${pair.context} - ratio: ${ratio.toFixed(2)}`)
      } else if (meetsAAA) {
        console.log(`✅ WCAG AAA contrast pass: ${pair.context} - ratio: ${ratio.toFixed(2)}`)
      } else {
        console.log(`✅ WCAG AA contrast pass: ${pair.context} - ratio: ${ratio.toFixed(2)}`)
      }
    })
  }

  private static calculateContrastRatio(color1: string, color2: string): number {
    const lum1 = this.getLuminance(color1)
    const lum2 = this.getLuminance(color2)
    const brightest = Math.max(lum1, lum2)
    const darkest = Math.min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)
  }

  private static getLuminance(color: string): number {
    const hex = color.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16) / 255
    const g = parseInt(hex.substr(2, 2), 16) / 255
    const b = parseInt(hex.substr(4, 2), 16) / 255

    const [rs, gs, bs] = [r, g, b].map(c => {
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    })

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }
}

// Auto-initialize on import
if (typeof window !== 'undefined') {
  AuthAccessibility.initialize()

  // Validate colors in development
  if (process.env.NODE_ENV === 'development') {
    AuthColorContrast.validateAuthColors()
  }
}

export default AuthAccessibility
