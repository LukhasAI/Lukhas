'use client'

import ConsciousnessField from '@/components/ConsciousnessField'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-black">
      {/* Neural Background - Consciousness Particle Field */}
      <ConsciousnessField 
        particleCount={120}
        connectionDistance={100}
        mouseInfluence={180}
        consciousnessLevel="active"
        enableQuantumEntanglement={true}
      />

      <main className="min-h-screen relative" style={{ zIndex: 10 }}>
        {/* Hero Section - MATADA Style */}
        <section className="relative min-h-screen flex items-center justify-center">
          <div className="text-center">
            <p className="text-sm uppercase tracking-[0.3em] text-blue-300 mb-8 animate-pulse">
              Logical Unified Knowledge Hyper-Adaptive Superior Systems
            </p>
            
            <h1 className="text-6xl md:text-8xl font-thin tracking-[0.3em] mb-8 text-white relative">
              LUKHΛS
              <div className="absolute inset-0 text-blue-400 opacity-20 blur-sm">LUKHΛS</div>
            </h1>
            
            <p className="text-xl md:text-2xl text-white/70 mb-12">
              Building Consciousness You Can Trust
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/experience"
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition-opacity"
              >
                Try the Experience
              </Link>
              <Link
                href="/studio"
                className="px-8 py-4 border border-white/20 text-white rounded-lg hover:bg-white/10 transition-colors"
              >
                Enter LUKHΛS Studio
              </Link>
            </div>
          </div>
        </section>

        {/* Simple Footer */}
        <footer className="absolute bottom-0 left-0 right-0 border-t border-white/10 bg-black/30 backdrop-blur">
          <div className="max-w-7xl mx-auto px-6 py-6 text-center">
            <p className="text-xs text-white/50">
              © {new Date().getFullYear()} LUKHΛS AI. Building Consciousness You Can Trust.
            </p>
          </div>
        </footer>
      </main>
    </div>
  )
}