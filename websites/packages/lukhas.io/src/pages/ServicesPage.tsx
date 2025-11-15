import { GlassCard } from '@lukhas/ui'
import { Network, Cloud, Database, Shield, Activity, Server, Code, Boxes } from 'lucide-react'

export default function ServicesPage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Infrastructure <span className="text-infrastructure-green">Services</span>
          </h1>
          <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
            Comprehensive cloud-native infrastructure for consciousness-aware AI applications
          </p>
        </div>
      </section>

      {/* API Gateway Service */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <GlassCard className="p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <Network className="w-16 h-16 text-infrastructure-green mb-6" />
                <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
                  API Gateway
                </h2>
                <p className="text-lg text-awareness-silver/70 mb-6">
                  Intelligent request routing and load balancing with consciousness-optimized paths.
                  Handle millions of requests with sub-50ms latency.
                </p>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-infrastructure-green font-medium mb-2">Features</h3>
                    <ul className="space-y-2 text-awareness-silver/70">
                      <li>" Dynamic routing with path-based rules</li>
                      <li>" Automatic load balancing across regions</li>
                      <li>" Request/response transformation</li>
                      <li>" API versioning and deprecation</li>
                      <li>" Real-time request analytics</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <GlassCard className="p-6 bg-infrastructure-green/5">
                  <h4 className="text-awareness-silver font-medium mb-2">Performance</h4>
                  <div className="space-y-2 text-sm text-awareness-silver/70">
                    <div className="flex justify-between">
                      <span>p50 Latency</span>
                      <span className="text-infrastructure-green">19ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span>p95 Latency</span>
                      <span className="text-infrastructure-green">47ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span>p99 Latency</span>
                      <span className="text-infrastructure-green">89ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Throughput</span>
                      <span className="text-infrastructure-green">100K req/sec</span>
                    </div>
                  </div>
                </GlassCard>
                <GlassCard className="p-6 bg-code-cyan/5">
                  <h4 className="text-awareness-silver font-medium mb-2">Pricing</h4>
                  <div className="space-y-2 text-sm text-awareness-silver/70">
                    <div className="flex justify-between">
                      <span>First 1M requests/month</span>
                      <span className="text-code-cyan">Free</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Additional requests</span>
                      <span className="text-code-cyan">$0.50/1M</span>
                    </div>
                  </div>
                </GlassCard>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Edge Computing Service */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <GlassCard className="p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div className="order-2 md:order-1 space-y-4">
                <GlassCard className="p-6 bg-code-cyan/5">
                  <h4 className="text-awareness-silver font-medium mb-2">Edge Locations</h4>
                  <div className="space-y-2 text-sm text-awareness-silver/70">
                    <div>" North America: 65 locations</div>
                    <div>" Europe: 52 locations</div>
                    <div>" Asia Pacific: 48 locations</div>
                    <div>" South America: 18 locations</div>
                    <div>" Middle East & Africa: 17 locations</div>
                  </div>
                </GlassCard>
                <GlassCard className="p-6 bg-infrastructure-green/5">
                  <h4 className="text-awareness-silver font-medium mb-2">Use Cases</h4>
                  <div className="space-y-2 text-sm text-awareness-silver/70">
                    <div>" Real-time AI inference</div>
                    <div>" Content delivery acceleration</div>
                    <div>" Edge-based data processing</div>
                    <div>" Geo-distributed applications</div>
                  </div>
                </GlassCard>
              </div>
              <div className="order-1 md:order-2">
                <Cloud className="w-16 h-16 text-code-cyan mb-6" />
                <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
                  Edge Computing
                </h2>
                <p className="text-lg text-awareness-silver/70 mb-6">
                  Deploy consciousness processing closer to users with 200+ edge locations worldwide.
                  Achieve sub-10ms latency for demanding applications.
                </p>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-code-cyan font-medium mb-2">Capabilities</h3>
                    <ul className="space-y-2 text-awareness-silver/70">
                      <li>" Serverless functions at the edge</li>
                      <li>" WebAssembly runtime support</li>
                      <li>" Edge caching and invalidation</li>
                      <li>" Geo-routing and failover</li>
                      <li>" Real-time metrics and logs</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Data Pipelines Service */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <GlassCard className="p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <Database className="w-16 h-16 text-lambda-gold mb-6" />
                <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
                  Data Pipelines
                </h2>
                <p className="text-lg text-awareness-silver/70 mb-6">
                  Stream and batch data processing at scale with built-in transformation and validation.
                </p>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lambda-gold font-medium mb-2">Pipeline Types</h3>
                    <ul className="space-y-2 text-awareness-silver/70">
                      <li>" Streaming: Real-time event processing</li>
                      <li>" Batch: Scheduled ETL workflows</li>
                      <li>" Hybrid: Mixed processing patterns</li>
                      <li>" CDC: Change data capture</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <GlassCard className="p-6 bg-lambda-gold/5">
                  <h4 className="text-awareness-silver font-medium mb-2">Processing Scale</h4>
                  <div className="space-y-2 text-sm text-awareness-silver/70">
                    <div className="flex justify-between">
                      <span>Events/second</span>
                      <span className="text-lambda-gold">1M+</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Batch size</span>
                      <span className="text-lambda-gold">10TB+</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Parallel tasks</span>
                      <span className="text-lambda-gold">10,000+</span>
                    </div>
                  </div>
                </GlassCard>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Additional Services Grid */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-12 text-center text-awareness-silver">
            Additional <span className="text-infrastructure-green">Services</span>
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <GlassCard className="p-6">
              <Shield className="w-12 h-12 text-success-green mb-4" />
              <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                Security Layer
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-4">
                DDoS protection, WAF, TLS 1.3 encryption, zero-trust architecture
              </p>
              <p className="text-success-green text-xs">SOC 2 · ISO 27001</p>
            </GlassCard>

            <GlassCard className="p-6">
              <Activity className="w-12 h-12 text-info-blue mb-4" />
              <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                Monitoring
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-4">
                Real-time metrics, distributed tracing, log aggregation, custom dashboards
              </p>
              <p className="text-info-blue text-xs">99.99% Visibility</p>
            </GlassCard>

            <GlassCard className="p-6">
              <Server className="w-12 h-12 text-warning-amber mb-4" />
              <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                Compute
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-4">
                GPU/CPU instances, auto-scaling, Kubernetes, spot instances
              </p>
              <p className="text-warning-amber text-xs">Up to 80% savings</p>
            </GlassCard>

            <GlassCard className="p-6">
              <Boxes className="w-12 h-12 text-infrastructure-green mb-4" />
              <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                Storage
              </h3>
              <p className="text-awareness-silver/70 text-sm mb-4">
                Object storage, block storage, file systems, backup & recovery
              </p>
              <p className="text-infrastructure-green text-xs">99.999999999% durability</p>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-6 text-awareness-silver">
            Get started with LUKHAS infrastructure
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Free tier available. No credit card required.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a href="https://lukhas.dev" target="_blank" rel="noopener noreferrer">
              <button className="px-8 py-4 bg-infrastructure-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-infrastructure-green/20 transition-all">
                Read Documentation
              </button>
            </a>
            <a href="https://lukhas.com" target="_blank" rel="noopener noreferrer">
              <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-infrastructure-green/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
                Contact Sales
              </button>
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
