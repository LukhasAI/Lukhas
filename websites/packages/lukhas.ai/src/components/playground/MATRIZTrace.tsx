import { useState } from 'react'
import { ChevronDown, ChevronRight, Copy, Check } from 'lucide-react'
import type { MATRIZTrace as MATRIZTraceType } from '../../types/playground'
import { MATRIZ_STAGES } from '../../lib/playground/constants'

interface MATRIZTraceProps {
  trace: MATRIZTraceType
}

export default function MATRIZTrace({ trace }: MATRIZTraceProps) {
  const [expandedStage, setExpandedStage] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const toggleStage = (stageId: string) => {
    setExpandedStage(expandedStage === stageId ? null : stageId)
  }

  const copyTrace = async () => {
    const traceText = JSON.stringify(trace, null, 2)
    await navigator.clipboard.writeText(traceText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Map trace data to stages
  const stageData = [
    {
      id: 'M',
      label: 'Memory',
      data: trace.memory,
      summary: `${trace.memory.retrieved.length} items retrieved`,
    },
    {
      id: 'A1',
      label: 'Attention',
      data: trace.attention,
      summary: `Focus: ${trace.attention.focus}`,
    },
    {
      id: 'T',
      label: 'Thought',
      data: trace.thought,
      summary: `${trace.thought.branches} reasoning branches`,
    },
    {
      id: 'R',
      label: 'Risk',
      data: trace.risk,
      summary: `Profile: ${trace.risk.profile}`,
      color: trace.risk.profile === 'low' ? 'green' : trace.risk.profile === 'medium' ? 'amber' : 'red',
    },
    {
      id: 'I',
      label: 'Intent',
      data: trace.intent,
      summary: `Primary: ${trace.intent.primary}`,
    },
    {
      id: 'A2',
      label: 'Awareness',
      data: trace.awareness,
      summary: `Coherence: ${Math.round(trace.awareness.coherence * 100)}%`,
    },
  ]

  return (
    <div className="bg-black/40 border border-white/10 rounded-lg p-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase tracking-wider text-white/60">
            MATRIZ Trace
          </span>
          <span className="text-[10px] text-white/40">
            Memory → Attention → Thought → Risk → Intent → Awareness
          </span>
        </div>
        <button
          onClick={copyTrace}
          className="flex items-center gap-1 text-xs text-white/60 hover:text-white/90 transition-colors px-2 py-1 rounded hover:bg-white/10"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              Copy Trace
            </>
          )}
        </button>
      </div>

      {/* Timeline */}
      <div className="flex items-center gap-1">
        {stageData.map((stage, index) => (
          <div key={stage.id} className="flex items-center">
            <StagePill
              stage={stage}
              isExpanded={expandedStage === stage.id}
              onClick={() => toggleStage(stage.id)}
            />
            {index < stageData.length - 1 && (
              <div className="w-2 h-0.5 bg-white/20 mx-0.5" />
            )}
          </div>
        ))}
      </div>

      {/* Expanded Details */}
      {expandedStage && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <StageDetails
            stage={stageData.find((s) => s.id === expandedStage)!}
          />
        </div>
      )}
    </div>
  )
}

interface StagePillProps {
  stage: {
    id: string
    label: string
    summary: string
    color?: string
  }
  isExpanded: boolean
  onClick: () => void
}

function StagePill({ stage, isExpanded, onClick }: StagePillProps) {
  const colorClass = stage.color === 'green' ? 'border-green-500/50 bg-green-500/10'
    : stage.color === 'amber' ? 'border-amber-500/50 bg-amber-500/10'
    : stage.color === 'red' ? 'border-red-500/50 bg-red-500/10'
    : 'border-violet-500/30 bg-violet-500/10'

  return (
    <button
      onClick={onClick}
      className={`group relative px-2.5 py-1.5 rounded-lg border transition-all hover:bg-white/10 ${colorClass} ${
        isExpanded ? 'ring-2 ring-violet-500/30' : ''
      }`}
      title={stage.summary}
    >
      <div className="flex items-center gap-1.5">
        <span className="text-sm font-medium text-white/90">{stage.id}</span>
        {isExpanded ? (
          <ChevronDown className="w-3 h-3 text-white/60" />
        ) : (
          <ChevronRight className="w-3 h-3 text-white/60 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
      </div>

      {/* Hover tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
        <div className="bg-black/95 border border-white/20 rounded px-2 py-1 text-xs text-white/90 whitespace-nowrap">
          {stage.label}: {stage.summary}
        </div>
      </div>
    </button>
  )
}

interface StageDetailsProps {
  stage: {
    id: string
    label: string
    data: any
  }
}

function StageDetails({ stage }: StageDetailsProps) {
  const renderData = (data: any): React.ReactNode => {
    if (Array.isArray(data)) {
      return (
        <ul className="list-disc list-inside space-y-1">
          {data.map((item, i) => (
            <li key={i} className="text-sm text-white/70">{item}</li>
          ))}
        </ul>
      )
    }

    if (typeof data === 'object' && data !== null) {
      return (
        <div className="space-y-2">
          {Object.entries(data).map(([key, value]) => (
            <div key={key}>
              <div className="text-xs text-white/60 uppercase tracking-wider mb-1">
                {key.replace(/_/g, ' ')}
              </div>
              <div className="pl-3">
                {typeof value === 'number' && value < 1
                  ? `${Math.round(value * 100)}%`
                  : Array.isArray(value)
                  ? value.length > 0
                    ? renderData(value)
                    : <span className="text-sm text-white/40 italic">None</span>
                  : typeof value === 'object'
                  ? renderData(value)
                  : <span className="text-sm text-white/80">{String(value)}</span>
                }
              </div>
            </div>
          ))}
        </div>
      )
    }

    return <span className="text-sm text-white/80">{String(data)}</span>
  }

  return (
    <div>
      <h4 className="text-xs font-medium text-white/70 mb-3 tracking-wider uppercase">
        {stage.label}
      </h4>
      {renderData(stage.data)}
    </div>
  )
}
