'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

type Theme = 'light' | 'dark' | 'system'

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

interface ThemeProviderState {
  theme: Theme
  setTheme: (theme: Theme) => void
  resolvedTheme: 'light' | 'dark'
}

const ThemeProviderContext = createContext<ThemeProviderState | undefined>(undefined)

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'lukhas-theme',
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(defaultTheme)
  const [mounted, setMounted] = useState(false)

  // Determine the resolved theme based on system preference
  const getResolvedTheme = (): 'light' | 'dark' => {
    if (theme === 'system') {
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      return 'dark'
    }
    return theme as 'light' | 'dark'
  }

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>(getResolvedTheme())

  useEffect(() => {
    setMounted(true)
    const stored = localStorage.getItem(storageKey) as Theme | null
    if (stored) {
      setTheme(stored)
    }
  }, [storageKey])

  useEffect(() => {
    if (!mounted) return

    const root = window.document.documentElement

    // Remove previous theme classes
    root.classList.remove('light', 'dark')

    const resolved = getResolvedTheme()
    setResolvedTheme(resolved)

    // Add current theme class
    root.classList.add(resolved)

    // Update CSS variables for smooth transitions
    if (resolved === 'light') {
      root.style.setProperty('--bg-primary', '255, 255, 255')
      root.style.setProperty('--bg-secondary', '250, 250, 250')
      root.style.setProperty('--bg-tertiary', '245, 245, 245')
      root.style.setProperty('--text-primary', '0, 0, 0')
      root.style.setProperty('--text-secondary', '64, 64, 64')
      root.style.setProperty('--text-tertiary', '128, 128, 128')
      root.style.setProperty('--glass', 'rgba(0, 0, 0, 0.03)')
      root.style.setProperty('--glass-border', 'rgba(0, 0, 0, 0.08)')
      root.style.setProperty('--trinity-identity', '107, 70, 193')
      root.style.setProperty('--trinity-consciousness', '168, 85, 247')
      root.style.setProperty('--trinity-guardian', '34, 197, 94')
      root.style.setProperty('--accent-gold', '251, 191, 36')
    } else {
      root.style.setProperty('--bg-primary', '0, 0, 0')
      root.style.setProperty('--bg-secondary', '17, 17, 17')
      root.style.setProperty('--bg-tertiary', '38, 38, 38')
      root.style.setProperty('--text-primary', '255, 255, 255')
      root.style.setProperty('--text-secondary', '179, 179, 179')
      root.style.setProperty('--text-tertiary', '128, 128, 128')
      root.style.setProperty('--glass', 'rgba(255, 255, 255, 0.05)')
      root.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.1)')
      root.style.setProperty('--trinity-identity', '107, 70, 193')
      root.style.setProperty('--trinity-consciousness', '168, 85, 247')
      root.style.setProperty('--trinity-guardian', '34, 197, 94')
      root.style.setProperty('--accent-gold', '251, 191, 36')
    }

    // Listen for system theme changes
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = () => {
        const newResolved = mediaQuery.matches ? 'dark' : 'light'
        setResolvedTheme(newResolved)
        root.classList.remove('light', 'dark')
        root.classList.add(newResolved)
      }
      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    }
  }, [theme, mounted])

  const value = {
    theme,
    setTheme: (newTheme: Theme) => {
      localStorage.setItem(storageKey, newTheme)
      setTheme(newTheme)
    },
    resolvedTheme,
  }

  // Prevent flash of unstyled content
  if (!mounted) {
    return null
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
      <ThemeTransition />
    </ThemeProviderContext.Provider>
  )
}

// Smooth theme transition overlay
function ThemeTransition() {
  const [transitioning, setTransitioning] = useState(false)
  const context = useContext(ThemeProviderContext)

  useEffect(() => {
    setTransitioning(true)
    const timer = setTimeout(() => setTransitioning(false), 300)
    return () => clearTimeout(timer)
  }, [context?.resolvedTheme])

  return (
    <AnimatePresence>
      {transitioning && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 pointer-events-none z-[100]"
          style={{
            background: 'radial-gradient(circle at center, transparent 0%, rgba(107, 70, 193, 0.05) 100%)',
          }}
        />
      )}
    </AnimatePresence>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }

  return context
}