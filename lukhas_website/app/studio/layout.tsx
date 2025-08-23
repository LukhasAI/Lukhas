import dynamic from 'next/dynamic'
import type { Metadata } from 'next'

const NeuralBackground = dynamic(() => import('@/components/neural-background'), { ssr: false })

export const metadata: Metadata = {
  title: 'LUKHAS Studio — AI Development Environment',
  description: 'Professional AI development environment with multi-model orchestration, real-time collaboration, and advanced consciousness visualization.',
}

interface StudioLayoutProps {
  children: React.ReactNode
}

export default function StudioLayout({ children }: StudioLayoutProps) {
  const bgEnabled = process.env.NEXT_PUBLIC_BG_IN_STUDIO === 'true' // default off
  
  return (
    <div className="studio-environment min-h-screen bg-black text-white relative">
      {bgEnabled && <NeuralBackground mode="studio" />}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
}