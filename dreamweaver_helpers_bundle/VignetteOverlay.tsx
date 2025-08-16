import * as React from 'react'

type Phase = 'seed'|'awakening'|'exploration'|'creation'|'resonance'|'integration'|'crystallization'
type Props = {
  intensity?: number
  phase?: Phase
  mapping?: Partial<Record<Phase, number>>
  respectReduceMotion?: boolean
  className?: string
}

/** VignetteOverlay — CSS vignette/focus overlay (fallback if shaders are off). */
export const VignetteOverlay: React.FC<Props> = ({
  intensity,
  phase,
  mapping,
  respectReduceMotion = true,
  className
}) => {
  const [reduce, setReduce] = React.useState(false)
  React.useEffect(() => {
    if (!respectReduceMotion) return
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const set = () => setReduce(!!mq.matches)
    set()
    mq.addEventListener?.('change', set)
    return () => mq.removeEventListener?.('change', set)
  }, [respectReduceMotion])

  const resolved = (() => {
    const byPhase = phase && mapping ? mapping[phase] : undefined
    const base = intensity ?? byPhase ?? 0.1
    return reduce ? Math.min(base, 0.06) : base
  })()

  const style: React.CSSProperties = {
    // @ts-ignore
    '--dw-vignette': String(resolved),
    pointerEvents: 'none',
    position: 'fixed',
    inset: 0,
    zIndex: 10
  }

  return (
    <div
      aria-hidden="true"
      className={['dw-vignette-overlay', className].filter(Boolean).join(' ')}
      style={style}
    />
  )
}

export default VignetteOverlay
