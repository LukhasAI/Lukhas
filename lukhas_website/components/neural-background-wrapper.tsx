'use client'

import dynamic from 'next/dynamic'

const NeuralBackground = dynamic(() => import('@/components/neural-background'), { ssr: false })

type Mode = "landing" | "studio"

interface NeuralBackgroundWrapperProps {
  mode?: Mode
}

export default function NeuralBackgroundWrapper({ mode = 'landing' }: NeuralBackgroundWrapperProps) {
  return <NeuralBackground mode={mode} />
}
