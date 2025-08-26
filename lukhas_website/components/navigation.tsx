'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, Search, Command, Sun, Moon, Monitor, Globe } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from './theme-provider'
import { useTranslation, languages, type Language } from '@/lib/i18n'

export function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [langMenuOpen, setLangMenuOpen] = useState(false)
  const [themeMenuOpen, setThemeMenuOpen] = useState(false)
  const { theme, setTheme, resolvedTheme } = useTheme()
  const { language, setLanguage, t } = useTranslation()

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Command palette shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
      if (e.key === 'Escape') {
        setSearchOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <>
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className={cn(
          'fixed top-0 w-full z-40 transition-all duration-500',
          scrolled ? 'glass py-4' : 'py-6'
        )}
      >
        <div className="container mx-auto px-6 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="group relative">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative"
            >
              <span className="font-ultralight text-3xl md:text-4xl tracking-[0.3em] uppercase">
                LUKHAS
              </span>
              <motion.div
                className="absolute -bottom-2 left-0 h-px bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian"
                initial={{ width: 0 }}
                whileHover={{ width: '100%' }}
                transition={{ duration: 0.3 }}
              />
            </motion.div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <NavLink href="#products">{t('nav.products')}</NavLink>
            <NavLink href="#technology">{t('nav.technology')}</NavLink>
            <NavLink href="#developers">{t('nav.developers')}</NavLink>
            <NavLink href="#pricing">{t('nav.pricing')}</NavLink>

            {/* Search Button */}
            <button
              onClick={() => setSearchOpen(true)}
              className="p-2 hover:bg-glass rounded-lg transition-colors group"
              aria-label="Search"
            >
              <Search className="w-4 h-4 text-text-secondary group-hover:text-text-primary transition-colors" />
            </button>

            {/* Language Switcher */}
            <div className="relative">
              <button
                onClick={() => setLangMenuOpen(!langMenuOpen)}
                className="flex items-center space-x-2 p-2 hover:bg-glass rounded-lg transition-colors"
                aria-label="Change language"
              >
                <Globe className="w-4 h-4 text-text-secondary" />
                <span className="text-xs text-text-secondary">{languages[language]?.flag || '🌍'}</span>
              </button>

              <AnimatePresence>
                {langMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-48 glass rounded-xl p-2 z-50"
                  >
                    {Object.entries(languages).map(([code, config]) => (
                      <button
                        key={code}
                        onClick={() => {
                          setLanguage(code as Language)
                          setLangMenuOpen(false)
                        }}
                        className={cn(
                          'w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 transition-colors',
                          language === code ? 'bg-trinity-consciousness/20' : 'hover:bg-glass'
                        )}
                      >
                        <span className="text-lg">{config?.flag || '🏳️'}</span>
                        <div>
                          <div className="text-sm">{config?.nativeName || code}</div>
                          <div className="text-xs text-text-tertiary">{config?.name || code}</div>
                        </div>
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Theme Toggle */}
            <div className="relative">
              <button
                onClick={() => setThemeMenuOpen(!themeMenuOpen)}
                className="p-2 hover:bg-glass rounded-lg transition-colors"
                aria-label="Change theme"
              >
                {resolvedTheme === 'dark' ? (
                  <Moon className="w-4 h-4 text-text-secondary" />
                ) : (
                  <Sun className="w-4 h-4 text-text-secondary" />
                )}
              </button>

              <AnimatePresence>
                {themeMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-36 glass rounded-xl p-2 z-50"
                  >
                    <button
                      onClick={() => {
                        setTheme('light')
                        setThemeMenuOpen(false)
                      }}
                      className={cn(
                        'w-full text-left px-3 py-2 rounded-lg flex items-center space-x-2 transition-colors',
                        theme === 'light' ? 'bg-trinity-consciousness/20' : 'hover:bg-glass'
                      )}
                    >
                      <Sun className="w-4 h-4" />
                      <span className="text-sm">Light</span>
                    </button>
                    <button
                      onClick={() => {
                        setTheme('dark')
                        setThemeMenuOpen(false)
                      }}
                      className={cn(
                        'w-full text-left px-3 py-2 rounded-lg flex items-center space-x-2 transition-colors',
                        theme === 'dark' ? 'bg-trinity-consciousness/20' : 'hover:bg-glass'
                      )}
                    >
                      <Moon className="w-4 h-4" />
                      <span className="text-sm">Dark</span>
                    </button>
                    <button
                      onClick={() => {
                        setTheme('system')
                        setThemeMenuOpen(false)
                      }}
                      className={cn(
                        'w-full text-left px-3 py-2 rounded-lg flex items-center space-x-2 transition-colors',
                        theme === 'system' ? 'bg-trinity-consciousness/20' : 'hover:bg-glass'
                      )}
                    >
                      <Monitor className="w-4 h-4" />
                      <span className="text-sm">System</span>
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Command Palette Hint */}
            <div className="flex items-center space-x-1 text-text-tertiary text-xs">
              <Command className="w-3 h-3" />
              <span>K</span>
            </div>

            {/* CTA Buttons */}
            <Link
              href="/console"
              className="px-6 py-2 border border-trinity-consciousness text-trinity-consciousness hover:bg-trinity-consciousness hover:text-bg-primary transition-all duration-300 font-regular text-sm tracking-[0.15em] uppercase"
            >
              {t('nav.console')}
            </Link>
            <button className="px-6 py-2 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-bg-primary hover:opacity-90 transition-opacity font-regular text-sm tracking-[0.15em] uppercase">
              {t('nav.lukhasId')}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 hover:bg-glass rounded-lg transition-colors"
            aria-label="Menu"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-30 md:hidden"
          >
            <div className="absolute inset-0 bg-bg-primary/95 backdrop-blur-2xl" />
            <div className="relative h-full flex flex-col items-center justify-center space-y-8">
              <MobileNavLink href="#products" onClick={() => setMobileMenuOpen(false)}>
                {t('nav.products')}
              </MobileNavLink>
              <MobileNavLink href="#technology" onClick={() => setMobileMenuOpen(false)}>
                {t('nav.technology')}
              </MobileNavLink>
              <MobileNavLink href="#developers" onClick={() => setMobileMenuOpen(false)}>
                {t('nav.developers')}
              </MobileNavLink>
              <MobileNavLink href="#pricing" onClick={() => setMobileMenuOpen(false)}>
                {t('nav.pricing')}
              </MobileNavLink>
              <div className="h-px w-32 bg-glass-border" />
              <Link
                href="/console"
                onClick={() => setMobileMenuOpen(false)}
                className="px-8 py-3 border border-trinity-consciousness text-trinity-consciousness font-regular text-sm tracking-[0.15em] uppercase"
              >
                {t('nav.console')}
              </Link>
              <button className="px-8 py-3 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-bg-primary font-regular text-sm tracking-[0.15em] uppercase">
                {t('nav.lukhasId')}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search Modal */}
      <AnimatePresence>
        {searchOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-start justify-center pt-32"
            onClick={() => setSearchOpen(false)}
          >
            <div className="absolute inset-0 bg-bg-primary/80 backdrop-blur-xl" />
            <motion.div
              initial={{ scale: 0.95, y: -20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: -20 }}
              onClick={(e) => e.stopPropagation()}
              className="relative w-full max-w-2xl mx-4 glass rounded-2xl p-6"
            >
              <input
                type="text"
                placeholder={t('nav.search')}
                className="w-full bg-transparent text-2xl font-light outline-none placeholder:text-text-tertiary"
                autoFocus
              />
              <div className="mt-6 text-text-tertiary text-sm">
                Press <kbd className="px-2 py-1 bg-glass rounded">ESC</kbd> to close
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="relative font-regular text-sm tracking-[0.15em] uppercase text-text-secondary hover:text-text-primary transition-colors group"
    >
      {children}
      <motion.span
        className="absolute -bottom-1 left-0 h-px bg-trinity-consciousness"
        initial={{ width: 0 }}
        whileHover={{ width: '100%' }}
        transition={{ duration: 0.3 }}
      />
    </Link>
  )
}

function MobileNavLink({
  href,
  children,
  onClick
}: {
  href: string;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Link
        href={href}
        onClick={onClick}
        className="font-regular text-2xl tracking-[0.2em] uppercase text-text-secondary hover:text-text-primary transition-colors"
      >
        {children}
      </Link>
    </motion.div>
  )
}
