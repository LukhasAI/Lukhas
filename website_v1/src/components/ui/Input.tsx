import React from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-small text-[var(--text-secondary)] mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--text-secondary)]">
              {icon}
            </div>
          )}
          <input
            className={cn(
              'w-full px-4 py-3 rounded-sm',
              'bg-[var(--surface)] border border-[var(--border)]',
              'text-[var(--text-primary)] placeholder:text-[var(--text-secondary)]',
              'transition-all duration-200',
              'focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              icon && 'pl-10',
              error && 'border-danger focus:border-danger focus:ring-danger/20',
              className
            )}
            ref={ref}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1 text-small text-danger">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';