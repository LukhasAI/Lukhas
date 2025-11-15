import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '../utils'
import '../styles/index.css'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button variant
   * @default 'default'
   */
  variant?: 'default' | 'primary' | 'secondary' | 'ghost' | 'outline' | 'destructive'
  /**
   * Button size
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg' | 'icon'
  /**
   * Enable glow effect on hover
   * @default false
   */
  glow?: boolean
  /**
   * Full width button
   * @default false
   */
  fullWidth?: boolean
  /**
   * Loading state
   * @default false
   */
  isLoading?: boolean
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Button - LUKHAS design system button component
 *
 * Features:
 * - Multiple variants (primary, secondary, ghost, outline)
 * - Size variants (sm, md, lg, icon)
 * - Optional glow effects
 * - Loading states
 * - Glassmorphism styling
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="lg" glow>
 *   Sign In with Passkey
 * </Button>
 * ```
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'default',
      size = 'md',
      glow = false,
      fullWidth = false,
      isLoading = false,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center',
          'font-display font-light uppercase tracking-logo',
          'transition-all duration-300 ease-lukhas',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lambda-blue',
          'disabled:pointer-events-none disabled:opacity-50',

          // Variants
          variant === 'default' &&
            'bg-glass backdrop-blur-glass border border-glass-border text-text-primary hover:border-border-bright hover:-translate-y-0.5',
          variant === 'primary' &&
            'bg-lambda-blue text-deep-space hover:bg-quantum-green hover:-translate-y-0.5',
          variant === 'secondary' &&
            'bg-card-elevated border border-border text-text-primary hover:bg-card-bg hover:border-border-bright',
          variant === 'ghost' &&
            'text-text-primary hover:bg-glass hover:text-lambda-blue',
          variant === 'outline' &&
            'border border-lambda-blue text-lambda-blue hover:bg-lambda-blue hover:text-deep-space',
          variant === 'destructive' &&
            'bg-danger text-white hover:bg-red-700',

          // Sizes
          size === 'sm' && 'h-9 px-4 text-xs rounded-md',
          size === 'md' && 'h-11 px-6 text-sm rounded-lg',
          size === 'lg' && 'h-14 px-8 text-base rounded-xl',
          size === 'icon' && 'h-11 w-11 rounded-lg',

          // Glow effect
          glow && variant === 'primary' && 'hover:shadow-glow-blue',
          glow && variant === 'outline' && 'hover:shadow-glow-blue',

          // Full width
          fullWidth && 'w-full',

          className
        )}
        {...props}
      >
        {isLoading && (
          <svg
            className="mr-2 h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

/**
 * ButtonGroup - Group multiple buttons together
 */
export interface ButtonGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  className?: string
}

export const ButtonGroup = forwardRef<HTMLDivElement, ButtonGroupProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex gap-2', className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

ButtonGroup.displayName = 'ButtonGroup'
