'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export function Footer() {
  return (
    <footer className="relative py-20 px-6 border-t border-glass-border">
      <div className="container mx-auto max-w-7xl">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">PRODUCTS</h3>
            <ul className="space-y-3">
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Lambda Suite</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">MATADA</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Trinity Framework</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">DEVELOPERS</h3>
            <ul className="space-y-3">
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Documentation</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">API</Link></li>
              <li><Link href="/console" className="font-light text-text-secondary hover:text-text-primary transition-colors">Console</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">COMPANY</h3>
            <ul className="space-y-3">
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">About</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Vision</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Careers</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">LEGAL</h3>
            <ul className="space-y-3">
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Privacy</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Terms</Link></li>
              <li><Link href="#" className="font-light text-text-secondary hover:text-text-primary transition-colors">Compliance</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-glass-border pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <span className="font-ultralight text-2xl tracking-[0.3em] uppercase">LUKHAS</span>
            <span className="text-text-tertiary">⚛️🧠🛡️</span>
          </div>
          <p className="font-light text-text-tertiary text-sm">
            © 2025 LUKHAS AI. Building Consciousness You Can Trust.
          </p>
        </div>
      </div>
    </footer>
  )
}