/**
 * Enhanced Design System following Jobs' principles:
 * - "Design is not just what it looks like and feels like. Design is how it works."
 * - "Simplicity is the ultimate sophistication."
 * - "Innovation is saying 'no' to 1,000 things."
 */
export class EnhancedDesignSystem {
  private static instance: EnhancedDesignSystem;

  // Extended Jobs-inspired color system
  private readonly colors = {
    // Primary palette
    primary: {
      main: '#000000',
      light: '#1D1D1F',
      dark: '#000000'
    },
    // Secondary palette for depth
    secondary: {
      main: '#86868B',
      light: '#F5F5F7',
      dark: '#424245'
    },
    // Accent colors for important actions
    accent: {
      blue: '#0066CC',
      green: '#34C759',
      red: '#FF3B30'
    },
    // Background system
    background: {
      primary: '#FFFFFF',
      secondary: '#F5F5F7',
      elevated: '#FFFFFF'
    }
  };

  // Enhanced spacing system
  private readonly spacing = {
    base: 8,
    get xxxs() { return this.base * 0.25 }, // 2px
    get xxs() { return this.base * 0.5 },   // 4px
    get xs() { return this.base },          // 8px
    get sm() { return this.base * 1.5 },    // 12px
    get md() { return this.base * 2 },      // 16px
    get lg() { return this.base * 3 },      // 24px
    get xl() { return this.base * 4 },      // 32px
    get xxl() { return this.base * 6 },     // 48px
    get xxxl() { return this.base * 8 }     // 64px
  };

  // Jobs-inspired typography system
  private readonly typography = {
    fonts: {
      primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      monospace: 'SF Mono, Monaco, Consolas, monospace'
    },
    weights: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    },
    styles: {
      display: {
        size: '44px',
        weight: 700,
        height: 1.2
      },
      title1: {
        size: '28px',
        weight: 600,
        height: 1.3
      },
      title2: {
        size: '22px',
        weight: 600,
        height: 1.3
      },
      body: {
        size: '17px',
        weight: 400,
        height: 1.5
      },
      caption: {
        size: '12px',
        weight: 400,
        height: 1.4
      }
    }
  };

  // Animation system
  private readonly animation = {
    durations: {
      fast: '200ms',
      normal: '300ms',
      slow: '500ms'
    },
    curves: {
      standard: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
      decelerate: 'cubic-bezier(0.0, 0.0, 0.2, 1)',
      accelerate: 'cubic-bezier(0.4, 0.0, 1, 1)'
    }
  };

  // Elevation system
  private readonly elevation = {
    none: 'none',
    low: '0 1px 3px rgba(0,0,0,0.12)',
    medium: '0 4px 6px rgba(0,0,0,0.12)',
    high: '0 8px 12px rgba(0,0,0,0.12)'
  };

  private constructor() {}

  static getInstance(): EnhancedDesignSystem {
    if (!this.instance) {
      this.instance = new EnhancedDesignSystem();
    }
    return this.instance;
  }

  /**
   * Jobs-inspired component styling
   */
  styleComponent(
    element: HTMLElement, 
    {
      variant = 'primary',
      importance = 'normal',
      state = 'default'
    }: {
      variant?: 'primary' | 'secondary' | 'accent';
      importance?: 'high' | 'normal' | 'low';
      state?: 'default' | 'hover' | 'active' | 'disabled';
    }
  ): void {
    // Base styles
    element.style.fontFamily = this.typography.fonts.primary;
    element.style.fontSize = this.typography.styles.body.size;
    element.style.lineHeight = this.typography.styles.body.height.toString();
    element.style.transition = `all ${this.animation.durations.normal} ${this.animation.curves.standard}`;

    // Variant styles
    switch (variant) {
      case 'primary':
        element.style.backgroundColor = this.colors.primary.main;
        element.style.color = this.colors.background.primary;
        break;
      case 'secondary':
        element.style.backgroundColor = this.colors.secondary.main;
        element.style.color = this.colors.primary.main;
        break;
      case 'accent':
        element.style.backgroundColor = this.colors.accent.blue;
        element.style.color = this.colors.background.primary;
        break;
    }

    // Importance styles
    switch (importance) {
      case 'high':
        element.style.boxShadow = this.elevation.high;
        element.style.fontWeight = this.typography.weights.bold.toString();
        break;
      case 'normal':
        element.style.boxShadow = this.elevation.medium;
        element.style.fontWeight = this.typography.weights.medium.toString();
        break;
      case 'low':
        element.style.boxShadow = this.elevation.low;
        element.style.fontWeight = this.typography.weights.regular.toString();
        break;
    }

    // State styles
    switch (state) {
      case 'hover':
        element.style.transform = 'scale(1.02)';
        element.style.boxShadow = this.elevation.high;
        break;
      case 'active':
        element.style.transform = 'scale(0.98)';
        element.style.boxShadow = this.elevation.low;
        break;
      case 'disabled':
        element.style.opacity = '0.5';
        element.style.boxShadow = this.elevation.none;
        element.style.cursor = 'not-allowed';
        break;
    }
  }

  /**
   * Jobs-inspired layout system
   */
  createLayout(container: HTMLElement, type: 'stack' | 'grid' | 'flow'): void {
    switch (type) {
      case 'stack':
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = `${this.spacing.md}px`;
        break;
      case 'grid':
        container.style.display = 'grid';
        container.style.gap = `${this.spacing.md}px`;
        container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(200px, 1fr))';
        break;
      case 'flow':
        container.style.display = 'flex';
        container.style.flexWrap = 'wrap';
        container.style.gap = `${this.spacing.md}px`;
        break;
    }
  }

  getTheme(): typeof EnhancedDesignSystem.prototype {
    return {
      colors: this.colors,
      spacing: this.spacing,
      typography: this.typography,
      animation: this.animation,
      elevation: this.elevation
    };
  }
}
