'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useDragControls } from 'framer-motion'
import { Layers, Plus, X, Sparkles, Shuffle, Lock, Unlock } from 'lucide-react'

interface Glyph {
  id: string
  symbol: string
  meaning: string
  color: string
  position: { x: number; y: number }
  locked: boolean
  connections: string[]
}

interface GlyphComposerProps {
  glyphs: string[]
  onGlyphUpdate: (glyphs: string[]) => void
}

const GLYPH_LIBRARY = [
  { symbol: '⚛️', meaning: 'Identity', color: '#60a5fa' },
  { symbol: '🧠', meaning: 'Consciousness', color: '#a78bfa' },
  { symbol: '🛡️', meaning: 'Guardian', color: '#fbbf24' },
  { symbol: '💫', meaning: 'Transformation', color: '#f472b6' },
  { symbol: '🌊', meaning: 'Flow', color: '#34d399' },
  { symbol: '🔥', meaning: 'Passion', color: '#ef4444' },
  { symbol: '❄️', meaning: 'Clarity', color: '#06b6d4' },
  { symbol: '⚡', meaning: 'Energy', color: '#fde047' },
  { symbol: '🌙', meaning: 'Dreams', color: '#c084fc' },
  { symbol: '☀️', meaning: 'Awakening', color: '#fb923c' },
  { symbol: '🌈', meaning: 'Harmony', color: '#e879f9' },
  { symbol: '💎', meaning: 'Value', color: '#38bdf8' }
]

export default function GlyphComposer({ glyphs: initialGlyphs, onGlyphUpdate }: GlyphComposerProps) {
  const [activeGlyphs, setActiveGlyphs] = useState<Glyph[]>([])
  const [selectedGlyph, setSelectedGlyph] = useState<string | null>(null)
  const [connectionMode, setConnectionMode] = useState(false)
  const [draggedOver, setDraggedOver] = useState<string | null>(null)
  const composerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    // Initialize with provided glyphs
    const newGlyphs = initialGlyphs.slice(0, 5).map((symbol, index) => {
      const glyphData = GLYPH_LIBRARY.find(g => g.symbol === symbol) || GLYPH_LIBRARY[index % GLYPH_LIBRARY.length]
      return {
        id: `glyph-${Date.now()}-${index}`,
        symbol: glyphData.symbol,
        meaning: glyphData.meaning,
        color: glyphData.color,
        position: {
          x: 100 + (index % 3) * 150,
          y: 100 + Math.floor(index / 3) * 150
        },
        locked: false,
        connections: []
      }
    })
    setActiveGlyphs(newGlyphs)
  }, [initialGlyphs])

  const addGlyph = (glyphData: typeof GLYPH_LIBRARY[0]) => {
    const newGlyph: Glyph = {
      id: `glyph-${Date.now()}`,
      symbol: glyphData.symbol,
      meaning: glyphData.meaning,
      color: glyphData.color,
      position: {
        x: Math.random() * 300 + 50,
        y: Math.random() * 200 + 50
      },
      locked: false,
      connections: []
    }

    const updated = [...activeGlyphs, newGlyph]
    setActiveGlyphs(updated)
    onGlyphUpdate(updated.map(g => g.symbol))
  }

  const removeGlyph = (id: string) => {
    const updated = activeGlyphs.filter(g => {
      if (g.id === id) return false
      // Remove connections to deleted glyph
      g.connections = g.connections.filter(c => c !== id)
      return true
    })
    setActiveGlyphs(updated)
    onGlyphUpdate(updated.map(g => g.symbol))
  }

  const toggleLock = (id: string) => {
    const updated = activeGlyphs.map(g =>
      g.id === id ? { ...g, locked: !g.locked } : g
    )
    setActiveGlyphs(updated)
  }

  const handleDragEnd = (id: string, x: number, y: number) => {
    const updated = activeGlyphs.map(g =>
      g.id === id ? { ...g, position: { x, y } } : g
    )
    setActiveGlyphs(updated)

    // Check for nearby glyphs to create connections
    const draggedGlyph = updated.find(g => g.id === id)
    if (draggedGlyph) {
      updated.forEach(g => {
        if (g.id !== id) {
          const distance = Math.sqrt(
            Math.pow(g.position.x - x, 2) +
            Math.pow(g.position.y - y, 2)
          )
          if (distance < 100) {
            // Create connection if close enough
            if (!draggedGlyph.connections.includes(g.id)) {
              draggedGlyph.connections.push(g.id)
            }
            if (!g.connections.includes(id)) {
              g.connections.push(id)
            }
          }
        }
      })
    }

    setActiveGlyphs(updated)
    onGlyphUpdate(updated.map(g => g.symbol))
  }

  const shuffleGlyphs = () => {
    const updated = activeGlyphs.map(g => ({
      ...g,
      position: {
        x: Math.random() * 300 + 50,
        y: Math.random() * 200 + 50
      }
    }))
    setActiveGlyphs(updated)
  }

  const createComposite = () => {
    if (activeGlyphs.length < 2) return

    // Combine all glyphs into a new composite meaning
    const composite = activeGlyphs.map(g => g.symbol).join('')
    const meanings = activeGlyphs.map(g => g.meaning).join(' + ')

    // Create a special composite glyph
    const compositeGlyph: Glyph = {
      id: `composite-${Date.now()}`,
      symbol: composite,
      meaning: `Composite: ${meanings}`,
      color: '#ffffff',
      position: { x: 200, y: 150 },
      locked: true,
      connections: activeGlyphs.map(g => g.id)
    }

    setActiveGlyphs([compositeGlyph])
    onGlyphUpdate([composite])
  }

  return (
    <div className="space-y-4">
      {/* Glyph Library */}
      <div className="flex flex-wrap gap-2 p-4 bg-white/5 rounded-lg">
        {GLYPH_LIBRARY.map((glyph) => (
          <motion.button
            key={glyph.symbol}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => addGlyph(glyph)}
            className="p-3 bg-white/10 hover:bg-white/20 rounded-lg transition-colors group relative"
            title={glyph.meaning}
          >
            <span className="text-2xl">{glyph.symbol}</span>
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-white/60 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              {glyph.meaning}
            </div>
          </motion.button>
        ))}
      </div>

      {/* Composition Canvas */}
      <div
        ref={composerRef}
        className="relative h-96 bg-gradient-to-br from-indigo-950/20 to-purple-950/20 rounded-2xl border border-white/10 overflow-hidden"
      >
        {/* Connection Lines */}
        <svg
          ref={svgRef}
          className="absolute inset-0 pointer-events-none"
          width="100%"
          height="100%"
        >
          {activeGlyphs.map(glyph =>
            glyph.connections.map(targetId => {
              const target = activeGlyphs.find(g => g.id === targetId)
              if (!target) return null

              return (
                <motion.line
                  key={`${glyph.id}-${targetId}`}
                  x1={glyph.position.x}
                  y1={glyph.position.y}
                  x2={target.position.x}
                  y2={target.position.y}
                  stroke="url(#gradient)"
                  strokeWidth="2"
                  strokeOpacity="0.3"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 0.5 }}
                />
              )
            })
          )}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>
          </defs>
        </svg>

        {/* Glyphs */}
        <AnimatePresence>
          {activeGlyphs.map((glyph) => (
            <motion.div
              key={glyph.id}
              drag={!glyph.locked}
              dragMomentum={false}
              dragElastic={0.1}
              onDragEnd={(e, info) => {
                const rect = composerRef.current?.getBoundingClientRect()
                if (rect) {
                  handleDragEnd(
                    glyph.id,
                    info.point.x - rect.left,
                    info.point.y - rect.top
                  )
                }
              }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{
                scale: 1,
                opacity: 1,
                x: glyph.position.x - 32,
                y: glyph.position.y - 32
              }}
              exit={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1.1 }}
              whileDrag={{ scale: 1.2 }}
              className="absolute w-16 h-16 cursor-move"
              style={{
                filter: selectedGlyph === glyph.id ? 'drop-shadow(0 0 20px rgba(139, 92, 246, 0.8))' : '',
                zIndex: selectedGlyph === glyph.id ? 10 : 1
              }}
            >
              <div
                className="relative w-full h-full rounded-full flex items-center justify-center"
                style={{ backgroundColor: glyph.color + '20', borderColor: glyph.color }}
                onClick={() => setSelectedGlyph(glyph.id === selectedGlyph ? null : glyph.id)}
              >
                <span className="text-2xl select-none">{glyph.symbol}</span>

                {/* Action Buttons */}
                {selectedGlyph === glyph.id && (
                  <div className="absolute -top-2 -right-2 flex gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleLock(glyph.id)
                      }}
                      className="p-1 bg-white/20 hover:bg-white/30 rounded-full"
                    >
                      {glyph.locked ?
                        <Lock className="w-3 h-3" /> :
                        <Unlock className="w-3 h-3" />
                      }
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        removeGlyph(glyph.id)
                      }}
                      className="p-1 bg-red-500/20 hover:bg-red-500/30 rounded-full"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}

                {/* Meaning Label */}
                <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-white/60 whitespace-nowrap">
                  {glyph.meaning}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Empty State */}
        {activeGlyphs.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-white/40">
            <div className="text-center">
              <Layers className="w-12 h-12 mx-auto mb-2" />
              <p>Add GLYPHs to begin composing</p>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={shuffleGlyphs}
          disabled={activeGlyphs.length === 0}
          className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Shuffle className="w-4 h-4" />
          Shuffle
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={createComposite}
          disabled={activeGlyphs.length < 2}
          className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          Create Composite
        </motion.button>
      </div>
    </div>
  )
}
