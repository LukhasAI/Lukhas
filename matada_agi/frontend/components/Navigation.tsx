'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled ? 'glass-panel py-4' : 'py-6'
      }`}
    >
      <div className="container mx-auto max-w-7xl px-6 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-3">
          <div className="relative">
            <span className="text-4xl font-ultralight tracking-[0.3em] gradient-text">
              LUKHAS
            </span>
            <div className="absolute -bottom-1 left-0 w-full h-px bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian opacity-50" />
          </div>
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center space-x-8">
          <Link href="/about" className="font-regular text-sm tracking-[0.2em] uppercase hover:text-trinity-consciousness transition-colors">
            ABOUT
          </Link>
          <Link href="/docs" className="font-regular text-sm tracking-[0.2em] uppercase hover:text-trinity-consciousness transition-colors">
            DOCS
          </Link>
          <Link href="/careers" className="font-regular text-sm tracking-[0.2em] uppercase hover:text-trinity-consciousness transition-colors">
            CAREERS
          </Link>
          <Link href="/partners" className="font-regular text-sm tracking-[0.2em] uppercase hover:text-trinity-consciousness transition-colors">
            PARTNERS
          </Link>
          <Link href="/console" className="font-regular text-sm tracking-[0.2em] uppercase px-6 py-2 border border-trinity-consciousness text-trinity-consciousness hover:bg-trinity-consciousness hover:text-primary-dark transition-all">
            CONSOLE
          </Link>
          <button className="font-regular text-sm tracking-[0.2em] uppercase px-6 py-2 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark hover:opacity-90 transition-opacity">
            LUKHAS ID
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden w-8 h-8 flex flex-col justify-center items-center"
        >
          <span className={`block w-6 h-0.5 bg-primary-light transition-all ${mobileMenuOpen ? 'rotate-45 translate-y-1' : ''}`} />
          <span className={`block w-6 h-0.5 bg-primary-light my-1 transition-all ${mobileMenuOpen ? 'opacity-0' : ''}`} />
          <span className={`block w-6 h-0.5 bg-primary-light transition-all ${mobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden absolute top-full left-0 w-full glass-panel border-t border-white/10"
        >
          <div className="container mx-auto max-w-7xl px-6 py-6 flex flex-col space-y-4">
            <Link href="/about" className="font-regular text-sm tracking-[0.2em] uppercase">ABOUT</Link>
            <Link href="/docs" className="font-regular text-sm tracking-[0.2em] uppercase">DOCS</Link>
            <Link href="/careers" className="font-regular text-sm tracking-[0.2em] uppercase">CAREERS</Link>
            <Link href="/partners" className="font-regular text-sm tracking-[0.2em] uppercase">PARTNERS</Link>
            <Link href="/console" className="font-regular text-sm tracking-[0.2em] uppercase">CONSOLE</Link>
            <button className="font-regular text-sm tracking-[0.2em] uppercase text-left">LUKHAS ID</button>
          </div>
        </motion.div>
      )}
    </motion.nav>
  )
}