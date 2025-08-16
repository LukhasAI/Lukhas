'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Plus, Link2, Clock, Sparkles, X, ChevronDown, ChevronUp } from 'lucide-react'

interface Memory {
  id: string
  content: string
  timestamp: number
  emotionalWeight: number
  causalLinks: string[]
  foldDepth: number
  type: 'personal' | 'shared' | 'dream'
}

interface MemoryIntegratorProps {
  memories: Memory[]
  onMemoryAdd: (memory: Memory) => void
}

export default function MemoryIntegrator({ memories, onMemoryAdd }: MemoryIntegratorProps) {
  const [newMemory, setNewMemory] = useState('')
  const [memoryType, setMemoryType] = useState<'personal' | 'shared' | 'dream'>('personal')
  const [emotionalWeight, setEmotionalWeight] = useState(0.5)
  const [selectedMemory, setSelectedMemory] = useState<string | null>(null)
  const [expandedMemories, setExpandedMemories] = useState<Set<string>>(new Set())
  const [isAddingMemory, setIsAddingMemory] = useState(false)

  const handleAddMemory = () => {
    if (!newMemory.trim()) return

    const memory: Memory = {
      id: `memory-${Date.now()}`,
      content: newMemory,
      timestamp: Date.now(),
      emotionalWeight,
      causalLinks: selectedMemory ? [selectedMemory] : [],
      foldDepth: memories.length + 1,
      type: memoryType
    }

    onMemoryAdd(memory)
    setNewMemory('')
    setEmotionalWeight(0.5)
    setIsAddingMemory(false)
  }

  const toggleMemoryExpansion = (id: string) => {
    const newExpanded = new Set(expandedMemories)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedMemories(newExpanded)
  }

  const getMemoryColor = (type: Memory['type']) => {
    switch (type) {
      case 'personal': return 'from-blue-500 to-indigo-600'
      case 'shared': return 'from-green-500 to-emerald-600'
      case 'dream': return 'from-purple-500 to-pink-600'
    }
  }

  const getMemoryIcon = (type: Memory['type']) => {
    switch (type) {
      case 'personal': return '💭'
      case 'shared': return '🤝'
      case 'dream': return '🌙'
    }
  }

  const calculateCausalStrength = (memory: Memory) => {
    const linkCount = memory.causalLinks.length
    const depthFactor = 1 / (memory.foldDepth || 1)
    const emotionalFactor = memory.emotionalWeight
    return (linkCount * 0.4 + depthFactor * 0.3 + emotionalFactor * 0.3)
  }

  return (
    <div className="space-y-4">
      {/* Add Memory Form */}
      <AnimatePresence>
        {isAddingMemory ? (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 bg-white/5 rounded-lg space-y-3"
          >
            <textarea
              value={newMemory}
              onChange={(e) => setNewMemory(e.target.value)}
              placeholder="Describe your memory..."
              className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-trinity-consciousness/50 resize-none"
              rows={3}
            />

            {/* Memory Type Selection */}
            <div className="flex gap-2">
              {(['personal', 'shared', 'dream'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setMemoryType(type)}
                  className={`px-3 py-1 rounded-lg text-sm capitalize transition-all ${
                    memoryType === type
                      ? 'bg-gradient-to-r ' + getMemoryColor(type) + ' text-white'
                      : 'bg-white/10 hover:bg-white/20'
                  }`}
                >
                  {getMemoryIcon(type)} {type}
                </button>
              ))}
            </div>

            {/* Emotional Weight Slider */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-white/60">Emotional Weight</span>
                <span className="text-xs text-white/80">{(emotionalWeight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={emotionalWeight}
                onChange={(e) => setEmotionalWeight(parseFloat(e.target.value))}
                className="w-full h-1 bg-white/20 rounded-full appearance-none"
                style={{
                  background: `linear-gradient(to right, transparent ${emotionalWeight * 100}%, rgba(255,255,255,0.2) ${emotionalWeight * 100}%)`
                }}
              />
            </div>

            {/* Causal Link Selection */}
            {memories.length > 0 && (
              <div>
                <span className="text-xs text-white/60 block mb-2">Link to existing memory (optional)</span>
                <select
                  value={selectedMemory || ''}
                  onChange={(e) => setSelectedMemory(e.target.value || null)}
                  className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-trinity-consciousness/50"
                >
                  <option value="">No link</option>
                  {memories.map((mem) => (
                    <option key={mem.id} value={mem.id}>
                      {mem.content.substring(0, 50)}...
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleAddMemory}
                disabled={!newMemory.trim()}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Weave Memory
              </motion.button>
              <button
                onClick={() => setIsAddingMemory(false)}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        ) : (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setIsAddingMemory(true)}
            className="w-full px-4 py-3 bg-white/10 hover:bg-white/20 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Memory to Dream
          </motion.button>
        )}
      </AnimatePresence>

      {/* Memory Fold Visualization */}
      <div className="space-y-2">
        {memories.length === 0 ? (
          <div className="text-center py-8 text-white/40">
            <Brain className="w-12 h-12 mx-auto mb-2" />
            <p>No memories woven yet</p>
            <p className="text-xs mt-1">Add memories to enrich your dream</p>
          </div>
        ) : (
          <AnimatePresence>
            {memories.map((memory, index) => {
              const isExpanded = expandedMemories.has(memory.id)
              const causalStrength = calculateCausalStrength(memory)
              
              return (
                <motion.div
                  key={memory.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative"
                >
                  {/* Causal Connection Lines */}
                  {memory.causalLinks.length > 0 && (
                    <div className="absolute left-4 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent" />
                  )}

                  <div
                    className={`relative p-4 rounded-lg border cursor-pointer transition-all ${
                      isExpanded ? 'bg-white/10 border-white/30' : 'bg-white/5 border-white/10 hover:bg-white/10'
                    }`}
                    onClick={() => toggleMemoryExpansion(memory.id)}
                    style={{
                      marginLeft: `${memory.foldDepth * 10}px`
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{getMemoryIcon(memory.type)}</span>
                          <span className={`px-2 py-0.5 text-xs rounded-full bg-gradient-to-r ${getMemoryColor(memory.type)} text-white`}>
                            {memory.type}
                          </span>
                          <span className="text-xs text-white/40">
                            Fold #{memory.foldDepth}
                          </span>
                          {memory.causalLinks.length > 0 && (
                            <Link2 className="w-3 h-3 text-white/40" />
                          )}
                        </div>
                        
                        <p className="text-sm text-white/80">
                          {isExpanded ? memory.content : `${memory.content.substring(0, 100)}${memory.content.length > 100 ? '...' : ''}`}
                        </p>

                        {isExpanded && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-3 pt-3 border-t border-white/10"
                          >
                            <div className="grid grid-cols-2 gap-4 text-xs">
                              <div>
                                <span className="text-white/40">Emotional Weight</span>
                                <div className="mt-1 h-1 bg-white/10 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                                    style={{ width: `${memory.emotionalWeight * 100}%` }}
                                  />
                                </div>
                              </div>
                              <div>
                                <span className="text-white/40">Causal Strength</span>
                                <div className="mt-1 h-1 bg-white/10 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                                    style={{ width: `${causalStrength * 100}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                            
                            {memory.causalLinks.length > 0 && (
                              <div className="mt-2">
                                <span className="text-xs text-white/40">Linked to:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {memory.causalLinks.map((linkId) => {
                                    const linkedMemory = memories.find(m => m.id === linkId)
                                    return linkedMemory ? (
                                      <span key={linkId} className="px-2 py-0.5 text-xs bg-white/10 rounded">
                                        {linkedMemory.content.substring(0, 20)}...
                                      </span>
                                    ) : null
                                  })}
                                </div>
                              </div>
                            )}

                            <div className="mt-2 flex items-center gap-2 text-xs text-white/40">
                              <Clock className="w-3 h-3" />
                              {new Date(memory.timestamp).toLocaleTimeString()}
                            </div>
                          </motion.div>
                        )}
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleMemoryExpansion(memory.id)
                        }}
                        className="ml-2 p-1 hover:bg-white/10 rounded"
                      >
                        {isExpanded ? 
                          <ChevronUp className="w-4 h-4 text-white/60" /> : 
                          <ChevronDown className="w-4 h-4 text-white/60" />
                        }
                      </button>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        )}
      </div>

      {/* Memory Statistics */}
      {memories.length > 0 && (
        <div className="p-3 bg-white/5 rounded-lg">
          <div className="grid grid-cols-3 gap-3 text-xs text-center">
            <div>
              <div className="text-lg font-medium">{memories.length}</div>
              <div className="text-white/40">Total Memories</div>
            </div>
            <div>
              <div className="text-lg font-medium">
                {Math.max(...memories.map(m => m.foldDepth), 0)}
              </div>
              <div className="text-white/40">Max Fold Depth</div>
            </div>
            <div>
              <div className="text-lg font-medium">
                {memories.filter(m => m.causalLinks.length > 0).length}
              </div>
              <div className="text-white/40">Linked Memories</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}