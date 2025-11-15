import { useEffect, useState } from 'react'
import { usePlaygroundStore } from '../../stores/playgroundStore'
import { CONSTELLATION_NODES } from '../../lib/playground/constants'
import type { ConstellationNode } from '../../types/playground'

export default function ConstellationPulse() {
  const activeNodes = usePlaygroundStore((state) => state.activeNodes)
  const nodeHistory = usePlaygroundStore((state) => state.nodeHistory)

  // Get latest detail for each node
  const getNodeDetail = (node: ConstellationNode): string => {
    const latestActivation = [...nodeHistory].reverse().find((h) => h.node === node)
    return latestActivation?.details || ''
  }

  return (
    <div className="w-40 h-full bg-black/40 backdrop-blur-md border-r border-white/10 px-3 py-4 overflow-y-auto">
      <div className="mb-6">
        <h2 className="text-xs uppercase tracking-wider text-white/60 mb-1">
          Constellation
        </h2>
        <p className="text-[10px] text-white/40 leading-relaxed">
          8 cognitive nodes
        </p>
      </div>

      <div className="space-y-3">
        {Object.values(CONSTELLATION_NODES).map((node) => {
          const intensity = activeNodes[node.id as ConstellationNode]
          const isActive = intensity > 0
          const detail = getNodeDetail(node.id as ConstellationNode)

          return (
            <NodeCard
              key={node.id}
              node={node}
              intensity={intensity}
              isActive={isActive}
              detail={detail}
            />
          )
        })}
      </div>
    </div>
  )
}

interface NodeCardProps {
  node: typeof CONSTELLATION_NODES[keyof typeof CONSTELLATION_NODES]
  intensity: number
  isActive: boolean
  detail: string
}

function NodeCard({ node, intensity, isActive, detail }: NodeCardProps) {
  const [showTooltip, setShowTooltip] = useState(false)

  const opacity = isActive ? 0.9 : 0.5

  const pulseAnimation = isActive
    ? {
        animation: `pulse ${node.pulseSpeed}s ease-in-out infinite`,
      }
    : {}

  return (
    <div
      className="relative group cursor-default"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Compact row instead of glass card */}
      <div
        className="flex items-center justify-between px-2 py-1 rounded-md hover:bg-white/5 transition-colors"
        style={{ opacity }}
      >
        <div className="flex items-center gap-2">
          <span
            className="text-sm"
            style={{
              filter: isActive ? 'brightness(1.4)' : 'brightness(0.9)',
              ...pulseAnimation,
            }}
          >
            {node.icon}
          </span>
          <span className="text-[11px] font-light text-white tracking-wide">
            {node.label}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-0.5 w-16 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-500 ease-out"
              style={{
                width: `${Math.max(intensity, 0.08) * 100}%`,
                backgroundColor: node.color,
                opacity: isActive ? 0.9 : 0.4,
              }}
            />
          </div>
          {isActive && (
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: node.color }}
            />
          )}
        </div>
      </div>

      {/* Smaller tooltip */}
      {showTooltip && (
        <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 z-50 w-56 pointer-events-none">
          <div className="bg-black/95 backdrop-blur-xl border border-white/15 rounded-lg px-3 py-2 shadow-2xl">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-base">{node.icon}</span>
              <h3 className="text-xs font-light text-white">{node.label}</h3>
            </div>
            <p className="text-[11px] text-white/70 leading-relaxed">
              {node.description}
            </p>
            {detail && (
              <div className="mt-2 pt-2 border-t border-white/10">
                <p className="text-[9px] text-white/50 uppercase tracking-wider mb-0.5">
                  Latest Activity
                </p>
                <p className="text-[11px] text-white/85">{detail}</p>
                {intensity > 0 && (
                  <p className="text-[9px] text-white/60 mt-0.5">
                    Intensity: {Math.round(intensity * 100)}%
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
