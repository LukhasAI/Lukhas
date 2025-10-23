'use client'

import { useStateMachineActions } from '@/hooks/use-state-machine'

interface QuoteOptionsProps {
  onEnterStudio?: () => void
  onExploreWebsite?: () => void
}

export default function QuoteOptions({ onEnterStudio, onExploreWebsite }: QuoteOptionsProps) {
  const { transition } = useStateMachineActions()

  return (
    <div className="fixed bottom-32 left-1/2 transform -translate-x-1/2 z-30">
      <div className="flex flex-col sm:flex-row gap-4 items-center">
        <button
          onClick={() => {
            if (onEnterStudio) onEnterStudio()
            transition('ENTER_STUDIO')
          }}
          className="px-8 py-3 bg-gradient-to-r from-purple-600/80 to-blue-600/80 backdrop-blur-sm text-white rounded-lg hover:from-purple-600 hover:to-blue-600 transition-all duration-300 border border-white/10"
        >
          Enter Studio
        </button>
        
        <button
          onClick={() => {
            if (onExploreWebsite) onExploreWebsite()
            transition('MARKETING_COMPLETE')
          }}
          className="px-8 py-3 bg-black/20 backdrop-blur-sm text-white rounded-lg hover:bg-black/30 transition-all duration-300 border border-white/20"
        >
          Explore Lukhas
        </button>
      </div>
      
      <div className="text-center mt-4">
        <p className="text-xs text-white/40 font-light tracking-wide">
          Choose your journey
        </p>
      </div>
    </div>
  )
}