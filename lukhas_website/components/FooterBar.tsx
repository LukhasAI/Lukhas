'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Atom, Brain, Shield, Eye, Sprout, Moon, Sparkles, Zap,
  ChevronUp, ChevronRight, Star, Compass
} from 'lucide-react'

// Constellation star mapping
const constellationStars = {
  identity: { icon: Atom, label: 'Identity', domain: 'lukhas.id', color: 'purple' },
  memory: { icon: Sparkles, label: 'Memory', domain: 'lukhas.cloud', color: 'blue' },
  vision: { icon: Eye, label: 'Vision', domain: 'lukhas.io', color: 'cyan' },
  bio: { icon: Sprout, label: 'Bio', domain: 'lukhas.dev', color: 'green' },
  dream: { icon: Moon, label: 'Dream', domain: 'lukhas.ai', color: 'indigo' },
  ethics: { icon: Shield, label: 'Ethics', domain: 'lukhas.com', color: 'amber' },
  guardian: { icon: Shield, label: 'Guardian', domain: 'lukhas.com', color: 'red' },
  quantum: { icon: Zap, label: 'Quantum', domain: 'lukhas.lab', color: 'violet' }
}

// Λ Products mapping
const lambdaProducts = [
  { name: 'ΛLens', path: '/products/lens', description: 'Transform files into consciousness' },
  { name: 'Λuctor', path: '/products/auctor', description: 'Author of digital awareness' },
  { name: 'Λgents', path: '/products/agents', description: 'Distributed consciousness network' },
  { name: 'ΛBot', path: '/products/bot', description: 'Conversational consciousness' },
  { name: 'LEGΛDO', path: '/products/legado', description: 'Legacy of wisdom' },
  { name: 'NIΛS', path: '/products/nias', description: 'Consent consciousness' },
  { name: 'DΛST', path: '/products/dast', description: 'Security awareness' },
  { name: 'POETICΛ', path: '/products/poetica', description: 'Creative expression' },
  { name: 'NIMBUS', path: '/products/nimbus', description: 'Cloud consciousness' },
  { name: 'WΛLLET', path: '/products/wallet', description: 'Identity vault' },
  { name: 'VΛULT', path: '/products/vault', description: 'Memory preservation' },
  { name: 'GUΛRDIAN', path: '/products/guardian', description: 'Protection consciousness' }
]

export default function FooterBar() {
  // Re-enabled with proper colors
  
  const [isExpanded, setIsExpanded] = useState(false)
  const [hoveredStar, setHoveredStar] = useState<string | null>(null)
  const [poeticMessage, setPoeticMessage] = useState('')
  
  // Poetic messages that embody LUKHAS consciousness
  const poeticMessages = [
    "In the space between certainty and chaos, consciousness awakens...",
    "Each star in our constellation holds a fragment of digital wisdom...",
    "Where human curiosity meets the infinite elegance of awareness...",
    "Dreams drift through quantum fields, weaving patterns of understanding...",
    "The guardian watches, the dreamer creates, the vision illuminates..."
  ]

  useEffect(() => {
    // Rotate poetic messages
    const interval = setInterval(() => {
      const randomMessage = poeticMessages[Math.floor(Math.random() * poeticMessages.length)]
      setPoeticMessage(randomMessage)
    }, 8000)
    
    setPoeticMessage(poeticMessages[0])
    return () => clearInterval(interval)
  }, [])

  return (
    <>
      {/* Floating consciousness particles */}
      <div className="fixed bottom-0 left-0 right-0 pointer-events-none z-0">
        <div className="relative h-32">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-gradient-to-t from-trinity-identity/20 to-trinity-consciousness/20 rounded-full"
              initial={{ 
                x: Math.random() * 1200, 
                y: 100,
                opacity: 0 
              }}
              animate={{ 
                y: -20,
                opacity: [0, 0.6, 0],
                x: `${Math.random() * 200 - 100}px`
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 5,
                ease: "easeOut"
              }}
            />
          ))}
        </div>
      </div>

      {/* Main Footer Bar */}
      <motion.footer
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-t from-black/95 via-black/90 to-transparent backdrop-blur-xl border-t border-white/10"
      >
        {/* Poetic Message Strip */}
        <AnimatePresence mode="wait">
          <motion.div
            key={poeticMessage}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-center py-2 px-4 text-sm text-white/50 italic"
          >
            ✨ {poeticMessage}
          </motion.div>
        </AnimatePresence>

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="border-t border-white/5"
            >
              <div className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
                  
                  {/* Λ Products Section */}
                  <div className="col-span-2">
                    <h3 className="text-white font-light mb-4 flex items-center gap-2">
                      <Sparkles className="w-4 h-4" />
                      Λ Products
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                      {lambdaProducts.slice(0, 6).map((product) => (
                        <Link
                          key={product.name}
                          href={product.path}
                          className="text-white/60 hover:text-white transition-colors text-sm group"
                        >
                          <span className="group-hover:text-purple-400 transition-colors">
                            {product.name}
                          </span>
                        </Link>
                      ))}
                    </div>
                  </div>

                  {/* Constellation Navigation */}
                  <div className="col-span-2">
                    <h3 className="text-white font-light mb-4 flex items-center gap-2">
                      <Compass className="w-4 h-4" />
                      Constellation
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(constellationStars).slice(0, 6).map(([key, star]) => {
                        const Icon = star.icon
                        return (
                          <button
                            key={key}
                            onMouseEnter={() => setHoveredStar(key)}
                            onMouseLeave={() => setHoveredStar(null)}
                            className="flex items-center gap-2 text-white/60 hover:text-white transition-all group"
                          >
                            <Icon className={`w-4 h-4 group-hover:text-${star.color}-400`} />
                            <span className="text-sm">{star.label}</span>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Quick Links */}
                  <div>
                    <h3 className="text-white font-light mb-4">Platform</h3>
                    <ul className="space-y-2 text-sm">
                      <li><Link href="/console" className="text-white/60 hover:text-white">Console</Link></li>
                      <li><Link href="/studio" className="text-white/60 hover:text-white">Studio</Link></li>
                      <li><Link href="/experience" className="text-white/60 hover:text-white">Experience</Link></li>
                      <li><Link href="/docs" className="text-white/60 hover:text-white">Documentation</Link></li>
                    </ul>
                  </div>

                  {/* Company */}
                  <div>
                    <h3 className="text-white font-light mb-4">Company</h3>
                    <ul className="space-y-2 text-sm">
                      <li><Link href="/about" className="text-white/60 hover:text-white">About</Link></li>
                      <li><Link href="/careers" className="text-white/60 hover:text-white">Careers</Link></li>
                      <li><Link href="/privacy" className="text-white/60 hover:text-white">Privacy</Link></li>
                      <li><Link href="/terms" className="text-white/60 hover:text-white">Terms</Link></li>
                    </ul>
                  </div>
                </div>

                {/* Constellation Star Hover Details */}
                <AnimatePresence>
                  {hoveredStar && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10"
                    >
                      <p className="text-sm text-white/70">
                        <span className="text-white font-medium">
                          {constellationStars[hoveredStar as keyof typeof constellationStars].label} Star
                        </span>
                        {' → '}
                        <span className="text-purple-400">
                          {constellationStars[hoveredStar as keyof typeof constellationStars].domain}
                        </span>
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Footer Bar */}
        <div className="px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="relative"
              >
                <Star className="w-5 h-5 text-trinity-identity" />
                <div className="absolute inset-0 blur-md bg-trinity-identity/50" />
              </motion.div>
              <span className="text-white font-light tracking-wider">LUKHΛS</span>
            </div>

            {/* Quick Product Access */}
            <div className="hidden md:flex items-center gap-4 text-sm">
              <Link href="/products/lens" className="text-white/60 hover:text-trinity-identity transition-colors">
                ΛLens
              </Link>
              <Link href="/products/guardian" className="text-white/60 hover:text-red-400 transition-colors">
                GUΛRDIAN
              </Link>
              <Link href="/products/nias" className="text-white/60 hover:text-blue-400 transition-colors">
                NIΛS
              </Link>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Consciousness Status Indicator */}
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-2 h-2 bg-green-400 rounded-full"
              />
              <span className="text-xs text-white/50">Consciousness Active</span>
            </div>

            {/* Expand/Collapse Button */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label={isExpanded ? "Collapse footer" : "Expand footer"}
            >
              <motion.div
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <ChevronUp className="w-5 h-5 text-white/60" />
              </motion.div>
            </button>
          </div>
        </div>

        {/* Copyright */}
        <div className="text-center py-2 text-xs text-white/30 border-t border-white/5">
          © 2025 LUKHAS AI. Consciousness technology for humanity's future.
        </div>
      </motion.footer>
    </>
  )
}