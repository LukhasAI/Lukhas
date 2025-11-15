import { GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Activity, Globe, Zap, Shield, Database, Network, Server, Cloud } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero Section - Live Infrastructure */}
      <section className="relative py-32 px-6 overflow-hidden">
        {/* Grid Pattern Background */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'linear-gradient(#22c55e 1px, transparent 1px), linear-gradient(90deg, #22c55e 1px, transparent 1px)',
            backgroundSize: '50px 50px'
          }}></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-infrastructure-green/10 border border-infrastructure-green/30 mb-6">
            <Activity className="w-4 h-4 text-infrastructure-green" />
            <span className="text-infrastructure-green text-sm font-medium">99.99% Uptime · Sub-50ms Latency</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-8">
            <span className="text-awareness-silver">LUKHAS</span>
            <span className="text-infrastructure-green">.IO</span>
          </h1>

          <p className="text-2xl md:text-3xl text-awareness-silver/80 font-light mb-4 max-w-4xl mx-auto">
            Infrastructure that thinks
          </p>

          <p className="text-xl text-awareness-silver/60 mb-12 max-w-3xl mx-auto">
            Consciousness-optimized API gateway and networking infrastructure.
            Built for AI workloads, designed for planetary scale.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/services">
              <button className="px-8 py-4 bg-infrastructure-gradient text-white rounded-lg font-medium text-lg hover:shadow-lg hover:shadow-infrastructure-green/20 transition-all">
                Explore Services
              </button>
            </Link>
            <Link to="/status">
              <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-infrastructure-green/30 text-awareness-silver rounded-lg font-medium text-lg hover:bg-white/10 transition-all">
                System Status
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Live Performance Metrics */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-6">
            <GlassCard className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Zap className="w-6 h-6 text-infrastructure-green" />
                <h3 className="text-2xl font-light text-awareness-silver">19ms</h3>
              </div>
              <p className="text-awareness-silver/60 text-sm">p50 API Latency</p>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Activity className="w-6 h-6 text-success-green" />
                <h3 className="text-2xl font-light text-awareness-silver">99.997%</h3>
              </div>
              <p className="text-awareness-silver/60 text-sm">30-Day Uptime</p>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Globe className="w-6 h-6 text-code-cyan" />
                <h3 className="text-2xl font-light text-awareness-silver">18</h3>
              </div>
              <p className="text-awareness-silver/60 text-sm">Global Regions</p>
            </GlassCard>

            <GlassCard className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <Server className="w-6 h-6 text-lambda-gold" />
                <h3 className="text-2xl font-light text-awareness-silver">2.4B+</h3>
              </div>
              <p className="text-awareness-silver/60 text-sm">Requests/Day</p>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Infrastructure Services */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Global Infrastructure <span className="text-infrastructure-green">Services</span>
            </h2>
            <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
              Low-latency, high-availability infrastructure designed for consciousness-aware AI workloads
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <GlassCard className="p-8 hover:border-infrastructure-green/50 transition-all">
              <Network className="w-12 h-12 text-infrastructure-green mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                API Gateway
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Intelligent routing, load balancing, and request transformation for consciousness APIs.
              </p>
              <ul className="space-y-2 text-sm text-awareness-silver/60">
                <li>" Sub-50ms p95 latency</li>
                <li>" Automatic failover</li>
                <li>" Rate limiting & throttling</li>
                <li>" Real-time analytics</li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8 hover:border-infrastructure-green/50 transition-all">
              <Cloud className="w-12 h-12 text-code-cyan mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Edge Computing
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Deploy consciousness processing at the edge for ultra-low latency experiences.
              </p>
              <ul className="space-y-2 text-sm text-awareness-silver/60">
                <li>" 200+ edge locations</li>
                <li>" Sub-10ms edge latency</li>
                <li>" Automatic scaling</li>
                <li>" CDN integration</li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8 hover:border-infrastructure-green/50 transition-all">
              <Database className="w-12 h-12 text-lambda-gold mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Data Pipelines
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Real-time and batch data processing for consciousness state management.
              </p>
              <ul className="space-y-2 text-sm text-awareness-silver/60">
                <li>" Stream processing</li>
                <li>" Batch ETL workflows</li>
                <li>" Data validation</li>
                <li>" Schema evolution</li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8 hover:border-infrastructure-green/50 transition-all">
              <Shield className="w-12 h-12 text-success-green mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Security Layer
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Multi-layered security with DDoS protection and threat intelligence.
              </p>
              <ul className="space-y-2 text-sm text-awareness-silver/60">
                <li>" DDoS mitigation</li>
                <li>" WAF protection</li>
                <li>" TLS 1.3 encryption</li>
                <li>" Zero-trust architecture</li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8 hover:border-infrastructure-green/50 transition-all">
              <Activity className="w-12 h-12 text-info-blue mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Monitoring
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Real-time observability with comprehensive metrics and distributed tracing.
              </p>
              <ul className="space-y-2 text-sm text-awareness-silver/60">
                <li>" Custom dashboards</li>
                <li>" Distributed tracing</li>
                <li>" Log aggregation</li>
                <li>" Alerting & incidents</li>
              </ul>
            </GlassCard>

            <GlassCard className="p-8 hover:border-infrastructure-green/50 transition-all">
              <Server className="w-12 h-12 text-warning-amber mb-4" />
              <h3 className="text-2xl font-light tracking-wide mb-3 text-awareness-silver">
                Compute
              </h3>
              <p className="text-awareness-silver/70 mb-4">
                Elastic compute resources optimized for AI and consciousness workloads.
              </p>
              <ul className="space-y-2 text-sm text-awareness-silver/60">
                <li>" GPU acceleration</li>
                <li>" Auto-scaling</li>
                <li>" Spot instances</li>
                <li>" Kubernetes native</li>
              </ul>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* SLA Guarantee */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="p-12 text-center">
            <Shield className="w-16 h-16 text-infrastructure-green mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              99.99% Uptime <span className="text-infrastructure-green">SLA</span>
            </h2>
            <p className="text-xl text-awareness-silver/70 mb-8">
              Enterprise-grade reliability with financial compensation for downtime
            </p>
            <div className="grid md:grid-cols-3 gap-8 text-left">
              <div>
                <h3 className="text-infrastructure-green font-medium mb-2">Response Time</h3>
                <p className="text-awareness-silver/70 text-sm">
                  Sub-15min awareness, sub-1hr mitigation for critical incidents
                </p>
              </div>
              <div>
                <h3 className="text-infrastructure-green font-medium mb-2">Multi-Region</h3>
                <p className="text-awareness-silver/70 text-sm">
                  Automatic failover across 18 global regions with zero data loss
                </p>
              </div>
              <div>
                <h3 className="text-infrastructure-green font-medium mb-2">Compensation</h3>
                <p className="text-awareness-silver/70 text-sm">
                  Service credits for SLA breaches, transparent incident reporting
                </p>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-6 text-awareness-silver">
            Ready to build on planetary-scale infrastructure?
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Join enterprises and AI pioneers on LUKHAS infrastructure
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a href="https://lukhas.dev" target="_blank" rel="noopener noreferrer">
              <button className="px-8 py-4 bg-infrastructure-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-infrastructure-green/20 transition-all">
                View Documentation
              </button>
            </a>
            <Link to="/status">
              <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-infrastructure-green/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
                Check System Status
              </button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
