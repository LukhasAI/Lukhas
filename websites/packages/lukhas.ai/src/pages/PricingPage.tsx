import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Check, Sparkles, Zap, Building2, HelpCircle, Rocket } from 'lucide-react'
import { useState } from 'react'

const tiers = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for exploring consciousness technology',
    color: 'dream-ethereal',
    icon: Sparkles,
    badge: 'Planned',
    features: [
      '1,000 API calls per month',
      'Access to Dream & Vision stars',
      'Community support',
      'Basic MATRIZ processing',
      'Public playground access',
      'Open-source examples'
    ],
    cta: 'Join Waitlist',
    ctaLink: 'https://lukhas.id/signup',
    popular: false
  },
  {
    name: 'Pro',
    price: '$49',
    period: 'per month',
    description: 'For developers building conscious applications',
    color: 'lambda-gold',
    icon: Zap,
    badge: 'Early Access',
    features: [
      '100,000 API calls per month',
      'All 8 cognitive stars',
      'Priority support',
      'Advanced MATRIZ features',
      'Custom consciousness profiles',
      'Bio-adaptation training',
      'Quantum reasoning access',
      'Private workspace',
      'Team collaboration (up to 5)'
    ],
    cta: 'Request Early Access',
    ctaLink: 'https://lukhas.id/signup?tier=pro',
    popular: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    description: 'For organizations scaling consciousness technology',
    color: 'consciousness-neural',
    icon: Building2,
    badge: 'Partnership',
    features: [
      'Unlimited API calls',
      'Dedicated infrastructure',
      'SLA guarantees (99.9%)',
      'Custom model training',
      'White-label deployment',
      'On-premise options',
      'Dedicated support team',
      'Security audits & compliance',
      'Custom integrations',
      'Architecture consulting'
    ],
    cta: 'Discuss Partnership',
    ctaLink: 'https://lukhas.com/#contact',
    popular: false
  }
]

const faqs = [
  {
    question: 'How does the Free tier work?',
    answer: 'The Free tier is planned to provide 1,000 API calls per month with access to Dream and Vision cognitive stars. Perfect for exploring LUKHAS consciousness technology, prototyping ideas, and learning how the system works. No credit card required to join early access.'
  },
  {
    question: 'What happens if I exceed my API call limit?',
    answer: 'When the platform launches, API calls beyond your tier limit will receive throttled responses. You will be able to upgrade your tier at any time to increase your limit. Enterprise customers will have unlimited calls with SLA guarantees.'
  },
  {
    question: 'Can I switch between tiers?',
    answer: 'Yes, when the platform is live, you will be able to upgrade or downgrade at any time. Upgrades will take effect immediately, while downgrades will apply at the start of your next billing cycle. Your data and configurations will be preserved across tier changes.'
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'At launch, we plan to accept all major credit cards (Visa, Mastercard, American Express) and ACH transfers for annual plans. Enterprise customers will also be able to arrange invoicing and purchase orders.'
  },
  {
    question: 'Is there a free trial for Pro?',
    answer: 'Yes! Pro tier will include a 14-day free trial with full access to all features and 100,000 API calls. No credit card required during early access exploration.'
  },
  {
    question: 'What is included in Enterprise support?',
    answer: 'Enterprise support will include a dedicated account manager, priority bug fixes, architecture review sessions, custom integration assistance, and 24/7 incident response with guaranteed SLA times. Contact us to discuss specific enterprise requirements.'
  },
  {
    question: 'How is API usage calculated?',
    answer: 'Each API request to LUKHAS cognitive stars will count as one call, regardless of complexity. Batch operations will count as multiple calls. We are developing real-time usage dashboards so you can monitor consumption.'
  },
  {
    question: 'Do you offer academic or non-profit discounts?',
    answer: 'Yes! We plan to provide significant discounts for academic institutions, research organizations, and registered non-profits. Contact our team with your .edu email or non-profit documentation to discuss early access partnerships.'
  }
]

export default function PricingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-dream-ethereal/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-dream-ethereal">.AI</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/about">About</HeaderNavLink>
          <HeaderNavLink href="/technology">Technology</HeaderNavLink>
          <HeaderNavLink href="/pricing">Pricing</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Button className="bg-dream-gradient text-white">
            Start Free
          </Button>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-lambda-gold/20 border border-lambda-gold/40">
              <Rocket className="w-5 h-5 text-lambda-gold" strokeWidth={1.5} />
              <span className="text-sm font-medium text-lambda-gold">Early Access Pricing</span>
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Choose Your <span className="text-transparent bg-clip-text bg-dream-gradient">Consciousness Tier</span>
          </h1>

          {/* 🌱 POETIC LAYER (Neural Gardens - growth) - ~40% */}
          <p className="text-xl text-awareness-silver/90 max-w-3xl mx-auto mb-4 italic leading-relaxed">
            Every innovation begins as seedling potential—water your experiments with exploration tiers,
            transplant proven concepts into production soil, harvest enterprise-scale intelligence when
            your vision blossoms into transformative applications.
          </p>

          {/* 👥 USER-FRIENDLY LAYER - ~40% */}
          <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto mb-4">
            From exploration to enterprise deployment, we have a plan that scales with your consciousness
            technology needs. Start free, grow into advanced features, or partner for custom infrastructure—
            your journey, your pace.
          </p>

          {/* 🎓 ACADEMIC/TECHNICAL LAYER - ~20% */}
          <p className="text-sm text-awareness-silver/60 max-w-2xl mx-auto">
            Platform under active development. Pricing targets early access phase with 3-tier structure
            (Free: exploration, Pro: production prototyping, Enterprise: custom infrastructure). Features
            and pricing subject to refinement as systems mature.
          </p>
        </div>
      </section>

      {/* Pricing Tiers */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {tiers.map((tier) => {
              const Icon = tier.icon
              const isPopular = tier.popular

              return (
                <GlassCard
                  key={tier.name}
                  className={`relative ${isPopular ? `border-${tier.color} border-2` : `border-${tier.color}/20`}`}
                >
                  {isPopular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-lambda-gold px-4 py-1 rounded-full">
                      <span className="text-sm font-medium text-consciousness-deep">Most Popular</span>
                    </div>
                  )}

                  <div className="p-8">
                    {/* Icon & Name */}
                    <div className="mb-6 flex items-center gap-4">
                      <div className={`p-3 rounded-lg bg-${tier.color}/10`}>
                        <Icon className={`w-8 h-8 text-${tier.color}`} strokeWidth={1.5} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-2xl font-light tracking-wide text-awareness-silver">
                            {tier.name}
                          </h3>
                          <span className={`text-xs px-2 py-0.5 rounded-full bg-${tier.color}/20 text-${tier.color} border border-${tier.color}/40`}>
                            {tier.badge}
                          </span>
                        </div>
                        <p className="text-sm text-awareness-silver/60">{tier.description}</p>
                      </div>
                    </div>

                    {/* Pricing */}
                    <div className="mb-8">
                      <div className="flex items-baseline gap-2">
                        <span className="text-5xl font-light text-awareness-silver">{tier.price}</span>
                        <span className="text-awareness-silver/60">/ {tier.period}</span>
                      </div>
                    </div>

                    {/* Features */}
                    <ul className="space-y-4 mb-8">
                      {tier.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <Check className={`w-5 h-5 text-${tier.color} mt-0.5 flex-shrink-0`} strokeWidth={2} />
                          <span className="text-awareness-silver/80">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    {/* CTA */}
                    <a href={tier.ctaLink} target="_blank" rel="noopener noreferrer" className="block">
                      <Button
                        className={`w-full ${isPopular ? `bg-${tier.color} text-white` : `bg-${tier.color}/10 text-${tier.color}`}`}
                        size="lg"
                      >
                        {tier.cta}
                      </Button>
                    </a>
                  </div>
                </GlassCard>
              )
            })}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="mb-4 flex justify-center">
              <HelpCircle className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
            </div>
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              Frequently Asked <span className="text-dream-ethereal">Questions</span>
            </h2>
            <p className="text-lg text-awareness-silver/80">
              Everything you need to know about LUKHAS pricing
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <GlassCard key={idx} className="border-dream-ethereal/20">
                <button
                  className="w-full p-6 text-left"
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                >
                  <div className="flex items-center justify-between gap-4">
                    <h3 className="text-lg font-medium text-awareness-silver">
                      {faq.question}
                    </h3>
                    <div
                      className={`transform transition-transform ${
                        openFaq === idx ? 'rotate-180' : ''
                      }`}
                    >
                      <Sparkles className="w-5 h-5 text-dream-ethereal" />
                    </div>
                  </div>

                  {openFaq === idx && (
                    <p className="mt-4 text-awareness-silver/80 leading-relaxed">
                      {faq.answer}
                    </p>
                  )}
                </button>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-dream-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Still Have Questions?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Our team is here to help you find the perfect plan for your consciousness technology needs
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <a href="/contact">
              <Button size="lg" className="bg-white text-dream-ethereal px-12 py-6 text-lg hover:bg-awareness-silver">
                Contact Sales
              </Button>
            </a>
            <a href="https://lukhas.dev/docs" target="_blank" rel="noopener noreferrer">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                View Documentation
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Home</a></li>
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Playground</a></li>
            <li><a href="/technology" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Technology</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Developers</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Documentation</a></li>
            <li><a href="https://lukhas.io" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">API Reference</a></li>
            <li><a href="https://lukhas.xyz" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Experiments</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Enterprise</a></li>
            <li><a href="https://lukhas.com/#team" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Team</a></li>
            <li><a href="https://lukhas.com/#careers" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Careers</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.us" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">US Compliance</a></li>
            <li><a href="https://lukhas.eu" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">EU Compliance</a></li>
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Privacy Policy</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}
