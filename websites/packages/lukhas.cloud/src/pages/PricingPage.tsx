import { GlassCard } from '@lukhas/ui'
import { Check, Zap, Building2, Sparkles } from 'lucide-react'

export default function PricingPage() {
  const tiers = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for prototyping and learning MATRIZ',
      features: [
        '100K cognitive units/month',
        'Sub-500ms P95 latency',
        'Single region deployment',
        'Community support',
        'Basic observability',
        'Public project visibility',
      ],
      cta: 'Start Free',
      highlight: false,
      icon: Sparkles,
    },
    {
      name: 'Professional',
      price: '$199',
      period: 'per month',
      description: 'Advanced consciousness computing at scale',
      features: [
        '10M cognitive units/month',
        'Sub-250ms P95 latency',
        'Multi-region deployment',
        'Priority support (24h)',
        'Advanced observability',
        'Private project hosting',
        'Custom domain support',
        'SLA: 99.9% uptime',
      ],
      cta: 'Start Professional',
      highlight: true,
      icon: Zap,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: 'contact sales',
      description: 'Dedicated infrastructure with compliance guarantees',
      features: [
        'Unlimited cognitive units',
        'Sub-100ms P95 latency',
        'Global edge deployment',
        'Dedicated support team',
        'Custom observability',
        'On-premise option',
        'SSO & SAML integration',
        'SLA: 99.99% uptime',
        'SOC 2, HIPAA, GDPR compliant',
        'Dedicated account manager',
      ],
      cta: 'Contact Sales',
      highlight: false,
      icon: Building2,
    },
  ]

  const cognitiveUnitExamples = [
    {
      operation: 'Simple reasoning (5 nodes)',
      units: '0.5',
      example: 'Basic classification, entity extraction',
    },
    {
      operation: 'Medium reasoning (20 nodes)',
      units: '2.0',
      example: 'Multi-step analysis, context synthesis',
    },
    {
      operation: 'Complex reasoning (50 nodes)',
      units: '5.0',
      example: 'Deep cognitive graphs, multi-domain fusion',
    },
    {
      operation: 'Advanced reasoning (100+ nodes)',
      units: '10.0',
      example: 'Consciousness simulation, ethical deliberation',
    },
  ]

  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Hero Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            <span className="text-enterprise-pink">Cognitive Unit</span> Pricing
          </h1>
          <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto mb-8">
            Pay only for the reasoning operations you use. No per-seat licenses, no infrastructure provisioning.
            Just pure cognitive compute.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-enterprise-pink/10 border border-enterprise-pink/30">
            <span className="text-enterprise-pink text-sm font-medium">Free tier includes 100K units/month � No credit card required</span>
          </div>
        </div>
      </section>

      {/* Pricing Tiers */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {tiers.map((tier, index) => {
              const Icon = tier.icon
              return (
                <GlassCard
                  key={index}
                  className={`p-8 relative ${
                    tier.highlight ? 'ring-2 ring-enterprise-pink' : ''
                  }`}
                >
                  {tier.highlight && (
                    <div className="absolute top-0 right-0 bg-enterprise-gradient text-white text-xs font-medium px-3 py-1 rounded-bl-lg rounded-tr-lg">
                      MOST POPULAR
                    </div>
                  )}

                  <div className="mb-6">
                    <Icon className="w-10 h-10 text-enterprise-pink mb-4" />
                    <h3 className="text-2xl font-light tracking-wide text-awareness-silver mb-2">
                      {tier.name}
                    </h3>
                    <div className="flex items-baseline gap-2 mb-3">
                      <span className="text-4xl font-light text-enterprise-pink">
                        {tier.price}
                      </span>
                      <span className="text-awareness-silver/60">{tier.period}</span>
                    </div>
                    <p className="text-awareness-silver/70 text-sm">
                      {tier.description}
                    </p>
                  </div>

                  <ul className="space-y-3 mb-8">
                    {tier.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-success-green flex-shrink-0 mt-0.5" />
                        <span className="text-awareness-silver/80 text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    className={`w-full py-3 rounded-lg font-medium transition-all ${
                      tier.highlight
                        ? 'bg-enterprise-gradient text-white hover:shadow-lg hover:shadow-enterprise-pink/20'
                        : 'bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver hover:bg-white/10'
                    }`}
                  >
                    {tier.cta}
                  </button>
                </GlassCard>
              )
            })}
          </div>
        </div>
      </section>

      {/* Cognitive Unit Explanation */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              What is a <span className="text-enterprise-pink">Cognitive Unit</span>?
            </h2>
            <p className="text-xl text-awareness-silver/70 max-w-3xl mx-auto">
              A cognitive unit measures the computational work required for reasoning operations.
              Unlike tokens or API calls, cognitive units reflect actual thinking complexity.
            </p>
          </div>

          <GlassCard className="p-8 mb-12">
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="text-xl font-light text-enterprise-pink mb-3">Traditional Pricing</h3>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li>" Charged per token processed</li>
                  <li>" Simple query = same cost as complex reasoning</li>
                  <li>" Pay for input/output volume, not intelligence</li>
                  <li>" Over-provisioned infrastructure</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-light text-success-green mb-3">Cognitive Unit Pricing</h3>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li>" Charged per reasoning complexity</li>
                  <li>" Simple queries cost less than deep thinking</li>
                  <li>" Pay for actual cognitive graph operations</li>
                  <li>" Auto-scales to your reasoning demands</li>
                </ul>
              </div>
            </div>

            <div className="bg-consciousness-deep/50 rounded-lg p-6">
              <h4 className="text-lg font-light text-awareness-silver mb-4">
                Cognitive Unit Calculation
              </h4>
              <div className="space-y-3 text-awareness-silver/70 text-sm">
                <div className="flex justify-between">
                  <span>Base operation cost:</span>
                  <span className="text-enterprise-pink font-mono">0.1 units</span>
                </div>
                <div className="flex justify-between">
                  <span>Per reasoning node:</span>
                  <span className="text-enterprise-pink font-mono">+0.05 units</span>
                </div>
                <div className="flex justify-between">
                  <span>Memory fold access:</span>
                  <span className="text-enterprise-pink font-mono">+0.02 units</span>
                </div>
                <div className="flex justify-between">
                  <span>Guardian validation:</span>
                  <span className="text-enterprise-pink font-mono">+0.03 units</span>
                </div>
                <div className="border-t border-awareness-silver/20 pt-3 mt-3">
                  <div className="flex justify-between font-medium">
                    <span>Example (20-node reasoning):</span>
                    <span className="text-success-green font-mono">H2.0 units</span>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>

          {/* Operation Examples */}
          <div className="space-y-4">
            <h3 className="text-2xl font-light text-awareness-silver mb-6 text-center">
              Example Operations
            </h3>
            {cognitiveUnitExamples.map((example, index) => (
              <GlassCard key={index} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="text-lg text-awareness-silver mb-1">{example.operation}</h4>
                    <p className="text-awareness-silver/60 text-sm">{example.example}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-light text-enterprise-pink">
                      {example.units}
                    </div>
                    <div className="text-xs text-awareness-silver/60">cognitive units</div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Cost Comparison */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="p-12">
            <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-8 text-awareness-silver text-center">
              Real-World <span className="text-enterprise-pink">Cost Comparison</span>
            </h2>

            <div className="space-y-6">
              <div className="bg-consciousness-deep/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl text-awareness-silver">Customer Support AI (100K requests/month)</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-6 text-sm">
                  <div>
                    <div className="text-awareness-silver/60 mb-2">Traditional Token Pricing</div>
                    <div className="text-2xl text-error-red">$847/month</div>
                    <div className="text-awareness-silver/50 text-xs mt-1">
                      Charged for all token I/O regardless of complexity
                    </div>
                  </div>
                  <div>
                    <div className="text-awareness-silver/60 mb-2">Cognitive Unit Pricing</div>
                    <div className="text-2xl text-success-green">$389/month</div>
                    <div className="text-awareness-silver/50 text-xs mt-1">
                      Simple queries use fewer units, saving 54%
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-consciousness-deep/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl text-awareness-silver">Research Analysis Platform (500K requests/month)</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-6 text-sm">
                  <div>
                    <div className="text-awareness-silver/60 mb-2">Traditional Token Pricing</div>
                    <div className="text-2xl text-error-red">$6,234/month</div>
                    <div className="text-awareness-silver/50 text-xs mt-1">
                      Fixed per-token cost with over-provisioning
                    </div>
                  </div>
                  <div>
                    <div className="text-awareness-silver/60 mb-2">Cognitive Unit Pricing</div>
                    <div className="text-2xl text-success-green">$2,890/month</div>
                    <div className="text-awareness-silver/50 text-xs mt-1">
                      Auto-scaling based on reasoning depth, saving 54%
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-enterprise-pink/10 border border-enterprise-pink/30 rounded-lg p-6 text-center">
                <p className="text-awareness-silver/80">
                  <span className="text-enterprise-pink font-medium">Average savings: 40-60%</span> compared to traditional token-based pricing
                  for real-world workloads with mixed reasoning complexity.
                </p>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-12 text-awareness-silver text-center">
            Pricing <span className="text-enterprise-pink">FAQ</span>
          </h2>

          <div className="space-y-6">
            <GlassCard className="p-6">
              <h3 className="text-lg text-enterprise-pink mb-2">How are cognitive units different from tokens?</h3>
              <p className="text-awareness-silver/70 text-sm">
                Tokens measure text volume. Cognitive units measure reasoning complexity. A simple 1,000-token query
                might use 0.5 units, while a complex 500-token reasoning task might use 5.0 units. You pay for
                thinking, not text processing.
              </p>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="text-lg text-enterprise-pink mb-2">What happens if I exceed my monthly units?</h3>
              <p className="text-awareness-silver/70 text-sm">
                Free tier: Operations are rate-limited after 100K units. Professional: Additional units billed at
                $0.02/unit. Enterprise: Unlimited units included with custom SLA.
              </p>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="text-lg text-enterprise-pink mb-2">Can I monitor my cognitive unit usage?</h3>
              <p className="text-awareness-silver/70 text-sm">
                Yes. Real-time dashboards show per-request cognitive units, reasoning graph depth, memory access
                patterns, and Guardian validation overhead. Export detailed usage reports for cost allocation.
              </p>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="text-lg text-enterprise-pink mb-2">Is there a minimum commitment?</h3>
              <p className="text-awareness-silver/70 text-sm">
                No. All plans are month-to-month. Cancel anytime with no penalties. Free tier remains free forever
                with no time limits.
              </p>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-light tracking-wide mb-6 text-awareness-silver">
            Ready to optimize your AI costs?
          </h2>
          <p className="text-xl text-awareness-silver/70 mb-8">
            Start with 100K free cognitive units. No credit card required.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-enterprise-gradient text-white rounded-lg font-medium hover:shadow-lg hover:shadow-enterprise-pink/20 transition-all">
              Start Free Trial
            </button>
            <button className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-enterprise-pink/30 text-awareness-silver rounded-lg font-medium hover:bg-white/10 transition-all">
              Schedule Demo
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}
