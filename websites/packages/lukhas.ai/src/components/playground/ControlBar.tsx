import { useState } from 'react'
import { usePlaygroundStore } from '../../stores/playgroundStore'
import { Button } from '@lukhas/ui'

export default function ControlBar() {
  const settings = usePlaygroundStore((state) => state.settings)
  const updateSettings = usePlaygroundStore((state) => state.updateSettings)

  const getRiskLabel = (value: number): string => {
    if (value <= 33) return 'Safe'
    if (value <= 66) return 'Balanced'
    return 'Experimental'
  }

  const getRiskColor = (value: number): string => {
    if (value <= 33) return 'text-green-400'
    if (value <= 66) return 'text-yellow-400'
    return 'text-orange-400'
  }

  return (
    <div className="border-b border-white/10 bg-black/40 backdrop-blur-md p-4">
      <div className="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Left: View Mode Toggle */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/60 uppercase tracking-wider">View</span>
          <div className="flex bg-white/5 border border-white/10 rounded-lg overflow-hidden">
            <button
              onClick={() => updateSettings({ viewMode: 'play' })}
              className={`px-4 py-2 text-sm transition-all ${
                settings.viewMode === 'play'
                  ? 'bg-violet-500/30 text-violet-300 border-r border-violet-500/50'
                  : 'text-white/60 hover:bg-white/5 border-r border-white/10'
              }`}
            >
              Play
            </button>
            <button
              onClick={() => updateSettings({ viewMode: 'lab' })}
              className={`px-4 py-2 text-sm transition-all ${
                settings.viewMode === 'lab'
                  ? 'bg-violet-500/30 text-violet-300'
                  : 'text-white/60 hover:bg-white/5'
              }`}
            >
              Lab
            </button>
          </div>
        </div>

        {/* Center: Risk Slider */}
        <div className="flex-1 min-w-[250px] max-w-md">
          <div className="flex items-center gap-3">
            <span className="text-xs text-white/60 uppercase tracking-wider whitespace-nowrap">
              Risk Profile
            </span>
            <div className="flex-1">
              <input
                type="range"
                min="0"
                max="100"
                value={settings.riskProfile}
                onChange={(e) => updateSettings({ riskProfile: parseInt(e.target.value) })}
                className="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-violet-400 [&::-webkit-slider-thumb]:cursor-pointer [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-violet-400 [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:cursor-pointer"
              />
              <div className="flex justify-between mt-1 text-[10px]">
                <span className={settings.riskProfile <= 33 ? getRiskColor(settings.riskProfile) : 'text-white/40'}>
                  Safe
                </span>
                <span className={settings.riskProfile > 33 && settings.riskProfile <= 66 ? getRiskColor(settings.riskProfile) : 'text-white/40'}>
                  Balanced
                </span>
                <span className={settings.riskProfile > 66 ? getRiskColor(settings.riskProfile) : 'text-white/40'}>
                  Experimental
                </span>
              </div>
            </div>
            <span className={`text-sm font-medium min-w-[100px] text-right ${getRiskColor(settings.riskProfile)}`}>
              {getRiskLabel(settings.riskProfile)}
            </span>
          </div>
        </div>

        {/* Right: Engine Display (read-only) */}
        <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-lg px-4 py-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-white/80">
            Engine: <span className="text-violet-400 font-medium">Azure GPT</span>
          </span>
          <span className="text-xs text-white/40">via LUKHΛS Brain</span>
        </div>
      </div>
    </div>
  )
}
