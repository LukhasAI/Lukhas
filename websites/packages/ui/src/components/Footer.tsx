import { ReactNode, forwardRef } from 'react'
import { cn } from '../utils'
import '../styles/index.css'

export interface FooterProps extends React.HTMLAttributes<HTMLElement> {
  /**
   * Footer content
   */
  children: ReactNode
  /**
   * Enable glassmorphism effect
   * @default false
   */
  glass?: boolean
  /**
   * Show ecosystem navigation
   * @default true
   */
  showEcosystem?: boolean
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Footer - LUKHAS design system footer component
 *
 * Features:
 * - Unified ecosystem navigation
 * - Constellation Framework branding
 * - Optional glassmorphism
 * - Responsive layout
 *
 * @example
 * ```tsx
 * <Footer showEcosystem>
 *   <FooterSection title="Product">
 *     <FooterLink href="/features">Features</FooterLink>
 *   </FooterSection>
 * </Footer>
 * ```
 */
export const Footer = forwardRef<HTMLElement, FooterProps>(
  (
    {
      children,
      glass = false,
      showEcosystem = true,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <footer
        ref={ref}
        className={cn(
          'w-full border-t mt-auto',
          glass && 'bg-glass backdrop-blur-glass border-glass-border',
          !glass && 'bg-deep-space border-border',
          className
        )}
        {...props}
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {showEcosystem && (
            <div className="mb-12 pb-8 border-b border-border">
              <FooterEcosystemNav />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
            {children}
          </div>

          <FooterBottom />
        </div>
      </footer>
    )
  }
)

Footer.displayName = 'Footer'

/**
 * FooterEcosystemNav - Navigation across LUKHAS domains
 */
export const FooterEcosystemNav = () => {
  const domains = [
    {
      name: 'lukhas.id',
      description: 'Identity & Authentication',
      color: 'domain-id-purple',
      href: 'https://lukhas.id',
    },
    {
      name: 'lukhas.com',
      description: 'Platform & Products',
      color: 'domain-com-trust-blue',
      href: 'https://lukhas.com',
    },
    {
      name: 'lukhas.us',
      description: 'Compliance & Governance',
      color: 'domain-us-institutional',
      href: 'https://lukhas.us',
    },
  ]

  return (
    <div>
      <h3 className="text-sm font-light uppercase tracking-logo text-text-secondary mb-4">
        LUKHAS Ecosystem
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {domains.map((domain) => (
          <a
            key={domain.name}
            href={domain.href}
            className={cn(
              'p-4 rounded-lg border transition-all duration-300',
              'hover:-translate-y-1 hover:shadow-md',
              `border-${domain.color}/30 hover:border-${domain.color}`
            )}
          >
            <div className={`text-base font-light uppercase tracking-logo text-${domain.color} mb-1`}>
              {domain.name}
            </div>
            <div className="text-xs text-text-secondary">
              {domain.description}
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}

/**
 * FooterSection - Footer column section
 */
export interface FooterSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  children: ReactNode
  className?: string
}

export const FooterSection = forwardRef<HTMLDivElement, FooterSectionProps>(
  ({ title, children, className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('flex flex-col gap-3', className)} {...props}>
        <h4 className="text-sm font-light uppercase tracking-logo text-text-primary mb-2">
          {title}
        </h4>
        <div className="flex flex-col gap-2">
          {children}
        </div>
      </div>
    )
  }
)

FooterSection.displayName = 'FooterSection'

/**
 * FooterLink - Footer navigation link
 */
export interface FooterLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  children: ReactNode
  className?: string
}

export const FooterLink = forwardRef<HTMLAnchorElement, FooterLinkProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <a
        ref={ref}
        className={cn(
          'text-sm text-text-secondary hover:text-lambda-blue transition-colors',
          className
        )}
        {...props}
      >
        {children}
      </a>
    )
  }
)

FooterLink.displayName = 'FooterLink'

/**
 * FooterBottom - Footer bottom with copyright and legal
 */
export const FooterBottom = () => {
  const currentYear = new Date().getFullYear()

  return (
    <div className="pt-8 border-t border-border flex flex-col sm:flex-row justify-between items-center gap-4">
      <div className="text-xs text-text-secondary">
        © {currentYear} LUKHAS AI. All rights reserved.
      </div>

      <div className="flex items-center gap-4">
        <a
          href="/privacy"
          className="text-xs text-text-secondary hover:text-lambda-blue transition-colors"
        >
          Privacy Policy
        </a>
        <a
          href="/terms"
          className="text-xs text-text-secondary hover:text-lambda-blue transition-colors"
        >
          Terms of Service
        </a>
        <a
          href="/security"
          className="text-xs text-text-secondary hover:text-lambda-blue transition-colors"
        >
          Security
        </a>
      </div>
    </div>
  )
}

FooterBottom.displayName = 'FooterBottom'
