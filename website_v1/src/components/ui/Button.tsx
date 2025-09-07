import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  href?: string;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, href, ...props }, ref) => {
    const baseClasses = [
      'inline-flex items-center justify-center font-medium transition-all duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed'
    ];

    const variants = {
      primary: [
        'bg-accent text-white hover:bg-[#3A7BFF]',
        'hover:transform hover:-translate-y-0.5',
        'active:translate-y-0'
      ],
      secondary: [
        'bg-transparent text-[var(--text-primary)] border border-[var(--border)]',
        'hover:bg-[var(--surface)] hover:border-accent'
      ],
      ghost: [
        'bg-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
        'hover:bg-[var(--surface)]'
      ]
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm rounded-sm',
      md: 'px-6 py-3 text-body rounded-sm',
      lg: 'px-8 py-4 text-lg rounded-md'
    };

    const classes = cn(
      baseClasses,
      variants[variant],
      sizes[size],
      className
    );

    if (href) {
      return (
        <a
          href={href}
          className={classes}
          {...(props as React.AnchorHTMLAttributes<HTMLAnchorElement>)}
        >
          {children}
        </a>
      );
    }

    return (
      <button
        className={classes}
        ref={ref}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';