'use client'

import { useState } from 'react'
import { InformationCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface EssentialModeBannerProps {
  onChangePreferences: () => void
}

export default function EssentialModeBanner({ onChangePreferences }: EssentialModeBannerProps) {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-30 bg-amber-900/20 backdrop-blur-sm border-b border-amber-500/20">
      <div className="max-w-7xl mx-auto px-4 py-2">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-3">
            <InformationCircleIcon className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <p className="text-amber-100">
              Limited experience (essential cookies only) • Some features may be unavailable
            </p>
            <button
              onClick={onChangePreferences}
              className="text-amber-300 hover:text-amber-200 underline underline-offset-2 transition-colors"
            >
              Change preferences
            </button>
          </div>
          <button
            onClick={() => setIsVisible(false)}
            className="text-amber-300 hover:text-amber-200 transition-colors ml-4"
            title="Dismiss notification"
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}