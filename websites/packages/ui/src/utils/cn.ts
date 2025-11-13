/**
 * Class Name Utility (cn)
 *
 * Merges multiple class names with clsx for conditional styling.
 * Commonly used pattern in modern React applications.
 *
 * @example
 * ```tsx
 * import { cn } from '@lukhas/ui'
 *
 * <div className={cn(
 *   'glass-card',
 *   isActive && 'border-lambda-blue',
 *   'hover:scale-105'
 * )}>
 *   Content
 * </div>
 * ```
 */

import clsx, { ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs)
}
