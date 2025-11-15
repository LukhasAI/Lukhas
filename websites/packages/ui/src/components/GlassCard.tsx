import { ReactNode, forwardRef } from 'react'
import { cn } from '../utils'
import '../styles/index.css'

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Card content
   */
  children: ReactNode
  /**
   * Card variant
   * @default 'default'
   */
  variant?: 'default' | 'elevated' | 'interactive'
  /**
   * Domain-specific accent border
   */
  domainAccent?: 'id' | 'com' | 'us' | 'none'
  /**
   * Enable hover animation
   * @default true
   */
  hoverable?: boolean
  /**
   * Enable breathing animation
   * @default false
   */
  breathe?: boolean
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * GlassCard - Glassmorphism card component
 *
 * Features:
 * - Backdrop blur glassmorphism effect
 * - Domain-specific accent borders
 * - Interactive hover states
 * - Consciousness-inspired animations
 *
 * @example
 * ```tsx
 * <GlassCard domainAccent="id" hoverable>
 *   <h3>Identity Management</h3>
 *   <p>Secure authentication with WebAuthn</p>
 * </GlassCard>
 * ```
 */
export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  (
    {
      children,
      variant = 'default',
      domainAccent = 'none',
      hoverable = true,
      breathe = false,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base styles
          'rounded-glass p-6 transition-all duration-300',
          'border border-glass-border backdrop-blur-glass',

          // Variants
          variant === 'default' && 'bg-glass',
          variant === 'elevated' && 'bg-card-elevated shadow-lg',
          variant === 'interactive' && 'bg-glass cursor-pointer',

          // Hoverable
          hoverable && 'hover:-translate-y-1 hover:border-border-bright hover:shadow-lg',

          // Domain accents
          domainAccent === 'id' && 'border-l-4 border-l-domain-id-purple',
          domainAccent === 'com' && 'border-l-4 border-l-domain-com-trust-blue',
          domainAccent === 'us' && 'border-l-4 border-l-domain-us-institutional',

          // Breathing animation
          breathe && 'animate-breathe-subtle',

          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

GlassCard.displayName = 'GlassCard'

/**
 * GlassCardHeader - Card header with title
 */
export interface GlassCardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
}

export const GlassCardHeader = forwardRef<HTMLDivElement, GlassCardHeaderProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('mb-4', className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

GlassCardHeader.displayName = 'GlassCardHeader'

/**
 * GlassCardTitle - Card title with LUKHAS typography
 */
export interface GlassCardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: ReactNode
  className?: string
}

export const GlassCardTitle = forwardRef<HTMLHeadingElement, GlassCardTitleProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={cn(
          'text-2xl font-light uppercase tracking-logo text-lambda-blue',
          className
        )}
        {...props}
      >
        {children}
      </h3>
    )
  }
)

GlassCardTitle.displayName = 'GlassCardTitle'

/**
 * GlassCardDescription - Card description text
 */
export interface GlassCardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: ReactNode
  className?: string
}

export const GlassCardDescription = forwardRef<HTMLParagraphElement, GlassCardDescriptionProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn('text-base text-text-secondary leading-normal', className)}
        {...props}
      >
        {children}
      </p>
    )
  }
)

GlassCardDescription.displayName = 'GlassCardDescription'

/**
 * GlassCardContent - Card content area
 */
export interface GlassCardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
}

export const GlassCardContent = forwardRef<HTMLDivElement, GlassCardContentProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('text-text-primary', className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

GlassCardContent.displayName = 'GlassCardContent'

/**
 * GlassCardFooter - Card footer with actions
 */
export interface GlassCardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
}

export const GlassCardFooter = forwardRef<HTMLDivElement, GlassCardFooterProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('mt-6 flex items-center gap-2', className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

GlassCardFooter.displayName = 'GlassCardFooter'
