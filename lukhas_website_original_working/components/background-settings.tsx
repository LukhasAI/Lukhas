'use client'

import { useState, useEffect } from 'react'
import { Cog6ToothIcon } from '@heroicons/react/24/outline'

interface BackgroundSettingsProps {
  className?: string
}

export default function BackgroundSettings({ className = '' }: BackgroundSettingsProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [settings, setSettings] = useState({
    enabled: true,
    intensity: 'normal' as 'low' | 'normal' | 'high',
    mode: 'auto' as 'auto' | 'landing' | 'studio' | 'off'
  })

  // Load settings from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('lukhas_background_settings')
    if (stored) {
      try {
        setSettings({ ...settings, ...JSON.parse(stored) })
      } catch (e) {
        console.warn('Failed to parse background settings:', e)
      }
    }
  }, [])

  // Save settings to localStorage
  const updateSettings = (newSettings: typeof settings) => {
    setSettings(newSettings)
    localStorage.setItem('lukhas_background_settings', JSON.stringify(newSettings))
    
    // Emit custom event for live background updates
    window.dispatchEvent(new CustomEvent('lukhas:background:settings', {
      detail: newSettings
    }))
  }

  const handleToggle = () => {
    updateSettings({ ...settings, enabled: !settings.enabled })
  }

  const handleIntensityChange = (intensity: typeof settings.intensity) => {
    updateSettings({ ...settings, intensity })
  }

  const handleModeChange = (mode: typeof settings.mode) => {
    updateSettings({ ...settings, mode })
  }

  return (
    <div className={`relative ${className}`}>
      {/* Settings Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
        title="Background Settings"
      >
        <Cog6ToothIcon className="w-5 h-5 text-white/60" />
      </button>

      {/* Settings Panel */}
      {isOpen && (
        <div className="absolute top-12 right-0 w-80 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl p-6 z-50">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-light">Visual Settings</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/60 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Enable/Disable Toggle */}
            <div className="flex items-center justify-between">
              <label className="text-sm text-white/80">Neural Background</label>
              <button
                onClick={handleToggle}
                className={`relative w-8 h-4 rounded-full transition-all duration-200 ${
                  settings.enabled 
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 shadow-lg shadow-blue-500/25' 
                    : 'bg-white/10 hover:bg-white/15'
                }`}
                title={settings.enabled ? 'Disable background' : 'Enable background'}
              >
                <div
                  className={`absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all duration-200 ${
                    settings.enabled 
                      ? 'translate-x-4 shadow-sm' 
                      : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>

            {/* Intensity Control */}
            <div className="space-y-3">
              <label className="text-sm text-white/80">Intensity</label>
              <div className="flex gap-2">
                {(['low', 'normal', 'high'] as const).map((level) => (
                  <button
                    key={level}
                    onClick={() => handleIntensityChange(level)}
                    className={`px-3 py-2 rounded-lg text-xs transition-colors ${
                      settings.intensity === level
                        ? 'bg-blue-600 text-white'
                        : 'bg-white/10 text-white/60 hover:bg-white/20'
                    }`}
                  >
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Mode Control */}
            <div className="space-y-3">
              <label className="text-sm text-white/80">Mode</label>
              <div className="grid grid-cols-2 gap-2">
                {(['auto', 'landing', 'studio', 'off'] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => handleModeChange(mode)}
                    className={`px-3 py-2 rounded-lg text-xs transition-colors ${
                      settings.mode === mode
                        ? 'bg-blue-600 text-white'
                        : 'bg-white/10 text-white/60 hover:bg-white/20'
                    }`}
                  >
                    {mode.charAt(0).toUpperCase() + mode.slice(1)}
                  </button>
                ))}
              </div>
              <p className="text-xs text-white/40">
                Auto: Landing mode on home, Studio mode in /studio, Off: Disabled everywhere
              </p>
            </div>

            {/* Performance Info */}
            <div className="pt-4 border-t border-white/10">
              <div className="text-xs text-white/40 space-y-1">
                <div>• Respects prefers-reduced-motion</div>
                <div>• Auto-disables on low-power devices</div>
                <div>• Uses hardware acceleration when available</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Backdrop to close panel */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}