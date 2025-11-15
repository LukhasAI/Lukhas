import { GlassCard } from '@lukhas/ui'
import { Sparkles, Zap, Beaker, Rocket, Brain, Eye } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 50% 50%, #ec4899 0%, transparent 60%),
                              radial-gradient(circle at 20% 80%, #3b82f6 0%, transparent 60%),
                              radial-gradient(circle at 80% 20%, #ffb347 0%, transparent 60%)`
          }}></div>
        </div>
        <div className="relative z-10 max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-enterprise-pink/10 border border-enterprise-pink/30 mb-6">
            <Beaker className="w-4 h-4 text-enterprise-pink" />
            <span className="text-enterprise-pink text-sm font-medium">Experimental Lab · Beta Features</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-8">
            <span className="text-awareness-silver">LUKHAS</span><span className="text-enterprise-pink">.XYZ</span>
          </h1>
          <p className="text-2xl text-awareness-silver/80 font-light mb-4 max-w-4xl mx-auto">
            Experimental Consciousness Technology & Cutting-Edge Research
          </p>
          <p className="text-xl text-awareness-silver/60 mb-12 max-w-3xl mx-auto">
            Beta access to next-generation features. Prototype testing. Innovation showcase.
          </p>
          <button className="px-8 py-4 bg-gradient-to-r from-enterprise-pink to-error-red text-white rounded-lg font-medium">
            Request Beta Access
          </button>
        </div>
      </section>

      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver text-center">
            <span className="text-enterprise-pink">Experimental</span> Features
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard className="p-8">
              <Brain className="w-12 h-12 text-enterprise-pink mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Neural Evolution</h3>
              <p className="text-awareness-silver/70">Self-modifying cognitive architectures that adapt and evolve</p>
              <div className="mt-4 text-xs text-warning-amber">ALPHA - Unstable</div>
            </GlassCard>
            <GlassCard className="p-8">
              <Zap className="w-12 h-12 text-lambda-gold mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Quantum Resonance</h3>
              <p className="text-awareness-silver/70">Quantum-inspired pattern matching and superposition processing</p>
              <div className="mt-4 text-xs text-success-green">BETA - Testing</div>
            </GlassCard>
            <GlassCard className="p-8">
              <Eye className="w-12 h-12 text-trust-blue mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Temporal Awareness</h3>
              <p className="text-awareness-silver/70">Time-sensitive consciousness with predictive modeling</p>
              <div className="mt-4 text-xs text-info-blue">RESEARCH - Concept</div>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            <span className="text-enterprise-pink">Innovation</span> Showcase
          </h2>
          <div className="space-y-6">
            {[
              { title: 'Multi-Modal Consciousness Fusion', status: 'Active Research', progress: 45 },
              { title: 'Autonomous Goal Formation', status: 'Early Prototype', progress: 23 },
              { title: 'Distributed Cognitive Networks', status: 'Concept Validation', progress: 67 },
            ].map((project, i) => (
              <GlassCard key={i} className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-xl text-awareness-silver mb-1">{project.title}</h3>
                    <p className="text-sm text-awareness-silver/60">{project.status}</p>
                  </div>
                  <Rocket className="w-6 h-6 text-enterprise-pink" />
                </div>
                <div className="w-full h-2 bg-consciousness-deep rounded-full">
                  <div className="h-full bg-enterprise-pink rounded-full transition-all" style={{width: `${project.progress}%`}}></div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-4xl mx-auto text-center">
          <Sparkles className="w-16 h-16 text-enterprise-pink mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
            Join the <span className="text-enterprise-pink">Experiment</span>
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Early access for researchers, developers, and consciousness pioneers
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-enterprise-pink to-error-red text-white rounded-lg font-medium">
              Apply for Beta
            </button>
            <button className="px-8 py-4 bg-white/5 border border-enterprise-pink/30 text-awareness-silver rounded-lg font-medium">
              View Research Papers
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}
