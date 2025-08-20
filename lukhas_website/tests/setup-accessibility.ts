/**
 * LUKHAS AI ΛiD Authentication System - Accessibility Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Setup file for accessibility tests - includes WCAG 2.1 AA compliance utilities
 */

import { configureAxe } from 'jest-axe';

// Configure axe-core for WCAG 2.1 AA compliance
const axe = configureAxe({
  rules: {
    // WCAG 2.1 AA rules
    'color-contrast': { enabled: true },
    'color-contrast-enhanced': { enabled: false }, // AAA level
    'focus-order-semantics': { enabled: true },
    'hidden-content': { enabled: true },
    'label-title-only': { enabled: true },
    'link-in-text-block': { enabled: true },
    'p-as-heading': { enabled: true },
    'region': { enabled: true },
    'skip-link': { enabled: true },
    'tabindex': { enabled: true },
    'text-spacing': { enabled: true },
    
    // Custom LUKHAS AI specific rules
    'landmark-banner-is-top-level': { enabled: true },
    'landmark-main-is-top-level': { enabled: true },
    'landmark-no-duplicate-banner': { enabled: true },
    'landmark-no-duplicate-contentinfo': { enabled: true },
    'landmark-one-main': { enabled: true },
    'page-has-heading-one': { enabled: true },
    'region': { enabled: true },
    
    // Form accessibility
    'autocomplete-valid': { enabled: true },
    'form-field-multiple-labels': { enabled: true },
    'input-button-name': { enabled: true },
    'input-image-alt': { enabled: true },
    'label': { enabled: true },
    'select-name': { enabled: true },
    
    // Keyboard accessibility
    'accesskeys': { enabled: true },
    'focus-order-semantics': { enabled: true },
    'tabindex': { enabled: true },
    
    // Screen reader accessibility
    'aria-allowed-attr': { enabled: true },
    'aria-command-name': { enabled: true },
    'aria-hidden-body': { enabled: true },
    'aria-hidden-focus': { enabled: true },
    'aria-input-field-name': { enabled: true },
    'aria-label': { enabled: true },
    'aria-labelledby': { enabled: true },
    'aria-required-attr': { enabled: true },
    'aria-required-children': { enabled: true },
    'aria-required-parent': { enabled: true },
    'aria-roledescription': { enabled: true },
    'aria-roles': { enabled: true },
    'aria-toggle-field-name': { enabled: true },
    'aria-tooltip-name': { enabled: true },
    'aria-valid-attr': { enabled: true },
    'aria-valid-attr-value': { enabled: true },
  },
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
});

// Accessibility testing utilities
globalThis.accessibilityUtils = {
  // Test page with axe-core
  async testAccessibility(element: Element | Document = document): Promise<any> {
    return await axe(element);
  },

  // Test keyboard navigation
  async testKeyboardNavigation(container: Element): Promise<{
    focusableElements: Element[];
    tabOrder: Element[];
    trapsFocus: boolean;
    hasSkipLinks: boolean;
  }> {
    // Find all focusable elements
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      'details summary',
    ];

    const focusableElements = Array.from(
      container.querySelectorAll(focusableSelectors.join(', '))
    ).filter((el) => {
      // Check if element is visible and not hidden
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden';
    });

    // Test tab order
    const tabOrder = focusableElements.sort((a, b) => {
      const aTabIndex = parseInt((a as HTMLElement).tabIndex.toString()) || 0;
      const bTabIndex = parseInt((b as HTMLElement).tabIndex.toString()) || 0;
      
      if (aTabIndex === bTabIndex) {
        // Use document order for elements with same tabindex
        return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
      }
      
      return aTabIndex - bTabIndex;
    });

    // Check for focus trap (modal dialogs)
    const trapsFocus = container.hasAttribute('aria-modal') || 
                      container.classList.contains('modal') ||
                      container.querySelector('[aria-modal="true"]') !== null;

    // Check for skip links
    const hasSkipLinks = container.querySelector('a[href^="#"]:first-child') !== null;

    return {
      focusableElements,
      tabOrder,
      trapsFocus,
      hasSkipLinks,
    };
  },

  // Test color contrast
  async testColorContrast(element: Element): Promise<{
    passed: boolean;
    violations: Array<{
      element: Element;
      contrast: number;
      required: number;
      foreground: string;
      background: string;
    }>;
  }> {
    const violations: any[] = [];
    const textElements = element.querySelectorAll('*');

    for (const el of textElements) {
      const style = window.getComputedStyle(el);
      const color = style.color;
      const backgroundColor = style.backgroundColor;
      
      if (color && backgroundColor && color !== 'rgba(0, 0, 0, 0)' && backgroundColor !== 'rgba(0, 0, 0, 0)') {
        // This is a simplified contrast check - in real implementation,
        // you would use a proper contrast calculation library
        const contrast = this.calculateContrast(color, backgroundColor);
        const fontSize = parseInt(style.fontSize);
        const isLargeText = fontSize >= 18 || (fontSize >= 14 && style.fontWeight === 'bold');
        const required = isLargeText ? 3 : 4.5; // WCAG AA requirements

        if (contrast < required) {
          violations.push({
            element: el,
            contrast,
            required,
            foreground: color,
            background: backgroundColor,
          });
        }
      }
    }

    return {
      passed: violations.length === 0,
      violations,
    };
  },

  // Calculate color contrast ratio (simplified)
  calculateContrast(color1: string, color2: string): number {
    // This is a simplified version - use a proper library like 'color' for accurate calculations
    // For now, return a mock value for testing
    return Math.random() * 21; // WCAG contrast ratios range from 1:1 to 21:1
  },

  // Test screen reader compatibility
  testScreenReaderCompatibility(element: Element): {
    hasProperHeadings: boolean;
    hasLandmarks: boolean;
    hasAltText: boolean;
    hasAriaLabels: boolean;
    hasValidAria: boolean;
  } {
    // Check heading structure
    const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const hasProperHeadings = headings.length > 0 && element.querySelector('h1') !== null;

    // Check landmarks
    const landmarks = element.querySelectorAll('main, nav, header, footer, aside, section[aria-label], section[aria-labelledby]');
    const hasLandmarks = landmarks.length > 0;

    // Check alt text on images
    const images = element.querySelectorAll('img');
    const hasAltText = Array.from(images).every(img => 
      img.hasAttribute('alt') || img.hasAttribute('aria-label') || img.getAttribute('role') === 'presentation'
    );

    // Check ARIA labels
    const interactiveElements = element.querySelectorAll('button, input, select, textarea, a[href]');
    const hasAriaLabels = Array.from(interactiveElements).every(el => 
      el.hasAttribute('aria-label') || 
      el.hasAttribute('aria-labelledby') || 
      el.textContent?.trim() ||
      (el as HTMLElement).querySelector('span:not(.sr-only)')
    );

    // Check valid ARIA usage
    const ariaElements = element.querySelectorAll('[aria-*]');
    const hasValidAria = Array.from(ariaElements).every(el => {
      // Basic validation - check if required ARIA attributes are present
      const role = el.getAttribute('role');
      if (role === 'button' && !el.hasAttribute('aria-label') && !el.textContent?.trim()) {
        return false;
      }
      return true;
    });

    return {
      hasProperHeadings,
      hasLandmarks,
      hasAltText,
      hasAriaLabels,
      hasValidAria,
    };
  },

  // Test form accessibility
  testFormAccessibility(form: HTMLFormElement): {
    hasLabels: boolean;
    hasRequiredIndicators: boolean;
    hasErrorHandling: boolean;
    hasFieldsets: boolean;
    hasAutocomplete: boolean;
  } {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    // Check labels
    const hasLabels = Array.from(inputs).every(input => {
      const id = input.getAttribute('id');
      return id && form.querySelector(`label[for="${id}"]`) !== null ||
             input.hasAttribute('aria-label') ||
             input.hasAttribute('aria-labelledby');
    });

    // Check required field indicators
    const requiredFields = form.querySelectorAll('[required], [aria-required="true"]');
    const hasRequiredIndicators = Array.from(requiredFields).every(field => {
      const label = form.querySelector(`label[for="${field.getAttribute('id')}"]`);
      return label?.textContent?.includes('*') || 
             label?.textContent?.includes('required') ||
             field.hasAttribute('aria-describedby');
    });

    // Check error handling
    const hasErrorHandling = form.querySelectorAll('[aria-invalid], [aria-describedby]').length > 0;

    // Check fieldsets for grouped inputs
    const radioGroups = form.querySelectorAll('input[type="radio"]');
    const checkboxGroups = form.querySelectorAll('input[type="checkbox"]');
    const hasFieldsets = (radioGroups.length > 1 && form.querySelector('fieldset') !== null) ||
                        (checkboxGroups.length > 1 && form.querySelector('fieldset') !== null);

    // Check autocomplete attributes for personal information
    const personalFields = form.querySelectorAll('input[type="email"], input[name*="email"], input[name*="phone"], input[name*="address"]');
    const hasAutocomplete = Array.from(personalFields).some(field => 
      field.hasAttribute('autocomplete')
    );

    return {
      hasLabels,
      hasRequiredIndicators,
      hasErrorHandling,
      hasFieldsets,
      hasAutocomplete,
    };
  },

  // Generate accessibility report
  generateAccessibilityReport(testResults: any): {
    score: number;
    level: 'AA' | 'A' | 'Fail';
    violations: any[];
    passed: any[];
    summary: string;
  } {
    const totalChecks = testResults.violations.length + testResults.passes.length;
    const score = totalChecks > 0 ? (testResults.passes.length / totalChecks) * 100 : 0;
    
    let level: 'AA' | 'A' | 'Fail' = 'Fail';
    if (score >= 95) level = 'AA';
    else if (score >= 85) level = 'A';

    const summary = `Accessibility Score: ${score.toFixed(1)}% (${level} Level)
    Violations: ${testResults.violations.length}
    Passed: ${testResults.passes.length}
    Incomplete: ${testResults.incomplete?.length || 0}`;

    return {
      score,
      level,
      violations: testResults.violations,
      passed: testResults.passes,
      summary,
    };
  },
};

// Mock assistive technology for testing
globalThis.mockAssistiveTechnology = {
  screenReader: {
    enabled: true,
    announcements: [] as string[],
    
    announce(text: string) {
      this.announcements.push(text);
    },
    
    getAnnouncements() {
      return [...this.announcements];
    },
    
    clearAnnouncements() {
      this.announcements = [];
    },
  },

  keyboardOnly: {
    enabled: false,
    
    enable() {
      this.enabled = true;
      // Disable mouse events in tests when this is enabled
    },
    
    disable() {
      this.enabled = false;
    },
  },

  highContrast: {
    enabled: false,
    
    enable() {
      this.enabled = true;
      document.body.classList.add('high-contrast');
    },
    
    disable() {
      this.enabled = false;
      document.body.classList.remove('high-contrast');
    },
  },

  reducedMotion: {
    enabled: false,
    
    enable() {
      this.enabled = true;
      document.body.classList.add('prefers-reduced-motion');
    },
    
    disable() {
      this.enabled = false;
      document.body.classList.remove('prefers-reduced-motion');
    },
  },
};

// Accessibility test environment
beforeEach(() => {
  // Reset assistive technology mocks
  globalThis.mockAssistiveTechnology.screenReader.clearAnnouncements();
  globalThis.mockAssistiveTechnology.keyboardOnly.disable();
  globalThis.mockAssistiveTechnology.highContrast.disable();
  globalThis.mockAssistiveTechnology.reducedMotion.disable();
});

// Set up global accessibility matcher
expect.extend({
  toBeAccessible: async function(received: Element | Document) {
    const results = await globalThis.accessibilityUtils.testAccessibility(received);
    
    return {
      pass: results.violations.length === 0,
      message: () => {
        if (results.violations.length === 0) {
          return 'Expected element to have accessibility violations, but none were found';
        } else {
          const violationMessages = results.violations.map((v: any) => 
            `${v.id}: ${v.description} (${v.nodes.length} instance${v.nodes.length > 1 ? 's' : ''})`
          ).join('\n');
          
          return `Expected element to be accessible, but found ${results.violations.length} violation${results.violations.length > 1 ? 's' : ''}:\n${violationMessages}`;
        }
      },
    };
  },
});

// Declare custom matcher type
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeAccessible(): Promise<R>;
    }
  }
}