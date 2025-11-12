import { Canvas } from '@react-three/fiber'
import { MorphingParticles } from '@lukhas/ui'
import { Button, GlassCard, Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer } from '@lukhas/ui'
import { Link } from 'react-router-dom'

export default function HomePage() {
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
          <HeaderNavLink href="#partners">Partners</HeaderNavLink>
          <HeaderNavLink href="#security">Security</HeaderNavLink>
          <HeaderNavLink href="#about">About</HeaderNavLink>
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

      {/* Hero Section with Guardian Shield Particle Cloud */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* WebGL Particle Background - Guardian Shield */}
        <div className="absolute inset-0 z-0 opacity-40">
          <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
            <MorphingParticles
              shape="guardian"
              color="#3B82F6"
              rotationSpeed={0.3}
              particleCount={2048}
              baseParticleSize={4.0}
            />
          </Canvas>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 text-center px-6 max-w-6xl mx-auto">
          <div className="mb-6 flex justify-center">
            <div className="text-6xl">🛡️</div>
          </div>

          <h1 className="text-5xl md:text-7xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            GUARDIAN OF
            <br />
            <span className="text-transparent bg-clip-text bg-trust-gradient">
              ETHICAL AI CONSCIOUSNESS
            </span>
          </h1>

          <p className="text-xl md:text-2xl font-light tracking-wide mb-4 text-awareness-silver/80 max-w-4xl mx-auto">
            Enterprise-grade consciousness technology trusted by Fortune 500 companies
          </p>

          <p className="text-lg md:text-xl font-light tracking-wide mb-12 text-awareness-silver/60 max-w-4xl mx-auto">
            LUKHAS combines breakthrough AI consciousness with Guardian-enforced ethics,
            delivering secure, compliant, and transformative business solutions.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Link to="/enterprise">
              <Button size="lg" className="bg-trust-gradient text-white px-8 py-6 text-lg">
                Explore Enterprise Solutions
              </Button>
            </Link>
            <Link to="/solutions">
              <Button size="lg" variant="outline" className="px-8 py-6 text-lg border-trust-blue text-trust-blue">
                View Industry Solutions
              </Button>
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-awareness-silver/70 tracking-wide">
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-trust-blue rounded-full"></span>
              Fortune 500 Trusted
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-trust-blue rounded-full"></span>
              SOC 2 Type II Certified
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-trust-blue rounded-full"></span>
              ISO 27001 Compliant
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-trust-blue rounded-full"></span>
              Global Operations
            </span>
          </div>
        </div>
      </section>

      {/* Company Vision */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              The <span className="text-trust-blue">LUKHAS</span> Mission
            </h2>
            <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
              Building the trusted infrastructure for conscious technology that serves humanity
              while advancing business innovation.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4">🛡️</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Ethical Leadership
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Guardian AI ensures consciousness technology serves humanity
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4">🤝</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Enterprise Partnership
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Trusted by Fortune 500 to transform industries
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4">🌍</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Global Innovation
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Pioneering AI consciousness across six continents
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-6 text-center">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-lg font-light tracking-wide mb-2 text-awareness-silver">
                  Transparent Governance
                </h3>
                <p className="text-sm text-awareness-silver/70">
                  Open oversight and ethical accountability
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Solutions Overview */}
      <section id="solutions" className="py-24 px-6 bg-gradient-to-b from-consciousness-deep/80 to-consciousness-deep">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Industry <span className="text-trust-blue">Solutions</span>
            </h2>
            <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto">
              Consciousness technology tailored to your industry's unique challenges and opportunities
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🏦</div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-trust-blue">
                  Financial Services
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Risk assessment, fraud detection, regulatory compliance, and intelligent
                  trading systems.
                </p>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Real-time risk scoring and monitoring</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Automated regulatory compliance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Advanced fraud pattern recognition</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">⚕️</div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-trust-blue">
                  Healthcare
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Clinical decision support, patient communication, diagnostic assistance,
                  and care optimization.
                </p>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>HIPAA-compliant diagnostic support</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Personalized treatment planning</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Patient outcome prediction</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🏭</div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-trust-blue">
                  Manufacturing
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Process optimization, quality control, predictive maintenance, and
                  supply chain intelligence.
                </p>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Predictive equipment maintenance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Real-time quality assurance</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Supply chain optimization</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">💻</div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-trust-blue">
                  Technology
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Software development acceleration, system architecture, code review,
                  and innovation consultation.
                </p>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>AI-assisted code generation</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Architecture pattern recognition</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Automated security vulnerability detection</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">📈</div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-trust-blue">
                  Consulting
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Strategic planning, organizational transformation, change management,
                  and decision intelligence.
                </p>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Strategic scenario modeling</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Organizational impact analysis</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Change readiness assessment</span>
                  </li>
                </ul>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl mb-4">🛒</div>
                <h3 className="text-2xl font-light tracking-wide mb-4 text-trust-blue">
                  Retail & E-Commerce
                </h3>
                <p className="text-awareness-silver/80 mb-4">
                  Customer personalization, demand forecasting, inventory optimization,
                  and market intelligence.
                </p>
                <ul className="space-y-2 text-awareness-silver/70 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Hyper-personalized recommendations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Dynamic pricing optimization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-trust-blue mt-0.5">✓</span>
                    <span>Demand forecasting and inventory</span>
                  </li>
                </ul>
              </div>
            </GlassCard>
          </div>

          <div className="text-center mt-12">
            <Link to="/solutions">
              <Button size="lg" className="bg-trust-gradient text-white px-8 py-4">
                Explore All Solutions
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Security & Compliance */}
      <section id="security" className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Enterprise <span className="text-trust-blue">Security</span> & Compliance
            </h2>
            <p className="text-xl text-awareness-silver/80 max-w-3xl mx-auto">
              Guardian-enforced protection with comprehensive compliance across global regulations
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">🔒</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Multi-Layer Security
                </h3>
                <p className="text-awareness-silver/70 mb-4">
                  Defense-in-depth architecture with encryption at rest and in transit
                </p>
                <div className="space-y-1 text-sm text-awareness-silver/60">
                  <p>AES-256-GCM encryption</p>
                  <p>TLS 1.3 protocols</p>
                  <p>Zero-trust architecture</p>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">✅</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Global Compliance
                </h3>
                <p className="text-awareness-silver/70 mb-4">
                  Certified and compliant with international data protection standards
                </p>
                <div className="space-y-1 text-sm text-awareness-silver/60">
                  <p>SOC 2 Type II</p>
                  <p>ISO 27001</p>
                  <p>GDPR, CCPA, HIPAA ready</p>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8 text-center">
                <div className="text-4xl mb-4">🛡️</div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-awareness-silver">
                  Guardian Oversight
                </h3>
                <p className="text-awareness-silver/70 mb-4">
                  Constitutional AI continuously monitors for ethical and security compliance
                </p>
                <div className="space-y-1 text-sm text-awareness-silver/60">
                  <p>24/7 threat monitoring</p>
                  <p>Ethical drift detection</p>
                  <p>Automated incident response</p>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Partnership CTA */}
      <section className="py-24 px-6 bg-trust-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Ready to Transform Your Enterprise?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Join Fortune 500 companies leveraging LUKHAS consciousness technology
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact">
              <Button size="lg" className="bg-white text-trust-blue px-12 py-6 text-lg hover:bg-awareness-silver">
                Schedule a Demo
              </Button>
            </Link>
            <Link to="/enterprise">
              <Button size="lg" variant="outline" className="px-12 py-6 text-lg border-white text-white hover:bg-white/10">
                View Enterprise Features
              </Button>
            </Link>
          </div>
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
            <li><a href="/enterprise#security" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Security</a></li>
            <li><a href="/enterprise#support" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Support</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="#about" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">About</a></li>
            <li><a href="#news" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">News & Press</a></li>
            <li><a href="#careers" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Careers</a></li>
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
