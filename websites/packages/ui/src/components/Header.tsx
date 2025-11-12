import { ReactNode, forwardRef } from 'react'
import { cn } from '../utils'
import '../styles/index.css'

export interface HeaderProps extends React.HTMLAttributes<HTMLElement> {
  /**
   * Header content
   */
  children: ReactNode
  /**
   * Make header sticky
   * @default true
   */
  sticky?: boolean
  /**
   * Enable glassmorphism effect
   * @default true
   */
  glass?: boolean
  /**
   * Enable breathing animation
   * @default false
   */
  breathe?: boolean
  /**
   * Domain-specific branding color
   */
  domain?: 'id' | 'com' | 'us' | 'none'
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Header - LUKHAS design system header component
 *
 * Features:
 * - Glassmorphism backdrop blur
 * - Sticky positioning
 * - Domain-specific accent colors
 * - Consciousness-inspired animations
 *
 * @example
 * ```tsx
 * <Header domain="id" sticky glass>
 *   <HeaderLogo>LUKHAS</HeaderLogo>
 *   <HeaderNav>
 *     <HeaderNavLink href="/login">Sign In</HeaderNavLink>
 *   </HeaderNav>
 * </Header>
 * ```
 */
export const Header = forwardRef<HTMLElement, HeaderProps>(
  (
    {
      children,
      sticky = true,
      glass = true,
      breathe = false,
      domain = 'none',
      className,
      ...props
    },
    ref
  ) => {
    return (
      <header
        ref={ref}
        className={cn(
          // Base styles
          'w-full border-b transition-all duration-300',

          // Sticky positioning
          sticky && 'sticky top-0 z-fixed',

          // Glassmorphism
          glass && 'bg-glass backdrop-blur-glass border-glass-border',
          !glass && 'bg-deep-space border-border',

          // Domain accents (subtle bottom border glow)
          domain === 'id' && 'border-b-domain-id-purple/30',
          domain === 'com' && 'border-b-domain-com-trust-blue/30',
          domain === 'us' && 'border-b-domain-us-institutional/30',

          // Breathing animation
          breathe && 'animate-breathe-subtle',

          className
        )}
        {...props}
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {children}
          </div>
        </div>
      </header>
    )
  }
)

Header.displayName = 'Header'

/**
 * HeaderLogo - Logo/brand component for header
 */
export interface HeaderLogoProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  /**
   * Link URL for logo
   */
  href?: string
  className?: string
}

export const HeaderLogo = forwardRef<HTMLDivElement, HeaderLogoProps>(
  ({ children, href = '/', className, ...props }, ref) => {
    const content = (
      <span className="text-2xl font-thin uppercase tracking-thin-capitals text-text-primary">
        {children}
      </span>
    )

    if (href) {
      return (
        <a
          href={href}
          className={cn(
            'flex items-center transition-opacity hover:opacity-80',
            className
          )}
        >
          {content}
        </a>
      )
    }

    return (
      <div ref={ref} className={cn('flex items-center', className)} {...props}>
        {content}
      </div>
    )
  }
)

HeaderLogo.displayName = 'HeaderLogo'

/**
 * HeaderNav - Navigation container for header
 */
export interface HeaderNavProps extends React.HTMLAttributes<HTMLElement> {
  children: ReactNode
  className?: string
}

export const HeaderNav = forwardRef<HTMLElement, HeaderNavProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <nav
        ref={ref}
        className={cn('flex items-center gap-6', className)}
        {...props}
      >
        {children}
      </nav>
    )
  }
)

HeaderNav.displayName = 'HeaderNav'

/**
 * HeaderNavLink - Navigation link for header
 */
export interface HeaderNavLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  children: ReactNode
  /**
   * Active state
   * @default false
   */
  active?: boolean
  className?: string
}

export const HeaderNavLink = forwardRef<HTMLAnchorElement, HeaderNavLinkProps>(
  ({ children, active = false, className, ...props }, ref) => {
    return (
      <a
        ref={ref}
        className={cn(
          'text-sm font-light uppercase tracking-logo transition-colors',
          active
            ? 'text-lambda-blue'
            : 'text-text-secondary hover:text-text-primary',
          className
        )}
        {...props}
      >
        {children}
      </a>
    )
  }
)

HeaderNavLink.displayName = 'HeaderNavLink'

/**
 * HeaderActions - Action buttons container for header
 */
export interface HeaderActionsProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
}

export const HeaderActions = forwardRef<HTMLDivElement, HeaderActionsProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-center gap-3', className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

HeaderActions.displayName = 'HeaderActions'
