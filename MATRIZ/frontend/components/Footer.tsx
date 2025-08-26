'use client'

import Link from 'next/link'
import { Github, Twitter, Linkedin, Mail, ExternalLink, Atom, Brain, Shield } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    product: [
      { label: 'Features', href: '/#trinity' },
      { label: 'Console', href: '/console' },
      { label: 'API', href: '/api' },
      { label: 'Pricing', href: '/pricing' }
    ],
    resources: [
      { label: 'Documentation', href: '/docs' },
      { label: 'GitHub', href: 'https://github.com/LukhasAI', external: true },
      { label: 'Blog', href: '/blog' },
      { label: 'Research', href: '/research' }
    ],
    company: [
      { label: 'About', href: '/about' },
      { label: 'Careers', href: '/careers' },
      { label: 'Contact', href: '/contact' },
      { label: 'Partners', href: '/partners' }
    ],
    legal: [
      { label: 'Privacy', href: '/privacy' },
      { label: 'Terms', href: '/terms' },
      { label: 'Security', href: '/security' },
      { label: 'Ethics', href: '/ethics' }
    ]
  }

  const socialLinks = [
    { icon: <Github className="w-5 h-5" />, href: 'https://github.com/LukhasAI', label: 'GitHub' },
    { icon: <Twitter className="w-5 h-5" />, href: 'https://twitter.com/lukhas_ai', label: 'Twitter' },
    { icon: <Linkedin className="w-5 h-5" />, href: 'https://linkedin.com/company/lukhas', label: 'LinkedIn' },
    { icon: <Mail className="w-5 h-5" />, href: 'mailto:hello@lukhas.ai', label: 'Email' }
  ]

  return (
    <footer className="relative bg-black/50 border-t border-white/10 mt-32">
      {/* Gradient Line */}
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian" />

      <div className="container mx-auto max-w-7xl px-6 py-16">
        {/* Main Footer Content */}
        <div className="grid md:grid-cols-5 gap-8 mb-12">
          {/* Brand Column */}
          <div className="md:col-span-1">
            <div className="mb-6">
              <h3 className="text-3xl font-ultralight tracking-[0.2em] gradient-text">
                LUKHAS
              </h3>
              <p className="text-xs text-primary-light/60 mt-2">
                Building Conscious AI
              </p>
            </div>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg bg-trinity-identity/10">
                <Atom className="w-6 h-6 text-trinity-identity" strokeWidth={1.5} />
              </div>
              <div className="p-2 rounded-lg bg-trinity-consciousness/10">
                <Brain className="w-6 h-6 text-trinity-consciousness" strokeWidth={1.5} />
              </div>
              <div className="p-2 rounded-lg bg-trinity-guardian/10">
                <Shield className="w-6 h-6 text-trinity-guardian" strokeWidth={1.5} />
              </div>
            </div>
            <p className="text-sm text-primary-light/60">
              Trinity Framework for ethical, transparent AI development
            </p>
          </div>

          {/* Links Columns */}
          <div className="md:col-span-4 grid sm:grid-cols-2 md:grid-cols-4 gap-8">
            {/* Product */}
            <div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-4 text-trinity-consciousness">
                Product
              </h4>
              <ul className="space-y-3">
                {footerLinks.product.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-primary-light/60 hover:text-primary-light transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-4 text-trinity-identity">
                Resources
              </h4>
              <ul className="space-y-3">
                {footerLinks.resources.map((link) => (
                  <li key={link.label}>
                    {link.external ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-light/60 hover:text-primary-light transition-colors inline-flex items-center space-x-1"
                      >
                        <span>{link.label}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <Link
                        href={link.href}
                        className="text-sm text-primary-light/60 hover:text-primary-light transition-colors"
                      >
                        {link.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-4 text-trinity-guardian">
                Company
              </h4>
              <ul className="space-y-3">
                {footerLinks.company.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-primary-light/60 hover:text-primary-light transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-4 text-accent-gold">
                Legal
              </h4>
              <ul className="space-y-3">
                {footerLinks.legal.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-primary-light/60 hover:text-primary-light transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Newsletter Section */}
        <div className="glass-panel rounded-xl p-6 mb-12">
          <div className="grid md:grid-cols-2 gap-6 items-center">
            <div>
              <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-2">
                Stay Updated
              </h3>
              <p className="text-sm text-primary-light/60">
                Get the latest updates on MATADA development and consciousness research
              </p>
            </div>
            <form className="flex space-x-2">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-trinity-consciousness transition-colors"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-trinity-consciousness text-primary-dark rounded-lg hover:opacity-90 transition-opacity text-sm font-regular"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-white/10">
          {/* Copyright */}
          <div className="text-sm text-primary-light/40 mb-4 md:mb-0">
            © {currentYear} LUKHAS AI. All rights reserved. Open source under MIT License.
          </div>

          {/* Social Links */}
          <div className="flex items-center space-x-4">
            {socialLinks.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                aria-label={social.label}
              >
                {social.icon}
              </a>
            ))}
          </div>
        </div>

        {/* Status Indicators */}
        <div className="mt-8 flex items-center justify-center space-x-6 text-xs text-primary-light/40">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-trinity-guardian animate-pulse" />
            <span>System Online</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Drift: 0.03</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Ethics: 0.97</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Nodes: 1,247 Active</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
