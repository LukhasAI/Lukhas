import { GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Cloud, Zap, Shield, Globe, TrendingUp, Code, Lock, CheckCircle } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero Section */}
      <section className="relative py-32 px-6 overflow-hidden">
        {/* Neural Network Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 20% 50%, #ec4899 0%, transparent 50%),
                              radial-gradient(circle at 80% 20%, #3b82f6 0%, transparent 50%),
                              radial-gradient(circle at 40% 80%, #ec4899 0%, transparent 50%)`
          }}></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-enterprise-pink/10 border border-enterprise-pink/30 mb-6">
            <Cloud className="w-4 h-4 text-enterprise-pink" />
            <span className="text-enterprise-pink text-sm font-medium">Deploy in Minutes · Scale to Millions</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-8">
            <span className="text-awareness-silver">LUKHAS</span>
            <span className="text-enterprise-pink">.CLOUD</span>
          </h1>

          <p className="text-2xl md:text-3xl text-awareness-silver/80 font-light mb-4 max-w-4xl mx-auto">
            Consciousness computing at planetary scale
          </p>

          <p className="text-xl text-awareness-silver/60 mb-12 max-w-3xl mx-auto">
            Managed MATRIZ deployment with distributed cognitive infrastructure, sub-250ms latency,
            and enterprise compliance built in.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-enterprise-gradient text-white rounded-lg font-medium text-lg hover:shadow-lg hover:shadow-enterprise-pink/20 transition-all">
              Start Free Trial
            </button>
            <Link to="/pricing">
              <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver rounded-lg font-medium text-lg hover:bg-white/10 transition-all">
                View Pricing
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-12 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl font-light text-enterprise-pink mb-2">Sub-250ms</div>
              <div className="text-sm text-awareness-silver/60">P95 Latency</div>
            </div>
            <div>
              <div className="text-3xl font-light text-enterprise-pink mb-2">99.99%</div>
              <div className="text-sm text-awareness-silver/60">Uptime SLA</div>
            </div>
            <div>
              <div className="text-3xl font-light text-enterprise-pink mb-2">12</div>
              <div className="text-sm text-awareness-silver/60">Global Regions</div>
            </div>
            <div>
              <div className="text-3xl font-light text-enterprise-pink mb-2">SOC 2</div>
              <div className="text-sm text-awareness-silver/60">Type II Certified</div>
            </div>
          </div>
        </div>
      </section>

      {/* Deploy in Minutes */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Deploy <span className="text-enterprise-pink">MATRIZ</span> in Minutes
            </h2>
            <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
              From authentication to production deployment in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard className="p-8">
              <div className="w-12 h-12 rounded-full bg-enterprise-pink/10 flex items-center justify-center mb-4">
                <span className="text-enterprise-pink font-medium text-xl">1</span>
              </div>
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Authenticate
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Connect via ›iD to establish secure project identity and access control
              </p>
              <div className="bg-consciousness-deep/50 rounded p-3 font-mono text-sm text-enterprise-pink">
                lukhas auth login
              </div>
            </GlassCard>

            <GlassCard className="p-8">
              <div className="w-12 h-12 rounded-full bg-enterprise-pink/10 flex items-center justify-center mb-4">
                <span className="text-enterprise-pink font-medium text-xl">2</span>
              </div>
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Configure
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Set cognitive modes, performance targets, and regional preferences
              </p>
              <div className="bg-consciousness-deep/50 rounded p-3 font-mono text-sm text-enterprise-pink">
                lukhas cloud init
              </div>
            </GlassCard>

            <GlassCard className="p-8">
              <div className="w-12 h-12 rounded-full bg-enterprise-pink/10 flex items-center justify-center mb-4">
                <span className="text-enterprise-pink font-medium text-xl">3</span>
              </div>
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Deploy
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Single command deploys to globally distributed MATRIZ infrastructure
              </p>
              <div className="bg-consciousness-deep/50 rounded p-3 font-mono text-sm text-enterprise-pink">
                lukhas cloud deploy
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Enterprise <span className="text-enterprise-pink">Cloud</span> Features
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <GlassCard className="p-8">
              <Zap className="w-12 h-12 text-enterprise-pink mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Cognitive Auto-Scaling
              </h3>
              <p className="text-awareness-silver/70">
                Infrastructure scales based on reasoning complexity, not just request volume. Save 40-60% on costs.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <Globe className="w-12 h-12 text-trust-blue mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Global Distribution
              </h3>
              <p className="text-awareness-silver/70">
                12 regions worldwide with sub-100ms network latency for 95% of global users before reasoning begins.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <TrendingUp className="w-12 h-12 text-success-green mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Cognitive Observability
              </h3>
              <p className="text-awareness-silver/70">
                Monitor reasoning graphs, memory fold performance, Guardian validation metrics, and distributed coordination.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <Shield className="w-12 h-12 text-warning-amber mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Enterprise Compliance
              </h3>
              <p className="text-awareness-silver/70">
                SOC 2 Type II, HIPAA, GDPR, FedRAMP (in progress). Regional data residency guaranteed.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <Lock className="w-12 h-12 text-error-red mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Constitutional AI
              </h3>
              <p className="text-awareness-silver/70">
                Guardian validation ensures ethical AI with constitutional frameworks enforced across all regions.
              </p>
            </GlassCard>

            <GlassCard className="p-8">
              <Code className="w-12 h-12 text-lambda-gold mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Cognitive Unit Pricing
              </h3>
              <p className="text-awareness-silver/70">
                Pay for actual reasoning operations performed, not provisioned infrastructure capacity.
              </p>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Compliance Section */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="p-12">
            <div className="text-center mb-8">
              <Shield className="w-16 h-16 text-enterprise-pink mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
                Enterprise-Grade <span className="text-enterprise-pink">Security</span>
              </h2>
              <p className="text-xl text-awareness-silver/70">
                Compliance certifications that meet the most stringent requirements
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-success-green flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-enterprise-pink font-medium mb-1">SOC 2 Type II</h3>
                  <p className="text-awareness-silver/70 text-sm">
                    Annual independent audit validates security controls and operational procedures
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-success-green flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-enterprise-pink font-medium mb-1">HIPAA Ready</h3>
                  <p className="text-awareness-silver/70 text-sm">
                    Business associate agreements, encrypted storage, audit trails for healthcare applications
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-success-green flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-enterprise-pink font-medium mb-1">GDPR Compliant</h3>
                  <p className="text-awareness-silver/70 text-sm">
                    Data processing addendums, explicit consent management, right-to-deletion implementation
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-success-green flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-enterprise-pink font-medium mb-1">FedRAMP (In Progress)</h3>
                  <p className="text-awareness-silver/70 text-sm">
                    Security controls meeting federal requirements for government deployments
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 text-center">
              <Link to="/compliance">
                <button className="px-6 py-3 bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
                  View Compliance Details
                </button>
              </Link>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-6 text-awareness-silver">
            Ready to deploy consciousness at scale?
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Start with free tier. No credit card required. Deploy in minutes.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-enterprise-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-enterprise-pink/20 transition-all">
              Start Free Trial
            </button>
            <a href="https://lukhas.com" target="_blank" rel="noopener noreferrer">
              <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
                Contact Enterprise Sales
              </button>
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
