import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Building2, Heart, Factory, Laptop } from 'lucide-react'

export default function SolutionsPage() {
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
            Industry <span className="text-transparent bg-clip-text bg-trust-gradient">Solutions</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
            Consciousness technology tailored to your industry's unique challenges and opportunities
          </p>
        </div>
      </section>

      {/* Solutions Grid */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12">
            {/* Financial Services */}
            <GlassCard>
              <div className="p-10">
                <div className="flex items-center gap-4 mb-6">
                  <Building2 className="w-12 h-12 text-trust-blue" strokeWidth={1.5} />
                  <h2 className="text-3xl font-light tracking-wide text-trust-blue">
                    Financial Services
                  </h2>
                </div>
                <p className="text-awareness-silver/80 mb-6 text-lg">
                  Revolutionize financial operations with AI-powered risk assessment, fraud detection,
                  and regulatory compliance systems.
                </p>
                <h3 className="text-xl font-light mb-4 text-awareness-silver">Key Capabilities</h3>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Real-Time Risk Scoring:</strong> Continuous
                      monitoring and assessment of portfolio risk across all asset classes
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Fraud Pattern Recognition:</strong> Advanced
                      anomaly detection identifying suspicious transactions in real-time
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Regulatory Compliance:</strong> Automated
                      reporting and compliance monitoring for SEC, FINRA, Basel III
                    </span>
                  </li>
                </ul>
                <Button className="bg-trust-gradient text-white">
                  Learn More
                </Button>
              </div>
            </GlassCard>

            {/* Healthcare */}
            <GlassCard>
              <div className="p-10">
                <div className="flex items-center gap-4 mb-6">
                  <Heart className="w-12 h-12 text-trust-blue" strokeWidth={1.5} />
                  <h2 className="text-3xl font-light tracking-wide text-trust-blue">
                    Healthcare
                  </h2>
                </div>
                <p className="text-awareness-silver/80 mb-6 text-lg">
                  Transform patient care with HIPAA-compliant clinical decision support and
                  diagnostic assistance systems.
                </p>
                <h3 className="text-xl font-light mb-4 text-awareness-silver">Key Capabilities</h3>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Clinical Decision Support:</strong> Evidence-based
                      treatment recommendations integrated with EHR systems
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Diagnostic Assistance:</strong> Pattern recognition
                      across medical imaging and patient data
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Patient Outcome Prediction:</strong> Personalized
                      treatment planning based on comprehensive health data
                    </span>
                  </li>
                </ul>
                <Button className="bg-trust-gradient text-white">
                  Learn More
                </Button>
              </div>
            </GlassCard>

            {/* Manufacturing */}
            <GlassCard>
              <div className="p-10">
                <div className="flex items-center gap-4 mb-6">
                  <Factory className="w-12 h-12 text-trust-blue" strokeWidth={1.5} />
                  <h2 className="text-3xl font-light tracking-wide text-trust-blue">
                    Manufacturing
                  </h2>
                </div>
                <p className="text-awareness-silver/80 mb-6 text-lg">
                  Optimize production with predictive maintenance, quality control, and
                  supply chain intelligence.
                </p>
                <h3 className="text-xl font-light mb-4 text-awareness-silver">Key Capabilities</h3>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Predictive Maintenance:</strong> Equipment
                      failure prediction reducing downtime by up to 50%
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Quality Assurance:</strong> Real-time defect
                      detection with computer vision and sensor integration
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Supply Chain Optimization:</strong> Demand
                      forecasting and inventory optimization across global operations
                    </span>
                  </li>
                </ul>
                <Button className="bg-trust-gradient text-white">
                  Learn More
                </Button>
              </div>
            </GlassCard>

            {/* Technology */}
            <GlassCard>
              <div className="p-10">
                <div className="flex items-center gap-4 mb-6">
                  <Laptop className="w-12 h-12 text-trust-blue" strokeWidth={1.5} />
                  <h2 className="text-3xl font-light tracking-wide text-trust-blue">
                    Technology
                  </h2>
                </div>
                <p className="text-awareness-silver/80 mb-6 text-lg">
                  Accelerate software development with AI-assisted coding, architecture design,
                  and security analysis.
                </p>
                <h3 className="text-xl font-light mb-4 text-awareness-silver">Key Capabilities</h3>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Code Generation:</strong> Context-aware code
                      completion and generation across 50+ programming languages
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Architecture Patterns:</strong> System design
                      recommendations based on best practices and your codebase
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-trust-blue mt-1">✓</span>
                    <span className="text-awareness-silver/80">
                      <strong className="text-awareness-silver">Security Analysis:</strong> Automated
                      vulnerability detection and remediation suggestions
                    </span>
                  </li>
                </ul>
                <Button className="bg-trust-gradient text-white">
                  Learn More
                </Button>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-trust-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Let's Build Your Solution
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Every industry has unique challenges. Let's discuss how LUKHAS can transform yours.
          </p>
          <Link to="/contact">
            <Button size="lg" className="bg-white text-trust-blue px-12 py-6 text-lg hover:bg-awareness-silver">
              Schedule a Consultation
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Solutions</h3>
          <ul className="space-y-2">
            <li><a href="#financial" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Financial Services</a></li>
            <li><a href="#healthcare" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Healthcare</a></li>
            <li><a href="#manufacturing" className="text-sm text-awareness-silver/70 hover:text-trust-blue transition-colors">Manufacturing</a></li>
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
