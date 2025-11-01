'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDreamContext } from '@/contexts/DreamContext'
import { useSSE, type DreamEvent } from '@/hooks/useSSE'
import dreamCopy from './dw_copy.json'

interface DreamSeedPortalProps {
  onDreamBegin: (seed: string) => void
}

export default function DreamSeedPortal({ onDreamBegin }: DreamSeedPortalProps) {
  const [seedValue, setSeedValue] = useState('')
  const [isHovering, setIsHovering] = useState(false)
  const [showPrompt, setShowPrompt] = useState(false)
  const [isGerminating, setIsGerminating] = useState(false)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches)
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  // Show prompt after a delay to create mystery (faster for reduced motion)
  useEffect(() => {
    const delay = prefersReducedMotion ? 500 : 2000
    const timer = setTimeout(() => setShowPrompt(true), delay)
    return () => clearTimeout(timer)
  }, [prefersReducedMotion])

  const handleSeedPlanting = async () => {
    if (!seedValue.trim()) return

    setIsGerminating(true)

    // Germination animation before transitioning
    setTimeout(() => {
      onDreamBegin(seedValue)
    }, 3000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSeedPlanting()
    }
  }

  return (
    <div className="relative min-h-screen bg-black overflow-hidden">
      {/* Cosmic Void Background */}
      <div className="absolute inset-0">
        {/* Subtle star field */}
        <div className="absolute inset-0 opacity-30">
          {Array.from({ length: prefersReducedMotion ? 20 : 100 }).map((_, i) => (
            <div
              key={i}
              className={`absolute w-px h-px bg-white rounded-full ${prefersReducedMotion ? '' : 'animate-pulse'}`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: prefersReducedMotion ? '0s' : `${Math.random() * 5}s`,
                animationDuration: prefersReducedMotion ? '0s' : `${2 + Math.random() * 3}s`,
              }}
            />
          ))}
        </div>

        {/* Gentle cosmic energy waves */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-radial from-purple-900/10 via-transparent to-transparent animate-pulse" />
          <div className="absolute inset-0 bg-gradient-radial from-blue-900/5 via-transparent to-transparent animate-pulse" style={{ animationDelay: '1s' }} />
        </div>
      </div>

      {/* Main Portal */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-6">
        <div className="text-center max-w-2xl">

          {/* Title - Appears first */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 2, ease: "easeOut" }}
            className="mb-16"
          >
            <h1 className="text-6xl md:text-8xl font-ultralight text-white mb-6 tracking-wider">
              <span className="inline-block">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-white">
                  Dream
                </span>
              </span>
              <br />
              <span className="inline-block">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-200 via-white to-purple-200">
                  Weaver
                </span>
              </span>
            </h1>
          </motion.div>

          {/* Seed Input Portal */}
          <AnimatePresence>
            {showPrompt && !isGerminating && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0 }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="space-y-8"
              >
                {/* Mystical prompt */}
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5, duration: 1 }}
                  className="text-xl md:text-2xl text-white/70 font-light leading-relaxed"
                >
                  {dreamCopy.phases.seed.description}
                </motion.p>

                {/* Seed Input - Glowing portal */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1, duration: 1 }}
                  className="relative"
                  onMouseEnter={() => setIsHovering(true)}
                  onMouseLeave={() => setIsHovering(false)}
                >
                  {/* Glow effect */}
                  <div className={`absolute inset-0 rounded-full transition-all duration-1000 ${
                    isHovering || seedValue
                      ? 'bg-purple-500/20 blur-xl scale-110'
                      : 'bg-purple-500/10 blur-lg scale-100'
                  }`} />

                  {/* Input field */}
                  <input
                    ref={inputRef}
                    type="text"
                    value={seedValue}
                    onChange={(e) => setSeedValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Plant your consciousness seed..."
                    aria-label={dreamCopy.phases.seed.description}
                    aria-describedby="seed-help"
                    autoFocus
                    className="relative z-10 w-full max-w-md mx-auto px-8 py-6 bg-black/50 border border-white/20 rounded-full text-white text-xl text-center placeholder-white/40 focus:outline-none focus:border-purple-400/50 focus:bg-black/70 transition-all duration-500 backdrop-blur-sm focus:ring-2 focus:ring-purple-400/20"
                  />

                  {/* Subtle pulsing ring */}
                  <div className="absolute inset-0 rounded-full border border-purple-500/30 animate-pulse" />
                </motion.div>

                {/* Begin Journey Trigger */}
                <AnimatePresence>
                  {seedValue.trim() && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.5 }}
                    >
                      <motion.button
                        onClick={handleSeedPlanting}
                        className="px-8 py-4 bg-gradient-to-r from-purple-600/80 to-blue-600/80 text-white rounded-full font-light text-lg hover:from-purple-500/90 hover:to-blue-500/90 transition-all duration-500 backdrop-blur-sm border border-white/20"
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        {dreamCopy.actions.begin_dream}
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Gentle guidance */}
                <motion.p
                  id="seed-help"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 2, duration: 1 }}
                  className="text-sm text-white/40 font-light"
                >
                  {dreamCopy.phases.seed.tooltip}
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Germination Animation */}
          <AnimatePresence>
            {isGerminating && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 1.5 }}
                className="space-y-8"
              >
                {/* Growing seed visualization */}
                <div className="relative">
                  <motion.div
                    initial={{ scale: 0.5, opacity: 0.5 }}
                    animate={{
                      scale: [0.5, 1.2, 1],
                      opacity: [0.5, 1, 0.8],
                      rotate: [0, 180, 360]
                    }}
                    transition={{
                      duration: 3,
                      times: [0, 0.6, 1],
                      ease: "easeInOut"
                    }}
                    className="w-32 h-32 mx-auto bg-gradient-to-r from-purple-500 to-blue-500 rounded-full opacity-80 blur-sm"
                  />
                  <motion.div
                    initial={{ scale: 0.3 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 2, ease: "easeOut" }}
                    className="absolute inset-0 flex items-center justify-center text-6xl"
                  >
                    🌱
                  </motion.div>
                </div>

                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="text-2xl text-white/80 font-light"
                >
                  {dreamCopy.phases.awakening.status}
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Attribution */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 5, duration: 2 }}
        className="absolute bottom-6 right-6 text-xs text-white/30"
      >
        {dreamCopy.messages.api_attribution}
      </motion.div>
    </div>
  )
}
