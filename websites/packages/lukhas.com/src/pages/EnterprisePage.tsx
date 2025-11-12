import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'

export default function EnterprisePage() {
  return (
    <div className="min-h-screen bg-consciousness-deep">
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-trust-blue/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-trust-blue">.COM</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/solutions">Solutions</HeaderNavLink>
          <HeaderNavLink href="/enterprise">Enterprise</HeaderNavLink>
          <HeaderNavLink href="/#partners">Partners</HeaderNavLink>
          <HeaderNavLink href="/#security">Security</HeaderNavLink>
          <HeaderNavLink href="/#about">About</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Link to="/contact">
            <Button className="bg-trust-gradient text-white">
              Contact Sales
            </Button>
          </Link>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Enterprise <span className="text-transparent bg-clip-text bg-trust-gradient">Integration</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
            Seamless deployment, enterprise-grade security, and white-glove support for
            Fortune 500 consciousness technology implementations
          </p>
        </div>
      </section>

      {/* Architecture Overview */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              Enterprise <span className="text-trust-blue">Architecture</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              LUKHAS consciousness technology integrates seamlessly with your existing
              enterprise infrastructure
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🔌</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-trust-blue">
                  API-First Integration
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  RESTful and GraphQL APIs with comprehensive SDKs for seamless integration
                </p>
                <ul className="space-y-2 text-sm text-awareness-silver/70">
                  <li>• OAuth 2.0 / OpenID Connect</li>
                  <li>• SAML 2.0 enterprise SSO</li>
                  <li>• Webhook-based event streaming</li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">☁️</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-trust-blue">
                  Cloud & On-Premise
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Flexible deployment options to meet your security and compliance requirements
                </p>
                <ul className="space-y-2 text-sm text-awareness-silver/70">
                  <li>• AWS, Azure, GCP support</li>
                  <li>• Private cloud deployment</li>
                  <li>• On-premise installation</li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🔄</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-trust-blue">
                  Data Synchronization
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Real-time bidirectional sync with existing enterprise systems
                </p>
                <ul className="space-y-2 text-sm text-awareness-silver/70">
                  <li>• CRM/ERP integration</li>
                  <li>• Data warehouse connectors</li>
                  <li>• ETL pipeline support</li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-trust-blue">
                  Monitoring & Analytics
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Comprehensive observability with custom dashboards and alerts
                </p>
                <ul className="space-y-2 text-sm text-awareness-silver/70">
                  <li>• Real-time performance metrics</li>
                  <li>• Custom alerting rules</li>
                  <li>• Usage analytics and reporting</li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🔒</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-trust-blue">
                  Security Framework
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Multi-layer security with encryption, access control, and audit logging
                </p>
                <ul className="space-y-2 text-sm text-awareness-silver/70">
                  <li>• End-to-end encryption</li>
                  <li>• Role-based access control</li>
                  <li>• Comprehensive audit trails</li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🛡️</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-trust-blue">
                  Compliance Ready
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Pre-configured for major regulatory frameworks and industry standards
                </p>
                <ul className="space-y-2 text-sm text-awareness-silver/70">
                  <li>• GDPR, CCPA, HIPAA</li>
                  <li>• SOC 2, ISO 27001</li>
                  <li>• Industry-specific standards</li>
                </ul>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Implementation Process */}
      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              Implementation <span className="text-trust-blue">Process</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              Phased deployment strategy designed to minimize disruption and maximize ROI
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4 text-trust-blue font-bold">1</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Discovery
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Assessment of current systems, requirements gathering, and architecture design
                </p>
                <p className="text-xs text-awareness-silver/50 mt-3">2-4 weeks</p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4 text-trust-blue font-bold">2</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Pilot Deployment
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Limited rollout to test integration, train users, and validate performance
                </p>
                <p className="text-xs text-awareness-silver/50 mt-3">4-8 weeks</p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4 text-trust-blue font-bold">3</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Scaled Rollout
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Phased expansion across departments with continuous monitoring and optimization
                </p>
                <p className="text-xs text-awareness-silver/50 mt-3">8-16 weeks</p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4 text-trust-blue font-bold">4</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Optimization
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Performance tuning, advanced features, and continuous improvement
                </p>
                <p className="text-xs text-awareness-silver/50 mt-3">Ongoing</p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Support Services */}
      <section id="support" className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-light tracking-[0.1em] mb-4 text-awareness-silver">
              Enterprise <span className="text-trust-blue">Support</span>
            </h2>
            <p className="text-lg text-awareness-silver/80 max-w-3xl mx-auto">
              White-glove service with dedicated teams ensuring your success
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">🎯</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Dedicated Support Team
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Named customer success manager and technical account manager
                </p>
                <p className="text-sm text-awareness-silver/70">
                  24/7 priority support with &lt;1hr response SLA
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Training & Onboarding
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Comprehensive training programs for administrators and end users
                </p>
                <p className="text-sm text-awareness-silver/70">
                  On-site workshops, webinars, and certification programs
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">🔧</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Custom Development
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Tailored features and integrations to meet unique requirements
                </p>
                <p className="text-sm text-awareness-silver/70">
                  Professional services for bespoke solutions
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-trust-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Start Your Enterprise Transformation
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Let's discuss your integration requirements and deployment timeline
          </p>
          <Link to="/contact">
            <Button size="lg" className="bg-white text-trust-blue px-12 py-6 text-lg hover:bg-awareness-silver">
              Request Enterprise Demo
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Solutions</h3>
          <ul className="space-y-2">
            <li><a href="/solutions#financial" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Financial Services</a></li>
            <li><a href="/solutions#healthcare" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Healthcare</a></li>
            <li><a href="/solutions#manufacturing" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Manufacturing</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Enterprise</h3>
          <ul className="space-y-2">
            <li><a href="/enterprise" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Integration</a></li>
            <li><a href="#security" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Security</a></li>
            <li><a href="#support" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Support</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="/#about" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">About</a></li>
            <li><a href="/#news" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">News & Press</a></li>
            <li><a href="/#careers" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Careers</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Contact</h3>
          <ul className="space-y-2">
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Sales Inquiries</a></li>
            <li><a href="/partners" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Partnership</a></li>
            <li><a href="/support" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Support</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}
