import { GlassCard } from '@lukhas/ui'
import { Shield, Globe, Lock, CheckCircle, FileText, Users } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      <section className="py-24 px-6 relative">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-trust-blue/10 border border-trust-blue/30 mb-6">
            <Shield className="w-4 h-4 text-trust-blue" />
            <span className="text-trust-blue text-sm font-medium">GDPR Compliant · EU Data Residency</span>
          </div>
          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-8">
            <span className="text-awareness-silver">LUKHAS</span><span className="text-trust-blue">.EU</span>
          </h1>
          <p className="text-2xl text-awareness-silver/80 font-light mb-4 max-w-4xl mx-auto">
            European Privacy & GDPR Compliance for Consciousness Technology
          </p>
          <p className="text-xl text-awareness-silver/60 mb-12 max-w-3xl mx-auto">
            Privacy-first infrastructure with EU data residency, regulatory alignment, and transparent data governance.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-8 text-awareness-silver text-center">
            <span className="text-trust-blue">European</span> Data Protection
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard className="p-8">
              <Globe className="w-12 h-12 text-trust-blue mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">EU Data Residency</h3>
              <p className="text-awareness-silver/70">All data stored exclusively in EU datacenters. Never leaves European jurisdiction.</p>
            </GlassCard>
            <GlassCard className="p-8">
              <Shield className="w-12 h-12 text-success-green mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">GDPR Compliant</h3>
              <p className="text-awareness-silver/70">Full compliance with EU data protection regulations and privacy rights.</p>
            </GlassCard>
            <GlassCard className="p-8">
              <Lock className="w-12 h-12 text-enterprise-pink mb-4" />
              <h3 className="text-xl font-light text-awareness-silver mb-3">Privacy by Design</h3>
              <p className="text-awareness-silver/70">Architecture built from ground up with European privacy principles.</p>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            <span className="text-trust-blue">User Rights</span> & Protections
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { title: 'Right to Access', desc: 'Full transparency on data collected and processed' },
              { title: 'Right to Rectification', desc: 'Correct inaccurate personal data instantly' },
              { title: 'Right to Erasure', desc: 'Delete your data permanently with one click' },
              { title: 'Right to Portability', desc: 'Export your data in machine-readable format' },
              { title: 'Right to Object', desc: 'Opt out of processing for specific purposes' },
              { title: 'Right to be Informed', desc: 'Clear information on data usage and sharing' }
            ].map((right, i) => (
              <GlassCard key={i} className="p-6">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-success-green flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg text-awareness-silver mb-2">{right.title}</h3>
                    <p className="text-awareness-silver/70 text-sm">{right.desc}</p>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-4xl mx-auto text-center">
          <FileText className="w-16 h-16 text-trust-blue mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
            Regulatory <span className="text-trust-blue">Compliance</span>
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8 max-w-2xl mx-auto">
            Full documentation, Data Processing Agreements (DPAs), and compliance certificates available
          </p>
          <button className="px-8 py-4 bg-gradient-to-r from-trust-blue to-info-blue text-white rounded-lg font-medium hover:shadow-lg transition-all">
            Download Compliance Pack
          </button>
        </div>
      </section>
    </div>
  )
}
