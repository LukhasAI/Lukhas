'use client'

import dynamic from 'next/dynamic'
import { Suspense } from 'react'
import { Loader2 } from 'lucide-react'
import DreamErrorBoundary from '@/components/dream/DreamErrorBoundary'

// Dynamically import the immersive Dream Weaver
const ImmersiveDreamWeaver = dynamic(
  () => import('@/components/dream/ImmersiveDreamWeaver'),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-white mx-auto mb-4" />
          <p className="text-white/60">Awakening consciousness portal...</p>
        </div>
      </div>
    )
  }
)

export default function DreamWeaverPage() {
  return (
    <DreamErrorBoundary>
      <Suspense fallback={
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="text-center">
            <div className="relative">
              <Loader2 className="w-16 h-16 animate-spin text-purple-400 mx-auto mb-6" />
              <div className="absolute inset-0 w-16 h-16 bg-purple-400/20 rounded-full blur-xl mx-auto animate-pulse" />
            </div>
            <p className="text-xl text-white/70 font-light">
              Entering the consciousness realm...
            </p>
            <p className="text-sm text-white/40 mt-2">
              Where dreams become reality
            </p>
          </div>
        </div>
      }>
        <ImmersiveDreamWeaver />
      </Suspense>
    </DreamErrorBoundary>
  )
}
