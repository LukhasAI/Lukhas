// Accessibility utilities for LUKHAS AI authentication system
// Ensures WCAG 2.1 AA compliance and enhanced user experience

/**
 * Focus management utilities for improved keyboard navigation
 */
export class FocusManager {
  private static focusStack: HTMLElement[] = []

  /**
   * Store current focus and move to new element
   * @param element Element to focus
   */
  static pushFocus(element: HTMLElement | null) {
    if (document.activeElement instanceof HTMLElement) {
      this.focusStack.push(document.activeElement)
    }
    if (element) {
      element.focus()
    }
  }

  /**
   * Restore previous focus from stack
   */
  static popFocus() {
    const previousElement = this.focusStack.pop()
    if (previousElement && document.body.contains(previousElement)) {
      previousElement.focus()
    }
  }

  /**
   * Focus first element with error
   */
  static focusFirstError() {
    const errorElement = document.querySelector('[role="alert"]') as HTMLElement
    if (errorElement) {
      errorElement.focus()
    }
  }

  /**
   * Trap focus within a container (for modals/dialogs)
   */
  static trapFocus(container: HTMLElement) {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>

    if (focusableElements.length === 0) return

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    container.addEventListener('keydown', handleTabKey)
    firstElement.focus()

    return () => container.removeEventListener('keydown', handleTabKey)
  }
}

/**
 * Announces dynamic content changes to screen readers
 */
export class AnnouncementManager {
  private static liveRegion: HTMLElement | null = null

  /**
   * Initialize live region for announcements
   */
  static initialize() {
    if (typeof window === 'undefined') return

    this.liveRegion = document.createElement('div')
    this.liveRegion.setAttribute('aria-live', 'polite')
    this.liveRegion.setAttribute('aria-atomic', 'true')
    this.liveRegion.style.position = 'absolute'
    this.liveRegion.style.left = '-10000px'
    this.liveRegion.style.width = '1px'
    this.liveRegion.style.height = '1px'
    this.liveRegion.style.overflow = 'hidden'
    document.body.appendChild(this.liveRegion)
  }

  /**
   * Announce message to screen readers
   * @param message Message to announce
   * @param priority Priority level (polite | assertive)
   */
  static announce(message: string, priority: 'polite' | 'assertive' = 'polite') {
    if (!this.liveRegion) {
      this.initialize()
    }

    if (this.liveRegion) {
      this.liveRegion.setAttribute('aria-live', priority)
      this.liveRegion.textContent = message

      // Clear after announcement
      setTimeout(() => {
        if (this.liveRegion) {
          this.liveRegion.textContent = ''
        }
      }, 1000)
    }
  }

  /**
   * Announce authentication state changes
   */
  static announceAuthState(state: 'loading' | 'success' | 'error', message?: string) {
    const announcements = {
      loading: 'Authentication in progress...',
      success: message || 'Authentication successful',
      error: message || 'Authentication failed'
    }

    this.announce(announcements[state], state === 'error' ? 'assertive' : 'polite')
  }
}

/**
 * Color contrast utilities for WCAG compliance
 */
export class ContrastChecker {
  /**
   * Calculate relative luminance of a color
   */
  private static getLuminance(r: number, g: number, b: number): number {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    })
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }

  /**
   * Calculate contrast ratio between two colors
   */
  static getContrastRatio(color1: string, color2: string): number {
    const hex1 = color1.replace('#', '')
    const hex2 = color2.replace('#', '')

    const r1 = parseInt(hex1.substr(0, 2), 16)
    const g1 = parseInt(hex1.substr(2, 2), 16)
    const b1 = parseInt(hex1.substr(4, 2), 16)

    const r2 = parseInt(hex2.substr(0, 2), 16)
    const g2 = parseInt(hex2.substr(2, 2), 16)
    const b2 = parseInt(hex2.substr(4, 2), 16)

    const lum1 = this.getLuminance(r1, g1, b1)
    const lum2 = this.getLuminance(r2, g2, b2)

    const brightest = Math.max(lum1, lum2)
    const darkest = Math.min(lum1, lum2)

    return (brightest + 0.05) / (darkest + 0.05)
  }

  /**
   * Check if color combination meets WCAG AA standard (4.5:1)
   */
  static meetsWCAGAA(foreground: string, background: string): boolean {
    return this.getContrastRatio(foreground, background) >= 4.5
  }

  /**
   * Check if color combination meets WCAG AAA standard (7:1)
   */
  static meetsWCAGAAA(foreground: string, background: string): boolean {
    return this.getContrastRatio(foreground, background) >= 7
  }
}

/**
 * Keyboard navigation helpers
 */
export class KeyboardNavigation {
  /**
   * Handle escape key for closing modals/dropdowns
   */
  static handleEscape(callback: () => void) {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        callback()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }

  /**
   * Handle arrow keys for navigation
   */
  static handleArrowNavigation(
    container: HTMLElement,
    options: {
      horizontal?: boolean
      vertical?: boolean
      wrap?: boolean
    } = {}
  ) {
    const { horizontal = true, vertical = true, wrap = true } = options

    const focusableElements = container.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return

      e.preventDefault()

      const currentIndex = Array.from(focusableElements).indexOf(document.activeElement as HTMLElement)
      if (currentIndex === -1) return

      let nextIndex = currentIndex

      if ((e.key === 'ArrowRight' && horizontal) || (e.key === 'ArrowDown' && vertical)) {
        nextIndex = currentIndex + 1
        if (nextIndex >= focusableElements.length) {
          nextIndex = wrap ? 0 : currentIndex
        }
      } else if ((e.key === 'ArrowLeft' && horizontal) || (e.key === 'ArrowUp' && vertical)) {
        nextIndex = currentIndex - 1
        if (nextIndex < 0) {
          nextIndex = wrap ? focusableElements.length - 1 : currentIndex
        }
      }

      focusableElements[nextIndex]?.focus()
    }

    container.addEventListener('keydown', handleKeyDown)
    return () => container.removeEventListener('keydown', handleKeyDown)
  }
}

/**
 * Form accessibility enhancements
 */
export class FormAccessibility {
  /**
   * Associate labels with form controls
   */
  static associateLabels() {
    const inputs = document.querySelectorAll('input[id], select[id], textarea[id]')
    inputs.forEach(input => {
      const label = document.querySelector(`label[for="${input.id}"]`)
      if (!label && input.parentElement?.querySelector('label')) {
        const parentLabel = input.parentElement.querySelector('label')
        if (parentLabel && !parentLabel.getAttribute('for')) {
          parentLabel.setAttribute('for', input.id)
        }
      }
    })
  }

  /**
   * Add error announcements to form fields
   */
  static enhanceErrorMessages() {
    const errorElements = document.querySelectorAll('[role="alert"]')
    errorElements.forEach(error => {
      const relatedInput = error.parentElement?.querySelector('input, select, textarea') as HTMLElement
      if (relatedInput && !relatedInput.getAttribute('aria-describedby')) {
        const errorId = `error-${relatedInput.id || Date.now()}`
        error.id = errorId
        relatedInput.setAttribute('aria-describedby', errorId)
        relatedInput.setAttribute('aria-invalid', 'true')
      }
    })
  }

  /**
   * Add password visibility toggle accessibility
   */
  static enhancePasswordFields() {
    const passwordToggles = document.querySelectorAll('[data-password-toggle]')
    passwordToggles.forEach(toggle => {
      const input = toggle.parentElement?.querySelector('input[type="password"], input[type="text"]') as HTMLInputElement
      if (input) {
        toggle.setAttribute('aria-label', 'Toggle password visibility')
        toggle.setAttribute('role', 'button')
        toggle.addEventListener('click', () => {
          const isPassword = input.type === 'password'
          input.type = isPassword ? 'text' : 'password'
          toggle.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password')
        })
      }
    })
  }
}

/**
 * Progressive enhancement utilities
 */
export class ProgressiveEnhancement {
  /**
   * Check if JavaScript is enabled and enhance accordingly
   */
  static initialize() {
    if (typeof window !== 'undefined') {
      document.documentElement.classList.add('js-enabled')
      document.documentElement.classList.remove('no-js')

      // Initialize accessibility managers
      AnnouncementManager.initialize()
      FormAccessibility.associateLabels()

      // Add motion preferences detection
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.classList.add('reduce-motion')
      }

      // Add high contrast detection
      if (window.matchMedia('(prefers-contrast: high)').matches) {
        document.documentElement.classList.add('high-contrast')
      }
    }
  }

  /**
   * Enhance forms with progressive functionality
   */
  static enhanceForms() {
    FormAccessibility.enhanceErrorMessages()
    FormAccessibility.enhancePasswordFields()
  }
}

// Auto-initialize on import
if (typeof window !== 'undefined') {
  ProgressiveEnhancement.initialize()
}

export default {
  FocusManager,
  AnnouncementManager,
  ContrastChecker,
  KeyboardNavigation,
  FormAccessibility,
  ProgressiveEnhancement
}
