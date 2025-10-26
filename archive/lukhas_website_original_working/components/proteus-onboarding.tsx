'use client'

import { useState } from 'react'
import { ChevronRight, Mic, MousePointer, Sparkles, Brain, Settings } from 'lucide-react'

interface ProteusOnboardingProps {
  onComplete: () => void
  isFirstVisit?: boolean
}

const steps = [
  {
    icon: Brain,
    title: 'Welcome to PR0T3US',
    description: 'Experience LUKHAS AI consciousness visualization through voice-reactive 3D morphing shapes.',
    content: (
      <div className="space-y-4">
        <p className="text-gray-300">
          PR0T3US transforms your voice and emotions into living, breathing geometric forms that respond in real-time.
        </p>
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-lg p-4 border border-purple-500/20">
          <p className="text-sm text-purple-300">
            This experience combines quantum-inspired processing with bio-adaptive algorithms to create a unique consciousness interface.
          </p>
        </div>
      </div>
    ),
  },
  {
    icon: Mic,
    title: 'Enable Your Microphone',
    description: 'Allow microphone access to enable voice-reactive features.',
    content: (
      <div className="space-y-4">
        <p className="text-gray-300">
          Click the microphone button in the top bar to enable voice input. Your browser will ask for permission.
        </p>
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <p className="text-sm text-gray-400 mb-3">Try these voice commands:</p>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">•</span>
              <span>"Show me consciousness" - Activates neural pattern visualization</span>
            </li>
            <li className="flex items-start">
              <span className="text-purple-400 mr-2">•</span>
              <span>"Transform to cube" - Morphs particles into geometric shapes</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-400 mr-2">•</span>
              <span>"Increase energy" - Amplifies particle movement and colors</span>
            </li>
          </ul>
        </div>
      </div>
    ),
  },
  {
    icon: MousePointer,
    title: 'Interactive Controls',
    description: 'Use your mouse to navigate and interact with the 3D space.',
    content: (
      <div className="space-y-4">
        <p className="text-gray-300">
          The visualization responds to both voice and mouse interactions.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="bg-white/5 rounded-lg p-3 border border-white/10">
            <p className="text-sm font-medium text-blue-400 mb-1">Left Click + Drag</p>
            <p className="text-xs text-gray-400">Rotate the 3D view</p>
          </div>
          <div className="bg-white/5 rounded-lg p-3 border border-white/10">
            <p className="text-sm font-medium text-purple-400 mb-1">Right Click + Drag</p>
            <p className="text-xs text-gray-400">Pan the camera</p>
          </div>
          <div className="bg-white/5 rounded-lg p-3 border border-white/10">
            <p className="text-sm font-medium text-green-400 mb-1">Scroll</p>
            <p className="text-xs text-gray-400">Zoom in/out</p>
          </div>
          <div className="bg-white/5 rounded-lg p-3 border border-white/10">
            <p className="text-sm font-medium text-orange-400 mb-1">Double Click</p>
            <p className="text-xs text-gray-400">Reset view</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    icon: Sparkles,
    title: 'Consciousness States',
    description: 'Watch how shapes respond to different emotional and cognitive states.',
    content: (
      <div className="space-y-4">
        <p className="text-gray-300">
          The system analyzes voice tone, pitch, and emotion to create unique visual patterns.
        </p>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-blue-400 animate-pulse" />
            <div>
              <p className="text-sm font-medium">Calm State</p>
              <p className="text-xs text-gray-400">Smooth, flowing particles in cool colors</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-purple-400 animate-pulse" />
            <div>
              <p className="text-sm font-medium">Focused State</p>
              <p className="text-xs text-gray-400">Organized geometric patterns</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-orange-400 animate-pulse" />
            <div>
              <p className="text-sm font-medium">Energetic State</p>
              <p className="text-xs text-gray-400">Rapid movement with warm colors</p>
            </div>
          </div>
        </div>
      </div>
    ),
  },
  {
    icon: Settings,
    title: 'Customize Your Experience',
    description: 'Configure API connections and visualization settings.',
    content: (
      <div className="space-y-4">
        <p className="text-gray-300">
          Click the settings icon to configure AI providers and adjust visualization parameters.
        </p>
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-lg p-4 border border-purple-500/20">
          <p className="text-sm text-purple-300 mb-3">Available Integrations:</p>
          <div className="grid grid-cols-2 gap-2">
            <span className="text-xs bg-black/30 rounded px-2 py-1">OpenAI GPT-4</span>
            <span className="text-xs bg-black/30 rounded px-2 py-1">Anthropic Claude</span>
            <span className="text-xs bg-black/30 rounded px-2 py-1">Google Gemini</span>
            <span className="text-xs bg-black/30 rounded px-2 py-1">Local Models</span>
          </div>
        </div>
        <p className="text-xs text-gray-400">
          Your settings are saved locally and persist between sessions.
        </p>
      </div>
    ),
  },
]

export default function ProteusOnboarding({ onComplete, isFirstVisit = true }: ProteusOnboardingProps) {
  const [currentStep, setCurrentStep] = useState(0)

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      onComplete()
    }
  }

  const handleSkip = () => {
    onComplete()
  }

  const step = steps[currentStep]
  const Icon = step.icon

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div 
        className="absolute inset-0 bg-black/90 backdrop-blur-md"
        onClick={handleSkip}
      />
      
      <div className="relative bg-gray-900 border border-white/10 rounded-2xl w-full max-w-2xl">
        {/* Progress bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-white/10 rounded-t-2xl overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-purple-600 to-blue-600 transition-all duration-300"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
        
        {/* Content */}
        <div className="p-8 pt-10">
          {/* Header */}
          <div className="flex items-center space-x-4 mb-6">
            <div className="p-3 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-xl border border-purple-500/20">
              <Icon className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-light">{step.title}</h2>
              <p className="text-sm text-gray-400 mt-1">{step.description}</p>
            </div>
          </div>
          
          {/* Step content */}
          <div className="mb-8">
            {step.content}
          </div>
          
          {/* Step indicator */}
          <div className="flex items-center justify-center space-x-2 mb-6">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`h-1.5 rounded-full transition-all ${
                  index === currentStep
                    ? 'w-8 bg-gradient-to-r from-purple-600 to-blue-600'
                    : index < currentStep
                    ? 'w-1.5 bg-blue-400'
                    : 'w-1.5 bg-white/20'
                }`}
              />
            ))}
          </div>
          
          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={handleSkip}
              className="text-gray-400 hover:text-white transition"
            >
              {isFirstVisit ? 'Skip tutorial' : 'Close'}
            </button>
            
            <button
              onClick={handleNext}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition flex items-center space-x-2"
            >
              <span>{currentStep === steps.length - 1 ? 'Get Started' : 'Next'}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}