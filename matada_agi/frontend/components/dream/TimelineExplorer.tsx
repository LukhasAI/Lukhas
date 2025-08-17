'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GitBranch, Circle, ChevronRight, Sparkles, AlertTriangle, TrendingUp } from 'lucide-react'

interface TimelineBranch {
  id: string
  probability: number
  description: string
  emotionalTone: {
    valence: number
    arousal: number
  }
  risk: number
  reward: number
  children?: TimelineBranch[]
}

interface TimelineExplorerProps {
  timeline: {
    branches: TimelineBranch[]
    selectedPath: number[]
  }
  onBranchSelect: (path: number[]) => void
}

function BranchNode({ 
  branch, 
  path, 
  depth, 
  selected,
  onSelect 
}: { 
  branch: TimelineBranch
  path: number[]
  depth: number
  selected: boolean
  onSelect: (path: number[]) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const [hovering, setHovering] = useState(false)

  const probabilityColor = branch.probability > 0.7 ? 'text-green-400' : 
                           branch.probability > 0.4 ? 'text-yellow-400' : 'text-red-400'
  
  const riskColor = branch.risk > 0.7 ? 'border-red-400' :
                     branch.risk > 0.4 ? 'border-yellow-400' : 'border-green-400'

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: depth * 0.1 }}
      className={`relative ${depth > 0 ? 'ml-8' : ''}`}
    >
      {/* Connection Line */}
      {depth > 0 && (
        <div className="absolute left-0 top-6 w-8 h-px bg-white/20" />
      )}

      {/* Branch Node */}
      <motion.div
        whileHover={{ scale: 1.02 }}
        onMouseEnter={() => setHovering(true)}
        onMouseLeave={() => setHovering(false)}
        onClick={() => {
          onSelect(path)
          if (branch.children && branch.children.length > 0) {
            setExpanded(!expanded)
          }
        }}
        className={`
          relative p-4 rounded-lg border cursor-pointer transition-all duration-200
          ${selected 
            ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border-indigo-400' 
            : `bg-white/5 hover:bg-white/10 ${riskColor}`
          }
        `}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Circle className={`w-3 h-3 ${selected ? 'fill-current text-indigo-400' : ''}`} />
              <span className="text-sm font-medium">{branch.description}</span>
              {branch.children && branch.children.length > 0 && (
                <ChevronRight 
                  className={`w-4 h-4 text-white/40 transition-transform ${expanded ? 'rotate-90' : ''}`} 
                />
              )}
            </div>
            
            {/* Metrics */}
            <div className="flex gap-4 text-xs">
              <span className={probabilityColor}>
                {(branch.probability * 100).toFixed(0)}% likely
              </span>
              <span className="text-white/50">
                Risk: {(branch.risk * 100).toFixed(0)}%
              </span>
              <span className="text-green-400/70">
                Reward: {(branch.reward * 100).toFixed(0)}%
              </span>
            </div>

            {/* Emotional Tone Indicator */}
            <div className="mt-2 flex gap-1">
              {Array.from({ length: 5 }, (_, i) => (
                <div
                  key={i}
                  className="h-1 w-8 rounded-full"
                  style={{
                    backgroundColor: `rgba(${
                      (branch.emotionalTone?.valence || 0.5) * 255
                    }, ${
                      (branch.emotionalTone?.arousal || 0.5) * 128
                    }, ${
                      (1 - (branch.emotionalTone?.valence || 0.5)) * 255
                    }, ${
                      i < Math.floor((branch.emotionalTone?.arousal || 0.5) * 5) ? 0.8 : 0.2
                    })`
                  }}
                />
              ))}
            </div>
          </div>

          {/* Visual Indicators */}
          <div className="flex flex-col gap-2 ml-4">
            {branch.probability > 0.7 && (
              <TrendingUp className="w-4 h-4 text-green-400" />
            )}
            {branch.risk > 0.6 && (
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
            )}
            {selected && (
              <Sparkles className="w-4 h-4 text-indigo-400" />
            )}
          </div>
        </div>

        {/* Hover Details */}
        <AnimatePresence>
          {hovering && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute left-0 right-0 -top-20 p-3 bg-black/90 border border-white/20 rounded-lg z-10 text-xs"
            >
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-white/50">Emotional Impact:</span>
                  <div className="mt-1">
                    Valence: {((branch.emotionalTone?.valence || 0.5) * 100).toFixed(0)}%
                  </div>
                  <div>
                    Arousal: {((branch.emotionalTone?.arousal || 0.5) * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <span className="text-white/50">Decision Metrics:</span>
                  <div className="mt-1">
                    Risk/Reward: {(branch.reward / (branch.risk || 0.1)).toFixed(2)}x
                  </div>
                  <div>
                    Confidence: {(branch.probability * (1 - branch.risk)).toFixed(2)}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Children Branches */}
      <AnimatePresence>
        {expanded && branch.children && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="relative"
          >
            {branch.children && branch.children.map((child, index) => (
              <BranchNode
                key={child.id}
                branch={child}
                path={[...path, index]}
                depth={depth + 1}
                selected={false}
                onSelect={onSelect}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function TimelineExplorer({ timeline, onBranchSelect }: TimelineExplorerProps) {
  const [selectedPath, setSelectedPath] = useState<number[]>(timeline?.selectedPath || [])
  const [collapseAnimation, setCollapseAnimation] = useState(false)

  // Mock timeline data if not provided or invalid
  const branches = (timeline?.branches && Array.isArray(timeline.branches) && timeline.branches.length > 0) 
    ? timeline.branches 
    : [
    {
      id: 'root',
      probability: 1.0,
      description: 'Current Reality',
      emotionalTone: { valence: 0.5, arousal: 0.5 },
      risk: 0,
      reward: 0.5,
      children: [
        {
          id: 'branch1',
          probability: 0.8,
          description: 'Path of Harmony',
          emotionalTone: { valence: 0.8, arousal: 0.4 },
          risk: 0.2,
          reward: 0.7,
          children: [
            {
              id: 'branch1-1',
              probability: 0.6,
              description: 'Creative Synthesis',
              emotionalTone: { valence: 0.9, arousal: 0.6 },
              risk: 0.3,
              reward: 0.9
            },
            {
              id: 'branch1-2',
              probability: 0.4,
              description: 'Peaceful Resolution',
              emotionalTone: { valence: 0.7, arousal: 0.3 },
              risk: 0.1,
              reward: 0.6
            }
          ]
        },
        {
          id: 'branch2',
          probability: 0.5,
          description: 'Path of Challenge',
          emotionalTone: { valence: 0.4, arousal: 0.8 },
          risk: 0.7,
          reward: 0.9,
          children: [
            {
              id: 'branch2-1',
              probability: 0.3,
              description: 'Breakthrough Discovery',
              emotionalTone: { valence: 0.6, arousal: 0.9 },
              risk: 0.8,
              reward: 1.0
            }
          ]
        },
        {
          id: 'branch3',
          probability: 0.3,
          description: 'Path of Mystery',
          emotionalTone: { valence: 0.5, arousal: 0.7 },
          risk: 0.5,
          reward: 0.8
        }
      ]
    }
  ]

  const handleBranchSelect = (path: number[]) => {
    setSelectedPath(path)
    setCollapseAnimation(true)
    
    // Trigger quantum collapse animation
    setTimeout(() => {
      onBranchSelect(path)
      setCollapseAnimation(false)
    }, 500)
  }

  return (
    <div className="relative">
      {/* Quantum Collapse Effect */}
      <AnimatePresence>
        {collapseAnimation && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 2, opacity: 0.5 }}
            exit={{ scale: 3, opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full blur-xl pointer-events-none"
          />
        )}
      </AnimatePresence>

      {/* Timeline Tree */}
      <div className="space-y-2">
        {branches && branches.length > 0 ? branches.map((branch, index) => (
          <BranchNode
            key={branch.id}
            branch={branch}
            path={[index]}
            depth={0}
            selected={selectedPath[0] === index}
            onSelect={handleBranchSelect}
          />
        )) : (
          <div className="p-4 text-center text-white/50">
            <p>No timeline branches available yet.</p>
            <p className="text-sm mt-2">Initiate a dream to explore possible paths.</p>
          </div>
        )}
      </div>

      {/* Timeline Statistics */}
      <div className="mt-6 p-4 bg-white/5 rounded-lg">
        <div className="grid grid-cols-3 gap-4 text-xs">
          <div>
            <span className="text-white/50">Total Branches:</span>
            <div className="text-lg font-medium mt-1">
              {countBranches(branches)}
            </div>
          </div>
          <div>
            <span className="text-white/50">Selected Depth:</span>
            <div className="text-lg font-medium mt-1">
              {selectedPath.length}
            </div>
          </div>
          <div>
            <span className="text-white/50">Quantum State:</span>
            <div className="text-lg font-medium mt-1">
              {collapseAnimation ? 'Collapsing' : 'Superposition'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function countBranches(branches: TimelineBranch[]): number {
  if (!branches || !Array.isArray(branches)) return 0
  let count = branches.length
  branches.forEach(branch => {
    if (branch?.children && Array.isArray(branch.children)) {
      count += countBranches(branch.children)
    }
  })
  return count
}